#!/usr/bin/python
"""
This module handles BGP EVPN Display commands
"""
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

import cli_client as cc
from scripts.render_cli import show_cli_output

RTTYPE_DICT = {
    "ead":"1",
    "es":"4",
    "macip":"2",
    "multicast":"3",
    "prefix":"5"
}

def evpn_args2dict(args):
    """Convert argument to dictionary"""
    dct = {}
    for elem in args:
        key, value = elem.split('=', 1)
        if value:
            dct[key] = value
    return dct

def apply_type_filter(response, rt_type):
    """Filter response based on type"""
    new_list = []
    if 'openconfig-bgp-evpn-ext:routes' in response:
        if 'route' in response['openconfig-bgp-evpn-ext:routes']:
            for i in range(len(response['openconfig-bgp-evpn-ext:routes']['route'])):
                route = response['openconfig-bgp-evpn-ext:routes']['route'][i]
                pfx_type = route['prefix'].split(':')[0].rstrip(']').lstrip('[')
                if RTTYPE_DICT[rt_type] == pfx_type:
                    new_list.append(route)
        response['openconfig-bgp-evpn-ext:routes']['route'] = new_list
    return response

def apply_macip_filter(response, mac, ip_addr):
    """Filter response based on MAC and IP"""
    new_list = []
    if 'openconfig-bgp-evpn-ext:routes' in response:
        if 'route' in response['openconfig-bgp-evpn-ext:routes']:
            for i in range(len(response['openconfig-bgp-evpn-ext:routes']['route'])):
                route = response['openconfig-bgp-evpn-ext:routes']['route'][i]
                pfx_type = route['prefix'].split(':')[0].rstrip(']').lstrip('[')
                if (pfx_type == RTTYPE_DICT['macip']
                        and mac in route['prefix']
                        and ip_addr in route['prefix']):
                    new_list.append(route)
        response['openconfig-bgp-evpn-ext:routes']['route'] = new_list
    return response

def apply_rd_filter(response, route_dist):
    """Filter response based on route distinguisher"""
    new_list = []
    if 'openconfig-bgp-evpn-ext:routes' in response:
        if 'route' in response['openconfig-bgp-evpn-ext:routes']:
            for i in range(len(response['openconfig-bgp-evpn-ext:routes']['route'])):
                route = response['openconfig-bgp-evpn-ext:routes']['route'][i]
                if route_dist == route['route-distinguisher']:
                    new_list.append(route)
        response['openconfig-bgp-evpn-ext:routes']['route'] = new_list
    return response

def invoke_api(func, args):
    """Process GET query"""
    api = cc.ApiClient()
    keypath = []

    if func == 'get_bgp_evpn_summary':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances'
                          +'/network-instance={vrf}/protocols/protocol=BGP,bgp/bgp/global',
                          vrf=args[0])
        response = api.get(keypath)
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances'
                          +'/network-instance={vrf}/protocols/protocol=BGP,bgp/bgp/neighbors',
                          vrf=args[0])
        response.content.update(api.get(keypath).content)
        return response
    if func == 'get_bgp_evpn_vni':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances'
                          +'/network-instance={vrf}/protocols/protocol=BGP,bgp/bgp/global'
                          +'/afi-safis/afi-safi={af_name}/l2vpn-evpn'
                          +'/openconfig-bgp-evpn-ext:vnis/vni={vni_number}/state',
                          vrf=args[0], af_name=args[1], vni_number=args[2])
        return api.get(keypath)
    if func == 'get_bgp_evpn_routes':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances'
                          +'/network-instance={vrf}/protocols/protocol=BGP,bgp/bgp/rib/afi-safis'
                          +'/afi-safi={af_name}/openconfig-bgp-evpn-ext:l2vpn-evpn/loc-rib/routes',
                          vrf=args[0], af_name=args[1])
        return api.get(keypath)
    if func == 'get_bgp_evpn_routes_filter':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances'
                          +'/network-instance={vrf}/protocols/protocol=BGP,bgp/bgp/rib/afi-safis'
                          +'/afi-safi={af_name}/openconfig-bgp-evpn-ext:l2vpn-evpn/loc-rib/routes',
                          vrf=args[0], af_name=args[1])
        response = api.get(keypath)
        if response.ok() and response.content is not None:
            if len(args) < 3:
                filterdict = {}
            else:
                filterdict = evpn_args2dict(args[2:])
            if "rd" in filterdict:
                if "type" in filterdict:
                    #apply rd,type filter
                    apply_rd_filter(response.content, filterdict["rd"])
                    apply_type_filter(response.content, filterdict["type"])
                elif "mac" in filterdict:
                    #apply rd,macip filter
                    apply_rd_filter(response.content, filterdict["rd"])
                    apply_macip_filter(response.content, filterdict["mac"], filterdict["ip"])
                else:
                    #apply rd only filter
                    apply_rd_filter(response.content, filterdict["rd"])
            elif "type" in filterdict:
                #apply type only filter
                apply_type_filter(response.content, filterdict["type"])
        return response
    return api.cli_not_implemented(func)

def run(func, args):
    """Main landing function"""
    response = invoke_api(func, args[1:])

    if response.ok():
        if response.content is not None:
            api_response = response.content
            show_cli_output(args[0], api_response)
        else:
            print("Empty response")
    else:
        print(response.error_message())
