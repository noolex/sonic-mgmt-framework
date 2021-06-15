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
from scripts.render_cli import show_cli_output
from routemap_openconfig_to_restconf import restconf_map


def invoke_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None
    internal_op = "REPLACE"

    op, attr = func.split('_', 1)
    if op == 'patchRemove':
        internal_op = "REMOVE"
        op = 'patch'

    if op == 'patch':
        uri = restconf_map[attr]
        if attr == 'openconfig_routing_policy_routing_policy_policy_definitions_policy_definition_statements_statement_actions_config_policy_result':
            keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions')
            body = { "openconfig-routing-policy:policy-definitions":
                     {"policy-definition":[{"name":args[0],"config":{"name":args[0]},
                      "statements":{"statement": [{"name":args[1],"config":{"name":args[1]},
                       "actions": { "config": {"policy-result": "ACCEPT_ROUTE" if args[2] == 'permit' else "REJECT_ROUTE"}}
                       }] } }] }}

            return api.patch(keypath, body)

        elif attr == 'openconfig_routing_policy_routing_policy_policy_definitions_policy_definition_statements_statement_actions_metric_action_config_set_metric':
            #print("Set metric arguments - args {}".format(args))
            if len(args) < 3 :
                return api.cli_not_implemented(func)

            metric_action = ''
            metric_value = ''
            metric_type = args[2]
            if metric_type == 'metric' :
                metric_value_str = args[3]
                metric_action = 'METRIC_SET_VALUE'
                if metric_value_str.startswith('+') :
                    metric_value = long(metric_value_str[1:])
                    metric_action = 'METRIC_ADD_VALUE'
                if metric_value_str.startswith('-') :
                    metric_value = long(metric_value_str[1:])
                    metric_action = 'METRIC_SUBTRACT_VALUE'
                else :
                    metric_value = long(metric_value_str)
            elif metric_type == 'rtt' :
                metric_action = 'METRIC_SET_RTT'
            elif metric_type == '+rtt' :
                metric_action = 'METRIC_ADD_RTT'
            elif metric_type == '-rtt' :
                metric_action = 'METRIC_SUBTRACT_RTT'
            else :
                return api.cli_not_implemented(func)

            #print("Set metric type: {} vlaue {}".format(metric_action, metric_value))
            #This block have to be removed once bgp med config is reorganized
            if metric_action == 'METRIC_SET_VALUE'  and metric_value != '' :
                med_uri = restconf_map['openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_actions_bgp_actions_config_set_med']
                med_keypath = cc.Path(med_uri, name=args[0], name1=args[1])
                med_body = { "openconfig-bgp-policy:set-med" : metric_value }
                api.patch(med_keypath, med_body)

            keypath = cc.Path(uri, name=args[0], name1=args[1])
            if metric_value != '' :
                body = {"config": { "action": metric_action, "metric": metric_value }}
            else :
                body = {"config": { "action": metric_action }}
            return api.patch(keypath, body)

        elif attr == 'openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_actions_bgp_actions_config_set_next_hop':
            if args[2] == 'ipv6' and args[3] == 'prefer-global':
                keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/actions/openconfig-bgp-policy:bgp-actions/config/set-ipv6-next-hop-prefer-global', name=args[0], name1=args[1])
                body = { "set-ipv6-next-hop-prefer-global" : True }
            elif args[2] == 'ipv6' and args[3] == 'global':
                keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/actions/openconfig-bgp-policy:bgp-actions/config/set-ipv6-next-hop-global', name=args[0], name1=args[1])
                body = { "set-ipv6-next-hop-global" : args[4] }
            elif args[2] == 'ipv4':
                keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/actions/openconfig-bgp-policy:bgp-actions/config/set-next-hop', name=args[0], name1=args[1])
                body = { "openconfig-bgp-policy:set-next-hop" : args[3] }
            else:
                return api.cli_not_implemented(func)

            return api.patch(keypath, body)
        elif attr == 'openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_actions_bgp_actions_config_set_local_pref':
            keypath = cc.Path(uri, name=args[0], name1=args[1])
            body = { "openconfig-bgp-policy:set-local-pref" : int(args[2]) }
            return api.patch(keypath, body)
        elif attr == 'openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_actions_bgp_actions_config_set_med':
            keypath = cc.Path(uri, name=args[0], name1=args[1])
            body = { "openconfig-bgp-policy:set-med" : int(args[2]) }
            return api.patch(keypath, body)
        elif attr == 'openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_actions_bgp_actions_config_set_route_origin':
            keypath = cc.Path(uri, name=args[0], name1=args[1])
            body = { "openconfig-bgp-policy:set-route-origin" : args[2].upper() }
            return api.patch(keypath, body)
        elif attr == 'openconfig_routing_policy_ext_routing_policy_policy_definitions_policy_definition_statements_statement_actions_bgp_actions_set_as_path_prepend_config_asn_list':
            keypath = cc.Path(uri, name=args[0], name1=args[1])
            body = {"openconfig-routing-policy-ext:asn-list":args[2]}
            return api.patch(keypath, body)
        elif attr == 'bgp_actions_set_community':
            keypath = cc.Path(uri, name=args[0], name1=args[1])
            comm_list = []
            i = 0
            for arg in args[2:]:
                if arg == "additive":
                    comm_val = "ADDITIVE"
                elif arg == "local-as": 
                    comm_val = "NO_EXPORT_SUBCONFED"
                elif arg == "no-advertise":
                    comm_val = "NO_ADVERTISE"
                elif arg == "no-export":
                    comm_val = "NO_EXPORT"  
                elif arg == "no-peer": 
                    comm_val = "NOPEER"
                else:
                    comm_val = arg

                comm_list.insert(i, comm_val)
                i = i + 1

            body = { "openconfig-bgp-policy:set-community": { "config" : { "method":"INLINE", "options": internal_op }, "inline": {"config": {"communities":comm_list}}}}
            return api.patch(keypath, body)
        elif attr == 'bgp_actions_set_ext_community':
            keypath = cc.Path(uri, name=args[0], name1=args[1])
            if "rt" == args[2]:
                body = { "openconfig-bgp-policy:set-ext-community": { "config" : { "method":"INLINE", "options":args[4]}, "inline": {"config": {"communities":["route-target:"+args[3]]}}}}
            else:
                body = { "openconfig-bgp-policy:set-ext-community": { "config" : { "method":"INLINE", "options":args[4]}, "inline": {"config": {"communities":["route-origin:"+args[3]]}}}}
            return api.patch(keypath, body)
    elif op == 'delete':
        uri = restconf_map[attr]
        if attr == 'openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_actions_bgp_actions_config_set_next_hop':
            if args[2] == 'ipv6' and args[3] == 'prefer-global':
                keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/actions/openconfig-bgp-policy:bgp-actions/config/set-ipv6-next-hop-prefer-global', name=args[0], name1=args[1])
            elif args[2] == 'ipv6' and args[3] == 'global':
                keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/actions/openconfig-bgp-policy:bgp-actions/config/set-ipv6-next-hop-global', name=args[0], name1=args[1])
            elif args[2] == 'ipv4':
                keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/actions/openconfig-bgp-policy:bgp-actions/config/set-next-hop', name=args[0], name1=args[1])
            else:
                return api.cli_not_implemented(func)
            return api.delete(keypath)
        elif attr == 'openconfig_routing_policy_routing_policy_policy_definitions_policy_definition':
            keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}',
            name=args[0])
            return api.delete(keypath)
        elif attr == 'openconfig_routing_policy_routing_policy_policy_definitions_policy_definition_statements_statement_actions_metric_action_config_set_metric':
            med_uri = restconf_map['openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_actions_bgp_actions_config_set_med']
            med_keypath = cc.Path(med_uri, name=args[0], name1=args[1])
            api.delete(med_keypath)

        keypath = cc.Path(uri, name=args[0], name1=args[1])
        return api.delete(keypath)

    elif op == 'get':

        if attr == 'openconfig_routing_policy_routing_policy_policy_definitions_policy_definition':
            if len(args) > 1:
                keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}',name=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions')
            return api.get(keypath)

    elif op == 'PyParse':

        if attr == 'no_route_map':
            if args[0] == "action-switch:":
                return invoke_api("delete_openconfig_routing_policy_routing_policy_policy_definitions_policy_definition", args[1:2])
            elif args[0] == "action-switch:permit":
                return invoke_api("delete_openconfig_routing_policy_routing_policy_policy_definitions_policy_definition_statements_statement", args[1:3] + [ "ACCEPT_ROUTE" ])
            else:
                return invoke_api("delete_openconfig_routing_policy_routing_policy_policy_definitions_policy_definition_statements_statement", args[1:3] + [ "REJECT_ROUTE" ])

        elif attr == 'no_set_extcommunity':
            if len(args) == 2:
                return invoke_api("delete_bgp_actions_set_ext_community", args[0:2])
            else:
                return invoke_api("patch_bgp_actions_set_ext_community", args[0:5] + [ "REMOVE" ])

        elif attr == 'set_community':
            return invoke_api("patch_bgp_actions_set_community", args)

        elif attr == 'no_set_community':
            if len(args) == 2:
                return invoke_api("delete_bgp_actions_set_community", args)
            else:
                return invoke_api("patchRemove_bgp_actions_set_community", args)

    return api.cli_not_implemented(func)

def run(func, args):
    response = invoke_api(func, args)

    if response.ok():
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print ("%Error: Internal error.")
                return 1
            show_cli_output(args[0], api_response)
    else:
        print response.error_message()
        return 1

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])

