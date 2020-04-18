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


def invoke_show_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None

    if func == 'show_ip_ospf':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=OSPF,ospfv2/ospfv2', name=args[1])
        return api.get(keypath)
    else:
        return api.cli_not_implemented(func)


def run(func, args):
    if func == 'show_ip_ospf':
        response = invoke_show_api(func, args)
        if response.ok():
            if (args[1]):
                d = { 'vrfName': args[1] }
            if response.content is not None:
                # Get Command Output
                api_response = response.content
                if api_response is None:
                    print("Failed")
                    return
            d.update(api_response)
        show_cli_output(args[0], d)
    else:
        print(response.error_message())

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])
