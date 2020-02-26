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
import collections
from collections import OrderedDict
import cli_client as cc
from scripts.render_cli import show_cli_output
import ipaddress
import traceback
import json
import cli_log as log


proto_number_map = OrderedDict([("1", "IP_ICMP"),
                                ("icmp", "IP_ICMP"),
                                ("6", "IP_TCP"),
                                ("17", "IP_UDP"),
                                ("tcp", "IP_TCP"),
                                ("udp", "IP_UDP"),
                                ("2", "IP_IGMP"),
                                ("103", "IP_PIM"),
                                ("46", "IP_RSVP"),
                                ("47", "IP_GRE"),
                                ("51", "IP_AUTH"),
                                ("icmpv6", 58),
                                ("115", "IP_L2TP")])

ethertype_map = OrderedDict([('0x0800', 'ETHERTYPE_IPV4'), ('ip', 'ETHERTYPE_IPV4'),
                             ('0x86dd', 'ETHERTYPE_IPV6'), ('ipv6', 'ETHERTYPE_IPV6'),
                             ('0x0806', 'ETHERTYPE_ARP'), ('arp', 'ETHERTYPE_ARP'),
                             ('0x88cc', 'ETHERTYPE_LLDP'), ('0x8915', 'ETHERTYPE_ROCE'),
                             ('0x8847', 'ETHERTYPE_MPLS')])

pcp_map = {"bk": 1, "be": 0, "ee": 2, "ca": 3, "vi": 4, "vo": 5, "ic": 6, "nc": 7}

proto_number_rev_map = {val: key for key, val in proto_number_map.items()}
ethertype_rev_map = {val: key for key, val in ethertype_map.items()}
pcp_rev_map = {val: key for key, val in pcp_map.items()}

acl_client = cc.ApiClient()


def handle_create_acl_request(args):
    """Configure ACL table"""
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set')
    body = collections.defaultdict()
    body["acl-set"] = [{
        "name": args[0],
        "type": args[1],
        "config": {
            "name": args[0],
            "type": args[1]
        }
    }]

    return acl_client.patch(keypath, body)


def __format_mac_addr(macaddr):
    return "{}{}:{}{}:{}{}:{}{}:{}{}:{}{}".format(*macaddr.translate(None, ".:-"))


def __create_acl_rule_l2(args):
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set={name},{acl_type}/acl-entries/acl-entry',
                      name=args[0], acl_type=args[1])

    forwarding_action = "ACCEPT" if args[3] == 'permit' else 'DROP'

    body = collections.defaultdict()
    body["acl-entry"] = [{
        "sequence-id": int(args[2]),
        "config": {
            "sequence-id": int(args[2])
        },
        "l2": {
            "config": {
            }
        },
        "actions": {
            "config": {
                "forwarding-action": forwarding_action
            }
        }
    }]

    if args[4] == 'host':
        body["acl-entry"][0]["l2"]["config"]["source-mac"] = __format_mac_addr(args[5])
        next_item = 6
    elif '/' in args[4]:
        mac, mask = args[4].split('/')
        body["acl-entry"][0]["l2"]["config"]["source-mac"] = __format_mac_addr(mac)
        body["acl-entry"][0]["l2"]["config"]["source-mac-mask"] = __format_mac_addr(mask)
        next_item = 5
    elif args[4] == 'any':
        next_item = 5
    else:
        print('%Error: Incorrect Source MAC Address')
        return

    if args[next_item] == 'host':
        body["acl-entry"][0]["l2"]["config"]["destination-mac"] = __format_mac_addr(args[next_item + 1])
        next_item += 2
    elif '/' in args[next_item]:
        mac, mask = args[next_item].split('/')
        body["acl-entry"][0]["l2"]["config"]["destination-mac"] = __format_mac_addr(mac)
        body["acl-entry"][0]["l2"]["config"]["destination-mac-mask"] = __format_mac_addr(mask)
        next_item += 1
    elif args[next_item] == 'any':
        next_item += 1
    else:
        print('%Error: Incorrect destination MAC Address')
        return

    while next_item < len(args):
        if args[next_item] == 'pcp':
            if args[next_item + 1] in pcp_map:
                body["acl-entry"][0]["l2"]["config"]['pcp'] = pcp_map[args[next_item + 1]]
            elif '/' in args[next_item + 1]:
                val, mask = args[next_item + 1].split('/')
                body["acl-entry"][0]["l2"]["config"]['pcp'] = int(val)
                body["acl-entry"][0]["l2"]["config"]['pcp-mask'] = int(mask)
            else:
                body["acl-entry"][0]["l2"]["config"]['pcp'] = int(args[next_item + 1])
            next_item += 2
        elif args[next_item] == 'dei':
            body["acl-entry"][0]["l2"]["config"]['dei'] = int(args[next_item + 1])
            next_item += 2
        elif args[next_item] == 'vlan':
            next_item += 2
        elif args[next_item] == 'remark':
            descr = " ".join(args[next_item + 1:])
            if descr.startswith('"') and descr.endswith('"'):
                descr = descr[1:-1]
            body["acl-entry"][0]["config"]['description'] = descr
            next_item = len(args)
        else:
            ethertype = args[next_item]
            if ethertype in ethertype_map:
                body["acl-entry"][0]["l2"]["config"]['ethertype'] = ethertype_map[ethertype]
            else:
                ethertype = "0x{:04x}".format(int(args[next_item], base=0))
                body["acl-entry"][0]["l2"]["config"]['ethertype'] = int(ethertype, base=0)
            next_item += 1

    log.log_debug(str(body))
    return acl_client.patch(keypath, body)


def __create_acl_rule_ipv4_ipv6(args):
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set={name},{acl_type}/acl-entries/acl-entry',
                      name=args[0], acl_type=args[1])

    forwarding_action = "ACCEPT" if args[3] == 'permit' else 'DROP'
    log.log_debug('Forwarding action is {}'.format(forwarding_action))

    body = collections.defaultdict()
    if args[1] == 'ACL_IPV4':
        af = 'ipv4'
        body["acl-entry"] = [{
            "sequence-id": int(args[2]),
            "config": {
                "sequence-id": int(args[2])
            },
            "ipv4": {
                "config": {
                }
            },
            "transport": {
                "config": {
                }
            },
            "actions": {
                "config": {
                    "forwarding-action": forwarding_action
                }
            }
        }]
    else:
        af = 'ipv6'
        body["acl-entry"] = [{
            "sequence-id": int(args[2]),
            "config": {
                "sequence-id": int(args[2])
            },
            "ipv6": {
                "config": {
                }
            },
            "transport": {
                "config": {
                }
            },
            "actions": {
                "config": {
                    "forwarding-action": forwarding_action
                }
            }
        }]

    if (args[4] == 'ip' and 'ipv4' == af) or (args[4] == 'ipv6' and 'ipv6' == af):
        protocol = None
    elif args[4] in proto_number_map.keys():
        protocol = proto_number_map.get(args[4])
    else:
        protocol = int(args[4])

    log.log_debug('Protocol is {}'.format(protocol))
    if protocol:
        body["acl-entry"][0][af]["config"]["protocol"] = protocol

    next_item = 6
    if args[5] == 'host':
        try:
            if 'ipv4' == af:
                ipaddress.IPv4Address(args[next_item].decode('utf-8'))
                body["acl-entry"][0][af]["config"]["source-address"] = args[next_item] + '/32'
            else:
                ipaddress.IPv6Address(args[next_item].decode('utf-8'))
                body["acl-entry"][0][af]["config"]["source-address"] = args[next_item] + '/128'
        except ipaddress.AddressValueError:
            print("%Error: Invalid {} address {}".format("IPv4" if 'ipv4' == af else 'IPv6', args[next_item]))
            return
        next_item += 1
    elif args[5] == 'any':
        log.log_debug('No value stored for src ip as any')
    elif '/' in args[5]:
        try:
            if 'ipv4' == af:
                ipaddress.IPv4Network(args[5].decode('utf-8'))
            else:
                ipaddress.IPv6Network(args[5].decode('utf-8'))
            body["acl-entry"][0][af]["config"]["source-address"] = args[5]
        except ipaddress.AddressValueError as e:
            log.log_error(str(e))
            print("%Error: Invalid {} prefix {}".format("IPv4" if 'ipv4' == af else 'IPv6', args[5]))
            return
        except ipaddress.NetmaskValueError as e:
            log.log_error(str(e))
            print("%Error: Invalid mask for {} address {}".format("IPv4" if 'ipv4' == af else 'IPv6', args[5]))
            return
    else:
        print("%Error: Unknown option {}".format(args[5]))
        return

    flags_list = []
    l4_port_type = "source-port"
    while next_item < len(args):
        log.log_debug("{} {}".format(next_item, args[next_item]))
        if args[next_item] == 'eq':
            body["acl-entry"][0]["transport"]["config"][l4_port_type] = int(args[next_item + 1])
            next_item += 2
        elif args[next_item] == 'range':
            begin = int(args[next_item + 1])
            end = int(args[next_item + 2])
            if begin >= end:
                print("%Error: Invalid range. Begin({}) is not lesser than End({})".format(begin, end))
                return
            body["acl-entry"][0]["transport"]["config"][l4_port_type] = "{}..{}".format(begin, end)
            next_item += 3
        elif args[next_item] == 'gt':
            body["acl-entry"][0]["transport"]["config"][l4_port_type] = "{}..65535".format(int(args[next_item + 1]))
            next_item += 2
        elif args[next_item] == 'lt':
            body["acl-entry"][0]["transport"]["config"][l4_port_type] = "0..{}".format(args[next_item + 1])
            next_item += 2
        elif args[next_item] == 'dscp':
            body["acl-entry"][0][af]["config"]["dscp"] = int(args[next_item + 1])
            next_item += 2
        elif args[next_item] in ['fin', 'syn', 'ack', 'urg', 'rst', 'psh']:
            flags_list.append("tcp_{}".format(args[next_item]).upper())
            next_item += 1
        elif args[next_item] == "vlan":
            next_item += 2
        elif args[next_item] == 'type':
            body["acl-entry"][0]["transport"]["config"]["icmp-type"] = int(args[next_item + 1])
            next_item += 2
        elif args[next_item] == 'code':
            body["acl-entry"][0]["transport"]["config"]["icmp-code"] = int(args[next_item + 1])
            next_item += 2
        elif args[next_item] == 'remark':
            descr = " ".join(args[next_item + 1:])
            if descr.startswith('"') and descr.endswith('"'):
                descr = descr[1:-1]
            body["acl-entry"][0]["config"]['description'] = descr
            next_item = len(args)
        else:
            l4_port_type = "destination-port"
            if args[next_item] == 'host':
                try:
                    if 'ipv4' == af:
                        ipaddress.IPv4Address(args[next_item+1].decode('utf-8'))
                        body["acl-entry"][0][af]["config"]["destination-address"] = args[next_item + 1] + '/32'
                    else:
                        ipaddress.IPv6Address(args[next_item+1].decode('utf-8'))
                        body["acl-entry"][0][af]["config"]["destination-address"] = args[next_item + 1] + '/128'
                except ipaddress.AddressValueError:
                    print("%Error: Invalid {} address {}".format("IPv4" if 'ipv4' == af else 'IPv6', args[next_item + 1]))
                    return
                next_item += 2
            elif args[next_item] == 'any':
                next_item += 1
            elif '/' in args[next_item]:
                try:
                    if 'ipv4' == af:
                        ipaddress.IPv4Network(args[next_item].decode('utf-8'))
                    else:
                        ipaddress.IPv6Network(args[next_item].decode('utf-8'))
                    body["acl-entry"][0][af]["config"]["destination-address"] = args[next_item]
                except ipaddress.AddressValueError as e:
                    log.log_error(str(e))
                    print("%Error: Invalid {} address {}".format("IPv4" if 'ipv4' == af else 'IPv6', args[next_item]))
                    return
                except ipaddress.NetmaskValueError as e:
                    log.log_error(str(e))
                    print("%Error: Invalid mask for {} address {}".format("IPv4" if 'ipv4' == af else 'IPv6', args[next_item]))
                    return
                next_item += 1
            else:
                print("%Error: Unknown option {}".format(args[next_item]))
                return

    if bool(flags_list):
        body["acl-entry"][0]["transport"]["config"]["tcp-flags"] = flags_list

    log.log_debug(str(body))
    return acl_client.patch(keypath, body)


def handle_create_acl_rule_request(args):
    if args[1] == 'ACL_L2':
        if args[3] == 'remark':
            return __set_acl_rule_remark(args)
        else:
            return __create_acl_rule_l2(args)
    if args[1] == 'ACL_IPV4' or args[1] == 'ACL_IPV6':
        if args[3] == 'remark':
            return __set_acl_rule_remark(args)
        else:
            return __create_acl_rule_ipv4_ipv6(args)


def handle_delete_acl_request(args):
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set={name},{acl_type}',
                      name=args[0], acl_type=args[1])
    return acl_client.delete(keypath)


def handle_delete_acl_rule_request(args):
    if len(args) == 3:
        keypath = cc.Path(
            '/restconf/data/openconfig-acl:acl/acl-sets/acl-set={name},{acl_type}/acl-entries/acl-entry={sequence_id}',
            name=args[0], acl_type=args[1], sequence_id=args[2])
    else:
        keypath = cc.Path(
            '/restconf/data/openconfig-acl:acl/acl-sets/acl-set={name},{acl_type}/acl-entries/acl-entry={sequence_id}/config/description',
            name=args[0], acl_type=args[1], sequence_id=args[2])
    return acl_client.delete(keypath)


def handle_bind_acl_request(args):
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/interfaces/interface')
    if args[3] == "in":
        body = {"openconfig-acl:interface": [{
            "id": args[2],
            "config": {
                "id": args[2]
            },
            "interface-ref": {
                "config": {
                    "interface": args[2]
                }
            },
            "ingress-acl-sets": {
                "ingress-acl-set": [
                    {
                        "set-name": args[0],
                        "type": args[1],
                        "config": {
                            "set-name": args[0],
                            "type": args[1]
                        }
                    }
                ]
            }
        }]}
    else:
        body = {"interface": [{
            "id": args[2],
            "config": {
                "id": args[2]
            },
            "interface-ref": {
                "config": {
                    "interface": args[2]
                }
            },
            "egress-acl-sets": {
                "egress-acl-set": [
                    {
                        "set-name": args[0],
                        "type": args[1],
                        "config": {
                            "set-name": args[0],
                            "type": args[1]
                        }
                    }
                ]
            }
        }]}

    log.log_debug(str(body))
    return acl_client.patch(keypath, body)


def handle_unbind_acl_request(args):
    if args[3] == 'in':
        keypath = cc.Path('/restconf/data/openconfig-acl:acl/interfaces/interface={id}/ingress-acl-sets/ingress-acl-set={set_name},{acl_type}',
                          id=args[0], set_name=args[1], acl_type=args[2])
    else:
        keypath = cc.Path('/restconf/data/openconfig-acl:acl/interfaces/interface={id}/egress-acl-sets/egress-acl-set={set_name},{acl_type}',
                          id=args[0], set_name=args[1], acl_type=args[2])
    return acl_client.delete(keypath)


def handle_get_acl_details_request(args):
    if len(args) == 1:
        keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets')
    else:
        keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set={name},{acl_type}',
                          name=args[1], acl_type=args[0])
    return acl_client.get(keypath)


def handle_get_all_acl_binding_request(args):
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/interfaces')
    return acl_client.get(keypath)


def set_acl_remark_request(args):
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set={acl_name},{acl_type}/config/description', acl_name=args[0], acl_type=args[1])
    descr = " ".join(args[2:])
    if descr.startswith('"') and descr.endswith('"'):
        descr = descr[1:-1]

    body = {"description": descr}

    return acl_client.patch(keypath, body)


def __set_acl_rule_remark(args):
    keypath = cc.Path(
        '/restconf/data/openconfig-acl:acl/acl-sets/acl-set={acl_name},{acl_type}/acl-entries/acl-entry={sequence_id}/config/description',
        acl_name=args[0], acl_type=args[1], sequence_id=args[2])

    descr = " ".join(args[4:])
    if descr.startswith('"') and descr.endswith('"'):
        descr = descr[1:-1]

    body = {"description": descr}

    return acl_client.patch(keypath, body)


def clear_acl_remark_request(args):
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set={acl_name},{acl_type}/config/description', acl_name=args[0], acl_type=args[1])

    return acl_client.delete(keypath)


def __clear_acl_rule_remark(args):
    keypath = cc.Path(
        '/restconf/data/openconfig-acl:acl/acl-sets/acl-set={acl_name},{acl_type}/acl-entries/acl-entry={sequence_id}/config/description',
        acl_name=args[0], acl_type=args[1], sequence_id=args[2])

    return acl_client.delete(keypath)


def handle_generic_set_response(response, args):
    if response.ok():
        resp_content = response.content
        if resp_content is not None:
            print("{}".format(str(resp_content)))
    else:
        try:
            error_data = response.errors().get('error', list())[0]
            if 'error-app-tag' in error_data and error_data['error-app-tag'] == 'too-many-elements':
                print('Error: Exceeds maximum number of ACL / ACL Rules')
            else:
                print(response.error_message())
        except Exception as e:
            print(response.error_message())


def handle_generic_delete_response(response, args):
    if response.ok():
        resp_content = response.content
        if resp_content is not None:
            print("%Error: {}".format(str(resp_content)))
    elif response.status_code != '404':
        try:
            error_data = response.errors().get('error', list())[0]
            if 'error-app-tag' in error_data and error_data['error-app-tag'] == 'too-many-elements':
                print('Error: Exceeds maximum number of ACL / ACL Rules')
            else:
                print(response.error_message())
        except Exception as e:
            log.log_error(str(e))
            print(response.error_message())


def __convert_ip_protocol_to_user_fmt(proto):
    log.log_debug(proto)
    if isinstance(proto, basestring):
        proto = proto.replace('openconfig-packet-match-types:', '')

    try:
        return proto_number_rev_map[proto]
    except KeyError:
        proto = str(proto)

    try:
        return proto_number_rev_map[proto]
    except KeyError:
        return proto


def __convert_oc_acl_type_to_user_fmt(acl_type):
    if acl_type == 'ACL_L2' or acl_type == 'openconfig-acl:ACL_L2':
        return 'mac'
    elif acl_type == 'ACL_IPV4' or acl_type == 'openconfig-acl:ACL_IPV4':
        return 'ip'
    elif acl_type == 'ACL_IPV6' or acl_type == 'openconfig-acl:ACL_IPV6':
        return 'ipv6'
    else:
        raise RuntimeError("Unknown ACL Type {}".format(acl_type))


def __convert_oc_l4_port_to_user_fmt(l4_port, rule_data):
    if isinstance(l4_port, basestring) and '..' in l4_port:
        l4_port = l4_port.split('..')
        if l4_port[0] == '0':
            rule_data.append('lt')
            rule_data.append(l4_port[1])
        elif l4_port[1] == '65535':
            rule_data.append('gt')
            rule_data.append(l4_port[0])
        else:
            rule_data.append('range')
            rule_data.append(l4_port[0])
            rule_data.append(l4_port[1])
    else:
        rule_data.append('eq')
        rule_data.append(l4_port)


def __convert_ip_addr_to_user_fmt(ip_addr, rule_data, ipv4=True):
    if ipv4:
        pl = '/32'
    else:
        pl = '/128'

    if ip_addr.endswith(pl):
        ip_addr = ip_addr.replace(pl, '')
        rule_data.append('host')
        rule_data.append(ip_addr)
    else:
        rule_data.append(ip_addr)


def __convert_oc_ip_rule_to_user_fmt(acl_entry, rule_data, ipv4=True):
    if ipv4:
        field = 'ipv4'
    else:
        field = 'ipv6'

    try:
        proto = __convert_ip_protocol_to_user_fmt(acl_entry[field]['state']['protocol'])
    except KeyError:
        if ipv4:
            proto = 'ip'
        else:
            proto = 'ipv6'
    rule_data.append(proto)

    try:
        __convert_ip_addr_to_user_fmt(acl_entry[field]['state']['source-address'], rule_data, ipv4)
    except KeyError:
        rule_data.append('any')

    if proto == 'tcp' or proto == 'udp':
        try:
            __convert_oc_l4_port_to_user_fmt(acl_entry['transport']['state']['source-port'], rule_data)
        except KeyError:
            pass

    try:
        __convert_ip_addr_to_user_fmt(acl_entry[field]['state']['destination-address'], rule_data, ipv4)
    except KeyError:
        rule_data.append('any')

    if proto == 'tcp' or proto == 'udp':
        try:
            __convert_oc_l4_port_to_user_fmt(acl_entry['transport']['state']['destination-port'], rule_data)
        except KeyError:
            pass

    try:
        dscp = acl_entry[field]['state']['dscp']
        rule_data.append('dscp')
        rule_data.append(dscp)
    except KeyError:
        pass

    if proto == 'tcp':
        try:
            tcp_flags = acl_entry['transport']['state']['tcp-flags']
            for flag in tcp_flags:
                rule_data.append(flag.replace('openconfig-packet-match-types:TCP_', '').lower())
        except KeyError:
            pass

    if proto == 'icmp' or proto == 'icmpv6':
        try:
            icmp_type = acl_entry['transport']['state']['openconfig-acl-ext:icmp-type']
            rule_data.append('type')
            rule_data.append(icmp_type)
        except KeyError:
            pass

        try:
            icmp_code = acl_entry['transport']['state']['openconfig-acl-ext:icmp-code']
            rule_data.append('code')
            rule_data.append(icmp_code)
        except KeyError:
            pass


def __convert_mac_addr_to_user_fmt(acl_entry, rule_data, field):
    mac = None
    mac_mask = None
    try:
        mac = acl_entry['l2']['state'][field]
        mac_mask = acl_entry['l2']['state'][field + '-mask']
    except KeyError:
        pass

    if mac and mac_mask:
        if mac_mask.lower() == 'ff:ff:ff:ff:ff:ff':
            rule_data.append('host')
            rule_data.append(mac)
        else:
            rule_data.append('{}/{}'.format(mac, mac_mask))
    elif mac:
        rule_data.append('host')
        rule_data.append(mac)
    else:
        rule_data.append('any')


def __convert_l2_rule_to_user_fmt(acl_entry, rule_data):
    __convert_mac_addr_to_user_fmt(acl_entry, rule_data, 'source-mac')
    __convert_mac_addr_to_user_fmt(acl_entry, rule_data, 'destination-mac')

    try:
        ethertype = acl_entry['l2']['state']['ethertype']
        if isinstance(ethertype, basestring):
            ethertype = ethertype.split(':')[-1]
            rule_data.append(ethertype_rev_map[ethertype])
        else:
            ethertype = "{:x}".format(ethertype)
            if ethertype in ethertype_rev_map:
                rule_data.append(ethertype_rev_map[ethertype])
            else:
                rule_data.append('0x' + ethertype)
    except KeyError:
        pass

    try:
        pcp = acl_entry['l2']['state']['openconfig-acl-ext:pcp']
        rule_data.append('pcp')
        if 'openconfig-acl-ext:pcp-mask' in acl_entry['l2']['state']:
            rule_data.append(pcp_rev_map[pcp] + '/' + acl_entry['l2']['state']['openconfig-acl-ext:pcp-mask'])
        else:
            rule_data.append(pcp_rev_map[pcp])
    except KeyError:
        pass

    try:
        dei = acl_entry['l2']['state']['openconfig-acl-ext:dei']
        rule_data.append('dei')
        rule_data.append(dei)
    except KeyError:
        pass


def __parse_acl_entry(data, acl_entry):
    seq_id = acl_entry['sequence-id']
    data[seq_id] = dict()

    try:
        data[seq_id]['packets'] = acl_entry['state']['matched-packets']
        data[seq_id]['octets'] = acl_entry['state']['matched-octets']
    except KeyError:
        pass

    try:
        data[seq_id]['description'] = acl_entry['state']['description']
    except KeyError:
        pass

    rule_data = list()
    if 'openconfig-acl:ACCEPT' == acl_entry['actions']['state']["forwarding-action"]:
        rule_data.append('permit')
    elif 'openconfig-acl:DROP' == acl_entry['actions']['state']["forwarding-action"]:
        rule_data.append('deny')

    if 'ipv4' in acl_entry:
        __convert_oc_ip_rule_to_user_fmt(acl_entry, rule_data)
    elif 'ipv6' in acl_entry:
        __convert_oc_ip_rule_to_user_fmt(acl_entry, rule_data, False)
    elif 'l2' in acl_entry:
        __convert_l2_rule_to_user_fmt(acl_entry, rule_data)

    data[seq_id]['rule_data'] = rule_data


def handle_get_acl_details_response(response, args):
    if response.ok():
        resp_content = response.content
        log.log_debug(json.dumps(resp_content, indent=4))
        if bool(resp_content):
            data = OrderedDict()
            if len(args) == 1:
                log.log_debug('Get details for specific ACL Type {}'.format(args[0]))
                for acl_set in resp_content["openconfig-acl:acl-sets"]["acl-set"]:
                    if not acl_set['type'].endswith(args[0]):
                        continue

                    acl_type = __convert_oc_acl_type_to_user_fmt(acl_set['type'])
                    acl_name = acl_set['name']
                    data[acl_type] = OrderedDict()
                    data[acl_type][acl_name] = OrderedDict()
                    data[acl_type][acl_name]['rules'] = OrderedDict()

                    try:
                        data[acl_type][acl_name]['description'] = acl_set['state']['description']
                    except KeyError:
                        pass

                    try:
                        for acl_entry in acl_set['acl-entries']['acl-entry']:
                            __parse_acl_entry(data[acl_type][acl_name]['rules'], acl_entry)
                    except KeyError:
                        pass
            else:
                log.log_debug('Get details for ACL Type {}::{}'.format(args[0], args[1]))
                acl_type = __convert_oc_acl_type_to_user_fmt(args[0])
                acl_name = args[1]
                data[acl_type] = OrderedDict()
                data[acl_type][acl_name] = OrderedDict()
                data[acl_type][acl_name]['rules'] = OrderedDict()

                acl_set = resp_content['openconfig-acl:acl-set'][0]
                try:
                    data[acl_type][acl_name]['description'] = acl_set['state']['description']
                except KeyError:
                    pass

                try:
                    for acl_entry in acl_set['acl-entries']['acl-entry']:
                        __parse_acl_entry(data[acl_type][acl_name]['rules'], acl_entry)
                except KeyError:
                    pass

            log.log_debug(str(data))
            show_cli_output('show_access_list.j2', data)
    else:
        if response.status_code != 404:
            print(response.error_message())


def handle_get_all_acl_binding_response(response, args):
    render_data = dict()
    log.log_debug(json.dumps(response.content, indent=4))
    if response.ok():
        resp_content = response.content
        if bool(resp_content):
            for intf_data in resp_content["openconfig-acl:interfaces"]["interface"]:
                render_data[intf_data["id"]] = list()
                for direction in ["ingress-acl-set", "egress-acl-set"]:
                    if (direction + "s") in intf_data:
                        for in_acl_data in intf_data[(direction + "s")][direction]:
                            if in_acl_data["type"] == 'openconfig-acl:' + args[0]:
                                if args[0] == 'ACL_L2':
                                    render_data[intf_data["id"]].append(tuple([(direction.split('-')[0]).capitalize(),
                                                                               "MAC", in_acl_data["set-name"]]))
                                elif args[0] == 'ACL_IPV4':
                                    render_data[intf_data["id"]].append(tuple([(direction.split('-')[0]).capitalize(),
                                                                               "IP", in_acl_data["set-name"]]))
                                elif args[0] == 'ACL_IPV6':
                                    render_data[intf_data["id"]].append(tuple([(direction.split('-')[0]).capitalize(),
                                                                               "IPv6", in_acl_data["set-name"]]))

            # TODO Sort the data in the order Eth->Po->Vlan->Switch
            log.log_debug(str(render_data))
            show_cli_output('show_access_group.j2', render_data)
    else:
        if response.status_code != 404:
            print(response.error_message())


request_handlers = {
    'create_acl': handle_create_acl_request,
    'create_acl_rule': handle_create_acl_rule_request,
    'delete_acl': handle_delete_acl_request,
    'delete_acl_rule': handle_delete_acl_rule_request,
    'bind_acl': handle_bind_acl_request,
    'unbind_acl': handle_unbind_acl_request,
    'get_acl_details': handle_get_acl_details_request,
    'get_all_acl_binding': handle_get_all_acl_binding_request,
    'set_acl_remark': set_acl_remark_request,
    'clear_acl_remark': clear_acl_remark_request
}

response_handlers = {
    'create_acl': handle_generic_set_response,
    'create_acl_rule': handle_generic_set_response,
    'delete_acl': handle_generic_delete_response,
    'delete_acl_rule': handle_generic_delete_response,
    'bind_acl': handle_generic_set_response,
    'unbind_acl': handle_generic_delete_response,
    'get_acl_details': handle_get_acl_details_response,
    'get_all_acl_binding': handle_get_all_acl_binding_response,
    'set_acl_remark': handle_generic_set_response,
    'clear_acl_remark': handle_generic_delete_response
}


def run(op_str, args):
    try:
        log.log_debug(str(args))
        resp = request_handlers[op_str](args)
        if resp:
            response_handlers[op_str](resp, args)
    except Exception as e:
        log.log_error(traceback.format_exc())
        print('%Error: Encountered exception "{}"'.format(str(e)))
    return


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2:])
