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
        vrf=(args[2])[4:]
        src_intf = ""
        if len(args) > 3:
            src_intf = replace_prefix(args[3], 'Management', 'eth')

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
        if len(src_intf) != 0:
            body["openconfig-system:remote-server"][0]\
					["config"]["openconfig-system-ext:source-interface"] = src_intf
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
                        [args[0], "rport=514", "vrf="])

            uri_suffix = {
                "remote-port": "/config/remote-port",
				"source-interface": "/config/openconfig-system-ext:source-interface",
                "vrf": "/config/openconfig-system-ext:vrf-name",
            }

            path = path + uri_suffix.get(args[1], "Invalid Attribute")

        keypath = cc.Path(path, address=args[0])
        return api.delete(keypath)
    else:
        body = {}

    return api.cli_not_implemented(func)

def replace_prefix(value, prefix, new_prefix):
    if value.startswith(prefix):
        return new_prefix + value[len(prefix):]
    return value

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
                and 'openconfig-system-ext:source-interface' in server['config']:
            src_intf = server['config']['openconfig-system-ext:source-interface']
            api_response['source'] = replace_prefix(src_intf, 'eth', 'Management')

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

def get_sonic_logging(args):
    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/operations/openconfig-system-ext:show-sys-log')
    if len(args) >= 2:
        body = { "openconfig-system-ext:input":{"num-lines": int(args[1])}}
    else:
        body = { "openconfig-system-ext:input":{"num-lines": 0}}
    templ=args[0]
    api_response = aa.post(keypath, body)

    try:
        if api_response.ok():
           response = api_response.content
           if response is not None and 'openconfig-system-ext:output' in response:
                show_cli_output(templ, response)
    except Exception as e:
        raise e

def clear_sonic_logging(args):
    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/operations/openconfig-system-ext:clear-sys-log')
    body = None
    templ=args[0]
    api_response = aa.post(keypath, body)

    try:
        if api_response.ok():
           response = api_response.content
           if response is not None and 'sonic-system-infra:output' in response:
                show_cli_output(templ, response['openconfig-system-ext:output']['result'])
    except Exception as e:
        raise e

def get_openconfig_system_logging_count(args):
    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/operations/openconfig-system-ext:sys-log-count')
    body = None
    templ=args[0]
    api_response = aa.post(keypath, body)

    try:
        if api_response.ok():
           response = api_response.content
           if response is not None and 'openconfig-system-ext:output' in response:
              show_cli_output(templ, response['openconfig-system-ext:output']['result'])
    except Exception as e:
        raise e


def run(func, args):
    if func == 'get_openconfig_system_logging_servers':
        get_sonic_logging_servers()
        return 0

    if func == 'get_openconfig_system_logging':
        get_sonic_logging(args)
        return 0

    if func == 'get_openconfig_clear_logging':
        clear_sonic_logging(args)
        return 0

    if func == 'get_openconfig_system_logging_count':
        get_openconfig_system_logging_count(args)
        return 0

    response = invoke_api(func, args)

    if response.ok():
        if response.content is not None:
            print("%Error: Transaction Failure")
    else:
        print(response.error_message())

if __name__ == '__main__':
    import sys
    from rpipe_utils import pipestr

    pipestr().write(sys.argv)
    func = sys.argv[1]
    if func == 'get_openconfig_system_logging_servers':
        get_sonic_logging_servers(sys.argv[2:])
    elif func == 'get_openconfig_system_logging':
        get_sonic_logging(sys.argv[2:])
    elif func == 'get_openconfig_clear_logging':
        clear_sonic_logging(sys.argv[2:])
    elif func == 'get_openconfig_system_logging_count':
        get_openconfig_system_logging_count(sys.argv[2:])
    else:
        run(func, sys.argv[2:])

