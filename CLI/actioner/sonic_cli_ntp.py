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
from rpipe_utils import pipestr
import cli_client as cc
from scripts.render_cli import show_cli_output

IDENTIFIER='NTP'
NAME1='ntp'


def invoke_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None
    ntp_data = {}

    if func == 'get_ntp_global':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/config')
        api_response = api.get(keypath)
        if  not api_response.ok():
            print api_response.error_message()
            return False

        if api_response.content == None:
            return False

        ntp_config = api_response.content
        if len(ntp_config) != 0:
            ntp_data["global"] = ntp_config["openconfig-system:config"]
            show_cli_output(args[0], ntp_data)

    elif func == 'get_ntp_server':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/servers/server')
        api_response = api.get(keypath)
        if not api_response.ok():
            print api_response.error_message()
            return False

        if api_response.content == None:
            return False

        ntp_servers = api_response.content
        if len(ntp_servers) != 0:
            ntp_data["servers"] = ntp_servers["openconfig-system:server"]
            show_cli_output(args[0], ntp_data)

    elif func == 'get_ntp_associations':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/servers/server')
        api_response = api.get(keypath)
        if not api_response.ok():
            print api_response.error_message()
            return False

        if api_response.content == None:
            return False
  
        ntp_servers = api_response.content
        if len(ntp_servers) != 0:
            ntp_data["associations"] = ntp_servers["openconfig-system:server"]
            show_cli_output(args[0], ntp_data)

    elif func == 'set_ntp_source':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/config/openconfig-system-ext:ntp-source-interface')
        body = { "openconfig-system-ext:ntp-source-interface" : args[0] if args[0] != 'Management0' else 'eth0' }
        api_response = api.patch(keypath, body)
        if not api_response.ok():
            # error response
            print api_response.error_message()
            return False

    elif func == 'delete_ntp_source':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/config/openconfig-system-ext:ntp-source-interface')
        return api.delete(keypath)

    elif func == 'set_ntp_server':
      
        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/servers') 
        body = { "openconfig-system:servers": { "server" : [{"config" : {"address": args[0]}, "address" : args[0]}]}}
        return api.patch(keypath, body)

    elif func == 'delete_ntp_server':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/servers/server={server}',
                          server=args[0])
        return api.delete(keypath)

    elif func == 'set_ntp_vrf':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/config')
        body = {"openconfig-system:config":{"openconfig-system-ext:vrf":args[0]}}
        api_response = api.patch(keypath, body)
        if not api_response.ok():
            print api_response.error_message()
            return False

    elif func == 'delete_ntp_vrf':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/config/openconfig-system-ext:vrf')
        return api.delete(keypath)
 
    else:
        print("%Error: Invalid NTP CLI function: {}".format(func))
        return False

    return True

def run(func, args):
    try:
        invoke_api(func, args)
    except:
        # system/network error
        print "%Error: Transaction Failure"

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])

