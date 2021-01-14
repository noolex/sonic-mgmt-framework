#!/usr/bin/python
###########################################################################
#
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

import sys
import time
import json
import ast
from rpipe_utils import pipestr
import cli_client as cc
from netaddr import *
from scripts.render_cli import show_cli_output
import subprocess
import syslog
import traceback
from natsort import natsorted
import sonic_intf_utils as ifutils
from sonic_cli_if_range import check_response
from collections import OrderedDict 
import sonic_cli_show_config

import urllib3
urllib3.disable_warnings()

lag_type_map = {"active" : "LACP", "on": "STATIC"}

def filter_address(d, isIPv4):
    if d is None:
        return
    if 'sonic-mgmt-interface:MGMT_INTF_TABLE_IPADDR_LIST' in d:
        ipData = d['sonic-mgmt-interface:MGMT_INTF_TABLE_IPADDR_LIST']
        newIpData = []
        for l in ipData:
            for k, v in l.items():
               if k == "ipPrefix":
                  ip = IPNetwork(v)
                  if isIPv4:
                      if ip.version == 4:
                          newIpData.append(l)
                  else:
                      if ip.version == 6:
                          newIpData.append(l)
        del ipData[:]
        ipData.extend(newIpData)

    if 'sonic-interface:INTF_TABLE_IPADDR_LIST' in d:
        ipData = d['sonic-interface:INTF_TABLE_IPADDR_LIST']
        newIpData = []
        for l in ipData:
            for k, v in l.items():
               if k == "ipPrefix":
                  ip = IPNetwork(v)
                  if isIPv4:
                      if ip.version == 4:
                          newIpData.append(l)
                  else:
                      if ip.version == 6:
                          newIpData.append(l)
        del ipData[:]
        ipData.extend(newIpData)

    if 'sonic-interface:VLAN_SUB_INTERFACE_IPADDR_LIST' in d:
        ipData = d['sonic-interface:VLAN_SUB_INTERFACE_IPADDR_LIST']
        newIpData = []
        for l in ipData:
            for k, v in l.items():
               if k == "ip_prefix":
                  ip = IPNetwork(v)
                  if isIPv4:
                      if ip.version == 4:
                          newIpData.append(l)
                  else:
                      if ip.version == 6:
                          newIpData.append(l)
        del ipData[:]
        ipData.extend(newIpData)

def get_helper_adr_str(args):
    ipAdrStr = ""
    for index,i in  enumerate(args):
        if (args[2] == 'ip'):
           if not ((i.find(".") == -1)):
              ipAdrStr += i
              ipAdrStr += ","
        elif (args[2] == 'ipv6'):
           if not ((i.find(":") == -1)):
              ipAdrStr += i
              ipAdrStr += ","

    return ipAdrStr[:-1];

def build_relay_address_info (args):
    api = cc.ApiClient()
    output = {}

    if len(args) < 0:
        return output

    tIntf = ("/restconf/data/sonic-interface:sonic-interface/INTERFACE/INTERFACE_LIST",
             "sonic-interface:INTERFACE_LIST",
             "portname")
    tVlanIntf = ("/restconf/data/sonic-vlan:sonic-vlan/VLAN/VLAN_LIST",
                 "sonic-vlan:VLAN_LIST",
                 "name")
    tPortChannelIntf = ("/restconf/data/sonic-portchannel-interface:sonic-portchannel-interface/PORTCHANNEL_INTERFACE/PORTCHANNEL_INTERFACE_LIST",
                        "sonic-portchannel-interface:PORTCHANNEL_INTERFACE_LIST",
                        "pch_name")

    requests = [tIntf, tVlanIntf, tPortChannelIntf]

    reqStr = args[0]
    for request in requests:
        keypath = cc.Path(request[0])
        try:
            response = api.get(keypath)
            response = response.content
            if not response is None:
                intfsList = response.get(request[1])
            if not intfsList is None:
                for intf in intfsList:
                    intfName = intf.get(request[2])
                    if not intfName is None:
                        if not ((reqStr.find("ipv6") == -1)):
                            relay_addresses = intf.get('dhcpv6_servers')
                        elif not ((reqStr.find("ip") == -1)):
                            relay_addresses = intf.get('dhcp_servers')
                        if not relay_addresses is None:
                            output[intfName] = relay_addresses
        except  Exception as e:
            log.syslog(log.LOG_ERR, str(e))
            print "%Error: Internal error"
    return output

def vlanFullList():
    fullList = []
    for i in range (1,4095):
        fullList.append(str(i))
    return fullList

def vlanExceptList(vlan):
    exceptStr = ''
    exceptList = vlanFullList()
    vlanList = vlan.split(',')
    for vid in vlanList:
        if '-' in vid:
            vid = vid.replace('-','..')
        if '..' in vid:
            vidList = vid.split('..')
            lower = int(vidList[0])
            upper = int(vidList[1])
            for i in range(lower,upper+1):
                vid = str(i)
                if vid in exceptList:
                    exceptList.remove(vid)
        else:
            exceptList.remove(vid)
            
    exceptStr = ','.join(exceptList)
            
    return exceptStr
    
def invoke_api(func, args=[]):
    api = cc.ApiClient()

    # handle interfaces using the 'switch' mode
    if func == 'if_config':
        if args[0] == 'phy-if-name' or args[0] == 'vlan-if-name':
            body = { "openconfig-interfaces:interfaces": { "interface": [{ "name": args[1], "config": { "name": args[1] }} ]}}
            path = cc.Path('/restconf/data/openconfig-interfaces:interfaces')
            return api.patch(path, body)
        elif args[0] == 'phy-sub-if-name':
            parent_if = args[1].split('.')[0]
            sub_if = int(args[1].split('.')[1])
            body = { "openconfig-interfaces:subinterfaces": { "subinterface": [{ "index": sub_if, "config": { "index": sub_if }} ]}}
            path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces', name=parent_if)
            return api.patch(path, body)

    # Create interface
    if func == 'patch_openconfig_interfaces_interfaces_interface':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}', name=args[0])
        return api.patch(path)
        
    elif func == 'patch_openconfig_interfaces_interfaces_interface_config':
        body = { "openconfig-interfaces:config": { "name": args[0] }}
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/config', name=args[0])
        return api.patch(path, body)

    #Configure PortChannel
    elif func == 'portchannel_config':
        if '.' in args[0]:
            parent_if = args[0].split('.')[0]
            sub_if = int(args[0].split('.')[1])
            body = { "openconfig-interfaces:subinterfaces": { "subinterface": [{ "index": sub_if, "config": { "index": sub_if }} ]}}
            path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces', name=parent_if)
            return api.patch(path, body)
        body ={
                 "openconfig-interfaces:interfaces": { "interface": [{
                                                      "name": args[0],
                                                      "config": {"name": args[0]},
                                                      "openconfig-if-aggregate:aggregation" : {"config": {}}
                                                    }]}
               }

        # Configure lag type (active/on)
        mode = args[1].split("=")[1]
        if mode != "" :
            body["openconfig-interfaces:interfaces"]["interface"][0]["openconfig-if-aggregate:aggregation"]["config"].update( {"lag-type": lag_type_map[mode] } )

        # Configure Min links
        links = args[2].split("=")[1]
        if links != "":
            body["openconfig-interfaces:interfaces"]["interface"][0]["openconfig-if-aggregate:aggregation"]["config"].update( {"min-links": int(links) } )

        # Configure Fallback
        fallback = args[3].split("=")[1]
        if fallback != "":
            body["openconfig-interfaces:interfaces"]["interface"][0]["openconfig-if-aggregate:aggregation"]["config"].update( {"openconfig-interfaces-ext:fallback": True} )

        # Configure Fast Rate
        fastRate = args[4].split("=")[1]
        if fastRate != "":
            body["openconfig-interfaces:interfaces"]["interface"][0]["openconfig-if-aggregate:aggregation"]["config"].update( {"openconfig-interfaces-ext:fast-rate": True} )

        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces')
        return api.patch(path, body)

    
    # Delete interface
    elif func == 'delete_openconfig_interfaces_interfaces_interface':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}', name=args[0])
        return api.delete(path)
    
    #Configure description
    elif func == 'patch_openconfig_interfaces_interfaces_interface_config_description':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/config/description', name=args[0])
        body = { "openconfig-interfaces:description": args[1] }
        return api.patch(path,body)
        
    # Enable or diable interface
    elif func == 'patch_openconfig_interfaces_interfaces_interface_config_enabled':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/config/enabled', name=args[0])
        if args[1] == "True":
           body = { "openconfig-interfaces:enabled": True }
        else:
           body = { "openconfig-interfaces:enabled": False }
        return api.patch(path, body)
        
    # Configure MTU
    elif func == 'patch_openconfig_interfaces_interfaces_interface_config_mtu':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/config/mtu', name=args[0])
        body = { "openconfig-interfaces:mtu":  int(args[1]) }
        return api.patch(path, body)
        
    elif func == 'patch_openconfig_if_ethernet_interfaces_interface_ethernet_config_auto_negotiate':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-ethernet:ethernet/config/auto-negotiate', name=args[0])
        if args[1] == "true":
            body = { "openconfig-if-ethernet:auto-negotiate": True }
        else :
            body = { "openconfig-if-ethernet:auto-negotiate": False }
        return api.patch(path, body)
        
    elif func == 'patch_openconfig_if_ethernet_interfaces_interface_ethernet_config_port_speed':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-ethernet:ethernet/config/port-speed', name=args[0])
        speed_map = {"10MBPS":"SPEED_10MB", "100MBPS":"SPEED_100MB", "1GIGE":"SPEED_1GB", "10GIGE":"SPEED_10GB",
                        "25GIGE":"SPEED_25GB", "40GIGE":"SPEED_40GB", "100GIGE":"SPEED_100GB"}
        if args[1] not in speed_map.keys():
            print("%Error: Unsupported speed")
            return None
        else:
            speed = speed_map.get(args[1])
            body = { "openconfig-if-ethernet:port-speed": speed }
        return api.patch(path, body)

    elif func == 'patch_openconfig_if_ethernet_interfaces_interface_ethernet_config_port_fec':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-ethernet:ethernet/config/openconfig-if-ethernet-ext2:port-fec', name=args[0])
        fec_map = {"RS": "FEC_RS", "FC": "FEC_FC", "off": "FEC_DISABLED", "default": "FEC_AUTO"}

        fec = args[1]
        if fec not in fec_map:
            print("%Error: Invalid port FEC config")
            return None

        body = { "openconfig-if-ethernet:port-fec": fec_map[fec]}
        return api.patch(path, body)

    elif func == 'patch_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ipv4_addresses_address_config':
        sp = args[1].split('/')
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses', name=args[0], index="0")
        if len(args) > 2 and len(args[2]) > 0:
            body = { "openconfig-if-ip:addresses": {"address":[ {"ip":sp[0], "openconfig-if-ip:config":  {"ip" : sp[0], "prefix-length" : int(sp[1]), "openconfig-interfaces-ext:gw-addr": args[2]} }]}}
        else:
            body = { "openconfig-if-ip:addresses": {"address":[ {"ip":sp[0], "openconfig-if-ip:config":  {"ip" : sp[0], "prefix-length" : int(sp[1])} }]}}
        return api.patch(path, body)
    
    elif func == 'patch_openconfig_if_ip_interfaces_interface_routed_vlan_ipv4_addresses_address_config':
        sp = args[1].split('/')
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/addresses', name=args[0])
        body = { "openconfig-if-ip:addresses": {"address":[ {"ip":sp[0], "openconfig-if-ip:config":  {"ip" : sp[0], "prefix-length" : int(sp[1])} }]}}
        return api.patch(path, body)    
    
    elif func == 'patch_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ipv6_addresses_address_config':
        parent_if=args[0]
        sub_if="0"
        if '.' in parent_if:
            parent_if = args[0].split('.')[0]
            sub_if = args[0].split('.')[1]
        parent_if = parent_if.replace("po", "PortChannel")
        sp = args[1].split('/')
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses', name=parent_if, index=sub_if)
        if len(args) > 2 and len(args[2]) > 0:
            body = { "openconfig-if-ip:addresses": {"address":[ {"ip":sp[0], "openconfig-if-ip:config":  {"ip" : sp[0], "prefix-length" : int(sp[1]), "openconfig-interfaces-ext:gw-addr": args[2]} }]}}
        else:
            body = { "openconfig-if-ip:addresses": {"address":[ {"ip":sp[0], "openconfig-if-ip:config":  {"ip" : sp[0], "prefix-length" : int(sp[1])} }]}}
        return api.patch(path, body)
        
    elif func == 'patch_if_ipv4':
        parent_if=args[0]
        sub_if="0"
        if '.' in parent_if:
            parent_if = args[0].split('.')[0]
            sub_if = args[0].split('.')[1]
        parent_if = parent_if.replace("po", "PortChannel")
        sp = args[1].split('/')
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses', name=parent_if, index=sub_if)
        if len(args) > 2 and args[2] == "secondary":
            body = { "openconfig-if-ip:addresses": {"address":[ {"ip":sp[0], "openconfig-if-ip:config":  {"ip" : sp[0], "prefix-length" : int(sp[1]), "openconfig-interfaces-ext:secondary": True} }]}}
        else:
            body = { "openconfig-if-ip:addresses": {"address":[ {"ip":sp[0], "openconfig-if-ip:config":  {"ip" : sp[0], "prefix-length" : int(sp[1])} }]}}
        return api.patch(path, body)

    elif func == 'patch_vlan_if_ipv4':
        sp = args[1].split('/')
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/addresses', name=args[0])

        if len(args) > 2 and args[2] == "secondary":
            body = { "openconfig-if-ip:addresses": {"address":[ {"ip":sp[0], "openconfig-if-ip:config":  {"ip" : sp[0], "prefix-length" : int(sp[1]), "openconfig-interfaces-ext:secondary": True} }]}}
        else:
            body = { "openconfig-if-ip:addresses": {"address":[ {"ip":sp[0], "openconfig-if-ip:config":  {"ip" : sp[0], "prefix-length" : int(sp[1])} }]}}
        return api.patch(path, body)

    elif func == 'patch_mgmt_if_ipv4':
        sp = args[1].split('/')
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses', name=args[0], index="0")

        body = { "openconfig-if-ip:addresses": {"address":[ {"ip":sp[0], "openconfig-if-ip:config":  {"ip" : sp[0], "prefix-length" : int(sp[1])} }]}}

        if len(args) > 2 and args[2] == "secondary":
            body["openconfig-if-ip:addresses"]["address"][0]["openconfig-if-ip:config"].update( {"openconfig-interfaces-ext:secondary": True} )

        if len(args) > 3 and args[2] == "gwaddr":
            body["openconfig-if-ip:addresses"]["address"][0]["openconfig-if-ip:config"].update({ "openconfig-interfaces-ext:gw-addr": args[3]} )

        return api.patch(path, body)


    elif func == 'patch_openconfig_if_ip_interfaces_interface_routed_vlan_ipv6_addresses_address_config':
        sp = args[1].split('/')
    
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/addresses', name=args[0])
        body = { "openconfig-if-ip:addresses": {"address":[ {"ip":sp[0], "openconfig-if-ip:config":  {"ip" : sp[0], "prefix-length" : int(sp[1])} }]}}
        return api.patch(path, body)
    
    elif func == 'patch_openconfig_vlan_interfaces_interface_ethernet_switched_vlan_config':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-ethernet:ethernet/openconfig-vlan:switched-vlan/config', name=args[0])
        if args[1] == "ACCESS":
           body = {"openconfig-vlan:config": {"interface-mode": "ACCESS","access-vlan": int(args[2])}}
        else:
           vlanlst = args[2].split(',')
           vlanlst = [sub.replace('-', '..') for sub in vlanlst]
           body = {"openconfig-vlan:config": {"interface-mode": "TRUNK","trunk-vlans": [int(i) if '..' not in i else i for i in vlanlst]}}

        return api.patch(path, body)

    elif func == 'put_openconfig_vlan_interfaces_interface_ethernet_switched_vlan_config':
	vlanlst = args[2].split(',')
	vlanlst = [sub.replace('-', '..') for sub in vlanlst]
	path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-ethernet:ethernet/openconfig-vlan:switched-vlan/config/trunk-vlans', name=args[0])
	body = {"openconfig-vlan:trunk-vlans":[int(i) if '..' not in i else i for i in vlanlst]}
        return api.put(path,body)

    elif func == 'patch_openconfig_vlan_interfaces_interface_aggregation_switched_vlan_config':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-aggregate:aggregation/openconfig-vlan:switched-vlan/config', name=args[0])
        if args[1] == "ACCESS":
           body = {"openconfig-vlan:config": {"interface-mode": "ACCESS","access-vlan": int(args[2])}}
        else:
           vlanlst = args[2].split(',')
           vlanlst = [sub.replace('-', '..') for sub in vlanlst]
           body = {"openconfig-vlan:config": {"interface-mode": "TRUNK","trunk-vlans": [int(i) if '..' not in i else i for i in vlanlst]}}
        return api.patch(path, body)

    elif func == 'put_openconfig_vlan_interfaces_interface_aggregation_switched_vlan_config':
        vlanlst = args[2].split(',')
	vlanlst = [sub.replace('-', '..') for sub in vlanlst]
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-aggregate:aggregation/openconfig-vlan:switched-vlan/config/trunk-vlans', name=args[0])
        body = {"openconfig-vlan:trunk-vlans":[int(i) if '..' not in i else i for i in vlanlst]}
        return api.put(path,body)


    elif func == 'delete_openconfig_vlan_interfaces_interface_ethernet_switched_vlan_config_access_vlan':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-ethernet:ethernet/openconfig-vlan:switched-vlan/config/access-vlan', name=args[0])
        return api.delete(path)
    elif func == 'delete_openconfig_vlan_interfaces_interface_aggregation_switched_vlan_config_access_vlan':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-aggregate:aggregation/openconfig-vlan:switched-vlan/config/access-vlan', name=args[0])
        return api.delete(path)

    elif func == 'del_llist_openconfig_vlan_interfaces_interface_ethernet_switched_vlan_config_trunk_vlans':
        vlanStr = args[2].replace('-', '..')
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-ethernet:ethernet/openconfig-vlan:switched-vlan/config/trunk-vlans={trunk}', name=args[0], trunk=vlanStr)
        return api.delete(path)
    
    elif func == 'del_llist_openconfig_vlan_interfaces_interface_ethernet_switched_vlan_config_trunk_vlans_all':
	path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-ethernet:ethernet/openconfig-vlan:switched-vlan/config/trunk-vlans',name=args[0])
	return api.delete(path)

    elif func == 'del_llist_openconfig_vlan_interfaces_interface_aggregation_switched_vlan_config_trunk_vlans':
        vlanStr = args[2].replace('-', '..')
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-aggregate:aggregation/openconfig-vlan:switched-vlan/config/trunk-vlans={trunk}', name=args[0], trunk=vlanStr)
        return api.delete(path)

    elif func == 'del_llist_openconfig_vlan_interfaces_interface_aggregation_switched_vlan_config_trunk_vlans_all':
	path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-aggregate:aggregation/openconfig-vlan:switched-vlan/config/trunk-vlans',name=args[0])
	return api.delete(path)

    elif func == 'rpc_replace_vlan':
        vlanlst = args[2].split(',')
        vlanlst = [sub.replace('-', '..') for sub in vlanlst]

        body = {"openconfig-interfaces-ext:input":{"ifname":[args[0]],"vlanlist":vlanlst}}
        path = cc.Path('/restconf/operations/openconfig-interfaces-ext:vlan-replace')
        return api.post(path,body)

    elif func == 'delete_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ipv4_addresses_address_config_prefix_length':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses/address={ip}/config/prefix-length', name=args[0], index="0", ip=args[1])
        return api.delete(path)
        
    elif func == 'delete_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ipv6_addresses_address_config_prefix_length':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses/address={ip}/config/prefix-length', name=args[0], index="0", ip=args[1])
        return api.delete(path)

    elif func == 'delete_phy_if_ip':
        if len(args) == 2:
            if args[1] == "True":
                path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses', name=args[0], index="0")
            else:
                path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses', name=args[0], index="0")

        else:
            if len(args) == 4 and args[3] == "secondary":
                body = {"sonic-interface:input":{"ifName":args[0].replace("po","PortChannel"),"ipPrefix":args[1],"secondary": True}}
            else:
                body = {"sonic-interface:input":{"ifName":args[0].replace("po","PortChannel"),"ipPrefix":args[1]}}
            path = cc.Path('/restconf/operations/sonic-interface:clear_ip')
            return api.post(path, body)
        return api.delete(path)

    elif func == 'delete_vlan_if_ip':
        if len(args) == 2:
            if args[1] == "True":
                path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/addresses', name=args[0])
            else:
                path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/addresses', name=args[0])
        else:
            if len(args) == 4 and args[3] == "secondary":
                body = {"sonic-interface:input":{"ifName":args[0],"ipPrefix":args[1],"secondary": True}}
            else:
                body = {"sonic-interface:input":{"ifName":args[0],"ipPrefix":args[1]}}
            path = cc.Path('/restconf/operations/sonic-interface:clear_ip')
            return api.post(path, body)
        return api.delete(path)

    elif func == 'delete_po_if_ip':
        if len(args) == 2:
            if args[1] == "True":
                path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses', name=args[0], index="0")
            else:
                path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses', name=args[0], index="0")
        else:
            if len(args) == 4 and args[3] == "secondary":
                body = {"sonic-interface:input":{"ifName":args[0],"ipPrefix":args[1],"secondary": True}}
            else:
                body = {"sonic-interface:input":{"ifName":args[0],"ipPrefix":args[1]}}
            path = cc.Path('/restconf/operations/sonic-interface:clear_ip')
            return api.post(path, body)
        return api.delete(path)

    elif func == 'delete_mgmt_if_ip':
        if len(args) == 2:
            if args[1] == "True":
                path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses', name=args[0], index="0")
            else:
                path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses', name=args[0], index="0")
        else:
            if len(args) == 4 and args[3] == "secondary":
                body = {"sonic-interface:input":{"ifName":args[0],"ipPrefix":args[1],"secondary": True}}
            else:
                body = {"sonic-interface:input":{"ifName":args[0],"ipPrefix":args[1]}}
            path = cc.Path('/restconf/operations/sonic-interface:clear_ip')
            return api.post(path, body)
        return api.delete(path)

    elif func == 'delete_lo_if_ip':
        if len(args) == 2:
            if args[1] == "True":
                path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses', name=args[0], index="0")
            else:
                path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses', name=args[0], index="0")
        else:
            if len(args) == 4 and args[3] == "secondary":
                body = {"sonic-interface:input":{"ifName":args[0],"ipPrefix":args[1],"secondary": True}}
            else:
                body = {"sonic-interface:input":{"ifName":args[0],"ipPrefix":args[1]}}
            path = cc.Path('/restconf/operations/sonic-interface:clear_ip')
            return api.post(path, body)
        return api.delete(path)
 
    elif func == 'get_openconfig_interfaces_interfaces_interface':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}', name=args[0])
        return api.get(path)

    elif func == 'get_sonic_port_sonic_port_port_table':
        path = cc.Path('/restconf/data/sonic-port:sonic-port/PORT_TABLE')
        return api.get(path)

    elif func == 'get_openconfig_interfaces_interfaces':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces')
        return api.get(path)
    elif func == 'ip_interfaces_get' or func == 'ip6_interfaces_get':
        d = {}

        path = cc.Path('/restconf/data/sonic-mgmt-interface:sonic-mgmt-interface/MGMT_INTF_TABLE/MGMT_INTF_TABLE_IPADDR_LIST')
        responseMgmtIntfTbl = api.get(path)
        if responseMgmtIntfTbl.ok():
            d.update(responseMgmtIntfTbl.content)
            mVrf = {}
            mVrf["isMgmtVrfEnabled"] = ifutils.isMgmtVrfEnabled(cc)
            d.update(mVrf)
            if func == 'ip_interfaces_get':
               filter_address(d, True)
            else:
               filter_address(d, False)

            path = cc.Path('/restconf/data/sonic-mgmt-port:sonic-mgmt-port/MGMT_PORT/MGMT_PORT_LIST')
            responseMgmtPortTbl = api.get(path)
            if responseMgmtPortTbl.ok():
                if 'sonic-mgmt-port:MGMT_PORT_LIST' in responseMgmtPortTbl.content:
                    for port in responseMgmtPortTbl.content['sonic-mgmt-port:MGMT_PORT_LIST']:
                        ifname = port['ifname']
                        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/state/oper-status', name=ifname)
                        responseMgmtPortOperStatus = api.get(path)
                        if responseMgmtPortOperStatus.ok():
                            port.update({'oper_status' : responseMgmtPortOperStatus.content['openconfig-interfaces:oper-status'].lower()})
                    d.update(responseMgmtPortTbl.content)


        path = cc.Path('/restconf/data/sonic-interface:sonic-interface/INTF_TABLE/INTF_TABLE_IPADDR_LIST')
        responseIntfTbl = api.get(path)
        if responseIntfTbl.ok():
            d.update(responseIntfTbl.content)
            tbl_key = "sonic-interface:INTF_TABLE_IPADDR_LIST"
            if tbl_key in d:
                d[tbl_key] = natsorted(d[tbl_key],key=lambda t: t["ifName"])
            if func == 'ip_interfaces_get':
                filter_address(d, True)
            else:
                filter_address(d, False)

        path = cc.Path('/restconf/data/sonic-interface:sonic-interface/INTF_TABLE/INTF_TABLE_LIST')
        responsePortTbl = api.get(path)
        if responsePortTbl.ok():
            d.update(responsePortTbl.content)
	
	path = cc.Path('/restconf/data/sonic-interface:sonic-interface/INTERFACE/INTERFACE_LIST')
        responseIntfVrfTbl =  api.get(path)
        if responseIntfVrfTbl.ok():
            d.update(responseIntfVrfTbl.content)

	
        path = cc.Path('/restconf/data/sonic-port:sonic-port/PORT_TABLE/PORT_TABLE_LIST')
        responsePortTbl = api.get(path)
        if responsePortTbl.ok():
            d.update(responsePortTbl.content)
	
	path = cc.Path('/restconf/data/sonic-loopback-interface:sonic-loopback-interface/LOOPBACK_INTERFACE/LOOPBACK_INTERFACE_LIST')
        responseLoopVrfTbl =  api.get(path)
        if responseLoopVrfTbl.ok():
            d.update(responseLoopVrfTbl.content)
	
        path = cc.Path('/restconf/data/sonic-portchannel:sonic-portchannel/LAG_TABLE/LAG_TABLE_LIST')
        responseLagTbl = api.get(path)
        if responseLagTbl.ok():
            d.update(responseLagTbl.content)
	
	path = cc.Path('/restconf/data/sonic-portchannel-interface:sonic-portchannel-interface/PORTCHANNEL_INTERFACE/PORTCHANNEL_INTERFACE_LIST')
        responseLagVrfTbl =  api.get(path)
        if responseLagVrfTbl.ok():
            d.update(responseLagVrfTbl.content)

        path = cc.Path('/restconf/data/sonic-vlan:sonic-vlan/VLAN_TABLE/VLAN_TABLE_LIST')
        responseVlanTbl =  api.get(path)
        if responseVlanTbl.ok():
            d.update(responseVlanTbl.content)
        
	path = cc.Path('/restconf/data/sonic-vlan-interface:sonic-vlan-interface/VLAN_INTERFACE/VLAN_INTERFACE_LIST')
        responseVlanVrfTbl =  api.get(path)
        if responseVlanVrfTbl.ok():
            d.update(responseVlanVrfTbl.content)

        path = cc.Path('/restconf/data/sonic-sag:sonic-sag/SAG_INTF/SAG_INTF_LIST')
        responseSAGTbl =  api.get(path)
        if responseSAGTbl.ok():
            if 'sonic-sag:SAG_INTF_LIST' in responseSAGTbl.content:
                for sag in responseSAGTbl.content['sonic-sag:SAG_INTF_LIST']:
                    if 'v6GwIp' in sag and func == 'ip_interfaces_get':
                        del sag['v6GwIp']
                    if 'v4GwIp' in sag and func == 'ip6_interfaces_get':
                        del sag['v4GwIp']
            d.update(responseSAGTbl.content)

        path = cc.Path('/restconf/data/sonic-interface:sonic-interface/VLAN_SUB_INTERFACE/VLAN_SUB_INTERFACE_IPADDR_LIST')
        responseSubIntfIpTbl =  api.get(path)
        if responseSubIntfIpTbl.ok():
            d.update(responseSubIntfIpTbl.content)
            if func == 'ip_interfaces_get':
               filter_address(d, True)
            else:
               filter_address(d, False)
        path = cc.Path('/restconf/data/sonic-interface:sonic-interface/VLAN_SUB_INTERFACE/VLAN_SUB_INTERFACE_LIST')
        responseSubIntfTbl =  api.get(path)
        if responseSubIntfTbl.ok():
            d.update(responseSubIntfTbl.content)

	return d
        
    # Add members to port-channel
    elif func == 'patch_openconfig_if_aggregate_interfaces_interface_ethernet_config_aggregate_id':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-ethernet:ethernet/config/openconfig-if-aggregate:aggregate-id', name=args[0])
        body = { "openconfig-if-aggregate:aggregate-id": args[1] }
        return api.patch(path, body)
    
    # Remove members from port-channel
    elif func == 'delete_openconfig_if_aggregate_interfaces_interface_ethernet_config_aggregate_id':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-ethernet:ethernet/config/openconfig-if-aggregate:aggregate-id', name=args[0])
        return api.delete(path)

    # Config min-links for port-channel
    elif func == 'patch_openconfig_if_aggregate_interfaces_interface_aggregation_config_min_links':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-aggregate:aggregation/config/min-links', name=args[0])
        body = { "openconfig-if-aggregate:min-links": int(args[1]) }
        return api.patch(path, body)
    
    # Config fallback mode for port-channel    
    elif func == 'patch_dell_intf_augments_interfaces_interface_aggregation_config_fallback':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-aggregate:aggregation/config/openconfig-interfaces-ext:fallback', name=args[0])
        if args[1] == "True":
            body = { "openconfig-interfaces-ext:fallback": True }
        else :
            body = { "openconfig-interfaces-ext:fallback": False }
        return api.patch(path, body)

    # Enable IGMP
    elif func == 'patch_openconfig_if_ip_enable_igmp':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/openconfig-igmp-ext:igmp/config/enabled', name=args[0], index="0")
        if args[1] == "True":
            body = {"openconfig-igmp-ext:enabled" : True}
        return api.patch(path, body)

    # Disable IGMP
    elif func == 'patch_openconfig_if_ip_disable_igmp':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/openconfig-igmp-ext:igmp/config', name=args[0], index="0")
        return api.delete(path)

    # Config IPv4 Unnumbered interface
    elif func == 'patch_intf_ipv4_unnumbered_intf':
        if "Vlan" in args[0]:
            path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/unnumbered/interface-ref/config/interface', name=args[0])
        else:
            path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/unnumbered/interface-ref/config/interface', name=args[0], index="0")

        body = { "openconfig-if-ip:interface" : args[1] }
        return api.patch(path, body)    
    elif func == 'delete_intf_ipv4_unnumbered_intf':
        if "Vlan" in args[0]:
            path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/unnumbered/interface-ref/config/interface', name=args[0])
        else:
            path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/unnumbered/interface-ref/config/interface', name=args[0], index="0")
        return api.delete(path)    
     
    # Configure static ARP
    elif func == 'patch_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_static_arp_config':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/neighbors', name=args[0], index="0")
        body = {"openconfig-if-ip:neighbors":{"neighbor":[{"ip":args[1],"config":{"ip":args[1],"link-layer-address":args[2]}}]}}
        return api.patch(path, body)

    # Delete static ARP
    elif func == 'delete_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_static_arp_config':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/neighbors/neighbor={sip}', name=args[0], index="0",sip=args[1])
        return api.delete(path)

    # Configure static ND
    elif func == 'patch_openconfig_if_ipv6_interfaces_interface_subinterfaces_subinterface_static_nd_config':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/neighbors', name=args[0], index="0")
        body = {"openconfig-if-ip:neighbors":{"neighbor":[{"ip":args[1],"config":{"ip":args[1],"link-layer-address":args[2]}}]}}
        return api.patch(path, body)

    # Delete static ND
    elif func == 'delete_openconfig_if_ipv6_interfaces_interface_subinterfaces_subinterface_static_nd_config':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/neighbors/neighbor={sip}', name=args[0], index="0",sip=args[1])
        return api.delete(path)

    # Configure static ARP - Routed Vlan interface
    elif func == 'patch_static_arp_config':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/neighbors', name=args[0], index="0")
        body = {"openconfig-if-ip:neighbors":{"neighbor":[{"ip":args[1],"config":{"ip":args[1],"link-layer-address":args[2]}}]}}
        return api.patch(path, body)

    # Delete static ARP - Routed Vlan interface
    elif func == 'delete_static_arp_config':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/neighbors/neighbor={sip}', name=args[0], index="0",sip=args[1])
        return api.delete(path)

    # Configure static ND - Routed vlan interface
    elif func == 'patch_static_nd_config':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/neighbors', name=args[0], index="0")
        body = {"openconfig-if-ip:neighbors":{"neighbor":[{"ip":args[1],"config":{"ip":args[1],"link-layer-address":args[2]}}]}}
        return api.patch(path, body)

    # Delete static ND - Routed vlan interface
    elif func == 'delete_static_nd_config':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/neighbors/neighbor={sip}', name=args[0], index="0",sip=args[1])
        return api.delete(path)

    elif func == 'patch_openconfig_relay_agent_relay_agent_dhcp_interfaces_interface_relay_agent_config':
        path1 = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/helper-address', id=args[0])
        body1 = {"openconfig-relay-agent:helper-address": [] }
        j=0
        helperConfig = ""
        srcIntf = ""
        linkSelect = ""
        MaxHopCount = ""
        serverVrf = ""
        selectVrf = ""
        policyAction = ""

        for index,i in  enumerate(args):
                #Find the ipv4 address from the list of args
                if not ((i.find(".") == -1)):
                   #Insert the found v4 address in the body
                   body1["openconfig-relay-agent:helper-address"].insert(j,args[index])
                   j += 1
                   helperConfig = "True"
                if ( i == "source-interface" ):
                   srcIntf = "True"
                   path2 = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/openconfig-relay-agent-ext:src-intf', id=args[0])
                   body2 = {"openconfig-relay-agent-ext:src-intf":  args[index+1] }
                elif ( i == "link-select" ):
                   linkSelect = "True"
                   path3 = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/openconfig-relay-agent-ext:link-select', id=args[0])
                   body3 = { "openconfig-relay-agent-ext:link-select": "ENABLE" }
                elif ( i == "max-hop-count" ):
                   MaxHopCount = "True"
                   path4 = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/openconfig-relay-agent-ext:max-hop-count', id=args[0])
                   body4 = {"openconfig-relay-agent-ext:max-hop-count": int(args[index+1]) }
                elif ( i == "vrf-name" ):
                   serverVrf = "True"
                   path5 = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/openconfig-relay-agent-ext:vrf', id=args[0])
                   body5 = {"openconfig-relay-agent-ext:vrf": args[index+1] }
                elif ( i == "vrf-select" ):
                   selectVrf = "True"
                   path6 = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/openconfig-relay-agent-ext:vrf-select', id=args[0])
                   body6 = {"openconfig-relay-agent-ext:vrf-select": "ENABLE" }
                elif ( i == "policy-action" ):
                   policyAction = "True"
                   path7 = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/openconfig-relay-agent-ext:policy-action', id=args[0])
                   body7 = {"openconfig-relay-agent-ext:policy-action": (args[index+1]).upper() }

        if (helperConfig == "True"):
           if (serverVrf ==  "True"):
               body1.update(body5)
           return  api.patch(path1, body1)
        elif ( srcIntf == "True" ):
           return  api.patch(path2, body2)
        elif ( linkSelect == "True"):
           return  api.patch(path3, body3)
        elif (MaxHopCount ==  "True"):
           return api.patch(path4, body4)
        elif (selectVrf ==  "True"):
           return api.patch(path6, body6)
        elif (policyAction ==  "True"):
           return api.patch(path7, body7)

    elif func == 'patch_openconfig_relay_agent_relay_agent_dhcpv6_interfaces_interface_relay_agent_config':
        path1 = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcpv6/interfaces/interface={id}/config/helper-address', id=args[0])
        body1 = {"openconfig-relay-agent:helper-address": [] }
        j=0
        helperConfig = ""
        srcIntf = ""
        linkSelect = ""
        MaxHopCount = ""
        serverVrf = ""
        selectVrf = ""

        for index,i in  enumerate(args):
                #Find the ipv6 address from the list of args
                if not ((i.find(":") == -1)):
                   #Insert the found v4 address in the body
                   body1["openconfig-relay-agent:helper-address"].insert(j,args[index])
                   j += 1
                   helperConfig = "True"
                if ( i == "source-interface" ):
                   srcIntf = "True"
                   path2 = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcpv6/interfaces/interface={id}/config/openconfig-relay-agent-ext:src-intf', id=args[0])
                   body2 = {"openconfig-relay-agent-ext:src-intf":  args[index+1] }
                elif ( i == "max-hop-count" ):
                   MaxHopCount = "True"
                   path3 = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcpv6/interfaces/interface={id}/config/openconfig-relay-agent-ext:max-hop-count', id=args[0])
                   body3 = {"openconfig-relay-agent-ext:max-hop-count": int(args[index+1]) }
                elif ( i == "vrf-name" ):
                   serverVrf = "True"
                   path4 = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcpv6/interfaces/interface={id}/config/openconfig-relay-agent-ext:vrf', id=args[0])
                   body4 = {"openconfig-relay-agent-ext:vrf": args[index+1] }
                elif ( i == "vrf-select" ):
                   selectVrf = "True"
                   path5 = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcpv6/interfaces/interface={id}/config/openconfig-relay-agent-ext:vrf-select', id=args[0])
                   body5 = {"openconfig-relay-agent-ext:vrf-select": "ENABLE"}

        if (helperConfig == "True"):
           if (serverVrf ==  "True"):
               body1.update(body4)
           return  api.patch(path1, body1)
        elif ( srcIntf == "True" ):
           return  api.patch(path2, body2)
        elif (MaxHopCount ==  "True"):
           return api.patch(path3, body3)
        elif (selectVrf ==  "True"):
           return api.patch(path5, body5)


    elif func == 'del_llist_openconfig_relay_agent_relay_agent_dhcp_interfaces_interface_relay_agent_config':
        ipAdrStr = ""
        ipAdrStr = get_helper_adr_str(args)
        helperAddress=ipAdrStr
        path1 = ""
        path = ""
        if len(helperAddress):
           #Delete specified ipv4 adresses
           path1 = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/helper-address={helperAddress}', id=args[0], helperAddress=ipAdrStr)
        elif len(args) == 4:
           #No adress specified so delete all the configured relay adressess
           path1 = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/helper-address', id=args[0])

        if (path1 != ""):
           api.delete(path1)
           path2 = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/helper-address', id=args[0])
           resp = api.get(path2)
           if  resp.ok():
              if not 'openconfig-relay-agent:helper-address' in resp.content:
                 path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/openconfig-relay-agent-ext:src-intf', id=args[0])
                 api.delete(path)
                 path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/openconfig-relay-agent-ext:link-select', id=args[0])
                 api.delete(path)
                 path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/openconfig-relay-agent-ext:max-hop-count', id=args[0])
                 api.delete(path)
                 path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/openconfig-relay-agent-ext:vrf', id=args[0])
                 api.delete(path)
                 path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/openconfig-relay-agent-ext:vrf-select', id=args[0])
                 api.delete(path)
                 path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/openconfig-relay-agent-ext:policy-action', id=args[0])
                 api.delete(path)

        for i in args:
           if ( i == "source-interface" ):
             path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/openconfig-relay-agent-ext:src-intf', id=args[0])
             api.delete(path)
           elif ( i == "link-select" ):
             path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/openconfig-relay-agent-ext:link-select', id=args[0])
             api.delete(path)
           elif ( i == "max-hop-count") :
             path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/openconfig-relay-agent-ext:max-hop-count', id=args[0])
             api.delete(path)
           elif ( i == "vrf-name") :
             path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/openconfig-relay-agent-ext:vrf', id=args[0])
             api.delete(path)
           elif ( i == "vrf-select") :
             path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/openconfig-relay-agent-ext:vrf-select', id=args[0])
             api.delete(path)
           elif ( i == "policy-action") :
             path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/config/openconfig-relay-agent-ext:policy-action', id=args[0])
             api.delete(path)

        if (path1 != ""):
           return api.delete(path1)
        if (path != ""):
           return api.delete(path)

    elif func == 'del_llist_openconfig_relay_agent_relay_agent_dhcpv6_interfaces_interface_relay_agent_config':
        ipAdrStr = ""
        ipAdrStr = get_helper_adr_str(args)
        helperAddress=ipAdrStr
        path1 = ""
        path = ""
        if len(helperAddress):
           #Delete specified ipv6 adresses
           path1 = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcpv6/interfaces/interface={id}/config/helper-address={helperAddress}', id=args[0], helperAddress=ipAdrStr)
        elif len(args) == 4:
           #No adress specified so delete all the configured relay adressess
           path1 = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcpv6/interfaces/interface={id}/config/helper-address', id=args[0])

        if (path1 != ""):
           api.delete(path1)
           path2 = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcpv6/interfaces/interface={id}/config/helper-address', id=args[0])
           resp = api.get(path2)
           if  resp.ok():
              if not 'openconfig-relay-agent:helper-address' in resp.content:
                 path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcpv6/interfaces/interface={id}/config/openconfig-relay-agent-ext:src-intf', id=args[0])
                 api.delete(path)
                 path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcpv6/interfaces/interface={id}/config/openconfig-relay-agent-ext:max-hop-count', id=args[0])
                 api.delete(path)
                 path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcpv6/interfaces/interface={id}/config/openconfig-relay-agent-ext:vrf', id=args[0])
                 api.delete(path)
                 path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcpv6/interfaces/interface={id}/config/openconfig-relay-agent-ext:vrf-select', id=args[0])
                 api.delete(path)

        for i in args:
           if ( i == "source-interface" ):
             path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcpv6/interfaces/interface={id}/config/openconfig-relay-agent-ext:src-intf', id=args[0])
             api.delete(path)
           elif ( i == "max-hop-count") :
             path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcpv6/interfaces/interface={id}/config/openconfig-relay-agent-ext:max-hop-count', id=args[0])
             api.delete(path)
           elif ( i == "vrf-name") :
             path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcpv6/interfaces/interface={id}/config/openconfig-relay-agent-ext:vrf', id=args[0])
             api.delete(path)
           elif ( i == "vrf-select") :
             path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcpv6/interfaces/interface={id}/config/openconfig-relay-agent-ext:vrf-select', id=args[0])
             api.delete(path)

        if (path1 != ""):
           return api.delete(path1)
        if (path != ""):
           return api.delete(path)

    elif func == 'get_openconfig_relay_agent_relay_agent':
        output = build_relay_address_info(args)
        show_cli_output('show_dhcp_relay_brief_sonic.j2', output)
        return api.get("")

    elif func == 'get_openconfig_relay_agent_relay_agent_dhcpv6':
        output = build_relay_address_info(args)
        show_cli_output('show_dhcp_relay_brief_sonic.j2', output)
        return api.get("")

    elif func == 'get_openconfig_relay_agent_relay_agent_dhcp_interfaces_interface_state':
        path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}/state', id=args[1])
        return api.get(path)

    elif func == 'get_openconfig_relay_agent_relay_agent_dhcpv6_interfaces_interface_state':
        path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcpv6/interfaces/interface={id}/state', id=args[1])
        return api.get(path)

    elif func == 'get_openconfig_relay_agent_relay_agent_detail':
        if not len(args) > 1:
           path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp')
        else:
           path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface={id}', id=args[1])
        return api.get(path)

    elif func == 'get_openconfig_relay_agent_relay_agent_detail_dhcpv6':
        if not len(args) > 1:
           path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcpv6')
        else:
           path = cc.Path('/restconf/data/openconfig-relay-agent:relay-agent/dhcpv6/interfaces/interface={id}', id=args[1])
        return api.get(path)
    elif func == 'default_port_config':
        path = cc.Path('/restconf/operations/sonic-config-mgmt:default-port-config')
        body = {"sonic-config-mgmt:input": { "ifname": args[0] }}
        resp = api.post(path, body)
        result = False
        if resp.ok() and resp.content is not None and \
           resp.content.get("sonic-config-mgmt:output") is not None and \
           resp.content.get("sonic-config-mgmt:output").get("status") is not None and \
           resp.content["sonic-config-mgmt:output"]["status"] == 0:
            result = True
        if not result:
            print("%Error: Failed to restore port " + args[0] + " to its default configuration")
        return resp
    elif func == 'rpc_interface_counters':
        ifname = args[1].split("=")[1]
        if ifname != "" :
            keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/state/counters', name=ifname)
            ifcounters = api.get(keypath)
            keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-ethernet:ethernet/state/counters', name=ifname)
            response = api.get(keypath)
            if response.ok():
                if response.content:
                    response.content[ifname] = ifcounters.content.pop("openconfig-interfaces:counters")
                    response.content[ifname].update(response.content["openconfig-if-ethernet:counters"].pop("openconfig-if-ethernet-ext2:eth-out-distribution"))
                    response.content[ifname].update(response.content["openconfig-if-ethernet:counters"].pop("openconfig-if-ethernet-ext2:eth-in-distribution"))
                    response.content[ifname].update(response.content.pop("openconfig-if-ethernet:counters"))

            return response
        else:
            keypath = cc.Path('/restconf/operations/sonic-counters:interface_counters')
        body = {}
        return api.post(keypath, body)
    elif func == 'showrun':
       arglen =0
       try:
         arglen = args.index('\\|')
       except ValueError:
         arglen = len(args)

       if arglen == 3:
         show_args=["views=configure-if,configure-lag,configure-vlan,configure-vxlan,configure-lo,configure-if-mgmt"]
         sonic_cli_show_config.run('show_multi_views',show_args)
       elif arglen > 3:
          show_args= ["views=configure-if"]
          intf = args[3]
          if intf is not None and type(intf)== str:
            if intf != "Ethernet" and intf != "Eth":
               view_key_str = "view_keys=\"name=" + intf + "\""
               show_args.append(view_key_str)
          sonic_cli_show_config.run('show_view',show_args)
       return
    return api.cli_not_implemented(func)

def getId(item):
    state_dict = item['state']
    ifName = state_dict['name']
    return ifutils.name_to_int_val(ifName)

def getSonicId(item):
    state_dict = item
    ifName = state_dict['ifname']
    return ifutils.name_to_int_val(ifName)

def get_all_eth_intfs_list():
    response = cc.ApiClient().get(cc.Path('/restconf/data/sonic-port:sonic-port/PORT/PORT_LIST'))
    if not(response and response.ok() and (response.content is not None) and ('sonic-port:PORT_LIST' in response.content)):
        return None

    intfList = []
    is_mode_std = ifutils.is_intf_naming_mode_std()
    for port_info in response.content['sonic-port:PORT_LIST']:
        if is_mode_std:
            intfList.append(port_info['alias'])
        else:
            intfList.append(port_info['ifname'])

    return sorted(intfList, key= lambda intf: [ifutils.name_to_int_val(intf)])

def hdl_get_all_ethernet(args):
    get_response = []
    response = {}

    for intf in get_all_eth_intfs_list():
        func = "get_openconfig_interfaces_interfaces_interface"
        intfargs = [intf]+args[0:]
        response = invoke_api(func, intfargs)
        if response and response.ok() and (response.content is not None) and ('openconfig-interfaces:interface' in response.content):
            get_response.append(response.content['openconfig-interfaces:interface'][0])

    if response and response.ok() and (response.content is not None) and ('openconfig-interfaces:interface' in response.content):
        response.content['openconfig-interfaces:interface'] = get_response
        return check_response(response, func, intfargs)

    return 0

def run(func, args):
   
    if func == 'rpc_relay_clear':
        api_clear = cc.ApiClient()
        if not (args[0].startswith("Eth") or args[0].startswith("Vlan") or args[0].startswith("PortChannel")):
           print("%Error: Invalid Interface")
           return 1

        path = cc.Path('/restconf/operations/sonic-counters:clear_relay_counters')
        body = {}

        if (args[2] == "ip"): 
            body = {"sonic-counters:input":{"ipv4-relay-param":args[0],"ipv6-relay-param":"NULL"}}
        elif (args[2] == "ipv6"):
            body = {"sonic-counters:input":{"ipv4-relay-param":"NULL","ipv6-relay-param":args[0]}}
        else:
            print("%Error: Invalid Interface family")
            return 1

        return api_clear.post(path,body)

    if func == "get_all_ethernet":
        return hdl_get_all_ethernet(args)

    if func == 'vlan_trunk_add_remove_ethernet':
	if args[2] == 'all':
	    args.insert(2,'1..4094')
	    func = 'patch_openconfig_vlan_interfaces_interface_ethernet_switched_vlan_config'
	elif args[2] == 'none':
	    func = 'del_llist_openconfig_vlan_interfaces_interface_ethernet_switched_vlan_config_trunk_vlans_all'
        elif args[3] == 'add':
            func = 'patch_openconfig_vlan_interfaces_interface_ethernet_switched_vlan_config'
        elif args[3] == 'remove':
            func = 'del_llist_openconfig_vlan_interfaces_interface_ethernet_switched_vlan_config_trunk_vlans'
	elif args[3] == 'except':
	    exceptStr = vlanExceptList(args[2])
	    args[2] = exceptStr
	    func = 'put_openconfig_vlan_interfaces_interface_ethernet_switched_vlan_config'
	else:
	    func = 'rpc_replace_vlan'

    if func == 'vlan_trunk_add_remove_portchannel':
	if args[2] == 'all':
	    args.insert(2,'1..4094')
	    func = 'patch_openconfig_vlan_interfaces_interface_aggregation_switched_vlan_config'
	elif args[2] == 'none':
	    func = 'del_llist_openconfig_vlan_interfaces_interface_aggregation_switched_vlan_config_trunk_vlans_all'
	elif args[3] == 'add':
	    func = 'patch_openconfig_vlan_interfaces_interface_aggregation_switched_vlan_config'
	elif args[3]=='remove':
	    func = 'del_llist_openconfig_vlan_interfaces_interface_aggregation_switched_vlan_config_trunk_vlans'
	elif args[3] == 'except':
	    exceptStr = vlanExceptList(args[2])
	    args[2] = exceptStr
	    func = 'put_openconfig_vlan_interfaces_interface_aggregation_switched_vlan_config'
	else:
	    func = 'rpc_replace_vlan'

    try:
        response = invoke_api(func, args)
        if func == 'ip_interfaces_get' or func == 'ip6_interfaces_get':
            show_cli_output(args[0], response)
            return
        elif func == 'showrun':
            return    
        if response.ok():
          if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("Failed")
                return 1

            if 'openconfig-interfaces:interfaces' in api_response:
                value = api_response['openconfig-interfaces:interfaces']
                if 'interface' in value:
                    tup = value['interface']
                    value['interface'] = sorted(tup, key=getId)
            elif 'sonic-port:PORT_TABLE' in api_response:
                value = api_response['sonic-port:PORT_TABLE']
                if 'PORT_TABLE_LIST' in value:
                    tup = value['PORT_TABLE_LIST']
                    value['PORT_TABLE_LIST'] =  sorted(tup, key=getSonicId)
            elif func == 'rpc_interface_counters' and 'sonic-counters:output' in api_response:
                value = api_response['sonic-counters:output']
                if value["status"] != 0:
                    print("%Error: Internal error.")
                    return 1
                if 'interfaces' in value:
                    interfaces = value['interfaces']
                    if 'interface' in interfaces:
                        tup = interfaces['interface']
                        value['interfaces']['interface'] = sorted(tup.items(), key= lambda item: [ifutils.name_to_int_val(item[0])])

            elif func == 'delete_phy_if_ip' or func == 'delete_mgmt_if_ip' or func == 'delete_vlan_if_ip' or func == 'delete_po_if_ip' or func == 'delete_lo_if_ip':
                if 'sonic-interface:output' in api_response:
                    value = api_response['sonic-interface:output']
                    if value["status"] != 0:
                        if value["status-detail"] != '':
                            print("%Error: {}".format(value["status-detail"]))
                        else:
                            print("%Error: Internal error.")

            elif func == 'rpc_replace_vlan':
                if 'openconfig-interfaces-ext:output' in api_response:
                    value = api_response['openconfig-interfaces-ext:output']
                    if value["status"] != 0:
                        if value["status-detail"] != '':
                            print("%Error: {}".format(value["status-detail"]))
                        else:
                            print("%Error: Internal error.")

            if func == 'get_openconfig_interfaces_interfaces_interface':
                show_cli_output(args[1], api_response)
            elif func == 'get_openconfig_interfaces_interfaces':
                show_cli_output(args[0], api_response)
            elif func == 'get_sonic_port_sonic_port_port_table':
                show_cli_output(args[0], api_response)
            elif func == 'get_openconfig_relay_agent_relay_agent_dhcp_interfaces_interface_state':
                show_cli_output(args[0], api_response)
            elif func == 'get_openconfig_relay_agent_relay_agent_dhcpv6_interfaces_interface_state':
                show_cli_output(args[0], api_response)
            elif func == 'get_openconfig_relay_agent_relay_agent_detail':
                show_cli_output(args[0], api_response)
            elif func == 'get_openconfig_relay_agent_relay_agent_detail_dhcpv6':
                show_cli_output(args[0], api_response)
            elif func == 'rpc_interface_counters':
                show_cli_output(args[0], api_response)

        else:
            print response.error_message()
            return 1

    except Exception as e:
        syslog.syslog(syslog.LOG_DEBUG, "Exception: " + traceback.format_exc())
        print("%Error: Transaction Failure")
        return 1

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])

