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
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output

import urllib3
urllib3.disable_warnings()

aa = cc.ApiClient()
macDict = {}

def get_keypath(func,args):
    keypath = None
    instance = None
    body = None

    if func == 'get_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ipv4_neighbors':
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/neighbors', name=args[1], index="0")
    elif func == 'get_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ipv6_neighbors':
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/neighbors', name=args[1], index="0")
    elif func == 'get_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ipv4_neighbors_neighbor':
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/neighbors/neighbor={ip}', name=args[1], index="0", ip=args[3])
    elif func == 'get_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ipv6_neighbors_neighbor':
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/neighbors/neighbor={ip}',name=args[1], index="0", ip=args[3])
    elif func == 'get_sonic_neigh_sonic_neigh_neigh_table':
        keypath = cc.Path('/restconf/data/sonic-neighbor:sonic-neighbor/NEIGH_TABLE')
    elif func == 'rpc_sonic_clear_neighbors':
        keypath = cc.Path('/restconf/operations/sonic-neighbor:clear-neighbors')
        if (len (args) == 2):
            body = {"sonic-neighbor:input":{"family": args[0], "force": args[1], "ip": "", "ifname": ""}}
        elif (len (args) == 3):
            body = {"sonic-neighbor:input":{"family": args[0], "force": args[1], "ip": args[2], "ifname": ""}}
        elif (len (args) == 4):
            body = {"sonic-neighbor:input":{"family": args[0], "force": args[1], "ip": "", "ifname": args[3]}}

    return keypath, body

def build_mac_list():
    global macDict
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/fdb/mac-table/entries', name='default')

    try:
        response = aa.get(keypath)
        response = response.content

        macContainer = response.get('openconfig-network-instance:entries')
        macList = macContainer.get('entry')

        for macEntry in macList:
            vlan = macEntry.get('vlan')
            if vlan is None:
                continue
            mac = macEntry.get('mac-address')
            if mac is None:
                continue

            intf = macEntry.get('interface').get('interface-ref').get('state').get('interface')
            if intf is None:
                continue

            key = "Vlan" + str(vlan) + "-" + mac
            macDict[key] = intf
    except:
        print "%Error: Internal error"

def process_nbrs_intf(response, args):
    nbr_list = []
    ifName = args[1]
    isMacDictAvailable = False
    if response['openconfig-if-ip:neighbors'] is None:
        return

    nbrs = response['openconfig-if-ip:neighbors']['neighbor']
    if nbrs is None:
        return

    for nbr in nbrs:
        ext_intf_name = "-"
        ipAddr = nbr['state']['ip']
        if ipAddr is None:
            return[]

        macAddr = nbr['state']['link-layer-address']
        if macAddr is None:
            return[]

        if ifName.startswith('Vlan'):
            if isMacDictAvailable is False:
                build_mac_list()
                isMacDictAvailable = True
            key = ifName + "-" + macAddr
            ext_intf_name = macDict.get(key)
            if ext_intf_name is None:
                ext_intf_name = "-"

        nbr_table_entry = {'ipAddr':ipAddr,
                            'macAddr':macAddr,
                            'intfName':args[1],
                            'extIntfName':ext_intf_name
                          }
        nbr_list.append(nbr_table_entry)

    return nbr_list

def process_sonic_nbrs(response, args):
    nbr_list = []
    isMacDictAvailable = False

    if response['sonic-neighbor:NEIGH_TABLE'] is None:
        return

    nbrs = response['sonic-neighbor:NEIGH_TABLE']['NEIGH_TABLE_LIST']
    if nbrs is None:
        return

    for nbr in nbrs:
        ext_intf_name = "-"

        family = nbr['family']
        if family is None:
            return []

        if family != args[1]:
            continue

        ifName = nbr['ifname']
        if ifName is None:
            return []

        ipAddr = nbr['ip']
        if ipAddr is None:
            return []

        macAddr = nbr['neigh']
        if macAddr is None:
            return []

        if ifName.startswith('Vlan'):
            if isMacDictAvailable is False:
                build_mac_list()
                isMacDictAvailable = True
            key = ifName + "-" + macAddr
            ext_intf_name = macDict.get(key)
            if ext_intf_name is None:
                ext_intf_name = "-"

        nbr_table_entry = {'ipAddr':ipAddr,
                           'macAddr':macAddr,
                           'intfName':ifName,
                           'extIntfName':ext_intf_name
                        }
        if (len(args) == 4):
            if (args[2] == "mac" and args[3] == macAddr):
                nbr_list.append(nbr_table_entry)
        elif (len(args) == 3 and args[2] != "summary"):
            if args[2] == ipAddr:
                nbr_list.append(nbr_table_entry)
        else:
            nbr_list.append(nbr_table_entry)

    return nbr_list

def run(func, args):
    global macDict

    # create a body block
    keypath, body = get_keypath(func, args)
    nbr_list = []

    try:
        if (func == 'rpc_sonic_clear_neighbors'):
            api_response = aa.post(keypath,body)
        else:
            api_response = aa.get(keypath)
    except:
        # system/network error
        print "Error: Unable to connect to the server"

    try:
        if api_response.ok():
            response = api_response.content
        else:
            return

        if response is None:
            return

        if 'openconfig-if-ip:neighbors' in response.keys():
            nbr_list = process_nbrs_intf(response, args)
        elif 'sonic-neighbor:NEIGH_TABLE' in response.keys():
            nbr_list = process_sonic_nbrs(response, args)
        elif 'sonic-neighbor:output' in response.keys():
            status = response['sonic-neighbor:output']
            status = status['response']
            if (status != "Success"):
                print status
            return
        else:
            return

        macDict = {}
        show_cli_output(args[0],nbr_list)
        return
    except:
        print "%Error: Internal error"

if __name__ == '__main__':
    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])


