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
import sys
from collections import OrderedDict
import cli_client as cc
from scripts.render_cli import show_cli_output
import traceback
import cli_log as log
from sonic_cli_acl import pcp_map, proto_number_map, dscp_map, ethertype_map, acl_natsort_intf_prio
from natsort import natsorted
import sonic_cli_acl
import ipaddress

fbs_client = cc.ApiClient()
TCP_FLAG_VALUES = {"fin": 1, "syn": 2, "rst": 4, "psh": 8, "ack": 16, "urg": 32, "ece": 64, "cwr": 128}


class FbsAclCLIError(RuntimeError):
    """Indicates CLI processing errors that needs to be displayed to user"""
    pass 


def create_policy_copp(args):
    if args[0] != "copp-system-policy":
        raise Exception("copp type classes must have the name 'copp-system-policy'")
    return


def create_policy(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy')
    body = {
    "openconfig-fbs-ext:policy": [{
        "policy-name": args[0],
            "config": {
                "name": args[0],
                "type": "POLICY_" + args[1].upper()
            }
        }]
    }

    return fbs_client.patch(keypath, body)


def delete_policy(args):
    if args[0] == "copp-system-policy":
        print("%Error: copp-system-policy cannot be deleted")
        return
    else:
        keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}', policy_name=args[0])
        return fbs_client.delete(keypath)


def set_policy_description(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/config/description', policy_name=args[0])
    if len(args) > 2:
        body = {"openconfig-fbs-ext:description": '"{}"'.format(" ".join(args[1:]))}
    else:
        body = {"openconfig-fbs-ext:description": args[1]}
    return fbs_client.patch(keypath, body)


def clear_policy_description(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/config/description', policy_name=args[0])
    return fbs_client.delete(keypath)


def create_classifier_copp(args):
    pass


def create_classifier(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier')
    body = {
        "openconfig-fbs-ext:classifier": [{
            "class-name": args[0],
                "config": {
                "name": args[0],
                "match-type": "MATCH_" + args[1].upper()
            }
        }]
    }
    return fbs_client.patch(keypath, body)


def delete_classifier(args):
    # try to delete fbs entry first by checking if fbs object exists, else delete copp entry
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={classifier_name}', classifier_name=args[0])
    response = fbs_client.get(keypath, depth=None, ignore404=False)
    if response.ok():
        keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={classifier_name}', classifier_name=args[0])
        return fbs_client.delete(keypath)
    else:
        keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-traps/copp-trap={copp_name}', copp_name=args[0])
        return fbs_client.delete(keypath)


def set_classifier_description(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/config/description', class_name=args[0])
    if len(args) > 2:
        body = {"openconfig-fbs-ext:description": '"{}"'.format(" ".join(args[1:]))}
    else:
        body = {"openconfig-fbs-ext:description": args[1]}

    return fbs_client.patch(keypath, body)


def clear_classifier_description(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/config/description', class_name=args[0])
    return fbs_client.delete(keypath)


def set_classifier_match_acl(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-acl/config', class_name=args[0])
    if 'mac' == args[1]:
        acl_type = 'ACL_L2'
    elif 'ip' == args[1]:
        acl_type = 'ACL_IPV4'
    elif 'ipv6' == args[1]:
        acl_type = 'ACL_IPV6'
    else:
        print('%Error: Unknown ACL Type')
        return

    body = {
        "openconfig-fbs-ext:config": {
            "acl-name": args[2],
            "acl-type": acl_type
        }
    }

    return fbs_client.patch(keypath, body)


def clear_classifier_match_acl(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-acl', class_name=args[0])
    return fbs_client.delete(keypath)


def __format_mac_addr(macaddr):
    return "{}{}:{}{}:{}{}:{}{}:{}{}:{}{}".format(*macaddr.translate(None, ".:-"))


def __validate_ip_address(addr, af):
    try:
        if 'ip' == af:
            ipaddress.IPv4Network(addr.decode('utf-8'))
        else:
            ipaddress.IPv6Network(addr.decode('utf-8'))
    except ipaddress.AddressValueError as e:
        log.log_error(str(e))
        raise FbsAclCLIError("Invalid {} prefix {}".format("IPv4" if 'ip' == af else 'IPv6', addr))
    except ipaddress.NetmaskValueError as e:
        log.log_error(str(e))
        raise FbsAclCLIError("Invalid mask for {} address {}".format("IPv4" if 'ip' == af else 'IPv6', addr))
    except ValueError as e:
        log.log_error(str(e))
        raise FbsAclCLIError("{}. Please fix the {} address or prefix length".format(str(e), "IPv4" if 'ip' == af else 'IPv6'))


def __set_match_address(addr_type, args):
    if 'mac' == args[1]:
        keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/l2/config', class_name=args[0])
        body = {
            "openconfig-fbs-ext:config": {
            }
        }
        if args[2] == 'host':
            body["openconfig-fbs-ext:config"]["{}-mac".format(addr_type)] = __format_mac_addr(args[3])
        else:
            body["openconfig-fbs-ext:config"]["{}-mac".format(addr_type)] = __format_mac_addr(args[2])
            body["openconfig-fbs-ext:config"]["{}-mac-mask".format(addr_type)] = __format_mac_addr(args[3])
    else: 
        __validate_ip_address(args[2] if args[2] != 'host' else args[3], args[1])

        if 'ip' == args[1]:
            keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/ipv4/config/{addr_type}-address',
                              class_name=args[0], addr_type=addr_type)
            body = {"openconfig-fbs-ext:{}-address".format(addr_type): args[2] if args[2] != 'host' else args[3] + '/32'}
        elif 'ipv6' == args[1]:
            keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/ipv6/config/{addr_type}-address',
                              class_name=args[0], addr_type=addr_type)
            body = {"openconfig-fbs-ext:{}-address".format(addr_type): args[2] if args[2] != 'host' else args[3] + '/128'}

    return fbs_client.patch(keypath, body)


def set_match_source_address(args):
    return __set_match_address('source', args)


def clear_match_source_address(args):
    if 'mac' == args[1]:
        keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/l2/config/source-mac', class_name=args[0])
    elif 'ip' == args[1]:
        keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/ipv4/config/source-address', class_name=args[0])
    elif 'ipv6' == args[1]:
        keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/ipv6/config/source-address', class_name=args[0])

    return fbs_client.delete(keypath)


def set_match_destination_address(args):
    return __set_match_address('destination', args)


def clear_match_destination_address(args):
    if 'mac' == args[1]:
        keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/l2/config/destination-mac', class_name=args[0])
    elif 'ip' == args[1]:
        keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/ipv4/config/destination-address', class_name=args[0])
    elif 'ipv6' == args[1]:
        keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/ipv6/config/destination-address', class_name=args[0])

    return fbs_client.delete(keypath)


def set_match_ethertype(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/l2/config/ethertype',
                      class_name=args[0])
    body = {
        "openconfig-fbs-ext:ethertype": int(args[1], 0) if args[1] not in ethertype_map else ethertype_map[args[1]]
    }

    return fbs_client.patch(keypath, body)


def clear_match_ethertype(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/l2/config/ethertype',
                      class_name=args[0])
    return fbs_client.delete(keypath)


def set_match_vlan(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/l2/config/vlanid',
                      class_name=args[0])
    body = {
        "openconfig-fbs-ext:vlanid": int(args[1])
    }
    return fbs_client.patch(keypath, body)


def clear_match_vlan(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/l2/config/vlanid',
                      class_name=args[0])
    return fbs_client.delete(keypath)


def set_match_pcp(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/l2/config/pcp',
                      class_name=args[0])
    body = {
        "openconfig-fbs-ext:pcp": int(args[1]) if args[1] not in pcp_map.keys() else pcp_map[args[1]]
    }
    return fbs_client.patch(keypath, body)


def clear_match_pcp(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/l2/config/pcp',
                      class_name=args[0])
    return fbs_client.delete(keypath)


def set_match_dei(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/l2/config/dei',
                      class_name=args[0])
    body = {
        "openconfig-fbs-ext:dei": int(args[1])
    }
    return fbs_client.patch(keypath, body)


def clear_match_dei(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/l2/config/dei',
                      class_name=args[0])
    return fbs_client.delete(keypath)


def set_match_ip_protocol(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/ip/config/protocol',
                      class_name=args[0])
    body = {
        "openconfig-fbs-ext:protocol": int(args[1]) if args[1] not in proto_number_map.keys() else proto_number_map[args[1]]
    }
    return fbs_client.patch(keypath, body)


def clear_match_ip_protocol(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/ip/config/protocol',
                      class_name=args[0])
    return fbs_client.delete(keypath)


def set_match_dscp(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/ip/config/dscp',
                      class_name=args[0])
    body = {
        "openconfig-fbs-ext:dscp": int(args[1]) if args[1] not in dscp_map.keys() else dscp_map[args[1]]
    }
    return fbs_client.patch(keypath, body)


def clear_match_dscp(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/ip/config/dscp',
                      class_name=args[0])
    return fbs_client.delete(keypath)


def set_match_layer4_port(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/transport/config/{dir}-port',
                      class_name=args[0], dir=args[1])

    if args[2] == 'eq':
        body = {
            "openconfig-fbs-ext:{}-port".format(args[1]): int(args[3])
        }
    else:
        body = {
            "openconfig-fbs-ext:{}-port".format(args[1]): '{}..{}'.format(args[3], args[4])
        }

    return fbs_client.patch(keypath, body)


def clear_match_layer4_port(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/transport/config/{dir}-port',
                      class_name=args[0], dir=args[1])
    return fbs_client.delete(keypath)


def __convert_tcp_flags(flags):
    flag_val = 0
    flag_mask = 0

    for v in flags:
        if v.startswith('not-'):
            x = v[4:]
            flag_mask = flag_mask | TCP_FLAG_VALUES[x]
        else:
            flag_val = flag_val | TCP_FLAG_VALUES[v]
            flag_mask = flag_mask | TCP_FLAG_VALUES[v]

    return [flag_val, flag_mask]


def __update_tcp_flags(classifier, flags, delete=False):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/transport/config/tcp-flags',
                      class_name=classifier)
    response = fbs_client.get(keypath,None,False)
    data = None
    if response.ok() and bool(response.content):
        data = response.content
    else:
        data = {
            "openconfig-fbs-ext:tcp-flags": []
        }

    tcp_flags = data["openconfig-fbs-ext:tcp-flags"]
    for idx in range(len(tcp_flags)):
        tcp_flags[idx] = tcp_flags[idx].split(":")[-1]

    for flag in flags:
        oc_flag = "TCP_" + flag.replace("-", "_").upper()
        if delete:
            try:
                tcp_flags.remove(oc_flag)
            except ValueError:
                pass
        else:
            tcp_flags.append(oc_flag)

    tcp_flags = list(set(tcp_flags))
    if len(tcp_flags) == 0:
        if delete:
            response = fbs_client.delete(keypath)
        else:
            print('%Error: No TCP Flags configured')
            return None
    else:
        data["openconfig-fbs-ext:tcp-flags"] = tcp_flags
        response = fbs_client.put(keypath, data)

    return response


def set_match_tcp_flags(args):
    return __update_tcp_flags(args[0], args[1:])


def clear_match_tcp_flags(args):
    if len(args) == 1:
        keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/transport/config/tcp-flags',
                          class_name=args[0])
        return fbs_client.delete(keypath)
    #elif len(args) == 2:
    #    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/classifiers/classifier={class_name}/match-hdr-fields/transport/config/tcp-flags={flag}',
    #                      class_name=args[0], flag="TCP_" + args[1].replace("-", "_").upper())
    #    return fbs_client.delete(keypath)
    else:
        return __update_tcp_flags(args[0], args[1:], True)


def create_flow_copp(args):
    # inputs: <policy_name> <class_name> [priority]
    keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-traps/copp-trap={copp_name}',
                      copp_name=args[1])
    response = fbs_client.get(keypath, None,False)
    if response.ok() and bool(response.content):
        if len(args) == 3:
            content = response.content
            if 'openconfig-copp-ext:copp-trap' in response.content:
                if 'config' in content['openconfig-copp-ext:copp-trap'][0]:
                    if 'trap-group' in content['openconfig-copp-ext:copp-trap'][0]['config']:
                        keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-groups/copp-group={copp_name}/config/trap-priority',
                                          copp_name=content['openconfig-copp-ext:copp-trap'][0]['config']['trap-group'])
                        body = {"openconfig-copp-ext:trap-priority": int(args[2])}

                        return fbs_client.patch(keypath, body)
    else:
        raise Exception('Class not found')


def create_flow(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section', policy_name=args[0])
    body = {"openconfig-fbs-ext:section": [{
        "class": args[1],
        "config": {
            "name": args[1],
        }}]}

    if len(args) == 3:
        body["openconfig-fbs-ext:section"][0]["config"]["priority"] = int(args[2])

    return fbs_client.patch(keypath, body)


def delete_flow_copp(args):
    # inputs: <policy_name> <class_name>
    keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-traps/copp-trap={copp_name}/config/trap-group', copp_name=args[1])
    return fbs_client.delete(keypath)


def delete_flow(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section={class_name}',
                      policy_name=args[0], class_name=args[1])
    return fbs_client.delete(keypath)


def set_flow_description(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section={class_name}/config/description',
                      policy_name=args[0], class_name=args[1])
    if len(args) > 3:
        body = {'openconfig-fbs-ext:description': '"{}"'.format(" ".join(args[2:]))}
    else:
        body = {'openconfig-fbs-ext:description': args[2]}
    return fbs_client.patch(keypath, body)


def clear_flow_description(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section={class_name}/config/description',
                      policy_name=args[0], class_name=args[1])
    return fbs_client.delete(keypath)


def set_pcp_remarking_action(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section={class_name}/qos/remark/config/set-dot1p',
                      policy_name=args[0], class_name=args[1])
    body = {'openconfig-fbs-ext:set-dot1p': int(args[2])}
    return fbs_client.patch(keypath, body)


def clear_pcp_remarking_action(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section={class_name}/qos/remark/config/set-dot1p',
                      policy_name=args[0], class_name=args[1])
    return fbs_client.delete(keypath)


def set_dscp_remarking_action(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section={class_name}/qos/remark/config/set-dscp',
                      policy_name=args[0], class_name=args[1])
    body = {'openconfig-fbs-ext:set-dscp': int(args[2])}
    return fbs_client.patch(keypath, body)


def clear_dscp_remarking_action(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section={class_name}/qos/remark/config/set-dscp',
                      policy_name=args[0], class_name=args[1])
    return fbs_client.delete(keypath)


def set_traffic_class_action(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section={class_name}/qos/queuing/config/output-queue-index',
                      policy_name=args[0], class_name=args[1])
    body = {'openconfig-fbs-ext:output-queue-index': int(args[2])}
    return fbs_client.patch(keypath, body)


def clear_traffic_class_action(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section={class_name}/qos/queuing/config/output-queue-index',
                      policy_name=args[0], class_name=args[1])
    return fbs_client.delete(keypath)


def set_policer_action(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section={class_name}/qos/policer/config',
                      policy_name=args[0], class_name=args[1])
    body = {
        "openconfig-fbs-ext:config": {
        }
    }

    index = 2
    while index < len(args):
        if args[index] == 'cir':
            key = 'cir'
            value = args[index + 1]
            if value.endswith('kbps'):
                value = value.replace('kbps', '000')
            elif value.endswith('mbps'):
                value = value.replace('mbps', '000000')
            elif value.endswith('gbps'):
                value = value.replace('gbps', '000000000')
            elif value.endswith('tbps'):
                value = value.replace('tbps', '000000000000')
            elif value.endswith('bps'):
                value = value.replace('bps', '')
        elif args[index] == 'cbs':
            key = 'cbs'
            value = args[index + 1]
            if value.endswith('KB'):
                value = value.replace('KB', '000')
            elif value.endswith('MB'):
                value = value.replace('MB', '000000')
            elif value.endswith('GB'):
                value = value.replace('GB', '000000000')
            elif value.endswith('TB'):
                value = value.replace('TB', '000000000000')
            elif value.endswith('B'):
                value = value.replace('B', '')
        elif args[index] == 'pir':
            key = 'pir'
            value = args[index+1]
            if value.endswith('kbps'):
                value = value.replace('kbps', '000')
            elif value.endswith('mbps'):
                value = value.replace('mbps', '000000')
            elif value.endswith('gbps'):
                value = value.replace('gbps', '000000000')
            elif value.endswith('tbps'):
                value = value.replace('tbps', '000000000000')
            elif value.endswith('bps'):
                value = value.replace('bps', '')
        elif args[index] == 'pbs':
            key = 'pbs'
            value = args[index + 1]
            if value.endswith('KB'):
                value = value.replace('KB', '000')
            elif value.endswith('MB'):
                value = value.replace('MB', '000000')
            elif value.endswith('GB'):
                value = value.replace('GB', '000000000')
            elif value.endswith('TB'):
                value = value.replace('TB', '000000000000')
            elif value.endswith('B'):
                value = value.replace('B', '')
        else:
            print('%Error: Unknown argument {}'.format(args[index]))
            return

        body["openconfig-fbs-ext:config"][key] = value
        index += 2

    return fbs_client.patch(keypath, body)


def clear_policer_action(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section={class_name}/qos/policer/config',
                      policy_name=args[0], class_name=args[1])
    if len(args) == 2:
        return fbs_client.delete(keypath)

    response = fbs_client.get(keypath, depth=None, ignore404=False)
    if response.ok():
        data = response.content
        if len(args) == 2:
            delete_params = ['cir', 'cbs', 'pir', 'pbs']
        else:
            delete_params = []
            for feat in args[2:]:
                if feat == 'cir' or feat == 'pir':
                    delete_params.append(feat)
                elif feat == 'cbs':
                    delete_params.append('cbs')
                elif feat == 'pbs':
                    delete_params.append('pbs')

        for feat in delete_params:
            if feat in data['openconfig-fbs-ext:config'].keys():
                del data['openconfig-fbs-ext:config'][feat]

        return fbs_client.put(keypath, data)
    else:
        print(response.error_message())


def set_mirror_session_action(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section={classifier_name}/monitoring/mirror-sessions/mirror-session',
                      policy_name=args[0], classifier_name=args[1])
    body = {
        "openconfig-fbs-ext:mirror-session": [{
            "session-name": args[2],
            "config": {
                "session-name": args[2]
            }
        }]
    }
    return fbs_client.patch(keypath, body)


def clear_mirror_session_action(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section={classifier_name}/monitoring/mirror-sessions/mirror-session',
                      policy_name=args[0], classifier_name=args[1])
    return fbs_client.delete(keypath)


def set_next_hop_action(args):
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section={classifier_name}/forwarding/next-hops/next-hop',
                      policy_name=args[0], classifier_name=args[1])
    vrf = ''
    pri = ''

    for idx in range(5, len(args), 2):
        if args[idx] == 'vrf':
            vrf = args[idx+1]
        elif args[idx] == 'priority':
            pri = args[idx+1]

    if vrf == "":
        vrf = "openconfig-fbs-ext:INTERFACE_NETWORK_INSTANCE"

    body = {"openconfig-fbs-ext:next-hop": [{
      "ip-address": args[4],
      "network-instance": vrf,
      "config": {
        "ip-address": args[4],
        "network-instance": vrf
      }}]
    }

    if pri != '':
        body["openconfig-fbs-ext:next-hop"][0]["config"]["priority"] = int(pri)

    return fbs_client.patch(keypath, body)


def clear_next_hop_action(args):
    vrf = ''
    pri = ''

    for idx in range(5, len(args), 2):
        if args[idx] == 'vrf':
            vrf = args[idx+1]
        elif args[idx] == 'priority':
            pri = args[idx+1]

    if pri != '':
        next_hop = '{}|{}|{}'.format(args[4], vrf, pri)
        keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_SECTIONS_TABLE/POLICY_SECTIONS_TABLE_LIST={policy_name},{classifier_name}/SET_{ip_type}_NEXTHOP={next_hop}',
                          policy_name=args[0], classifier_name=args[1], ip_type=args[2].upper(), next_hop=next_hop)
    else:
        if vrf == "":
            vrf = "openconfig-fbs-ext:INTERFACE_NETWORK_INSTANCE"
        keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section={classifier_name}/forwarding/next-hops/next-hop={ip_address},{network_instance}',
                          policy_name=args[0], classifier_name=args[1], ip_address=args[4], network_instance=vrf)

    return fbs_client.delete(keypath)


def set_egress_interface_action(args):
    if args[2] == 'null':
        keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section={classifier_name}/forwarding/config/discard',
                          policy_name=args[0], classifier_name=args[1])
        data = {
            "openconfig-fbs-ext:discard": True
        }
        return fbs_client.patch(keypath, data)
    else:
        keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section={classifier_name}/forwarding/egress-interfaces/egress-interface',
                          policy_name=args[0], classifier_name=args[1])

        data = {
            "openconfig-fbs-ext:egress-interface": [{
                "intf-name": args[2],
                "config": {
                    "intf-name": args[2]
                }
            }]
        }

        if len(args) == 5:
            data["openconfig-fbs-ext:egress-interface"][0]["config"]["priority"] = int(args[4])

        return fbs_client.patch(keypath, data)


def clear_egress_interface_action(args):
    if args[2] == 'null':
        keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section={classifier_name}/forwarding/config/discard',
                          policy_name=args[0], classifier_name=args[1])
        return fbs_client.delete(keypath)
    else:
        if len(args) == 5:
            egr_if = "{}|{}".format(args[2], args[4])
            keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_SECTIONS_TABLE/POLICY_SECTIONS_TABLE_LIST={policy_name},{classifier_name}/SET_INTERFACE={egr_if}',
                              policy_name=args[0], classifier_name=args[1], egr_if=egr_if)
        else:
            keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/policies/policy={policy_name}/sections/section={classifier_name}/forwarding/egress-interfaces/egress-interface={intf_name}',
                              policy_name=args[0], classifier_name=args[1], intf_name=args[2])

        return fbs_client.delete(keypath)


def bind_policy(args):
    ifname = args[3] if len(args) == 4 else "Switch"
    body = {
        "openconfig-fbs-ext:config": {
            "id": ifname
        },
        "openconfig-fbs-ext:interface-ref": {
            "config": {
                "interface": ifname
            }
        },
        "openconfig-fbs-ext:{}-policies".format('ingress' if args[2] =='in' else 'egress'): {
            args[1]: {
                "config": {
                    "policy-name": args[0]
                }
            }
        }
    }
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/interfaces/interface={interface_name}',
                      interface_name=ifname)
    return fbs_client.post(keypath, body)


def unbind_policy(args):
    ifname = args[2] if len(args) == 3 else "Switch"
    keypath = cc.Path('/restconf/data/openconfig-fbs-ext:fbs/interfaces/interface={interface_name}/{direction}-policies/{policy_type}', 
            interface_name=ifname, direction='ingress' if args[1] =='in' else 'egress', policy_type=args[0])
    return fbs_client.delete(keypath)


def show_policy_summary(args):
    if len(args) > 0:
        if args[0] == 'interface':
            interface_name = args[1]
            keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_BINDING_TABLE/POLICY_BINDING_TABLE_LIST={interface_name}',
                              interface_name=interface_name)
        elif args[0] == "Switch":
            interface_name = args[0]
            keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_BINDING_TABLE/POLICY_BINDING_TABLE_LIST={interface_name}',
                              interface_name=interface_name)
        else:
            keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_BINDING_TABLE/POLICY_BINDING_TABLE_LIST')
    else:
        keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_BINDING_TABLE/POLICY_BINDING_TABLE_LIST')

    return fbs_client.get(keypath, depth=None, ignore404=False)


def show_policy(args):
    body = {"sonic-flow-based-services:input": {}}
    if len(args) > 1:
        body = {"sonic-flow-based-services:input": {"TYPE": args[1].upper()}}
    elif len(args) == 1:
        policy_name = args[0]
        body = {"sonic-flow-based-services:input": {"POLICY_NAME": policy_name}}

    keypath = cc.Path('/restconf/operations/sonic-flow-based-services:get-policy')
    return fbs_client.post(keypath, body)


def show_classifier(args):
    body = {"sonic-flow-based-services:input": {}}
    if len(args) > 1:
        body = {"sonic-flow-based-services:input": {"MATCH_TYPE": args[1].upper()}}
    elif len(args) == 1:
        body = {"sonic-flow-based-services:input": {"CLASSIFIER_NAME": args[0]}}

    keypath = cc.Path('/restconf/operations/sonic-flow-based-services:get-classifier')
    return fbs_client.post(keypath, body)


def show_details_by_policy(args):
    body = {"sonic-flow-based-services:input": dict()}
    if len(args) > 0:
        body["sonic-flow-based-services:input"]["POLICY_NAME"] = args[0]
    if len(args) > 1:
        if args[1] == "interface":
            body["sonic-flow-based-services:input"]["INTERFACE_NAME"] = args[2]
        else:
            body["sonic-flow-based-services:input"]["INTERFACE_NAME"] = args[1]

    keypath = cc.Path('/restconf/operations/sonic-flow-based-services:get-service-policy')
    return fbs_client.post(keypath, body)


def show_details_by_interface(args):
    body = {"sonic-flow-based-services:input": dict()}
    if args[0] == "Switch":
        body["sonic-flow-based-services:input"]["INTERFACE_NAME"] = args[0]
        if len(args) == 3:
            body["sonic-flow-based-services:input"]["TYPE"] = args[2]
    else:
        if args[0] == "Vlan":
            body["sonic-flow-based-services:input"]["INTERFACE_NAME"] = args[0] + args[1]
            if len(args) == 5:
                body["sonic-flow-based-services:input"]["TYPE"] = args[4]
        else:
            body["sonic-flow-based-services:input"]["INTERFACE_NAME"] = args[0]
            if len(args) == 4:
                body["sonic-flow-based-services:input"]["TYPE"] = args[3]

    keypath = cc.Path('/restconf/operations/sonic-flow-based-services:get-service-policy')
    return fbs_client.post(keypath, body)


def clear_details_by_policy(args):
    body = {"sonic-flow-based-services:input": dict()}
    if len(args) > 0:
        body["sonic-flow-based-services:input"]["POLICY_NAME"] = args[0]
    if len(args) > 1:
        if args[1] == "interface":
            body["sonic-flow-based-services:input"]["INTERFACE_NAME"] = args[2] + args[3]
        else:
            body["sonic-flow-based-services:input"]["INTERFACE_NAME"] = args[1]

    keypath = cc.Path('/restconf/operations/sonic-flow-based-services:clear-service-policy-counters')
    return fbs_client.post(keypath, body)


def clear_details_by_interface(args):
    body = {"sonic-flow-based-services:input": dict()}
    if args[0] == "Switch":
        body["sonic-flow-based-services:input"]["INTERFACE_NAME"] = args[0]
        if len(args) == 3:
            body["sonic-flow-based-services:input"]["TYPE"] = args[2]
    else:
        body["sonic-flow-based-services:input"]["INTERFACE_NAME"] = args[0]
        if len(args) == 3:
            body["sonic-flow-based-services:input"]["TYPE"] = args[2]

    keypath = cc.Path('/restconf/operations/sonic-flow-based-services:clear-service-policy-counters')
    return fbs_client.post(keypath, body)


def get_copp_trap_id(name):
    trap_id_val = ""
    tmp_keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-traps/copp-trap={copp_name}/config/trap-ids',
                          copp_name=name)
    tmp_response = fbs_client.get(tmp_keypath, depth=None, ignore404=False)
    if tmp_response is None:
        trap_id_val = ""
    elif tmp_response.ok():
        response = tmp_response.content
        if 'openconfig-copp-ext:trap-ids' in response:
            trap_id_val = response['openconfig-copp-ext:trap-ids']

    return trap_id_val


def set_classifier_match_protocol(args):
    trap_id_val = get_copp_trap_id(args[0])

    nd_list = []
    if trap_id_val != "":
        nd_list = trap_id_val.split(',')
    if args[1] in nd_list:
        # entry already exists
        return
    nd_list.append(args[1])
    outval = ','.join(nd_list)
    keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-traps')
    body = {"openconfig-copp-ext:copp-traps": {
        "copp-trap": [
            {
                "name": args[0],
                "config": {
                    "trap-ids": outval
                }
            }
        ]
    }}

    return fbs_client.patch(keypath, body)


def clear_classifier_match_protocol(args):
    trap_id_val = get_copp_trap_id(args[0])

    nd_list = []
    if trap_id_val != "":
        nd_list = trap_id_val.split(',')
    if args[1] not in nd_list:
        # entry does not exist
        return
    nd_list.remove(args[1])
    outval = ','.join(nd_list)
    if outval == "":
        keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-traps/copp-trap={copp_name}/config/trap-ids',
                          copp_name=args[0])
        return fbs_client.delete(keypath)
    else:
        keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-traps/copp-trap={copp_name}/config/trap-ids',
                          copp_name=args[0])
        body = {"openconfig-copp-ext:trap-ids": outval}

        return fbs_client.patch(keypath, body)


def set_trap_action(args):
    keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-groups')
    body = {"openconfig-copp-ext:copp-groups": {
        "copp-group": [
            {
                "name": args[0],
                "config": {
                    "trap-action": args[1]
                }
            }
        ]
    }}

    return fbs_client.patch(keypath, body)


def clear_trap_action(args):
    keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-groups/copp-group={copp_name}/config/trap-action',
                      copp_name=args[0])

    return fbs_client.delete(keypath)


def set_queue_id_action(args):
    keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-groups')
    body = {"openconfig-copp-ext:copp-groups": {
        "copp-group": [
            {
                "name": args[0],
                "config": {
                    "queue": int(args[1])
                }
            }
        ]
    }}

    return fbs_client.patch(keypath, body)


def clear_queue_id_action(args):
    keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-groups/copp-group={copp_name}/config/queue',
                      copp_name=args[0])

    return fbs_client.delete(keypath)


def set_copp_policer_action(args):
    keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-groups')
    body = {"openconfig-copp-ext:copp-groups": {
        "copp-group": [
            {
                "name": args[0],
                "config": dict()
            }
        ]
    }}
    data = {
        "name": args[0],
        "config": dict()
    }

    index = 1
    while index < len(args):
        if args[index] == 'cir':
            key = 'cir'
            value = args[index + 1]
            if value.endswith('kbps'):
                value = value.replace('kbps', '000')
            elif value.endswith('mbps'):
                value = value.replace('mbps', '000000')
            elif value.endswith('gbps'):
                value = value.replace('gbps', '000000000')
            elif value.endswith('tbps'):
                value = value.replace('tbps', '000000000000')
            elif value.endswith('bps'):
                value = value.replace('bps', '')
        elif args[index] == 'cbs':
            key = 'cbs'
            value = args[index + 1]
            if value.endswith('KB'):
                value = value.replace('KB', '000')
            elif value.endswith('MB'):
                value = value.replace('MB', '000000')
            elif value.endswith('GB'):
                value = value.replace('GB', '000000000')
            elif value.endswith('TB'):
                value = value.replace('TB', '000000000000')
            elif value.endswith('B'):
                value = value.replace('B', '')
        elif args[index] == 'pir':
            key = 'pir'
            value = args[index + 1]
            if value.endswith('kbps'):
                value = value.replace('kbps', '000')
            elif value.endswith('mbps'):
                value = value.replace('mbps', '000000')
            elif value.endswith('gbps'):
                value = value.replace('gbps', '000000000')
            elif value.endswith('tbps'):
                value = value.replace('tbps', '000000000000')
            elif value.endswith('bps'):
                value = value.replace('bps', '')
        elif args[index] == 'pbs':
            key = 'pbs'
            value = args[index + 1]
            if value.endswith('KB'):
                value = value.replace('KB', '000')
            elif value.endswith('MB'):
                value = value.replace('MB', '000000')
            elif value.endswith('GB'):
                value = value.replace('GB', '000000000')
            elif value.endswith('TB'):
                value = value.replace('TB', '000000000000')
            elif value.endswith('B'):
                value = value.replace('B', '')
        elif args[index] == 'meter-type':
            key = 'meter-type'
            value = args[index + 1]
        elif args[index] == 'mode':
            key = 'mode'
            value = args[index + 1]
        elif args[index] == 'green':
            key = 'green-action'
            value = args[index + 1]
        elif args[index] == 'red':
            key = 'red-action'
            value = args[index + 1]
        elif args[index] == 'yellow':
            key = 'yellow-action'
            value = args[index + 1]
        else:
            print('%Error: Unknown argument {}'.format(args[index]))
            return

        data["config"][key] = value
        index += 2

    body["openconfig-copp-ext:copp-groups"]["copp-group"] = [data]
    return fbs_client.patch(keypath, body)


def clear_copp_policer_action(args):
    keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-groups/copp-group={copp_name}',
                      copp_name=args[0])

    response = fbs_client.get(keypath, depth=None, ignore404=False)
    if response.ok():
        data = response.content
        if len(args) == 1:
            delete_params = ['pbs', 'pir', 'cbs', 'cir', 'meter-type', 'mode', 'green-action', 'red-action', 'yellow-action']
        else:
            delete_params = []
        for feat in args[1:]:
            if feat == 'mode':
                delete_params.append('mode')
                delete_params.append('green-action')
                delete_params.append('red-action')
                delete_params.append('yellow-action')
            elif feat == 'red':
                delete_params.append('red-action')
            elif feat == 'green':
                delete_params.append('green-action')
            elif feat == 'yellow':
                delete_params.append('yellow-action')
            elif feat == 'cir':
                delete_params.append('cir')
                delete_params.append('cbs')
                delete_params.append('pir')
                delete_params.append('pbs')
            elif feat == 'cbs':
                delete_params.append('cbs')
                delete_params.append('pir')
                delete_params.append('pbs')
            elif feat == 'pir':
                delete_params.append('pir')
                delete_params.append('pbs')
            else:
                delete_params.append(feat)

        for feat in delete_params:
            if feat in data['openconfig-copp-ext:copp-group'][0]['config'].keys():
                del data['openconfig-copp-ext:copp-group'][0]['config'][feat]
        if 'state' in data['openconfig-copp-ext:copp-group'][0].keys():
            del data['openconfig-copp-ext:copp-group'][0]['state']

        return fbs_client.put(keypath, data)
    else:
        print('Error:{}'.format(response.error_message()))


def create_copp_action(args):
    pass


def delete_copp_action(args):
    keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-groups/copp-group={copp_name}',
                      copp_name=args[0])

    return fbs_client.delete(keypath)


def set_copp_action_group(args):
    keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-traps')
    body = {"openconfig-copp-ext:copp-traps": {
        "copp-trap": [
            {
                "name": args[1],
                "config": {
                    "trap-group": args[2]
                }
            }
        ]
    }}

    return fbs_client.patch(keypath, body)


def set_copp_trap_priority_action(args):
    keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-groups')
    body = {"openconfig-copp-ext:copp-groups": {
        "copp-group": [
            {
                "name": args[0],
                "config": {
                    "trap-priority": int(args[1])
                }
            }
        ]
    }}

    return fbs_client.patch(keypath, body)


def clear_copp_trap_priority_action(args):
    keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-groups/copp-group={copp_name}/config/trap-priority',
                      copp_name=args[0])

    return fbs_client.delete(keypath)


def show_copp_protocols(args):
    if args[0] == "actions":
        keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-groups/copp-group')
        return fbs_client.get(keypath, depth=None, ignore404=False)
    elif args[0] == "classifiers":
        keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-traps/copp-trap')
        return fbs_client.get(keypath, depth=None, ignore404=False)
    elif args[0] == "policy":
        keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-traps/copp-trap')
        return fbs_client.get(keypath, depth=None, ignore404=False)
    keypath = cc.Path('/restconf/operations/sonic-copp:get-match-protocols')
    return fbs_client.post(keypath, {})


########################################################################################################################
#                                                  Response handlers                                                   #
########################################################################################################################
def handle_generic_set_response(response, args, op_str):
    if response.ok():
        resp_content = response.content
        if resp_content is not None:
            print("{}".format(str(resp_content)))
        return 0
    else:
        try:
            error_data = response.errors().get('error', list())[0]
            if 'error-app-tag' in error_data:
                if error_data['error-app-tag'] == 'too-many-elements':
                    print('%Error: Configuration limit reached.')
                elif error_data['error-app-tag'] == 'update-not-allowed':
                    if op_str.startswith('create_policy_'):
                        print("%Error: Creating policy-maps with same name and different type not allowed")
                    elif op_str.startswith('create_classifier_'):
                        print("%Error: Creating class-maps with same name and different match-types not allowed")
                    else:
                        print("%Error: Update not allowed for this configuration")
                elif error_data['error-app-tag'] != 'same-policy-already-applied':
                    print(response.error_message())
            else:
                print(response.error_message())
        except Exception as e:
            print(response.error_message())

        return -1


def handle_generic_delete_response(response, args, op_str):
    if response.ok():
        resp_content = response.content
        if resp_content is not None:
            print("%Error: {}".format(str(resp_content)))
            return -1
        return 0
    elif response.status_code != '404':
        print(response.error_message())
        return -1
    else:
        return 0


def handle_show_policy_summary_response(response, args, op_str):
    if response.ok():
        filter_type = ['qos', 'monitoring', 'forwarding']
        directions = ['ingress', 'egress']
        if_filter = None
        next = 0

        while len(args) > next+1:
            if args[next] == 'type':
                filter_type = [args[next + 1]]
                next = next + 2
            elif args[next] == 'interface':
                if_filter = args[next + 1]
                next = next + 2
            elif args[next] == 'Switch':
                if_filter = args[next + 1]
                next = next + 1

        render_data = OrderedDict()
        for binding in response.content.get('sonic-flow-based-services:POLICY_BINDING_TABLE_LIST', []):
            if if_filter and if_filter != binding['INTERFACE_NAME']:
                continue

            if_data = []
            for dir in directions:
                for ft in filter_type:

                    key = '{}_{}_POLICY'.format(dir.upper(), ft.upper())
                    if key in binding:
                        if_data.append(tuple([ft, binding[key], dir]))

            if len(if_data):
                render_data[binding['INTERFACE_NAME']] = if_data

        sorted_data = OrderedDict(natsorted(render_data.items(), key=acl_natsort_intf_prio))
        log.log_debug(str(sorted_data))
        show_cli_output('show_service_policy_summary.j2', sorted_data)
    else:
        if response.status_code != 404:
            print(response.error_message())


def policy_util_form_ip_nexthop_list(if_name, remote_if_list):
    ip_nexthop_dict = {}
    ip_nexthop_list = []
    return ip_nexthop_dict, ip_nexthop_list


def handle_show_policy_response(response, args, op_str):
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
            show_cli_output('show_policy.j2', render_data)
    else:
        print(response.error_message())


def handle_show_classifier_response(response, args, op_str):
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

            # TODO Sort references also
            show_cli_output('show_classifier.j2',
                            render_data,
                            mac_addr_to_user_fmt=sonic_cli_acl.mac_addr_to_user_fmt,
                            ip_addr_to_user_fmt=sonic_cli_acl.convert_ip_addr_to_user_fmt,
                            ip_proto_to_user_fmt=sonic_cli_acl.ip_protocol_to_user_fmt,
                            tcp_flags_to_user_fmt=sonic_cli_acl.tcp_flags_to_user_fmt,
                            ethertype_to_user_fmt=ethertype_to_user_fmt,
                            pcp_to_user_fmt=sonic_cli_acl.pcp_to_user_fmt,
                            dscp_to_user_fmt=sonic_cli_acl.dscp_to_user_fmt)
    else:
        print(response.error_message())


def handle_show_service_policy_details_response(response, args, op_str):
    if response.ok():
        if response.content is not None and bool(response.content):
            output = response.content["sonic-flow-based-services:output"]["INTERFACES"]
            render_data = OrderedDict()
            output_dict = dict()
            for entry in output:
                output_dict[entry["INTERFACE_NAME"]] = entry

            # sort by intf name
            sorted_intfs = natsorted(output_dict.keys(), key=acl_natsort_intf_prio)
            for intf_name in sorted_intfs:
                intf_data = output_dict[intf_name]
                render_data[intf_name] = OrderedDict()

                # Assume ingress and egress. Will not be displayed if not present
                render_data[intf_name]["ingress"] = OrderedDict()
                render_data[intf_name]["egress"] = OrderedDict()

                for policy_data in intf_data["APPLIED_POLICIES"]:
                    # Sort policies applied by ingress and egress
                    for stage in ["INGRESS", "EGRESS"]:
                        policy_names = list()
                        data = dict()
                        if policy_data["STAGE"] == stage:
                            policy_names.append(policy_data["POLICY_NAME"])
                            data[policy_data["POLICY_NAME"]] = policy_data

                        policy_names = natsorted(policy_names)
                        for name in policy_names:
                            policy_sort_data = OrderedDict()
                            policy_data = data[name]
                            policy_sort_data["TYPE"] = policy_data["TYPE"].lower()
                            policy_sort_data["DESCRIPTION"] = policy_data.get("DESCRIPTION", "")
                            policy_sort_data["FLOWS"] = OrderedDict()
                            flows = dict()
                            for flow in policy_data.get("FLOWS", list()):
                                flows[(flow["PRIORITY"], flow["CLASS_NAME"])] = flow

                            # Sort Policy flows by priority
                            flow_keys = natsorted(flows.keys(), reverse=True)
                            for flow in flow_keys:
                                policy_sort_data["FLOWS"][flow] = flows[flow]

                            render_data[intf_name][stage.lower()][name] = policy_sort_data

            # Finally render the sorted data
            show_cli_output('show_service_policy.j2', render_data)
    else:
        print(response.error_message())


def handle_clear_details_by_policy_response(response, args, op_str):
    if not response.ok():
        print(response.error_message())


def handle_clear_details_by_interface_response(response, args, op_str):
    if not response.ok():
        print(response.error_message())


def handle_show_copp_protocols_response(response, args, op_str):
    if response.ok():
        content = response.content
        if "openconfig-copp-ext:copp-group" in content:
            show_cli_output('show_copp_actions.j2', content)
        if 'sonic-copp:output' in content:
            if 'Match_protocols' in content['sonic-copp:output']:
                show_cli_output('show_copp_protocols.j2', sorted(content['sonic-copp:output']['Match_protocols'], key = lambda i: i['Protocol']))
        if "openconfig-copp-ext:copp-trap" in content:
            if args[0] == "policy":
                if "openconfig-copp-ext:copp-trap" in content:
                    for entry in content["openconfig-copp-ext:copp-trap"]:
                        if "config" in entry and "trap-group" in entry["config"]:
                            keypath = cc.Path('/restconf/data/openconfig-copp-ext:copp/copp-groups/copp-group={copp_name}',
                                              copp_name=entry["config"]["trap-group"])
                            resp2 = fbs_client.get(keypath, depth=None, ignore404=False)
                            if resp2.ok():
                                content2 = resp2.content
                                if "openconfig-copp-ext:copp-group" in content2:
                                    for entry2 in resp2.content["openconfig-copp-ext:copp-group"]:
                                        if "config" in entry2:
                                            for key, value in entry2["config"].items():
                                                entry[key] = value
                show_cli_output('show_copp_policy.j2', content)
            else:
                show_cli_output('show_copp_classifier.j2', content)


# ######################################################################################################################
#
# #######################################################################################################################

request_handlers = {
    'create_policy_qos': create_policy,
    'create_policy_monitoring': create_policy,
    'create_policy_forwarding': create_policy,
    'create_policy_copp': create_policy_copp,
    'delete_policy': delete_policy,
    'set_policy_description': set_policy_description,
    'clear_policy_description': clear_policy_description,
    'create_classifier_acl': create_classifier,
    'create_classifier_fields': create_classifier,
    'create_classifier_copp': create_classifier_copp,
    'delete_classifier': delete_classifier,
    'set_classifier_description': set_classifier_description,
    'clear_classifier_description': clear_classifier_description,
    'set_classifier_match_acl': set_classifier_match_acl,
    'clear_classifier_match_acl': clear_classifier_match_acl,
    'set_match_source_address': set_match_source_address,
    'clear_match_source_address': clear_match_source_address,
    'set_match_destination_address': set_match_destination_address,
    'clear_match_destination_address': clear_match_destination_address,
    'set_match_ethertype': set_match_ethertype,
    'clear_match_ethertype': clear_match_ethertype,
    'set_match_vlan': set_match_vlan,
    'clear_match_vlan': clear_match_vlan,
    'set_match_pcp': set_match_pcp,
    'clear_match_pcp': clear_match_pcp,
    'set_match_dei': set_match_dei,
    'clear_match_dei': clear_match_dei,
    'set_match_ip_protocol': set_match_ip_protocol,
    'clear_match_ip_protocol': clear_match_ip_protocol,
    'set_match_dscp': set_match_dscp,
    'clear_match_dscp': clear_match_dscp,
    'set_match_layer4_port': set_match_layer4_port,
    'clear_match_layer4_port': clear_match_layer4_port,
    'set_match_tcp_flags': set_match_tcp_flags,
    'clear_match_tcp_flags': clear_match_tcp_flags,
    'create_flow_qos': create_flow,
    'create_flow_monitoring': create_flow,
    'create_flow_forwarding': create_flow,
    'create_flow_copp': create_flow_copp,
    'delete_flow_qos': delete_flow,
    'delete_flow_monitoring': delete_flow,
    'delete_flow_forwarding': delete_flow,
    'delete_flow_copp': delete_flow_copp,
    'set_flow_description': set_flow_description,
    'clear_flow_description': clear_flow_description,
    'set_pcp_remarking_action': set_pcp_remarking_action,
    'clear_pcp_remarking_action': clear_pcp_remarking_action,
    'set_dscp_remarking_action': set_dscp_remarking_action,
    'clear_dscp_remarking_action': clear_dscp_remarking_action,
    'set_traffic_class_action': set_traffic_class_action,
    'clear_traffic_class_action': clear_traffic_class_action,
    'set_policer_action': set_policer_action,
    'clear_policer_action': clear_policer_action,
    'set_mirror_session_action': set_mirror_session_action,
    'clear_mirror_session_action': clear_mirror_session_action,
    'set_next_hop_action': set_next_hop_action,
    'clear_next_hop_action': clear_next_hop_action,
    'set_egress_interface_action': set_egress_interface_action,
    'clear_egress_interface_action': clear_egress_interface_action,
    'bind_policy': bind_policy,
    'unbind_policy': unbind_policy,
    'show_policy': show_policy,
    'show_classifier': show_classifier,
    'show_policy_summary': show_policy_summary,
    'show_details_by_policy': show_details_by_policy,
    'show_details_by_interface': show_details_by_interface,
    'clear_details_by_policy': clear_details_by_policy,
    'clear_details_by_interface': clear_details_by_interface,
    'set_classifier_match_protocol': set_classifier_match_protocol,
    'clear_classifier_match_protocol': clear_classifier_match_protocol,
    'set_trap_action': set_trap_action,
    'clear_trap_action': clear_trap_action,
    'set_queue_id_action': set_queue_id_action,
    'clear_queue_id_action': clear_queue_id_action,
    'set_copp_policer_action': set_copp_policer_action,
    'clear_copp_policer_action': clear_copp_policer_action,
    'show_copp_protocols': show_copp_protocols,
    'create_copp_action': create_copp_action,
    'delete_copp_action': delete_copp_action,
    'set_copp_action_group': set_copp_action_group,
    'set_copp_trap_priority_action': set_copp_trap_priority_action,
    'clear_copp_trap_priority_action': clear_copp_trap_priority_action
}


response_handlers = {
    'create_policy_qos': handle_generic_set_response,
    'create_policy_monitoring': handle_generic_set_response,
    'create_policy_forwarding': handle_generic_set_response,
    'create_policy_copp': handle_generic_set_response,
    'delete_policy': handle_generic_delete_response,
    'set_policy_description': handle_generic_set_response,
    'clear_policy_description': handle_generic_delete_response,
    'create_classifier_acl': handle_generic_set_response,
    'create_classifier_fields': handle_generic_set_response,
    'create_classifier_copp': handle_generic_set_response,
    'delete_classifier': handle_generic_delete_response,
    'set_classifier_description': handle_generic_set_response,
    'clear_classifier_description': handle_generic_delete_response,
    'set_classifier_match_acl': handle_generic_set_response,
    'clear_classifier_match_acl': handle_generic_delete_response,
    'set_match_source_address': handle_generic_set_response,
    'clear_match_source_address': handle_generic_delete_response,
    'set_match_destination_address': handle_generic_set_response,
    'clear_match_destination_address': handle_generic_delete_response,
    'set_match_ethertype': handle_generic_set_response,
    'clear_match_ethertype': handle_generic_delete_response,
    'set_match_vlan': handle_generic_set_response,
    'clear_match_vlan': handle_generic_delete_response,
    'set_match_pcp': handle_generic_set_response,
    'clear_match_pcp': handle_generic_delete_response,
    'set_match_dei': handle_generic_set_response,
    'clear_match_dei': handle_generic_delete_response,
    'set_match_ip_protocol': handle_generic_set_response,
    'clear_match_ip_protocol': handle_generic_delete_response,
    'set_match_dscp': handle_generic_set_response,
    'clear_match_dscp': handle_generic_delete_response,
    'set_match_layer4_port': handle_generic_set_response,
    'clear_match_layer4_port': handle_generic_delete_response,
    'set_match_tcp_flags': handle_generic_set_response,
    'clear_match_tcp_flags': handle_generic_delete_response,
    'create_flow_qos': handle_generic_set_response,
    'create_flow_monitoring': handle_generic_set_response,
    'create_flow_forwarding': handle_generic_set_response,
    'create_flow_copp': handle_generic_set_response,
    'delete_flow_qos': handle_generic_delete_response,
    'delete_flow_monitoring': handle_generic_delete_response,
    'delete_flow_forwarding': handle_generic_delete_response,
    'delete_flow_copp': handle_generic_set_response,
    'set_flow_description': handle_generic_set_response,
    'clear_flow_description': handle_generic_delete_response,
    'set_pcp_remarking_action': handle_generic_set_response,
    'clear_pcp_remarking_action': handle_generic_delete_response,
    'set_dscp_remarking_action': handle_generic_set_response,
    'clear_dscp_remarking_action': handle_generic_delete_response,
    'set_traffic_class_action': handle_generic_set_response,
    'clear_traffic_class_action': handle_generic_delete_response,
    'set_policer_action': handle_generic_set_response,
    'clear_policer_action': handle_generic_delete_response,
    'set_mirror_session_action': handle_generic_set_response,
    'clear_mirror_session_action': handle_generic_delete_response,
    'set_next_hop_action': handle_generic_set_response,
    'clear_next_hop_action': handle_generic_delete_response,
    'set_egress_interface_action': handle_generic_set_response,
    'clear_egress_interface_action': handle_generic_delete_response,
    'bind_policy': handle_generic_set_response,
    'unbind_policy': handle_generic_delete_response,
    'show_policy': handle_show_policy_response,
    'show_classifier': handle_show_classifier_response,
    'show_policy_summary': handle_show_policy_summary_response,
    'show_details_by_policy': handle_show_service_policy_details_response,
    'show_details_by_interface': handle_show_service_policy_details_response,
    'clear_details_by_policy': handle_clear_details_by_policy_response,
    'clear_details_by_interface': handle_clear_details_by_interface_response,
    'set_classifier_match_protocol': handle_generic_set_response,
    'clear_classifier_match_protocol': handle_generic_delete_response,
    'set_trap_action': handle_generic_set_response,
    'clear_trap_action': handle_generic_delete_response,
    'set_queue_id_action': handle_generic_set_response,
    'clear_queue_id_action': handle_generic_delete_response,
    'set_copp_policer_action': handle_generic_set_response,
    'clear_copp_policer_action': handle_generic_delete_response,
    'show_copp_protocols': handle_show_copp_protocols_response,
    'create_copp_action': handle_generic_set_response,
    'delete_copp_action': handle_generic_delete_response,
    'set_copp_action_group': handle_generic_set_response,
    'set_copp_trap_priority_action': handle_generic_set_response,
    'clear_copp_trap_priority_action': handle_generic_delete_response
}


def run(op_str, args):
    try:
        log.log_debug(str(args))
        correct_args = list()
        for arg in args:
            if arg == "|" or arg == "\\|":
                break
            else:
                correct_args.append(arg)
        log.log_debug(str(correct_args))
        resp = request_handlers[op_str](correct_args)
        if resp:
            return response_handlers[op_str](resp, correct_args, op_str)
    except FbsAclCLIError as e:
        print("%Error: {}".format(e.message))
        return -1
    except Exception as e:
        log.log_error(traceback.format_exc())
        print('%Error: Encountered exception "{}"'.format(str(e)))
        return -1
    return 0


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2:])


def ethertype_to_user_fmt(val):
    if val == '0x800':
        return 'ip'
    elif val == '0x86dd':
        return 'ipv6'
    elif val == '0x806':
        return 'arp'
    else:
        return val

