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
auth_type_dict = {
  "sha1": "NTP_AUTH_SHA1",
  "md5": "NTP_AUTH_MD5",
  "sha2-256": "NTP_AUTH_SHA2_256"
}

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
            return None

        if api_response.content == None:
            return None

        ntp_config = api_response.content
        if len(ntp_config) != 0:
            ntp_data["global"] = ntp_config["openconfig-system:config"]
            show_cli_output(args[0], ntp_data)

    elif func == 'get_ntp_server':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/servers/server')
        api_response = api.get(keypath)
        if not api_response.ok():
            print api_response.error_message()
            return None

        if api_response.content == None:
            return None

        ntp_servers = api_response.content
        if len(ntp_servers) != 0:
            ntp_data["servers"] = ntp_servers["openconfig-system:server"]
            show_cli_output(args[0], ntp_data)

    elif func == 'get_ntp_associations':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/servers/server')
        api_response = api.get(keypath)
        if not api_response.ok():
            print api_response.error_message()
            return None

        if api_response.content == None:
            return None
  
        ntp_servers = api_response.content
        if len(ntp_servers) != 0:
            ntp_data["associations"] = ntp_servers["openconfig-system:server"]
            show_cli_output(args[0], ntp_data)

    elif func == 'set_ntp_source':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/config/openconfig-system-ext:ntp-source-interface')
        body = { "openconfig-system-ext:ntp-source-interface" : [args[0] if args[0] != 'Management0' else 'eth0'] }
        return api.patch(keypath, body)

    elif func == 'delete_ntp_source':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/config/openconfig-system-ext:ntp-source-interface={source}',
                          source=args[0] if args[0] != 'Management0' else 'eth0')
        return api.delete(keypath)

    elif func == 'set_ntp_server':
      
        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/servers') 
        if len(args) >= 3:
            body = { "openconfig-system:servers": { "server" : [{"config" : {"address": args[0],
                                                                             "openconfig-system-ext:key-id" : int(args[2])},
                                                                 "address" : args[0]}]}}
        else:
            body = { "openconfig-system:servers": { "server" : [{"config" : {"address": args[0]},
                                                                 "address" : args[0]}]}}
        api_response = api.patch(keypath, body)
        if not api_response.ok() and "does not match regular expression pattern" in api_response.error_message():
            print "%Error: Invalid IP address or hostname"
            return None
        else:
            return api_response

    elif func == 'delete_ntp_server':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/servers/server={server}',
                          server=args[0])

        api_response = api.delete(keypath)
        if not api_response.ok() and "does not match regular expression pattern" in api_response.error_message():
            print "%Error: Invalid IP address or hostname"
            return None
        else:
            return api_response

    elif func == 'set_ntp_vrf':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/config')
        body = {"openconfig-system:config":{"openconfig-system-ext:vrf":args[0]}}
        return api.patch(keypath, body)

    elif func == 'delete_ntp_vrf':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/config/openconfig-system-ext:vrf')
        return api.delete(keypath)
 
    elif func == 'set_ntp_authentication':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/config')
        body = {"openconfig-system:config":{"enable-ntp-auth":True if args[0] == 'True' else False}}
        return api.patch(keypath, body)

    elif func == 'set_ntp_trusted_key':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/config')
        body = {"openconfig-system:config":{"openconfig-system-ext:trusted-key":[int(args[0])]}}
        return api.patch(keypath, body)

    elif func == 'delete_ntp_trusted_key':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/config/openconfig-system-ext:trusted-key={trustkey}',
                          trustkey=args[0])
        return api.delete(keypath)

    elif func == 'set_ntp_authentication_key':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/ntp-keys')
        body = { "openconfig-system:ntp-keys": { "ntp-key" : [{"config" : {"key-id": int(args[0]),
                                                                           "key-type" : auth_type_dict[args[1]],
                                                                           "key-value" : args[2],
                           "openconfig-system-ext:encrypted" : False if len(args) < 4 else True},
                                                               "key-id" : int(args[0])}]}}
        return api.patch(keypath, body)

    elif func == 'delete_ntp_authentication_key':

        keypath = cc.Path('/restconf/data/openconfig-system:system/ntp/ntp-keys/ntp-key={ntpkey}', ntpkey=args[0])
        return api.delete(keypath)

    else:
        print("%Error: Invalid NTP CLI function: {}".format(func))
        return None

    return None

def run(func, args):
    try:
        response = invoke_api(func, args)
        if response is not None and not response.ok():
            print response.error_message()
    except:
        # system/network error
        print "%Error: Transaction Failure"

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])

