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

aa = cc.ApiClient()

g_stp_mode = None
g_stp_resp = None

def stp_mode_get(aa):
    global g_stp_mode
    global g_stp_resp

    g_stp_resp = aa.get('/restconf/data/openconfig-spanning-tree:stp/global/config/enabled-protocol', None)
    if not g_stp_resp.ok():
        print ("%Error: Entry not found or STP not enabled")
        return g_stp_resp,g_stp_mode

    #g_stp_resp = aa.api_client.sanitize_for_serialization(g_stp_resp)

    if g_stp_resp['openconfig-spanning-tree:enabled-protocol'][0] == "openconfig-spanning-tree-ext:PVST":
        g_stp_mode = "PVST"
    elif g_stp_resp['openconfig-spanning-tree:enabled-protocol'][0] == "openconfig-spanning-tree-types:RAPID_PVST":
        g_stp_mode = "RAPID_PVST"
    else:
        print ("%Error: Invalid STP mode")

    return g_stp_resp,g_stp_mode


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
        return patch_stp_vlan_enable(args)

    return None



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
    body = None
    if (len(args) > 1):
        if args[1]:
            body = { "openconfig-spanning-tree-ext:spanning-tree-enable": True }
        else:
            body = { "openconfig-spanning-tree-ext:spanning-tree-enable": False }
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}/config/spanning-tree-enable', vlan_id=args[0])
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}/config/openconfig-spanning-tree-ext:spanning-tree-enable',vlan_id=args[0])
    else:
        return None

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
    if len(args) == 2:
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
        if args[2].strip() == 'auto':
            return delete_stp_intf_link_type([ifname])
        elif args[2].strip() == 'point-to-point':
            return patch_stp_intf_link_type([ifname, 'P2P'])
        elif args[2].strip() == 'shared':
            return patch_stp_intf_link_type([ifname, 'SHARED'])
        else:
            return None
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
    body = { "openconfig-spanning-tree:guard": 'ROOT' }
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces/interface={name}/config/guard', name=args[0])
    return aa.patch(uri, body)


def config_stp_vlan_intf_subcmds(args):
    if args[0] == 'cost':
        return patch_stp_vlan_intf_cost(args[1:])
    elif args[0] == 'priority':
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
    body = { "openconfig-spanning-tree:link-type": args[1] }
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
        if len(args) == 3:
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


def delete_stp_vlan_intf_config(args):
    if args[0] == 'cost':
        return delete_stp_vlan_intf_cost(args[1:])
    elif args[0] == 'port-priority':
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
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst')
    else:
        return None

    output = {}
    api_response = aa.get(uri, None)
    if api_response.ok():
        output.update(g_stp_resp.content)
        output.update(api_response.content)
    return output


def get_stp_vlan_response(vlan):
    if g_stp_mode == 'PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan={vlan_id}', vlan_id=vlan)
    elif g_stp_mode == 'RAPID_PVST':
        uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/rapid-pvst/vlan={vlan_id}', vlan_id=vlan)
    else:
        return None

    output = {}
    api_response = aa.get(uri, None)
    if api_response.ok():
        output.update(g_stp_resp.content)
        output.update(api_response.content)
    return output


def show_stp_intfs(args):
    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/interfaces')
    stp_intf_response = aa.get(uri, None)
    if stp_intf_response.ok():
        return stp_intf_response.content
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
    if stp_intf_response.ok():
        output.update(stp_intf_response.content)

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
    if stp_global_response.ok():
        output.update(stp_global_response.content)

    return output


def show_stp_inconsistentports_vlan(args):
    output = get_stp_vlan_response(args[1])
    if not output:
        return None

    uri = cc.Path('/restconf/data/openconfig-spanning-tree:stp/global/config')
    stp_global_response = aa.get(uri, None)
    if stp_global_response.ok():
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

        if op_str != 'post_openconfig_spanning_tree_stp_global_config_enabled_protocol':
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

