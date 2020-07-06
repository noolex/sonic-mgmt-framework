#!/usr/bin/python
###########################################################################
#
# Copyright 2019 Broadcom, Inc.
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
import pdb
import ast
from rpipe_utils import pipestr
import cli_client as cc
from scripts.render_cli import show_cli_output


def generate_show_ip_igmp_sources(args):
    api = cc.ApiClient()
    keypath = []
    vrfName = "default"
    i = 0
    for arg in args:
        if "vrf" in arg or "Vrf" in arg or "all" in arg:
            vrfName = args[i]
        i = i + 1

    d = {}
    dlist = []
    d = { 'vrfName': vrfName }
    dlist.append(d)
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=IGMP,igmp/igmp/openconfig-igmp-ext:sources', name=vrfName)
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("Failed")
                return
            dlist.append(api_response)
    show_cli_output(args[0], dlist)
    return dlist

def generate_show_ip_igmp_statistics(args):
    api = cc.ApiClient()
    keypath = []
    vrfName = "default"
    i = 0
    for arg in args:
        if "vrf" in arg or "Vrf" in arg:
            vrfName = args[i]
        i = i + 1
    d = {}
    dlist = []
    d = { 'vrfName': vrfName }
    dlist.append(d)
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=IGMP,igmp/igmp/openconfig-igmp-ext:statistics', name=vrfName)
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("Failed")
                return
            dlist.append(api_response)
    show_cli_output(args[0], dlist)
    return dlist

def generate_show_ip_igmp_interface(args):
    api = cc.ApiClient()
    keypath = []
    vrfName = "default"
    interfacename = ""
    i = 0
    for arg in args:
        if "vrf" in arg or "Vrf" in arg:
            vrfName = args[i]
        i = i + 1
    interfacename = args[len(args)-1]

    d = {}
    dlist = []
    d = { 'vrfName': vrfName }
    dlist.append(d)
    if interfacename != "":
        intfparam = {'interfacename': interfacename }
        dlist.append(intfparam)
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=IGMP,igmp/igmp/openconfig-igmp-ext:interfaces/interface={name1}', name=vrfName, name1=interfacename)
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("Failed")
                return
            dlist.append(api_response)
    show_cli_output(args[0], dlist)
    return dlist

def generate_show_ip_igmp_groups(args):
    api = cc.ApiClient()
    keypath = []
    vrfName = "default"
    i = 0
    for arg in args:
        if "vrf" in arg or "Vrf" in arg  or "all" in arg:
            vrfName = args[i]
        i = i + 1

    d = {}
    dlist = []
    d = { 'vrfName': vrfName }
    dlist.append(d)
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=IGMP,igmp/igmp/openconfig-igmp-ext:groups', name=vrfName)
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("Failed")
                return
            dlist.append(api_response)
    show_cli_output(args[0], dlist)
    return dlist


def invoke_show_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None
    if func == 'show_ip_igmp_groups':
        return generate_show_ip_igmp_groups(args)
    elif func == 'show_ip_igmp_sources':
        return generate_show_ip_igmp_sources(args)
    elif func == 'show_ip_igmp_statistics':
        return generate_show_ip_igmp_statistics(args)
    elif func == 'show_ip_igmp_interface':
        return generate_show_ip_igmp_interface(args)
    elif func == 'show_ip_igmp_vrf':
        if args[2].lower() == 'statistics':
           api_response = generate_show_ip_igmp_statistics(args)
           show_cli_output('show_ip_igmp_statistics.j2', api_response)
        elif args[2].lower() == 'interface':
           api_response = generate_show_ip_igmp_interface(args)
           show_cli_output('show_ip_igmp_interface.j2', api_response)
        elif args[2].lower() == 'groups':
           api_response = generate_show_ip_igmp_groups(args)
           show_cli_output('show_ip_igmp_groups.j2', api_response)
        elif args[2].lower() == 'sources':
           api_response = generate_show_ip_igmp_sources(args)
           show_cli_output('show_ip_igmp_sources.j2', api_response)
    else: 
        return api.cli_not_implemented(func)


def run(func, args):
    invoke_show_api(func, args)

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])
