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
import time
import json
import ast
from rpipe_utils import pipestr
import cli_client as cc
from scripts.render_cli import show_cli_output
import collections

IDENTIFIER='VRF'
NAME1='vrf'

def isMgmtVrfEnabled():
    api = cc.ApiClient()
    try:
        request = "/restconf/data/openconfig-network-instance:network-instances/network-instance=mgmt/state/enabled/"

        response = api.get(request)
        response = response.content
        response = response.get('openconfig-network-instance:enabled')
        if response is None:
            return False
        else:
            return True

    except Exception as e:
        log.syslog(log.LOG_ERR, str(e))
        print "%Error: Internal error"

def get_vrf_data(vrf_name, vrf_intf_info):
    api = cc.ApiClient()
    vrf = {}
    vrf_data = {}
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/config', name=vrf_name)
    vrf_config = api.get(keypath)
    if vrf_config.ok():
        if len(vrf_config.content) == 0:
            return vrf_config

        vrf_intf_info.setdefault(vrf_name, [])

        vrf_data['openconfig-network-instance:config'] = vrf_config.content['openconfig-network-instance:config']

        if vrf_name == 'mgmt':
            if vrf_data['openconfig-network-instance:config']['enabled'] == True:
                vrf_intf_info.setdefault("mgmt", []).append("eth0")
        else:
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/interfaces/interface', name=vrf_name)
            vrf_intfs = api.get(keypath)
            if vrf_intfs.ok():
                vrf_data['openconfig-network-instance:interface'] = vrf_intfs.content['openconfig-network-instance:interface']
            else:
                vrf_data['openconfig-network-instance:interface'] = []

            intfs = vrf_data['openconfig-network-instance:interface']
            for intf in intfs:
                intf_name = intf.get('id')
                vrf_intf_info.setdefault(vrf_name, []).append(intf_name)

    return vrf_config

def build_intf_vrf_binding (intf_vrf_binding):
    api = cc.ApiClient()

    # get mgmt vrf first
    if isMgmtVrfEnabled() == True:
        intf_vrf_binding.setdefault("mgmt", []).append("eth0")

    tIntf = ("/restconf/data/sonic-interface:sonic-interface/INTERFACE/",
             "sonic-interface:INTERFACE",
             "INTERFACE_LIST",
             "portname")

    tVlanIntf = ("/restconf/data/sonic-vlan-interface:sonic-vlan-interface/VLAN_INTERFACE/",
                 "sonic-vlan-interface:VLAN_INTERFACE",
                 "VLAN_INTERFACE_LIST",
                 "vlanName")

    tPortChannelIntf = ("/restconf/data/sonic-portchannel-interface:sonic-portchannel-interface/PORTCHANNEL_INTERFACE/",
                        "sonic-portchannel-interface:PORTCHANNEL_INTERFACE",
                        "PORTCHANNEL_INTERFACE_LIST",
                        "pch_name")

    tLoopbackIntf = ("/restconf/data/sonic-loopback-interface:sonic-loopback-interface/LOOPBACK_INTERFACE/",
                     "sonic-loopback-interface:LOOPBACK_INTERFACE",
                     "LOOPBACK_INTERFACE_LIST",
                     "loIfName")

    requests = [tIntf, tVlanIntf, tPortChannelIntf, tLoopbackIntf]

    for request in requests:
        keypath = cc.Path(request[0])
        try:
            response = api.get(keypath)
            response = response.content

            if response is None:
                continue

            intfsContainer = response.get(request[1])
            if intfsContainer is None:
                continue

            intfsList = intfsContainer.get(request[2])
            if intfsList is None:
                continue

            for intf in intfsList:
                intfName = intf.get(request[3])
                if intfName is None:
                    continue

                vrfName = intf.get('vrf_name')

                if vrfName is None:
                    continue

                intf_vrf_binding.setdefault(vrfName, []).append(intfName)

        except  Exception as e:
            log.syslog(log.LOG_ERR, str(e))
            print "%Error: Internal error"

def invoke_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None

    if func == 'get_openconfig_network_instance_network_instances_network_instances':

        # for show all vrf, get the intf/vrf bindings from all the sonic interface yangs
        # for show a specific vrf, get the intf/vrf binding from the openconfig yang

        intf_vrf_binding = {}

        if args[1] == 'all':

            # Use SONIC model to get all configued VRF names and set the keys in the dictionary
            keypath = cc.Path('/restconf/data/sonic-vrf:sonic-vrf/VRF/VRF_LIST')
            sonic_vrfs = api.get(keypath)
            if sonic_vrfs.ok():
                if 'sonic-vrf:VRF_LIST' in sonic_vrfs.content:
                    vrf_list = sonic_vrfs.content['sonic-vrf:VRF_LIST']
                    for vrf in vrf_list:
                       vrf_name = vrf['vrf_name']
                       if vrf_name != "default":
                           intf_vrf_binding.setdefault(vrf_name, [])

            # build the dictionary with vrf name as key and list of interfaces as value
            build_intf_vrf_binding(intf_vrf_binding)

            intf_vrf_binding = collections.OrderedDict(sorted(intf_vrf_binding.items()))

            if len(intf_vrf_binding) != 0:
                show_cli_output(args[0], intf_vrf_binding)

            return sonic_vrfs

        else:
            vrf_data = get_vrf_data(args[1], intf_vrf_binding)
            if vrf_data.ok() and (len(vrf_data.content) != 0):
                show_cli_output(args[0], intf_vrf_binding)

            return vrf_data

    else:
        body = {}

    return api.cli_not_implemented(func)

def run(func, args):
    try:
        api_response = invoke_api(func, args)

        if not api_response.ok():
            # error response
            print api_response.error_message()

    except:
            # system/network error
            print "%Error: Transaction Failure"

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])

