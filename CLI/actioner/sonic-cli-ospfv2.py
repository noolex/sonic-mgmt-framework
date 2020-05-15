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
from rpipe_utils import pipestr
import cli_client as cc
from scripts.render_cli import show_cli_output

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

    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_config_log_adjacency_changes_details':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/log-adjacency-changes', vrfname=args[0])
        body = {"openconfig-network-instance:log-adjacency-changes": "DETAIL"}
        return api.patch(keypath, body)

    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_config_log_adjacency_changes':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/log-adjacency-changes', vrfname=args[0])
        body = {"openconfig-network-instance:log-adjacency-changes": "BRIEF"}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_config_log_adjacency_changes':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/log-adjacency-changes', vrfname=args[0])
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

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_abr_type':
        abrtype = None

        if args[1] == "cisco":
            abrtype = "CISCO" 
        elif args[1] == "ibm":
            abrtype = "IBM"
        elif args[1] == "shortcut":
            abrtype = "SHORTCUT"
        elif args[1] == "standard":
            abrtype = "STANDARD"

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:abr-type', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:abr-type": abrtype}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_abr_type':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:abr-type', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_ospf_rfc1583_compatible':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:ospf-rfc1583-compatible', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:ospf-rfc1583-compatible": True}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_ospf_rfc1583_compatible':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:ospf-rfc1583-compatible', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_passive_interface_default':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:passive-interface-default', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:passive-interface-default": True}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_passive_interface_default':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/config/openconfig-ospfv2-ext:passive-interface-default', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_passive_interface':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:passive-interfaces/passive-interface={intfname},{intfaddr}', vrfname=args[0], intfname=args[1], intfaddr=args[2])
        body = {"openconfig-ospfv2-ext:passive-interface": [{"name": args[1], "address": args[2], "config": {"name": args[1],"address": args[2]}}]}
        return api.patch(keypath, body)
		
    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_passive_interface':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:passive-interfaces/passive-interface={intfname},{intfaddr}', vrfname=args[0], intfname=args[1], intfaddr=args[2])
        return api.delete(keypath)

    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_lsa_generation_config_minimum_arrival':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/lsa-generation/config/openconfig-ospfv2-ext:minimum-arrival', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:minimum-arrival": int(args[1])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_lsa_generation_config_minimum_arrival':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/lsa-generation/config/openconfig-ospfv2-ext:minimum-arrival', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_lsa_generation_config_minimum_interval':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/lsa-generation/config/openconfig-ospfv2-ext:minimum-interval', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:minimum-interval": int(args[1])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_lsa_generation_config_minimum_interval':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/lsa-generation/config/openconfig-ospfv2-ext:minimum-interval', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_spf':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/spf', vrfname=args[0])
        body = {"openconfig-network-instance:spf": { "config": { "initial-delay": int(args[1]), "maximum-delay": int(args[2]), "openconfig-ospfv2-ext:throttle-delay": int(args[3]) } }}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_spf_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/spf/config', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_max_metric_config_administrative':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/max-metric/config/openconfig-ospfv2-ext:administrative', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:administrative": True}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_max_metric_config_administrative':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/max-metric/config/openconfig-ospfv2-ext:administrative', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_max_metric_config_on_startup':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/max-metric/config/openconfig-ospfv2-ext:on-startup', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:on-startup": int(args[1])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_max_metric_config_on_startup':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/max-metric/config/openconfig-ospfv2-ext:on-startup', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_max_metric_config_on_shutdown':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/max-metric/config/openconfig-ospfv2-ext:on-shutdown', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:on-shutdown": int(args[1])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_max_metric_config_on_shutdown':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/max-metric/config/openconfig-ospfv2-ext:on-shutdown', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_lsa_generation_config_refresh_timer':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/lsa-generation/config/openconfig-ospfv2-ext:refresh-timer', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:refresh-timer": int(args[1])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_lsa_generation_config_refresh_timer':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/lsa-generation/config/openconfig-ospfv2-ext:refresh-timer', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distance_config_all':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distance/config/all', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:all": int(args[1])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distance_config_all':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distance/config/all', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distance_config_intra_area':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distance/config/intra-area', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:intra-area": int(args[1])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distance_config_intra_area':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distance/config/intra-area', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distance_config_inter_area':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distance/config/inter-area', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:inter-area": int(args[1])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distance_config_inter_area':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distance/config/inter-area', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distance_config_external':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distance/config/external', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:external": int(args[1])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distance_config_external':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distance/config/external', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_route_map':
        importprotocol = None
       
        if (args[1] == "ospf"):
            importprotocol = "OSPF"
        elif (args[1] == "bgp"):
            importprotocol = "BGP"
        elif (args[1] == "static"):
            importprotocol = "STATIC"
        elif (args[1] == "kernel"):
            importprotocol = "KERNEL"
        elif (args[1] == "connected"):
            importprotocol = "DIRECTLY_CONNECTED"
        elif (args[1] == "table"):
            importprotocol = "DEFAULT_ROUTE"

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},IMPORT/config/route-map', vrfname=args[0], protocol=importprotocol)
        body = {"openconfig-ospfv2-ext:route-map": (args[2])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_route_map':
        importprotocol = None

        if (args[1] == "ospf"):
            importprotocol = "OSPF"
        elif (args[1] == "bgp"):
            importprotocol = "BGP"
        elif (args[1] == "static"):
            importprotocol = "STATIC"
        elif (args[1] == "kernel"):
            importprotocol = "KERNEL"
        elif (args[1] == "connected"):
            importprotocol = "DIRECTLY_CONNECTED"
        elif (args[1] == "table"):
            importprotocol = "DEFAULT_ROUTE"

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},IMPORT/config/route-map', vrfname=args[0], protocol=importprotocol)
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_import':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config', vrfname=args[0])
        body = { "openconfig-ospfv2-ext:config": { "protocol": "DEFAULT_ROUTE", "direction": "IMPORT" }}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_import':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_metric':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config/metric', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:metric": int(args[2])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_metric':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config/metric', vrfname=args[0])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_metric_type':
        metrictype = None

        if ("1" == args[2]):
            metrictype = "TYPE_1"
        else:
            metrictype = "TYPE_2"

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config/metric-type', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:metric-type": metrictype}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_metric_type':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config/metric-type', vrfname=args[0])
        return api.delete(keypath)

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

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_export':
        exportprotocol = None
        if (args[1] == "ospf"):
            exportprotocol = "OSPF"
        elif (args[1] == "bgp"):
            exportprotocol = "BGP"
        elif (args[1] == "static"):
            exportprotocol = "STATIC"
        elif (args[1] == "kernel"):
            exportprotocol = "KERNEL"
        elif (args[1] == "connected"):
            exportprotocol = "DIRECTLY_CONNECTED"
        else:
            exportprotocol = "DEFAULT_ROUTE"

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},EXPORT/config', vrfname=args[0], protocol=exportprotocol)
        body = { "openconfig-ospfv2-ext:config": { "protocol": exportprotocol, "direction": "EXPORT" }}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_export':
        exportprotocol = None
        if (args[1] == "ospf"):
            exportprotocol = "OSPF"
        elif (args[1] == "bgp"):
            exportprotocol = "BGP"
        elif (args[1] == "static"):
            exportprotocol = "STATIC"
        elif (args[1] == "kernel"):
            exportprotocol = "KERNEL"
        elif (args[1] == "connected"):
            exportprotocol = "DIRECTLY_CONNECTED"
        else:
            exportprotocol = "DEFAULT_ROUTE"

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},EXPORT', vrfname=args[0], protocol=exportprotocol)
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_redistribute_list_config_metric':
        exportprotocol = None

        if (args[1] == "ospf"):
            exportprotocol = "OSPF"
        elif (args[1] == "bgp"):
            exportprotocol = "BGP"
        elif (args[1] == "static"):
            exportprotocol = "STATIC"
        elif (args[1] == "kernel"):
            exportprotocol = "KERNEL"
        elif (args[1] == "connected"):
            exportprotocol = "DIRECTLY_CONNECTED"
        else:
            exportprotocol = "DEFAULT_ROUTE"

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},EXPORT/config/metric', vrfname=args[0], protocol=exportprotocol)
        body = {"openconfig-ospfv2-ext:metric": int(args[2])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_redistribute_list_config_metric':
        exportprotocol = None

        if (args[1] == "ospf"):
            exportprotocol = "OSPF"
        elif (args[1] == "bgp"):
            exportprotocol = "BGP"
        elif (args[1] == "static"):
            exportprotocol = "STATIC"
        elif (args[1] == "kernel"):
            exportprotocol = "KERNEL"
        elif (args[1] == "connected"):
            exportprotocol = "DIRECTLY_CONNECTED"
        else:
            exportprotocol = "DEFAULT_ROUTE"

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},EXPORT/config/metric', vrfname=args[0], protocol=exportprotocol)
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_redistribute_list_config_metric_type':
        exportprotocol = None
        metrictype = None

        if (args[1] == "ospf"):
            exportprotocol = "OSPF"
        elif (args[1] == "bgp"):
            exportprotocol = "BGP"
        elif (args[1] == "static"):
            exportprotocol = "STATIC"
        elif (args[1] == "kernel"):
            exportprotocol = "KERNEL"
        elif (args[1] == "connected"):
            importprotocol = "DIRECTLY_CONNECTED"
        else:
            exportprotocol = "DEFAULT_ROUTE"

        if ("1" == args[2]):
            metrictype = "TYPE_1"
        else:
            metrictype = "TYPE_2"

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},EXPORT/config/metric-type', vrfname=args[0], protocol=exportprotocol)
        body = {"openconfig-ospfv2-ext:metric-type": metrictype}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_redistribute_list_config_metric_type':
        exportprotocol = None

        if (args[1] == "ospf"):
            exportprotocol = "OSPF"
        elif (args[1] == "bgp"):
            exportprotocol = "BGP"
        elif (args[1] == "static"):
            exportprotocol = "STATIC"
        elif (args[1] == "kernel"):
            exportprotocol = "KERNEL"
        elif (args[1] == "connected"):
            importprotocol = "DIRECTLY_CONNECTED"
        else:
            exportprotocol = "DEFAULT_ROUTE"

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},EXPORT/config/metric-type', vrfname=args[0], protocol=exportprotocol)
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_redistribute_list_config_route_map':
        exportprotocol = None

        if (args[1] == "ospf"):
            exportprotocol = "OSPF"
        elif (args[1] == "bgp"):
            exportprotocol = "BGP"
        elif (args[1] == "static"):
            exportprotocol = "STATIC"
        elif (args[1] == "kernel"):
            exportprotocol = "KERNEL"
        elif (args[1] == "connected"):
            exportprotocol = "DIRECTLY_CONNECTED"
        else:
            exportprotocol = "DEFAULT_ROUTE"

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},EXPORT/config/route-map', vrfname=args[0], protocol=exportprotocol)
        body = {"openconfig-ospfv2-ext:route-map": args[2]}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_redistribute_list_config_route_map':
        exportprotocol = None

        if (args[1] == "ospf"):
            exportprotocol = "OSPF"
        elif (args[1] == "bgp"):
            exportprotocol = "BGP"
        elif (args[1] == "static"):
            exportprotocol = "STATIC"
        elif (args[1] == "kernel"):
            exportprotocol = "KERNEL"
        elif (args[1] == "connected"):
            exportprotocol = "DIRECTLY_CONNECTED"
        else:
            exportprotocol = "DEFAULT_ROUTE"

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list={protocol},EXPORT/config/route-map', vrfname=args[0], protocol=exportprotocol)
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_always':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config/always', vrfname=args[0])
        body = {"openconfig-ospfv2-ext:always": True}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_always':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/openconfig-ospfv2-ext:route-distribution-policies/distribute-list=DEFAULT_ROUTE,IMPORT/config/always', vrfname=args[0])
        return api.delete(keypath)


    ##--------Area related commands begins

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_config_authentication_type_text':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/config/openconfig-ospfv2-ext:authentication-type', vrfname=args[0], areaid=args[1])
        body = {"openconfig-ospfv2-ext:authentication-type": "TEXT"}
        return api.patch(keypath, body)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_config_authentication_type_message_digest':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/config/openconfig-ospfv2-ext:authentication-type', vrfname=args[0], areaid=args[1])
        body = {"openconfig-ospfv2-ext:authentication-type": "MD5HMAC"}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_config_authentication_type':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/config/openconfig-ospfv2-ext:authentication-type', vrfname=args[0], areaid=args[1])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_stub_config_default_cost':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/openconfig-ospfv2-ext:stub/config/default-cost', vrfname=args[0], areaid=args[1])
        body = {"openconfig-ospfv2-ext:default-cost": int(args[2])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_stub_config_default_cost':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/openconfig-ospfv2-ext:stub/config/default-cost', vrfname=args[0], areaid=args[1])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_stub_config_enable':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/openconfig-ospfv2-ext:stub/config/enable', vrfname=args[0], areaid=args[1])
        body = {"openconfig-ospfv2-ext:enable": True}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_stub_config_enable':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/openconfig-ospfv2-ext:stub/config/enable', vrfname=args[0], areaid=args[1])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_stub_config_no_summary':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/openconfig-ospfv2-ext:stub/config/no-summary', vrfname=args[0], areaid=args[1])
        body = {"openconfig-ospfv2-ext:no-summary": True}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_stub_config_no_summary':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/openconfig-ospfv2-ext:stub/config/no-summary', vrfname=args[0], areaid=args[1])
        return api.delete(keypath)

    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_virtual_links_virtual_link':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}', vrfname=args[0], areaid=args[1], linkid=args[2])
        body = {"openconfig-network-instance:virtual-link": [ { "remote-router-id": args[2], "config": { "remote-router-id": args[2]} }]}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_virtual_links_virtual_link':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}', vrfname=args[0], areaid=args[1], linkid=args[2])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_virtual_links_virtual_link_config_dead_interval':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:dead-interval', vrfname=args[0], areaid=args[1], linkid=args[2])
        body = {"openconfig-ospfv2-ext:dead-interval": int(args[3])}
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_virtual_links_virtual_link_config_dead_interval':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:dead-interval', vrfname=args[0], areaid=args[1], linkid=args[2])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_virtual_links_virtual_link_config_hello_interval':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:hello-interval', vrfname=args[0], areaid=args[1], linkid=args[2])
        body = {"openconfig-ospfv2-ext:hello-interval": int(args[3])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_virtual_links_virtual_link_config_hello_interval':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:hello-interval', vrfname=args[0], areaid=args[1], linkid=args[2])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_virtual_links_virtual_link_retransmission_interval':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:retransmission-interval', vrfname=args[0], areaid=args[1], linkid=args[2])
        body = {"openconfig-ospfv2-ext:retransmission-interval": int(args[3])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_virtual_links_virtual_link_retransmission_interval':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:retransmission-interval', vrfname=args[0], areaid=args[1], linkid=args[2])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_virtual_links_virtual_link_config_transmit_interval':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:transmit-delay', vrfname=args[0], areaid=args[1], linkid=args[2])
        body = {"openconfig-ospfv2-ext:transmit-delay": int(args[3])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_virtual_links_virtual_link_config_transmit_interval':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:transmit-delay', vrfname=args[0], areaid=args[1], linkid=args[2])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_virtual_links_virtual_link_config_auth_type_null':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:authentication/authentication-type', vrfname=args[0], areaid=args[1], linkid=args[2])
        body = {"openconfig-ospfv2-ext:authentication-type": "AUTH_NONE"}
        return api.patch(keypath, body)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_virtual_links_virtual_link_config_auth_type_message_digest':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:authentication/authentication-type', vrfname=args[0], areaid=args[1], linkid=args[2])
        body = {"openconfig-ospfv2-ext:authentication-type": "MD5HMAC"}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_virtual_links_virtual_link_config_auth_type':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:authentication/authentication-type', vrfname=args[0], areaid=args[1], linkid=args[2])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_virtual_links_virtual_link_config_auth_type_message_digest_keyid':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:authentication/authentication-key-id', vrfname=args[0], areaid=args[1], linkid=args[2])
        body = {"openconfig-ospfv2-ext:authentication-key-id": int(args[3])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_virtual_links_virtual_link_config_auth_type_message_digest_keyid':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:authentication/authentication-key-id', vrfname=args[0], areaid=args[1], linkid=args[2])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_virtual_links_virtual_link_config_auth_type_message_digest_md5pass':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:authentication/authentication-md5-key', vrfname=args[0], areaid=args[1], linkid=args[2])
        body = {"openconfig-ospfv2-ext:authentication-md5-key": args[3]}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_virtual_links_virtual_link_config_auth_type_message_digest_md5pass':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:authentication/authentication-md5-key', vrfname=args[0], areaid=args[1], linkid=args[2])
        return api.delete(keypath)
    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_virtual_links_virtual_link_config_auth_type_message_digest_key':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:authentication/authentication-key', vrfname=args[0], areaid=args[1], linkid=args[2])
        body = {"openconfig-ospfv2-ext:authentication-key": args[3]}
        return api.patch(keypath, body)    
    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_virtual_links_virtual_link_config_auth_type_message_digest_key':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/virtual-links/virtual-link={linkid}/config/openconfig-ospfv2-ext:authentication/authentication-key', vrfname=args[0], areaid=args[1], linkid=args[2])
        return api.delete(keypath)
    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_propagation_policy_address_prefix':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}/config', vrfname=args[0], areaid=args[1], addressprefix=args[2])
        body = {"openconfig-ospfv2-ext:config": { "address-prefix": args[2] }}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_propagation_policy_address_prefix':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}', vrfname=args[0], areaid=args[1], addressprefix=args[2])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_propagation_policy_address_prefix_advertise':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}/config/advertise', vrfname=args[0], areaid=args[1], addressprefix=args[2])
        body = {"openconfig-ospfv2-ext:advertise": True}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_propagation_policy_address_prefix_advertise':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}/config/advertise', vrfname=args[0], areaid=args[1], addressprefix=args[2])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_propagation_policy_address_prefix_metric':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}/config/metric', vrfname=args[0], areaid=args[1], addressprefix=args[2])
        body = {"openconfig-ospfv2-ext:metric": int(args[3])}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_propagation_policy_address_prefix_metric':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}/config/metric', vrfname=args[0], areaid=args[1], addressprefix=args[2])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_propagation_policy_address_prefix_notadvertise':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}/config/advertise', vrfname=args[0], areaid=args[1], addressprefix=args[2])
        body = {"openconfig-ospfv2-ext:advertise": False}
        return api.patch(keypath, body)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_propagation_policy_address_prefix_substitute':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}/config/substitue-prefix', vrfname=args[0], areaid=args[1], addressprefix=args[2])
        body = {"openconfig-ospfv2-ext:substitue-prefix": args[3]}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_propagation_policy_address_prefix_substitute':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/ranges/range={addressprefix}/config/substitue-prefix', vrfname=args[0], areaid=args[1], addressprefix=args[2])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_networks_network_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/openconfig-ospfv2-ext:networks/network={addressprefix}/config', vrfname=args[0], areaid=args[1], addressprefix=args[2])
        body = { "openconfig-ospfv2-ext:config": { "address-prefix": args[2] }}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_networks_network':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/areas/area={areaid}/openconfig-ospfv2-ext:networks/network={addressprefix}', vrfname=args[0], areaid=args[1], addressprefix=args[2])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_area_importlist':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/import-list/config/name', vrfname=args[0], areaid=args[1])
        body = {"openconfig-ospfv2-ext:name": args[2]}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_area_importlist':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/import-list/config/name', vrfname=args[0], areaid=args[1])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_area_exportlist':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/export-list/config/name', vrfname=args[0], areaid=args[1])
        body = {"openconfig-ospfv2-ext:name": args[2]}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_area_exportlist':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/export-list/config/name', vrfname=args[0], areaid=args[1])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_area_filterlist_in':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/filter-list-in/config/name', vrfname=args[0], areaid=args[1])
        body = {"openconfig-ospfv2-ext:name": args[2]}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_area_filterlist_in':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/filter-list-in/config/name', vrfname=args[0], areaid=args[1])
        return api.delete(keypath)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_area_filterlist_out':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/filter-list-out/config/name', vrfname=args[0], areaid=args[1])
        body = {"openconfig-ospfv2-ext:name": args[2]}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_area_filterlist_out':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrfname}/protocols/protocol=OSPF,ospfv2/ospfv2/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={areaid}/filter-list-out/config/name', vrfname=args[0], areaid=args[1])
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
               auth_type = "AUTH_NONE"
           elif args[1] == "message-digest" :
               auth_type = "MD5HMAC"
           else :
               if_address = args[1] if (args[1] != "") else "0.0.0.0"
        elif len(args) >= 3 :
           if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
           if args[1] == "null" :
               auth_type = "AUTH_NONE"
           elif args[1] == "message-digest" :
               auth_type = "MD5HMAC"

        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/authentication/authentication-type', ospf_if=if_name, ospf_if_addr=if_address)

        body = { "openconfig-ospfv2-ext:authentication-type": auth_type}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_type' :
        if_name = args[0]
        if_address = "0.0.0.0"
        auth_type = "TEXT"

        if len(args) == 2 :
           if args[1] == "null" :
               auth_type = "AUTH_NONE"
           elif args[1] == "message-digest" :
               auth_type = "MD5HMAC"
           else :
               if_address = args[1] if (args[1] != "") else "0.0.0.0"
        elif len(args) >= 3 :
           if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
           if args[1] == "null" :
               auth_type = "AUTH_NONE"
           elif args[1] == "message-digest" :
               auth_type = "MD5HMAC"

        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/authentication/authentication-type', ospf_if=if_name, ospf_if_addr=if_address)
        return api.delete(keypath)

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_key' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/authentication/authentication-key', ospf_if=if_name, ospf_if_addr=if_address)
        body = { "openconfig-ospfv2-ext:authentication-key": args[1]}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_key' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/authentication/authentication-key', ospf_if=if_name, ospf_if_addr=if_address)
        return api.delete(keypath)

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_key_id' :
        if_name = args[0]
        if_address = args[3] if (len(args) >= 4 and args[3] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/authentication/authentication-key-id', ospf_if=if_name, ospf_if_addr=if_address)
        body = {  "openconfig-ospfv2-ext:authentication-key-id": int(args[1]), "openconfig-ospfv2-ext:authentication-md5-key": args[2]}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_key_id' :
        if_name = args[0]
        if_address = args[3] if (len(args) >= 4 and args[3] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/authentication/authentication-key-id', ospf_if=if_name, ospf_if_addr=if_address)
        response = api.delete(keypath)
        if response.ok() == False : return response
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/authentication/authentication-md5-key', ospf_if=if_name, ospf_if_addr=if_address)
        return api.delete(keypath)

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_md5_key' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/authentication/authentication-md5-key', ospf_if=if_name, ospf_if_addr=if_address)
        body = {  "openconfig-ospfv2-ext:authentication-md5-key": args[1]}
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_md5_key' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={ospf_if}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2/if-addresses={ospf_if_addr}/config/authentication/authentication-md5-key', ospf_if=if_name, ospf_if_addr=if_address)
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
