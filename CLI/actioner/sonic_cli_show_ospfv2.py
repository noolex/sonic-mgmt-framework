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
import ast
import os
from rpipe_utils import pipestr
from collections import OrderedDict
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
    area_id_list = []
    d = { 'vrfName': vrfName }
    area_id_list = build_area_id_list (vrfName)
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
    areaInfoList = []
    for areaId in area_id_list:
        areaConfig = OrderedDict()
        areaConfig['identifier'] = areaId
        areaInfo = OrderedDict()
        areaInfo['config'] = areaConfig
        areaInfo['identifier'] = areaId
        areaInfoList.append(areaInfo)
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols'
                          + '/protocol=OSPF,ospfv2/ospfv2/areas/area={identifier1}/state', name=vrfName, identifier1=areaId)
        response = api.get(keypath)
        if(response.ok()):
            if response.content is not None:
                # Get Command Output
                api_response = response.content
                if api_response is None:
                    print("Failed")
                    return
                if 'openconfig-network-instance:state' in api_response and api_response['openconfig-network-instance:state'] is not None:
                    areaInfo['state'] = api_response['openconfig-network-instance:state']
    
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols'
                          + '/protocol=OSPF,ospfv2/ospfv2/areas/area={identifier1}/openconfig-ospfv2-ext:stub', name=vrfName, identifier1=areaId)
        response = api.get(keypath)
        if(response.ok()):
            if response.content is not None:
                # Get Command Output
                api_response = response.content
                if api_response is None:
                    print("Failed")
                    return
                if 'openconfig-ospfv2-ext:stub' in api_response and api_response['openconfig-ospfv2-ext:stub'] is not None:
                    areaInfo['openconfig-ospfv2-ext:stub'] = api_response['openconfig-ospfv2-ext:stub']

    areasInfo = OrderedDict()
    areasInfo['area'] = areaInfoList
    areasOuter = OrderedDict()
    areasOuter['openconfig-network-instance:areas'] = areasInfo  
    dlist.append(areasOuter)
    show_cli_output("show_ip_ospf.j2", dlist)



def generate_show_ip_ospf_interfaces(vrf, template, intfname):
    api = cc.ApiClient()
    keypath = []
    interfacename = ""
    countNbr = 0 
    vrfName = vrf
    interfacename = intfname

    d = {}
    dlist = []
    area_id_list = []
    d = { 'vrfName': vrfName }
    dlist.append(d)

    area_id_list = build_area_id_list (vrfName)
    if len(area_id_list) == 0:
        print("% OSPF instance not found")
        return

    if interfacename != "":
        intfparam = {'interfacename': interfacename }
        dlist.append(intfparam)

    areaInfoList = []
    for areaId in area_id_list:
        areaConfig = OrderedDict()
        areaConfig['identifier'] = areaId
        areaInfo = OrderedDict()
        areaInfo['config'] = areaConfig
        areaInfo['identifier'] = areaId
        areaInfoList.append(areaInfo)
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols'
                          + '/protocol=OSPF,ospfv2/ospfv2/areas/area={identifier1}/interfaces', name=vrfName, identifier1=areaId)
        response = api.get(keypath)
        if(response.ok()):
            if response.content is not None:
                # Get Command Output
                api_response = response.content
                if 'openconfig-network-instance:interfaces' in api_response and api_response['openconfig-network-instance:interfaces'] is not None:
                    areaInfo['interfaces'] = api_response['openconfig-network-instance:interfaces']

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols'
                          + '/protocol=OSPF,ospfv2/ospfv2/areas/area={identifier1}/virtual-links', name=vrfName, identifier1=areaId)
        response = api.get(keypath)
        if(response.ok()):
            if response.content is not None:
                # Get Command Output
                api_response = response.content
                if 'openconfig-network-instance:virtual-links' in api_response and api_response['openconfig-network-instance:virtual-links'] is not None:
                    areaInfo['virtual-links'] = api_response['openconfig-network-instance:virtual-links']
    
    areasInfo = OrderedDict()
    areasInfo['area'] = areaInfoList
    areasOuter = OrderedDict()
    areasOuter['openconfig-network-instance:areas'] = areasInfo  
    if '.' in intfname or ':' in intfname:
        countNbr = ospfv2_filter_neighbors_by_neighbor_id(areasOuter, intfname)
        if countNbr == 0 and template == "show_ip_ospf_neighbor_detail.j2":
            print("No such interface.")
            return
            
        # since we have already filtered above, remove filter (don't filter in template)
        intfparam = {'interfacename': intfname }
        dlist.remove(intfparam)
        # Change template to "neighbor detail", evenif "detail" option is not mentioned in CLI
        template = "show_ip_ospf_neighbor_detail.j2"
    dlist.append(areasOuter)
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


def generate_show_ip_ospf_database(vrf, template, ls_id, adv_router, selforg):
    api = cc.ApiClient()
    keypath = []
    vrfName = vrf
    self_originate = selforg
    advRouter = adv_router
    lsId = ls_id

    d = {}
    dlist = []
    area_id_list = []
    d = { 'vrfName': vrfName }
    dlist.append(d)
    area_id_list = build_area_id_list (vrfName)
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

    areaInfoList = []
    for areaId in area_id_list:
        areaConfig = OrderedDict()
        areaConfig['identifier'] = areaId
        areaInfo = OrderedDict()
        areaInfo['config'] = areaConfig
        areaInfo['identifier'] = areaId
        areaInfoList.append(areaInfo)
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols'
                          + '/protocol=OSPF,ospfv2/ospfv2/areas/area={identifier1}/lsdb', name=vrfName, identifier1=areaId)
        response = api.get(keypath)
        if(response.ok()):
            if response.content is not None:
                # Get Command Output
                api_response = response.content
                if 'openconfig-network-instance:lsdb' in api_response and api_response['openconfig-network-instance:lsdb'] is not None:
                    areaInfo['lsdb'] = api_response['openconfig-network-instance:lsdb']

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols'
                          + '/protocol=OSPF,ospfv2/ospfv2/areas/area={identifier1}/openconfig-ospfv2-ext:stub', name=vrfName, identifier1=areaId)
        response = api.get(keypath)
        if(response.ok()):
            if response.content is not None:
                # Get Command Output
                api_response = response.content
                if api_response is None:
                    print("Failed")
                    return
                if 'openconfig-ospfv2-ext:stub' in api_response and api_response['openconfig-ospfv2-ext:stub'] is not None:
                    areaInfo['openconfig-ospfv2-ext:stub'] = api_response['openconfig-ospfv2-ext:stub']

    areasInfo = OrderedDict()
    areasInfo['area'] = areaInfoList
    areasOuter = OrderedDict()
    areasOuter['openconfig-network-instance:areas'] = areasInfo  
    if advRouter != "":
        ospfv2_filter_lsdb_by_adv_router(areasOuter, advRouter)
    if self_originate == True and self_router_id != "":
        ospfv2_filter_lsdb_by_adv_router(areasOuter, self_router_id)
    if lsId != "":
        ospfv2_filter_lsdb_by_ls_id(areasOuter, lsId)

    dlist.append(areasOuter)
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

def ospfv2_filter_neighbors_by_neighbor_id(response, intfname):
    count = 0
    if 'openconfig-network-instance:areas' in  response and 'area' in response['openconfig-network-instance:areas']:
        for i in range(len(response['openconfig-network-instance:areas']['area'])):
            areainfo = response['openconfig-network-instance:areas']['area'][i]
            if 'interfaces' in areainfo and 'interface' in areainfo['interfaces']:
                for j in range(len(areainfo['interfaces']['interface'])):
                    interfaceinfo = areainfo['interfaces']['interface'][j]
                    if 'openconfig-ospfv2-ext:neighbors-list' in interfaceinfo and 'neighbor' in interfaceinfo['openconfig-ospfv2-ext:neighbors-list']:
                        temp_nbr_list = []
                        while interfaceinfo['openconfig-ospfv2-ext:neighbors-list']['neighbor']:
                            nbr = interfaceinfo['openconfig-ospfv2-ext:neighbors-list']['neighbor'].pop()
                            if 'neighbor-id' in nbr and nbr['neighbor-id'] == intfname:
                                temp_nbr_list.append(nbr)
                        while temp_nbr_list:
                            interfaceinfo['openconfig-ospfv2-ext:neighbors-list']['neighbor'].append(temp_nbr_list.pop())
                            count = count + 1
    return count

# The below function prepares area_id_list e.g. ['0.0.0.0', '0.0.0.1'] 
# For area_id = 5, it is internally treated as string 0.0.0.5
def build_area_id_list (vrf_name):
    api = cc.ApiClient()
    output = []

    tableArea = ("/restconf/data/sonic-ospfv2:sonic-ospfv2/OSPFV2_ROUTER_AREA/OSPFV2_ROUTER_AREA_LIST",
             "sonic-ospfv2:OSPFV2_ROUTER_AREA_LIST",
             "area-id")
    requests = [tableArea]
    for request in requests:
        keypath = cc.Path(request[0])
        try:
            response = api.get(keypath)
            response = response.content
            if response is None:
                continue
            areasList = response.get(request[1])
            if areasList is None:
                continue
            for area in areasList:
                # request[2] = tableArea[2] or area-id column
                areaId = area.get(request[2])
                if areaId is None:
                    continue
                vrfName = area.get('vrf_name')
                if vrfName is None or  vrfName != vrf_name:
                    continue
                output.append(areaId)
            output.sort()
        except  Exception as e:
            log.syslog(log.LOG_ERR, str(e))
            print "%Error: Internal error"
    return output

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
                    return generate_show_ip_ospf_interfaces(vrf, "show_ip_ospf_neighbor_detail.j2", intfname)
                else:
                    return generate_show_ip_ospf_interfaces(vrf, "show_ip_ospf_neighbor.j2", intfname)

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
                    return generate_show_ip_ospf_interfaces(vrf, "show_ip_ospf_interface_traffic.j2", intfname)
                else:
                    return generate_show_ip_ospf_interfaces(vrf, "show_ip_ospf_interface.j2", intfname)
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
                maxAge = ""

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
                    elif (dbarg == "max-age"):
                        maxAge = args[j]
                    elif (dbarg == "self-originate"):
                        selforg = True

                    j = j + 1
                if (dbtype == "database"):
                    if maxAge == "" :
                        return generate_show_ip_ospf_database(vrf, "show_ip_ospf_database.j2", lsid, advrouter, selforg)
                    else:
                        full_cmd = os.getenv('USER_COMMAND', None).split('|')[0]
                        keypath = cc.Path('/restconf/operations/sonic-ospfv2-show:show-ospfv2-max-age-lsa')
                        body = {"sonic-ospfv2-show:input": { "cmd":full_cmd }}
                        response = cc.ApiClient().post(keypath, body)
                        if not response:
                            print "No response"
                            return 1
                        if response.ok():
                            if 'sonic-ospfv2-show:output' in response.content and 'response' in response.content['sonic-ospfv2-show:output']:
                                output = response.content['sonic-ospfv2-show:output']['response']
                                show_cli_output("dump.j2", output)
                        else:
                            return 1
                        return
                if (dbtype == "router"):
                    return generate_show_ip_ospf_database(vrf, "show_ip_ospf_database_router.j2", lsid, advrouter, selforg)
                elif (dbtype == "network"):
                    return generate_show_ip_ospf_database(vrf, "show_ip_ospf_database_network.j2", lsid, advrouter, selforg)
                elif (dbtype == "summary"):
                    return generate_show_ip_ospf_database(vrf, "show_ip_ospf_database_summary.j2", lsid, advrouter, selforg)
                elif (dbtype == "asbr_summary"):
                    return generate_show_ip_ospf_database(vrf, "show_ip_ospf_database_asbr_summary.j2", lsid, advrouter, selforg)
                elif (dbtype == "external"):
                    return generate_show_ip_ospf_database(vrf, "show_ip_ospf_database_external.j2", lsid, advrouter, selforg)
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
