#!/usr/bin/python
###########################################################################
#
# Copyright 2019 Broadcom, Inc.
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
import pdb
import ast
from rpipe_utils import pipestr
import cli_client as cc
from scripts.render_cli import show_cli_output

def generate_show_ip_ospf(args):
    api = cc.ApiClient()
    keypath = []
    vrfName = "default"
    i = 0
    for arg in args:
        if "vrf" in arg or "Vrf" in arg:
            vrfName = args[i]
        i = i + 1

    d = {}
    dlist = []
    d = { 'vrfName': vrfName }
    dlist.append(d)
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/global/state', name=args[1])
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("Failed")
                return
	    api_response['openconfig-network-instance:global_state'] = api_response.pop('openconfig-network-instance:state')
            dlist.append(api_response)
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/spf/state', name=args[1])
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("Failed")
                return
	    api_response['openconfig-network-instance:spf_state'] = api_response.pop('openconfig-network-instance:state')
            dlist.append(api_response)
    
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/global/timers/lsa-generation/state', name=args[1])
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("Failed")
                return
	    api_response['openconfig-network-instance:lsa_gen_state'] = api_response.pop('openconfig-network-instance:state')
            dlist.append(api_response)

    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/areas', name=args[1])
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("Failed")
                return
            dlist.append(api_response)
    show_cli_output(args[0], dlist)


def invoke_show_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None

    if func == 'show_ip_ospf':
        return generate_show_ip_ospf(args)
    elif func == 'show_ip_ospf_neighbor_detail_all':
        keypath = cc.path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2/neighbors-list', name=args[1])
        return api.get(keypath)
    else: 
        return api.cli_not_implemented(func)


def run(func, args):
    invoke_show_api(func, args)

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])
