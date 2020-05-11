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
import cli_client as cc
from rpipe_utils import pipestr
from render_cli import show_cli_output

def str2bool(s):
    return s.lower() in ("true", "t")

def convertTlv(s):
    if s == "management-address":
        return "MANAGEMENT_ADDRESS"
    elif s == "system-capabilities":
        return "SYSTEM_CAPABILITIES"

def invoke_api(fn, args):
    api = cc.ApiClient()
    body = None

    if fn == 'get_openconfig_lldp_lldp_interfaces':
       path = cc.Path('/restconf/data/openconfig-lldp:lldp/interfaces')
       return api.get(path)
    elif fn == 'get_openconfig_lldp_lldp_interfaces_interface':
       path = cc.Path('/restconf/data/openconfig-lldp:lldp/interfaces/interface={name}', name=args[1])
       return api.get(path)
    elif fn == 'disable_lldp_global':
        keypath = cc.Path('/restconf/data/openconfig-lldp:lldp/config/enabled')
        body = { "openconfig-lldp:enabled": str2bool(args[0]) } 
        return api.patch(keypath, body)
    elif fn == 'enable_lldp_global':
        keypath = cc.Path('/restconf/data/openconfig-lldp:lldp/config/enabled')
        return api.delete(keypath, body)
    elif fn == 'set_hello_time':
        keypath = cc.Path('/restconf/data/openconfig-lldp:lldp/config/hello-timer')
        body = { "openconfig-lldp:hello-timer": str(args[0])}
        return api.patch(keypath, body)
    elif fn == 'del_hello_time':
        keypath = cc.Path('/restconf/data/openconfig-lldp:lldp/config/hello-timer')
        return api.delete(keypath, body)
    elif fn == 'set_multiplier':
        keypath = cc.Path('/restconf/data/openconfig-lldp:lldp/config/openconfig-lldp-ext:multiplier')
        body = { "openconfig-lldp-ext:multiplier": int(args[0])}
        return api.patch(keypath, body)
    elif fn == 'del_multiplier':
        keypath = cc.Path('/restconf/data/openconfig-lldp:lldp/config/openconfig-lldp-ext:multiplier')
        return api.delete(keypath, body)
    elif fn == 'set_system_name':
        keypath = cc.Path('/restconf/data/openconfig-lldp:lldp/config/system-name')
        body = { "openconfig-lldp:system-name": args[0]}
        return api.patch(keypath, body)
    elif fn == 'del_system_name':
        keypath = cc.Path('/restconf/data/openconfig-lldp:lldp/config/system-name')
        return api.delete(keypath, body)
    elif fn == 'set_system_description':
        keypath = cc.Path('/restconf/data/openconfig-lldp:lldp/config/system-description')
        body = { "openconfig-lldp:system-description": args[0]}
        return api.patch(keypath, body)
    elif fn == 'del_system_description':
        keypath = cc.Path('/restconf/data/openconfig-lldp:lldp/config/system-description')
        return api.delete(keypath, body)
    elif fn == 'set_mode':
        keypath = cc.Path('/restconf/data/openconfig-lldp:lldp/config/openconfig-lldp-ext:mode')
        body = { "openconfig-lldp-ext:mode": args[0]}
        return api.patch(keypath, body)
    elif fn == 'del_mode':
        keypath = cc.Path('/restconf/data/openconfig-lldp:lldp/config/openconfig-lldp-ext:mode')
        return api.delete(keypath, body)
    elif fn == 'set_tlv':
        keypath = cc.Path('/restconf/data/openconfig-lldp:lldp/config/suppress-tlv-advertisement')
        body = { "openconfig-lldp:suppress-tlv-advertisement": [convertTlv(args[0])]}
        return api.patch(keypath, body)
    elif fn == 'del_tlv':
        keypath = cc.Path('/restconf/data/openconfig-lldp:lldp/config/suppress-tlv-advertisement={name}', name=convertTlv(args[0]))
        return api.delete(keypath, body)
    elif fn == 'disable_lldp_intf':
        keypath = cc.Path('/restconf/data/openconfig-lldp:lldp/interfaces/interface={name}/config/enabled', name=args[0])
        body = { "openconfig-lldp:enabled": str2bool(args[1]) } 
        return api.patch(keypath, body)
    elif fn == 'enable_lldp_intf':
        keypath = cc.Path('/restconf/data/openconfig-lldp:lldp/interfaces/interface={name}/config/enabled', name=args[0])
        return api.delete(keypath, body)
    elif fn == 'set_lldp_intf_mode':
        keypath = cc.Path('/restconf/data/openconfig-lldp:lldp/interfaces/interface={name}/config/openconfig-lldp-ext:mode', name=args[0])
        body = { "openconfig-lldp-ext:mode": args[1]} 
        return api.patch(keypath, body)
    elif fn == 'del_lldp_intf_mode':
        keypath = cc.Path('/restconf/data/openconfig-lldp:lldp/interfaces/interface={name}/config/openconfig-lldp-ext:mode', name=args[0])
        return api.delete(keypath, body)
    else:
        body = {}

    return api.cli_not_implemented(fn)


def run(fn, args):
    response = invoke_api(fn, args)
    if response.ok():
        if response.content is not None:
            # Get Command Output
            api_response = response.content

            if api_response:
                response = api_response
                if 'openconfig-lldp:interfaces' in response.keys():
                    if not response['openconfig-lldp:interfaces']:
                        return
                    neigh_list = response['openconfig-lldp:interfaces']['interface']
                    if neigh_list is None:
                        return
                    show_cli_output(args[0], neigh_list)
                elif 'openconfig-lldp:interface' in response.keys():
                    neigh = response['openconfig-lldp:interface']  # [0]['neighbors']['neighbor']
                    if neigh is None:
                        return
                    show_cli_output(args[0],neigh)
                else:
                    print("Failed")
    else:
        print response.error_message()


if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])
