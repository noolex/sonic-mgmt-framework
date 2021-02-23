#!/usr/bin/python
###########################################################################
#
# Copyright 2019 BRCM, Inc.
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
import json
import collections
import re
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
import ast
import subprocess

def invoke(func, args):
    body = None
    aa = cc.ApiClient()

    addr4 = "1.1.1.1"
    addr6 = "1::1"

    # Get VRRP all - nothing for get all
    if func == '':
        keypath = cc.Path('')
        return aa.get(keypath)

    # Get VRRP instance
    if func == 'get_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ip_addresses_address_vrrp_vrrp_group_state':

        if len(args) == 2:
            if args[0] == "ipv4":
                keypath = cc.Path('/restconf/operations/sonic-vrrp:get-vrrp')
            else:
                keypath = cc.Path('/restconf/operations/sonic-vrrp:get-vrrp6')
            return aa.post(keypath, body)
        else:
            if "Vlan" in args[2]:
                if args[0] == "ipv4":
                    keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}', name=args[2], ip=addr4, vrid=args[3])
                else:
                    keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}', name=args[2], ip=addr6, vrid=args[3])
            else:
                parent_if = args[2]
                sub_if = "0"
                if '.' in parent_if:
                    parent_if = args[2].split('.')[0]
                    sub_if = args[2].split('.')[1]

                if args[0] == "ipv4":
                    keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}', name=parent_if, index=sub_if, ip=addr4, vrid=args[3])
                else:
                    keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}', name=parent_if, index=sub_if, ip=addr6, vrid=args[3])
            return aa.get(keypath)

    # VRRP delete
    if func == 'delete_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ip_addresses_address_vrrp_vrrp_group' :
        if "Vlan" in args[0]:
            if args[2] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}', name=args[0], ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}', name=args[0], ip=addr6, vrid=args[1])
        else:
            parent_if = args[0]
            sub_if = "0"
            if '.' in parent_if:
                parent_if = args[0].split('.')[0]
                sub_if = args[0].split('.')[1]

            if args[2] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}', name=parent_if, index=sub_if, ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}', name=parent_if, index=sub_if, ip=addr6, vrid=args[1])
        return aa.delete(keypath)

    # VRRP set
    if func == 'post_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ip_addresses_address_vrrp_vrrp_group_config' :

        if "Vlan" in args[0]:
            if args[2] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp', name=args[0], ip=addr4)
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp', name=args[0], ip=addr6)
        else:
            parent_if = args[0]
            sub_if = "0"
            if '.' in parent_if:
                parent_if = args[0].split('.')[0]
                sub_if = args[0].split('.')[1]

            if args[2] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp', name=parent_if, index=sub_if, ip=addr4)
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp', name=parent_if, index=sub_if, ip=addr6)

        body=collections.defaultdict(dict)
        body = {"openconfig-if-ip:vrrp": {"vrrp-group": [{"virtual-router-id": int(args[1]),"config": {"virtual-router-id": int(args[1])}}]}}
        return aa.patch(keypath, body)

    # VRRP delete vip
    if func == 'del_llist_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ip_addresses_address_vrrp_vrrp_group_config_virtual_address' :
        body = collections.defaultdict(dict)

        if "Vlan" in args[0]:
            if args[3] == "ipv4":
                body = {"name": args[0], "ip": addr4, "vrid": args[1], "vip": args[2]}
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/virtual-address={vip}', **body)
            else:
                body = {"name": args[0], "ip": addr6, "vrid": args[1], "vip": args[2]}
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/virtual-address={vip}', **body)
        else:
            parent_if = args[0]
            sub_if = "0"
            if '.' in parent_if:
                parent_if = args[0].split('.')[0]
                sub_if = args[0].split('.')[1]

            if args[3] == "ipv4":
                body = {"name": parent_if, "index": sub_if, "ip": addr4, "vrid": args[1], "vip": args[2]}
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/virtual-address={vip}', **body)
            else:
                body = {"name": parent_if, "index": sub_if, "ip": addr6, "vrid": args[1], "vip": args[2]}
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/virtual-address={vip}', **body)

        return aa.delete(keypath)

    # VRRP set vip
    if func == 'patch_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ip_addresses_address_vrrp_vrrp_group_config_virtual_address' :
        if "Vlan" in args[0]:
            if args[3] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/virtual-address', name=args[0], ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/virtual-address', name=args[0], ip=addr6, vrid=args[1])
        else:
            parent_if = args[0]
            sub_if = "0"
            if '.' in parent_if:
                parent_if = args[0].split('.')[0]
                sub_if = args[0].split('.')[1]

            if args[3] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/virtual-address', name=parent_if, index=sub_if, ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/virtual-address', name=parent_if, index=sub_if, ip=addr6, vrid=args[1])
        body=collections.defaultdict(dict)
        body = {"openconfig-if-ip:virtual-address": [args[2]]}

        return aa.patch(keypath, body)


    # VRRP delete track interface
    if func == 'delete_openconfig_interfaces_ext' :
        body = collections.defaultdict(dict)
        if "Vlan" in args[0]:
            if args[3] == "ipv4":
                body = {"name": args[0], "ip": addr4, "vrid": args[1], "trackif": args[2]}
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/openconfig-interfaces-ext:vrrp-track/vrrp-track-interface={trackif}', **body)
            else:
                body = {"name": args[0], "ip": addr6, "vrid": args[1], "trackif": args[2]}
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/openconfig-interfaces-ext:vrrp-track/vrrp-track-interface={trackif}', **body)
        else:
            parent_if = args[0]
            sub_if = "0"
            if '.' in parent_if:
                parent_if = args[0].split('.')[0]
                sub_if = args[0].split('.')[1]

            if args[3] == "ipv4":
                body = {"name": parent_if, "index": sub_if, "ip": addr4, "vrid": args[1], "trackif": args[2]}
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/openconfig-interfaces-ext:vrrp-track/vrrp-track-interface={trackif}', **body)
            else:
                body = {"name": parent_if, "index": sub_if, "ip": addr6, "vrid": args[1], "trackif": args[2]}
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/openconfig-interfaces-ext:vrrp-track/vrrp-track-interface={trackif}', **body)
        return aa.delete(keypath)

    # VRRP set track interfaces
    if func == 'patch_openconfig_interfaces_ext' :
        if "Vlan" in args[0]:
            if args[4] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/openconfig-interfaces-ext:vrrp-track', name=args[0], ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/openconfig-interfaces-ext:vrrp-track', name=args[0], ip=addr6, vrid=args[1])
        else:
            parent_if = args[0]
            sub_if = "0"
            if '.' in parent_if:
                parent_if = args[0].split('.')[0]
                sub_if = args[0].split('.')[1]

            if args[4] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/openconfig-interfaces-ext:vrrp-track', name=parent_if, index=sub_if, ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/openconfig-interfaces-ext:vrrp-track', name=parent_if, index=sub_if, ip=addr6, vrid=args[1])
        body=collections.defaultdict(dict)
        body = {"openconfig-interfaces-ext:vrrp-track": {"vrrp-track-interface": [{"track-intf": args[2],"config": {"track-intf": args[2],"priority-increment": int(args[3])}}]}}
        return aa.patch(keypath, body)


    # VRRP delete priority
    if func == 'delete_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ip_addresses_address_vrrp_vrrp_group_config_priority' :
        if "Vlan" in args[0]:
            if args[2] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/priority',name=args[0], ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/priority', name=args[0], ip=addr6, vrid=args[1])
        else:
            parent_if = args[0]
            sub_if = "0"
            if '.' in parent_if:
                parent_if = args[0].split('.')[0]
                sub_if = args[0].split('.')[1]

            if args[2] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/priority',name=parent_if, index=sub_if, ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/priority', name=parent_if, index=sub_if, ip=addr6, vrid=args[1])
        return aa.delete(keypath)

    # VRRP set priority
    if func == 'patch_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ip_addresses_address_vrrp_vrrp_group_config_priority' :
        if "Vlan" in args[0]:
            if args[3] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/priority', name=args[0], ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/priority', name=args[0], ip=addr6, vrid=args[1])
        else:
            parent_if = args[0]
            sub_if = "0"
            if '.' in parent_if:
                parent_if = args[0].split('.')[0]
                sub_if = args[0].split('.')[1]

            if args[3] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/priority', name=parent_if, index=sub_if, ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/priority', name=parent_if, index=sub_if, ip=addr6, vrid=args[1])

        body=collections.defaultdict(dict)
        body = {"openconfig-if-ip:priority": int(args[2])}

        return aa.patch(keypath, body)

    # VRRP set & delete preempt
    if func == 'patch_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ip_addresses_address_vrrp_vrrp_group_config_preempt' :
        if "Vlan" in args[0]:
            if args[3] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/preempt', name=args[0], ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/preempt', name=args[0], ip=addr6, vrid=args[1])
        else:
            parent_if = args[0]
            sub_if = "0"
            if '.' in parent_if:
                parent_if = args[0].split('.')[0]
                sub_if = args[0].split('.')[1]

            if args[3] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/preempt', name=parent_if, index=sub_if, ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/preempt', name=parent_if, index=sub_if, ip=addr6, vrid=args[1])

        body=collections.defaultdict(dict)
        if args[2] == "true":
            body = {"openconfig-if-ip:preempt": True}
        else:
            body = {"openconfig-if-ip:preempt": False}

        return aa.patch(keypath, body)

    # VRRP set & delete use_v2_checksum
    if func == 'patch_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ip_addresses_address_vrrp_vrrp_group_config_use_v2_checksum':
        if "Vlan" in args[0]:
            keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/openconfig-interfaces-ext:use-v2-checksum', name=args[0], ip=addr4, vrid=args[1])
        else:
            parent_if = args[0]
            sub_if = "0"
            if '.' in parent_if:
                parent_if = args[0].split('.')[0]
                sub_if = args[0].split('.')[1]

            keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/openconfig-interfaces-ext:use-v2-checksum', name=parent_if, index=sub_if, ip=addr4, vrid=args[1])

        body=collections.defaultdict(dict)
        if args[2] == "true":
            body = {"openconfig-if-ip:use-v2-checksum": True}
        else:
            body = {"openconfig-if-ip:use-v2-checksum": False}

        return aa.patch(keypath, body)

    # VRRP delete advertisement
    if func == 'delete_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ip_addresses_address_vrrp_vrrp_group_config_advertisement_interval' :
        if "Vlan" in args[0]:
            if args[2] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/advertisement-interval', name=args[0], ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/advertisement-interval', name=args[0], ip=addr6, vrid=args[1])
        else:
            parent_if = args[0]
            sub_if = "0"
            if '.' in parent_if:
                parent_if = args[0].split('.')[0]
                sub_if = args[0].split('.')[1]

            if args[2] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/advertisement-interval', name=parent_if, index=sub_if, ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/advertisement-interval', name=parent_if, index=sub_if, ip=addr6, vrid=args[1])

        return aa.delete(keypath)

    # VRRP set advertisement
    if func == 'patch_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ip_addresses_address_vrrp_vrrp_group_config_advertisement_interval' :
        if "Vlan" in args[0]:
            if args[3] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/advertisement-interval', name=args[0], ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/advertisement-interval', name=args[0], ip=addr6, vrid=args[1])
        else:
            parent_if = args[0]
            sub_if = "0"
            if '.' in parent_if:
                parent_if = args[0].split('.')[0]
                sub_if = args[0].split('.')[1]

            if args[3] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/advertisement-interval', name=parent_if, index=sub_if, ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/advertisement-interval', name=parent_if, index=sub_if, ip=addr6, vrid=args[1])

        body=collections.defaultdict(dict)
        body = {"openconfig-if-ip:advertisement-interval": int(args[2])}
        return aa.patch(keypath, body)

    # VRRP delete version
    if func == 'delete_openconfig_interfaces_ext_interfaces_interface_subinterfaces_subinterface_ip_addresses_address_vrrp_vrrp_group_config_version' :
        if "Vlan" in args[0]:
            if args[2] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/openconfig-interfaces-ext:version', name=args[0], ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/openconfig-interfaces-ext:version', name=args[0], ip=addr6, vrid=args[1])
        else:
            parent_if = args[0]
            sub_if = "0"
            if '.' in parent_if:
                parent_if = args[0].split('.')[0]
                sub_if = args[0].split('.')[1]

            if args[2] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/openconfig-interfaces-ext:version', name=parent_if, index=sub_if, ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/openconfig-interfaces-ext:version', name=parent_if, index=sub_if, ip=addr6, vrid=args[1])

        return aa.delete(keypath)

    # VRRP set version
    if func == 'patch_openconfig_interfaces_ext_interfaces_interface_subinterfaces_subinterface_ip_addresses_address_vrrp_vrrp_group_config_version' :
        if "Vlan" in args[0]:
            if args[3] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/openconfig-interfaces-ext:version', name=args[0], ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-vlan:routed-vlan/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/openconfig-interfaces-ext:version', name=args[0], ip=addr6, vrid=args[1])
        else:
            parent_if = args[0]
            sub_if = "0"
            if '.' in parent_if:
                parent_if = args[0].split('.')[0]
                sub_if = args[0].split('.')[1]

            if args[3] == "ipv4":
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv4/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/openconfig-interfaces-ext:version', name=parent_if, index=sub_if, ip=addr4, vrid=args[1])
            else:
                keypath = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/subinterfaces/subinterface={index}/openconfig-if-ip:ipv6/addresses/address={ip}/vrrp/vrrp-group={vrid}/config/openconfig-interfaces-ext:version', name=parent_if, index=sub_if, ip=addr6, vrid=args[1])

        body=collections.defaultdict(dict)
        body = {"openconfig-interfaces-ext:version": int(args[2])}

        return aa.patch(keypath, body)

    else:
        print("%Error: not implemented")
        exit(1)

def run(func, args):
    try:
        if func == 'patch_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ip_addresses_address_vrrp_vrrp_group_config_priority' and args[2] == "100":
            func = 'delete_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ip_addresses_address_vrrp_vrrp_group_config_priority'
            args[2] = args[3]


        api_response = invoke(func, args)

        if api_response.ok():
            response = api_response.content
            if response is None:
                pass
            # is it correct
            elif 'openconfig-if-ip:vrrp-group' in response.keys():
                # check for subif
                response[u'ifname'] = args[2]
                response[u'vrid'] = args[3]

                if args[0] == "ipv6":
                    response[u'afi'] = 2
                else:
                    response[u'afi'] = 1

                single_instance = response.values()[0][0]
                if 'config' in single_instance.keys():
                    show_cli_output("show_vrrp.j2", response)
                return
            else:
                if args[0] == "ipv6":
                    response[u'afi'] = 2
                else:
                    response[u'afi'] = 1
                show_cli_output("show_vrrp_summary.j2", response)
        elif func == 'post_openconfig_if_ip_interfaces_interface_subinterfaces_subinterface_ip_addresses_address_vrrp_vrrp_group_config' and '%Error: Resource not found' in api_response.error_message():
            print('%Error: Configure interface IP before configuring VRRP')
            return 1 
        else:
            #error response
            print(api_response.error_message())
            return 1

    except:
            # system/network error
            raise

if __name__ == '__main__':
    pipestr().write(sys.argv)
    #pdb.set_trace()
    run(sys.argv[1], sys.argv[2:])
