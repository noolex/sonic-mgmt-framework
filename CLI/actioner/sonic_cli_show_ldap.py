#!/usr/bin/python
###########################################################################
#
# Copyright 2020 Broadcom. The term Broadcom refers to Broadcom Inc. and/or
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
LDAP KLISH Actioner script
"""

import sys
from rpipe_utils import pipestr
import cli_client as cc
from scripts.render_cli import show_cli_output

SYSTEM = '/restconf/data/openconfig-system:system/'
AAA = SYSTEM + 'aaa/'
SERVER_GROUPS = AAA + 'server-groups/'
MODNAME = 'openconfig-aaa-ldap-ext:'
MODNAME_LDAP = MODNAME + 'ldap'
MODNAME_MAPS = MODNAME + 'maps'
MODNAME_CONFIG = MODNAME + 'config'
LDAP_SERVER_GROUP = SERVER_GROUPS + 'server-group={}/'
LDAP = 'LDAP'
LDAP_NSS = 'LDAP_NSS'
LDAP_PAM = 'LDAP_PAM'
LDAP_SUDO = 'LDAP_SUDO'
LDAP_CONFIG = LDAP_SERVER_GROUP + MODNAME_LDAP + '/config/'
LDAP_SERVER_CONFIG = LDAP_SERVER_GROUP.format(LDAP) + \
    'servers/server={}/' + MODNAME + 'ldap/config/'
LDAP_MAPS = LDAP_SERVER_GROUP.format(LDAP) + MODNAME_LDAP + '/maps/'



def get_sonic_ldap_global():
    """
    LDAP KLISH globals show
    """
    api_response = {}
    api = cc.ApiClient()

    for sg in [ LDAP, LDAP_NSS, LDAP_PAM, LDAP_SUDO ]:
        path = cc.Path(LDAP_CONFIG.format(sg))
        response = api.get(path)
        if response.ok():
            if response.content and MODNAME_CONFIG in response.content:
                api_response = (response.content)[MODNAME_CONFIG]
                show_cli_output("show_ldap_global.j2", api_response, sg=sg)

def get_sonic_ldap_servers():
    """
    LDAP KLISH server show
    """
    api_response = {}
    api = cc.ApiClient()

    path = cc.Path(LDAP_SERVER_GROUP.format(LDAP) + 'servers')
    response = api.get(path)

    if not response.ok():
        print("%Error: Get Failure")
        return

    if (not 'openconfig-system:servers' in response.content) \
        or (not 'server' in response.content['openconfig-system:servers']):
        return

    api_response['header'] = 'True'
    show_cli_output("show_ldap_server.j2", api_response)

    for server in response.content['openconfig-system:servers']['server']:
        api_response.clear()
        api_response['header'] = 'False'
        if 'address' in server:
            api_response['address'] = server['address']

        api_response['use_type'] = "-"
        api_response['retry'] = "-"
        api_response['priority'] = "-"
        api_response['ssl'] = "-"
        api_response['port'] = "-"

        if (MODNAME_LDAP in server) \
                and ('config' in server[MODNAME_LDAP]):
            config = server[MODNAME_LDAP]['config']
            if 'use-type' in config:
                api_response['use_type'] = config['use-type']
            if 'retransmit-attempts' in config:
                api_response['retry'] = config['retransmit-attempts']
            if 'priority' in config:
                api_response['priority'] = config['priority']
            if 'ssl' in config:
                api_response['ssl'] = config['ssl']
            if 'port' in config:
                api_response['port'] = config['port']

            show_cli_output("show_ldap_server.j2", api_response)

def get_sonic_ldap_maps():
    """
    LDAP KLISH maps show
    """
    api_response = {}
    api = cc.ApiClient()

    path = cc.Path(LDAP_MAPS)
    response = api.get(path)

    if not response.ok():
        print("%Error: Get Failure")
        return

    if (not (MODNAME_MAPS) in response.content) \
            or (not 'map' in response.content[MODNAME_MAPS]) \
            or (len(response.content[MODNAME_MAPS]['map']) == 0):
        return

    api_response['header'] = 'True'
    show_cli_output("show_ldap_maps.j2", api_response)

    # show the maps
    maps = { 'ATTRIBUTE' : {},
             'OBJECTCLASS' : {},
             'DEFAULT_ATTRIBUTE_VALUE' : {},
             'OVERRIDE_ATTRIBUTE_VALUE' : {}
           }
    for entry in response.content[MODNAME_MAPS]['map']:
        maps[entry['name']][entry['from']] = entry['config']['to']

    # print maps

    for mapname, map in maps.iteritems():
        if len(map) != 0:
            show_cli_output("show_ldap_maps.j2", map, name=mapname)

def run(func, args):
    """
    Main routine for RADIUS KLISH Actioner script
    """
    if func == 'get_sonic_ldap':
        get_sonic_ldap_global()
        get_sonic_ldap_servers()
        get_sonic_ldap_maps()
        return

if __name__ == '__main__':

    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])

