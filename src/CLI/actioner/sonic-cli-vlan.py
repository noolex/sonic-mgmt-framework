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
import collections
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output

vlanDict = {}
suppressVlanList = []

class ifInfo:
    ifModeDict = {}
    oper_status = "down"

    def __init__(self, ifModeDict):
        self.ifModeDict = ifModeDict
    
    def asdict(self):
        return {'vlanMembers':self.ifModeDict, 'oper_status':self.oper_status}

def invoke_api(func, args=[]):
    api = cc.ApiClient()

    if func == 'get_sonic_vlan_sonic_vlan':
        path = cc.Path('/restconf/data/sonic-vlan:sonic-vlan')
        return api.get(path)

    if func == 'get_sonic_vxlan_sonic_vxlan_suppress_vlan_neigh':
        path = cc.Path('/restconf/data/sonic-vxlan:sonic-vxlan')
        return api.get(path)

    return api.cli_not_implemented(func)

def getVlanId(key):
    try:
        return int(key)
    except ValueError:
        return key

def updateVlanToIntfMap(vlanTuple, vlanId):
    for dict in vlanTuple:
        if "ifname" in dict:
            ifName = dict["ifname"]
        if "name" in dict:
            vlanName = dict["name"]
            if vlanId:
                if vlanName != vlanId:
                    continue
            vlanName = vlanName[len("Vlan"):]
        
        if "tagging_mode" in dict:
            ifMode = dict["tagging_mode"]
     
        if not vlanName:
            return

        if vlanDict.get(vlanName) == None:
            ifModeDict = {}

            if ifMode and ifName:
                ifModeDict[ifName] = ifMode
            ifData = ifInfo(ifModeDict)
            vlanDict[vlanName] = ifData
        else:
            ifData = vlanDict.get(vlanName)
            existingifDict = ifData.ifModeDict
            if ifMode and ifName:
                existingifDict[ifName] = ifMode

def updateVlanInfoMap(vlanTuple, vlanId):
    for dict in vlanTuple:
        if "name" in dict:
            vlanName = dict["name"]
            if vlanId:
                if vlanName != vlanId:
                    continue
            vlanName = vlanName[len("Vlan"):]
        if not vlanName:
            return

        operStatus = "down"
        if "oper_status" in dict:
            operStatus = dict["oper_status"]

        if vlanDict.get(vlanName) == None:
            ifModeDict = {}

            ifData = ifInfo(ifModeDict)
            ifData.oper_status = operStatus
            vlanDict[vlanName] = ifData
        else:
            ifData = vlanDict.get(vlanName)
            ifData.oper_status = operStatus

def updateVlanNeighSuppressMap(suppTuple, tunnelMapTuple, vlanId):
    sDict = {}
    tempDict = {}
    num = 0
    for dict in tunnelMapTuple:
        vid = dict['vlan']
        num += 1
        if vlanId:
            if(vid != vlanId):
                continue
        sDict['name'] = vid
        tempDict['name'] = vid
        tempDict['suppress'] = 'on'
        if tempDict in suppTuple:
            sDict['suppress'] = "on"
        else:
            sDict['suppress'] = "off"
        sDict['netdev'] = dict['name'] + "-" + vid[4:]
        suppressVlanList.append(sDict.copy())
 
def run(func, args):
    response = invoke_api(func, args)

    if response.ok():
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if 'sonic-vlan:sonic-vlan' in api_response:
                value = api_response['sonic-vlan:sonic-vlan']
                if 'VLAN_MEMBER_TABLE' in value:
                    vlanMemberCont = value['VLAN_MEMBER_TABLE']
                    if 'VLAN_MEMBER_TABLE_LIST' in vlanMemberCont:
                        vlanMemberTup = vlanMemberCont['VLAN_MEMBER_TABLE_LIST']
                        updateVlanToIntfMap(vlanMemberTup, args[0])
                if 'VLAN_TABLE' in value:
                    vlanCont = value['VLAN_TABLE']
                    if 'VLAN_TABLE_LIST' in vlanCont:
                         vlanTup = vlanCont['VLAN_TABLE_LIST']
                         updateVlanInfoMap(vlanTup, args[0])

            if 'sonic-vxlan:sonic-vxlan' in api_response:
                value = api_response['sonic-vxlan:sonic-vxlan']
                suppressCont = value['SUPPRESS_VLAN_NEIGH']
                vxlanCont = value['VXLAN_TUNNEL_MAP']
                suppTuple = suppressCont['SUPPRESS_VLAN_NEIGH_LIST']
                vxlanTuple = vxlanCont['VXLAN_TUNNEL_MAP_LIST']
                updateVlanNeighSuppressMap(suppTuple,vxlanTuple, args[0])

            if api_response is None:
                print("Failed")
            else:
                vDict = {}
                for key, val in vlanDict.iteritems():
                    vDict[key] = vlanDict[key].asdict()
                for key, val in vDict.iteritems():
                    sortMembers = collections.OrderedDict(sorted(val['vlanMembers'].items(), key=lambda t: t[1]))
                    val['vlanMembers'] = sortMembers
                vDictSorted = collections.OrderedDict(sorted(vDict.items(), key = lambda t: getVlanId(t[0])))
                if func == 'get_sonic_vlan_sonic_vlan':
                     show_cli_output(args[1], vDictSorted)
                elif func == 'get_sonic_vxlan_sonic_vxlan_suppress_vlan_neigh':
                     show_cli_output(args[1], suppressVlanList)
                else:
                     return

    else:
        print response.error_message()

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])
