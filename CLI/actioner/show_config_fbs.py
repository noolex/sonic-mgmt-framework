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
                if 'DESCRIPTION' in class_data.keys() and class_data['DESCRIPTION'] != "":
                    if ' ' in class_data['DESCRIPTION']:
                        cmd_str += ' description "{}";'.format(class_data['DESCRIPTION'])
                    else:
                        cmd_str += ' description {};'.format(class_data['DESCRIPTION'])
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
                render_data[name]["TYPE"] = policy_data["TYPE"].lower().replace("_", "-")
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
                match_type = render_data[policy_name]['TYPE'].lower().replace("_", "-")
                cmd_str += 'policy-map {} type {};'.format(policy_name, match_type)
                if 'DESCRIPTION' in render_data[policy_name] and render_data[policy_name]['DESCRIPTION'] != "":
                    if ' ' in render_data[policy_name]['DESCRIPTION']:
                        cmd_str += ' description "{}";'.format(render_data[policy_name]['DESCRIPTION'])
                    else:
                        cmd_str += ' description {};'.format(render_data[policy_name]['DESCRIPTION'])
                for flow in render_data[policy_name]['FLOWS']:
                    flow_data = render_data[policy_name]['FLOWS'][flow]
                    priority = ""
                    if 'PRIORITY' in flow_data:
                        priority = "priority " + str(flow_data['PRIORITY']) 
                    cmd_str += ' class {} {};'.format(flow_data['CLASS_NAME'], priority)
                    if 'DESCRIPTION' in flow_data and flow_data['DESCRIPTION'] != "":
                        if " " in flow_data['DESCRIPTION']:
                            cmd_str += ' description "{}";'.format(flow_data['DESCRIPTION'])
                        else:
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
                        all_egress = list()
                        for nhop in flow_data.get("SET_IP_NEXTHOP", list()):
                            vrf_str = ""
                            prio_str = ""
                            prio = 0
                            if "VRF" in nhop:
                                vrf_str = "vrf " + str(nhop["VRF"])
                            if "PRIORITY" in nhop:
                                prio_str = "priority " + str(nhop["PRIORITY"])
                                prio = int(nhop["PRIORITY"])
                            all_egress.append((prio, 'set ip next-hop {} {} {};'.format(nhop["IP_ADDRESS"], vrf_str, prio_str).replace('  ', ' ')))
                        for nhop in flow_data.get('SET_IP_NEXTHOP_GROUP', list()):
                            prio_str = ""
                            prio = 0
                            if 'PRIORITY' in nhop:
                                prio_str = "priority " + str(nhop["PRIORITY"])
                                prio = int(nhop["PRIORITY"])
                            all_egress.append((prio, 'set ip next-hop-group {} {};'.format(nhop["GROUP_NAME"], prio_str).replace('  ', ' ')))
                        for nhop in flow_data.get("SET_IPV6_NEXTHOP", list()):
                            vrf_str = ""
                            prio_str = ""
                            prio = 0
                            if "VRF" in nhop:
                                vrf_str = "vrf " + str(nhop["VRF"])
                            if "PRIORITY" in nhop:
                                prio_str = "priority " + str(nhop["PRIORITY"])
                                prio = int(nhop["PRIORITY"])
                            all_egress.append((prio, 'set ipv6 next-hop {} {} {};'.format(nhop["IP_ADDRESS"], vrf_str, prio_str).replace('  ', ' ')))
                        for nhop in flow_data.get('SET_IPV6_NEXTHOP_GROUP', list()):
                            prio_str = ""
                            prio = 0
                            if 'PRIORITY' in nhop:
                                prio_str = "priority " + str(nhop["PRIORITY"])
                                prio = int(nhop["PRIORITY"])
                            all_egress.append((prio, 'set ipv6 next-hop-group {} {};'.format(nhop["GROUP_NAME"], prio_str).replace('  ', ' ')))
                        for intf in  flow_data.get("SET_INTERFACE", list()):
                            prio_str = ""
                            prio = 0
                            if "PRIORITY" in intf:
                                prio_str = "priority " + str(intf["PRIORITY"])
                                prio = int(intf["PRIORITY"])
                            all_egress.append((prio, 'set interface {} {};'.format(intf["INTERFACE"], prio_str)))

                        all_egress.sort(key=lambda x: 0xffff-x[0])
                        for egr in all_egress:
                            cmd_str += '  {};'.format(egr[1])
                        if 'DEFAULT_PACKET_ACTION' in flow_data:
                            cmd_str += '  set interface null;'
                        cmd_str += ' !;'
                    elif match_type == 'monitoring':
                        if 'SET_MIRROR_SESSION' in flow_data:
                            cmd_str += '  set mirror-session {};'.format(flow_data['SET_MIRROR_SESSION'])
                        cmd_str += ' !;'
                    elif match_type == 'acl-copp':
                        if 'SET_TRAP_QUEUE' in flow_data:
                            cmd_str += '  set trap-queue {};'.format(flow_data['SET_TRAP_QUEUE'])

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

    return 'CB_SUCCESS', cmd_str, True


def __show_runn_fbs_service_policy_for_intf(ifname, cache):
    cmd_str = ''
    policy_types = ['qos', 'monitoring', 'forwarding', 'acl-copp']
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
    elif opstr == "show_running_next_hop_group_by_name":
        show_running_next_hop_group_by_name(args)


def show_running_class_map(args):
    import sonic_cli_show_config 
    sonic_cli_show_config.run("show_view",
                              ["views=configure-${fbs-class-type}-classifier",
                               'view_keys="fbs-class-name={class_name}"'.format(
                                   class_name=args[0] if len(args) == 1 else "")])


def show_running_next_hop_group_by_name(args):
    import sonic_cli_show_config 
    sonic_cli_show_config.run("show_view",
                              ["views=configure-pbf-${fbs-dynamic-nhgrp-type}-nh-grp",
                               'view_keys="fbs-nhgrp-name={grp_name}"'.format(
                                   grp_name=args[0] if len(args) == 1 else "")])


def show_running_config_fbs_start_callback(context, cache):
    fbs_client = cc.ApiClient()
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_BINDING_TABLE/POLICY_BINDING_TABLE_LIST')
    response = fbs_client.get(keypath, depth=None, ignore404=False)
    if response.ok():
        for binding in response.content.get('sonic-flow-based-services:POLICY_BINDING_TABLE_LIST', []):
            cache[binding.pop('INTERFACE_NAME')] = binding


def show_running_next_hop_group(render_tables):
    fbs_client = cc.ApiClient()
    if 'fbs-nhgrp-name' in render_tables:
        path = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/next-hop-groups/next-hop-group={group_name}', 
                group_name=render_tables["fbs-nhgrp-name"])
    else:
        path = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/next-hop-groups/next-hop-group')
    
    response = fbs_client.get(path, ignore404=False)
    if not response.ok():
        if 'fbs-nhgrp-name' in render_tables:
            return 'CB_SUCCESS', "%Error: No pbf next-hop group found", True
        else:
            return 'CB_SUCCESS', '', True

    all_groups = response.content.get("openconfig-fbs-ext:next-hop-group", list())
    data = dict()
    runn_config = ''
    for grp_data in all_groups:
        item = dict()
        group_name = grp_data["group-name"]
        grp_type = (grp_data["state"].get("group-type", "")).replace("openconfig-fbs-ext:NEXT_HOP_GROUP_TYPE_",
                                                                     "").replace("V4", "").lower()
        data[(grp_type, group_name)] = item

        if 'description' in grp_data["config"]:
            item["DESCRIPTION"] = grp_data["config"]['description']
            if ' ' in item["DESCRIPTION"]:
                item["DESCRIPTION"] = '"{}"'.format(item["DESCRIPTION"])
        thr_cli = ''
        if 'threshold-type' in grp_data["config"]:
            thr_cli += 'threshold type {}'.format(grp_data["config"]['threshold-type'].replace("openconfig-fbs-ext:NEXT_HOP_GROUP_THRESHOLD_", "").lower())
            if 'threshold-up' in grp_data["config"]:
                thr_cli += ' up {}'.format(grp_data["config"]['threshold-up'])
            if 'threshold-down' in grp_data["config"]:
                thr_cli += ' down {}'.format(grp_data["config"]['threshold-down'])
            item['THRESHOLD'] = thr_cli

        nhops = list()
        for nh in grp_data.get("next-hops", dict()).get("next-hop", list()):
            eid = int(nh["entry-id"])
            cli_str = "entry {} next-hop {}".format(eid, nh["state"]["ip-address"])
            if "network-instance" in nh["state"]:
                cli_str = "{} vrf {}".format(cli_str, nh["state"]["network-instance"])
            if "next-hop-type" in nh["state"]:
                cli_str = "{} {}".format(cli_str, nh["state"]["next-hop-type"].split(":")[-1].
                                         replace('NEXT_HOP_TYPE_', '').lower().replace('_', '-'))
            nhops.append((eid, cli_str))
            nhops.sort(key=lambda x: x[0])
            item['NEXT_HOPS'] = nhops

    for grp_name in natsorted(data.keys()):
        grp_data = data[grp_name]
        runn_config += 'pbf next-hop-group {} type {};'.format(grp_name[1], grp_name[0])
        if 'DESCRIPTION' in grp_data:
            runn_config += '  description {};'.format(grp_data['DESCRIPTION'])
        if 'THRESHOLD' in grp_data:
            runn_config += '  {};'.format(grp_data['THRESHOLD'])
        for nh in grp_data.get('NEXT_HOPS', list()):
            runn_config += '  {};'.format(nh[1])
        runn_config += '!;'

    return 'CB_SUCCESS', runn_config, True

