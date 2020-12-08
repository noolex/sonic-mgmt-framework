#!/usr/bin/python

###########################################################################
#
# Copyright 2019 Dell, Inc.
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

from scripts.render_cli import show_cli_output
import cli_client as cc
import sys
import sonic_intf_utils as ifutils
from natsort import natsorted

aa = cc.ApiClient()

g_stp_mode = None
g_stp_resp = None
g_stp_data = {}

def stp_mode_get(aa):
    global g_stp_mode
    global g_stp_data
    global g_stp_resp

    g_stp_resp = aa.get('/restconf/data/openconfig-spanning-tree:stp/global/config', None, False)
    if not g_stp_resp.ok():
        if g_stp_resp.status_code == 405:
            print(g_stp_resp.error_message())
        else:
            print ("%Error: spanning-tree is not enabled")
        return g_stp_resp,g_stp_mode

    #g_stp_resp = aa.api_client.sanitize_for_serialization(g_stp_resp)

    if not 'enabled-protocol' in g_stp_resp['openconfig-spanning-tree:config']:
        print ("%Error: spanning-tree is not enabled")
        return g_stp_resp,g_stp_mode

    if g_stp_resp['openconfig-spanning-tree:config']['enabled-protocol'][0] == "openconfig-spanning-tree-ext:PVST":
        g_stp_mode = "PVST"
    elif g_stp_resp['openconfig-spanning-tree:config']['enabled-protocol'][0] == "openconfig-spanning-tree-types:RAPID_PVST":
        g_stp_mode = "RAPID_PVST"
    else:
        print ("%Error: Invalid spanning-tree mode")


    if "loop-guard" in g_stp_resp['openconfig-spanning-tree:config']:
        g_stp_data['loop-guard'] = g_stp_resp['openconfig-spanning-tree:config']["loop-guard"]

    if "bpdu-filter" in g_stp_resp['openconfig-spanning-tree:config']:
        g_stp_data['bpdu-filter'] = g_stp_resp['openconfig-spanning-tree:config']["bpdu-filter"]

    if "openconfig-spanning-tree-ext:rootguard-timeout" in g_stp_resp['openconfig-spanning-tree:config']:
        g_stp_data['rootguard-timeout'] = g_stp_resp['openconfig-spanning-tree:config']["openconfig-spanning-tree-ext:rootguard-timeout"]

    if "openconfig-spanning-tree-ext:portfast" in g_stp_resp['openconfig-spanning-tree:config']:
        g_stp_data['portfast'] = g_stp_resp['openconfig-spanning-tree:config']["openconfig-spanning-tree-ext:portfast"]

    if "openconfig-spanning-tree-ext:hello-time" in g_stp_resp['openconfig-spanning-tree:config']:
        g_stp_data['hello-time'] = g_stp_resp['openconfig-spanning-tree:config']["openconfig-spanning-tree-ext:hello-time"]

    if "openconfig-spanning-tree-ext:max-age" in g_stp_resp['openconfig-spanning-tree:config']:
        g_stp_data['max-age'] = g_stp_resp['openconfig-spanning-tree:config']["openconfig-spanning-tree-ext:max-age"]

    if "openconfig-spanning-tree-ext:forwarding-delay" in g_stp_resp['openconfig-spanning-tree:config']:
        g_stp_data['forwarding-delay'] = g_stp_resp['openconfig-spanning-tree:config']["openconfig-spanning-tree-ext:forwarding-delay"]

    if "openconfig-spanning-tree-ext:bridge-priority" in g_stp_resp['openconfig-spanning-tree:config']:
        g_stp_data['bridge-priority'] = g_stp_resp['openconfig-spanning-tree:config']["openconfig-spanning-tree-ext:bridge-priority"]

    return g_stp_resp,g_stp_mode

def getId(item):
    ifName = item['name']
    return ifutils.name_to_int_val(ifName)

def generic_set_response_handler(response, args):
    if not response.ok():
        print(response.error_message())


def generic_delete_response_handler(response, args):
    if response.ok():
        resp_content = response.content
        if resp_content is not None:
            print("%Error: {}".format(str(resp_content)))
    elif response.status_code != 404:
        print(response.error_message())


def generic_show_response_handler(output_data, args):
    j2_tmpl = args[0]
    show_cli_output(j2_tmpl, output_data)


def set_stp_global_mode(args):
    mode = args[0].strip()
    if mode == 'pvst':
        body = { "openconfig-spanning-tree:enabled-protocol": ['PVST'] }
    elif mode == 'rapid-pvst':
        body = { "openconfig-spanning-tree:enabled-protocol": ['RAPID_PVST'] }
    else:
        print('%Error: Invalid mode')
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config')
    return aa.post(uri, body)


def set_stp_global_bpdu_filter(args):
    body = { "openconfig-spanning-tree:bpdu-filter": True if args[0] else False }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/bpdu-filter')
    return aa.patch(uri, body)

def set_stp_global_loop_guard(args):
    body = { "openconfig-spanning-tree:loop-guard": args[0] }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/loop-guard')
    return aa.patch(uri, body)

def set_stp_global_portfast(args):
    body = {"openconfig-spanning-tree-ext:portfast": args[0]}
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:portfast')
    return aa.patch(uri, body)


def del_stp_vlan_subcmds(args):
    op_str = args[0].strip()
    if op_str == 'hello-time':
        args.append(g_stp_data['hello-time'])
        return patch_stp_vlan_hello_time(args[1:])
    elif op_str == 'priority':
        args.append(g_stp_data['bridge-priority'])
        return patch_stp_vlan_bridge_priority(args[1:])
    elif op_str == 'max-age':
        args.append(g_stp_data['max-age'])
        return patch_stp_vlan_max_age(args[1:])
    elif op_str == 'forward-time':
        args.append(g_stp_data['forwarding-delay'])
        return patch_stp_vlan_fwd_delay(args[1:])
    else:
        return delete_stp_vlan(args)


def set_stp_vlan_subcmds(args):
    op_str = args[0].strip()
    if op_str == 'hello-time':
        return patch_stp_vlan_hello_time(args[1:])
    elif op_str == 'priority':
        return patch_stp_vlan_bridge_priority(args[1:])
    elif op_str == 'max-age':
        return patch_stp_vlan_max_age(args[1:])
    elif op_str == 'forward-time':
        return patch_stp_vlan_fwd_delay(args[1:])
    else:
        return patch_stp_vlan_enable(args)

    return None


def range_to_list(vrange):
    range_list = []
    vlist = vrange.split(',')
    for v in vlist:
        if '-' in v:
            ranges = v.split('-')
            for i in range(int(ranges[0]), int(ranges[1])+1):
                range_list.append(i)
        else:
            range_list.append(int(v))

    return range_list


def build_vlan_config_body(vlan_range, param_dict):

    body = {}
    if g_stp_mode == 'PVST':
        oc_vlan_format = "openconfig-spanning-tree-ext:vlan"
    elif g_stp_mode == 'RAPID_PVST':
        oc_vlan_format = "openconfig-spanning-tree:vlan"
    else:
        return None
    
    body[oc_vlan_format] = []

    vlan_list = range_to_list(vlan_range)

    for vlan in vlan_list:
        vlan_data = {
                    "vlan-id": vlan,
                    "config": {
                        "vlan-id": vlan,
                        }
                    }
        vlan_data["config"].update(param_dict)
        body[oc_vlan_format].append(vlan_data)
    return body


def build_vlan_intf_config_body(vlan_range, intf_name, param_dict):
    body = {}
    if g_stp_mode == 'PVST':
        oc_vlan_format = "openconfig-spanning-tree-ext:vlan"
    elif g_stp_mode == 'RAPID_PVST':
        oc_vlan_format = "openconfig-spanning-tree:vlan"
    else:
        return None
    
    body[oc_vlan_format] = []

    vlan_list = range_to_list(vlan_range)
    for vlan in vlan_list:
        vlan_data = {
                    "vlan-id": vlan,
                    "interfaces": {
                        "interface": [
                            {
                                "name" : intf_name,
                                "config" : {
                                    "name" : intf_name,
                                }
                            }
                        ]
                        }
                    }
        vlan_data["interfaces"]["interface"][0]["config"].update(param_dict)
        body[oc_vlan_format].append(vlan_data)
    return body


def patch_stp_vlan_fwd_delay(args):
    body = build_vlan_config_body(args[0], {'forwarding-delay':int(args[1])})
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan')
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan')
    else:
        return None

    return aa.patch(uri, body)


def patch_stp_vlan_hello_time(args):
    body = build_vlan_config_body(args[0], {'hello-time':int(args[1])})
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan')
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan')
    else:
        return None

    return aa.patch(uri, body)


def patch_stp_vlan_max_age(args):
    body = build_vlan_config_body(args[0], {'max-age':int(args[1])})
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan')
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan')
    else:
        return None

    return aa.patch(uri, body)


def patch_stp_vlan_bridge_priority(args):
    body = build_vlan_config_body(args[0], {'bridge-priority':int(args[1])})
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan')
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan')
    else:
        return None

    return aa.patch(uri, body)


def patch_stp_vlan_enable(args):
    vlanList = args[0].split(',')
    for pattern in vlanList:
        if '-' in pattern:
            vlan_range = pattern.replace('-', '..')
            uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:disabled-vlans={}'.format(vlan_range))
        else:
            uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:disabled-vlans={}'.format(pattern))
        resp = aa.delete(uri, None)
        if not resp.ok():
            return resp
    return resp

'''
patch_stp_vlan_enable(args):
    body = { "openconfig-spanning-tree-ext:spanning-tree-enable": True }

    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}/config/spanning-tree-enable', vlan_id=args[0])
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}/config/openconfig-spanning-tree-ext:spanning-tree-enable', vlan_id=args[0])
    else:
        return None

    return aa.patch(uri, body)
'''

def set_stp_global_forwarding_delay(args):
    body = {"openconfig-spanning-tree-ext:forwarding-delay": int(args[0])}
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:forwarding-delay')
    return aa.patch(uri, body)


def set_stp_global_rootguard_timeout(args):
    body = {"openconfig-spanning-tree-ext:rootguard-timeout": int(args[0])}
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:rootguard-timeout')
    return aa.patch(uri, body)


def set_stp_global_hello_time(args):
    body = {"openconfig-spanning-tree-ext:hello-time": int(args[0])}
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:hello-time')
    return aa.patch(uri, body)


def set_stp_global_max_age(args):
    body = {"openconfig-spanning-tree-ext:max-age": int(args[0])}
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:max-age')
    return aa.patch(uri, body)


def set_stp_global_bridge_priority(args):
    body = {"openconfig-spanning-tree-ext:bridge-priority": int(args[0])}
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:bridge-priority')
    return aa.patch(uri, body)


def set_stp_intf_bpdu_guard(args):
    ifname  = args[0].strip()
    if len(args) == 2:
        return patch_stp_intf_bpdu_guard_shutdown([ifname, True])
    else:
        return patch_stp_intf_bpdu_guard([ifname, True])


def patch_stp_intf_bpdu_guard_shutdown(args):
    body = None
    if args[1]:
        body = { "openconfig-spanning-tree-ext:bpdu-guard-port-shutdown": True }
    else:
        body = { "openconfig-spanning-tree-ext:bpdu-guard-port-shutdown": False }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/openconfig-spanning-tree-ext:bpdu-guard-port-shutdown', name=args[0])
    return aa.patch(uri, body)


def set_stp_intf_portfast(args):
    body = None
    if args[1]:
        body = { "openconfig-spanning-tree-ext:portfast": True }
    else:
        body = { "openconfig-spanning-tree-ext:portfast": False }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/openconfig-spanning-tree-ext:portfast', name=args[0])
    return aa.patch(uri, body)


def set_stp_intf_uplink_fast(args):
    body = None
    if args[1]:
        body = { "openconfig-spanning-tree-ext:uplink-fast": True }
    else:
        body = { "openconfig-spanning-tree-ext:uplink-fast": False }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/openconfig-spanning-tree-ext:uplink-fast', name=args[0])
    return aa.patch(uri, body)


def set_stp_intf_enable(args):
    body = None
    if args[1]:
        body = { "openconfig-spanning-tree-ext:spanning-tree-enable": True }
    else:
        body = { "openconfig-spanning-tree-ext:spanning-tree-enable": False }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/openconfig-spanning-tree-ext:spanning-tree-enable', name=args[0])
    return aa.patch(uri, body)


def set_stp_intf_cost(args):
    body = { "openconfig-spanning-tree-ext:cost": int(args[1]) }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/openconfig-spanning-tree-ext:cost', name=args[0])
    return aa.patch(uri, body)


def set_stp_intf_port_priority(args):
    body = { "openconfig-spanning-tree-ext:port-priority": int(args[1]) }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/openconfig-spanning-tree-ext:port-priority', name=args[0])
    return aa.patch(uri, body)


def set_stp_intf_edge_port(args):
    body = None
    if args[1]:
        body = { "openconfig-spanning-tree:edge-port": "EDGE_ENABLE" }
    else:
        body = { "openconfig-spanning-tree:edge-port": "EDGE_DISABLE" }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/edge-port', name=args[0])
    return aa.patch(uri, body)


def set_stp_intf_bpdu_filter(args):
    body = None
    if args[0] == "enable":
        body = { "openconfig-spanning-tree:bpdu-filter": True }
    elif args[0] == "disable":
        body = { "openconfig-spanning-tree:bpdu-filter": False }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/bpdu-filter', name=args[1])
    return aa.patch(uri, body)


def patch_stp_intf_bpdu_guard(args):
    body = None
    if args[1]:
        body = { "openconfig-spanning-tree:bpdu-guard": True }
    else:
        body = { "openconfig-spanning-tree:bpdu-guard": False }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/bpdu-guard', name=args[0])
    return aa.patch(uri, body)


def set_stp_intf_guard(args):
    body = None
    if args[1] == "root":
        body = { "openconfig-spanning-tree:guard": "ROOT"}
    elif args[1] == "loop":
        body = { "openconfig-spanning-tree:guard": "LOOP"}
    else:
        body = { "openconfig-spanning-tree:guard": "NONE"}

    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/guard', name=args[0])
    return aa.patch(uri, body)


def set_stp_intf_vlan_subcmds(args):
    sub_cmd = args[0].strip()
    if sub_cmd == "cost":
        return patch_stp_vlan_intf_cost(args[1:])
    elif sub_cmd == "port-priority":
        return patch_stp_vlan_intf_priority(args[1:])
    else:
        return None


def patch_stp_vlan_intf_cost(args):
    body = build_vlan_intf_config_body(args[0], args[1], {"cost": int(args[2])})
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan')
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan')
    else:
        return None
    return aa.patch(uri, body)


def patch_stp_vlan_intf_priority(args):
    body = build_vlan_intf_config_body(args[0], args[1], {"port-priority": int(args[2])})
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan')
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan')
    else:
        return None
    return aa.patch(uri, body)


def set_stp_intf_link_type(args):
    link_type = ''
    if args[1].strip() == 'point-to-point':
        link_type = 'P2P'
    elif args[1].strip() == 'shared':
        link_type = 'SHARED'
    body = { "openconfig-spanning-tree:link-type": link_type }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/link-type', name=args[0])
    return aa.patch(uri, body)


def del_stp_global_mode(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config')
    return aa.delete(uri, None)


def delete_stp_vlan(args):
    vlanList = args[0].split(',')
    ocyangFormatList = []
    for pattern in vlanList:
        if '-' in pattern:
            ocyangFormatList.append(pattern.replace('-', '..'))
        else:
            ocyangFormatList.append(int(pattern))

    body = {"openconfig-spanning-tree-ext:disabled-vlans": ocyangFormatList}
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:disabled-vlans')
    return aa.patch(uri, body)


def delete_stp_vlan_fwd_delay(args):
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}/config/forwarding-delay', vlan_id=args[0])
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}/config/forwarding-delay', vlan_id=args[0])
    else:
        return None
    return aa.delete(uri, None)


def delete_stp_vlan_hello_time(args):
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}/config/hello-time', vlan_id=args[0])
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}/config/hello-time', vlan_id=args[0])
    else:
        return None
    return aa.delete(uri, None)


def delete_stp_vlan_max_age(args):
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}/config/max-age', vlan_id=args[0])
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}/config/max-age', vlan_id=args[0])
    else:
        return None

    return aa.delete(uri, None)


def delete_stp_vlan_bridge_priority(args):
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}/config/bridge-priority', vlan_id=args[0])
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}/config/bridge-priority', vlan_id=args[0])
    else:
        return None

    return aa.delete(uri, None)


def del_stp_global_forwarding_delay(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:forwarding-delay')
    return aa.delete(uri, None)


def del_stp_global_rootguard_timeout(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:rootguard-timeout')
    return aa.delete(uri, None)


def del_stp_global_hello_time(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:hello-time')
    return aa.delete(uri, None)


def del_stp_global_max_age(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:max-age')
    return aa.delete(uri, None)


def del_stp_global_bridge_priority(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:bridge-priority')
    return aa.delete(uri, None)

def del_stp_intf_cost(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/openconfig-spanning-tree-ext:cost', name=args[0])
    return aa.delete(uri, None)


def del_stp_intf_port_priority(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/openconfig-spanning-tree-ext:port-priority', name=args[0])
    return aa.delete(uri, None)


def del_stp_intf_bpdu_filter(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/bpdu-filter', name=args[0])
    return aa.delete(uri, None)

def del_stp_intf_guard(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/guard', name=args[0])
    return aa.delete(uri, None)

def del_stp_intf_vlan_subcmds(args):
    if args[0].strip() == "cost":
        return delete_stp_vlan_intf_cost(args[1:])
    elif args[0].strip() == "port-priority":
        return delete_stp_vlan_intf_priority(args[1:])
    else:
        return None


def del_stp_intf_bpdu_guard(args):
    ifname  = args[0].strip()
    if len(args) == 2:
        return patch_stp_intf_bpdu_guard_shutdown([ifname, False])
    else:
        return patch_stp_intf_bpdu_guard([ifname, False])


def delete_stp_vlan_intf_cost(args):
    resp = None
    vlan_list = range_to_list(args[0])
    if g_stp_mode == 'PVST':
        for vlan in vlan_list:
            uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}/interfaces/interface={name}/config/cost', vlan_id=str(vlan), name=args[1])
            resp = aa.delete(uri, None)
            if not resp.ok():
                return resp
    elif g_stp_mode == 'RAPID_PVST':
        for vlan in vlan_list:
            uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}/interfaces/interface={name}/config/cost', vlan_id=str(vlan), name=args[1])
            resp = aa.delete(uri, None)
            if not resp.ok():
                return resp
    return resp


def delete_stp_vlan_intf_priority(args):
    resp = None
    vlan_list = range_to_list(args[0])
    if g_stp_mode == 'PVST':
        for vlan in vlan_list:
            uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}/interfaces/interface={name}/config/port-priority', vlan_id=str(vlan), name=args[1])
            resp = aa.delete(uri, None)
            if not resp.ok():
                return resp
    elif g_stp_mode == 'RAPID_PVST':
        for vlan in vlan_list:
            uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}/interfaces/interface={name}/config/port-priority', vlan_id=str(vlan), name=args[1])
            resp = aa.delete(uri, None)
            if not resp.ok():
                return resp
    return resp


def del_stp_intf_link_type(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/link-type', name=args[0])
    return aa.delete(uri, None)


def del_stp_intf_edge_port(args):
    ifname  = args[0].strip()
    if len(args) == 2:
        return set_stp_intf_edge_port([ifname, False])   
    return None


def get_stp_response():
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst')  
        str1 = 'openconfig-spanning-tree-ext:pvst'
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst')
        str1 = 'openconfig-spanning-tree:rapid-pvst'
    else:
        return None

    output = {}
    api_response = aa.get(uri, None)
    if api_response.ok() and api_response.content is not None:
        if str1 in api_response.content and 'vlan' in api_response.content[str1]:
            value = api_response.content[str1]['vlan']
            for item in value:
                if 'interfaces' in item and 'interface' in item['interfaces']:
                    tup = item['interfaces']['interface']
                    item['interfaces']['interface'] = sorted(tup, key=getId)
            api_response.content[str1]['vlan'] = sorted(api_response.content[str1]['vlan'], key = lambda i: int(i['vlan-id']))
        output.update(g_stp_resp.content)
        output.update(api_response.content)
    return output


def get_stp_bulk_vlan_response_and_filter(vlan_list):
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan')
        str1 = 'openconfig-spanning-tree-ext:vlan'
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan')
        str1 = 'openconfig-spanning-tree:vlan'
    else:
        return None

    output = {}
    api_response = aa.get(uri, None)
    if api_response.ok() and api_response.content is not None:
        if str1 in api_response.content:
            value = api_response.content[str1]
            vlan_data_in_range = []
            for item in value:
                if "vlan-id" in item and item["vlan-id"] in vlan_list:
                    if 'interfaces' in item and 'interface' in item['interfaces']:
                        tup = item['interfaces']['interface']
                        item['interfaces']['interface'] = sorted(tup, key=getId)
                    vlan_data_in_range.append(item)
            api_response.content[str1] = sorted(vlan_data_in_range, key = lambda i: int(i['vlan-id']))

        output.update(g_stp_resp.content)
        output.update(api_response.content)
    return output


def get_stp_vlan_response(vlan):
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}', vlan_id=vlan)
        str1 = 'openconfig-spanning-tree-ext:vlan'
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}', vlan_id=vlan)
        str1 = 'openconfig-spanning-tree:vlan'
    else:
        return None

    output = {}
    api_response = aa.get(uri, None)
    if api_response.ok() and api_response.content is not None:
        if str1 in api_response.content:
            value = api_response.content[str1]
            for item in value:
                if 'interfaces' in item and 'interface' in item['interfaces']:
                    tup = item['interfaces']['interface']
                    item['interfaces']['interface'] = sorted(tup, key=getId)
            api_response.content[str1] = sorted(api_response.content[str1], key = lambda i: int(i['vlan-id']))
     
        output.update(g_stp_resp.content)
        output.update(api_response.content)
    return output


def show_stp_intfs(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces')
    stp_intf_response = aa.get(uri, None)
    if stp_intf_response.ok() and stp_intf_response.content is not None:
        if 'openconfig-spanning-tree:interfaces' in stp_intf_response.content:
            value = stp_intf_response.content['openconfig-spanning-tree:interfaces']
            if 'interface' in value:
                tup = value['interface']
                value['interface'] = sorted(tup, key=getId)
                return stp_intf_response.content
            else:
                return None
    else:
        return None
 

def process_stp_show_cmd(args):
    if len(args) == 1:
        return show_stp(args)
    elif len(args) == 2:
        return show_stp_vlan(args)
    elif len(args) == 3:
        return show_stp_vlan_intfs(args)
    else:
        return None


def show_stp(args):
    output = get_stp_response()
    if not output:
        return None

    stp_intf_data = show_stp_intfs(args)
    if stp_intf_data:
        output.update(stp_intf_data)

    return output


def show_stp_vlan(args):
    vlan_list  = range_to_list(args[1])
    if len(vlan_list) > 1:
        output = get_stp_bulk_vlan_response_and_filter(vlan_list)
    else:
        output = get_stp_vlan_response(args[1])
    if not output:
        return None

    stp_intf_data = show_stp_intfs(args)
    if stp_intf_data:
        output.update(stp_intf_data)

    return output


def show_stp_vlan_intfs(args):
    vlan_list  = range_to_list(args[1])
    if len(vlan_list) > 1:
        output = get_stp_bulk_vlan_response_and_filter(vlan_list)
    else:
        output = get_stp_vlan_response(args[1])

    if not output:
        return None

    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}', name=args[2])
    stp_intf_response = aa.get(uri, None)
    #stp_intf_response = aa.api_client.sanitize_for_serialization(stp_intf_response)
    if stp_intf_response.ok() and stp_intf_response.content is not None:
        output.update(stp_intf_response.content)
    else:
        #print ("% Error: Internal error")
        return None

    return output


def process_stp_show_counters_cmd(args):
    if len(args) == 1:
        return show_stp_counters(args)
    elif len(args) == 2:
        return show_stp_counters_vlan(args)

    return None

 
def show_stp_counters(args):
    output = get_stp_response()
    if not output:
        return None

    return output


def show_stp_counters_vlan(args):
    vlan_list  = range_to_list(args[1])
    if len(vlan_list) > 1:
        output = get_stp_bulk_vlan_response_and_filter(vlan_list)
    else:
        output = get_stp_vlan_response(args[1])

    if not output:
        return None

    return output


def process_stp_show_inconsistentports_cmd(args):
    if len(args) == 1:
        return show_stp_inconsistentports(args)
    elif len(args) == 2:
        return show_stp_inconsistentports_vlan(args)

    return None

 
def show_stp_inconsistentports(args):
    output = get_stp_response()
    if not output:
        return None

    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config')
    stp_global_response = aa.get(uri, None)
    if stp_global_response.ok() and stp_global_response.content is not None:
        output.update(stp_global_response.content)

    return output


def show_stp_inconsistentports_vlan(args):
    output = get_stp_vlan_response(args[1])
    if not output:
        return None

    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config')
    stp_global_response = aa.get(uri, None)
    if stp_global_response.ok() and stp_global_response.content is not None:
        output.update(stp_global_response.content)

    return output


request_handlers = {
        #show
        'process_stp_show': process_stp_show_cmd,
        'process_stp_show_counters':process_stp_show_counters_cmd,
        'process_stp_show_inconsistentports':process_stp_show_inconsistentports_cmd,
	    'get_openconfig_spanning_tree_stp_interfaces':show_stp_intfs,
        #config
        'set_stp_global_bpdu_filter': set_stp_global_bpdu_filter, 
        'set_stp_global_mode': set_stp_global_mode,
        'set_stp_global_forwarding_delay': set_stp_global_forwarding_delay,
        'set_stp_global_rootguard_timeout': set_stp_global_rootguard_timeout,
        'set_stp_global_hello_time': set_stp_global_hello_time,
        'set_stp_global_max_age': set_stp_global_max_age,
        'set_stp_global_bridge_priority': set_stp_global_bridge_priority,
        'set_stp_global_loop_guard': set_stp_global_loop_guard, 
        'set_stp_global_portfast': set_stp_global_portfast, 
        'set_stp_vlan_subcmds': set_stp_vlan_subcmds,
        'set_stp_intf_vlan_subcmds': set_stp_intf_vlan_subcmds,
        'set_stp_intf_link_type':set_stp_intf_link_type,
        'set_stp_intf_edge_port':set_stp_intf_edge_port,
        'set_stp_intf_bpdu_filter':set_stp_intf_bpdu_filter,
        'set_stp_intf_bpdu_guard': set_stp_intf_bpdu_guard,
        'set_stp_intf_guard': set_stp_intf_guard,
        'set_stp_intf_cost': set_stp_intf_cost,
        'set_stp_intf_enable': set_stp_intf_enable,
        'set_stp_intf_portfast':set_stp_intf_portfast,
        'set_stp_intf_port_priority':set_stp_intf_port_priority,
        'set_stp_intf_uplink_fast': set_stp_intf_uplink_fast,
        #delete
        'del_stp_global_mode': del_stp_global_mode,
        'del_stp_global_forwarding_delay': del_stp_global_forwarding_delay,
        'del_stp_global_rootguard_timeout': del_stp_global_rootguard_timeout,
        'del_stp_global_hello_time': del_stp_global_hello_time,
        'del_stp_global_max_age': del_stp_global_max_age,
        'del_stp_global_bridge_priority': del_stp_global_bridge_priority,
        'del_stp_intf_bpdu_filter': del_stp_intf_bpdu_filter,
        'del_stp_intf_bpdu_guard' : del_stp_intf_bpdu_guard,
        'del_stp_intf_cost': del_stp_intf_cost,
        'del_stp_intf_guard': del_stp_intf_guard,
        'del_stp_vlan_subcmds': del_stp_vlan_subcmds,
        'del_stp_intf_vlan_subcmds': del_stp_intf_vlan_subcmds,
        'del_stp_intf_port_priority': del_stp_intf_port_priority,
        'del_stp_intf_link_type': del_stp_intf_link_type,
        'del_stp_intf_edge_port' : del_stp_intf_edge_port,
}

response_handlers = {
        #show
        'process_stp_show': generic_show_response_handler,
        'process_stp_show_counters': generic_show_response_handler,
        'process_stp_show_inconsistentports': generic_show_response_handler,
	    'get_openconfig_spanning_tree_stp_interfaces': generic_show_response_handler,
        #config
        'set_stp_global_bpdu_filter': generic_set_response_handler,
        'set_stp_global_mode': generic_set_response_handler,
        'set_stp_global_forwarding_delay': generic_set_response_handler,
        'set_stp_global_rootguard_timeout': generic_set_response_handler,
        'set_stp_global_hello_time': generic_set_response_handler,
        'set_stp_global_max_age': generic_set_response_handler,
        'set_stp_global_bridge_priority': generic_set_response_handler,
        'set_stp_global_loop_guard': generic_set_response_handler,
        'set_stp_global_portfast': generic_set_response_handler, 
        'set_stp_vlan_subcmds': generic_set_response_handler,
        'set_stp_intf_vlan_subcmds': generic_set_response_handler,
        'set_stp_intf_link_type': generic_set_response_handler,
        'set_stp_intf_edge_port': generic_set_response_handler,
        'set_stp_intf_bpdu_filter': generic_set_response_handler,
        'set_stp_intf_bpdu_guard': generic_set_response_handler,
        'set_stp_intf_guard': generic_set_response_handler,
        'set_stp_intf_cost': generic_set_response_handler,
        'set_stp_intf_enable': generic_set_response_handler,
        'set_stp_intf_portfast': generic_set_response_handler,
        'set_stp_intf_port_priority': generic_set_response_handler,
        'set_stp_intf_uplink_fast': generic_set_response_handler,
        #delete
        'del_stp_global_mode': generic_delete_response_handler,
        'del_stp_global_forwarding_delay': generic_delete_response_handler,
        'del_stp_global_rootguard_timeout': generic_delete_response_handler,
        'del_stp_global_hello_time': generic_delete_response_handler,
        'del_stp_global_max_age': generic_delete_response_handler,
        'del_stp_global_bridge_priority': generic_delete_response_handler,
        'del_stp_intf_bpdu_filter': generic_delete_response_handler,
        'del_stp_intf_bpdu_guard': generic_delete_response_handler,
        'del_stp_intf_cost': generic_delete_response_handler,
        'del_stp_intf_guard': generic_delete_response_handler,
        'del_stp_vlan_subcmds': generic_delete_response_handler,
        'del_stp_intf_vlan_subcmds': generic_delete_response_handler,
        'del_stp_intf_port_priority': generic_delete_response_handler,
        'del_stp_intf_link_type': generic_delete_response_handler,
        'del_stp_intf_edge_port' : generic_delete_response_handler,
        }


def is_stp_mode_mandatory_prerequisite(op_str, new_args):
    if op_str == 'set_stp_global_mode':
        return False
    if op_str == 'del_stp_vlan_subcmds' or op_str == 'set_stp_vlan_subcmds':
        if new_args[0] not in ['hello-time', 'priority', 'max-age', 'forward-time']:
            return False
    return True


def run(op_str, args):
    global g_stp_mode
    global g_stp_resp
    global g_stp_data

    g_stp_mode = None
    g_stp_resp = None
    g_stp_data = {}

    try:
        new_args = []
        for arg in args:
            if isinstance(arg, str):
                arg = arg.strip()

            if arg == 'True':
                arg = True
            elif arg == 'False':
                arg = False

            new_args.append(arg)

        op_str = op_str.strip()

        if op_str == 'show_running_spanning_tree':
            return show_running_spanning_tree()

        #configs allowed before STP mode config

        if is_stp_mode_mandatory_prerequisite(op_str, new_args):
            stp_mode_get(aa)
            if not g_stp_mode:
                #show commands should not return error
                if 'process_stp_show' in op_str:
                    return 0
                else:
                    return -1

        resp = request_handlers[op_str](new_args)
        if not resp:
            if 'process_stp_show' in op_str:
                return 0
            else:
                return -1
        else:
            if 'process_stp_show' in op_str:
                if len(resp.keys()) == 1 and 'openconfig-spanning-tree:enabled-protocol' in resp.keys():
                    return 0

        response_handlers[op_str](resp, new_args)
    except Exception as e:
        print("%Error: {}".format(str(e)))
        sys.exit(-1)

    return 0


g_max_age = 20
g_br_prio = 32768
g_fwd_delay = 15
g_hello_time = 2

def show_run_config_interface(intf_dict, vlan_list=[]):
    cmd = ''
    if 'openconfig-spanning-tree-ext:spanning-tree-enable' in intf_dict.keys() and \
            intf_dict['openconfig-spanning-tree-ext:spanning-tree-enable'] == False:
        cmd += '\n no spanning-tree enable'

    if 'openconfig-spanning-tree-ext:portfast' in intf_dict.keys() and \
            intf_dict['openconfig-spanning-tree-ext:portfast'] == True:
        cmd += '\n spanning-tree portfast'

    cmd_prfx = '\n spanning-tree '

    if 'bpdu-filter' in intf_dict.keys():
        if intf_dict["bpdu-filter"] == True:
            cmd += cmd_prfx + 'bpdufilter enable'
        else:
            cmd += cmd_prfx + 'bpdufilter disable'

    if 'guard' in intf_dict.keys():
        if intf_dict['guard'] == "ROOT":
            cmd += cmd_prfx + 'guard root'
        elif intf_dict['guard'] == "LOOP":
            cmd += cmd_prfx + 'guard loop'
        elif intf_dict['guard'] == "NONE":
            cmd += cmd_prfx + 'guard none'

    if 'bpdu-guard' in intf_dict.keys() and intf_dict['bpdu-guard'] == True:
        if 'openconfig-spanning-tree-ext:bpdu-guard-port-shutdown' in intf_dict.keys() and \
                intf_dict['openconfig-spanning-tree-ext:bpdu-guard-port-shutdown'] == True:
            cmd += cmd_prfx + 'bpduguard port-shutdown'
        else:
            cmd += cmd_prfx + 'bpduguard'

    if 'openconfig-spanning-tree-ext:cost' in intf_dict.keys():
        cmd += cmd_prfx + 'cost ' + str(intf_dict['openconfig-spanning-tree-ext:cost'])


    if 'link-type' in intf_dict.keys():
        if intf_dict["link-type"] == "SHARED":
            cmd += cmd_prfx + 'link-type shared'
        if intf_dict["link-type"] == "P2P":
            cmd += cmd_prfx + 'link-type point-to-point'

    if 'openconfig-spanning-tree-ext:port-priority' in intf_dict.keys():
        cmd += cmd_prfx + 'port-priority ' + str(intf_dict['openconfig-spanning-tree-ext:port-priority'])

    if 'edge-port' in intf_dict.keys():
        if intf_dict['edge-port'] == "openconfig-spanning-tree-types:EDGE_ENABLE":
            cmd += cmd_prfx + 'port type edge'

    if 'openconfig-spanning-tree-ext:uplink-fast' in intf_dict.keys() and \
            intf_dict['openconfig-spanning-tree-ext:uplink-fast'] == True:
        cmd += cmd_prfx + 'uplinkfast'

    if len(vlan_list) != 0:
        vdata = {'cost' : {}, 'port-priority' : {}}
        for vlan_dict in vlan_list:
            vid = vlan_dict['vlan-id']
            if 'interfaces' in vlan_dict.keys():
                if 'interface' in vlan_dict['interfaces']:
                    vport_list = vlan_dict['interfaces']['interface']
                    for vport_dict in vport_list:
                        if 'config' not in vport_dict.keys():
                            continue
                        if vport_dict['name'] == intf_dict['name']:
                            for param in ['cost', 'port-priority']:
                                if param in vport_dict['config'].keys():
                                    val = vport_dict['config'][param]
                                    if val in vdata[param].keys():
                                        vdata[param][val].append(vid)
                                    else:
                                        vdata[param][val] = [vid]

        for param in ['cost', 'port-priority']:
            configured_values = vdata[param].keys()
            if len(configured_values) == 0:
                continue

            configured_values = sorted(configured_values)

            for val in configured_values:
                vrange_str = convert_list_to_range_groups(vdata[param][val])
                cmd += ' '.join(['\n spanning-tree', 'vlan', vrange_str, param, str(val)])

    if len(cmd) != 0:
        ifname = intf_dict['name'].strip()
        if ifname.startswith('PortChannel'):
            po_num = ifname[len('PortChannel'):]
            print('!\ninterface PortChannel ' + po_num + cmd)
        else:
            print('!\ninterface ' + ifname + cmd)
            
    return


def _convert_list_to_range_groups(vlist):

    vlist = sorted(vlist)

    start = vlist[0]
    end = vlist[0]
    for item in vlist[1:]:
        if item - end == 1:
            end = item
        else:
            if start == end:
                yield(str(start))
            else:
                yield("{}-{}".format(start, end))

            start = item
            end = item

    if start == end:
        yield(str(start))
    else:
        yield("{}-{}".format(start, end))


def convert_list_to_range_groups(vlist):
    vlist_len = len(vlist)
    if vlist_len == 0:
        return None

    if not all(isinstance(item, int) for item in vlist):
        return None

    vrange_list = list(_convert_list_to_range_groups(vlist))
    return ','.join(vrange_list)


def show_run_config_vlan(vlan_data, g_stp):
    cmd_list = []
    vlan_params_name_map = {'bridge-priority': 'priority', 'hello-time': 'hello-time', 'forwarding-delay': 'forward-time', 'max-age': 'max-age'}
    # dictionary holding list of vlans with common value
    vdata = {'bridge-priority':{}, 'hello-time':{}, 'forwarding-delay':{}, 'max-age':{}}

    for vlan_dict in vlan_data:
        if 'vlan-id' not in vlan_dict.keys() or 'config' not in vlan_dict.keys():
            continue

        vid = vlan_dict['vlan-id']
        vconf_dict = vlan_dict['config']
        # if all fileds are 0, nothing to print, 
        # this can happen when only enabled key is set in the STP_VLAN table
        if all(key in vconf_dict.keys() for key in vlan_params_name_map.keys()):
            if all(vconf_dict[key] == 0 for key in vlan_params_name_map.keys()):
                continue 

        for key in vlan_params_name_map.keys():
            if key not in vconf_dict.keys():
                continue
            val = vconf_dict[key]
            if val != g_stp[key]:
                if val not in vdata[key].keys():
                    vdata[key][val] = [vid]
                else:
                    vdata[key][val].append(vid)

        '''
        no spanning-tree vlan 55,101-111,113-199,400,500,3000-3900
        spanning-tree vlan 100 priority 61440
        spanning-tree vlan 111 priority 4096
        spanning-tree vlan 100 hello-time 4
        spanning-tree vlan 101-103,105-111 hello-time 3
        spanning-tree vlan 100 forward-time 14
        spanning-tree vlan 101-103,105-111 forward-time 22
        spanning-tree vlan 100 max-age 7
        spanning-tree vlan 101-103,105-111 max-age 6
        '''

    for key in vlan_params_name_map.keys():
        configured_values = vdata[key].keys()
        if len(configured_values) == 0:
            continue
    
        configured_values = sorted(configured_values)

        for val in configured_values:
            vrange_str = convert_list_to_range_groups(vdata[key][val])
            cmd_list.append(' '.join(['spanning-tree', 'vlan', vrange_str, vlan_params_name_map[key], str(val)]))
        
    if len(cmd_list) != 0:
        print('\n'.join(cmd_list))
    return

def show_run_disabled_vlans():
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:disabled-vlans')  
    api_response = aa.get(uri, None)
    disabled_vlans = []
    if api_response.ok() and api_response.content is not None:
        if 'openconfig-spanning-tree-ext:disabled-vlans' in api_response.content:
            disabled_vlans = natsorted(api_response.content['openconfig-spanning-tree-ext:disabled-vlans'])
    if len(disabled_vlans) > 0:
        disabled_vlans = [str(vlan).replace('..','-') for vlan in disabled_vlans]
        print('no spanning-tree vlan {}'.format(','.join(disabled_vlans)))
    return 

'''
def show_run_disabled_vlans(vlan_list, stp_mode):
    cmd = ''
    for vlan_dict in vlan_list:
        if 'config' not in vlan_dict.keys():
            continue

        if stp_mode == "openconfig-spanning-tree-ext:pvst":
            if 'spanning-tree-enable' in vlan_dict['config'].keys() and \
                    vlan_dict['config']['spanning-tree-enable'] == False:
                cmd += '\nno spanning-tree vlan ' + str(vlan_dict['vlan-id'])
        elif stp_mode == 'rapid-pvst':
            if 'openconfig-spanning-tree-ext:spanning-tree-enable' in vlan_dict['config'].keys() and \
                    vlan_dict['config']['openconfig-spanning-tree-ext:spanning-tree-enable'] == False:
                cmd += '\nno spanning-tree vlan ' + str(vlan_dict['vlan-id'])

    if len(cmd) != 0:
        print('!' + cmd)
    return 
'''

def show_run_config_global(data, stp_mode):
    global g_max_age
    global g_br_prio
    global g_fwd_delay
    global g_hello_time

    if stp_mode == "openconfig-spanning-tree-ext:pvst":
        print('spanning-tree mode pvst')
    elif stp_mode == 'rapid-pvst':
        print('spanning-tree mode rapid-pvst')
    else:
        return 

    global_config = data['config']

    if 'bpdu-filter' in global_config.keys() and global_config['bpdu-filter'] == True:
        print('spanning-tree edge-port bpdufilter default')

    if 'openconfig-spanning-tree-ext:forwarding-delay' in global_config.keys() and \
            global_config['openconfig-spanning-tree-ext:forwarding-delay'] != 15:
        g_fwd_delay = global_config['openconfig-spanning-tree-ext:forwarding-delay']
        print('spanning-tree forward-time {}'.format(global_config['openconfig-spanning-tree-ext:forwarding-delay']))

    if 'openconfig-spanning-tree-ext:rootguard-timeout' in global_config.keys() and \
            global_config['openconfig-spanning-tree-ext:rootguard-timeout'] != 30:
        print('spanning-tree guard root timeout {}'.format(global_config['openconfig-spanning-tree-ext:rootguard-timeout']))

    if 'openconfig-spanning-tree-ext:hello-time' in global_config.keys() and \
            global_config['openconfig-spanning-tree-ext:hello-time'] != 2:
        g_hello_time = global_config['openconfig-spanning-tree-ext:hello-time']
        print('spanning-tree hello-time {}'.format(global_config['openconfig-spanning-tree-ext:hello-time']))

    if 'openconfig-spanning-tree-ext:max-age' in global_config.keys() and \
            global_config['openconfig-spanning-tree-ext:max-age'] != 20:
        g_max_age = global_config['openconfig-spanning-tree-ext:max-age']
        print('spanning-tree max-age {}'.format(global_config['openconfig-spanning-tree-ext:max-age']))

    if 'openconfig-spanning-tree-ext:bridge-priority' in global_config.keys() and \
            global_config['openconfig-spanning-tree-ext:bridge-priority'] != 32768:
        g_br_prio = global_config['openconfig-spanning-tree-ext:bridge-priority']
        print('spanning-tree priority {}'.format(global_config['openconfig-spanning-tree-ext:bridge-priority']))

    if 'loop-guard' in global_config.keys() and global_config['loop-guard'] != False:
        print('spanning-tree loopguard default')

    if 'openconfig-spanning-tree-ext:portfast' in global_config.keys() and \
            global_config['openconfig-spanning-tree-ext:portfast'] != False:
        print('spanning-tree portfast default')

    return


def show_running_spanning_tree():
    stp_mode = ''
    aa = cc.ApiClient()

    show_run_disabled_vlans()
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp')  
    api_response = aa.get(uri, None)
    if api_response.ok() and api_response.content is not None:
        data = api_response.content['openconfig-spanning-tree:stp']
        if 'global' in data.keys() and \
                'config' in data['global'].keys() and \
                'enabled-protocol' in data['global']['config'] and \
                len(data['global']['config']['enabled-protocol']) != 0:
            if "openconfig-spanning-tree-types:RAPID_PVST" in data['global']['config']['enabled-protocol'][0]:
                stp_mode = 'rapid-pvst'
            elif "openconfig-spanning-tree-ext:PVST" in data['global']['config']['enabled-protocol'][0]:
                stp_mode = 'openconfig-spanning-tree-ext:pvst'
            else:
                return
            show_run_config_global(data['global'], stp_mode)

            if stp_mode in data.keys():
                if 'vlan' in data[stp_mode].keys():
                    g_stp = {}
                    g_stp['forwarding-delay'] = g_fwd_delay
                    g_stp['hello-time'] = g_hello_time
                    g_stp['max-age'] = g_max_age
                    g_stp['bridge-priority'] = g_br_prio
                    show_run_config_vlan(data[stp_mode]['vlan'], g_stp)
                    #for vlan_dict in data[stp_mode]['vlan']:
                        #show_run_config_vlan(vlan_dict['config'])

            if 'interfaces' in data.keys():
                if 'interface' in data['interfaces'].keys():
                    for intf_dict in data['interfaces']['interface']:
                        vlan_list = []
                        if stp_mode in data.keys():
                            if 'vlan' in data[stp_mode].keys():
                                vlan_list = data[stp_mode]['vlan']

                        show_run_config_interface(intf_dict['config'], vlan_list=vlan_list)

    return 


