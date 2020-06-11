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

    op, attr = func.split('_', 1)
    if op == 'patch':
        uri = restconf_map[attr]
        if attr == 'openconfig_routing_policy_routing_policy_policy_definitions_policy_definition_statements_statement_actions_config_policy_result':
            keypath = cc.Path(uri, name=args[0], name1=args[1])
            body = { "openconfig-routing-policy:policy-result": "ACCEPT_ROUTE" if args[2] == 'permit' else "REJECT_ROUTE" }
            return api.patch(keypath, body)
        elif attr == 'openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_actions_bgp_actions_config_set_next_hop':
            if args[2] == 'ipv6' and args[3] == 'prefer-global':
                keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/actions/openconfig-bgp-policy:bgp-actions/config/openconfig-bgp-policy-ext:set-ipv6-next-hop-prefer-global', name=args[0], name1=args[1])
                body = { "openconfig-bgp-policy-ext:set-ipv6-next-hop-prefer-global" : True }
            elif args[2] == 'ipv6' and args[3] == 'global':
                keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/actions/openconfig-bgp-policy:bgp-actions/config/openconfig-bgp-policy-ext:set-ipv6-next-hop-global', name=args[0], name1=args[1])
                body = { "openconfig-bgp-policy-ext:set-ipv6-next-hop-global" : args[4] }
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
            body = { "openconfig-bgp-policy:set-community": { "config" : { "method":"INLINE", "options": "ADD" if 'additive' in args[4:] else args[3]}, "inline": {"config": {"communities":[args[2]]}}}}
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
                keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/actions/openconfig-bgp-policy:bgp-actions/config/openconfig-bgp-policy-ext:set-ipv6-next-hop-prefer-global', name=args[0], name1=args[1])
            elif args[2] == 'ipv6' and args[3] == 'global':
                keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/actions/openconfig-bgp-policy:bgp-actions/config/openconfig-bgp-policy-ext:set-ipv6-next-hop-global', name=args[0], name1=args[1])
            elif args[2] == 'ipv4':
                keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/actions/openconfig-bgp-policy:bgp-actions/config/set-next-hop', name=args[0], name1=args[1])
            else:
                return api.cli_not_implemented(func)
            return api.delete(keypath)
        elif attr == 'openconfig_routing_policy_routing_policy_policy_definitions_policy_definition':
            keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}',
            name=args[0])
            return api.delete(keypath)
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
            replace_add = [ 'REPLACE', 'additive' ] if args[-1] == 'additive' else [ 'REPLACE' ]
            if args[2] == "comm-num":
                return invoke_api("patch_bgp_actions_set_community", args[0:2] + args[3:4] + replace_add)
            elif args[2] == "local-AS":
                return invoke_api("patch_bgp_actions_set_community", args[0:2] + [ "NO_EXPORT_SUBCONFED" ] + replace_add)
            elif args[2] == "no-advertise":
                return invoke_api("patch_bgp_actions_set_community", args[0:2] + [ "NO_ADVERTISE" ] + replace_add)
            elif args[2] == "no-export":
                return invoke_api("patch_bgp_actions_set_community", args[0:2] + [ "NO_EXPORT" ] + replace_add)
            elif args[2] == "no-peer":
                return invoke_api("patch_bgp_actions_set_community", args[0:2] + [ "NOPEER" ] + replace_add)

        elif attr == 'no_set_community':
            if args[2] == "comm-opt:":
                return invoke_api("delete_bgp_actions_set_community", args[0:2])
            elif args[2] == "comm-opt:comm-num":
                return invoke_api("patch_bgp_actions_set_community", args[0:2] + [ args[3], "REMOVE" ])
            elif args[2] == "comm-opt:local-AS":
                return invoke_api("patch_bgp_actions_set_community", args[0:2] + [ "NO_EXPORT_SUBCONFED", "REMOVE" ])
            elif args[2] == "comm-opt:no-advertise":
                return invoke_api("patch_bgp_actions_set_community", args[0:2] + [ "NO_ADVERTISE", "REMOVE" ])
            elif args[2] == "comm-opt:no-export":
                return invoke_api("patch_bgp_actions_set_community", args[0:2] + [ "NO_EXPORT", "REMOVE" ])
            elif args[2] == "comm-opt:no-peer":
                return invoke_api("patch_bgp_actions_set_community", args[0:2] + [ "NOPEER", "REMOVE" ])

    return api.cli_not_implemented(func)

def run(func, args):
    response = invoke_api(func, args)

    if response.ok():
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print ("%Error: Internal error.")
                sys.exit(1)
            show_cli_output(args[0], api_response)
    else:
        print response.error_message()
        sys.exit(1)

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])

