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
DNS=SYSTEM+'dns/'
DNS_SERVERS=DNS+'servers/'

def invoke_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None

    if func == 'patch_openconfig_dns_global_config_source_address':
        keypath = cc.Path(DNS +
            'config/openconfig-system-ext:source-address')
        body = { "openconfig-system-ext:source-address": args[0] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_dns_server_address':
        keypath = cc.Path(DNS_SERVERS+
            'server={nameserver}/config', nameserver=args[0])
        body = { "openconfig-system:config": { "address": args[0]} }
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_dns_global_config_source_address':
        keypath = cc.Path(DNS +
            'config/openconfig-system-ext:source-address')
        return api.delete(keypath)
    elif func == 'delete_openconfig_dns_server_address':
        keypath = cc.Path(DNS_SERVERS+
            'server={nameserver}', nameserver=args[0])
        return api.delete(keypath)
    else:
        body = {}

    return api.cli_not_implemented(func)

def get_sonic_dns_all():
    api_response = {} 
    api = cc.ApiClient()
    
    path = cc.Path(DNS)
    response = api.get(path)
    if response.ok():
        if response.content:
            api_response = response.content

    show_cli_output("show_hosts.j2", api_response)

def run(func, args):
    if func == 'get_sonic_dns_hosts':
        return get_sonic_dns_all()

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

    run(func, sys.argv[2:])

