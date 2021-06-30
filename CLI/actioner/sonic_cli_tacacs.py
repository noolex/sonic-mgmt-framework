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
import json
import collections
import re
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
import urllib3
urllib3.disable_warnings()

SYSTEM = '/restconf/data/openconfig-system:system/'
AAA = SYSTEM + 'aaa/'
SERVER_GROUPS = AAA + 'server-groups/'
TACACS_SERVER_GROUP = SERVER_GROUPS + 'server-group=TACACS/'
TACACS_SERVER_GROUP_CONFIG = TACACS_SERVER_GROUP + 'config/'
TACACS_CONFIG = TACACS_SERVER_GROUP + 'openconfig-aaa-tacacs-ext:tacacs/config/'

def invoke_api(func, args):
    body = None
    api = cc.ApiClient()

    if func == 'patch_openconfig_tacacs_global_config_key':
        keypath = cc.Path(SERVER_GROUPS)
        body = \
        { "openconfig-system:server-groups": {\
            "openconfig-system:server-group": [{\
              "openconfig-system:name": "TACACS",\
              "openconfig-system:config": {\
                "openconfig-system:name": "TACACS",\
                "openconfig-system-ext:secret-key": (args[0]).replace("\\\\", "\\"),\
                "openconfig-system-ext:encrypted": False if len(args) < 2 else True \
              }\
            }]\
          }\
        }
        return api.patch(keypath, body)

    # Set/Get tacacs configuration
    if func == 'patch_tacacs_server':
       indata = {}
       body = {}
       isEncrypted = False

       # get server data
       api_response = get_sonic_tacacs_server_api(args)
       if api_response:
           indata = api_response[0]
       else:
           # default server values
           indata['port'] = 49
           indata['timeout'] = 5
           indata['authtype'] = 'pap'
           indata['priority'] = 1
           indata['encrypted'] = isEncrypted

       # fetch parameter values
       for i in range(len(args)):
           val = (args[i].split(":", 1))[-1]
           val_name = (args[i].split(":", 1))[0]
           if val_name == 'encrypted':
               if not val:
                   isEncrypted = False
               else:
                   isEncrypted = True
           else:
               if val:
                   indata[val_name] = val

       if "port" in indata:
         tconfig_body = {
           "openconfig-system:config": {
             "port": int(indata['port']),
           }
         }

       if "key" in indata:
         if tconfig_body:
             tconfig_body["openconfig-system:config"]["secret-key"] = indata['key']
         else:
           tconfig_body = {
             "openconfig-system:config": {
               "secret-key": indata['key']
             }
           }
         tconfig_body["openconfig-system:config"]["openconfig-aaa-tacacs-ext:encrypted"] = isEncrypted
         
       config_body = {
             "timeout": int(indata['timeout']),
             "openconfig-system:address": args[0],
             "openconfig-system-ext:auth-type": indata['authtype'],
             "openconfig-system-ext:priority": int(indata['priority'])
       }

       if "vrf" in indata:
           config_body["openconfig-system-ext:vrf"] = indata['vrf']


       path = cc.Path('/restconf/data/openconfig-system:system/aaa/server-groups')
       body = { "openconfig-system:server-groups": { "server-group": [{ "name" : "TACACS", "config" : { "name" : "TACACS" },
                                                     "servers": { "server" : [{ "openconfig-system:address": args[0],
                                                     "config": config_body,
                                                     "tacacs": tconfig_body}] }}]}}
       return api.patch(path, body)
    elif func == 'patch_sonic_tacacs_global_src_intf':
       path = cc.Path('/restconf/data/openconfig-system:system/aaa/server-groups')
       body = { "openconfig-system:server-groups": { "server-group": [{ "name" : "TACACS", "config" : { "name" : "TACACS",
           "openconfig-system-ext:source-interface": args[0] if args[0] != 'Management0' else 'eth0'}}]}}
       return api.patch(path, body)
    else:
       body = {}

    return api.cli_not_implemented(func)

def get_sonic_tacacs_server_api(args):
    api_response = []
    api = cc.ApiClient()

    path = cc.Path('/restconf/data/openconfig-system:system/aaa/server-groups/server-group=TACACS/servers/', address=args[0])
    response = api.get(path)
    if response.ok():
        if response.content:
            server_list = response.content["openconfig-system:servers"]["server"]
            for i in range(len(server_list)):
                if args[0] == server_list[i]['address'] or args[0] == 'show_tacacs_server.j2':
                    api_response_data = {}
                    api_response_data['address'] = server_list[i]['address']
                    if 'openconfig-system-ext:auth-type' in server_list[i]['config']:
                        api_response_data['authtype'] = server_list[i]['config']['openconfig-system-ext:auth-type']
                    if 'openconfig-system-ext:priority' in server_list[i]['config']:
                        api_response_data['priority'] = server_list[i]['config']['openconfig-system-ext:priority']
                    if 'openconfig-system-ext:vrf' in server_list[i]['config']:
                        api_response_data['vrf'] = server_list[i]['config']['openconfig-system-ext:vrf']
                    if 'timeout' in server_list[i]['config']:
                        api_response_data['timeout'] = server_list[i]['config']['timeout']
                    if 'tacacs' in server_list[i]:
                        tac_cfg = {}
                        if 'config' in server_list[i]['tacacs']:
                            tac_cfg = server_list[i]['tacacs']['config']
                            if 'port' in tac_cfg:
                                api_response_data['port'] = tac_cfg['port']
                            if "secret-key" in tac_cfg:
                                api_response_data['key'] = tac_cfg['secret-key'] + " encrypted" 
                    api_response.append(api_response_data)
    return api_response

def get_sonic_tacacs_server(args):
    address_arg = args.pop(0)
    address = address_arg.split("=")[1]
    if address != "":
        args.insert(0, address)

    api_response = get_sonic_tacacs_server_api(args)
    show_cli_output("show_tacacs_server.j2", api_response)

def get_sonic_tacacs_global():
    api_response = {}
    api = cc.ApiClient()

    path = cc.Path('/restconf/data/openconfig-system:system/aaa/server-groups/server-group=TACACS/config')
    response = api.get(path)
    if response.ok():
        if response.content:
            api_response = response.content

    show_cli_output("show_tacacs_global.j2", api_response)

def run_config(func, args):
    response = invoke_api(func, args)
    if response.ok():
        if response.content is not None:
            # Get Command Output
            api_response = response.content

            if api_response is None:
                print("%Error: Transaction Failure")
                return 1
            else:
                return
    else:
        print(response.error_message())
        return 1

def get_sonic_tacacs_all():
    get_sonic_tacacs_global()
    get_sonic_tacacs_server(['address=', 'show_tacacs_server.j2'])

def run(func, args):
    if func == 'get_sonic_tacacs_global':
        get_sonic_tacacs_global()
    elif func == 'get_sonic_tacacs_server':
        get_sonic_tacacs_server(args)
    elif func == 'get_sonic_tacacs_all':
        get_sonic_tacacs_all()
    else:
        return run_config(func, args)

if __name__ == '__main__':
    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])
