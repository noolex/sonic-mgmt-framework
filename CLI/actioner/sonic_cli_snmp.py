#!/usr/bin/python
import os
import subprocess
import sys
import json
import collections
import re
import swsssdk
import cli_client as cc
import socket
import ipaddress
import netifaces
import syslog
import traceback
import psutil
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
from swsssdk import ConfigDBConnector
from operator import itemgetter
from collections import OrderedDict
from socket import AF_INET,AF_INET6

ALLOW_SYSNAME=False
"""
module: ietf-snmp
  +--rw snmp
     +--rw engine
     |  +--rw enabled?     boolean
     |  +--rw listen* [name]
     |  |  +--rw name         snmp:identifier
     |  |  +--rw (transport)
     |  |     +--:(udp)
     |  |        +--rw udp
     |  |           +--rw ip                    inet:ip-address
     |  |           +--rw port?                 inet:port-number
     |  |           +--rw snmp-ext:interface?   string
     |  +--rw version
     |  |  +--rw v2c?   empty
     |  |  +--rw v3?    empty
     |  +--rw engine-id?   snmp:engine-id
     +--rw target* [name]
     |  +--rw name             snmp:identifier
     |  +--rw (transport)
     |  |  +--:(udp)
     |  |     +--rw udp
     |  |        +--rw ip                           inet:ip-address
     |  |        +--rw port?                        inet:port-number
     |  |        +--rw snmp-ext:source-interface?   string
     |  +--rw tag*             snmp:tag-value
     |  +--rw timeout?         uint32
     |  +--rw retries?         uint8
     |  +--rw target-params    snmp:identifier
     +--rw target-params* [name]
     |  +--rw name         snmp:identifier
     |  +--rw (params)?
     |     +--:(v2c)
     |     |  +--rw v2c
     |     |     +--rw security-name    snmp:security-name
     |     +--:(usm)
     |        +--rw usm
     |           +--rw user-name         snmp:security-name
     |           +--rw security-level    snmp:security-level
     +--rw vacm
     |  +--rw group* [name]
     |  |  +--rw name      snmp:group-name
     |  |  +--rw member* [security-name]
     |  |  |  +--rw security-name     snmp:security-name
     |  |  |  +--rw security-model*   snmp:security-model
     |  |  +--rw access* [context security-model security-level]
     |  |     +--rw context           snmp:context-name
     |  |     +--rw context-match?    enumeration
     |  |     +--rw security-model    snmp:security-model-or-any
     |  |     +--rw security-level    snmp:security-level
     |  |     +--rw read-view?        snmp:view-name
     |  |     +--rw write-view?       view-name
     |  |     +--rw notify-view?      view-name
     |  +--rw view* [name]
     |     +--rw name       view-name
     |     +--rw include*   snmp:wildcard-object-identifier
     |     +--rw exclude*   snmp:wildcard-object-identifier
     +--rw notify* [name]
     |  +--rw name    snmp:identifier
     |  +--rw tag     snmp:tag-value
     |  +--rw type?   enumeration
     +--rw community* [index]
     |  +--rw index            snmp:identifier
     |  +--rw security-name    snmp:security-name
     +--rw usm
     |  +--rw local
     |     +--rw user* [name]
     |        +--rw name    snmp:identifier
     |        +--rw auth!
     |        |  +--rw (protocol)
     |        |     +--:(md5)
     |        |     |  +--rw md5
     |        |     |     +--rw key    yang:hex-string
     |        |     +--:(sha)
     |        |        +--rw sha
     |        |           +--rw key    yang:hex-string
     |        +--rw priv!
     |           +--rw (protocol)
     |              +--:(des)
     |              |  +--rw des
     |              |     +--rw key    yang:hex-string
     |              +--:(aes)
     |                 +--rw aes
     |                    +--rw key    yang:hex-string
     +--rw snmp-ext:system
        +--rw snmp-ext:contact?       string
        +--rw snmp-ext:location?      string
        +--rw snmp-ext:trap-enable?   boolean
"""
DEVICE_METADATA = 'DEVICE_METADATA'
AGENTADDRESS    = 'SNMP_AGENT_ADDRESS_CONFIG'
SYSTEM          = 'SYSTEM'
SNMP_SERVER     = 'SNMP_SERVER'
SNMP_SERVER_GROUP_MEMBER = 'SNMP_SERVER_GROUP_MEMBER'
sysname         = 'sysName'
contact         = 'sysContact'
location        = 'sysLocation'
traps           = 'traps'
context         = 'Default'
SecurityModels = { 'any' : 'any', 'v1': 'v1', 'v2c': 'v2c', 'v3': 'usm' }
SecurityLevels = { 'noauth' : 'no-auth-no-priv', 'auth' : 'auth-no-priv', 'priv' : 'auth-priv' }
ViewOpts       = { 'read' : 'readView', 'write' : 'writeView', 'notify' : 'notifyView'}
SORTED_ORDER   = ['sysName', 'sysLocation','sysContact', 'engineID', 'traps']
ipFamily       = {4: AF_INET, 6: AF_INET6}

aa = cc.ApiClient()

def manageGroupMasterKey(group):
  """ Group table has two sub-tables, Access and Memmber.
      This routine removes the master if it is no longer needed.
  """
  deleteGroup = True

  response = invoke('snmp_group_member_get', None)
  if response.ok():
    for entry in response.content['group-member']:
      if entry['name'] == group:
        deleteGroup = False

  response = invoke('snmp_group_access_get', None)
  if response.ok() and len(response.content) != 0:
    for entry in response.content['group-access']:
      if entry['name'] == group:
        deleteGroup = False

  if deleteGroup == True:
    path = '/restconf/data/ietf-snmp:snmp/vacm/group={name}'
    keypath = cc.Path(path, name=group)
    response = aa.delete(keypath)

  return deleteGroup

def entryNotFound(response):
  """ Helper routine to detect entries that are not found. """
  if response.content == None:
    return True
  error_data = response.content['ietf-restconf:errors']['error'][0]
  if 'error-message' in error_data:
    err_msg = error_data['error-message']
    if err_msg == 'Entry not found':
      return True
  return False

def findKeyForAgentEntry(ipAddr, port, interface):
  """ Search the Agent Table for ipAddr and return the key
      Keys are of the form agentEntry1, agentEntry2, etc.
  """
  keypath = cc.Path('/restconf/data/ietf-snmp:snmp/engine/listen')
  entry = "None"
  response = aa.get(keypath)
  if response.ok() and response.content is not None and 'ietf-snmp:listen' in response.content.keys():
    listenList = response.content['ietf-snmp:listen']
    if len(listenList) > 0:
      for listen in listenList:
        iface = ""
        udp = listen['udp']
        if (ipAddr == udp['ip']) and (int(port) == udp['port']):
          if udp.has_key('ietf-snmp-ext:interface'):
            iface = udp['ietf-snmp-ext:interface']
          if interface == iface:
            entry = listen['name']
            break

  return entry

def findNextKeyForAgentEntry():
  """ Find the next available agentEntry key """
  index = 1
  key = "agentEntry{}".format(index)
  keypath = cc.Path('/restconf/data/ietf-snmp:snmp/engine/listen')
  response=aa.get(keypath)
  if response.ok() and response.content is not None and 'ietf-snmp:listen' in response.content.keys():
    listenList = response.content['ietf-snmp:listen']
    if len(listenList) > 0:
      while 1:
        for listen in listenList:
          found = False
          if listen['name'] == key:
            found = True
            break;

        if found == True:
          index += 1
          key = "agentEntry{}".format(index)
        else:
          break

  return key

def findKeyForTargetEntry(ipAddr):
  """ Search the Target Table for ipAddr and return the key
      Keys are of the form targetEntry1, targetEntry2, etc.
  """
  keypath = cc.Path('/restconf/data/ietf-snmp:snmp/target')
  response=aa.get(keypath, None, False)
  if response.ok():
    if 'ietf-snmp:target' in response.content.keys():
      for key, table in response.content.items():
        while len(table) > 0:
          data = table.pop(0)
          udp = data['udp']
          if udp['ip'] == ipAddr:
            return data['name']
  return "None"

def findNextKeyForTargetEntry(ipAddr):
  """ Find the next available TargetEntry key """
  key = "None"
  index = 1
  while 1:
    key = "targetEntry{}".format(index)
    index += 1
    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/target={name}', name=key)
    response=aa.get(keypath, None, False)
    if response.ok():
      if len(response.content) == 0:
        break
    else:
      break
  return key

def createYangHexStr(textString):
  """ Convert plain hex string into yang:hex-string """
  data = textString[0:2]
  i = 2
  while i < len(textString):
    data = data + ':' + textString[i:i+2]
    i = i + 2
  return data

def getEngineID():
  """ Construct SNMP engineID from the configured value or from scratch """
  keypath = cc.Path('/restconf/data/ietf-snmp:snmp/engine/engine-id')
  response=aa.get(keypath)

  # First, try to get engineID via rest
  engineID = ''
  if response.ok() and response.content is not None and len(response.content) != 0:
    content = response.content
    if content.has_key('ietf-snmp:engine-id'):
      engineID = content['ietf-snmp:engine-id']
    elif content.has_key('engine-id'):
      engineID = content['engine-id']
    engineID = engineID.encode('ascii')
    engineID = engineID.translate(None, ':')

  # ensure engineID is properly formatted before use. See RFC 3411
  try:
    # must be hex (base 16)
    value = int(engineID, 16)
    # length of 5 - 32 octets
    if len(engineID) < 10:
      engineID = ''
    if len(engineID) > 64:
      engineID = ''
  except:
    # Whoops, not hex
    engineID = ''

  # if the engineID is not configured, construct as per SnmpEngineID
  # TEXTUAL-CONVENTION in RFC 3411 using the system MAC address.
  if len(engineID) == 0:
    keypath = cc.Path('/restconf/data/sonic-device-metadata:sonic-device-metadata/DEVICE_METADATA/DEVICE_METADATA_LIST={name}/mac', name="localhost")
    response = aa.get(keypath, None, False)
    if response.ok():
        sysmac = response.content['sonic-device-metadata:mac'].encode('ascii')
    if sysmac == None:
      # All else fails, something must be used. Fabricated MAC Address
      sysmac = '00:00:00:12:34:56'
    sysmac = sysmac.translate(None, ':')
    # engineID is:
    # 3) The length of the octet string varies.
    #   bit 0 == '1'
    #   The snmpEngineID has a length of 12 octets
    #   The first four octets are set to the binary equivalent of the agent's
    #     SNMP management private enterprise number as assigned by IANA.
    #     Microsoft = 311 = 0000 0137
    #   The fifth octet indicates how the rest (6th andfollowing octets) are formatted.
    #     3     - MAC address (6 octets)
    #   + System MAC address
    engineID = "8000013703"+sysmac

  return engineID

def getIPType(x):
  try: socket.inet_pton(AF_INET6, x)
  except socket.error:
    return False
  return True

def getAgentAddresses():
  """ Read system saved agent addresses.
      This has history in the CLICK config command:
        config snmpagentaddress add [-p <udpPort>] [-v <vrfName>] <IpAddress>
        config snmpagentaddress del [-p <udpPort>] [-v <vrfName>] <IpAddress>
      The key to this table is  ipaddr|udpPort|ifname
  """
  agentAddresses = []
  datam = {}
  keypath = cc.Path('/restconf/data/ietf-snmp:snmp/engine/listen')
  response = aa.get(keypath)
  if response.ok() and response.content is not None and 'ietf-snmp:listen' in response.content.keys():
    listenList = response.content['ietf-snmp:listen']
    if len(listenList) > 0:
      for listen in listenList:
        udp = listen['udp']
        entry = {}
        entry['udpPort'] = udp[u'port']
        entry['ipAddr'] = udp[u'ip']
        if u'ietf-snmp-ext:interface' in udp.keys():
          entry['ifName']  = udp[u'ietf-snmp-ext:interface']
        agentAddresses.append(entry)

  return agentAddresses

# Return the list of interfaces
#   eg. ['Ethernet0', 'Ethernet1', etc.
#   or: "
def interfaces_list():
    names = []
    keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces')
    response = aa.get(keypath)
    if response.ok():
        content = response.content
        if content:
            interfaces = content.get("openconfig-interfaces:interfaces")
            if interfaces:
                interface = interfaces.get("interface")
                if interface:
                    for c in interface:
                        config = c.get("config")
                        if config:
                            name = config.get("name")
                            if name:
                                names.append(str(name))
    ifaces = netifaces.interfaces()
    for iface in ifaces:
        if iface[:8].lower() != "ethernet":
            names.append(iface)
    return names

# Are we in native mode (eg: "Ethernet80") or standard mode (eg: "Eth1/21/1")
def is_in_standard_mode():
    keypath = cc.Path('/restconf/data/sonic-device-metadata:sonic-device-metadata/DEVICE_METADATA/DEVICE_METADATA_LIST={name}/intf_naming_mode', name="localhost")
    response = aa.get(keypath)
    if response.ok():
        content = response.content
        if content == None:
            return False
        try:
            mode = content['sonic-device-metadata:intf_naming_mode']
            return mode.lower() == "standard"
        except:
            return False
    else:
        return False

# Construct a list of interfaces [[standard, native], ...]
#   Eg. [['Ethernet0', 'Eth1/1'], ['Ethernet1', 'Eth1/2'], ...]
def alias_interfaces_list():
    names =[]
    keypath = cc.Path('/restconf/data/sonic-port:sonic-port/PORT_TABLE')
    response = aa.get(keypath)
    if response.ok():
        content = response.content
        if content != None:
            port_table = content['sonic-port:PORT_TABLE']
            port_table_list = port_table['PORT_TABLE_LIST']
            for l in port_table_list:
                try:
                    n = [l['alias'], l['ifname']]
                    names.append(n)
                except:
                    pass
    return names

def convert_to_native(data, standard):
    if standard in [i[1] for i in data]:
        for x in data:
            if standard in x[1]:
                return x[0]
    return standard


def invoke(func, args):
  if func == 'snmp_get':
    datam = {}
    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/ietf-snmp-ext:system/contact')
    response = aa.get(keypath)
    if response.ok() and response.content is not None and 'ietf-snmp-ext:contact' in response.content.keys():
        datam['sysContact'] = response.content['ietf-snmp-ext:contact']

    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/ietf-snmp-ext:system/location')
    response = aa.get(keypath)
    if response.ok() and response.content is not None and 'ietf-snmp-ext:location' in response.content.keys():
        datam['sysLocation'] = response.content['ietf-snmp-ext:location']

    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/ietf-snmp-ext:system/trap-enable')
    response = aa.get(keypath)
    if response.ok() and response.content is not None and 'ietf-snmp-ext:trap-enable' in response.content.keys():
      trapEnable = response.content['ietf-snmp-ext:trap-enable']
      if trapEnable == True:
        datam['traps'] = 'enable'

    datam['engineID'] = getEngineID()
    if len(datam) > 0:
      order = []
      for key in SORTED_ORDER:
        if datam.has_key(key):
          order.append(key)
      tuples = [(key, datam[key]) for key in order]
      datam = OrderedDict(tuples)

    agentAddr = {}
    agentAddresses = getAgentAddresses()
    if len(agentAddresses) > 0:
      agentAddr['agentAddr'] = agentAddresses

    response=aa.cli_not_implemented("global")      # Just to get the proper format to return data and status
    response.content = {}                          # This method is used extensively throughout
    response.status_code = 204
    response.content['system'] = datam
    response.content['global'] = agentAddr
    return response

  elif func == 'snmp_location':
    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/ietf-snmp-ext:system/location')
    if len(args) > 0:
      location = args[0]
      for element in args[1:]:
        location = location + ' ' + element
      body = {"ietf-snmp-ext:location": location}
      response = aa.patch(keypath, body)
    else:
      response = aa.delete(keypath)
    return response

  elif func == 'snmp_contact':
    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/ietf-snmp-ext:system/contact')
    if len(args) > 0:
      contact = args[0]
      for element in args[1:]:
        contact = contact + ' ' + element
      body = {"ietf-snmp-ext:contact": contact}
      response = aa.patch(keypath, body)
    else:
      response = aa.delete(keypath)
    return response

  elif func == 'snmp_trap':
    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/ietf-snmp-ext:system/trap-enable')
    if (len(args)>0) and (args[0] == 'enable'):
      body = {"ietf-snmp-ext:trap-enable": True}
      response = aa.patch(keypath, body)
    else:
      response = aa.delete(keypath)
    return response

  elif func == 'snmp_engine':
    data = ''
    if (len(args) == 1):
      # Configure Engine ID
      engineID = createYangHexStr(args[0])
      keypath = cc.Path('/restconf/data/ietf-snmp:snmp/engine')
      entry=collections.defaultdict(dict)
      entry['engine']={ "engine-id" : engineID }
      response = aa.patch(keypath, entry)
    else:
      # Remove Engine ID
      keypath = cc.Path('/restconf/data/ietf-snmp:snmp/engine')
      response = aa.delete(keypath)

    return response

  elif func == 'snmp_agentaddr' or func == 'no_snmp_agentaddr':
    ipAddress = args.pop(0)
    port = '161'                    # standard IPv4 listening UDP port.
    interface = ''
    if 'port' in args:
      index = args.index('port')
      port = args[index+1]
    if 'interface' in args:
      index = args.index('interface')
      interface = args[index+1]

    response = None
    # Since the key to the YANG model is the listening address i.e. the listen name
    # there can exist only a single entry per name.
    key=findKeyForAgentEntry(ipAddress, port, interface)
    if not key == 'None':
      keypath = cc.Path('/restconf/data/ietf-snmp:snmp/engine/listen={name}', name=key)
      response = aa.delete(keypath, True)

    if func == 'snmp_agentaddr':    # Need to test parameters before setting
      if key == 'None':
        key=findNextKeyForAgentEntry()
      standard_mode = is_in_standard_mode()
      if standard_mode:
          std_nat_interfaces = alias_interfaces_list()
      ipAddrValid = False
      ifValid = False
      net_if_addrs_dict = psutil.net_if_addrs()
      if interface == '':
        ifValid = True
      else:
        interface = convert_to_native(std_nat_interfaces, interface) if standard_mode else interface
        if net_if_addrs_dict.get(interface):
          ifValid = True
      if ifValid:
        ip = ipaddress.ip_address(unicode(ipAddress))
        for intf, ipaddrs in net_if_addrs_dict.items():
          for _ip in ipaddrs:
            if ipFamily[ip.version] == _ip.family:
              testAddr = _ip.address
              if '%' in testAddr:            # some IPv6 addresses include an interface at the end
                testAddr = testAddr[0:testAddr.index('%')]
              if ipAddress == testAddr:
                ipAddrValid = True
                break

      portValid = True
      if ipAddrValid == True and not port == '161':
        reusePort = False
        agentAddresses = getAgentAddresses()
        for agentaddr in agentAddresses:
          if agentaddr['udpPort'] == port:
            reusePort = True
        if reusePort == False:
          if getIPType(ipAddress):
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
          else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
          try:
            sock.bind(('', int(port)))
            sock.close()
          except:
            portValid = False

      if ipAddrValid == True and portValid == True:
        # make sure ip:port combo not already in use
        agentAddresses = getAgentAddresses()
        for agentaddr in agentAddresses:
          if agentaddr['ipAddr'] == ipAddress and agentaddr['udpPort'] == port:
            ipAddrValid = False
            portValid == False

      if ipAddrValid == False or portValid == False or ifValid == False:
        response=aa.cli_not_implemented("None")        # Just to get the proper format to return data and status
        response.content = {}                          # This method is used extensively throughout
        response.status_code = 409
        if ipAddrValid == False and portValid == False:
          message = "IP Address/port combination {}:{} is in use".format(ipAddress, port)
        if ipAddrValid == False:
          message = "{} is not a valid interface IP Address".format(ipAddress)
        elif portValid == False:
          message = "UDP port {} is not available".format(port)
        elif ifValid == False:
          message = "{} is not a valid interface".format(interface)
        response.set_error_message(message)
        return response

      entry = {}                    # if configuring, this tells set_entry to create it
      keypath = cc.Path('/restconf/data/ietf-snmp:snmp/engine')
      udp = {}
      udp['ip']   = ipAddress
      udp['port'] = int(port, 10)
      if len(interface) > 0:
        udp['ietf-snmp-ext:interface'] = interface
      listen = {'name' : key,
                'udp' : udp }
      body = { 'ietf-snmp:engine' : { 'listen' : [ listen ] }}
      response = aa.patch(keypath, body)

    return response

  # Get the configured communities.
  elif func == 'snmp_community_get':
    groupResps = invoke('snmp_group_member_get', None)
    groups = {}
    if groupResps.ok() and len(groupResps.content) != 0:
      for grpResponse in groupResps.content['group-member']:
        if grpResponse['security-model'] == 'v2c':                # communities only
          comm = grpResponse['security-name']
          grp =  grpResponse['name']
          groups[comm] = grp

    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/community')
    response=aa.get(keypath, None, False)
    data = []
    if response.ok() and len(response.content) != 0:
      if 'ietf-snmp:community' in response.content.keys():
        communities = response.content['ietf-snmp:community']
        for community in communities:
          if community['security-name'] == 'None':
            community['group'] = 'None'
          else:
            community['group'] = groups[community['index']]
        response.content['community'] = sorted(communities, key=itemgetter('index'))
    else:
      response = None
    return response

  # Configure a new community.
  elif func == 'snmp_community_add':
    invoke('snmp_community_delete', [args[0]])     # delete community config if it already exists
    group="None"
    if (1<len(args)):
      group=args[1]
    entry=collections.defaultdict(dict)
    entry["community"]=[{ "index": args[0],
                          "security-name" : group }]
    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/community')
    response = aa.patch(keypath, entry)
    if response.ok() and not group == "None":
      member = [group, args[0], 'v2c']
      response = invoke('snmp_group_member_add', member)
    return response

  # Remove a community.
  elif func == 'snmp_community_delete':
    group = 'None'
    groupResps = invoke('snmp_group_member_get', None)
    if groupResps.ok():
      for grpResponse in groupResps.content['group-member']:
        if grpResponse['security-name'] == args[0] and grpResponse['security-model'] == 'v2c':
          group = grpResponse['name']
          break

    member = [group, args[0]]
    response = invoke('snmp_group_member_del', member)

    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/community={index}', index=args[0])
    response = aa.delete(keypath)
    return response

#============================================================================
  # Get the configured member groups.
  elif func == 'snmp_group_member_get':
    groups = []
    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/vacm/group')
    response = aa.get(keypath, None, False)
    if response.ok() and len(response.content) != 0:
      if 'ietf-snmp:group' in response.content.keys():
        groupDict = response.content['ietf-snmp:group']
        while len(groupDict) > 0:
          row = groupDict.pop(0)
          group = row['name']

          if 'member' in row.keys():
            members = row['member']
            for member in members:
              g = {}
              g['name'] = group
              g['security-name'] = member['security-name']
              secModel = member['security-model']
              g['security-model'] = secModel.pop()
              groups.append(g)

          else:
            path = '/restconf/data/ietf-snmp:snmp/vacm/group={name}/member'
            keypath = cc.Path(path, name = group)
            response = aa.get(keypath, None, False)
            if response.ok() and len(response.content) != 0:
              if 'ietf-snmp:member' in response.content.keys():
                data = response.content['ietf-snmp:member']
                while len(data) > 0:
                  entry = data.pop(0)
                  g = {}
                  g['name'] = group
                  g['security-name'] = entry['security-name']
                  g['security-model'] = entry['security-model']
                  groups.append(g)

      response=aa.cli_not_implemented("group")              # just to get the proper format
      response.content = {}
      response.status_code = 200
      response.content['group-member'] = sorted(groups, key=itemgetter('name', 'security-model', 'security-name'))
    else:
      response=aa.cli_not_implemented("group")              # just to get the proper format
      response.content = {}
      response.status_code = 404

    return response

  elif func == 'snmp_group_member_add':
    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/vacm')
    memberEntry =  { "security-name": args[1],
                     "security-model": [ args[2] ] }
    groupEntry =   { "name": args[0],
                     "member": [ memberEntry ] }
    vacmEntry = { "group": [ groupEntry ]  }
    body = { "ietf-snmp:vacm": vacmEntry }

    response = aa.patch(keypath, body)
    return response

  # Remove an member group.
  elif func == 'snmp_group_member_del':
    path = '/restconf/data/ietf-snmp:snmp/vacm/group={name}/member={secName}'
    keypath = cc.Path(path, name=args[0], secName=args[1])
    response = aa.delete(keypath)

    # only delete master key if all access and all member entries are removed.
    if response.ok() or entryNotFound(response):
      manageGroupMasterKey(args[0])

    return response
#============================================================================

  # Get the configured access groups.
  elif func == 'snmp_group_access_get':
    groups = []
    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/vacm/group')
    response = aa.get(keypath, None, False)
    if response.ok() and len(response.content) != 0:
      if 'ietf-snmp:group' in response.content.keys():
        groupDict = response.content['ietf-snmp:group']
        while len(groupDict) > 0:
          row = groupDict.pop(0)
          group = row['name']
          if 'access' in row.keys():
            access = row['access']

            while len(access) > 0:
              entry = access.pop(0)
              if 'read-view' in entry.keys():
                g = {}
                g['name'] = group
                g['context'] = entry['context']
                secModel = entry['security-model']
                if secModel == "usm":
                  g['model'] = 'v3'
                else:
                  g['model'] = secModel
                g['security'] = entry['security-level']
                g['read-view']   = entry['read-view']
                g['write-view']  = entry['write-view']
                g['notify-view'] = entry['notify-view']
                groups.append(g)

      response=aa.cli_not_implemented("group")              # just to get the proper format
      response.content = {}
      response.status_code = 204
      response.content['group-access'] = sorted(groups, key=itemgetter('name', 'model', 'security'))
    else:
      response=aa.cli_not_implemented("group")              # just to get the proper format
      response.content = {}
      response.status_code = 404
      response.content['group-member'] = groups

    return response

  # Add an access group.
  elif func == 'snmp_group_access_add':
    secModel = SecurityModels[args[1]]
    if secModel == 'usm':
      secLevel = SecurityLevels[args[2]]
      index = 3
    else:
      secLevel = 'no-auth-no-priv'
      index = 2
    argsList = []
    if len(args) >  index:
      argsList = args[index:]
    viewOpts = { 'read' : 'None', 'write' : 'None', 'notify' : 'None'}
    argsDict = dict(zip(*[iter(argsList)]*2))
    for key in argsDict:
      viewOpts[key] = argsDict[key]

    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/vacm')
    accessEntry = { "context": "Default",
                    "security-model": secModel,
                    "security-level": secLevel,
                    "read-view": viewOpts['read'],
                    "write-view": viewOpts['write'],
                    "notify-view": viewOpts['notify'] }
    groupEntry =   { "name": args[0],
                     "access": [ accessEntry ] }
    vacmEntry = { "group": [ groupEntry ]  }
    body = { "ietf-snmp:vacm": vacmEntry }

    response = aa.patch(keypath, body)
    return response

  # Remove an access group.
  elif func == 'snmp_group_access_delete':
    secModel = SecurityModels[args[1]]
    if secModel == 'usm':
      secLevel = SecurityLevels[args[2]]
    else:
      secLevel = 'no-auth-no-priv'

    path = '/restconf/data/ietf-snmp:snmp/vacm/group={name}/access={contextName},{securityModel},{securityLevel}'
    keypath = cc.Path(path, name=args[0], contextName="Default", securityModel=secModel, securityLevel=secLevel)
    response = aa.delete(keypath)

    # only delete master key if all access and all member entries are removed.
    if response.ok() or entryNotFound(response):
      manageGroupMasterKey(args[0])

    return response

  # Get the configured views.
  elif func == 'snmp_view_get':
    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/vacm/view')
    response=aa.get(keypath, None, False)
    views = []
    if response.ok():
      content = response.content
      if 'ietf-snmp:view' in response.content.keys():
        for key, data in response.content.items():
          while len(data) > 0:
            row = data.pop(0)
            for action in ['include', 'exclude']:
              if row.has_key(action):
                for oidTree in row[action]:
                  v = {}
                  v['name'] = row['name']
                  v['type'] = action+'d'
                  v['oid'] = oidTree
                  views.append(v)
                  response.content = {'view' : sorted(views, key=itemgetter('name', 'oid'))}
      else:
        response = None
    return response

  # Add a view.
  elif func == 'snmp_view_add':
    action = args[2].rstrip('d')      # one of 'exclude' or 'include'
    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/vacm')
    viewEntry =  { "name": args[0],
                   action : [ args[1] ] }
    vacmEntry = { "view": [ viewEntry ]  }
    body = { "ietf-snmp:vacm": vacmEntry }
    response = aa.patch(keypath, body)
    return response

  # Remove a view.
  elif func == 'snmp_view_delete':
    for action in ['exclude', 'include']:
      # though only one exists, extraneous action appears harmless
      path = '/restconf/data/ietf-snmp:snmp/vacm/view={name}/%s={oidtree}' %action
      keypath = cc.Path(path, name=args[0], oidtree=args[1])
      response = aa.delete(keypath)

    path = '/restconf/data/ietf-snmp:snmp/vacm/view={name}'
    keypath = cc.Path(path, name=args[0])
    response=aa.get(keypath, None, False)
    if response.ok():
      if 'ietf-snmp:view' in response.content.keys():
        for key, data in response.content.items():
          while len(data) > 0:
            row = data.pop(0)
            notfound = True
            for action in ['include', 'exclude']:
              if row.has_key(action):
                notfound = False
            if notfound == True:
              response = aa.delete(keypath)

    return response

  # Get the configured users.
  elif func == 'snmp_user_get':
    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/usm/local/user')
    response=aa.get(keypath, None, False)

    users = []
    if response.ok() and len(response.content) != 0:
      if 'ietf-snmp:user' in response.content.keys():
        for key, data in response.content.items():
          while len(data) > 0:
            row = data.pop(0)
            u = {}
            u['username'] = row['name']
            u['group'] = 'None'
            groupResps = invoke('snmp_group_member_get', None)
            for grpResponse in groupResps.content['group-member']:
              if grpResponse['security-name'] == u['username'] and grpResponse['security-model'] == 'usm':
                u['group'] = grpResponse['name']
                break

            auth = row['auth']
            if auth.has_key('md5'):
              u['auth'] = 'md5'
            elif auth.has_key('sha'):
              u['auth'] = 'sha'
            else:
              u['auth'] = 'None'
            key = auth[u['auth']]
            value = key['key']
            value = value.encode('ascii')
            value = value.translate(None, ':')
            if value == '00000000000000000000000000000000':
              u['auth'] = 'None'

            u['priv'] = 'None'
            if row.has_key('priv'):
              priv = row['priv']
              if priv.has_key('aes'):
                u['priv'] = 'aes'
              elif priv.has_key('des'):
                u['priv'] = 'des'
              else:
                u['priv'] = 'None'
              key = priv[u['priv']]
              value = key['key']
              value = value.encode('ascii')
              value = value.translate(None, ':')
              if value == '00000000000000000000000000000000':
                u['priv'] = 'None'
              if u['priv'] == 'aes':
                u['priv'] = 'aes-128'

            users.append(u)
      response.content = {'user' : users}
    else:
      response = None

    return response

  elif func == 'snmp_user_add':
    user = args.pop(0)
    invoke('snmp_user_delete', [user])        # delete user config if it already exists

    engineID = getEngineID()
    group = 'None'
    if args.count("group") > 0:
      index = args.index("group")
      group = args.pop(index+1)
      args.pop(index)

    encrypted = False
    if len(args) > 0 and args[0].lower() == 'encrypted':
      # check if authentication is encrypted
      encrypted = True
      args.pop(0)

    authType = None
    authPassword = '00000000000000000000000000000000'
    authKey = None
    if len(args) > 0 and args[0].lower() == 'auth':
    # At this point, only authentication and privacy information remain in args[]. Parse that.
    # 'auth' will always be the first argument. Don't need it.
      args.pop(0)
      authType = args.pop(0).lower()
      if authType in ['md5', 'sha']:
        args.pop(0)   # remove 'auth-password'
        authPassword = args.pop(0)
      elif authType == 'noauth':
        authType = None

    privType = None
    privPassword = '00000000000000000000000000000000'
    privKey = None
    if len(args) > 0 and args[0].lower() == 'priv':
    # At this point, only privacy information remains in args[]. Parse that.
    # 'priv' will always be the first argument. Don't need it.
      args.pop(0)
      privType = args.pop(0).lower()
      if privType == 'aes-128':
        privType = 'aes'
      if privType in ['des', 'aes']:
        args.pop(0)   # remove 'priv-password'
        privPassword = args.pop(0)

    if authType == None:
      authType = "md5"
      privType = "des"
    elif not (encrypted):
      privacyType = privType
      if privType == None:
        privacyType = "des"
      try:
        rc = subprocess.check_output(["snmpkey", authType, authPassword, engineID, privacyType, privPassword])
      except:
        response = aa.cli_not_implemented("None")
        response.set_error_message("Cannot compute md5 key for user %s" %user)
        return response

      authStr, crlf, privStr = rc.partition('\n')
      securityDict = {}
      if crlf == '\n':        # split was good
        for element in authStr, privStr:
          key, space, data = element.partition(' ')
          if space == ' ':          # split was good
            securityDict[key.rstrip(':')] = data[2:].rstrip() # trim prepended '0x' from the encrypted value and trailing colon from key
      if len(securityDict) > 0:    # good authentication and privacy key are found
        authPassword = securityDict['authKey']
        if not privType == None:
          privPassword = securityDict['privKey']

    authKey = createYangHexStr(authPassword)
    privKey = createYangHexStr(privPassword)

    payload = {}
    payload["name"] = user
    payload["auth"] = { authType : { "key": authKey}}
    if not privType == None:
      payload["priv"] = { privType : { "key": privKey}}

    entry=collections.defaultdict(dict)
    entry["user"]=[payload]
    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/usm/local/user')
    response = aa.patch(keypath, entry)
    if response.ok():
      member = [group, user, 'usm']
      response = invoke('snmp_group_member_add', member)
    return response

  # Remove a user.
  elif func == 'snmp_user_delete':
    groupResps = invoke('snmp_group_member_get', None)
    group = 'None'
    if groupResps.ok() and len(groupResps.content) != 0:
      for grpResponse in groupResps.content['group-member']:
        if grpResponse['security-name'] == args[0] and grpResponse['security-model'] == 'usm':
          group = grpResponse['name']
          break
    member = [group, args[0]]
    groupResps = invoke('snmp_group_member_del', member)

    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/usm/local/user={index}', index=args[0])
    response = aa.delete(keypath)
    return response

  # Get the configured hosts.
  elif func == 'snmp_host_get':
    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/target')
    response=aa.get(keypath, None, False)
    hosts4_c = []
    hosts4_u = []
    hosts6_c = []
    hosts6_u = []
    if response.ok():
      if 'ietf-snmp:target' in response.content.keys():
        for key, table in response.content.items():
          hosts4_c, hosts6_c, hosts4_u, hosts6_u = ([] for i in range(4))
          while len(table) > 0:
            data = table.pop(0)
            h = {}
            h['target'] = data['target-params']
            udp = data['udp']
            h['ipaddr'] = udp['ip']
            h['port'] = udp['port']
            h['ip6'] = getIPType(h['ipaddr'])
            for key, value in data.items():
              if key == 'target-params':
                path = cc.Path('/restconf/data/ietf-snmp:snmp/target-params={name}', name=data[key])
                params=aa.get(path, None, False)
                if response.ok():
                  if 'ietf-snmp:target-params' in params.content.keys():
                    data = params.content['ietf-snmp:target-params']
                    while len(data) > 0:
                      entry = data.pop(0)
                      if 'v1' in entry:
                        security = entry['v1']
                        h['version'] = 'v1'
                        h['security-name'] = security['security-name']
                      elif 'v2c' in entry:
                        security = entry['v2c']
                        h['version'] = 'v2c'
                        h['security-name'] = security['security-name']
                      elif 'usm' in entry:
                        security = entry['usm']
                        h['version'] = 'usm'
                        h['user-name'] = security['user-name']
                        h['security-level'] = security['security-level']
              if key == 'tag':
                tag = value[0]
                if tag.endswith("Notify"):
                  h['trapOrInform'] = tag[:-6]
                else:
                  h['trapOrInform'] = tag
              h[key] = value
            if 'timeout' in h:
              h['timeout'] = h['timeout']/100  # displayed in seconds
            if "user-name" not in h:
              if not h['ip6']:
                hosts4_c.append(h)
              else:
                hosts6_c.append(h)
            else:
              if not h['ip6']:
                hosts4_u.append(h)
              else:
                hosts6_u.append(h)

    if len(hosts4_c) == 0 and len(hosts6_c) == 0 and len(hosts4_u) == 0 and len(hosts6_u) == 0:
      response=aa.cli_not_implemented("None")        # Just to get the proper format to return data and status
      response.content = {}                          # This method is used extensively throughout
      response.status_code = 404
      message = "Resource not found"
      response.set_error_message(message)
      return response
    else:
      response.content = { "community" : sorted(hosts4_c, key=lambda i: ipaddress.ip_address(i['ipaddr'])) + sorted(hosts6_c, key=lambda i: ipaddress.ip_address(i['ipaddr'])),
                           "user"      : sorted(hosts4_u, key=lambda i: ipaddress.ip_address(i['ipaddr'])) + sorted(hosts6_u, key=lambda i: ipaddress.ip_address(i['ipaddr'])) }
    return response

  # Add a host.
  elif func == 'snmp_host_add':
    host = args[0]
    key = findKeyForTargetEntry(host)
    if key == 'None':
      key = findNextKeyForTargetEntry(host)

    type = 'trapNotify'
    if 'user' == args[1]:
      secModel = SecurityModels['v3']
    else:
      secModel = SecurityModels['v2c']                   # v1 is not supported, v2c should be default
    secName = args[2]
    additionalArgs = args[3:]

    response = invoke('snmp_host_delete', [host])        # delete user config if it already exists
    secLevel = SecurityLevels['noauth']
    timeout = '15'
    retries = '3'
    udpPort = '162'
    srcIf = None
    ifValid = False

    # parameter parsing
    # optional arguments 'interface', 'port', and for informs, 'timeout' & 'retries'
    # 'traps' and 'informs' are mutually exclusive but one or the other is required.
    if 'interface' in additionalArgs:
      # record interface and remove from optional params
      index = additionalArgs.index('interface')
      srcIf = additionalArgs.pop(index + 1)
      additionalArgs.pop(index)
    if 'port' in additionalArgs:
      # record port and remove from optional params
      index = additionalArgs.index('port')
      udpPort = additionalArgs.pop(index + 1)
      additionalArgs.pop(index)
    if 'timeout' in additionalArgs:
      # record timeout and remove from optional params
        index = additionalArgs.index('timeout')
        timeout = additionalArgs.pop(index + 1)
        additionalArgs.pop(index)
    if 'retries' in additionalArgs:
      # record retires and remove from optional params
        index = additionalArgs.index('retries')
        retries = additionalArgs.pop(index + 1)
        additionalArgs.pop(index)
    #end of additional/optional paramters

    if len(additionalArgs)>0:
      type = additionalArgs.pop(0)
      type = type.rstrip('s')+'Notify'      # one of 'trapNotify' or 'informNotify'
      if secModel == SecurityModels['v3']:
        secLevel = SecurityLevels[additionalArgs.pop(0)]
      if len(additionalArgs) > 0:
        if type == 'trapNotify':
          secModel = additionalArgs.pop(0)
    else:
      type = 'trapNotify'

    # parameter checking
    # informs can never be 'v1'
    if type == 'informNotify' and secModel == SecurityModels['v1']:
      secModel = SecurityModels['v2c']
    if srcIf == 'mgmt' :
      ifValid = True
    elif not srcIf == None:
      standard_mode = is_in_standard_mode()
      if_names = interfaces_list() if standard_mode else netifaces.interfaces()
      if srcIf in if_names:
          ifValid = True

    tag = [ type ]
    if ifValid == True:
      tag.append(srcIf)
    elif not srcIf == None:
      response=aa.cli_not_implemented("None")        # Just to get the proper format to return data and status
      response.content = {}
      response.status_code = 409
      message = "{} is not a valid interface".format(srcIf)
      response.set_error_message(message)
      return response

    targetEntry=collections.defaultdict(dict)
    targetEntry["target"]=[{ "name": key,
                             "timeout": 100*int(timeout),
                             "retries": int(retries),
                             "target-params": key,
                             "tag": tag,
                             "udp" : { "ip": host, "port": int(udpPort)}
                             }]
    if secModel == 'usm':
      security = { "user-name": secName,
                   "security-level": secLevel}
    else:
      security = { "security-name": secName}

    targetParams=collections.defaultdict(dict)
    targetParams["target-params"]=[{ "name": key,
                                     secModel : security }]


    # since it is the targetParams is a leafref to "target-params",
    # target-params must be written first
    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/target-params')
    response = aa.patch(keypath, targetParams)

    if response.ok():
      keypath = cc.Path('/restconf/data/ietf-snmp:snmp/target')
      response = aa.patch(keypath, targetEntry)

    return response

  # Remove a host.
  elif func == 'snmp_host_delete':
    key = findKeyForTargetEntry(args[0])
    keypath = cc.Path('/restconf/data/ietf-snmp:snmp/target={name}', name=key)
    response = aa.delete(keypath)
    if response.ok():
      keypath = cc.Path('/restconf/data/ietf-snmp:snmp/target-params={name}', name=key)
      response = aa.delete(keypath)
    return response

  # Clear SNMP counters
  elif func == 'snmp_clear_counters':
    keypath = cc.Path('/restconf/operations/sonic-snmp:clear-counters')
    response = aa.post(keypath)
    return response

  # Show SNMP counters
  elif func == 'snmp_show_counters':
    keypath = cc.Path('/restconf/operations/sonic-snmp:show-counters')
    response = aa.post(keypath)
    return response

  else:
      print("%Error: %func not implemented "+func)
      exit(1)

  return None

def run(func, args):
  try:
    api_response = invoke(func, args)

    if api_response == None:
      return
    elif api_response.ok():
      if func == 'snmp_get':
        show_cli_output(args[0], api_response.content['system'])
        temp = api_response.content['global']
        if len(temp)>0:
          show_cli_output('show_snmp_agentaddr.j2', temp['agentAddr'])
      elif func == 'snmp_community_get':
        show_cli_output(args[0], api_response.content['community'])
      elif func == 'snmp_show_counters':
          show_cli_output('show_snmp_counters.j2', api_response.content['sonic-snmp:output']['counters'])
      elif func == 'snmp_view_get':
        show_cli_output(args[0], api_response.content['view'])
      elif func == 'snmp_group_access_get':
        show_cli_output(args[0], api_response.content['group-access'])
      elif func == 'snmp_user_get':
        show_cli_output(args[0], api_response.content['user'])
      elif func == 'snmp_host_get':
        show_cli_output(args[0], api_response.content['community'])
        show_cli_output('show_snmp_host_user.j2', api_response.content['user'])
    else:
      if api_response.status_code == 404:               # Resource not found
        return
      else:
        print (api_response.error_message())

  except:
    # system/network error
    syslog.syslog(syslog.LOG_ERR, "Exception: " + traceback.format_exc())
    print "%Error: Transaction Failure"

if __name__ == '__main__':
  pipestr().write(sys.argv)
  run(sys.argv[1], sys.argv[2:])
