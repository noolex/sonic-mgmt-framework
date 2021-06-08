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

def invoke_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None

    if func == 'patch_openconfig_routing_policy_routing_policy_policy_definitions_policy_definition_statements_statement_actions_config_policy_result':
        keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/actions/config/policy-result',
                name=args[0], name1= args[1])
        body = {"openconfig-routing-policy:policy-result": 'ACCEPT_ROUTE' if args[2] == 'permit' else 'REJECT_ROUTE'}
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_routing_policy_routing_policy_policy_definitions_policy_definition_statements_statement_actions':
        keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/actions',
                name=args[0], name1= args[1])
        return api.delete(keypath)

    elif func == 'patch_openconfig_routing_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_match_prefix_set_config_prefix_set':
        keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/match-prefix-set/config/prefix-set',
                name=args[0], name1= args[1])
        body = {"openconfig-routing-policy:prefix-set":args[2]}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_routing_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_match_prefix_set_config_ipv6_prefix_set':
        keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/match-prefix-set/config/openconfig-routing-policy-ext:ipv6-prefix-set',
                name=args[0], name1= args[1])
        body = {"openconfig-routing-policy-ext:ipv6-prefix-set":args[2]}
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_routing_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_match_prefix_set_config_prefix_set':
        keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/match-prefix-set/config/prefix-set',
                name=args[0], name1= args[1])
        return api.delete(keypath)
    elif func == 'delete_openconfig_routing_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_match_prefix_set_config_ipv6_prefix_set':
        keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/match-prefix-set/config/openconfig-routing-policy-ext:ipv6-prefix-set',
                name=args[0], name1= args[1])
        return api.delete(keypath)
    elif func == 'patch_openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_bgp_conditions_match_as_path_set_config_as_path_set':
        keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/match-as-path-set/config/as-path-set', name=args[0], name1= args[1])
        body = {"openconfig-bgp-policy:as-path-set":args[2]}
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_bgp_conditions_match_as_path_set_config_as_path_set':
        keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/match-as-path-set/config/as-path-set', name=args[0], name1= args[1])
        return api.delete(keypath)

    elif func == 'patch_openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_bgp_conditions_match_evpn':
        index = 0
        for arg in args[index:]:
            if (arg == "match_evpn_cmd_type" and args[index + 1] == "default-route"):
                keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/match-evpn-set/config/default-type5-route', name=args[0], name1= args[1])
                body = {"openconfig-bgp-policy:default-type5-route": True}
                break
            if (arg == "match_evpn_cmd_type" and args[index + 1] == "route-type"):
                keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/match-evpn-set/config/route-type', name=args[0], name1= args[1])
                body = {"openconfig-bgp-policy:route-type": args[index + 3].upper() }
                break
            if (arg == "match_evpn_cmd_type" and args[index + 1] == "vni"):
                keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/match-evpn-set/config/vni-number', name=args[0], name1= args[1])
                body = {"openconfig-bgp-policy:vni-number": int(args[index + 4])}
                break
            index = index + 1
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_bgp_conditions_match_evpn':
        index = 0
        for arg in args[index:]:
            if (arg == "match_evpn_cmd_type" and args[index + 1] == "default-route"):
                keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/match-evpn-set/config/default-type5-route', name=args[0], name1= args[1])
                break
            if (arg == "match_evpn_cmd_type" and args[index + 1] == "route-type"):
                keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/match-evpn-set/config/route-type', name=args[0], name1= args[1])
                break
            if (arg == "match_evpn_cmd_type" and args[index + 1] == "vni"):
                keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/match-evpn-set/config/vni-number', name=args[0], name1= args[1])
                break
            index = index + 1
        return api.delete(keypath)

    elif func == 'patch_openconfig_routing_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_match_interface_config_interface':
        keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/match-interface/config/interface',name=args[0], name1= args[1])
        body = {"openconfig-routing-policy:interface":args[3] if args[2] == 'phy-if-name' or args[2] == 'PortChannel' else args[2] + args[3]}
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_routing_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_match_interface_config_interface':
        keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/match-interface/config/interface',name=args[0], name1= args[1])
        return api.delete(keypath)

    elif func == 'patch_openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_bgp_conditions_config_community_set':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/config/community-set',
             name=args[0], name1= args[1])
        body = {"openconfig-bgp-policy:community-set":args[2]}
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_bgp_conditions_config_community_set':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/config/community-set',
             name=args[0], name1= args[1])
        return api.delete(keypath)

    elif func == 'patch_openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_bgp_conditions_config_ext_community_set':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/config/ext-community-set',
             name=args[0], name1= args[1])
        body = {"openconfig-bgp-policy:ext-community-set":args[2]}
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_bgp_conditions_config_ext_community_set':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/config/ext-community-set',
             name=args[0], name1= args[1])
        return api.delete(keypath)

    elif func == 'patch_openconfig_routing_policy_ext_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_match_tag_set_config_tag_value':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/match-tag-set/config/openconfig-routing-policy-ext:tag-value',
             name=args[0], name1= args[1])
        api.delete(keypath)
        body = {"openconfig-routing-policy:tag-value":[int(args[2])]}
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_routing_policy_ext_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_match_tag_set_config_tag_value':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/match-tag-set/config/openconfig-routing-policy-ext:tag-value',
             name=args[0], name1= args[1])
        return api.delete(keypath)

    elif func == 'patch_openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_bgp_conditions_config_origin_eq':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/config/origin-eq',
             name=args[0], name1= args[1])
        body = {"openconfig-bgp-policy:origin-eq":args[2].upper()}
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_bgp_conditions_config_origin_eq':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/config/origin-eq',
             name=args[0], name1= args[1])
        return api.delete(keypath)

    elif func == 'patch_openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_bgp_conditions_config_med_eq':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/config/med-eq',
             name=args[0], name1= args[1])
        body = {"openconfig-bgp-policy:med-eq":int(args[2])}
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_bgp_conditions_config_med_eq':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/config/med-eq',
             name=args[0], name1= args[1])
        return api.delete(keypath)

    elif func == 'patch_openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_bgp_conditions_config_local_pref_eq':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/config/local-pref-eq',
             name=args[0], name1= args[1])
        body = {"openconfig-bgp-policy:local-pref-eq":int(args[2])}
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_bgp_conditions_config_local_pref_eq':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/config/local-pref-eq',
             name=args[0], name1= args[1])
        return api.delete(keypath)

    elif func == 'patch_openconfig_routing_policy_ext_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_match_neighbor_set_config_address':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/match-neighbor-set/config/openconfig-routing-policy-ext:address',
             name=args[0], name1= args[1])
        api.delete(keypath)
        body = {"openconfig-routing-policy-ext:address":[ args[3] if args[2] == 'match-peer' or args[2] == 'phy-if-name' or args[2] == 'PortChannel' else args[2] + args[3] ]}
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_routing_policy_ext_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_match_neighbor_set_config_address':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/match-neighbor-set/config/openconfig-routing-policy-ext:address',
             name=args[0], name1= args[1])
        return api.delete(keypath)

    elif func == 'patch_openconfig_bgp_policy_ext_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_bgp_conditions_config_next_hop_set':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/config/openconfig-bgp-policy-ext:next-hop-set',
             name=args[0], name1= args[1])
        body = {"openconfig-bgp-policy-ext:next-hop-set":args[2]}
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_bgp_policy_ext_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_bgp_conditions_config_next_hop_set':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-bgp-policy:bgp-conditions/config/openconfig-bgp-policy-ext:next-hop-set',
             name=args[0], name1= args[1])
        return api.delete(keypath)

    elif func == 'patch_openconfig_routing_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_config_call_policy':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/config/call-policy',
             name=args[0], name1= args[1])
        body = {"openconfig-routing-policy:call-policy":args[2]}
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_routing_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_config_call_policy':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/config/call-policy',
             name=args[0], name1= args[1])
        return api.delete(keypath)

    elif func == 'patch_openconfig_routing_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_config_install_protocol_eq':
        proto_number = {"bgp":"BGP","ospf":"OSPF","ospf3":"OSPF3","static":"STATIC","connected":"DIRECTLY_CONNECTED"}
        if args[2] not in proto_number.keys():
            print("%Error: Invalid protocol number in route-match config")
            exit(1)
        else:
            protocol = proto_number.get(args[2])
            keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/config/install-protocol-eq',
            name=args[0], name1= args[1])
            body = {"openconfig-routing-policy:install-protocol-eq":protocol}
            return api.patch(keypath, body)
    elif func == 'delete_openconfig_routing_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_config_install_protocol_eq':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/config/install-protocol-eq',
             name=args[0], name1= args[1])

        return api.delete(keypath)

    elif func == 'patch_openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_match_src_network_instance_config_name':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-routing-policy-ext:match-src-network-instance/config/name',
            name=args[0], name1= args[1])
        body = {"openconfig-routing-policy-ext:name": args[2]}
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_bgp_policy_routing_policy_policy_definitions_policy_definition_statements_statement_conditions_match_src_network_instance_config_name':
        keypath  = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition={name}/statements/statement={name1}/conditions/openconfig-routing-policy-ext:match-src-network-instance/config/name',
             name=args[0], name1= args[1])
        return api.delete(keypath)

    else:
        body = {}

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
    else:
        print response.error_message()
        return 1

if __name__ == '__main__':

    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])

