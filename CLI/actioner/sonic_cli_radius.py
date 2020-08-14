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
"""
RADIUS KLISH Actioner script
"""

import sys
from rpipe_utils import pipestr
import cli_client as cc
from scripts.render_cli import show_cli_output

SYSTEM = '/restconf/data/openconfig-system:system/'
AAA = SYSTEM + 'aaa/'
SERVER_GROUPS = AAA + 'server-groups/'
RADIUS_SERVER_GROUP = SERVER_GROUPS + 'server-group=RADIUS/'
RADIUS_SERVER_GROUP_CONFIG = RADIUS_SERVER_GROUP + 'config/'
RADIUS_CONFIG = RADIUS_SERVER_GROUP + 'openconfig-aaa-radius-ext:radius/config/'

def invoke_api(func, args):
    """
    Make the REST request for RADIUS
    """
    api = cc.ApiClient()
    keypath = []
    body = None

    if func == 'patch_openconfig_radius_global_config_source_address':
        keypath = cc.Path(SERVER_GROUPS)
        body = \
        { "openconfig-system:server-groups": {\
            "openconfig-system:server-group": [{\
              "openconfig-system:name": "RADIUS",\
              "openconfig-system:config": {\
                "openconfig-system:name": "RADIUS",\
                "openconfig-system-ext:source-address": args[0]\
              }\
            }]\
          }\
        }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_radius_global_config_nas_ip_address':
        keypath = cc.Path(SERVER_GROUPS)
        body = \
        { "openconfig-system:server-groups": {\
            "openconfig-system:server-group": [{\
              "openconfig-system:name": "RADIUS",\
              "openconfig-system:config": {\
                "openconfig-system:name": "RADIUS"\
              },\
              "openconfig-aaa-radius-ext:radius": {\
                "openconfig-aaa-radius-ext:config": {\
                  "openconfig-aaa-radius-ext:nas-ip-address": args[0]\
                }\
              }\
            }]\
          }\
        }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_radius_global_config_statistics':
        if args[0] == 'enable':
            keypath = cc.Path(SERVER_GROUPS)
            body = \
            { "openconfig-system:server-groups": {\
                "openconfig-system:server-group": [{\
                  "openconfig-system:name": "RADIUS",\
                  "openconfig-system:config": {\
                    "openconfig-system:name": "RADIUS"\
                  },\
                  "openconfig-aaa-radius-ext:radius": {\
                    "openconfig-aaa-radius-ext:config": {\
                      "openconfig-aaa-radius-ext:statistics": True\
                    }\
                  }\
                }]\
              }\
            }
            return api.patch(keypath, body)
        else:
            keypath = cc.Path(RADIUS_CONFIG + 'statistics')
            return api.delete(keypath)
    elif func == 'patch_openconfig_radius_global_config_timeout':
        keypath = cc.Path(SERVER_GROUPS)
        body = \
        { "openconfig-system:server-groups": {\
            "openconfig-system:server-group": [{\
              "openconfig-system:name": "RADIUS",\
              "openconfig-system:config": {\
                "openconfig-system:name": "RADIUS",\
                "openconfig-system-ext:timeout": int(args[0])\
              }\
            }]\
          }\
        }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_radius_global_config_retransmit':
        keypath = cc.Path(SERVER_GROUPS)
        body = \
        { "openconfig-system:server-groups": {\
            "openconfig-system:server-group": [{\
              "openconfig-system:name": "RADIUS",\
              "openconfig-system:config": {\
                  "openconfig-system:name": "RADIUS"\
              },\
              "openconfig-aaa-radius-ext:radius": {\
                "openconfig-aaa-radius-ext:config": {\
                  "openconfig-aaa-radius-ext:retransmit-attempts": int(args[0])\
                }\
              }\
            }]\
          }\
        }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_radius_global_config_key':
        keypath = cc.Path(SERVER_GROUPS)
        body = \
        { "openconfig-system:server-groups": {\
            "openconfig-system:server-group": [{\
              "openconfig-system:name": "RADIUS",\
              "openconfig-system:config": {\
                "openconfig-system:name": "RADIUS",\
                "openconfig-system-ext:secret-key": args[0]\
              }\
            }]\
          }\
        }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_radius_global_config_auth_type':
        keypath = cc.Path(SERVER_GROUPS)
        body = \
        { "openconfig-system:server-groups": {\
            "openconfig-system:server-group": [{\
              "openconfig-system:name": "RADIUS",\
              "openconfig-system:config": {\
                "openconfig-system:name": "RADIUS",\
                "openconfig-system-ext:auth-type": args[0]\
              }\
            }]\
          }\
        }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_radius_global_config_host':

        auth_port = (args[1])[10:]
        timeout = (args[2])[8:]
        retransmit = (args[3])[11:]
        key = (args[4])[4:]
        auth_type = (args[5])[10:]
        priority = (args[6])[9:]
        vrf = (args[7])[4:]
        source_interface = (args[8])[17:]

        body = {

                 "openconfig-system:server": [{

                       "openconfig-system:address": args[0],

                       "openconfig-system:config": {
                           "address": args[0],
                       },

                       "openconfig-system:radius": {
                           "openconfig-system:config": {
                           }
                       }
                  }]
               }

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
        if len(priority) != 0:
            body["openconfig-system:server"][0]["openconfig-system:config"]\
                ["openconfig-system-ext:priority"] = int(priority)
        if len(vrf) != 0:
            body["openconfig-system:server"][0]["openconfig-system:config"]\
                ["openconfig-system-ext:vrf"] = vrf
        if len(source_interface) != 0:
            body["openconfig-system:server"][0]["openconfig-system:radius"]\
                ["openconfig-system:config"]\
                ["openconfig-aaa-radius-ext:source-interface"] = args[9] \
                    if args[9] != 'Management0' else 'eth0'

        keypath = cc.Path(SERVER_GROUPS)
        restconf_body = \
        { "openconfig-system:server-groups": {\
            "openconfig-system:server-group": [{\
              "openconfig-system:name": "RADIUS",\
              "openconfig-system:config": {\
                "openconfig-system:name": "RADIUS"\
              },\
              "openconfig-system:servers": body\
            }]\
          }\
        }
        return api.patch(keypath, restconf_body)
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

            uri_suffix = {
                "auth-port": "/radius/config/auth-port",
                "retransmit": "/radius/config/retransmit-attempts",
                "key": "/radius/config/secret-key",
                "timeout": "/config/timeout",
                "auth-type": "/config/openconfig-system-ext:auth-type",
                "priority": "/config/openconfig-system-ext:priority",
                "vrf": "/config/openconfig-system-ext:vrf",
                "source-interface": "/radius/config/openconfig-aaa-radius-ext:source-interface",
            }

            path = path + uri_suffix.get(args[1], "Invalid Attribute")

        keypath = cc.Path(path, address=args[0])
        return api.delete(keypath)
    # Clear RADIUS statistics
    elif func == 'rpc_sonic_clear_radius_statistics':
        path = cc.Path('/restconf/operations/sonic-system-radius:clear-radius')
        body = {}
        return api.post(path, body)
    else:
        body = {}

    return api.cli_not_implemented(func)

def get_sonic_radius_global():
    """
    RADIUS KLISH globals show
    """
    api_response = {}
    api = cc.ApiClient()

    path = cc.Path(RADIUS_SERVER_GROUP_CONFIG)
    response = api.get(path)
    if response.ok():
        if response.content and 'openconfig-system:config' in response.content:
            api_response = (response.content)['openconfig-system:config']

    path = cc.Path(RADIUS_CONFIG)
    response = api.get(path)
    if response.ok():
        if response.content and 'openconfig-aaa-radius-ext:config' in response.content:
            api_response.update((response.content)['openconfig-aaa-radius-ext:config'])

    if len(api_response) > 0:
        show_cli_output("show_radius_global.j2", api_response)
    return api_response

def get_sonic_radius_servers(globals):
    """
    RADIUS KLISH server show
    """
    api_response = {}
    api = cc.ApiClient()

    path = cc.Path(RADIUS_SERVER_GROUP + 'servers')
    response = api.get(path)

    if not response.ok():
        print("%Error: Get Failure")
        return

    if    (not 'openconfig-system:servers' in response.content)\
       or (not 'server' in response.content['openconfig-system:servers']):
        return
    server_list =  response.content['openconfig-system:servers']['server']

    api_response['header'] = 'True'
    show_cli_output("show_radius_server.j2", api_response)

    for server in server_list:
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

        api_response['src_intf'] = "-"
        if 'radius' in server \
                and 'config' in server['radius'] \
                and 'openconfig-aaa-radius-ext:source-interface' \
                    in server['radius']['config']:
            api_response['src_intf'] = server['radius']['config']\
                ['openconfig-aaa-radius-ext:source-interface']

        show_cli_output("show_radius_server.j2", api_response)

    statistics = 'False'
    if 'statistics' in globals:
        statistics = globals['statistics']

    if statistics != True:
        return

    api_response['header'] = 'True'
    show_cli_output("show_radius_statistics.j2", api_response)

    for server in server_list:
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
            api_response['access-requests'] = \
                counters['openconfig-aaa-radius-ext:access-requests']
        if 'openconfig-aaa-radius-ext:retried-access-requests' in counters:
            api_response['retried-access-requests'] = \
                counters['openconfig-aaa-radius-ext:retried-access-requests']
        if 'timeout-access-requests' in counters:
            api_response['timeout-access-requests'] = \
                counters['timeout-access-requests']
        if 'openconfig-aaa-radius-ext:access-challenges' in counters:
            api_response['access-challenges'] = \
                counters['openconfig-aaa-radius-ext:access-challenges']
        if 'openconfig-aaa-radius-ext:bad-authenticators' in counters:
            api_response['bad-authenticators'] = \
                counters['openconfig-aaa-radius-ext:bad-authenticators']
        if 'openconfig-aaa-radius-ext:invalid-packets' in counters:
            api_response['invalid-packets'] = \
                counters['openconfig-aaa-radius-ext:invalid-packets']

        show_cli_output("show_radius_statistics.j2", api_response)


def run(func, args):
    """
    Main routine for RADIUS KLISH Actioner script
    """
    try:
        if func == 'get_sonic_radius':
            global_response = get_sonic_radius_global()
            get_sonic_radius_servers(globals=global_response)
            return

        response = invoke_api(func, args)

        if response.ok():
            if response.content is not None:
                print("%Error: Invalid command")
        else:
            print(response.error_message())
    except Exception as e:
        # system/network error
        print("%Error: Transaction Failure")


if __name__ == '__main__':

    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])

