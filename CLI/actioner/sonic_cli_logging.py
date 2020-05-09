#!/usr/bin/python
###########################################################################
#
# Copyright 2019 Broadcom. The term Broadcom refers to Broadcom Inc. and/or
# its subsidiaries.
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
SYSTEM='/restconf/data/openconfig-system:system/'
LOG_SERVERS=SYSTEM+'logging/remote-servers'

def invoke_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None

    if func == 'patch_openconfig_system_logging_server_config_host':

        rport=(args[1])[6:]
        source_ip=(args[2])[10:]
        vrf=(args[3])[4:]

        #keypath = cc.Path(LOG_SERVERS +
        #    '/remote-server={address}', address=args[0])
        keypath = cc.Path(LOG_SERVERS + '/remote-server')
        body = {   "openconfig-system:remote-server": [ {

                       "host": args[0],

                       "config": {
                           "host": args[0],
                       }

                  } ]
               }

        getpath = cc.Path(LOG_SERVERS)
        response = api.get(getpath)

        exists='False'
        if response.ok()\
              and ('openconfig-system:remote-servers' in response.content)\
              and ('remote-server' in response.content['openconfig-system:remote-servers']):
            for server in response.content['openconfig-system:remote-servers']['remote-server']:
                if ('host' in server) and (server['host'] == args[0]):
                    exists='True'

        if (exists == 'False') and (len(rport) == 0):
            rport="514"
        if len(rport) != 0:
            body["openconfig-system:remote-server"][0]\
                ["config"]["remote-port"] = int(rport)
        if len(source_ip) != 0:
            body["openconfig-system:remote-server"][0]\
                ["config"]["source-address"] = source_ip
        if len(vrf) != 0:
            body["openconfig-system:remote-server"][0]\
                ["config"]["openconfig-system-ext:vrf-name"] = vrf

        return api.patch(keypath, body)
    elif func == 'delete_openconfig_system_looging_server_config_host':
        path = LOG_SERVERS + '/remote-server={address}'
        if (len(args) >= 2) and (len(args[1]) != 0):

            if (args[1] == "remote-port"):
                getpath = cc.Path(LOG_SERVERS)
                response = api.get(getpath)

                if not response.ok():
                    print("%Error: Get Failure")
                    return response

                if (not ('openconfig-system:remote-servers' in response.content))\
                  or (not ('remote-server' \
                   in response.content['openconfig-system:remote-servers'])):
                    return response

                exists = 'False'
                for server in response.content['openconfig-system:remote-servers']['remote-server']:
                    if ('host' in server) and (server['host'] == args[0]):
                        exists = 'True'

                if exists == 'False':
                    return response

                if (args[1] == "remote-port"):
                    return invoke_api(
                        'patch_openconfig_system_logging_server_config_host',
                        [args[0], "rport=514", "source-ip=", "vrf="])

            uri_suffix = {
                "remote-port": "/config/auth-port",
                "source-address": "/config/source-address",
                "vrf": "/config/openconfig-system-ext:vrf",
            }

            path = path + uri_suffix.get(args[1], "Invalid Attribute")

        keypath = cc.Path(path, address=args[0])
        return api.delete(keypath)
    else:
        body = {}

    return api.cli_not_implemented(func)

def get_sonic_logging_servers(args=[]):
    api_response = {}
    api = cc.ApiClient()

    path = cc.Path(LOG_SERVERS)
    response = api.get(path)


    if not response.ok():
        print("%Error: Get Failure")
        return

    if (not ('openconfig-system:remote-servers' in response.content)) \
        or (not ('remote-server' in response.content['openconfig-system:remote-servers'])):
        return

    api_response['header'] = 'True'
    show_cli_output("show_logging_server.j2", api_response)

    for server in response.content['openconfig-system:remote-servers']['remote-server']:
        api_response.clear()
        api_response['header'] = 'False'
        if 'host' in server:
            api_response['host'] = server['host']

        api_response['source'] = "-"
        if 'config' in server \
                and 'source-address' in server['config']:
            api_response['source'] = server['config']['source-address']

        api_response['port'] = "-"
        if 'config' in server \
                and 'remote-port' in server['config']:
            api_response['port'] = server['config']['remote-port']

        api_response['vrf'] = "-"
        if 'config' in server \
                and 'openconfig-system-ext:vrf-name' in server['config']:
            api_response['vrf'] = \
                server['config']['openconfig-system-ext:vrf-name']
        show_cli_output("show_logging_server.j2", api_response)


def run(func, args):
    if func == 'get_openconfig_system_logging_servers':
        get_sonic_logging_servers()
        return

    response = invoke_api(func, args)

    if response.ok():
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("%Error: Transaction Failure")
    else:
        print(response.error_message())

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    if func == 'get_openconfig_system_logging_servers':
        get_sonic_logging_servers(sys.argv[2:])
    else:
        run(func, sys.argv[2:])

