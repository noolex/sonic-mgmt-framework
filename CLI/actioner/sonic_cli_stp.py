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

aa = cc.ApiClient()

g_stp_mode = None
g_stp_resp = None

def stp_mode_get(aa):
    global g_stp_mode
    global g_stp_resp

    g_stp_resp = aa.get('/restconf/data/openconfig-spanning-tree:stp/global/config', None, False)
    if not g_stp_resp.ok():
        print ("%Error: Entry not found or STP not enabled")
        return g_stp_resp,g_stp_mode

    #g_stp_resp = aa.api_client.sanitize_for_serialization(g_stp_resp)

    if g_stp_resp['openconfig-spanning-tree:config']['enabled-protocol'][0] == "openconfig-spanning-tree-ext:PVST":
        g_stp_mode = "PVST"
    elif g_stp_resp['openconfig-spanning-tree:config']['enabled-protocol'][0] == "openconfig-spanning-tree-types:RAPID_PVST":
        g_stp_mode = "RAPID_PVST"
    else:
        print ("%Error: Invalid STP mode")

    return g_stp_resp,g_stp_mode

def getId(item):
    ifName = item['name']
    return ifutils.name_to_int_val(ifName)

def generic_set_response_handler(response, args):
    #if response.ok():
        #resp_content = response.content
        #if resp_content is not None:
            #print("%Error: {}".format(str(resp_content)))
    #else:
    if not response.ok():
        print(response.error_message())


def generic_delete_response_handler(response, args):
    if response.ok():
        resp_content = response.content
        if resp_content is not None:
            print("%Error: {}".format(str(resp_content)))
    elif response.status_code != '404':
        print(response.error_message())


def generic_show_response_handler(output_data, args):
    j2_tmpl = args[0]
    show_cli_output(j2_tmpl, output_data)


def post_stp_global_enable(args):
    mode = args[0].strip()
    if mode == 'pvst' or mode == '':
        body = { "openconfig-spanning-tree:enabled-protocol": ['PVST'] }
    elif mode == 'rapid-pvst':
        body = { "openconfig-spanning-tree:enabled-protocol": ['RAPID_PVST'] }
    else:
        print('%Error: Invalid mode')
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config')
    return aa.post(uri, body)


def patch_stp_global_bpdu_filter(args):
    body = { "openconfig-spanning-tree:bpdu-filter": True if args[0] else False }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/bpdu-filter')
    return aa.patch(uri, body)

def config_stp_loopguard(args):
    body = { "openconfig-spanning-tree:loop-guard": args[0] }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/loop-guard')
    return aa.patch(uri, body)

def config_stp_portfast(args):
    body = {"openconfig-spanning-tree-ext:portfast": args[0]}
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:portfast')
    return aa.patch(uri, body)


def delete_stp_vlan_config(args):
    op_str = args[0].strip()
    if op_str == 'hello-time':
        return delete_stp_vlan_hello_time(args[1:])
    elif op_str == 'priority':
        return delete_stp_vlan_bridge_priority(args[1:])
    elif op_str == 'max-age':
        return delete_stp_vlan_max_age(args[1:])
    elif op_str == 'forward-time':
        return delete_stp_vlan_fwd_delay(args[1:])
    else:
        return patch_stp_vlan_disable(args)


def config_stp_vlan_subcmds(args):
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


def patch_stp_vlan_fwd_delay(args):
    body = { "openconfig-spanning-tree:forwarding-delay": int(args[1]) }
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}/config/forwarding-delay', vlan_id=args[0])
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}/config/forwarding-delay', vlan_id=args[0])
    else:
        return None

    return aa.patch(uri, body)


def patch_stp_vlan_hello_time(args):
    body = { "openconfig-spanning-tree:hello-time": int(args[1]) }
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}/config/hello-time', vlan_id=args[0])
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}/config/hello-time', vlan_id=args[0])
    else:
        return None

    return aa.patch(uri, body)


def patch_stp_vlan_max_age(args):
    body = { "openconfig-spanning-tree:max-age": int(args[1]) }
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}/config/max-age', vlan_id=args[0])
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}/config/max-age', vlan_id=args[0])
    else:
        return None

    return aa.patch(uri, body)


def patch_stp_vlan_bridge_priority(args):
    body = { "openconfig-spanning-tree:bridge-priority": int(args[1]) }
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}/config/bridge-priority', vlan_id=args[0])
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}/config/bridge-priority', vlan_id=args[0])
    else:
        return None

    return aa.patch(uri, body)


def patch_stp_vlan_enable(args):
    body = { "openconfig-spanning-tree-ext:spanning-tree-enable": True }
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}/config/spanning-tree-enable', vlan_id=args[0])
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}/config/openconfig-spanning-tree-ext:spanning-tree-enable',vlan_id=args[0])
    else:
        return None

    return aa.patch(uri, body)

def patch_stp_vlan_disable(args):
    body = {"openconfig-spanning-tree-ext:disabled-vlans": [int(args[0])]}
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:disabled-vlans')
    return aa.patch(uri, body)

def patch_stp_global_fwd_delay(args):
    body = {"openconfig-spanning-tree-ext:forwarding-delay": int(args[0])}
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:forwarding-delay')
    return aa.patch(uri, body)


def patch_stp_global_rootguard_timeout(args):
    body = {"openconfig-spanning-tree-ext:rootguard-timeout": int(args[0])}
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:rootguard-timeout')
    return aa.patch(uri, body)


def patch_stp_global_hello_time(args):
    body = {"openconfig-spanning-tree-ext:hello-time": int(args[0])}
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:hello-time')
    return aa.patch(uri, body)


def patch_stp_global_max_age(args):
    body = {"openconfig-spanning-tree-ext:max-age": int(args[0])}
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:max-age')
    return aa.patch(uri, body)


def patch_stp_global_bridge_priority(args):
    body = {"openconfig-spanning-tree-ext:bridge-priority": int(args[0])}
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:bridge-priority')
    return aa.patch(uri, body)


def config_stp_intf_bpdu_guard_subcmds(args):
    ifname  = args[0].strip()
    if args[1].strip() == "port-shutdown":
        return patch_stp_intf_bpdu_guard_shutdown([ifname, True])
    else:
        return patch_stp_intf_bpdu_guard([ifname, True])


def config_stp_intf_subcmds(args):
    sub_cmd = args[0].strip()
    ifname  = args[1].strip()
    if sub_cmd == 'bpduguard':
        if len(args) == 3:
            return patch_stp_intf_bpdu_guard_shutdown([ifname, True])
        else:
            return patch_stp_intf_bpdu_guard([ifname, True])
    elif sub_cmd == 'portfast':
        return patch_stp_intf_portfast([ifname, True])
    elif sub_cmd == "uplinkfast":
        return patch_stp_intf_uplink_fast([ifname, True])
    elif sub_cmd == "enable":
        return patch_stp_intf_enable([ifname, True])
    elif sub_cmd == "cost":
        value   = args[2].strip()
        return patch_stp_intf_cost([ifname, value])
    elif sub_cmd == "port-priority":
        value   = args[2].strip()
        return patch_stp_intf_port_priority([ifname, value])
    elif sub_cmd == "link-type":
        return patch_stp_intf_link_type([ifname, args[2]])
    elif sub_cmd == "port":
        if len(args) == 3:
            return patch_stp_intf_edge_port([ifname, True])
        else:
            return None
    else:
        return None
    


def patch_stp_intf_bpdu_guard_shutdown(args):
    body = None
    if args[1]:
        body = { "openconfig-spanning-tree-ext:bpdu-guard-port-shutdown": True }
    else:
        body = { "openconfig-spanning-tree-ext:bpdu-guard-port-shutdown": False }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/openconfig-spanning-tree-ext:bpdu-guard-port-shutdown', name=args[0])
    return aa.patch(uri, body)


def patch_stp_intf_portfast(args):
    body = None
    if args[1]:
        body = { "openconfig-spanning-tree-ext:portfast": True }
    else:
        body = { "openconfig-spanning-tree-ext:portfast": False }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/openconfig-spanning-tree-ext:portfast', name=args[0])
    return aa.patch(uri, body)


def patch_stp_intf_uplink_fast(args):
    body = None
    if args[1]:
        body = { "openconfig-spanning-tree-ext:uplink-fast": True }
    else:
        body = { "openconfig-spanning-tree-ext:uplink-fast": False }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/openconfig-spanning-tree-ext:uplink-fast', name=args[0])
    return aa.patch(uri, body)


def patch_stp_intf_enable(args):
    body = None
    if args[1]:
        body = { "openconfig-spanning-tree-ext:spanning-tree-enable": True }
    else:
        body = { "openconfig-spanning-tree-ext:spanning-tree-enable": False }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/openconfig-spanning-tree-ext:spanning-tree-enable', name=args[0])
    return aa.patch(uri, body)


def patch_stp_intf_cost(args):
    body = { "openconfig-spanning-tree-ext:cost": int(args[1]) }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/openconfig-spanning-tree-ext:cost', name=args[0])
    return aa.patch(uri, body)


def patch_stp_intf_port_priority(args):
    body = { "openconfig-spanning-tree-ext:port-priority": int(args[1]) }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/openconfig-spanning-tree-ext:port-priority', name=args[0])
    return aa.patch(uri, body)


def patch_stp_intf_edge_port(args):
    body = None
    if args[1]:
        body = { "openconfig-spanning-tree:edge-port": "EDGE_ENABLE" }
    else:
        body = { "openconfig-spanning-tree:edge-port": "EDGE_DISABLE" }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/edge-port', name=args[0])
    return aa.patch(uri, body)


def patch_stp_intf_bpdu_filter(args):
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


def patch_stp_intf_root_guard(args):
    body = None
    if args[1] == "root":
        body = { "openconfig-spanning-tree:guard": "ROOT"}
    elif args[1] == "loop":
        body = { "openconfig-spanning-tree:guard": "LOOP"}
    else:
        body = { "openconfig-spanning-tree:guard": "NONE"}

    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/guard', name=args[0])
    return aa.patch(uri, body)


def config_stp_vlan_intf_subcmds(args):
    sub_cmd = args[0].strip()
    if sub_cmd == "cost":
        return patch_stp_vlan_intf_cost(args[1:])
    elif sub_cmd == "port-priority":
        return patch_stp_vlan_intf_priority(args[1:])
    else:
        return None


def patch_stp_vlan_intf_cost(args):
    body = { "openconfig-spanning-tree:cost": int(args[2])}
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}/interfaces/interface={name}/config/cost', vlan_id=args[0], name=args[1])
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}/interfaces/interface={name}/config/cost', vlan_id=args[0], name=args[1])
    else:
        return None
    return aa.patch(uri, body)


def patch_stp_vlan_intf_priority(args):
    body = { "openconfig-spanning-tree:port-priority": int(args[2])}
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}/interfaces/interface={name}/config/port-priority', vlan_id=args[0], name=args[1])
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}/interfaces/interface={name}/config/port-priority', vlan_id=args[0], name=args[1])
    else:
        return None
    return aa.patch(uri, body)


def patch_stp_intf_link_type(args):
    link_type = ''
    if args[1].strip() == 'point-to-point':
        link_type = 'P2P'
    elif args[1].strip() == 'shared':
        link_type = 'SHARED'
    body = { "openconfig-spanning-tree:link-type": link_type }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/link-type', name=args[0])
    return aa.patch(uri, body)


def delete_stp_global_enable(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config')
    return aa.delete(uri, None)


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


def delete_stp_global_fwd_delay(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:forwarding-delay')
    return aa.delete(uri, None)


def delete_stp_global_rootguard_timeout(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:rootguard-timeout')
    return aa.delete(uri, None)


def delete_stp_global_hello_time(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:hello-time')
    return aa.delete(uri, None)


def delete_stp_global_max_age(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:max-age')
    return aa.delete(uri, None)


def delete_stp_global_bridge_priority(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:bridge-priority')
    return aa.delete(uri, None)

def delete_stp_intf_config(args):
    sub_cmd = args[0].strip()
    ifname  = args[1].strip()
    if sub_cmd == 'bpduguard':
        if len(args) == 4:
            return patch_stp_intf_bpdu_guard_shutdown([ifname, False])
        else:
            return patch_stp_intf_bpdu_guard([ifname, False])
    elif sub_cmd == 'portfast':
        return patch_stp_intf_portfast([ifname, False])
    elif sub_cmd == 'bpdufilter':
        return delete_stp_intf_bpdu_filter([ifname])
    elif sub_cmd == "uplinkfast":
        return patch_stp_intf_uplink_fast([ifname, False])
    elif sub_cmd == "enable":
        return patch_stp_intf_enable([ifname, False])
    elif sub_cmd == "cost":
        return delete_stp_intf_cost([ifname])
    elif sub_cmd == "port-priority":
        return delete_stp_intf_port_priority([ifname])
    elif sub_cmd == "link-type":
        return delete_stp_intf_link_type([ifname])
    elif sub_cmd == "port":
        if len(args) == 3:
            return patch_stp_intf_edge_port([ifname, False])
        else:
            return None
    else:
        return None


def delete_stp_intf_cost(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/openconfig-spanning-tree-ext:cost', name=args[0])
    return aa.delete(uri, None)


def delete_stp_intf_port_priority(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/openconfig-spanning-tree-ext:port-priority', name=args[0])
    return aa.delete(uri, None)


def delete_stp_intf_bpdu_filter(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/bpdu-filter', name=args[0])
    return aa.delete(uri, None)

def delete_stp_intf_guard(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/guard', name=args[0])
    return aa.delete(uri, None)

def delete_stp_vlan_intf_config(args):
    if args[0].strip() == "cost":
        return delete_stp_vlan_intf_cost(args[1:])
    elif args[0].strip() == "port-priority":
        return delete_stp_vlan_intf_priority(args[1:])
    else:
        return None


def delete_stp_intf_bpdu_guard_subcmds(args):
    ifname  = args[0].strip()
    if len(args) == 2:
        return patch_stp_intf_bpdu_guard_shutdown([ifname, False])
    else:
        return patch_stp_intf_bpdu_guard([ifname, False])


def delete_stp_vlan_intf_cost(args):
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}/interfaces/interface={name}/config/cost', vlan_id=args[0], name=args[1])
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}/interfaces/interface={name}/config/cost', vlan_id=args[0], name=args[1])
    else:
        return None
    return aa.delete(uri, None)


def delete_stp_vlan_intf_priority(args):
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}/interfaces/interface={name}/config/port-priority', vlan_id=args[0], name=args[1])
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}/interfaces/interface={name}/config/port-priority', vlan_id=args[0], name=args[1])
    else:
        return None
    return aa.delete(uri, None)


def delete_stp_intf_link_type(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/link-type', name=args[0])
    return aa.delete(uri, None)


def delete_stp_intf_edge_port_subcmds(args):
    ifname  = args[0].strip()
    if len(args) == 2:
        return patch_stp_intf_edge_port([ifname, False])   
    return None


def get_stp_response():
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst')  
        str = 'openconfig-spanning-tree-ext:pvst'
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst')
        str = 'openconfig-spanning-tree:rapid-pvst'
    else:
        return None

    output = {}
    api_response = aa.get(uri, None)
    if api_response.ok() and api_response.content is not None:
        if str in api_response.content and 'vlan' in api_response.content[str]:
            value = api_response.content[str]['vlan']
            for item in value:
                if 'interfaces' in item and 'interface' in item['interfaces']:
                    tup = item['interfaces']['interface']
                    item['interfaces']['interface'] = sorted(tup, key=getId)
        output.update(g_stp_resp.content)
        output.update(api_response.content)
    return output


def get_stp_vlan_response(vlan):
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}', vlan_id=vlan)
        str = 'openconfig-spanning-tree-ext:vlan'
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}', vlan_id=vlan)
        str = 'openconfig-spanning-tree:vlan'
    else:
        return None

    output = {}
    api_response = aa.get(uri, None)
    if api_response.ok() and api_response.content is not None:
        if str in api_response.content:
            value = api_response.content[str]
            for item in value:
                if 'interfaces' in item and 'interface' in item['interfaces']:
                    tup = item['interfaces']['interface']
                    item['interfaces']['interface'] = sorted(tup, key=getId)
     
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
    output = get_stp_vlan_response(args[1])
    if not output:
        return None

    stp_intf_data = show_stp_intfs(args)
    if stp_intf_data:
        output.update(stp_intf_data)

    return output


def show_stp_vlan_intfs(args):
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
        'patch_openconfig_spanning_tree_stp_global_config_bpdu_filter': patch_stp_global_bpdu_filter, 
        'post_openconfig_spanning_tree_stp_global_config_enabled_protocol': post_stp_global_enable,
        'patch_openconfig_spanning_tree_ext_stp_global_config_forwarding_delay': patch_stp_global_fwd_delay,
        'patch_openconfig_spanning_tree_ext_stp_global_config_rootguard_timeout': patch_stp_global_rootguard_timeout,
        'patch_openconfig_spanning_tree_ext_stp_global_config_hello_time': patch_stp_global_hello_time,
        'patch_openconfig_spanning_tree_ext_stp_global_config_max_age': patch_stp_global_max_age,
        'patch_openconfig_spanning_tree_ext_stp_global_config_bridge_priority': patch_stp_global_bridge_priority,
        'patch_openconfig_spanning_tree_stp_global_config_loop_guard': config_stp_loopguard, 
        'patch_openconfig_spanning_tree_ext_stp_global_config_portfast': config_stp_portfast, 
        'config_stp_vlan_subcmds': config_stp_vlan_subcmds,
        'config_stp_if_subcmds': config_stp_intf_subcmds,
        'config_stp_if_vlan_subcmds': config_stp_vlan_intf_subcmds,
        'config_stp_if_link_type_subcmds':patch_stp_intf_link_type,
        'config_stp_if_edge_port':patch_stp_intf_edge_port,
        'config_stp_if_bpdu_filter':patch_stp_intf_bpdu_filter,
        'config_stp_if_bpdu_guard_subcmds': config_stp_intf_bpdu_guard_subcmds,
        'patch_openconfig_spanning_tree_stp_interfaces_interface_config_guard': patch_stp_intf_root_guard,
        'patch_openconfig_spanning_tree_ext_stp_interfaces_interface_config_cost': patch_stp_intf_cost,
        'patch_openconfig_spanning_tree_ext_stp_interfaces_interface_config_spanning_tree_enable': patch_stp_intf_enable,
        'patch_openconfig_spanning_tree_ext_stp_interfaces_interface_config_portfast':patch_stp_intf_portfast,
        'patch_openconfig_spanning_tree_ext_stp_interfaces_interface_config_port_priority':patch_stp_intf_port_priority,
        'patch_openconfig_spanning_tree_ext_stp_interfaces_interface_config_uplink_fast': patch_stp_intf_uplink_fast,
        #delete
        'delete_openconfig_spanning_tree_stp_global_config_enabled_protocol': delete_stp_global_enable,
        'delete_openconfig_spanning_tree_ext_stp_global_config_forwarding_delay': delete_stp_global_fwd_delay,
        'delete_openconfig_spanning_tree_ext_stp_global_config_rootguard_timeout': delete_stp_global_rootguard_timeout,
        'delete_openconfig_spanning_tree_ext_stp_global_config_hello_time': delete_stp_global_hello_time,
        'delete_openconfig_spanning_tree_ext_stp_global_config_max_age': delete_stp_global_max_age,
        'delete_openconfig_spanning_tree_ext_stp_global_config_bridge_priority': delete_stp_global_bridge_priority,
        'delete_openconfig_spanning_tree_stp_interfaces_interface_config_bpdu_filter': delete_stp_intf_bpdu_filter,
        'delete_openconfig_spanning_tree_stp_interfaces_interface_config_guard': delete_stp_intf_guard,
        'delete_stp_vlan_subcmds': delete_stp_vlan_config,
        'delete_stp_if_subcmds': delete_stp_intf_config,
        'delete_stp_if_vlan_subcmds': delete_stp_vlan_intf_config,
        'delete_stp_if_bpdu_guard_subcmds':delete_stp_intf_bpdu_guard_subcmds,
        'delete_openconfig_spanning_tree_ext_stp_interfaces_interface_config_cost': delete_stp_intf_cost,
        'delete_openconfig_spanning_tree_ext_stp_interfaces_interface_config_port_priority': delete_stp_intf_port_priority,
        'delete_custom_stp_vlan_interfaces_interface_config_cost': delete_stp_vlan_intf_cost,
        'delete_custom_stp_vlan_interfaces_interface_config_port_priority': delete_stp_vlan_intf_priority,
        'delete_openconfig_spanning_tree_stp_interfaces_interface_config_link_type': delete_stp_intf_link_type,
        'delete_stp_if_edge_port_subcmds': delete_stp_intf_edge_port_subcmds,
}

response_handlers = {
        #show
        'process_stp_show': generic_show_response_handler,
        'process_stp_show_counters': generic_show_response_handler,
        'process_stp_show_inconsistentports': generic_show_response_handler,
	'get_openconfig_spanning_tree_stp_interfaces': generic_show_response_handler,
        #config
        'patch_openconfig_spanning_tree_stp_global_config_bpdu_filter': generic_set_response_handler,
        'post_openconfig_spanning_tree_stp_global_config_enabled_protocol': generic_set_response_handler,
        'patch_openconfig_spanning_tree_ext_stp_global_config_forwarding_delay': generic_set_response_handler,
        'patch_openconfig_spanning_tree_ext_stp_global_config_rootguard_timeout': generic_set_response_handler,
        'patch_openconfig_spanning_tree_ext_stp_global_config_hello_time': generic_set_response_handler,
        'patch_openconfig_spanning_tree_ext_stp_global_config_max_age': generic_set_response_handler,
        'patch_openconfig_spanning_tree_ext_stp_global_config_bridge_priority': generic_set_response_handler,
        'patch_openconfig_spanning_tree_stp_global_config_loop_guard': generic_set_response_handler,
        'patch_openconfig_spanning_tree_ext_stp_global_config_portfast': generic_set_response_handler, 
        'config_stp_vlan_subcmds': generic_set_response_handler,
        'config_stp_if_subcmds': generic_set_response_handler,
        'config_stp_if_vlan_subcmds': generic_set_response_handler,
        'config_stp_if_link_type_subcmds': generic_set_response_handler,
        'config_stp_if_edge_port': generic_set_response_handler,
        'config_stp_if_bpdu_filter': generic_set_response_handler,
        'config_stp_if_bpdu_guard_subcmds': generic_set_response_handler,
        'patch_openconfig_spanning_tree_stp_interfaces_interface_config_guard': generic_set_response_handler,
        'patch_openconfig_spanning_tree_ext_stp_interfaces_interface_config_cost': generic_set_response_handler,
        'patch_openconfig_spanning_tree_ext_stp_interfaces_interface_config_spanning_tree_enable': generic_set_response_handler,
        'patch_openconfig_spanning_tree_ext_stp_interfaces_interface_config_portfast': generic_set_response_handler,
        'patch_openconfig_spanning_tree_ext_stp_interfaces_interface_config_port_priority': generic_set_response_handler,
        'patch_openconfig_spanning_tree_ext_stp_interfaces_interface_config_uplink_fast': generic_set_response_handler,
        #delete
        'delete_openconfig_spanning_tree_stp_global_config_enabled_protocol': generic_delete_response_handler,
        'delete_openconfig_spanning_tree_ext_stp_global_config_forwarding_delay': generic_delete_response_handler,
        'delete_openconfig_spanning_tree_ext_stp_global_config_rootguard_timeout': generic_delete_response_handler,
        'delete_openconfig_spanning_tree_ext_stp_global_config_hello_time': generic_delete_response_handler,
        'delete_openconfig_spanning_tree_ext_stp_global_config_max_age': generic_delete_response_handler,
        'delete_openconfig_spanning_tree_ext_stp_global_config_bridge_priority': generic_delete_response_handler,
        'delete_openconfig_spanning_tree_stp_interfaces_interface_config_bpdu_filter': generic_delete_response_handler,
        'delete_openconfig_spanning_tree_stp_interfaces_interface_config_guard': generic_delete_response_handler,
        'delete_stp_vlan_subcmds': generic_delete_response_handler,
        'delete_stp_if_subcmds': generic_delete_response_handler,
        'delete_stp_if_vlan_subcmds': generic_delete_response_handler,
        'delete_stp_if_bpdu_guard_subcmds': generic_delete_response_handler,
        'delete_openconfig_spanning_tree_ext_stp_interfaces_interface_config_cost': generic_delete_response_handler,
        'delete_openconfig_spanning_tree_ext_stp_interfaces_interface_config_port_priority': generic_delete_response_handler,
        'delete_custom_stp_vlan_interfaces_interface_config_cost': generic_delete_response_handler,
        'delete_custom_stp_vlan_interfaces_interface_config_port_priority': generic_delete_response_handler,
        'delete_openconfig_spanning_tree_stp_interfaces_interface_config_link_type': generic_delete_response_handler,
        'delete_stp_if_edge_port_subcmds': generic_delete_response_handler,
        }


def run(op_str, args):
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

        #allow vlan delete before mode config
        if op_str not in ['post_openconfig_spanning_tree_stp_global_config_enabled_protocol', 'delete_stp_vlan_subcmds']:
            stp_mode_get(aa)
            if not g_stp_mode:
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
            intf_dict['openconfig-spanning-tree-ext:portfast'] == False:
        cmd += '\n no spanning-tree portfast'

    cmd_prfx = '\n spanning-tree '

    if 'bpdu-filter' in intf_dict.keys():
        if intf_dict["bpdu-filter"] == True:
            cmd += cmd_prfx + 'bpdufilter enable'
        else:
            cmd += cmd_prfx + 'bpdufilter disable'

    if 'guard' in intf_dict.keys() and intf_dict['guard'] == "ROOT":
        cmd += cmd_prfx + 'guard root'

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
        for vlan_dict in vlan_list:
            if 'interfaces' in vlan_dict.keys():
                if 'interface' in vlan_dict['interfaces']:
                    vport_list = vlan_dict['interfaces']['interface']
                    for vport_dict in vport_list:
                        if 'config' not in vport_dict.keys():
                            continue
                        if vport_dict['name'] == intf_dict['name']:
                            if 'cost' in vport_dict['config'].keys():
                                cmd += cmd_prfx + 'vlan ' + str(vlan_dict['vlan-id']) + ' cost ' + str(vport_dict['config']['cost'])
                            if 'port-priority' in vport_dict['config'].keys():
                                cmd += cmd_prfx + 'vlan ' + str(vlan_dict['vlan-id']) + ' port-priority ' + str(vport_dict['config']['port-priority'])

    if len(cmd) != 0:
        ifname = intf_dict['name'].strip()
        if ifname.startswith('PortChannel'):
            po_num = ifname[len('PortChannel'):]
            print('!\ninterface PortChannel ' + po_num + cmd)
        else:
            print('!\ninterface ' + ifname + cmd)
            
    return


def show_run_config_vlan(vlan_dict):
    if 'vlan-id' not in vlan_dict.keys():
        return

    # if all fileds are 0, nothing to print, 
    # this can happen when only enabled key is set in the STP_VLAN table
    keys = ['forwarding-delay', 'hello-time', 'max-age', 'bridge-priority']
    if all(key in vlan_dict.keys() for key in keys):
        if all(vlan_dict[key] == 0 for key in keys):
            return 

    cmd = ''
    prfx = '\nspanning-tree vlan '+ str(vlan_dict['vlan-id']) + ' '
    if 'forwarding-delay' in vlan_dict.keys() \
            and vlan_dict['forwarding-delay'] != g_fwd_delay:
        cmd += prfx + 'forward-time ' + str(vlan_dict['forwarding-delay'])
    if 'hello-time' in vlan_dict.keys() \
            and vlan_dict['hello-time'] != g_hello_time:
        cmd += prfx + 'hello-time ' + str(vlan_dict['hello-time'])
    if 'max-age' in vlan_dict.keys() \
            and vlan_dict['max-age'] != g_max_age:
        cmd += prfx + 'max-age ' + str(vlan_dict['max-age'])
    if 'bridge-priority' in vlan_dict.keys() \
            and vlan_dict['bridge-priority'] != g_br_prio:
        cmd += prfx + 'priority ' + str(vlan_dict['bridge-priority'])

    if len(cmd) != 0:
        print('!' + cmd)
    return


def show_run_disabled_vlans():
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config/openconfig-spanning-tree-ext:disabled-vlans')  
    api_response = aa.get(uri, None)
    if api_response.ok() and api_response.content is not None:
        if 'openconfig-spanning-tree-ext:disabled-vlans' in api_response.content:
            disabled_vlans = api_response.content['openconfig-spanning-tree-ext:disabled-vlans']
            for vlan in disabled_vlans:
                print('no spanning-tree vlan ' + str(vlan))
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
                    #show_run_disabled_vlans(data[stp_mode]['vlan'], stp_mode)

                    for vlan_dict in data[stp_mode]['vlan']:
                        show_run_config_vlan(vlan_dict['config'])

            if 'interfaces' in data.keys():
                if 'interface' in data['interfaces'].keys():
                    for intf_dict in data['interfaces']['interface']:
                        vlan_list = []
                        if stp_mode in data.keys():
                            if 'vlan' in data[stp_mode].keys():
                                vlan_list = data[stp_mode]['vlan']

                        show_run_config_interface(intf_dict['config'], vlan_list=vlan_list)

    return 


