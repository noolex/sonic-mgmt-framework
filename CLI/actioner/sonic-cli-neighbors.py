# Copyright 2019 Dell, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###########################################################################

import syslog as log
import sys
import cli_client as cc
import ipaddress
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output

import urllib3
urllib3.disable_warnings()

#Define globals
vrfDict = {}
macDict = {}
inputDict = {}
intfList = []
egressPortDict = {}
isMacDictAvailable = False
apiClient = cc.ApiClient()
PREFIX = 0
PREFIXIP = 1

def get_keypath(func,args):
    keypath = None
    instance = None
    body = None

    rcvdIntfName = inputDict.get('intf')
    if rcvdIntfName == None:
        rcvdIntfName = ""
    elif rcvdIntfName == "phy-if-name":
        rcvdIntfName = inputDict.get('phyIf')
    elif rcvdIntfName == "vlan-if-name":
        rcvdIntfName = inputDict.get('vlanIf')
    elif rcvdIntfName == "po-if-name":
        rcvdIntfName = inputDict.get('poIf')
    elif rcvdIntfName == "mgmt-if-name":
        rcvdIntfName = inputDict.get('mgmtIf')
    else:
        rcvdIntfName = inputDict.get('intf')

    rcvdIpAddr = inputDict.get('ip')
    if rcvdIpAddr == None:
        rcvdIpAddr = ""

    rcvdFamily = inputDict.get('family')
    if rcvdFamily == None:
        rcvdFamily = ""

    rcvdVrf = inputDict.get('vrf')
    if rcvdVrf == None:
        rcvdVrf = ""

#keypath for 'show ip/ipv6 arp/neighbors'
    if func == 'get_nbrs':
        intf = ""

        namespace = '/restconf/data/openconfig-interfaces:interfaces/interface={name}'
        if len(rcvdIntfName) > 0:
            intf = rcvdIntfName
        else:
            intf = args

        if len(intf) == 0:
            return None

        if intf.lower().startswith('vlan'):
            namespace = namespace + "/openconfig-vlan:routed-vlan"
        else:
            namespace = namespace + "/subinterfaces/subinterface={index}"

        if (rcvdFamily.lower() == "ipv4"):
            namespace = namespace + '/openconfig-if-ip:ipv4/neighbors'
        else:
            namespace = namespace + '/openconfig-if-ip:ipv6/neighbors'

        if len(rcvdIpAddr) > 0:
            msgType = PREFIXIP
            namespace = namespace + '/neighbor=' + rcvdIpAddr

        keypath = cc.Path(namespace, name=intf, index="0")

#keypath for 'clear ip/ipv6 arp/neighbors'
    elif func == 'rpc_sonic_clear_neighbors':
        keypath = cc.Path('/restconf/operations/sonic-neighbor:clear-neighbors')
        if rcvdVrf == "all":
            body = {"sonic-neighbor:input":{"family": rcvdFamily, "ip": rcvdIpAddr, "ifname": rcvdIntfName, "all_vrfs": True}}
        else:
            body = {"sonic-neighbor:input":{"family": rcvdFamily, "ip": rcvdIpAddr, "ifname": rcvdIntfName, "vrf": rcvdVrf}}
    elif func == 'set_ipv4_arp_timeout':
        keypath = cc.Path('/restconf/data/sonic-neighbor:sonic-neighbor/NEIGH_GLOBAL/NEIGH_GLOBAL_LIST')
        body = {"sonic-neighbor:NEIGH_GLOBAL_LIST": [{"sonic-neighbor:name": "Values", "sonic-neighbor:ipv4_arp_timeout": int(args[0])}]}
    elif func == 'set_ipv6_nd_cache_expiry':
        keypath = cc.Path('/restconf/data/sonic-neighbor:sonic-neighbor/NEIGH_GLOBAL/NEIGH_GLOBAL_LIST')
        body = {"sonic-neighbor:NEIGH_GLOBAL_LIST": [{"sonic-neighbor:name": "Values", "sonic-neighbor:ipv6_nd_cache_expiry": int(args[0])}]}
    elif func == 'del_ipv4_arp_timeout':
        keypath = cc.Path('/restconf/data/sonic-neighbor:sonic-neighbor/NEIGH_GLOBAL/NEIGH_GLOBAL_LIST=Values/ipv4_arp_timeout')
    elif func == 'del_ipv6_nd_cache_expiry':
        keypath = cc.Path('/restconf/data/sonic-neighbor:sonic-neighbor/NEIGH_GLOBAL/NEIGH_GLOBAL_LIST=Values/ipv6_nd_cache_expiry')

    return keypath, body

def build_mac_list():
    global macDict
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/fdb/mac-table/entries', name='default')

    try:
        response = apiClient.get(keypath)
        response = response.content
        if response is None:
            return

        macContainer = response.get('openconfig-network-instance:entries')
        if macContainer is None:
            return

        macList = macContainer.get('entry')
        if macList is None:
            return

        for macEntry in macList:
            vlan = macEntry.get('vlan')
            if vlan is None:
                continue

            mac = macEntry.get('mac-address')
            if mac is None:
                continue

            macIntf = macEntry.get('interface')
            if macIntf is None:
                continue

            intfRef = macIntf.get('interface-ref')
            if intfRef is None:
                continue

            state = intfRef.get('state')
            if state is None:
                continue

            intf = state.get('interface')
            if intf is None:
                continue

            key = "Vlan" + str(vlan) + "-" + mac.lower()
            macDict[key] = intf
    except Exception as e:
        log.syslog(log.LOG_ERR, str(e))
        print "% Error: Internal error"

def get_egress_port(ifName, macAddr):
    global isMacDictAvailable
    if ifName.startswith('Vlan'):
        if isMacDictAvailable is False:
            build_mac_list()
            isMacDictAvailable = True
        key = ifName + "-" + macAddr
        egressPort = macDict.get(key)
        if egressPort is None:
            egressPort= "-"
        return egressPort
    return "-"

def isMgmtVrfEnabled():
    try:
        request = "/restconf/data/openconfig-network-instance:network-instances/network-instance=mgmt/state/enabled/"

        response = apiClient.get(request)
        response = response.content

        if not response:
            return False

        response = response.get('openconfig-network-instance:enabled')
        if response is None:
            return False
        else:
            return response

    except Exception as e:
        log.syslog(log.LOG_ERR, str(e))
        print "% Error: Internal error"

    return False

def build_vrf_list():
    global vrfDict
    tIntf = ("/restconf/data/sonic-interface:sonic-interface/INTERFACE/",
             "sonic-interface:INTERFACE",
             "INTERFACE_LIST",
             "portname")

    tVlanIntf = ("/restconf/data/sonic-vlan-interface:sonic-vlan-interface/VLAN_INTERFACE/",
                 "sonic-vlan-interface:VLAN_INTERFACE",
                 "VLAN_INTERFACE_LIST",
                 "vlanName")

    tPortChannelIntf = ("/restconf/data/sonic-portchannel-interface:sonic-portchannel-interface/PORTCHANNEL_INTERFACE/",
                        "sonic-portchannel-interface:PORTCHANNEL_INTERFACE",
                        "PORTCHANNEL_INTERFACE_LIST",
                        "pch_name")


    requests = [tIntf, tVlanIntf, tPortChannelIntf]

    for request in requests:
        keypath = cc.Path(request[0])

        try:
            response = apiClient.get(keypath)
            response = response.content
            if response is None:
                continue

            intfsContainer = response.get(request[1])
            if intfsContainer is None:
                continue

            intfsList = intfsContainer.get(request[2])
            if intfsList is None:
                continue

            for intf in intfsList:
                portName = intf.get(request[3])
                if portName is None:
                    continue

                vrfName = intf.get('vrf_name')
                vrfDict[portName] = vrfName

        except Exception as e:
            log.syslog(log.LOG_ERR, str(e))
            print "% Error: Internal error"
            break

    if isMgmtVrfEnabled():
        vrfDict["eth0"] = "mgmt"
    else:
        vrfDict["eth0"] = None

def process_nbrs(response, rcvdIntfName, outputList, msgType):
    if rcvdIntfName is None:
        return

    rcvdIpAddr  = inputDict.get('ip')
    if rcvdIpAddr is not None:
        rcvdIpAddr = rcvdIpAddr.lower()

    rcvdMacAddr = inputDict.get('mac')
    rcvdFamily  = inputDict.get('family')

    if msgType is PREFIX:
        nbrsContainer = response.get('openconfig-if-ip:neighbors')
        if nbrsContainer:
            nbrsList = nbrsContainer.get('neighbor')
    elif msgType is PREFIXIP:
        nbrsList = response.get('openconfig-if-ip:neighbor')

    if nbrsList is None:
        return

    for nbr in nbrsList:
        egressPort = "-"

        state = nbr.get('state')
        if state is None:
           continue

        ipAddr = state.get('ip')
        if ipAddr is None or ipAddr == "0.0.0.0":
            continue

        macAddr = state.get('link-layer-address')
        if macAddr is None:
            continue

        egressPort = get_egress_port(rcvdIntfName, macAddr)

        if rcvdIntfName == "eth0":
            rcvdIntfName = "Management0"

        nbrEntry = {'ipAddr':ipaddress.ip_address(ipAddr),
                    'macAddr':macAddr,
                    'intfName':rcvdIntfName,
                    'egressPort':egressPort
                    }

        if (rcvdMacAddr == macAddr):
            outputList.append(nbrEntry)
        elif (rcvdIpAddr == ipAddr.lower()):
            outputList.append(nbrEntry)
        elif (rcvdIpAddr is None and rcvdMacAddr is None):
            outputList.append(nbrEntry)

    return outputList

def clear_neighbors(keypath, body):
    status = ""
    try:
        apiResponse = apiClient.post(keypath,body)
    except:
        # system/network error
        print "Error: Unable to connect to the server"
        return

    if apiResponse.ok():
        response = apiResponse.content
    else:
        print "% Error: Internal error"
        return

    if 'sonic-neighbor:output' in response.keys():
        status = response.get('sonic-neighbor:output')
        if status is None:
            return

        status = status.get('response')
        if status is None:
            return

        if "255" in status:
            status = "Unable to clear all entries, please try again"

        if status != "Success":
            print status
    else:
        return

def set_neighbors(keypath, body, del_req):
    if del_req:
        apiResponse = apiClient.delete(keypath)
    else:
        apiResponse = apiClient.patch(keypath, body)

    if apiResponse.ok():
        response = apiResponse.content
    else:
        print(apiResponse.error_message())
        return -1
    return 0

def show_neighbors(func):
    global inputDict
    msgType = PREFIX
    keypath = ""
    outputList = []
    rcvdVrfName = inputDict.get('vrf')
    rcvdIp = inputDict.get('ip')
    if rcvdIp is not None:
        rcvdIp = rcvdIp.lower()

    rendererScript = "arp_show.j2"

    rcvdFamily = inputDict.get('family')
    if rcvdFamily == None:
        rcvdFamily = "ipv4"
    else:
        rcvdFamily = rcvdFamily.lower()

    if rcvdFamily == "ipv6":
        rendererScript = "arp_show_v6.j2"

    summary = inputDict.get('summary')
    if summary is not None:
        rendererScript = "arp_summary_show.j2"

    rcvdIntf = inputDict.get('intf')
    if rcvdIntf is not None:
        keypath, body = get_keypath(func, rcvdIntf)
        try:
            apiResponse = apiClient.get(keypath)
        except:
            # system/network error
            print "Error: Unable to connect to the server"
            return

        if apiResponse.ok():
            response = apiResponse.content
        else:
            print "% Error: Internal error"
            return
        if response:
            outputList = process_nbrs(response, rcvdIntf, outputList, PREFIX)
    else:
        for intf, vrf in vrfDict.items():
            if ((vrf is None and rcvdVrfName is None) or
                (vrf == rcvdVrfName) or
                rcvdVrfName == "all"):
                keypath, body = get_keypath(func, intf)
            else:
                continue

            try:
                apiResponse = apiClient.get(keypath)
            except:
                # system/network error
                print "Error: Unable to connect to the server"
                return

            if apiResponse.ok():
                response = apiResponse.content
            else:
                print "% Error: Internal error"
                continue

            if (response is None) or (len(response) == 0):
                continue

            outputList = process_nbrs(response, intf, outputList, msgType)

    if len(outputList) > 0 :
        outputList =  sorted(outputList, key=lambda k: k['ipAddr'])
        show_cli_output(rendererScript, outputList)

def process_args(args):
  global inputDict

  for arg in args:
        tmp = arg.split(":", 1)
        if not len(tmp) == 2:
            continue
        if tmp[1] == "":
            tmp[1] = None
        inputDict[tmp[0]] = tmp[1]

def run(func, args):
    global macDict
    global vrfDict
    global inputDict
    global egressPortDict
    status = 0

    process_args(args)
    build_vrf_list()

    if (func == 'rpc_sonic_clear_neighbors'):
        keypath, body = get_keypath(func, args)
        clear_neighbors(keypath, body)
    elif (func == 'set_ipv4_arp_timeout') or (func == 'set_ipv6_nd_cache_expiry'):
        keypath, body = get_keypath(func, args)
        status = set_neighbors(keypath, body, False)
    elif (func == 'del_ipv4_arp_timeout') or (func == 'del_ipv6_nd_cache_expiry'):
        keypath, body = get_keypath(func, args)
        status = set_neighbors(keypath, body, True)
    elif(func == ('get_nbrs')):
        show_neighbors(func)

    macDict = {}
    vrfDict = {}
    inputDict = {}
    egressPortDict = {}
    isMacDictAvailable = False
    return status

if __name__ == '__main__':
    pipestr().write(sys.argv)
    status = run(sys.argv[1], sys.argv[2:])
    if status != 0:
        sys.exit(0)
