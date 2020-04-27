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

IDENTIFIER='VRF'
NAME1='vrf'

def get_vrf_data(vrf_name, vrf_show_data):
    api = cc.ApiClient()
    vrf = {}
    vrf_data = {}
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/config', name=vrf_name)
    vrf_config = api.get(keypath)
    if vrf_config.ok():
        if len(vrf_config.content) == 0:
            return vrf_config

        vrf_data['openconfig-network-instance:config'] = vrf_config.content['openconfig-network-instance:config']

        if vrf_name == 'mgmt':
            vrf_data['openconfig-network-instance:interface'] = []
        else:
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/interfaces/interface', name=vrf_name)
            vrf_intfs = api.get(keypath)
            if vrf_intfs.ok():
                vrf_data['openconfig-network-instance:interface'] = vrf_intfs.content['openconfig-network-instance:interface']
            else:
                vrf_data['openconfig-network-instance:interface'] = []

        vrf[vrf_name] = vrf_data
        vrf_show_data.append(vrf)

    return vrf_config



def invoke_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None

    if func == 'get_openconfig_network_instance_network_instances_network_instances':
        show_data = []

        if args[1] == 'all':

            # Get management VRF first, if any.
            get_vrf_data('mgmt', show_data)

            # Use SONIC model to get all configued VRF names
            keypath = cc.Path('/restconf/data/sonic-vrf:sonic-vrf/VRF/VRF_LIST')
            sonic_vrfs = api.get(keypath)
            if sonic_vrfs.ok():
                # Then use openconfig model to get all VRF information
                if 'sonic-vrf:VRF_LIST' in sonic_vrfs.content:
                    vrf_list = sonic_vrfs.content['sonic-vrf:VRF_LIST']
                    for vrf in vrf_list:
                       vrf_name = vrf['vrf_name']
                       if vrf_name != "default": 
                           get_vrf_data(vrf_name, show_data)

                if len(show_data) != 0:
                    show_cli_output(args[0], show_data)

            return sonic_vrfs

        else:

            vrf_data = get_vrf_data(args[1], show_data)
            if vrf_data.ok() and (len(vrf_data.content) != 0):
                show_cli_output(args[0], show_data)

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

