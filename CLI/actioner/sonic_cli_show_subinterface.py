#!/usr/bin/python
"""
This module handles Subinterface Display commands
"""
###########################################################################
#
# Copyright 2020 Broadcom, Inc.
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
from natsort import natsorted

def add_speed_and_mtu(data_in):
    """Add speed and mtu fields for subinterface through querying parent if tables"""
    api = cc.ApiClient()
    keypath = []
    if 'sonic-interface:VLAN_SUB_INTERFACE_LIST' not in data_in:
        return
    parent_if_list = {d['parent'] for d in data_in['sonic-interface:VLAN_SUB_INTERFACE_LIST']}
    parent_data = dict()
    for item in parent_if_list:
        if item.startswith('Eth'):
            keypath = cc.Path('/restconf/data/sonic-port:sonic-port/PORT_TABLE'
                              +'/PORT_TABLE_LIST={name}', name=item)
            response = api.get(keypath)
            if response.ok() and response.content is not None:
                parent_data[item] = dict()
                parent_data[item]['mtu'] = \
                    response.content['sonic-port:PORT_TABLE_LIST'][0]['mtu']
                parent_data[item]['speed'] = \
                    response.content['sonic-port:PORT_TABLE_LIST'][0]['speed']
        elif item.startswith('Po'):
            keypath = cc.Path('/restconf/data/sonic-portchannel:sonic-portchannel'
                              +'/LAG_TABLE/LAG_TABLE_LIST={name}', name=item)
            response = api.get(keypath)
            if response.ok() and response.content is not None:
                parent_data[item] = dict()
                parent_data[item]['mtu'] = \
                    response.content['sonic-portchannel:LAG_TABLE_LIST'][0]['mtu']
                if 'speed' in response.content['sonic-portchannel:LAG_TABLE_LIST'][0]:
                    parent_data[item]['speed'] = \
                        response.content['sonic-portchannel:LAG_TABLE_LIST'][0]['speed']
                else:
                    parent_data[item]['speed'] = "n/a"
    data_in['aux_info'] = parent_data

def invoke_api(func, args):
    """Handle GET request"""
    api = cc.ApiClient()
    keypath = []

    if func == 'status_sonic':
        keypath = cc.Path('/restconf/data/sonic-interface:sonic-interface/VLAN_SUB_INTERFACE'
                          +'/VLAN_SUB_INTERFACE_LIST')
        response = api.get(keypath)
        renderer = 'show_subinterfaces_status_sonic.j2'
        return response, renderer

    return api.cli_not_implemented(func), ''

def run(func, args):
    """Main landing function"""
    response, renderer = invoke_api(func, args[1:])
    if response.ok():
        if response.content is not None:
            api_response = response.content
            add_speed_and_mtu(api_response)
            tbl_key = "sonic-interface:VLAN_SUB_INTERFACE_LIST"
            if tbl_key in api_response:
                api_response[tbl_key] = natsorted(api_response[tbl_key], key=lambda t: t["id"])
            show_cli_output(renderer, api_response)
        else:
            print("Empty response")
    else:
        print(response.error_message())
