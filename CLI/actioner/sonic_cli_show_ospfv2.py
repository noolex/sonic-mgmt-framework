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

def generate_show_ip_ospf(vrf):
    api = cc.ApiClient()
    keypath = []
    vrfName = ""
    i = 0
    vrfName = vrf

    d = {}
    dlist = []
    d = { 'vrfName': vrfName }
    dlist.append(d)
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/global/state', name=vrfName)
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None or len(api_response) == 0:
                print("% OSPF instance not found")
                return
            if 'openconfig-network-instance:state' in api_response and api_response['openconfig-network-instance:state'] is not None:
                api_response['openconfig-network-instance:global_state'] = api_response.pop('openconfig-network-instance:state')
                dlist.append(api_response)
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/spf/state', name=vrfName)
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            # Let the below code return an empty dictionary
            # An error code is returned from the ospfv2/global level.
            if api_response is None:
                print("Failed")
                return
            if 'openconfig-network-instance:state' in api_response and api_response['openconfig-network-instance:state'] is not None:
                api_response['openconfig-network-instance:spf_state'] = api_response.pop('openconfig-network-instance:state')
                dlist.append(api_response)
    
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/lsa-generation/state', name=vrfName)
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("Failed")
                return
            if 'openconfig-network-instance:state' in api_response and api_response['openconfig-network-instance:state'] is not None:
                api_response['openconfig-network-instance:lsa_gen_state'] = api_response.pop('openconfig-network-instance:state')
                dlist.append(api_response)

    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/areas', name=vrfName)
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("Failed")
                return
            dlist.append(api_response)
    show_cli_output("show_ip_ospf.j2", dlist)



def generate_show_ip_ospf_areas(vrf, template, intfname):
    api = cc.ApiClient()
    keypath = []
    interfacename = ""
    
    vrfName = vrf
    interfacename = intfname

    d = {}
    dlist = []
    d = { 'vrfName': vrfName }
    dlist.append(d)
    if interfacename != "":
        intfparam = {'interfacename': interfacename }
        dlist.append(intfparam)
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/areas', name=vrfName)
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None or len(api_response) == 0:
                print("% OSPF instance not found")
                return
            dlist.append(api_response)
    show_cli_output(template, dlist)



def generate_show_ip_ospf_route(vrf, template):
    api = cc.ApiClient()
    keypath = []
    vrfName = vrf

    d = {}
    dlist = []
    d = { 'vrfName': vrfName }
    dlist.append(d)
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/openconfig-ospfv2-ext:route-tables', name=vrfName)
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None or len(api_response) == 0:
                print("% OSPF instance not found")
                return
            dlist.append(api_response)
    show_cli_output(template, dlist)


def generate_show_ip_ospf_database_router(vrf, template, ls_id, adv_router, selforg):
    api = cc.ApiClient()
    keypath = []
    vrfName = vrf
    self_originate = selforg
    advRouter = adv_router
    lsId = ls_id

    d = {}
    dlist = []
    d = { 'vrfName': vrfName }
    dlist.append(d)
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/global/state', name=vrfName)
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None or len(api_response) == 0:
                print("% OSPF instance not found")
                return
            if 'openconfig-network-instance:state' in api_response and api_response['openconfig-network-instance:state'] is not None:
                d = {}
                self_router_id = api_response['openconfig-network-instance:state']['router-id']
                d = { 'self_router_id': self_router_id }
                dlist.append(d)
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/areas', name=vrfName)
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
    show_cli_output(template, dlist)


def ospfv2_filter_lsdb_by_adv_router(response, advRouter):
    if 'openconfig-network-instance:areas' in  response and 'area' in response['openconfig-network-instance:areas']:
        for i in range(len(response['openconfig-network-instance:areas']['area'])):
            areainfo = response['openconfig-network-instance:areas']['area'][i]
            if 'lsdb' in areainfo and 'lsa-types' in areainfo['lsdb'] and 'lsa-type' in areainfo['lsdb']['lsa-types']:
                for j in range(len(areainfo['lsdb']['lsa-types']['lsa-type'])):
                    lsa_type = areainfo['lsdb']['lsa-types']['lsa-type'][j]
                    if 'lsas' in lsa_type and 'openconfig-ospfv2-ext:lsa-ext' in lsa_type['lsas']:
                        temp_lsa_list = []
                        while lsa_type['lsas']['openconfig-ospfv2-ext:lsa-ext']:
                            lsainfo = lsa_type['lsas']['openconfig-ospfv2-ext:lsa-ext'].pop()
                            if 'advertising-router' in lsainfo and lsainfo['advertising-router'] == advRouter:
                                temp_lsa_list.append(lsainfo)
                        while temp_lsa_list:
                            lsa_type['lsas']['openconfig-ospfv2-ext:lsa-ext'].append(temp_lsa_list.pop())
                                
                            
def ospfv2_filter_lsdb_by_ls_id(response, ls_id):
    if 'openconfig-network-instance:areas' in  response and 'area' in response['openconfig-network-instance:areas']:
        for i in range(len(response['openconfig-network-instance:areas']['area'])):
            areainfo = response['openconfig-network-instance:areas']['area'][i]
            if 'lsdb' in areainfo and 'lsa-types' in areainfo['lsdb'] and 'lsa-type' in areainfo['lsdb']['lsa-types']:
                for j in range(len(areainfo['lsdb']['lsa-types']['lsa-type'])):
                    lsa_type = areainfo['lsdb']['lsa-types']['lsa-type'][j]
                    if 'lsas' in lsa_type and 'openconfig-ospfv2-ext:lsa-ext' in lsa_type['lsas']:
                        temp_lsa_list = []
                        while lsa_type['lsas']['openconfig-ospfv2-ext:lsa-ext']:
                            lsainfo = lsa_type['lsas']['openconfig-ospfv2-ext:lsa-ext'].pop()
                            if 'link-state-id' in lsainfo and lsainfo['link-state-id'] == ls_id:
                                temp_lsa_list.append(lsainfo)
                        while temp_lsa_list:
                            lsa_type['lsas']['openconfig-ospfv2-ext:lsa-ext'].append(temp_lsa_list.pop())


def invoke_show_api(func, args=[]):
    vrf = args[0]
    i = 3
    if (len(args[i:]) == 1):
        return generate_show_ip_ospf(vrf)
    else:
        i = i + 1
        for arg in args[i:]:
            if (arg == "neighbor"):
                j = i + 1
                neighip = ""
                intfname = ""
                allneigh = False
                detail = False

                for neiarg in args[j:]:
                    if (neiarg == "detail"):
                        detail = True
                    elif (neiarg == "all"):
                        allneigh = true
                    elif (("." in neiarg) or (":" in neiarg)):
                        intfname = neiarg
                    elif (neiarg == "\|"):
                        break
                    elif  (neiarg != "vrf" and args[j - 1] != "vrf" and neiarg != "neighbor"):
                        intfname = neiarg

                    j = j + 1               
               
                if (detail == True):
                    return generate_show_ip_ospf_areas(vrf, "show_ip_ospf_neighbor_detail.j2", intfname)
                else:
                    return generate_show_ip_ospf_areas(vrf, "show_ip_ospf_neighbor.j2", intfname)

            elif (arg == "interface"):
                j = i
                trafficcmd = False
                intfname = ""

                for intfarg in args[j:]:
                    if (intfarg == "traffic"):
                        trafficcmd = True
                    elif (intfarg == "interface"):
                        intfname = ""
                    elif (intfarg == "\|"):
                        break
                    elif (intfarg != "vrf" and args[j - 1] != "vrf"):
                        intfname = intfarg

                    j = j + 1

                if (trafficcmd == True):
                    return generate_show_ip_ospf_areas(vrf, "show_ip_ospf_interface_traffic.j2", intfname)
                else:
                    return generate_show_ip_ospf_areas(vrf, "show_ip_ospf_interface.j2", intfname)
            elif (arg == "route"):
                return generate_show_ip_ospf_route(vrf, "show_ip_ospf_route.j2")
            elif (arg == "border-routers"):
                return generate_show_ip_ospf_route(vrf, "show_ip_ospf_border_routers.j2")
            elif (arg == "database"):
                j = i
                dbtype = "database"
                lsid = ""
                advrouter = ""
                selforg = False
                skipNextArg = False

                for dbarg in args[j:]:
                    if skipNextArg == True:
                        skipNextArg = False
                    elif (dbarg == "router"):
                        dbtype = "router"
                    elif (dbarg == "network"):
                        dbtype = "network"
                    elif (dbarg == "summary"):
                        dbtype = "summary"
                    elif (dbarg == "asbr-summary"):
                        dbtype = "asbr_summary"
                    elif (dbarg == "external"):
                        dbtype = "external"
                    elif (("." in dbarg) or (":" in dbarg)):
                        lsid = args[j]
                    elif (dbarg == "adv-router"):
                        advrouter = args[j + 1]
                        skipNextArg = True
                    elif (dbarg == "self-originate"):
                        selforg = True

                    j = j + 1

                if (dbtype == "database"):
                    return generate_show_ip_ospf_database_router(vrf, "show_ip_ospf_database.j2", lsid, advrouter, selforg)
                if (dbtype == "router"):
                    return generate_show_ip_ospf_database_router(vrf, "show_ip_ospf_database_router.j2", lsid, advrouter, selforg)
                elif (dbtype == "network"):
                    return generate_show_ip_ospf_database_router(vrf, "show_ip_ospf_database_network.j2", lsid, advrouter, selforg)
                elif (dbtype == "summary"):
                    return generate_show_ip_ospf_database_router(vrf, "show_ip_ospf_database_summary.j2", lsid, advrouter, selforg)
                elif (dbtype == "asbr_summary"):
                    return generate_show_ip_ospf_database_router(vrf, "show_ip_ospf_database_asbr_summary.j2", lsid, advrouter, selforg)
                elif (dbtype == "external"):
                    return generate_show_ip_ospf_database_router(vrf, "show_ip_ospf_database_external.j2", lsid, advrouter, selforg)
            elif (arg == "vrf" or arg == "\|"):
                if (arg == "vrf" and (len(args[(i + 1):]) > 1) and args[i + 2] != "\|"):
                    continue

                return generate_show_ip_ospf(vrf)
            else:
                continue 
            i = i + 1
def run(func, args):
    invoke_show_api(func, args)

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])
