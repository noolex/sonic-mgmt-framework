#!/usr/bin/python
###########################################################################
#
# Copyright 2019 Broadcom.  The term "Broadcom" refers to Broadcom Inc. and/or
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

import cli_client as cc
from collections import OrderedDict
from natsort import natsorted
import sonic_cli_acl
from sonic_cli_fbs import ethertype_to_user_fmt


def show_running_fbs_classifier(render_tables):
    fbs_client = cc.ApiClient()
    if 'fbs-class-name' in render_tables:
        body = {"sonic-flow-based-services:input": {"CLASSIFIER_NAME": render_tables['fbs-class-name']}}
    else:
        body = {"sonic-flow-based-services:input": {}}
    keypath = cc.Path('/restconf/operations/sonic-flow-based-services:get-classifier')
    response = fbs_client.post(keypath, body)
    cmd_str = ''
    if response.ok():
        if response.content is not None and bool(response.content):
            output = response.content["sonic-flow-based-services:output"]["CLASSIFIERS"]
            render_data = OrderedDict()
            output_dict = dict()
            for entry in output:
                output_dict[entry["CLASSIFIER_NAME"]] = entry
            sorted_keys = natsorted(output_dict.keys())
            for key in sorted_keys:
                render_data[key] = output_dict[key]

            index = 0
            for class_name in render_data:
                cmd_str += '' if index == 0 else "!;" 
                index += 1
                class_data = render_data[class_name]
                match_type = class_data['MATCH_TYPE'].lower()
                fields_str = ""
                if match_type == 'fields':
                    fields_str = 'match-all'
                cmd_str += 'class-map {} match-type {} {};'.format(class_name, match_type, fields_str)
                if match_type == 'copp':
                    if 'TRAP_IDS' in class_data.keys():
                        trap_id_list = class_data['TRAP_IDS'].split(',')
                        for trap_id in trap_id_list:
                            cmd_str += ' match protocol {};'.format(trap_id)
                elif match_type.lower() == 'acl':
                    if 'ACL_TYPE' in class_data:
                        acl_type = class_data["ACL_TYPE"]
                        if acl_type == "L2":
                            acl_type_str = "mac"
                        elif acl_type == "L3":
                            acl_type_str = "ip"
                        elif acl_type == "L3V6":
                            acl_type_str = "ipv6"
                        else:
                            acl_type_str = 'unknown'
                        if 'ACL_NAME' in class_data:
                            cmd_str += ' match access-group {} {};'.format(acl_type_str, class_data["ACL_NAME"])
                elif match_type.lower() == 'fields':
                    if 'ETHER_TYPE' in class_data:
                        val = ethertype_to_user_fmt(class_data["ETHER_TYPE"])
                        cmd_str += ' match ethertype {};'.format(val)
                    if 'SRC_MAC' in class_data:
                        val = sonic_cli_acl.mac_addr_to_user_fmt(class_data["SRC_MAC"])
                        cmd_str += ' match source-adress mac {};'.format(val)
                    if 'DST_MAC' in class_data:
                        val = sonic_cli_acl.mac_addr_to_user_fmt(class_data["DST_MAC"])
                        cmd_str += ' match destination-adress mac {};'.format(val)
                    if 'VLAN' in class_data:
                        cmd_str += ' match vlan {};'.format(class_data["VLAN"])
                    if 'PCP' in class_data:
                        cmd_str += ' match pcp {};'.format(sonic_cli_acl.pcp_to_user_fmt(class_data["PCP"]))
                    if 'DSCP' in class_data:
                        cmd_str += ' match dscp {};'.format(sonic_cli_acl.dscp_to_user_fmt(class_data["DSCP"]))
                    if 'DEI' in class_data:
                        cmd_str += ' match dei {};'.format(class_data["DEI"]) 
                    if 'IP_PROTOCOL' in class_data:
                        val = sonic_cli_acl.ip_protocol_to_user_fmt(class_data["IP_PROTOCOL"])
                        cmd_str += ' match ip protocol {};'.format(val)
                    if 'SRC_IP' in class_data:
                        val = sonic_cli_acl.convert_ip_addr_to_user_fmt(class_data["SRC_IP"])
                        cmd_str += ' match source-address ip {};'.format(val)
                    if 'SRC_IPV6' in class_data:
                        val = sonic_cli_acl.convert_ip_addr_to_user_fmt(class_data["SRC_IPV6"])
                        cmd_str += ' match source-address ipv6 {};'.format(val)
                    if 'DST_IP' in class_data:
                        val = sonic_cli_acl.convert_ip_addr_to_user_fmt(class_data["DST_IP"])
                        cmd_str += ' match destination-address ip {};'.format(val)
                    if 'DST_IPV6' in class_data:
                        val = sonic_cli_acl.convert_ip_addr_to_user_fmt(class_data["DST_IPV6"])
                        cmd_str += ' match destination-address ipv6 {};'.format(val)
                    if 'L4_SRC_PORT' in class_data:
                        cmd_str += ' match source-port eq {};'.format(class_data["L4_SRC_PORT"])
                    if 'L4_SRC_PORT_RANGE' in class_data:
                        val = class_data["L4_SRC_PORT_RANGE"]
                        cmd_str += ' match source-port range {};'.format(class_data["L4_SRC_PORT_RANGE"])
                    if 'L4_DST_PORT' in class_data:
                        val = class_data["L4_DST_PORT"]
                        cmd_str += ' match destination-port eq {};'.format(class_data["L4_DST_PORT"])
                    if 'L4_DST_PORT_RANGE' in class_data:
                        val = class_data["L4_DST_PORT"]
                        cmd_str += ' match destination-port range {};'.format(class_data["L4_DST_PORT_RANGE"])
                    if 'TCP_FLAGS' in class_data:
                        val = sonic_cli_acl.tcp_flags_to_user_fmt(class_data["TCP_FLAGS"])
                        cmd_str += ' match tcp-flags {};'.format(val)

    return 'CB_SUCCESS', cmd_str, True


def show_running_fbs_policy(render_tables):
    fbs_client = cc.ApiClient()
    if 'fbs-policy-name' in render_tables:
        body = {"sonic-flow-based-services:input": {"POLICY_NAME":render_tables['fbs-policy-name']}}
    else:
        body = {"sonic-flow-based-services:input": {}}
    keypath = cc.Path('/restconf/operations/sonic-flow-based-services:get-policy')
    response = fbs_client.post(keypath, body)
    cmd_str = ''
    if response.ok():
        if response.content is not None and bool(response.content):
            render_data = OrderedDict()

            output = response.content["sonic-flow-based-services:output"]["POLICIES"]
            policy_names = []
            data = dict()
            for entry in output:
                policy_names.append(entry["POLICY_NAME"])
                data[entry["POLICY_NAME"]] = entry

            policy_names = natsorted(policy_names)
            for name in policy_names:
                render_data[name] = OrderedDict()
                policy_data = data[name]
                render_data[name]["TYPE"] = policy_data["TYPE"].lower()
                render_data[name]["DESCRIPTION"] = policy_data.get("DESCRIPTION", "")

                render_data[name]["FLOWS"] = OrderedDict()
                flows = dict()
                for flow in policy_data.get("FLOWS", list()):
                    flows[(flow["PRIORITY"], flow["CLASS_NAME"])] = flow

                flow_keys = natsorted(flows.keys(), reverse=True)
                for flow in flow_keys:
                    render_data[name]["FLOWS"][flow] = flows[flow]

                render_data[name]["APPLIED_INTERFACES"] = policy_data.get("APPLIED_INTERFACES", [])
            index = 0
            for policy_name in render_data:
                cmd_str += '' if index == 0 else "!;" 
                index += 1
                match_type = render_data[policy_name]['TYPE'].lower()
                cmd_str += 'policy-map {} type {};'.format(policy_name, match_type)
                if 'DESCRIPTION' in render_data and render_data['DESCRIPTION'] != "":
                    cmd_str += ' description {};'.format(render_data['DESCRIPTION'])
                for flow in render_data[policy_name]['FLOWS']:
                    flow_data = render_data[policy_name]['FLOWS'][flow]
                    priority = ""
                    if 'PRIORITY' in flow_data:
                        priority = "priority " + str(flow_data['PRIORITY']) 
                    cmd_str += ' class {} {};'.format(flow_data['CLASS_NAME'], priority)
                    if 'DESCRIPTION' in flow_data and flow_data['DESCRIPTION'] != "":
                        cmd_str += ' description {};'.format(flow_data['DESCRIPTION'])
                    if match_type == 'copp':
                        if 'TRAP_GROUP' in flow_data:
                            if flow_data['TRAP_GROUP'] != 'null':
                                cmd_str += '  set copp-action {};'.format(flow_data['TRAP_GROUP'])
                                cmd_str += ' !;'
                    elif match_type == 'qos':
                        if 'SET_PCP' in flow_data:
                            cmd_str += '  set pcp {};'.format(flow_data['SET_PCP'])
                        if 'SET_DSCP' in flow_data:
                            cmd_str += '  set dscp {};'.format(flow_data['SET_DSCP'])
                        if 'SET_TC' in flow_data:
                            cmd_str += '  set traffic-class {};'.format(flow_data['SET_TC'])

                        pstr = ""
                        if 'SET_POLICER_CIR' in flow_data:
                            pstr += 'cir {} '.format(flow_data['SET_POLICER_CIR'])
                        if 'SET_POLICER_CBS' in flow_data:
                            pstr += 'cbs {} '.format(flow_data['SET_POLICER_CBS'])
                        if 'SET_POLICER_PIR' in flow_data:
                            pstr += 'pir {} '.format(flow_data['SET_POLICER_PIR'])
                        if 'SET_POLICER_PBS' in flow_data:
                            pstr += 'pbs {} '.format(flow_data['SET_POLICER_PBS'])
                        if pstr != "":
                            cmd_str += '  police {};'.format(pstr)
                        cmd_str += ' !;'
                    elif match_type == 'forwarding':
                        if 'DEFAULT_PACKET_ACTION' in flow_data:
                            cmd_str += ' set interface null;'
                        if 'SET_INTERFACE' in flow_data:
                            for intf in  flow_data["SET_INTERFACE"]:
                                prio_str = ""
                                if "PRIORITY" in intf:
                                    prio_str = "priority " + str(intf["PRIORITY"])
                                cmd_str += '  set interface {} {};'.format(intf["INTERFACE"], prio_str)
                        if 'SET_IP_NEXTHOP' in flow_data:
                            for nhop in flow_data["SET_IP_NEXTHOP"]:
                                vrf_str = "" 
                                prio_str = ""
                                if "VRF" in nhop:
                                    vrf_str = "vrf " + str(nhop["VRF"])
                                if "PRIORITY" in nhop:
                                    prio_str = "priority " + str(nhop["PRIORITY"])
                                cmd_str += '  set ip next-hop {} {} {};'.format(nhop["IP_ADDRESS"], vrf_str, prio_str)
                        if 'SET_IPV6_NEXTHOP' in flow_data:
                            for nhop in flow_data["SET_IPV6_NEXTHOP"]:
                                vrf_str = "" 
                                prio_str = ""
                                if "VRF" in nhop:
                                    vrf_str = "vrf " + str(nhop["VRF"])
                                if "PRIORITY" in nhop:
                                    prio_str = "priority " + str(nhop["PRIORITY"])
                                cmd_str += '  set ipv6 next-hop {} {} {};'.format(nhop["IP_ADDRESS"], vrf_str,
                                                                                   prio_str)
                        cmd_str += ' !;'
                    elif match_type == 'monitoring':
                        if 'SET_MIRROR_SESSION' in flow_data:
                            cmd_str += '  set mirror-session {};'.format(flow_data['SET_MIRROR_SESSION'])
                        cmd_str += ' !;'

    return 'CB_SUCCESS', cmd_str, True


def __show_runn_fbs_service_policy_for_intf(ifname, cache):
    cmd_str = ''
    policy_types = ['qos', 'monitoring', 'forwarding']
    directions = ['ingress', 'egress']
    cfg_pdir_map = {directions[0]: "in", directions[1]: "out"}
    if ifname in cache:
        ifdata = cache[ifname]
        for pdir in directions:
            for policy_type in policy_types:
                key = '{}_{}_POLICY'.format(pdir.upper(), policy_type.upper())
                if key in ifdata:
                    cmd_str += 'service-policy type {} {} {};'.format(policy_type, cfg_pdir_map[pdir], ifdata[key])

    return 'CB_SUCCESS', cmd_str, True


def show_running_fbs_service_policy_global(render_tables):
    return __show_runn_fbs_service_policy_for_intf('Switch', render_tables[__name__])


def show_running_fbs_service_policy_ctrlplane(render_tables):
    return __show_runn_fbs_service_policy_for_intf('CtrlPlane', render_tables[__name__])


def show_running_fbs_service_policy_interface(render_tables):
    return __show_runn_fbs_service_policy_for_intf(render_tables['name'], render_tables[__name__])


def run(opstr, args):
    if opstr == "show_running_class_map":
        show_running_class_map(args)


def show_running_class_map(class_name):
    import sonic_cli_show_config 
    sonic_cli_show_config.run("show_view",
                              ["views=configure-${fbs-class-type}-classifier",
                               'view_keys="fbs-class-name={class_name}"'.format(
                                   class_name=class_name[0] if len(class_name) == 1 else "")])


def show_running_config_fbs_start_callback(context, cache):
    fbs_client = cc.ApiClient()
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_BINDING_TABLE/POLICY_BINDING_TABLE_LIST')
    response = fbs_client.get(keypath, depth=None, ignore404=False)
    if response.ok():
        for binding in response.content.get('sonic-flow-based-services:POLICY_BINDING_TABLE_LIST', []):
            cache[binding.pop('INTERFACE_NAME')] = binding
