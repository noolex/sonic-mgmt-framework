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

            intf = macEntry.get('interface').get('interface-ref').get('state').get('interface')
            if intf is None:
                continue

            key = "Vlan" + str(vlan) + "-" + mac
            macDict[key] = intf
    except:
        print "%Error: Internal error"

def process_nbrs_intf(response, args):
    outputList = []
    ifName = args[1]
    isMacDictAvailable = False

    nbrsContainer = response.get('openconfig-if-ip:neighbors')
    if nbrsContainer is None:
        return[]

    nbrsList = nbrsContainer.get('neighbor')
    if nbrsList is None:
        return[]

    for nbr in nbrsList:
        extIntfName = "-"
        state = nbr.get('state')
        if state is None:
            continue

        ipAddr = state.get('ip')
        if ipAddr is None:
            continue

        macAddr = state.get('link-layer-address')
        if macAddr is None:
            continue

        if ifName.startswith('Vlan'):
            if isMacDictAvailable is False:
                build_mac_list()
                isMacDictAvailable = True
            key = ifName + "-" + macAddr
            extIntfName = macDict.get(key)
            if extIntfName is None:
                extIntfName = "-"

        nbrTableEntry = {'ipAddr':ipAddr,
                            'macAddr':macAddr,
                            'intfName':args[1],
                            'extIntfName':extIntfName
                          }
        outputList.append(nbrTableEntry)

    return outputList

def process_sonic_nbrs(response, args):
    outputList = []
    isMacDictAvailable = False

    nbrsContainer = response.get('sonic-neighbor:NEIGH_TABLE')
    if nbrsContainer is None:
        return []

    nbrsList = nbrsContainer.get('NEIGH_TABLE_LIST')
    if nbrsList is None:
        return []

    for nbr in nbrsList:
        extIntfName = "-"

        family = nbr.get('family')
        if family is None:
            continue

        if family != args[1]:
            continue

        ifName = nbr.get('ifname')
        if ifName is None:
            continue

        ipAddr = nbr.get('ip')
        if ipAddr is None:
            continue

        macAddr = nbr.get('neigh')
        if macAddr is None:
            continue

        if ifName.startswith('Vlan'):
            if isMacDictAvailable is False:
                build_mac_list()
                isMacDictAvailable = True
            key = ifName + "-" + macAddr
            extIntfName = macDict.get(key)
            if extIntfName is None:
                extIntfName = "-"

        nbrTableEntry = {'ipAddr':ipAddr,
                           'macAddr':macAddr,
                           'intfName':ifName,
                           'extIntfName':extIntfName
                        }
        if (len(args) == 4):
            if (args[2] == "mac" and args[3] == macAddr):
                outputList.append(nbrTableEntry)
        elif (len(args) == 3 and args[2] != "summary"):
            if args[2] == ipAddr:
                outputList.append(nbrTableEntry)
        else:
            outputList.append(nbrTableEntry)

    return outputList

def run(func, args):
    global macDict

    # create a body block
    keypath, body = get_keypath(func, args)
    outputList = []

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
            outputList = process_nbrs_intf(response, args)
        elif 'sonic-neighbor:NEIGH_TABLE' in response.keys():
            outputList = process_sonic_nbrs(response, args)
        elif 'sonic-neighbor:output' in response.keys():
            status = response['sonic-neighbor:output']
            status = status['response']
            if (status != "Success"):
                print status
            return
        else:
            return

        macDict = {}
        show_cli_output(args[0], outputList)
        return
    except:
        print "%Error: Internal error"

if __name__ == '__main__':
    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])


