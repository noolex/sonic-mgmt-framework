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

def get_ssh_server_vrfs(vrf_name):
    api = cc.ApiClient()
    vrf = {}
    vrf_data = {}
    if vrf_name:
        keypath = cc.Path('/restconf/data/openconfig-system:system/ssh-server/openconfig-system-ext:ssh-server-vrfs/ssh-server-vrf={name}', name=vrf_name)
    else:
        keypath = cc.Path('/restconf/data/openconfig-system:system/ssh-server/openconfig-system-ext:ssh-server-vrfs')
    vrf_config = api.get(keypath)
    if vrf_config.ok():
        if len(vrf_config.content) == 0:
            return vrf_config

    return vrf_config

def invoke_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None

    if func == 'patch_openconfig_system_ssh_server_vrf':
        keypath = cc.Path('/restconf/data/openconfig-system:system/ssh-server/openconfig-system-ext:ssh-server-vrfs/ssh-server-vrf')
        body = { "openconfig-system-ext:ssh-server-vrf": [ { "vrf-name": args[0], "config":{ "vrf-name": args[0], "port": 22 } } ] }
        return api.patch(keypath, body)

    elif func == 'delete_openconfig_system_ssh_server_vrf':
        keypath = cc.Path('/restconf/data/openconfig-system:system/ssh-server/openconfig-system-ext:ssh-server-vrfs/ssh-server-vrf={name}', name=args[0])
        return api.delete(keypath)

    elif func == 'get_openconfig_system_ssh_server_vrfs':
        vrf = None
        if args:
            vrf = args[0]
        vrf_data = get_ssh_server_vrfs(vrf)
        if vrf_data.ok() and (len(vrf_data.content) != 0):
            if vrf:
                show_cli_output("show_ssh_server_vrf.j2", vrf_data['openconfig-system-ext:ssh-server-vrf'])
            else:
                vrf_data1 = vrf_data['openconfig-system-ext:ssh-server-vrfs']
                show_cli_output("show_ssh_server_vrf.j2", vrf_data1['ssh-server-vrf'])

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

