#!/usr/bin/python
###########################################################################
#
# Copyright 2019 Broadcom, Inc.
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
import pdb
import ast
from rpipe_utils import pipestr
import cli_client as cc
from scripts.render_cli import show_cli_output

def generate_show_ip_ospf(args):
    api = cc.ApiClient()
    keypath = []
    vrfName = "default"
    i = 0
    for arg in args:
        if "vrf" in arg or "Vrf" in arg:
            vrfName = args[i]
        i = i + 1

    d = {}
    dlist = []
    d = { 'vrfName': vrfName }
    dlist.append(d)
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/global/state', name=args[1])
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("Failed")
                return
            if api_response['openconfig-network-instance:state'] is not None:
                api_response['openconfig-network-instance:global_state'] = api_response.pop('openconfig-network-instance:state')
                dlist.append(api_response)
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/spf/state', name=args[1])
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("Failed")
                return
            if api_response['openconfig-network-instance:state'] is not None:
                api_response['openconfig-network-instance:spf_state'] = api_response.pop('openconfig-network-instance:state')
                dlist.append(api_response)
    
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/lsa-generation/state', name=args[1])
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("Failed")
                return
            if api_response['openconfig-network-instance:state'] is not None:
                api_response['openconfig-network-instance:lsa_gen_state'] = api_response.pop('openconfig-network-instance:state')
                dlist.append(api_response)

    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/areas', name=args[1])
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("Failed")
                return
            dlist.append(api_response)
    show_cli_output(args[0], dlist)



def generate_show_ip_ospf_areas(args):
    api = cc.ApiClient()
    keypath = []
    vrfName = "default"
    interfacename = ""
    i = 0
    for arg in args:
        if "vrf" in arg or "Vrf" in arg:
            vrfName = args[i]
        i = i + 1

    if(len(args) > 2):
       interfacename = args[2]
    d = {}
    dlist = []
    d = { 'vrfName': vrfName }
    dlist.append(d)
    if interfacename != "":
        intfparam = {'interfacename': interfacename }
        dlist.append(intfparam)
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/areas', name=args[1])
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("Failed")
                return
            dlist.append(api_response)
    show_cli_output(args[0], dlist)



def generate_show_ip_ospf_route(args):
    api = cc.ApiClient()
    keypath = []
    vrfName = "default"
    i = 0
    for arg in args:
        if "vrf" in arg or "Vrf" in arg:
            vrfName = args[i]
        i = i + 1

    d = {}
    dlist = []
    d = { 'vrfName': vrfName }
    dlist.append(d)
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/openconfig-ospfv2-ext:route-tables', name=args[1])
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("Failed")
                return
            dlist.append(api_response)
    show_cli_output(args[0], dlist)


def generate_show_ip_ospf_database_router(args):
    api = cc.ApiClient()
    keypath = []
    vrfName = "default"
    self_originate = False
    self_router_id = ""
    advRouter = ""
    lsId = ""
    i = 0
    for arg in args:
        if "vrf" in arg or "Vrf" in arg:
            vrfName = args[i]
        if "self-originate" in arg:
            self_originate = True
        if "adv-router" in arg:
            advRouter = args[i+1]
        if "ls-id" in arg:
            lsId = args[i+1]
        i = i + 1

    d = {}
    dlist = []
    d = { 'vrfName': vrfName }
    dlist.append(d)
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/global/state', name=args[1])
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("Failed")
                return
            if api_response['openconfig-network-instance:state'] is not None:
                d = {}
                self_router_id = api_response['openconfig-network-instance:state']['router-id']
                d = { 'self_router_id': self_router_id }
                dlist.append(d)
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/areas', name=args[1])
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("Failed")
                return
            if advRouter != "":
                ospfv2_filter_lsdb_by_adv_router(api_response, advRouter)
            if self_originate == True and self_router_id != "":
                ospfv2_filter_lsdb_by_adv_router(api_response, self_router_id)
            if lsId != "":
                ospfv2_filter_lsdb_by_ls_id(api_response, lsId)
            dlist.append(api_response)
    show_cli_output(args[0], dlist)


def ospfv2_filter_lsdb_by_adv_router(response, advRouter):
    if 'openconfig-network-instance:areas' in  response and 'area' in response['openconfig-network-instance:areas']:
        for i in range(len(response['openconfig-network-instance:areas']['area'])):
            areainfo = response['openconfig-network-instance:areas']['area'][i]
            if 'lsdb' in areainfo and 'lsa-types' in areainfo['lsdb'] and 'lsa-type' in areainfo['lsdb']['lsa-types']:
                for j in range(len(areainfo['lsdb']['lsa-types']['lsa-type'])):
                    lsa_type = areainfo['lsdb']['lsa-types']['lsa-type'][j]
                    if 'lsas' in lsa_type and 'lsa' in lsa_type['lsas']:
                        temp_lsa_list = []
                        while lsa_type['lsas']['lsa']:
                            lsainfo = lsa_type['lsas']['lsa'].pop()
                            if 'state' in lsainfo and 'advertising-router' in lsainfo['state'] and lsainfo['state']['advertising-router'] == advRouter:
                                temp_lsa_list.append(lsainfo)
                        if temp_lsa_list:
                            lsa_type['lsas']['lsa'].append(temp_lsa_list.pop())
                                
                            
def ospfv2_filter_lsdb_by_ls_id(response, ls_id):
    if 'openconfig-network-instance:areas' in  response and 'area' in response['openconfig-network-instance:areas']:
        for i in range(len(response['openconfig-network-instance:areas']['area'])):
            areainfo = response['openconfig-network-instance:areas']['area'][i]
            if 'lsdb' in areainfo and 'lsa-types' in areainfo['lsdb'] and 'lsa-type' in areainfo['lsdb']['lsa-types']:
                for j in range(len(areainfo['lsdb']['lsa-types']['lsa-type'])):
                    lsa_type = areainfo['lsdb']['lsa-types']['lsa-type'][j]
                    if 'lsas' in lsa_type and 'lsa' in lsa_type['lsas']:
                        temp_lsa_list = []
                        while lsa_type['lsas']['lsa']:
                            lsainfo = lsa_type['lsas']['lsa'].pop()
                            if 'link-state-id' in lsainfo and lsainfo['link-state-id'] == ls_id:
                                temp_lsa_list.append(lsainfo)
                        if temp_lsa_list:
                            lsa_type['lsas']['lsa'].append(temp_lsa_list.pop())


def invoke_show_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None
    if func == 'show_ip_ospf':
        return generate_show_ip_ospf(args)
    elif func == 'show_ip_ospf_neighbor_detail':
        return generate_show_ip_ospf_areas(args)
    elif func == 'show_ip_ospf_neighbor':
        return generate_show_ip_ospf_areas(args)
    elif func == 'show_ip_ospf_interface':
        return generate_show_ip_ospf_areas(args)
    elif func == 'show_ip_ospf_interface_traffic':
        return generate_show_ip_ospf_areas(args)
    elif func == 'show_ip_ospf_route':
        return generate_show_ip_ospf_route(args)
    elif func == 'show_ip_ospf_border_routers':
        return generate_show_ip_ospf_route(args)
    elif func == 'show_ip_ospf_database_router':
        return generate_show_ip_ospf_database_router(args)
    elif func == 'show_ip_ospf_database_network':
        return generate_show_ip_ospf_database_router(args)
    else: 
        return api.cli_not_implemented(func)


def run(func, args):
    invoke_show_api(func, args)

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])
