#!/usr/bin/python
###########################################################################
#
# Copyright 2020 Dell, Inc.
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
import os
from rpipe_utils import pipestr
import cli_client as cc
from netaddr import *
from scripts.render_cli import show_cli_output
import subprocess
import re
from sonic_intf_utils import name_to_int_val
from natsort import natsorted

import urllib3
urllib3.disable_warnings()

lag_type_map = {"active" : "LACP", "on": "STATIC"}

def getId(item):
    state_dict = item['state']
    ifName = state_dict['name']
    return name_to_int_val(ifName)

def getSonicId(item):
    state_dict = item
    ifName = state_dict['ifname']
    return name_to_int_val(ifName)

def intersection(lst1, lst2): 
    return list(set(lst1) & set(lst2)) 

# Function to expand range into list of individual interfaces
def rangetolst(givenifrange):
    temp = re.compile("(Vlan|PortChannel)([0-9].*)") #ex: Vlan1-10,20 or PortChannel20,1-10
    try:
        res = temp.match(givenifrange).groups()
    except:
        return None, None
    iftype = res[0]
    idlst = res[1].split(',')
    givenifrange = []
    for i in idlst:
        if "-" in i:
            sId, eId = map(int, i.split('-'))
            if sId > eId:
                givenifrange.extend(list(range(eId,sId+1)))
            givenifrange.extend(list(range(sId,eId+1)))
        else:
            givenifrange.append(i)
    ifrangelist = [iftype+str(i) for i in givenifrange]
    return iftype, ifrangelist

# Function to check if intf fall inside any subset in the range list
def check_in_range(ifName, rangelst):
    port_val = name_to_int_val(ifName)
    for r in rangelst:
        if "-" in r:
            sId, eId = map(lambda x : name_to_int_val("Eth"+x), r.split('-'))
            if (sId == eId) and (port_val) == sId:
                return True
            elif (sId < eId) and (sId <= port_val <= eId):
                return True
            elif (sId > eId) and (eId <= port_val <= sId):
                return True
        elif port_val == name_to_int_val("Eth"+r):
            return True

# Function to expand range to available physical interfaces list
# Param: Physical interface range string in standard or non-standard naming format
# Return: List of all available physical interfaces in the range
def eth_intf_range_expand(givenifrange):
    intf_list = set()
    temp = re.compile("(Eth|Ethernet)([0-9].*)") #ex: Ethernet1-10,20 or Eth1/1-1/10,1/5/2
    res = temp.match(givenifrange).groups()
    iftype = res[0]
    rangelst = res[1].split(',') #ex: [1-20,40,44-80] or [1/1-1/10,1/2/3]
    iflist = invoke_api("get_available_interface_names_list", [iftype])
    for p in iflist:
        #store the interfaces that fall inside any subset in the range
        if check_in_range(p, rangelst):
            intf_list.add(p)
    return list(intf_list)

def generate_body(func, args=[]):

    body = {}

    if func == 'patch_interface_config':
        body = {"name": args[0],"config": {"name": args[0]}}

    elif func == 'portchannel_config':
        body = {
                 "name": args[0],
                 "config": {"name": args[0]},
                 "openconfig-if-aggregate:aggregation" : {"config": {}}
               }

        # Configure lag type (active/on)
        mode = args[1].split("=")[1]
        if mode != "" :
            body["openconfig-if-aggregate:aggregation"]["config"].update( {"lag-type": lag_type_map[mode] } )

        # Configure Min links
        links = args[2].split("=")[1]
        if links != "":
            body["openconfig-if-aggregate:aggregation"]["config"].update( {"min-links": int(links) } )

        # Configure Fallback
        fallback = args[3].split("=")[1]
        if fallback != "":
            body["openconfig-if-aggregate:aggregation"]["config"].update( {"openconfig-interfaces-ext:fallback": True} )

        # Configure Fast Rate
        fast_rate = args[4].split("=")[1]
        if fast_rate != "":
            body["openconfig-if-aggregate:aggregation"]["config"].update( {"openconfig-interfaces-ext:fast_rate": True} )

    #Configure description
    elif func == 'patch_description':
        body = {"name": args[0],"config": {}}
        full_cmd = os.getenv('USER_COMMAND', None)
        match = re.search('description (["]?.*["]?)', full_cmd)
        if match:
            body["config"].update( {"description": match.group(1) } )
        else:
            body["config"].update( {"description": "" } )


    # Enable or diable interface
    elif func == 'patch_enabled':
        body = {"name": args[0],"config": {}}
        if args[1] == "True":
           body["config"].update( {"enabled": True} )
        else:
           body["config"].update( {"enabled": False} )
        
    # Configure MTU
    elif func == 'patch_mtu':
        body = {"name": args[0],"config": {}}
        body["config"].update( {"mtu": int(args[1])} )

    # Add members to port-channel
    elif func == 'patch_aggregate_id':
        body = {
                 "name": args[0],
                 "openconfig-if-ethernet:ethernet" : {"config": {}}
               }
        body["openconfig-if-ethernet:ethernet"]["config"].update( { "openconfig-if-aggregate:aggregate-id": args[1] } )
    
     #configure switchport
    elif func == 'patch_access_vlan':
        body = {
                 "name": args[0],
                 "config": {"name": args[0]},
                 "openconfig-if-ethernet:ethernet": {"openconfig-vlan:switched-vlan":{}}
        }
        body["openconfig-if-ethernet:ethernet"]["openconfig-vlan:switched-vlan"].update({"config": {"interface-mode": "ACCESS", "access-vlan": int(args[1])}})

    elif func == 'patch_trunk_vlan':
        vlanlst = args[1].split(',')
        vlanlst = [sub.replace('-', '..') for sub in vlanlst]

        body = {
                 "name": args[0],
                 "config": {"name": args[0]},
                 "openconfig-if-ethernet:ethernet": {"openconfig-vlan:switched-vlan":{}}
        }

        body["openconfig-if-ethernet:ethernet"]["openconfig-vlan:switched-vlan"].update({"config": {"interface-mode": "TRUNK", "trunk-vlans": [int(i) if '..' not in i else i for i in vlanlst]}}) 
   
    elif func == 'patch_aggregation_access_vlan':
        body = {
                 "name": args[0],
                 "config": {"name": args[0]},
                 "openconfig-if-aggregate:aggregation": {"openconfig-vlan:switched-vlan":{}}
        }
        body["openconfig-if-aggregate:aggregation"]["openconfig-vlan:switched-vlan"].update({"config": {"interface-mode": "ACCESS", "access-vlan": int(args[1])}})

    elif func == 'patch_aggregation_trunk_vlan':
        vlanlst = args[1].split(',')
        vlanlst = [sub.replace('-', '..') for sub in vlanlst]

        body = {
                 "name": args[0],
                 "config": {"name": args[0]},
                 "openconfig-if-aggregate:aggregation": {"openconfig-vlan:switched-vlan":{}}
        }

        body["openconfig-if-aggregate:aggregation"]["openconfig-vlan:switched-vlan"].update({"config": {"interface-mode": "TRUNK", "trunk-vlans": [int(i) if '..' not in i else i for i in vlanlst]}})

    # Speed config
    elif func == 'patch_port_speed':
        body = {
                 "name": args[0],
                 "openconfig-if-ethernet:ethernet" : {"config": {}}
               }

        speed_map = {"10MBPS":"SPEED_10MB", "100MBPS":"SPEED_100MB", "1GIGE":"SPEED_1GB", "auto":"SPEED_1GB", "10GIGE":"SPEED_10GB",
                        "25GIGE":"SPEED_25GB", "40GIGE":"SPEED_40GB", "100GIGE":"SPEED_100GB", "SPEED_UNKNOWN":"SPEED_UNKNOWN"}
        if args[1] not in speed_map.keys():
            print("%Error: Invalid port speed config")
            exit(1)
        else:
            speed = speed_map.get(args[1])
            body["openconfig-if-ethernet:ethernet"]["config"].update( { "openconfig-if-ethernet:port-speed": speed } )
    elif func == 'patch_ipv6_enabled':
        body = { "name": args[0] }
        if args[0].startswith("Vlan"):
            body.update({"openconfig-vlan:routed-vlan" : {"openconfig-if-ip:ipv6": {"config": {"enabled": bool(args[1])}}}})
        else:
            body.update({"subinterfaces" : {"subinterface": [ {"index": 0,"openconfig-if-ip:ipv6": {"config": {"enabled": bool(args[1])}}} ] }})

    else:
        print("%Error: %s not supported" % func)

    return body
        
 
def invoke_api(func, args=[]):
    api = cc.ApiClient()

    # Delete interface
    if func == 'delete_interface':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}', name=args[0])
        return api.delete(path)

    # Remove members from port-channel
    elif func == 'delete_aggregate_id':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-ethernet:ethernet/config/openconfig-if-aggregate:aggregate-id', name=args[0])
        return api.delete(path)

    #Remove access vlan
    elif func == 'delete_access_vlan':
	path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-ethernet:ethernet/openconfig-vlan:switched-vlan/config/access-vlan', name=args[0])
        return api.delete(path) 

    #Remove trunk vlan
    elif func == 'delete_trunk_vlan':
        vlanStr = args[1].replace('-', '..')
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-ethernet:ethernet/openconfig-vlan:switched-vlan/config/trunk-vlans={trunk}', name=args[0], trunk=vlanStr)
        return api.delete(path)

    #Remove aggregate access vlan
    elif func == 'delete_aggregate_access_vlan':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-aggregate:aggregation/openconfig-vlan:switched-vlan/config/access-vlan', name=args[0])
        return api.delete(path)

      #Remove aggregate trunk vlan
    elif func == 'delete_aggregate_trunk_vlan':
        vlanStr = args[1].replace('-', '..')
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-aggregate:aggregation/openconfig-vlan:switched-vlan/config/trunk-vlans={trunk}', name=args[0], trunk=vlanStr)
        return api.delete(path)

    # Remove IP addresses from interface
    elif func == 'delete_if_ip':
	if args[0].startswith("Vlan"):
            path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/addresses', name=args[0])
        else:
            path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses', name=args[0], index="0")
        return api.delete(path)
    elif func == 'delete_if_ip6':
	if args[0].startswith("Vlan"):
            path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/addresses', name=args[0])
        else:
            path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses', name=args[0], index="0")
        return api.delete(path)

    # Disable IPv6
    elif func == 'delete_if_ip6_enabled':
	if args[0].startswith("Vlan"):
            path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/config/enabled', name=args[0])
        else:
            path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/config/enabled', name=args[0], index="0")
        return api.delete(path)

    # Get interface
    elif func == 'get_openconfig_interfaces_interfaces_interface':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}', name=args[0])
        return api.get(path)
    elif func == 'get_sonic_port_sonic_port_port_table':
        path = cc.Path('/restconf/data/sonic-port:sonic-port/PORT_TABLE')
        return api.get(path)
    elif func == 'get_openconfig_interfaces_interfaces':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces')
        return api.get(path)

    elif func == 'get_available_interface_names_list':
	iflist = [] #To store list of existing intefaces of given interface type
	if args[0].startswith("Eth") :
            path = cc.Path('/restconf/data/sonic-port:sonic-port/PORT_TABLE/PORT_TABLE_LIST')
            responsePortTbl = api.get(path)
            if responsePortTbl.ok():
		intf_map = responsePortTbl.content
                tbl_key = "sonic-port:PORT_TABLE_LIST"
		if tbl_key in intf_map:
		    iflist = [i["ifname"] for i in intf_map[tbl_key] if i["ifname"].startswith("Eth")]
	elif args[0] == "Vlan":
            path = cc.Path('/restconf/data/sonic-vlan:sonic-vlan/VLAN/VLAN_LIST')
            responseVlanTbl = api.get(path)
	    iflist = []
            if responseVlanTbl.ok():
		intf_map = responseVlanTbl.content
                tbl_key = "sonic-vlan:VLAN_LIST"
		if tbl_key in intf_map:
		    iflist = [i["name"] for i in intf_map[tbl_key] if i["name"].startswith("Vlan")]
	elif args[0] == "PortChannel":
            path = cc.Path('/restconf/data/sonic-portchannel:sonic-portchannel/PORTCHANNEL/PORTCHANNEL_LIST')
            responseLagTbl = api.get(path)
	    iflist = []
            if responseLagTbl.ok():
		intf_map = responseLagTbl.content
	    	tbl_key = "sonic-portchannel:PORTCHANNEL_LIST"
		if tbl_key in intf_map:
		    iflist = [i["name"] for i in intf_map[tbl_key] if i["name"].startswith("PortChannel")]
	return iflist

    elif func == 'create_if_range': 
        """
            Create number, range, or comma-delimited list of numbers and range of Vlan or PortChannel interfaces
            param:
                -range of interfaces
        """
        ifrange = args[0].split("=")[1]
        iftype, ifrangelist = rangetolst(ifrange)
        body = {"openconfig-interfaces:interfaces": {"interface": []} }
        if iftype == "Vlan":
            subfunc = "patch_interface_config"
        elif iftype == "PortChannel":
            subfunc = "portchannel_config"
        else:
            print "%Error: Not supported"
            return 1
        for intf in ifrangelist:
            intfargs = [intf]+args[1:]
            body["openconfig-interfaces:interfaces"]["interface"].append(generate_body(subfunc, intfargs))
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces')
        return api.patch(path, body)

    elif func == 'config_if_range':
        """
            - Configure number, range, or comma-delimited list of numbers and range of Vlan or Ethernet or PortChannel interfaces
            param:
                - List of available interfaces to be configured
                - API to be called to generate payload
        """
        body = {"openconfig-interfaces:interfaces": {"interface": []} }
        iflistStr = args[0].split("=")[1]
        iflist = iflistStr.rstrip().split(',') 
        subfunc = args[1]
        for intf in iflist:
            intfargs = [intf]+ args[2:]
            time.sleep(.1)
            body["openconfig-interfaces:interfaces"]["interface"].append(generate_body(subfunc, intfargs))
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces')
        return api.patch(path, body)

    return api.cli_not_implemented(func)

def check_response(response, func, args):
    if response.ok():
        if response.content is not None:
            # Get Command Output
            api_response = response.content
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

            if api_response is None:
                print("%Error: Internal error.")
                return 1
            else:
                if func == 'get_openconfig_interfaces_interfaces_interface':
                    show_cli_output(args[1], api_response)
                elif func == 'get_openconfig_interfaces_interfaces':
                    show_cli_output(args[0], api_response)
                elif func == 'get_sonic_port_sonic_port_port_table':
                    show_cli_output(args[0], api_response)
    else:
        print response.error_message()
        return 1

def run(func, args):
    try:
        if len(args) == 0:
            return
        # Get available interfaces in given range
        if func == 'get_available_iflist_in_range':
            givenifrange = args[0]
            if givenifrange.startswith("Eth"):
                iflist = eth_intf_range_expand(givenifrange)
            else:
                iftype, ifrangelist = rangetolst(givenifrange)
                iflist = invoke_api("get_available_interface_names_list", [iftype])
                iflist = intersection(iflist, ifrangelist)
            res = ",".join(natsorted(iflist))
            sys.stdout.write(res)

        elif func == 'expand_if_range_to_list':
            givenifrange = args[0]
            _, ifrangelist = rangetolst(givenifrange)
            res = ",".join(natsorted(ifrangelist))
            return res

        elif func == 'delete_if_range':
            """
                - Delete/Remove config for given number, range, or comma-delimited list of numbers and range of interfaces.
                - Transaction is per interface.
                param:
                    -List of available interfaces in given range of interfaces.
                    -Delete API to be invoked
            """
            iflistStr = args[0].split("=")[1]
            if iflistStr == "":
                return 1
            iflist = iflistStr.rstrip().split(',')
            subfunc = args[1]  #ex: delete_interface or delete_aggregate_id
            for intf in iflist:
                intfargs = [intf]+ args[2:]
                response = invoke_api(subfunc, intfargs)
                if check_response(response, subfunc, intfargs):
                    print "%Error: Interface: "+intf

        elif func == 'create_if_range': 
            cmd = args[0].split("=")[1]
            iflistStr = args[1].split("=")[1]
            if cmd != "create":
                # Validate if any interface exist in range
                if iflistStr == "":
                    print("%Error: No interface exist in given range")
                    return 1
                print("%Info: Configuring only existing interfaces in range")
            else:
                # Create range of interfaces
                return check_response(invoke_api(func, args[2:]), func, args)
        elif func == 'get_if_range':
            """
                - Get state data of number, range, or comma-delimited list of numbers and range of interfaces.
                - Transaction is per interface.
                param:
                    -List of existing interfaces in given range of interfaces.
            """
            if args[0] == "":
                return 1
            iflist = args[0].rstrip().split(',') 
            for intf in iflist:
                func = "get_openconfig_interfaces_interfaces_interface"
                intfargs = [intf]+args[1:]
                response = invoke_api(func, intfargs)
                if check_response(response, func, intfargs):
                    print "%Error: Interface: "+intf
            return
        elif func == 'default_port_config_range':
            api = cc.ApiClient()
            iflistStr = args[0].split("=")[1]
            # Validate if any interface exist in range
            if iflistStr == "":
                print("%Error: No interface exists in the given range")
                return 1
            fail_list = []
            iflist = iflistStr.rstrip().split(',')
            for intf in iflist:
                body = {"sonic-config-mgmt:input": { "ifname": intf }}
                path = cc.Path('/restconf/operations/sonic-config-mgmt:default-port-config')
                resp = api.post(path, body)
                result = False
                if resp.ok() and resp.content is not None and \
                   resp.content.get("sonic-config-mgmt:output") is not None and \
                   resp.content.get("sonic-config-mgmt:output").get("status") is not None and \
                   resp.content["sonic-config-mgmt:output"]["status"] == 0:
                    result = True
                if not result:
                    fail_list.append(intf)
            if len(fail_list) != 0:
                print("%Error: Failed to restore the following interfaces to their default configuration:\n" + "\n".join(fail_list))
                return 1
            return 0
        else:
            response = invoke_api(func, args)
            return check_response(response, func, args)

    except Exception as e:
        print("%Error: Transaction Failure ", e)
        return 1

if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])

