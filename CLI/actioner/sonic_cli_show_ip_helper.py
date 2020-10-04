#!/usr/bin/python
###########################################################################
#
# Copyright 2020 Broadcom, Inc.
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
from scripts.render_cli import show_cli_output
import syslog as log

use_sonic_db = True

def shortcut_ip_helper_config_data(output):
    del_list = []
    if "openconfig-ip-helper:interfaces" in output:
        interfaces = output["openconfig-ip-helper:interfaces"]
        if "interface" in interfaces:
            interfacelist = interfaces["interface"]
            for i, interface in enumerate(interfacelist):
                if "servers" in interface:
                    output[interface["id"]] = {}
                    output[interface["id"]]["openconfig-ip-helper:servers"] = interface["servers"]
                else:
                    del_list.append(i)

    for item in reversed(del_list):
        output["openconfig-interfaces:interfaces"]["interface"].pop(item)
    return output

def shortcut_ip_helper_counters_data(output):
    del_list = []
    if "openconfig-ip-helper:interfaces" in output:
        interfaces = output["openconfig-ip-helper:interfaces"]
        if "interface" in interfaces:
            interfacelist = interfaces["interface"]
            for i, interface in enumerate(interfacelist):
                if "state" in interface:
                    state = interface["state"]
                    if "counters" in state:
                        counters = state["counters"]
                        output[interface["id"]] = {}
                        output[interface["id"]]["openconfig-ip-helper:counters"] = counters
                    else:
                        del_list.append(i)
                else:
                    del_list.append(i)

    for item in reversed(del_list):
        output["openconfig-interfaces:interfaces"]["interface"].pop(item)
    return output

def build_helper_counters_info ():
    api = cc.ApiClient()
    output = {}

    keypath = cc.Path("/restconf/data/sonic-ip-helper:sonic-ip-helper/COUNTERS_IP_HELPER/COUNTERS_IP_HELPER_LIST")
    try:
        response = api.get(keypath)
        response = response.content
        if response is None:
            return output
        intfsList = response.get("sonic-ip-helper:COUNTERS_IP_HELPER_LIST")
        if intfsList is None:
            return output
        for intf in intfsList:
            intfName = intf.get("interface")
            output[intfName] = intf
    except  Exception as e:
        log.syslog(log.LOG_ERR, str(e))
        print "%Error: Internal error"
    return output

def build_helper_address_info ():
    api = cc.ApiClient()
    output = {}

    tIntf = ("/restconf/data/sonic-interface:sonic-interface/INTERFACE/INTERFACE_LIST",
             "sonic-interface:INTERFACE_LIST",
             "portname")
    tVlanIntf = ("/restconf/data/sonic-vlan-interface:sonic-vlan-interface/VLAN_INTERFACE/VLAN_INTERFACE_LIST",
                 "sonic-vlan-interface:VLAN_INTERFACE_LIST",
                 "vlanName")
    tPortChannelIntf = ("/restconf/data/sonic-portchannel-interface:sonic-portchannel-interface/PORTCHANNEL_INTERFACE/PORTCHANNEL_INTERFACE_LIST",
                        "sonic-portchannel-interface:PORTCHANNEL_INTERFACE_LIST",
                        "pch_name")

    requests = [tIntf, tVlanIntf, tPortChannelIntf]

    for request in requests:
        keypath = cc.Path(request[0])
        try:
            response = api.get(keypath)
            response = response.content
            if response is None:
                continue
            intfsList = response.get(request[1])
            if intfsList is None:
                continue
            for intf in intfsList:
                intfName = intf.get(request[2])
                if intfName is None:
                    continue
                helper_addresses = intf.get('helper_addresses')
                if helper_addresses is None:
                    continue
                output[intfName] = helper_addresses
        except  Exception as e:
            log.syslog(log.LOG_ERR, str(e))
            print "%Error: Internal error"
    return output

def invoke_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    
    if func == 'global_config':
        keypath = cc.Path('/restconf/data/openconfig-ip-helper:ip-helper/state')
        response = api.get(keypath)
        return response
    elif func == 'iface_config':
        if len(args) > 0:
            keypath = cc.Path('/restconf/data/openconfig-ip-helper:ip-helper/interfaces/interface={iface}/servers',
                    iface=args[0])
            response = api.get(keypath)
            output = response.content
            if response.ok() and response.content is not None:
                response.content[args[0]] = output
            return response
        else:
            keypath = cc.Path('/restconf/data/openconfig-ip-helper:ip-helper/interfaces')
            response = api.get(keypath)
            shortcut_ip_helper_config_data(response.content)
            return response
    elif func == 'iface_stats':
        if len(args) > 0:
            keypath = cc.Path('/restconf/data/openconfig-ip-helper:ip-helper/interfaces/interface={iface}/state/counters',
                    iface=args[0])
            response = api.get(keypath)
            output = response.content
            if response.ok() and response.content is not None:
                response.content[args[0]] = output
            return response
        else:
            keypath = cc.Path('/restconf/data/openconfig-ip-helper:ip-helper/interfaces')
            response = api.get(keypath)
            shortcut_ip_helper_counters_data(response.content)
            return response
    else:
        body = {}

    return api.cli_not_implemented(func)

def run(func, args):
    renderer = args[0]
    if use_sonic_db:
        if len(args) < 2:
            if func == 'iface_config':
                output = build_helper_address_info()
                show_cli_output('show_ip_helper_interface_config_sonic.j2', output)
                return
            elif func == 'iface_stats':
                output = build_helper_counters_info()
                show_cli_output('show_ip_helper_interface_statistics_sonic.j2', output)
                return
    response = invoke_api(func, args[1:])
    if response.ok():
        if response.content is not None:
            api_response = response.content
            #print(api_response)
            show_cli_output(renderer, api_response)
        else:
            print("Empty response")
    else:
        print(response.error_message())

#if __name__ == '__main__':
#    pipestr().write(sys.argv)
#    func = sys.argv[1]
    #run(func, sys.argv[3:], sys.argv[2])

