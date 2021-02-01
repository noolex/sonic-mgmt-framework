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
import collections
from collections import OrderedDict
import cli_client as cc
from scripts.render_cli import show_cli_output
from natsort import natsorted
import ipaddress
import traceback
import json
import cli_log as log
import os
import re


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
dscp_map = {
    "default": 0,
    "cs1": 8,
    "cs2": 16,
    "cs3": 24,
    "cs4": 32,
    "cs5": 40,
    "cs6": 48,
    "cs7": 56,
    "af11": 10,
    "af12": 12,
    "af13": 14,
    "af21": 18,
    "af22": 20,
    "af23": 22,
    "af31": 26,
    "af32": 28,
    "af33": 30,
    "af41": 34,
    "af42": 36,
    "af43": 38,
    "ef": 46,
    "voice-admit": 44,
}

TCP_FLAGS_LIST = ["fin", "not-fin", "syn", "not-syn", "rst", "not-rst", "psh", "not-psh", "ack", "not-ack", "urg",
                  "not-urg", "ece", "not-ece", "cwr", "not-cwr"]
TCP_FLAG_VALUES = {"fin": 1, "syn": 2, "rst": 4, "psh": 8, "ack": 16, "urg": 32, "ece": 64, "cwr": 128}
TCP_FLAG_VALUES_REV = {}

proto_number_rev_map = {val: key for key, val in proto_number_map.items()}
ethertype_rev_map = {val: key for key, val in ethertype_map.items()}
pcp_rev_map = {val: key for key, val in pcp_map.items()}
dscp_rev_map = {val: key for key, val in dscp_map.items()}
acl_client = cc.ApiClient()
for tcp_flag, tcp_flag_val in TCP_FLAG_VALUES.items():
    TCP_FLAG_VALUES_REV[tcp_flag_val] = tcp_flag


class SonicAclCLIError(RuntimeError):
    """Indicates CLI processing errors that needs to be displayed to user"""
    pass


class SonicACLCLIStopNoError(RuntimeError):
    """Indicates that CLI processing should be stopped. No error will be displayed to user"""
    pass


def acl_natsort_intf_prio(ifname):
    if isinstance(ifname, tuple):
        ifname = ifname[0]
    if '.' not in ifname:
        if ifname.startswith('Ethernet'):
            prio = 310000 + int(ifname.replace('Ethernet', ''), 0)
        elif ifname.startswith('Eth'):
            portnum = ifname.replace('Eth', '')
            parts = portnum.split('/')
            # Ideally slot on Pizzabox is supposed to be 0. Just in case its changed in future
            slot=int(parts[0])+1
            port=int(parts[1])
            try:
                breakout = int(parts[2])
            except IndexError:
                breakout = 1
            prio = 310000 + slot*(port*16 + breakout)
        elif ifname.startswith('PortChannel'):
            prio = 320000 + int(ifname.replace('PortChannel', ''), 0)
        elif ifname.startswith('Vlan'):
            prio = 330000 + int(ifname.replace('Vlan', ''), 0)
        elif ifname == "Switch":
            prio = 340000
        else:
            prio = 350000
    else:
        #sub-interfaces
        if ifname.startswith('Ethernet'):
            portnum = ifname.replace('Ethernet', '').split('.')
            prio = 10000 + 250*int(portnum[1]) + int(portnum[0])
        elif ifname.startswith('Eth'):
            portnum = ifname.replace('Eth', '')
            parts = portnum.split('/')
            slot=int(parts[0])
            if '.' in parts[1]:
                ports = parts[1].split('.')
                port = int(ports[0])
                breakout = 1
            else:
                port = int(parts[1])
                try:
                    ports = parts[2].split('.')
                    breakout = int(ports[0])
                except IndexError:
                    breakout = 1
            prio = 10000 + slot*(250*(port*8 + breakout) + int(ports[1]))
        elif ifname.startswith('PortChannel'):
            portnum = ifname.replace('PortChannel', '').split('.')
            prio = 150000 + 250*int(portnum[1]) + int(portnum[0])

    return prio


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


def __convert_oc_fwd_action_to_user(action):
    if ":" in action:
        action = action.split(":")[-1]

    if action == "ACCEPT":
        return "permit"
    if action == "DROP":
        return "deny"
    if action == "DISCARD":
        return "discard"
    if action == "TRANSIT":
        return "transit"
    if action == "DENY":
        return "DROP"
    if action == "DO_NOT_NAT":
        return "do-not-nat"

    raise SonicAclCLIError("Internal error. Unsupported action")


def __convert_user_fwd_action_to_oc(action):
    if action == "permit":
        return "ACCEPT"
    if action == "discard":
        return "DISCARD"
    if action == "deny":
        return "DROP"
    if action == "transit":
        return "TRANSIT"
    if action == "do-not-nat":
        return "DO_NOT_NAT"

    raise SonicAclCLIError("Internal error. Unsupported action")


def __create_acl_rule_l2(args):
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set={name},{acl_type}/acl-entries',
                      name=args[0], acl_type=args[1])

    body = collections.defaultdict()
    body["openconfig-acl:acl-entry"] = [{
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
                "forwarding-action": __convert_user_fwd_action_to_oc(args[3])
            }
        }
    }]

    if args[4] == 'host':
        body["openconfig-acl:acl-entry"][0]["l2"]["config"]["source-mac"] = __format_mac_addr(args[5])
        next_item = 6
    elif args[4] == 'any':
        next_item = 5
    else:
        body["openconfig-acl:acl-entry"][0]["l2"]["config"]["source-mac"] = __format_mac_addr(args[4])
        body["openconfig-acl:acl-entry"][0]["l2"]["config"]["source-mac-mask"] = __format_mac_addr(args[5])
        next_item = 6

    if args[next_item] == 'host':
        body["openconfig-acl:acl-entry"][0]["l2"]["config"]["destination-mac"] = __format_mac_addr(args[next_item + 1])
        next_item += 2
    elif args[next_item] == 'any':
        next_item += 1
    else:
        body["openconfig-acl:acl-entry"][0]["l2"]["config"]["destination-mac"] = __format_mac_addr(args[next_item])
        body["openconfig-acl:acl-entry"][0]["l2"]["config"]["destination-mac-mask"] = __format_mac_addr(args[next_item + 1])
        next_item += 2

    while next_item < len(args):
        if args[next_item] == 'pcp':
            if args[next_item + 1] in pcp_map:
                body["openconfig-acl:acl-entry"][0]["l2"]["config"]['pcp'] = pcp_map[args[next_item + 1]]
                next_item += 2
            else:
                body["openconfig-acl:acl-entry"][0]["l2"]["config"]['pcp'] = int(args[next_item + 1])
                next_item += 2
        elif args[next_item] == 'pcp-mask':
            mask = int(args[next_item + 1])
            body["openconfig-acl:acl-entry"][0]["l2"]["config"]['pcp-mask'] = mask
            next_item = next_item + 2
        elif args[next_item] == 'dei':
            body["openconfig-acl:acl-entry"][0]["l2"]["config"]['dei'] = int(args[next_item + 1])
            next_item += 2
        elif args[next_item] == 'vlan':
            body["openconfig-acl:acl-entry"][0]["l2"]["config"]['vlanid'] = int(args[next_item + 1])
            next_item += 2
        elif args[next_item] == 'remark':
            full_cmd = os.getenv('USER_COMMAND', None)
            match = re.search('remark (["]?.*["]?)', full_cmd)
            if match:
                body["openconfig-acl:acl-entry"][0]["config"]['description'] = match.group(1)
            next_item = len(args)
        else:
            ethertype = args[next_item]
            if ethertype in ethertype_map:
                body["openconfig-acl:acl-entry"][0]["l2"]["config"]['ethertype'] = ethertype_map[ethertype]
            else:
                ethertype = "0x{:04x}".format(int(args[next_item], base=0))
                body["openconfig-acl:acl-entry"][0]["l2"]["config"]['ethertype'] = int(ethertype, base=0)
            next_item += 1

    log.log_debug(str(body))
    return acl_client.post(keypath, body)


def __create_acl_rule_ipv4_ipv6(args):
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set={name},{acl_type}/acl-entries',
                      name=args[0], acl_type=args[1])

    body = collections.defaultdict()
    if args[1] == 'ACL_IPV4':
        af = 'ipv4'
        body["openconfig-acl:acl-entry"] = [{
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
                    "forwarding-action": __convert_user_fwd_action_to_oc(args[3])
                }
            }
        }]
    else:
        af = 'ipv6'
        body["openconfig-acl:acl-entry"] = [{
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
                    "forwarding-action": __convert_user_fwd_action_to_oc(args[3])
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
    if protocol is not None:
        body["openconfig-acl:acl-entry"][0][af]["config"]["protocol"] = protocol

    next_item = 6
    if args[5] == 'host':
        try:
            if 'ipv4' == af:
                ipaddress.IPv4Address(args[next_item].decode('utf-8'))
                body["openconfig-acl:acl-entry"][0][af]["config"]["source-address"] = args[next_item] + '/32'
            else:
                ipaddress.IPv6Address(args[next_item].decode('utf-8'))
                body["openconfig-acl:acl-entry"][0][af]["config"]["source-address"] = args[next_item] + '/128'
        except ipaddress.AddressValueError:
            raise SonicAclCLIError("Invalid {} address {}".format("IPv4" if 'ipv4' == af else 'IPv6', args[next_item]))
        next_item += 1
    elif args[5] == 'any':
        log.log_debug('No value stored for src ip as any')
    elif '/' in args[5]:
        try:
            if 'ipv4' == af:
                ipaddress.IPv4Network(args[5].decode('utf-8'))
            else:
                ipaddress.IPv6Network(args[5].decode('utf-8'))
            body["openconfig-acl:acl-entry"][0][af]["config"]["source-address"] = args[5]
        except ipaddress.AddressValueError as e:
            log.log_error(str(e))
            raise SonicAclCLIError("Invalid {} prefix {}".format("IPv4" if 'ipv4' == af else 'IPv6', args[5]))
        except ipaddress.NetmaskValueError as e:
            log.log_error(str(e))
            raise SonicAclCLIError("Invalid mask for {} address {}".format("IPv4" if 'ipv4' == af else 'IPv6', args[5]))
        except ValueError as e:
            log.log_error(str(e))
            raise SonicAclCLIError("{}. Please fix the {} address or prefix length".format(str(e), "IPv4" if 'ipv4' == af else 'IPv6'))

    else:
        raise SonicAclCLIError("Unknown option {}".format(args[5]))

    flags_list = []
    l4_port_type = "source-port"
    while next_item < len(args):
        log.log_debug("{} {}".format(next_item, args[next_item]))
        if args[next_item] == 'eq':
            body["openconfig-acl:acl-entry"][0]["transport"]["config"][l4_port_type] = int(args[next_item + 1])
            next_item += 2
        elif args[next_item] == 'range':
            begin = int(args[next_item + 1])
            end = int(args[next_item + 2])
            if begin >= end:
                raise SonicAclCLIError("Invalid range. Begin({}) is not lesser than End({})".format(begin, end))
            body["openconfig-acl:acl-entry"][0]["transport"]["config"][l4_port_type] = "{}..{}".format(begin, end)
            next_item += 3
        elif args[next_item] == 'gt':
            body["openconfig-acl:acl-entry"][0]["transport"]["config"][l4_port_type] = "{}..65535".format(int(args[next_item + 1]))
            next_item += 2
        elif args[next_item] == 'lt':
            body["openconfig-acl:acl-entry"][0]["transport"]["config"][l4_port_type] = "0..{}".format(args[next_item + 1])
            next_item += 2
        elif args[next_item] == 'dscp':
            body["openconfig-acl:acl-entry"][0][af]["config"]["dscp"] = int(args[next_item + 1]) if args[next_item + 1] not in dscp_map else dscp_map[args[next_item + 1]]
            next_item += 2
        elif args[next_item] in TCP_FLAGS_LIST:
            flags_list.append("tcp_{}".format(args[next_item]).upper().replace('-', '_'))
            next_item += 1
        elif args[next_item] == "established":
            body["openconfig-acl:acl-entry"][0]["transport"]["config"]["tcp-session-established"] = True
            next_item += 1
        elif args[next_item] == "vlan":
            body["openconfig-acl:acl-entry"][0]["l2"] = {}
            body["openconfig-acl:acl-entry"][0]["l2"]['config'] = {}
            body["openconfig-acl:acl-entry"][0]["l2"]['config']['vlanid'] = int(args[next_item + 1])
            next_item += 2
        elif args[next_item] == 'type':
            body["openconfig-acl:acl-entry"][0]["transport"]["config"]["icmp-type"] = int(args[next_item + 1])
            next_item += 2
        elif args[next_item] == 'code':
            body["openconfig-acl:acl-entry"][0]["transport"]["config"]["icmp-code"] = int(args[next_item + 1])
            next_item += 2
        elif args[next_item] == 'remark':
            full_cmd = os.getenv('USER_COMMAND', None)
            match = re.search('remark (["]?.*["]?)', full_cmd)
            if match:
                body["openconfig-acl:acl-entry"][0]["config"]['description'] = match.group(1)
            next_item = len(args)
        else:
            l4_port_type = "destination-port"
            if args[next_item] == 'host':
                try:
                    if 'ipv4' == af:
                        ipaddress.IPv4Address(args[next_item+1].decode('utf-8'))
                        body["openconfig-acl:acl-entry"][0][af]["config"]["destination-address"] = args[next_item + 1] + '/32'
                    else:
                        ipaddress.IPv6Address(args[next_item+1].decode('utf-8'))
                        body["openconfig-acl:acl-entry"][0][af]["config"]["destination-address"] = args[next_item + 1] + '/128'
                except ipaddress.AddressValueError:
                    raise SonicAclCLIError("Invalid {} address {}".format("IPv4" if 'ipv4' == af else 'IPv6', args[next_item + 1]))
                next_item += 2
            elif args[next_item] == 'any':
                next_item += 1
            elif '/' in args[next_item]:
                try:
                    if 'ipv4' == af:
                        ipaddress.IPv4Network(args[next_item].decode('utf-8'))
                    else:
                        ipaddress.IPv6Network(args[next_item].decode('utf-8'))
                    body["openconfig-acl:acl-entry"][0][af]["config"]["destination-address"] = args[next_item]
                except ipaddress.AddressValueError as e:
                    log.log_error(str(e))
                    raise SonicAclCLIError("Invalid {} address {}".format("IPv4" if 'ipv4' == af else 'IPv6', args[next_item]))
                except ipaddress.NetmaskValueError as e:
                    log.log_error(str(e))
                    raise SonicAclCLIError("Invalid mask for {} address {}".format("IPv4" if 'ipv4' == af else 'IPv6', args[next_item]))
                next_item += 1
            else:
                raise SonicAclCLIError("Unknown option {}".format(args[next_item]))

    if bool(flags_list):
        body["openconfig-acl:acl-entry"][0]["transport"]["config"]["tcp-flags"] = flags_list

    log.log_debug(str(body))
    return acl_client.post(keypath, body)


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


def __handle_interface_acl_bind_request(args):
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/interfaces/interface={id}', id=args[2])
    # PortChannel subinterface contains an extra argument after interface id - parent interface.
    if len(args) > 4 and '.' in args[2]:
        direction = args[4]
    else:
        direction = args[3]

    if direction == "in":
        body = {
            "openconfig-acl:config": {
                "id": args[2]
            },
            "openconfig-acl:interface-ref": {
                "config": {
                    "interface": args[2]
                }
            },
            "openconfig-acl:ingress-acl-sets": {
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
            }}
    else:
        body = {
            "openconfig-acl:config": {
                "id": args[2]
            },
            "openconfig-acl:interface-ref": {
                "config": {
                    "interface": args[2]
                }
            },
            "openconfig-acl:egress-acl-sets": {
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
            }}

    log.log_debug(str(body))
    return acl_client.post(keypath, body)


def __handle_global_ctrl_plane_acl_bind_request(args):
    if args[3] == "in":
        if args[2] == "Switch":
            keypath = cc.Path(
                '/restconf/data/openconfig-acl:acl/openconfig-acl-ext:global/ingress-acl-sets')
        else:
            keypath = cc.Path(
                '/restconf/data/openconfig-acl:acl/openconfig-acl-ext:control-plane/ingress-acl-sets')

        body = {
            "openconfig-acl-ext:ingress-acl-set": [
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
    else:
        if args[2] == "Switch":
            keypath = cc.Path(
                '/restconf/data/openconfig-acl:acl/openconfig-acl-ext:global/egress-acl-sets')
        else:
            raise SonicAclCLIError("Control Plane ACLs not supported at egress")

        body = {
            "openconfig-acl-ext:egress-acl-set": [
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

    log.log_debug(str(body))
    return acl_client.post(keypath, body)


def handle_bind_acl_request(args):
    if args[2] == "Switch" or args[2] == "ControlPlane":
        return __handle_global_ctrl_plane_acl_bind_request(args)
    else:
        return __handle_interface_acl_bind_request(args)


def handle_unbind_acl_request(args):
    if args[2] == "Switch":
        if args[3] == 'in':
            keypath = cc.Path('/restconf/data/openconfig-acl:acl/openconfig-acl-ext:global/ingress-acl-sets/ingress-acl-set={set_name},{acl_type}',
                              set_name=args[0], acl_type=args[1])
        else:
            keypath = cc.Path('/restconf/data/openconfig-acl:acl/openconfig-acl-ext:global/egress-acl-sets/egress-acl-set={set_name},{acl_type}',
                              set_name=args[0], acl_type=args[1])
    elif args[2] == "ControlPlane":
        if args[3] == 'in':
            keypath = cc.Path('/restconf/data/openconfig-acl:acl/openconfig-acl-ext:control-plane/ingress-acl-sets/ingress-acl-set={set_name},{acl_type}',
                              set_name=args[0], acl_type=args[1])
        else:
            keypath = cc.Path('/restconf/data/openconfig-acl:acl/openconfig-acl-ext:control-plane/egress-acl-sets/egress-acl-set={set_name},{acl_type}',
                              set_name=args[0], acl_type=args[1])
    else:
        # PortChannel subinterface contains an extra argument after interface id - parent interface.
        if len(args) > 4 and '.' in args[2]:
            direction = args[4]
        else:
            direction = args[3]
        if direction == 'in':
            keypath = cc.Path('/restconf/data/openconfig-acl:acl/interfaces/interface={id}/ingress-acl-sets/ingress-acl-set={set_name},{acl_type}',
                              id=args[2], set_name=args[0], acl_type=args[1])
        else:
            keypath = cc.Path('/restconf/data/openconfig-acl:acl/interfaces/interface={id}/egress-acl-sets/egress-acl-set={set_name},{acl_type}',
                              id=args[2], set_name=args[0], acl_type=args[1])

    return acl_client.delete(keypath)


def handle_get_acl_details_request(args):
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/state/counter-capability')
    resp = acl_client.get(keypath, depth=None, ignore404=False)
    if resp.ok():
        counter_mode = resp.content["openconfig-acl:counter-capability"].split(":")[1]
    else:
        raise SonicAclCLIError("Unable to get ACL Counter mode")

    if len(args) == 1:
        if counter_mode == "AGGREGATE_ONLY":
            keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets')
            response = acl_client.get(keypath, depth=None, ignore404=False)
        else:
            keypath = cc.Path('/restconf/data/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST')
            response = acl_client.get(keypath, depth=None, ignore404=False)
    elif len(args) == 2:
        if counter_mode == "AGGREGATE_ONLY":
            keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set={name},{acl_type}', name=args[1], acl_type=args[0])
            response = acl_client.get(keypath, depth=None, ignore404=False)
        else:
            keypath = cc.Path('/restconf/data/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST={aclname}', aclname=args[1])
            response = acl_client.get(keypath, depth=None, ignore404=False)
    else:
        if counter_mode != "INTERFACE_ONLY":
            raise SonicAclCLIError("Per interface counter mode not set")
        keypath = cc.Path('/restconf/data/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST={aclname}', aclname=args[1])
        response = acl_client.get(keypath, depth=None, ignore404=False)

    response.counter_mode = counter_mode
    return response


def handle_get_all_acl_binding_request(args):
    keypath = cc.Path('/restconf/data/sonic-acl:sonic-acl/ACL_BINDING_TABLE/ACL_BINDING_TABLE_LIST')
    return acl_client.get(keypath, depth=None, ignore404=False)


def set_acl_remark_request(args):
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set={acl_name},{acl_type}/config/description',
                      acl_name=args[0], acl_type=args[1])
    full_cmd = os.getenv('USER_COMMAND', None)
    match = re.search('remark (["]?.*["]?)', full_cmd)
    if match:
        body = {"description": match.group(1)}
        return acl_client.patch(keypath, body)


def __set_acl_rule_remark(args):
    keypath = cc.Path(
        '/restconf/data/openconfig-acl:acl/acl-sets/acl-set={acl_name},{acl_type}/acl-entries/acl-entry={sequence_id}/config/description',
        acl_name=args[0], acl_type=args[1], sequence_id=args[2])

    full_cmd = os.getenv('USER_COMMAND', None)
    match = re.search('remark (["]?.*["]?)', full_cmd)
    if match:
        body = {"description": match.group(1)}

        return acl_client.patch(keypath, body)


def clear_acl_remark_request(args):
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set={acl_name},{acl_type}/config/description',
                      acl_name=args[0], acl_type=args[1])

    return acl_client.delete(keypath)


def __clear_acl_rule_remark(args):
    keypath = cc.Path(
        '/restconf/data/openconfig-acl:acl/acl-sets/acl-set={acl_name},{acl_type}/acl-entries/acl-entry={sequence_id}/config/description',
        acl_name=args[0], acl_type=args[1], sequence_id=args[2])

    return acl_client.delete(keypath)


def clear_acl_counters_request(args):
    path = cc.Path('/restconf/operations/sonic-acl:clear-acl-counters')

    if len(args) == 1:
        body = {"sonic-acl:input": {"type": args[0]}}
    elif len(args) == 2:
        body = {"sonic-acl:input": {"aclname": args[1], "type": args[0]}}
    else:
        intf_name = args[2] if len(args) == 3 else "".join(args[3:])
        body = {"sonic-acl:input": {"aclname": args[1], "type": args[0], "ifname": intf_name}}

    return acl_client.post(path, body)


def set_counter_mode_request(args):
    keypath = cc.Path("/restconf/data/openconfig-acl:acl/config/openconfig-acl-ext:counter-capability")
    if args[0] == 'per-entry':
        body = {"openconfig-acl-ext:counter-capability": "AGGREGATE_ONLY"}
    else:
        body = {"openconfig-acl-ext:counter-capability": "INTERFACE_ONLY"}

    return acl_client.patch(keypath, body)


def handle_generic_set_response(response, op_str, args):
    if response.ok():
        resp_content = response.content
        if resp_content is not None:
            print("{}".format(str(resp_content)))
    else:
        try:
            error_data = response.errors().get('error', list())[0]
            if 'error-app-tag' in error_data:
                if error_data['error-app-tag'] == 'too-many-elements':
                    print('%Error: Exceeds maximum number of ACL / ACL Rules.')
                elif error_data['error-app-tag'] == 'counters-in-use':
                    print('%Error: ACL Counter mode update is not allowed when ACLs are applied to interfaces.')
                elif error_data['error-app-tag'] == 'update-not-allowed':
                    print("%Error: Creating ACLs with same name and different type not allowed")
                elif error_data['error-app-tag'] != 'same-config-exists':
                    print(response.error_message())
                else:
                    return 0
            else:
                print(response.error_message())
            return -1
        except Exception as e:
            log.log_error(str(e))
            print(response.error_message())
            return -1

    return 0


def handle_generic_delete_response(response, op_str, args):
    if response.ok():
        resp_content = response.content
        if resp_content is not None:
            raise SonicAclCLIError("{}".format(str(resp_content)))
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


def __convert_oc_acl_type_to_sonic_fmt(acl_type):
    if acl_type == 'ACL_L2' or acl_type == 'openconfig-acl:ACL_L2':
        return 'L2'
    elif acl_type == 'ACL_IPV4' or acl_type == 'openconfig-acl:ACL_IPV4':
        return 'L3'
    elif acl_type == 'ACL_IPV6' or acl_type == 'openconfig-acl:ACL_IPV6':
        return 'L3V6'
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


def convert_ip_addr_to_user_fmt(ip_addr, ipv4=True):
    if ipv4:
        pl = '/32'
    else:
        pl = '/128'

    if ip_addr.endswith(pl):
        ip_addr = ip_addr.replace(pl, '')
        return "host {}".format(ip_addr).lower()
    else:
        return ip_addr.lower()


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
        rule_data.append(convert_ip_addr_to_user_fmt(acl_entry[field]['state']['source-address'], ipv4))
    except KeyError:
        rule_data.append('any')

    if proto == 'tcp' or proto == 'udp':
        try:
            __convert_oc_l4_port_to_user_fmt(acl_entry['transport']['state']['source-port'], rule_data)
        except KeyError:
            pass

    try:
        rule_data.append(convert_ip_addr_to_user_fmt(acl_entry[field]['state']['destination-address'], ipv4))
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
        rule_data.append(dscp_rev_map.get(dscp, dscp))
    except KeyError:
        pass

    if proto == 'tcp':
        try:
            established = acl_entry['transport']['state']['openconfig-acl-ext:tcp-session-established']
            rule_data.append('established')
        except KeyError:
            pass

        try:
            tcp_flags = acl_entry['transport']['state']['tcp-flags']
            for flag in tcp_flags:
                rule_data.append(flag.split(":")[1].replace('TCP_', '').lower().replace("_", "-"))
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


def __convert_oc_mac_addr_to_user_fmt(acl_entry, rule_data, field):
    mac = None
    mac_mask = None
    try:
        mac = acl_entry['l2']['state'][field]
        mac = mac.lower()
        mac_mask = acl_entry['l2']['state'][field + '-mask']
        mac_mask = mac_mask.lower()
    except KeyError:
        pass

    if mac and mac_mask:
        if mac_mask.lower() == 'ff:ff:ff:ff:ff:ff':
            rule_data.append('host')
            rule_data.append(mac)
        else:
            rule_data.append('{} {}'.format(mac, mac_mask))
    elif mac:
        rule_data.append('host')
        rule_data.append(mac)
    else:
        rule_data.append('any')


def __convert_l2_rule_to_user_fmt(acl_entry, rule_data):
    __convert_oc_mac_addr_to_user_fmt(acl_entry, rule_data, 'source-mac')
    __convert_oc_mac_addr_to_user_fmt(acl_entry, rule_data, 'destination-mac')

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
        if 'openconfig-acl-ext:pcp-mask' in acl_entry['l2']['state']:
            rule_data.append('pcp {} pcp-mask {}'.format(pcp_rev_map[pcp], acl_entry['l2']['state']['openconfig-acl-ext:pcp-mask']))
        else:
            rule_data.append('pcp {}'.format(pcp_rev_map[pcp]))
    except KeyError:
        pass

    try:
        dei = acl_entry['l2']['state']['openconfig-acl-ext:dei']
        rule_data.append('dei')
        rule_data.append(dei)
    except KeyError:
        pass


def __parse_acl_entry(data, acl_entry, acl_type):
    seq_id = acl_entry['sequence-id']
    data[seq_id] = dict()

    log.log_debug("Parse {} rule {}".format(acl_type, str(acl_entry)))
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
    rule_data.append(__convert_oc_fwd_action_to_user(acl_entry['actions']['state']["forwarding-action"]))

    if 'ip' == acl_type:
        __convert_oc_ip_rule_to_user_fmt(acl_entry, rule_data)
    elif 'ipv6' == acl_type:
        __convert_oc_ip_rule_to_user_fmt(acl_entry, rule_data, False)
    elif 'mac' == acl_type:
        __convert_l2_rule_to_user_fmt(acl_entry, rule_data)

    try:
        vlanid = acl_entry['l2']['state']['openconfig-acl-ext:vlanid']
        rule_data.append('vlan')
        rule_data.append(vlanid)
    except KeyError:
        pass

    data[seq_id]['rule_data'] = rule_data


def __convert_oc_acl_set_to_user_fmt(acl_set, data):
    acl_name = acl_set['name']
    acl_type = __convert_oc_acl_type_to_user_fmt(acl_set['type'])
    if not data.get(acl_type, None):
        data[acl_type] = OrderedDict()
    data[acl_type][acl_name] = OrderedDict()
    data[acl_type][acl_name]['rules'] = OrderedDict()

    try:
        data[acl_type][acl_name]['description'] = acl_set['state']['description']
    except KeyError:
        pass

    try:
        temp_rules = dict()
        for acl_entry in acl_set['acl-entries']['acl-entry']:
            __parse_acl_entry(temp_rules, acl_entry, acl_type)

        rules_key_list = temp_rules.keys()
        rules_key_list.sort()
        for k in rules_key_list:
            data[acl_type][acl_name]['rules'][k] = temp_rules[k]
    except KeyError:
        pass


def __handle_get_acl_details_aggregate_mode_response(resp_content, args):
    log.log_debug(json.dumps(resp_content, indent=4))
    if bool(resp_content):
        data = OrderedDict()
        if len(args) == 1:
            log.log_debug('Get details for specific ACL Type {}'.format(args[0]))
            acl_type = __convert_oc_acl_type_to_user_fmt(args[0])
            data[acl_type] = OrderedDict()

            for acl_set in resp_content["openconfig-acl:acl-sets"]["acl-set"]:
                if not acl_set['type'].endswith(args[0]):
                    continue

                __convert_oc_acl_set_to_user_fmt(acl_set, data)
        else:
            log.log_debug('Get details for ACL Type {}::{}'.format(args[0], args[1]))
            __convert_oc_acl_set_to_user_fmt(resp_content['openconfig-acl:acl-set'][0], data)

        log.log_debug(str(data))
        show_cli_output('show_access_list.j2', data)


def __deep_copy(dst, src):
    for key, value in src.items():
        if isinstance(value, dict):
            node = dst.setdefault(key, {})
            __deep_copy(node, value)
        else:
            dst[key] = value
    return dst


def __get_and_show_acl_counters_by_name_and_intf(acl_name, acl_type, intf_name, stage, cache, continuation):
    log.log_debug('ACL:{} Type:{} Intf:{} Stage:{}'.format(acl_name, acl_type, intf_name, stage))
    acl_name = acl_name.replace("_" + acl_type, "")
    output = OrderedDict()
    if cache is None or cache.get(acl_name, None) is None:
        log.log_debug("No Cache present")
        keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set={name},{acl_type}',
                          name=acl_name, acl_type=acl_type)
        response = acl_client.get(keypath, depth=None, ignore404=False)
        if response.ok():
            log.log_debug(response.content)
            __convert_oc_acl_set_to_user_fmt(response.content['openconfig-acl:acl-set'][0], output)
            temp = OrderedDict()
            __deep_copy(temp, output)
            if cache:
                cache[acl_name] = temp
        else:
            log.log_error("Error pulling ACL config for {}:{}".format(acl_name, acl_type))
            raise SonicAclCLIError("{}".format(response.error_message()))
    else:
        log.log_debug("Cache present")
        __deep_copy(output, cache[acl_name])

    user_acl_type = __convert_oc_acl_type_to_user_fmt(acl_type)
    output[user_acl_type][acl_name]['stage'] = stage.capitalize()
    if intf_name != "CtrlPlane":
        keypath = cc.Path('/restconf/data/openconfig-acl:acl/interfaces/interface={id}/{stage}-acl-sets/{stage}-acl-set={setname},{acltype}',
                          id=intf_name, stage=stage.lower(), setname=acl_name, acltype=acl_type)
        response = acl_client.get(keypath, depth=None, ignore404=False)
        if not response.ok():
            raise SonicAclCLIError("{}".format(response.error_message()))

        log.log_debug(response.content)
        acl_set = response.content['openconfig-acl:{}-acl-set'.format(stage.lower())][0]
        user_acl_type = __convert_oc_acl_type_to_user_fmt(acl_set['type'])
        output[user_acl_type][acl_name]['stage'] = stage.capitalize()
        for acl_entry in acl_set['acl-entries']['acl-entry']:
            output[user_acl_type][acl_name]['rules'][acl_entry['sequence-id']]['packets'] = acl_entry['state']['matched-packets']
            output[user_acl_type][acl_name]['rules'][acl_entry['sequence-id']]['octets'] = acl_entry['state']['matched-octets']

    render_dict = dict()
    if intf_name != "Switch":
        render_dict["interface {}".format(intf_name)] = output
    else:
        render_dict[intf_name] = output

    if show_cli_output('show_access_list_intf.j2', render_dict, continuation=continuation):
        raise SonicACLCLIStopNoError


def __process_acl_counters_request_by_name_and_inf(response, args):
    acl_type = __convert_oc_acl_type_to_sonic_fmt(args[0])
    acl_data = response["sonic-acl:ACL_TABLE_LIST"]
    if not bool(acl_data):
        raise SonicAclCLIError("ACL not found")

    acl_data = acl_data[0]
    if acl_type != acl_data["type"].upper():
        raise SonicAclCLIError("ACL is not of type {}".format(__convert_oc_acl_type_to_user_fmt(args[0])))

    stage = acl_data.get("stage", "INGRESS")
    ports = acl_data.get("ports", [])
    intf_name = args[2] if len(args) == 3 else "".join(args[3:])
    if intf_name in ports:
        __get_and_show_acl_counters_by_name_and_intf(acl_data["aclname"], args[0], intf_name, stage, None, False)
    else:
        raise SonicAclCLIError("ACL {} not applied to {}".format(args[1], intf_name))


def __process_acl_counters_request_by_type_and_name(response, args):
    acl_type = __convert_oc_acl_type_to_sonic_fmt(args[0])
    if not bool(response):
        raise SonicAclCLIError("ACL not found")

    acl_data = response["sonic-acl:ACL_TABLE_LIST"]
    if not bool(acl_data):
        raise SonicAclCLIError("ACL not found")

    acl_data = acl_data[0]
    if acl_type != acl_data["type"].upper():
        raise SonicAclCLIError("ACL is not of type {}".format(__convert_oc_acl_type_to_user_fmt(args[0])))

    cache = dict()
    stage = acl_data.get("stage", "INGRESS")
    ports = acl_data.get("ports", [])
    if len(ports) != 0:
        # Sort and show 
        ports = natsorted(ports, key=acl_natsort_intf_prio)
        log.log_debug("ACL {} Type {} has ports.".format(acl_data["aclname"], acl_type))
        cont = False
        for port in ports:
            __get_and_show_acl_counters_by_name_and_intf(acl_data["aclname"], args[0], port, stage, cache, cont)
            cont = True
    else:
        log.log_debug("ACL {} Type {} has ZERO ports. Show only ACL configuration.".format(acl_data["aclname"], acl_type))
        keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set={name},{acl_type}', name=args[1], acl_type=args[0])
        response = acl_client.get(keypath, depth=None, ignore404=False)
        if response.ok():
            __handle_get_acl_details_aggregate_mode_response(response.content, args)
        else:
            print(response.error_message())
            return


def __process_acl_counters_request_by_type(response, args):
    acl_type = __convert_oc_acl_type_to_sonic_fmt(args[0])

    filtered_acls = []
    for acl_data in response["sonic-acl:ACL_TABLE_LIST"]:
        if acl_type == acl_data["type"].upper():
            filtered_acls.append(acl_data)
            log.log_debug("ACL {} is of type {}. Add to list".format(acl_data["aclname"], acl_type))
        else:
            log.log_debug("ACL {} is not of type {}. Skip".format(acl_data["aclname"], acl_type))

    cache = dict()
    for acl in filtered_acls:
        stage = acl.get("stage", "INGRESS")
        ports = acl.get("ports", [])
        if len(ports) != 0:
            # Sort and show 
            ports = natsorted(ports, key=acl_natsort_intf_prio)
            log.log_debug("ACL {} Type {} has ports.".format(acl["aclname"], acl_type))
            cont = False
            for port in ports:
                __get_and_show_acl_counters_by_name_and_intf(acl["aclname"], args[0], port, stage, cache, cont)
                cont = True
        else:
            log.log_debug("ACL {} Type {} has ZERO ports. Show only ACL configuration.".format(acl["aclname"], acl_type))

            acl_name = acl["aclname"].replace("_" + args[0], "")
            keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set={name},{acl_type}', name=acl_name, acl_type=args[0])
            response = acl_client.get(keypath, depth=None, ignore404=False)
            if response.ok():
                __handle_get_acl_details_aggregate_mode_response(response.content, [args[0], acl_name])
            else:
                print(response.error_message())
                return


def __handle_get_acl_details_interface_mode_response(response, args):
    if len(args) == 1:
        __process_acl_counters_request_by_type(response, args)
    elif len(args) == 2:
        __process_acl_counters_request_by_type_and_name(response, args)
    else:
        __process_acl_counters_request_by_name_and_inf(response, args)


def handle_get_acl_details_response(response, op_str, args):
    if response.ok():
        if response.counter_mode == 'AGGREGATE_ONLY':
            __handle_get_acl_details_aggregate_mode_response(response.content, args)
        else: 
            if bool(response.content):
                __handle_get_acl_details_interface_mode_response(response.content, args)
            elif len(args) > 1:
                raise SonicAclCLIError('ACL {} not found'.format(args[1]))
    else:
        if response.status_code != 404:
            print(response.error_message())
        elif len(args) == 2:
            raise SonicAclCLIError('ACL {} not found'.format(args[1]))


def handle_get_all_acl_binding_response(response, op_str, args):
    acl_typemap = {'L2': 'MAC', 'L3': 'IP', 'L3V6': 'IPV6'}
    log.log_debug(json.dumps(response.content, indent=4))
    render_data = OrderedDict()
    filter_acl_type = None
    if len(args) == 1:
        filter_acl_type = __convert_oc_acl_type_to_sonic_fmt(args[0])

    if response.ok():
        resp_content = response.content
        if bool(resp_content):
            for intf_data in resp_content["sonic-acl:ACL_BINDING_TABLE_LIST"]:
                if intf_data["intfname"] not in render_data.keys():
                    if_bind_list = list()
                else:
                    if_bind_list = render_data[intf_data["intfname"]]

                for acl_type in acl_typemap.keys():
                    if filter_acl_type is not None and filter_acl_type != acl_type:
                        continue
                    if acl_type in intf_data.keys():
                        aclname = intf_data[acl_type]
                        if_bind_list.append(tuple([intf_data["stage"].capitalize(), acl_typemap[acl_type], aclname]))

                if_bind_list.sort(key=lambda x: (x[0].replace('ress', '').replace('Ing', 'A'), x[1]))
                render_data[intf_data["intfname"]] = if_bind_list

            # Sort the data in the order Eth->Po->Vlan->Switch
            sorted_data = OrderedDict(natsorted(render_data.items(), key=acl_natsort_intf_prio))
            log.log_debug(str(sorted_data))
            show_cli_output('show_access_group.j2', sorted_data)
    else:
        if response.status_code != 404:
            print(response.error_message())


def clear_acl_counters_response(response, op_str, args):
    if not response.ok():
        print(response.error_message())
    else:
        if response.content['sonic-acl:output']['status'] != "SUCCESS":
            raise SonicAclCLIError("{}".format(response.content['sonic-acl:output']['status-detail']))
        log.log_debug("clear completed")


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
    'clear_acl_remark': clear_acl_remark_request,
    'clear_acl_counters': clear_acl_counters_request,
    'set_counter_mode': set_counter_mode_request
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
    'clear_acl_remark': handle_generic_delete_response,
    'clear_acl_counters': clear_acl_counters_response,
    'set_counter_mode': handle_generic_set_response
}


def run(op_str, args=None):
    try:
        log.log_debug(str(args))
        correct_args = list()
        if args is None:
            args = list()
        for arg in args:
            if arg == "|" or arg == "\\|":
                break
            else:
                correct_args.append(arg)
        log.log_debug(str(correct_args))
        resp = request_handlers[op_str](correct_args)
        if resp:
            return response_handlers[op_str](resp, op_str, correct_args)
    except SonicAclCLIError as e:
        print("%Error: {}".format(e.message))
        return -1
    except SonicACLCLIStopNoError:
        pass
    except Exception as e:
        log.log_error(traceback.format_exc())
        print('%Error: Encountered exception "{}"'.format(str(e)))
        return -1

    return 0


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2:])


# ================================================
#            Jinja2 functions
# ================================================
def tcp_flags_to_user_fmt(value):
    tcp_flags, tcp_flags_mask = value.split('/')
    tcp_flags = int(tcp_flags, 0)
    tcp_flags_mask = int(tcp_flags_mask, 0)
    flags_str = ''
    for i in range(0, 8):
        if tcp_flags_mask & (1 << i):
            if tcp_flags & (1 << i):
                flags_str = flags_str + ' ' + TCP_FLAG_VALUES_REV[1 << i]
            else:
                flags_str = flags_str + ' not-' + TCP_FLAG_VALUES_REV[1 << i]

    return flags_str.strip()


def mac_addr_to_user_fmt(mac_val):
    mac_val = str(mac_val).upper()
    parts = mac_val.split("/")
    if len(parts) == 2:
        mac_addr = parts[0]
        mac_mask = parts[1]
    else:
        mac_addr = mac_val
        mac_mask = 'FF:FF:FF:FF:FF:FF'

    if mac_mask == 'FF:FF:FF:FF:FF:FF':
        return "host " + mac_addr.lower()
    else:
        return "{}/{}".format(mac_addr, mac_mask).lower()


def ip_protocol_to_user_fmt(val):
    val = str(val)
    if val == "6":
        return "tcp"
    if val == "17":
        return "udp"
    if val == "1":
        return "icmp"
    if val == "58":
        return "icmpv6"

    return val


def pcp_to_user_fmt(pcp):
    return pcp_rev_map[pcp]


def dscp_to_user_fmt(dscp):
    if dscp in dscp_rev_map:
        return dscp_rev_map[dscp]

    return dscp

