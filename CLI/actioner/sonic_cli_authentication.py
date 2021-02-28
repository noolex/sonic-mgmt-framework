#!/usr/bin/python
###########################################################################
#
# Copyright 2020 Dell, Inc.
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
import cli_client as cc
import collections
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output

def invoke_api(func, args):
    api = cc.ApiClient()
    body = None

    # Set/Get the rules of all IFA table entries.
    if func == 'get_sonic_client_auth_rest':
       path = cc.Path('/restconf/data/sonic-client-auth:sonic-client-auth/REST_SERVER/REST_SERVER_LIST=default/client_auth')
       return api.get(path)
    elif func == 'get_sonic_client_auth_telemetry':
       path = cc.Path('/restconf/data/sonic-client-auth:sonic-client-auth/TELEMETRY/TELEMETRY_LIST=gnmi/client_auth')
       return api.get(path)
    elif func == 'set_sonic_client_auth_rest':
       path = cc.Path('/restconf/data/sonic-client-auth:sonic-client-auth/REST_SERVER')
       body = { "sonic-client-auth:REST_SERVER": {"REST_SERVER_LIST": [{"server": "default","client_auth": args[0].strip(',')}]}}
       return api.patch(path, body)
    elif func == 'set_sonic_client_auth_telemetry':
       path = cc.Path('/restconf/data/sonic-client-auth:sonic-client-auth/TELEMETRY')
       body = { "sonic-client-auth:TELEMETRY": {"TELEMETRY_LIST": [{"server": "gnmi","client_auth": args[0].strip(',')}]}}
       return api.patch(path, body)
    else:
       body = {}

    return api.cli_not_implemented(func)

def run(func, args):

    funcs_temps = func.split(',')
    
    for ft in funcs_temps:
        func = ft
        temp = None
        if ':' in ft:
          func,temp = ft.split(':')


        response = invoke_api(func, args)
        if response.ok():
            if response.content is not None:
                # Get Command Output
                api_response = response.content

                if api_response is None:
                    print("%Error: api_response is None")
                    return 1
                elif func in ['get_sonic_client_auth_rest', 'get_sonic_client_auth_telemetry']:
                    show_cli_output(temp, api_response)
                else:
                    return
        else:
            print(response.error_message())
            return 1

if __name__ == '__main__':

    pipestr().write(sys.argv)

    run(sys.argv[1], sys.argv[2:])
