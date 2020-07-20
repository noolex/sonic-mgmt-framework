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
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=IGMP,igmp/igmp/openconfig-igmp-ext:sources', name=vrfName)
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                return
    return api_response

def generate_show_ip_igmp_statistics(args):
    api = cc.ApiClient()
    keypath = []
    vrfName = "default"
    i = 0
    for arg in args:
        if "vrf" in arg or "Vrf" in arg:
            vrfName = args[i]
        i = i + 1
    dlist = []
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=IGMP,igmp/igmp/openconfig-igmp-ext:statistics', name=vrfName)
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                return
            dlist.append(api_response)
    show_cli_output(args[0], api_response)
    return api_response

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
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=IGMP,igmp/igmp/openconfig-igmp-ext:interfaces/interface={name1}', name=vrfName, name1=interfacename)
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print("% No such Interface")
                return
    show_cli_output(args[0], api_response)
    return api_response

def generate_show_ip_igmp_groups(args):
    api = cc.ApiClient()
    keypath = []
    vrfName = "default"
    i = 0
    for arg in args:
        if "vrf" in arg or "Vrf" in arg  or "all" in arg:
            vrfName = args[i]
        i = i + 1
    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol=IGMP,igmp/igmp/openconfig-igmp-ext:groups', name=vrfName)
    response = api.get(keypath)
    if(response.ok()):
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                return
    return api_response

def generate_show_ip_igmp_joins(args):
    api = cc.ApiClient()
    keypath = []
    body = None
    vrfName = "default"
    i = 0
    for arg in args:
        if "vrf" in arg or "Vrf" in arg:
            vrfName = args[i]
        i = i + 1
    d = {}
    method = "rpc"
    keypath = cc.Path('/restconf/operations/sonic-igmp:get-igmp-join')
    inputs = {"vrf-name":vrfName}
    body = {"sonic-igmp:input": inputs}
    response = api.post(keypath, body)
    if(response.ok()):
        d = response.content['sonic-igmp:output']['response']
        if len(d) != 0 and "warning" not in d and "Unknown command:" not in d:
             try:
                 d = json.loads(d)
             except:
                 return 1
             show_cli_output('show_ip_igmp_joins.j2',d)

def generate_show_ip_igmp_vrf_all_groups(args):
    api = cc.ApiClient()
    keypath = []
    body = None
    args[0] = 'show_ip_igmp_groups.j2'
    # Use SONIC model to get all configued VRF names
    keypath = cc.Path('/restconf/data/sonic-vrf:sonic-vrf/VRF/VRF_LIST')
    sonic_vrfs = api.get(keypath)
    if sonic_vrfs.ok():
        if 'sonic-vrf:VRF_LIST' in sonic_vrfs.content:
            vrf_list = sonic_vrfs.content['sonic-vrf:VRF_LIST']
            for vrf in vrf_list:
               vrf_name = vrf['vrf_name']
               args[1] = vrf_name
               d = {}
               dlist = []
               d = {'vrfName': vrf_name}
               dlist.append(d)
               api_response = generate_show_ip_igmp_groups(args)
               dlist.append(api_response)
               show_cli_output(args[0], dlist)

def generate_show_ip_igmp_vrf_all_sources(args):
    api = cc.ApiClient()
    keypath = []
    body = None
    vrfName = "default"
    args[0] = 'show_ip_igmp_sources.j2'
    # Use SONIC model to get all configued VRF names
    keypath = cc.Path('/restconf/data/sonic-vrf:sonic-vrf/VRF/VRF_LIST')
    sonic_vrfs = api.get(keypath)
    if sonic_vrfs.ok():
        if 'sonic-vrf:VRF_LIST' in sonic_vrfs.content:
            vrf_list = sonic_vrfs.content['sonic-vrf:VRF_LIST']
            for vrf in vrf_list:
               vrf_name = vrf['vrf_name']
               args[1] = vrf_name
               d = {}
               dlist = []
               d = { 'vrfName': vrf_name }
               dlist.append(d)
               api_response = generate_show_ip_igmp_sources(args)
               dlist.append(api_response)
               show_cli_output(args[0], dlist)

def generate_show_ip_igmp_vrf_all_joins(args):
    api = cc.ApiClient()
    keypath = []
    body = None
    vrfName = "default"
    # Use SONIC model to get all configued VRF names
    keypath = cc.Path('/restconf/data/sonic-vrf:sonic-vrf/VRF/VRF_LIST')
    sonic_vrfs = api.get(keypath)
    if sonic_vrfs.ok():
        if 'sonic-vrf:VRF_LIST' in sonic_vrfs.content:
            vrf_list = sonic_vrfs.content['sonic-vrf:VRF_LIST']
            for vrf in vrf_list:
               vrf_name = vrf['vrf_name']
               args[1] = vrf_name
               print("VRF : "+vrf_name)
               generate_show_ip_igmp_joins(args)

def invoke_show_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None
    dlist = []
    if func == 'show_ip_igmp_groups':
        api_response = generate_show_ip_igmp_groups(args)
        dlist.append(api_response)
        show_cli_output(args[0], dlist)
    elif func == 'show_ip_igmp_sources':
        api_response = generate_show_ip_igmp_sources(args)
        dlist.append(api_response)
        show_cli_output(args[0], dlist)
    elif func == 'show_ip_igmp_joins':
        return generate_show_ip_igmp_joins(args)
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
           if args[1].lower() == 'all':
              generate_show_ip_igmp_vrf_all_groups(args)
           else:
              api_response = generate_show_ip_igmp_groups(args)
              dlist.append(api_response)
              show_cli_output('show_ip_igmp_groups.j2', dlist)
        elif args[2].lower() == 'sources':
           if args[1].lower() == 'all':
              generate_show_ip_igmp_vrf_all_sources(args)
           else:
              api_response = generate_show_ip_igmp_sources(args)
              dlist.append(api_response)
              show_cli_output('show_ip_igmp_sources.j2', dlist)
        elif args[2].lower() == 'join':
              if args[1].lower() == 'all':
                 generate_show_ip_igmp_vrf_all_joins(args)
              else:
                 generate_show_ip_igmp_joins(args)
    elif func == 'clear_igmp' :
        keypath = cc.Path('/restconf/operations/sonic-igmp:clear-igmp')
        vrfname = "default"
        body = {"sonic-igmp:input": { "vrf-name" : vrfname,"interface_all" : True } }
        return api.post(keypath, body)
    elif func == 'clear_igmp_vrf' :
        vrfname = ""
        keypath = cc.Path('/restconf/operations/sonic-igmp:clear-igmp')
        _, vrfname = args[0].split("=")
        body = {"sonic-igmp:input": { "vrf-name" : vrfname,"interface_all" : True } }
        return api.post(keypath, body)
    else: 
        return api.cli_not_implemented(func)


def run(func, args):
    invoke_show_api(func, args)

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])
