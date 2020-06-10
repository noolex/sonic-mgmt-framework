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
AAA=SYSTEM+'aaa/'
SERVER_GROUPS=AAA+'server-groups/'
RADIUS_SERVER_GROUP=SERVER_GROUPS+'server-group=RADIUS/'
RADIUS_CONFIG=RADIUS_SERVER_GROUP+'openconfig-aaa-radius-ext:radius/config/'

def invoke_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None

    if func == 'patch_openconfig_radius_global_config_source_address':
        keypath = cc.Path(RADIUS_SERVER_GROUP +
            'config/openconfig-system-ext:source-address')
        body = { "openconfig-system-ext:source-address": args[0] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_radius_global_config_nas_ip_address':
        keypath = cc.Path(RADIUS_CONFIG + 'nas-ip-address')
        body = { "openconfig-aaa-radius-ext:nas-ip-address": args[0] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_radius_global_config_statistics':
        keypath = cc.Path(RADIUS_CONFIG + 'statistics')
        if args[0] == 'enable':
            body = { "openconfig-aaa-radius-ext:statistics": True}
        else:
            body = { "openconfig-aaa-radius-ext:statistics": False}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_radius_global_config_timeout':
        keypath = cc.Path(RADIUS_SERVER_GROUP +
            'config/openconfig-system-ext:timeout')
        body = { "openconfig-system-ext:timeout": int(args[0]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_radius_global_config_retransmit':
        keypath = cc.Path(RADIUS_CONFIG + 'retransmit-attempts')
        body = { "openconfig-aaa-radius-ext:retransmit-attempts": int(args[0])}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_radius_global_config_key':
        keypath = cc.Path(RADIUS_SERVER_GROUP +
            'config/openconfig-system-ext:secret-key')
        body = { "openconfig-system-ext:secret-key": args[0] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_radius_global_config_auth_type':
        keypath = cc.Path(RADIUS_SERVER_GROUP +
            'config/openconfig-system-ext:auth-type')
        body = { "openconfig-system-ext:auth-type": args[0] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_radius_global_config_host':

        auth_port=(args[1])[10:]
        timeout=(args[2])[8:]
        retransmit=(args[3])[11:]
        key=(args[4])[4:]
        auth_type=(args[5])[10:]
        priority=(args[6])[9:]
        vrf=(args[7])[4:]

        keypath = cc.Path(RADIUS_SERVER_GROUP +
            'servers/server={address}', address=args[0])
        body = {   "openconfig-system:server": [ {

                       "address": args[0],

                       "openconfig-system:config": {
                           "name": args[0],
                       },

                       "openconfig-system:radius": {
                           "openconfig-system:config": {
                           }
                       }
                  } ]
               }

        getpath = cc.Path(RADIUS_SERVER_GROUP + 'servers')
        response = api.get(getpath)

        exists='False'
        if response.ok()\
              and ('openconfig-system:servers' in response.content)\
              and ('server' in response.content['openconfig-system:servers']):
            for server in response.content['openconfig-system:servers']['server']:
                if ('address' in server) and (server['address'] == args[0]):
                    exists='True'

        if (exists == 'False') and (len(auth_port) == 0):
            auth_port="1812"
        if len(auth_port) != 0:
            body["openconfig-system:server"][0]["openconfig-system:radius"]\
                ["openconfig-system:config"]["auth-port"] = int(auth_port)
        if len(retransmit) != 0:
            body["openconfig-system:server"][0]["openconfig-system:radius"]\
                ["openconfig-system:config"]["retransmit-attempts"] \
                = int(retransmit)
        if len(key) != 0:
            body["openconfig-system:server"][0]["openconfig-system:radius"]\
                ["openconfig-system:config"]["secret-key"] = key

        if len(timeout) != 0:
            body["openconfig-system:server"][0]["openconfig-system:config"]\
                ["timeout"] = int(timeout)
        if len(auth_type) != 0:
            body["openconfig-system:server"][0]["openconfig-system:config"]\
                ["openconfig-system-ext:auth-type"] = auth_type
        if (exists == 'False') and (len(priority) == 0):
            priority="1"
        if len(priority) != 0:
            body["openconfig-system:server"][0]["openconfig-system:config"]\
                ["openconfig-system-ext:priority"] = int(priority)
        if len(vrf) != 0:
            body["openconfig-system:server"][0]["openconfig-system:config"]\
                ["openconfig-system-ext:vrf"] = vrf

        return api.patch(keypath, body)
    elif func == 'delete_openconfig_radius_global_config_source_address':
        keypath = cc.Path(RADIUS_SERVER_GROUP +
            'config/openconfig-system-ext:source-address')
        return api.delete(keypath)
    elif func == 'delete_openconfig_radius_global_config_nas_ip_address':
        keypath = cc.Path(RADIUS_CONFIG + 'nas-ip-address')
        return api.delete(keypath)
    elif func == 'delete_openconfig_radius_global_config_retransmit':
        keypath = cc.Path(RADIUS_CONFIG + 'retransmit-attempts')
        return api.delete(keypath)
    elif func == 'delete_openconfig_radius_global_config_key':
        keypath = cc.Path(RADIUS_SERVER_GROUP +
            'config/openconfig-system-ext:secret-key')
        return api.delete(keypath)
    elif func == 'delete_openconfig_radius_global_config_auth_type':
        keypath = cc.Path(RADIUS_SERVER_GROUP +
            'config/openconfig-system-ext:auth-type')
        return api.delete(keypath)
    elif func == 'delete_openconfig_radius_global_config_timeout':
        keypath = cc.Path(RADIUS_SERVER_GROUP +
            'config/openconfig-system-ext:timeout')
        return api.delete(keypath)
    elif func == 'delete_openconfig_radius_global_config_host':
        path = RADIUS_SERVER_GROUP + 'servers/server={address}'
        if (len(args) >= 2) and (len(args[1]) != 0):

            if (args[1] == "auth-port") or (args[1] == "priority"):
                getpath = cc.Path(RADIUS_SERVER_GROUP + 'servers')
                response = api.get(getpath)

                if not response.ok():
                    print("%Error: Get Failure")
                    return response

                if (not ('openconfig-system:servers' in response.content))\
                  or (not ('server' \
                   in response.content['openconfig-system:servers'])):
                    return response

                exists = 'False'
                for server in response.content['openconfig-system:servers']['server']:
                    if ('address' in server) and (server['address'] == args[0]):
                        exists = 'True'

                if exists == 'False':
                    return response

                if (args[1] == "auth-port"):
                    return invoke_api(
                        'patch_openconfig_radius_global_config_host',
                        [args[0], "auth_port=1812", "timeout=", "retransmit=",
                        "key=", "auth_type=", "priority=", "vrf="])
                if (args[1] == "priority"):
                    return invoke_api(
                        'patch_openconfig_radius_global_config_host',
                        [args[0], "auth_port=", "timeout=", "retransmit=",
                        "key=", "auth_type=", "priority=1", "vrf="])

            uri_suffix = {
                "auth-port": "/radius/config/auth-port",
                "retransmit": "/radius/config/retransmit-attempts",
                "key": "/radius/config/secret-key",
                "timeout": "/config/timeout",
                "auth-type": "/config/openconfig-system-ext:auth-type",
                "priority": "/config/openconfig-system-ext:priority",
                "vrf": "/config/openconfig-system-ext:vrf",
            }

            path = path + uri_suffix.get(args[1], "Invalid Attribute")

        keypath = cc.Path(path, address=args[0])
        return api.delete(keypath)
    # Clear RADIUS statistics
    elif func == 'rpc_sonic_clear_radius_statistics':
        path = cc.Path('/restconf/operations/sonic-system-radius:clear-radius')
        body = {}
        return api.post(path,body)
    else:
        body = {}

    return api.cli_not_implemented(func)

def get_sonic_radius_global():
    api_response = {} 
    api = cc.ApiClient()
    
    path = cc.Path(RADIUS_SERVER_GROUP)
    response = api.get(path)
    if response.ok():
        if response.content:
            api_response = response.content

    show_cli_output("show_radius_global.j2", api_response)
    return api_response

def get_sonic_radius_servers(args=[], globals={}):
    api_response = {}
    api = cc.ApiClient()

    path = cc.Path(RADIUS_SERVER_GROUP+'servers')
    response = api.get(path)


    if not response.ok():
        print("%Error: Get Failure")
        return

    if (not ('openconfig-system:servers' in response.content)) \
        or (not ('server' in response.content['openconfig-system:servers'])):
        return

    api_response['header'] = 'True'
    show_cli_output("show_radius_server.j2", api_response)

    for server in response.content['openconfig-system:servers']['server']:
        api_response.clear()
        api_response['header'] = 'False'
        if 'address' in server:
            api_response['address'] = server['address']

        api_response['timeout'] = "-"
        if 'config' in server \
                and 'timeout' in server['config']:
            api_response['timeout'] = server['config']['timeout']

        api_response['port'] = "-"
        if 'radius' in server \
                and 'config' in server['radius'] \
                and 'auth-port' in server['radius']['config']:
            api_response['port'] = server['radius']['config']['auth-port']

        api_response['key'] = "-"
        if 'radius' in server \
                and 'config' in server['radius'] \
                and 'secret-key' in server['radius']['config']:
            api_response['key'] = server['radius']['config']['secret-key']

        api_response['retransmit'] = "-"
        if 'radius' in server \
                and 'config' in server['radius'] \
                and 'retransmit-attempts' in server['radius']['config']:
            api_response['retransmit'] = \
                server['radius']['config']['retransmit-attempts']

        api_response['authtype'] = "-"
        if 'config' in server \
                and 'openconfig-system-ext:auth-type' in server['config']:
            api_response['authtype'] = \
                server['config']['openconfig-system-ext:auth-type']

        api_response['priority'] = "-"
        if 'config' in server \
                and 'openconfig-system-ext:priority' in server['config']:
            api_response['priority'] = \
                server['config']['openconfig-system-ext:priority']

        api_response['vrf'] = "-"
        if 'config' in server \
                and 'openconfig-system-ext:vrf' in server['config']:
            api_response['vrf'] = \
                server['config']['openconfig-system-ext:vrf']

        show_cli_output("show_radius_server.j2", api_response)

    statistics = 'False'
    if ('openconfig-system:server-group' in globals) and \
       ('openconfig-aaa-radius-ext:radius' in globals['openconfig-system:server-group'][0]) and \
       ('config' in globals['openconfig-system:server-group'][0]['openconfig-aaa-radius-ext:radius']) and \
       ('statistics' in globals['openconfig-system:server-group'][0]['openconfig-aaa-radius-ext:radius']['config']):
        statistics = globals['openconfig-system:server-group'][0]['openconfig-aaa-radius-ext:radius']['config']['statistics']

    if statistics != True:
        return

    api_response['header'] = 'True'
    show_cli_output("show_radius_statistics.j2", api_response)

    for server in response.content['openconfig-system:servers']['server']:
        api_response.clear()
        api_response['header'] = 'False'
        if 'address' in server:
            api_response['address'] = server['address']
        if 'radius' not in server or \
           'state' not in server['radius'] or \
           'counters' not in server['radius']['state']:
            continue
        counters = server['radius']['state']['counters']
        if 'access-accepts' in counters:
            api_response['access-accepts'] = counters['access-accepts']
        if 'access-rejects' in counters:
            api_response['access-rejects'] = counters['access-rejects']
        if 'openconfig-aaa-radius-ext:access-requests' in counters:
            api_response['access-requests'] = counters['openconfig-aaa-radius-ext:access-requests']
        if 'openconfig-aaa-radius-ext:retried-access-requests' in counters:
            api_response['retried-access-requests'] = counters['openconfig-aaa-radius-ext:retried-access-requests']
        if 'timeout-access-requests' in counters:
            api_response['timeout-access-requests'] = counters['timeout-access-requests']
        if 'openconfig-aaa-radius-ext:access-challenges' in counters:
            api_response['access-challenges'] = counters['openconfig-aaa-radius-ext:access-challenges']
        if 'openconfig-aaa-radius-ext:bad-authenticators' in counters:
            api_response['bad-authenticators'] = counters['openconfig-aaa-radius-ext:bad-authenticators']
        if 'openconfig-aaa-radius-ext:invalid-packets' in counters:
            api_response['invalid-packets'] = counters['openconfig-aaa-radius-ext:invalid-packets']

        show_cli_output("show_radius_statistics.j2", api_response)


def run(func, args):
    if func == 'get_sonic_radius':
        global_response = get_sonic_radius_global()
        get_sonic_radius_servers(globals=global_response)
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

    if func == 'get_sonic_radius':
        global_response = get_sonic_radius_global()
        get_sonic_radius_servers(sys.argv[2:], globals=global_response)
    else:
        run(func, sys.argv[2:])

