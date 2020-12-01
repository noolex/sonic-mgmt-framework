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

def invoke_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    
    if func == 'status_sonic':
        keypath = cc.Path('/restconf/data/sonic-interface:sonic-interface/VLAN_SUB_INTERFACE/VLAN_SUB_INTERFACE_LIST')
        response = api.get(keypath)
        renderer = 'show_subinterfaces_status_sonic.j2'
        return response, renderer
    else:
        body = {}

    return api.cli_not_implemented(func), ''

def run(func, args):
    response, renderer = invoke_api(func, args[1:])
    if response.ok():
        if response.content is not None:
            api_response = response.content
            show_cli_output(renderer, api_response)
        else:
            print("Empty response")
    else:
        print(response.error_message())

#if __name__ == '__main__':
#    pipestr().write(sys.argv)
#    func = sys.argv[1]
    #run(func, sys.argv[3:], sys.argv[2])

