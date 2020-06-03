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
  
        ntp_servers = api_response.content
        if len(ntp_servers) != 0:
            ntp_data["associations"] = ntp_servers["openconfig-system:server"]
            show_cli_output(args[0], ntp_data)

    elif func == 'set_ntp_source':

        ntp_src = None
        ip_src = args[0].split("=")[1]
        intf_src = args[1].split("=")[1]

        if ip_src != "":
            ntp_src = ip_src
        elif intf_src == "interface":
            intf_type_src = args[2].split("=")[1] 
            if intf_type_src == "Ethernet":
                ntp_src = args[3].split("=")[1] 
            elif intf_type_src == "Loopback":
                ntp_src = args[4].split("=")[1] 
            elif intf_type_src == "Management":
                ntp_src = "eth0" 
            elif intf_type_src == "PortChannel":
                ntp_src = args[7].split("=")[1] 
            elif intf_type_src == "Vlan":
                ntp_src = args[8].split("=")[1] 
            else:
                print("%Error: Invalid NTP interface source")
                return False
        else:
            print("%Error: Invalid NTP source")
            return False

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/config')
        body = { "openconfig-system:config" : { "openconfig-system-ext:ntp-source-interface" : ntp_src } }
        api_response = api.patch(keypath, body)
        if not api_response.ok():
            # error response
            print api_response.error_message()
            return False

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

