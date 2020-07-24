#!/usr/bin/python
###########################################################################
#
# Copyright 2020 Broadcom. The term Broadcom refers to Broadcom Inc. and/or
# its subsidiaries.
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
from scripts.render_cli import show_cli_output

def area_to_dotted(area):
    areastr = "{}".format(area)
    if areastr.isdigit():
        areaInt = int(area)
        
        b0 = ((areaInt >> 24) & 0xff)
        b1 = ((areaInt >> 16) & 0xff)
        b2 = ((areaInt >> 8) & 0xff)
        b3 = ((areaInt & 0xff))

        areaDotted = "{}.{}.{}.{}".format(b0, b1, b2, b3)
        return areaDotted
    else :
        return areastr

def cli_to_db_protocol_map(cli_protocol):
    db_protocol = None
    protocol_map = { "ospf" : "OSPF",
                     "bgp" : "BGP",
                     "static" : "STATIC", 
                     "kernel": "KERNEL",
                     "connected" : "DIRECTLY_CONNECTED",
                     "table" : "DEFAULT_ROUTE" }

    if cli_protocol != None :
        if cli_protocol in protocol_map.keys() :
            db_protocol = protocol_map[cli_protocol]
  
    return db_protocol


def invoke_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None

    if func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:enable', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:enable": True}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_config_router_id':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/router-id', vrfname=args[0])
        body = {"openconfig-network-instance:router-id": args[1]}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_config_router_id':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/router-id', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_config_log_adjacency_changes':
        logtype = ""

        for arg in args:
            if (arg == "detail"):
                logtype = "detail"

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:log-adjacency-state-changes', vrfname=args[0])
        if (logtype != ""):
            body = {"openconfig-ospfv2-ext:log-adjacency-state-changes": "DETAIL"}
        else:
            body = {"openconfig-ospfv2-ext:log-adjacency-state-changes": "BRIEF"}

        return api.patch(keypath, body)

    elif func == 'delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_config_log_adjacency_changes':
        logtype = ""

        for arg in args:
            if (arg == "detail"):
                logtype = "detail"

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:log-adjacency-state-changes', vrfname=args[0])
        if (logtype != ""):
            body = {"openconfig-ospfv2-ext:log-adjacency-state-changes": "BRIEF"}
            return api.patch(keypath, body)
        else:
            return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_auto_cost_reference_bandwidth':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:auto-cost-reference-bandwidth', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:auto-cost-reference-bandwidth": int(args[1])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_auto_cost_reference_bandwidth':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:auto-cost-reference-bandwidth', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_write_multiplier':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:write-multiplier', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:write-multiplier": int(args[1])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_write_multiplier':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:write-multiplier', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config':
        vrf = ""
        abrtypecmdval = ""
        routeridval = ""
        i = 0

        vrf = args[0]

        for arg in args:
            if (arg == "abr-type"):
                abrtypecmdval = args[i + 1]

            if (arg == "router-id"):
                routeridval = args[i + 1]

            i = i + 1

        if (abrtypecmdval != ""):
            abrtypeval = None

            if abrtypecmdval == "cisco":
                abrtypeval = "CISCO" 
            elif abrtypecmdval == "ibm":
                abrtypeval = "IBM"
            elif abrtypecmdval == "shortcut":
                abrtypeval = "SHORTCUT"
            elif abrtypecmdval == "standard":
                abrtypeval = "STANDARD"

            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:abr-type', vrfname=vrf)
            body = {"openconfig-ospfv2-ext:abr-type": abrtypeval}
            return api.patch(keypath, body)

        if (routeridval != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/router-id', vrfname=vrf)
            body = {"openconfig-network-instance:router-id": routeridval}
            return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config':
        vrf = ""
        abrtypecmd = ""
        routeridcmd = ""

        vrf = args[0]

        for arg in args:
            if (arg == "abr-type"):
                abrtypecmd = "abr-type"

            if (arg == "router-id"):
                routeridcmd = "router-id"

        if (abrtypecmd != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:abr-type', vrfname=vrf)
            return api.delete(keypath)

        if (routeridcmd != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/router-id', vrfname=vrf)
            return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_ospf_rfc1583_compatible':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:ospf-rfc1583-compatible', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:ospf-rfc1583-compatible": True}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_ospf_rfc1583_compatible':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:ospf-rfc1583-compatible', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_passive_interface':
        vrf = ""
        cmdtype = ""

        vrf = args[0]

        for arg in args[1:]:
            if (arg == "default"):
                cmdtype = "default"

        if (cmdtype != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:passive-interface-default', vrfname=vrf)
            body = {"openconfig-ospfv2-ext:passive-interface-default": True}
            return api.patch(keypath, body)
        else:
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:passive-interfaces/passive-interface={intfname},{intfaddr}', vrfname=vrf, intfname=args[1], intfaddr=args[2])
            body = {"openconfig-ospfv2-ext:passive-interface": [{"name": args[1], "address": args[2], "config": {"name": args[1],"address": args[2]}}]}
            return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_passive_interface':
        vrf = ""
        cmdtype = ""

        vrf = args[0]

        for arg in args[1:]:
            if (arg == "default"):
                cmdtype = "default"

        if (cmdtype != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:passive-interface-default', vrfname=vrf)
            return api.delete(keypath)
        else:
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:passive-interfaces/passive-interface={intfname},{intfaddr}', vrfname=vrf, intfname=args[1], intfaddr=args[2])
            return api.delete(keypath)

    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_timers':
        vrf = ""
        response = {}
        minarrival_val = ""
        throttletype = ""
        spfdelay = ""
        spfinitial = ""
        spfhold = ""
        lsadelayval = ""
        i = 0

        vrf = args[0]
        
        for arg in args:
            if (arg == "throttle"):
                throttletype = args[i + 1]
                
                if (throttletype == "spf"):
                    spfinitial  = args[i + 2] 
                    spfmax      = args[i + 3]
                    spfthrottle = args[i + 4]
                else:
                    lsadelayval = args[i + 3]
            elif (arg == "min-arrival"):
                minarrival_val = args[i + 1]

            i = i + 1

        if (throttletype == ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/lsa-generation/config/openconfig-ospfv2-ext:minimum-arrival', vrfname=vrf)
            body = {"openconfig-ospfv2-ext:minimum-arrival": int(minarrival_val)}
            return api.patch(keypath, body)
        
        if (throttletype == "spf"):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/spf', vrfname=args[0])
            body = {"openconfig-network-instance:spf": { "config": { "initial-delay": int(spfinitial), "maximum-delay": int(spfmax), "openconfig-ospfv2-ext:throttle-delay": int(spfthrottle) } }}
            response = api.patch(keypath, body)
            if response.ok() == False : return response
        else:
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/lsa-generation/config/openconfig-ospfv2-ext:minimum-interval', vrfname=args[0])
            body = {"openconfig-ospfv2-ext:minimum-interval": int(lsadelayval)}
            response = api.patch(keypath, body)
            if response.ok() == False : return response

        return response 

    elif func == 'delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_timers':
        vrf = ""
        response = {}
        throttletype = ""
        i = 0

        vrf = args[0]

        for arg in args:
            if (arg == "throttle"):
                throttletype = args[i + 1]

            i = i + 1

        if (throttletype == ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/lsa-generation/config/openconfig-ospfv2-ext:minimum-arrival', vrfname=vrf)
            return api.delete(keypath)

        if (throttletype == "spf"):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/spf/config/initial-delay', vrfname=vrf)
            response = api.delete(keypath)
            if response.ok() == False : return response

            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/spf/config/maximum-delay', vrfname=vrf)
            response = api.delete(keypath)
            if response.ok() == False : return response

            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/spf/config/openconfig-ospfv2-ext:throttle-delay', vrfname=vrf)
            response = api.delete(keypath)
            if response.ok() == False : return response
        else:
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/lsa-generation/config/openconfig-ospfv2-ext:minimum-interval', vrfname=vrf)
            response = api.delete(keypath)

        return response

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_max_metric_config':
        vrf = ""
        metrictypeadmin = ""
        sratupmetricval = ""
        i = 0
    
        vrf = args[0]

        for arg in args:
            if (arg == "administrative"):
                metrictypeadmin = "administrative:"
            
            if (arg == "on-startup"):
                sratupmetricval = args[i + 1]

            i = i +1

        if (metrictypeadmin != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/max-metric/config/openconfig-ospfv2-ext:administrative', vrfname=vrf)
            body = {"openconfig-ospfv2-ext:administrative": True}
            return api.patch(keypath, body)
        else:
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/max-metric/config/openconfig-ospfv2-ext:on-startup', vrfname=vrf)
            body = {"openconfig-ospfv2-ext:on-startup": int(sratupmetricval)}
            return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_max_metric_config':
        vrf = ""
        metrictypeadmin = ""

        vrf = args[0]

        for arg in args:
            if (arg == "administrative"):
                metrictypeadmin = "administrative:"

        if (metrictypeadmin != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/max-metric/config/openconfig-ospfv2-ext:administrative', vrfname=vrf)
            return api.delete(keypath)
        else:
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/max-metric/config/openconfig-ospfv2-ext:on-startup', vrfname=vrf)
            return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_lsa_generation_config_refresh_timer':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/lsa-generation/config/openconfig-ospfv2-ext:refresh-timer', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:refresh-timer": int(args[1])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_lsa_generation_config_refresh_timer':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/lsa-generation/config/openconfig-ospfv2-ext:refresh-timer', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distance_config':
        vrf = ""
        extdistance = ""
        interareadist = ""
        intraareadist = ""
        ospfcmd = ""
        response = ""
        i = 0

        vrf = args[0]

        for arg in args:
            if ("external" == arg):
                extdistance = args[i + 1]
            if ("inter-area" == arg):
                interareadist = args[i + 1]
            if ("intra-area" == arg):
                intraareadist = args[i + 1]
            if ("ospf" == arg):
                ospfcmd = "ospf"

            i = i + 1

        if (extdistance == "" and interareadist == "" and intraareadist == "" and ospfcmd == ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:distance/config/all', vrfname=vrf)
            body = {"openconfig-ospfv2-ext:all": int(args[2])}
            response = api.patch(keypath, body)
            if response.ok() == False : return response

        if (extdistance != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:distance/config/external', vrfname=vrf)
            body = {"openconfig-ospfv2-ext:external": int(extdistance)}
            response = api.patch(keypath, body)
            if response.ok() == False : return response

        if (intraareadist != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:distance/config/intra-area', vrfname=vrf)
            body = {"openconfig-ospfv2-ext:intra-area": int(intraareadist)}
            response = api.patch(keypath, body)
            if response.ok() == False : return response

        if (interareadist != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:distance/config/inter-area', vrfname=vrf)
            body = {"openconfig-ospfv2-ext:inter-area": int(interareadist)}
            response = api.patch(keypath, body)
            if response.ok() == False : return response

        return response

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distance_config':
        vrf = ""
        extcmd = ""
        interareacmd = ""
        intraareacmd = ""
        ospfcmd = ""
        response = ""
        i = 0

        vrf = args[0]

        for arg in args:
            if ("external" == arg):
                extcmd = "external"
            if ("inter-area" == arg):
                interareacmd = "inter-area"
            if ("intra-area" == arg):
                intraareacmd = "intra-area"
            if ("ospf" == arg):
                ospfcmd = "ospf"

            i = i + 1

        if (extcmd == "" and interareacmd == "" and intraareacmd == "" and ospfcmd == ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:distance/config/all', vrfname=vrf)
            response = api.delete(keypath)
            if response.ok() == False : return response

        if (extcmd != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:distance/config/external', vrfname=vrf)
            response = api.delete(keypath)
            if response.ok() == False : return response

        if (intraareacmd != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:distance/config/intra-area', vrfname=vrf)
            response = api.delete(keypath)
            if response.ok() == False : return response

        if (interareacmd != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:distance/config/inter-area', vrfname=vrf)
            response = api.delete(keypath)
            if response.ok() == False : return response

        return response

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_import':
        vrf = ""
        alwayscmd = ""
        metricval = ""
        metrictypeval = ""
        routemap = ""
        response = ""

        i = 0

        vrf = args[0]
        for arg in args: 
            if ("always" == arg):
                alwayscmd = "always"

            if ("metric" == arg):
                metricval = args[i + 1]

            if ("metric-type" == arg):
                metrictypeval = args[i + 1]

            if ("route-map" == arg):
                routemap = args[i + 1]

            i = i + 1

        if (alwayscmd == "" and  metricval == "" and metrictypeval == "" and routemap == ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config', vrfname=vrf)
            body = { "openconfig-ospfv2-ext:config": { "protocol": "DEFAULT_ROUTE", "direction": "IMPORT" }}
            response = api.patch(keypath, body)
            if response.ok() == False : return response

        if (alwayscmd != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config/always', vrfname=vrf)
            body = {"openconfig-ospfv2-ext:always": True}
            response = api.patch(keypath, body)
            if response.ok() == False : return response

        if (metricval != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config/metric', vrfname=vrf)
            body = {"openconfig-ospfv2-ext:metric": int(metricval)}
            response = api.patch(keypath, body)
            if response.ok() == False : return response

        if (metrictypeval != ""):
            metrictype = None

            if ("1" == metrictypeval):
                metrictype = "TYPE_1"
            else:
                metrictype = "TYPE_2"

            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config/metric-type', vrfname=vrf)
            body = {"openconfig-ospfv2-ext:metric-type": metrictype}
            response = api.patch(keypath, body)
            if response.ok() == False : return response

        if (routemap != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config/route-map', vrfname=vrf)
            body = {"openconfig-ospfv2-ext:route-map": args[2]}
            response = api.patch(keypath, body)
            if response.ok() == False : return response

        return response
    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_access_list':
        exportprotocol = cli_to_db_protocol_map(args[1])
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},EXPORT/config/access-list', vrfname=args[0], protocol=exportprotocol)
        body = {"openconfig-ospfv2-ext:access-list": (args[2])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_access_list':
        exportprotocol = cli_to_db_protocol_map(args[1])
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},EXPORT/config/access-list', vrfname=args[0], protocol=exportprotocol)
        return api.delete(keypath)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_import':
        vrf = ""
        alwayscmd = ""
        metriccmd = ""
        metrictypecmd = ""
        routemapcmd = ""
        response = ""

        i = 0

        vrf = args[0]
        for arg in args:
            if ("always" == arg):
                alwayscmd = "always"

            if ("metric" == arg):
                metriccmd = "metriccmd"

            if ("metric-type" == arg):
                metrictypecmd = "metrictypecmd"

            if ("route-map" == arg):
                routemapcmd = "routemapcmd"

            i = i + 1

        if (alwayscmd == "" and  metriccmd == "" and metrictypecmd == "" and routemapcmd == ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT', vrfname=vrf)
            response = api.delete(keypath)
            if response.ok() == False : return response

        if (alwayscmd != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config/always', vrfname= vrf)
            response = api.delete(keypath)
            if response.ok() == False : return response

        if (metriccmd != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config/metric', vrfname=vrf)
            response = api.delete(keypath)
            if response.ok() == False : return response

        if (metrictypecmd != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config/metric-type', vrfname=vrf)
            response = api.delete(keypath)
            if response.ok() == False : return response

        if (routemapcmd != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config/route-map', vrfname=vrf)
            response = api.delete(keypath)
            if response.ok() == False : return response

        return response

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_metric':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config/metric', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:metric": int(args[2])}
        return api.patch(keypath, body)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_metric_type':
        metrictype = None

        if ("1" == args[2]):
            metrictype = "TYPE_1"
        else:
            metrictype = "TYPE_2"

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config/metric-type', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:metric-type": metrictype}
        return api.patch(keypath, body)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_route_map_default':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config/route-map', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:route-map": args[2]}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_route_map_default':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config/route-map', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_config_default_metric':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2', vrfname=args[0])
        body = {"openconfig-network-instance:ospfv2": {"global": {"config": {"default-metric": int(args[1])}}}}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_config_default_metric':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:default-metric', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_redistribute_list_config_import':
        vrf = ""
        response = {}
        protocol = ""
        metricval = ""
        metrictypeval = ""
        routemapval = ""
        i = 0

        for arg in args:
            if (arg == "metric"):
                metricval = args[i + 1]
            elif (arg == "metric-type"):
                metrictypeval = args[i + 1]
            elif (arg == "route-map"):
                routemapval = args[i + 1]

            i = i + 1

        vrf = args[0]
        importprotocol = cli_to_db_protocol_map(args[1])

        if (metricval == "" and metrictypeval == "" and routemapval == ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},IMPORT/config', vrfname=vrf, protocol=importprotocol)
            body = { "openconfig-ospfv2-ext:config": { "protocol": importprotocol, "direction": "IMPORT" }}
            response = api.patch(keypath, body)
            if response.ok() == False : return response

        if (metricval != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},IMPORT/config/metric', vrfname=vrf, protocol=importprotocol)
            body = {"openconfig-ospfv2-ext:metric": int(metricval)}
            response = api.patch(keypath, body)
            if response.ok() == False : return response

        if (metrictypeval != ""):
            metrictype = None

            if ("1" == metrictypeval):
                metrictype = "TYPE_1"
            else:
                metrictype = "TYPE_2"

            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},IMPORT/config/metric-type', vrfname=vrf, protocol=importprotocol)
            body = {"openconfig-ospfv2-ext:metric-type": metrictype}
            response = api.patch(keypath, body)
            if response.ok() == False : return response

        if (routemapval != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},IMPORT/config/route-map', vrfname=vrf, protocol=importprotocol)
            body = {"openconfig-ospfv2-ext:route-map": routemapval}
            response = api.patch(keypath, body)
            if response.ok() == False : return response

        return response

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_redistribute_list_config_import':
        vrf = ""
        response = {}
        protocol = ""
        metriccmd = ""
        metrictypecmd = ""
        routemapcmd = ""
        i = 0

        for arg in args:
            if (arg == "metric"):
                metriccmd = "metric"
            elif (arg == "metric-type"):
                metrictypecmd = "metric-type"
            elif (arg == "route-map"):
                routemapcmd = "route-map"

            i = i + 1

        vrf = args[0]
        importprotocol = cli_to_db_protocol_map(args[1])

        if (metriccmd == "" and metrictypecmd == "" and routemapcmd == ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},IMPORT', vrfname=vrf, protocol=importprotocol)
            response = api.delete(keypath)
            if response.ok() == False : return response

        if (metriccmd != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},IMPORT/config/metric', vrfname=vrf, protocol=importprotocol)
            response = api.delete(keypath)
            if response.ok() == False : return response
 
        if (metrictypecmd != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},IMPORT/config/metric-type', vrfname=vrf, protocol=importprotocol)
            response = api.delete(keypath)
            if response.ok() == False : return response

        if (routemapcmd != ""):
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},IMPORT/config/route-map', vrfname=vrf, protocol=importprotocol)
            response = api.delete(keypath)
            if response.ok() == False : return response

        return response
    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_always':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config/always', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:always": True}
        return api.patch(keypath, body)



    ##--------Area related commands begins

    elif func == 'patch_openconfig_ospfv2_area':
        vrf = args[0]
        areaidval = args[1]
        response = {}
        i = 0

        for arg in args:

            if (arg == "virtual-link"):
                vlinkid = args[i +1]

                keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:enable', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                body = {"openconfig-ospfv2-ext:enable": True}

                response = api.patch(keypath)
                if response.ok() == False : return response

                j = i
                for vlinkarg in args[i:]:
                    if (vlinkarg == "dead-interval"):
                        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:dead-interval', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                        body = {"openconfig-ospfv2-ext:dead-interval": int(args[j + 1])}
                        return api.patch(keypath, body)

                    if (vlinkarg == "hello-interval"):
                        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:hello-interval', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                        body = {"openconfig-ospfv2-ext:hello-interval": int(args[j + 1])}
                        return api.patch(keypath, body)

                    if  (vlinkarg == "retransmit-interval"):
                        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:retransmission-interval', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                        body = {"openconfig-ospfv2-ext:retransmission-interval": int(args[j + 1])}
                        response = api.patch(keypath, body)
                        if response.ok() == False : return response

                    if (vlinkarg == "transmit-delay"):
                        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:transmit-delay', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                        body = {"openconfig-ospfv2-ext:transmit-delay": int(args[j + 1])}
                        return api.patch(keypath, body)

                    if (vlinkarg == "authentication"):
                        if (args[j + 1] == "null"):
                            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:authentication-type', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                            body = {"openconfig-ospfv2-ext:authentication-type": "NONE"}
                            response = api.patch(keypath, body)
                            if response.ok() == False : return response
                        else:
                            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:authentication-type', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                            body = {"openconfig-ospfv2-ext:authentication-type": "MD5HMAC"}
                            response = api.patch(keypath, body)
                            if response.ok() == False : return response
 
                            if (len(args[(j + 1):]) > 1):
                                keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:authentication-key-id', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                                body = {"openconfig-ospfv2-ext:authentication-key-id": int(args[j + 3])}
                                response = api.patch(keypath, body)
                                if response.ok() == False : return response

                                keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:authentication-md5-key', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                                body = {"openconfig-ospfv2-ext:authentication-md5-key": args[j + 4]}
                                response = api.patch(keypath, body)
                                if response.ok() == False : return response

                    if (vlinkarg == "authentication-key"):
                        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:authentication-key', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                        body = {"openconfig-ospfv2-ext:authentication-key": args[j + 1]}
                        response = api.patch(keypath, body)
                        if response.ok() == False : return response

                    j = j + 1

                return response
            elif (arg == "authentication"):
                if (len(args[i:]) > 1 and args[i + 1] == "message-digest"):
                    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/config/openconfig-ospfv2-ext:authentication-type', vrfname=vrf, areaid=areaidval)
                    body = {"openconfig-ospfv2-ext:authentication-type": "MD5HMAC"}
                    return api.patch(keypath, body)
                else:
                    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/config/openconfig-ospfv2-ext:authentication-type', vrfname=vrf, areaid=areaidval)
                    body = {"openconfig-ospfv2-ext:authentication-type": "TEXT"}
                    return api.patch(keypath, body)

            elif (arg == "default-cost"):
                keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/openconfig-ospfv2-ext:stub/config/default-cost', vrfname=vrf, areaid=areaidval)
                body = {"openconfig-ospfv2-ext:default-cost": int(args[i + 1])}
                return api.patch(keypath, body)

            elif (arg == "filter-list"):
                prefixname = args[i + 2]
                direction = args[i + 3]

                if (direction == "in"):
                    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/filter-list-in/config/name', vrfname=vrf, areaid=areaidval)
                    body = {"openconfig-ospfv2-ext:name": prefixname}
                    return api.patch(keypath, body)
                elif (direction == "out"):
                    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/filter-list-out/config/name', vrfname=vrf, areaid=areaidval)
                    body = {"openconfig-ospfv2-ext:name": prefixname}
                    return api.patch(keypath, body)

            elif (arg == "range"):
                range = args[i + 1]

                if (len(args[(i + 1):]) == 1):
                    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}/config', vrfname=vrf, areaid=areaidval, addressprefix=range)
                    body = {"openconfig-ospfv2-ext:config": { "address-prefix": range }}
                    return api.patch(keypath, body)

                j = i + 1
                for rangearg in args[j:]:
                    if (rangearg == "advertise"):
                        if (len(args[j:]) > 1):
                            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}/config/metric', vrfname=vrf, areaid=areaidval, addressprefix=range)
                            body = {"openconfig-ospfv2-ext:metric": int(args[j + 2])}
                            return api.patch(keypath, body)
                        else:
                            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}/config/advertise', vrfname=vrf, areaid=areaidval, addressprefix=range)
                            body = {"openconfig-ospfv2-ext:advertise": True}
                            return api.patch(keypath, body)
                    elif (rangearg == "cost"):
                        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}/config/metric', vrfname=vrf, areaid=areaidval, addressprefix=range)
                        body = {"openconfig-ospfv2-ext:metric": int(args[j + 1])}
                        return api.patch(keypath, body)
                    elif (rangearg == "not-advertise"):
                            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}/config/advertise', vrfname=vrf, areaid=areaidval, addressprefix=range)
                            body = {"openconfig-ospfv2-ext:advertise": False}
                            return api.patch(keypath, body)
                    elif (rangearg == "substitute"):
                        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}/config/substitue-prefix', vrfname=vrf, areaid=areaidval, addressprefix=range)
                        body = {"openconfig-ospfv2-ext:substitue-prefix": args[j + 1]}
                        return api.patch(keypath, body)
                    j = j + 1

            elif (arg == "stub"):
                if (len(args[i:]) > 1):
                    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/openconfig-ospfv2-ext:stub/config/no-summary', vrfname=vrf, areaid=areaidval)
                    body = {"openconfig-ospfv2-ext:no-summary": True}
                    return api.patch(keypath, body)
                else:
                    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/openconfig-ospfv2-ext:stub/config/enable', vrfname=vrf, areaid=areaidval)
                    body = {"openconfig-ospfv2-ext:enable": True}
                    return api.patch(keypath, body)
            elif (arg == "shortcut"):
                shortcuttype = ""

                if (args[i + 1] == "default"):
                    shortcuttype = "DEFAULT"
                elif (args[i + 1] == "disable"):
                    shortcuttype = "DISABLE"
                elif (args[i + 1] == "enable"):
                    shortcuttype = "ENABLE"

                keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/config/openconfig-ospfv2-ext:shortcut', vrfname=vrf, areaid=areaidval)
                body = {"openconfig-ospfv2-ext:shortcut": shortcuttype}
                return api.patch(keypath, body)

            i = i + 1

    elif func == 'delete_openconfig_ospfv2_area':
        vrf = args[0]
        areaidval = args[1]
        response = {}
        i = 0

        for arg in args:

            if (arg == "virtual-link"):
                vlinkid = args[i +1]

                if (len(args[(i + 1):]) == 1):
                    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:enable', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                    return api.delete(keypath)

                j = i + 1
                for vlinkarg in args[i:]:
                    if (vlinkarg == "dead-interval"):
                        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:dead-interval', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                        return api.delete(keypath)

                    if (vlinkarg == "hello-interval"):
                        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:hello-interval', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                        return api.delete(keypath)

                    if  (vlinkarg == "retransmit-interval"):
                        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:retransmission-interval', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                        return api.delete(keypath)

                    if (vlinkarg == "transmit-delay"):
                        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:transmit-delay', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                        return api.delete(keypath)

                    if (vlinkarg == "authentication"):
                        if (args[j] == "null"):
                            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:authentication-type', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                            response = api.delete(keypath)
                            if response.ok() == False : return response
                        else:
                            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:authentication-type', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                            response = api.delete(keypath)
                            if response.ok() == False : return response

                            if (len(args[j:]) > 1):
                                keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:authentication-key-id', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                                response = api.delete(keypath)
                                if response.ok() == False : return response

                                keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:authentication-md5-key', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                                response = api.delete(keypath)
                                if response.ok() == False : return response

                    if (vlinkarg == "authentication-key"):
                        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:authentication-key', vrfname=vrf, areaid=areaidval, linkid=vlinkid)
                        response = api.delete(keypath)
                        if response.ok() == False : return response

                    j = j + 1

                return response
            elif (arg == "authentication"):
                keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/config/openconfig-ospfv2-ext:authentication-type', vrfname=vrf, areaid=areaidval)
                return api.delete(keypath)

            elif (arg == "default-cost"):
                keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/openconfig-ospfv2-ext:stub/config/default-cost', vrfname=vrf, areaid=areaidval)
                return api.delete(keypath)

            elif (arg == "filter-list"):
                direction = args[i + 2]

                if (direction == "in"):
                    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/filter-list-in/config/name', vrfname=vrf, areaid=areaidval)
                    return api.delete(keypath)
                elif (direction == "out"):
                    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/filter-list-out/config/name', vrfname=vrf, areaid=areaidval)
                    return api.delete(keypath)
                
            elif (arg == "range"):
                range = args[i + 1]

                if (len(args[(i + 1):]) == 1):
                    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}', vrfname=vrf, areaid=area_to_dotted(areaidval), addressprefix=range)
                    return api.delete(keypath)

                j = i + 1
                for rangearg in args[j:]:
                    if (rangearg == "advertise"):
                        if (len(args[j:]) > 1):
                            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}/config/metric', vrfname=vrf, areaid=areaidval, addressprefix=range)
                            return api.delete(keypath)
                        else:
                            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}/config/advertise', vrfname=vrf, areaid=areaidval, addressprefix=range)
                            return api.delete(keypath)
                    elif (rangearg == "cost"):
                        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}/config/metric', vrfname=vrf, areaid=areaidval, addressprefix=range)
                        return api.delete(keypath)
                    elif (rangearg == "not-advertise"):
                            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}/config/advertise', vrfname=vrf, areaid=areaidval, addressprefix=range)
                            return api.delete(keypath)
                    elif (rangearg == "substitute"):
                        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}/config/substitue-prefix', vrfname=vrf, areaid=areaidval, addressprefix=range)
                        return api.delete(keypath)
                    j = j + 1

            elif (arg == "stub"):
                if (len(args[i:]) > 1):
                    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/openconfig-ospfv2-ext:stub/config/no-summary', vrfname=vrf, areaid=areaidval)
                    return api.delete(keypath)
                else:
                    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/openconfig-ospfv2-ext:stub/config/enable', vrfname=vrf, areaid=areaidval)
                    return api.delete(keypath)
            elif (arg == "shortcut"):
                keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/config/openconfig-ospfv2-ext:shortcut', vrfname=vrf, areaid=areaidval)
                return api.delete(keypath)

            i = i + 1

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_networks_network_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/openconfig-ospfv2-ext:networks/network={addressprefix}/config', vrfname=args[0], areaid=args[1], addressprefix=args[2])
        body = { "openconfig-ospfv2-ext:config": { "address-prefix": args[2] }}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_networks_network':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/openconfig-ospfv2-ext:networks/network={addressprefix}', vrfname=args[0], areaid=area_to_dotted(args[1]), addressprefix=args[2])
        return api.delete(keypath)

    #-------- Ospf interface cli handling start
    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_vrf' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/vrf', ospf_if=if_name, ospf_if_addr=if_address)
        body = {"openconfig-ospfv2-ext:vrf": args[1]}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_vrf' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/vrf', ospf_if=if_name, ospf_if_addr=if_address)
        return api.delete(keypath)

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_area_id' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/area-id', ospf_if=if_name, ospf_if_addr=if_address)
        body = { "openconfig-ospfv2-ext:area-id": int(args[1]) if args[1].isdigit() else args[1]}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_area_id' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/area-id', ospf_if=if_name, ospf_if_addr=if_address)
        return api.delete(keypath)

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_type' :
        if_name = args[0]
        if_address = "0.0.0.0"
        auth_type = "TEXT"

        if len(args) == 2 :
           if args[1] == "null" :
               auth_type = "NONE"
           elif args[1] == "message-digest" :
               auth_type = "MD5HMAC"
           else :
               if_address = args[1] if (args[1] != "") else "0.0.0.0"
        elif len(args) >= 3 :
           if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
           if args[1] == "null" :
               auth_type = "NONE"
           elif args[1] == "message-digest" :
               auth_type = "MD5HMAC"

        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/authentication-type', ospf_if=if_name, ospf_if_addr=if_address)

        body = { "openconfig-ospfv2-ext:authentication-type": auth_type}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_type' :
        if_name = args[0]
        if_address = "0.0.0.0"
        auth_type = "TEXT"

        if len(args) == 2 :
           if args[1] == "null" :
               auth_type = "NONE"
           elif args[1] == "message-digest" :
               auth_type = "MD5HMAC"
           else :
               if_address = args[1] if (args[1] != "") else "0.0.0.0"
        elif len(args) >= 3 :
           if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
           if args[1] == "null" :
               auth_type = "NONE"
           elif args[1] == "message-digest" :
               auth_type = "MD5HMAC"

        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/authentication-type', ospf_if=if_name, ospf_if_addr=if_address)
        return api.delete(keypath)

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_key' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/authentication-key', ospf_if=if_name, ospf_if_addr=if_address)
        body = { "openconfig-ospfv2-ext:authentication-key": args[1]}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_key' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/authentication-key', ospf_if=if_name, ospf_if_addr=if_address)
        return api.delete(keypath)

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_key_id' :
        if_name = args[0]
        if_address = args[3] if (len(args) >= 4 and args[3] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/authentication-key-id', ospf_if=if_name, ospf_if_addr=if_address)
        body = {  "openconfig-ospfv2-ext:authentication-key-id": int(args[1]), "openconfig-ospfv2-ext:authentication-md5-key": args[2]}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_key_id' :
        if_name = args[0]
        if_address = args[3] if (len(args) >= 4 and args[3] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/authentication-key-id', ospf_if=if_name, ospf_if_addr=if_address)
        response = api.delete(keypath)
        if response.ok() == False : return response
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/authentication-md5-key', ospf_if=if_name, ospf_if_addr=if_address)
        return api.delete(keypath)

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_md5_key' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/authentication-md5-key', ospf_if=if_name, ospf_if_addr=if_address)
        body = {  "openconfig-ospfv2-ext:authentication-md5-key": args[1]}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_md5_key' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/authentication-md5-key', ospf_if=if_name, ospf_if_addr=if_address)
        return api.delete(keypath)

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_bfd' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/bfd-enable', ospf_if=if_name, ospf_if_addr=if_address)
        body = { "openconfig-ospfv2-ext:bfd-enable": True }
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_bfd' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/bfd-enable', ospf_if=if_name, ospf_if_addr=if_address)
        return api.delete(keypath)

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_cost' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/metric', ospf_if=if_name, ospf_if_addr=if_address)
        body = { "openconfig-ospfv2-ext:metric": int(args[1]) } 
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_cost' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/metric', ospf_if=if_name, ospf_if_addr=if_address)
        return api.delete(keypath)

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_mtu_ignore' :
        if_name = args[0]
        if_address = args[1] if (len(args) >= 2 and args[1] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/mtu-ignore', ospf_if=if_name, ospf_if_addr=if_address)
        body = { "openconfig-ospfv2-ext:mtu-ignore": True }  
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_mtu_ignore' :
        if_name = args[0]
        if_address = args[1] if (len(args) >= 2 and args[1] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/mtu-ignore', ospf_if=if_name, ospf_if_addr=if_address)
        return api.delete(keypath)

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_network_type' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/network-type', ospf_if=if_name, ospf_if_addr=if_address)
        network_type = ""
        if args[1] == "point-to-point" :
          network_type = "POINT_TO_POINT_NETWORK"
        elif args[1] == "broadcast" :
          network_type = "BROADCAST_NETWORK"
        if network_type != "" :
          body = { "openconfig-ospfv2-ext:network-type": network_type }
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_network_type' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/network-type', ospf_if=if_name, ospf_if_addr=if_address)
        return api.delete(keypath)

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_priority' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/priority', ospf_if=if_name, ospf_if_addr=if_address)
        body = { "openconfig-ospfv2-ext:priority": int(args[1]) }
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_priority' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/priority', ospf_if=if_name, ospf_if_addr=if_address)
        return api.delete(keypath)

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_dead_interval' :
        if_name = args[0]
        if_address = args[3] if (len(args) >= 4 and args[3] != "") else "0.0.0.0"

        deadtype = args[1]
        if deadtype != "" and deadtype == 'deadinterval' :
            keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/dead-interval', ospf_if=if_name, ospf_if_addr=if_address)
            body = { "openconfig-ospfv2-ext:dead-interval": int(args[2]), "openconfig-ospfv2-ext:dead-interval-minimal": False }
            return api.patch(keypath, body)
        elif deadtype != "" and deadtype == 'minimal' :
            keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/hello-multiplier', ospf_if=if_name, ospf_if_addr=if_address)
            body = { "openconfig-ospfv2-ext:hello-multiplier": int(args[2]), "openconfig-ospfv2-ext:dead-interval-minimal": True }  
            return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_dead_interval' :
        if_name = args[0]
        if_address = "0.0.0.0"
        deadtype = ''
        if len(args) >= 2 and args[1] != '' : deadtype = args[1]
        #print("System arguments - args {} deadtype {}".format(args, deadtype))
        if deadtype == 'minimal' :
            if len(args) >= 3 and args[2] != '' : if_address = args[2]
            keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/dead-interval-minimal', ospf_if=if_name, ospf_if_addr=if_address)
            response = api.delete(keypath)
            if response.ok() == False : return response
            keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/dead-interval', ospf_if=if_name, ospf_if_addr=if_address)
            response = api.delete(keypath)
            if response.ok() == False : return response
            keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/hello-multiplier', ospf_if=if_name, ospf_if_addr=if_address)
            return api.delete(keypath)
        else :
            if deadtype == 'ip-address' :
                if len(args) >= 3 and args[2] != '' : if_address = args[2]
            else :
                if len(args) >= 2 and args[1] != '' : if_address = args[1]
            keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/dead-interval-minimal', ospf_if=if_name, ospf_if_addr=if_address)
            response = api.delete(keypath)
            if response.ok() == False : return response
            keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/hello-multiplier', ospf_if=if_name, ospf_if_addr=if_address)
            response = api.delete(keypath)
            if response.ok() == False : return response
            keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/dead-interval', ospf_if=if_name, ospf_if_addr=if_address)
            return api.delete(keypath)

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_hello_multiplier' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/hello-multiplier', ospf_if=if_name, ospf_if_addr=if_address)
        body = { "openconfig-ospfv2-ext:hello-multiplier": int(args[1]) }    
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_hello_multiplier' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/hello-multiplier', ospf_if=if_name, ospf_if_addr=if_address)
        return api.delete(keypath)

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_hello_interval' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/hello-interval', ospf_if=if_name, ospf_if_addr=if_address)
        body = { "openconfig-ospfv2-ext:hello-interval": int(args[1]) }   
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_hello_interval' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/hello-interval', ospf_if=if_name, ospf_if_addr=if_address)
        return api.delete(keypath)

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_retransmit_interval' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/retransmission-interval', ospf_if=if_name, ospf_if_addr=if_address)
        body = { "openconfig-ospfv2-ext:retransmission-interval": int(args[1]) }  
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_retransmit_interval' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/retransmission-interval', ospf_if=if_name, ospf_if_addr=if_address)
        return api.delete(keypath)

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_transmit_delay' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/transmit-delay', ospf_if=if_name, ospf_if_addr=if_address)
        body = { "openconfig-ospfv2-ext:transmit-delay": int(args[1]) } 
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_transmit_delay' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/transmit-delay', ospf_if=if_name, ospf_if_addr=if_address)
        return api.delete(keypath)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_unconfig' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2', ospf_if=if_name, ospf_if_addr=if_address)
        return api.delete(keypath)
    #-------- Ospf interface cli handling end

    else:
        body = {}
 
    return api.cli_not_implemented(func)



def run(func, args):
    response = invoke_api(func, args)

    if response.ok():
	if response.content is not None:
	    print("Failed")
    else:
        print(response.error_message())

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    #print("System arguments - {}".format(sys.argv))

    run(func, sys.argv[2:])
