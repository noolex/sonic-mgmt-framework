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
import os
import json
import ast
import subprocess
from rpipe_utils import pipestr
import cli_client as cc
from scripts.render_cli import show_cli_output

def get_value(in_dict, ifname, field, default):
    for item in in_dict:
        if item["ifname"] == ifname and field in item:
            return item[field]
    return default


def get_if_master_and_oper(in_data, state_data):
    data = in_data
    totalgwipv4 = 0
    adminupgwipv4 = 0
    operupgwipv4 = 0
    totalgwipv6 = 0
    adminupgwipv6 = 0
    operupgwipv6 = 0
    output = {}

    for item in data:
        if "ifname" in item:
            if item["ifname"] not in output:
                output[item["ifname"]] = {}
            vrf = get_value(state_data, item["ifname"], "vrf", "")
            if vrf != "default":
                output[item["ifname"]]["master"] = vrf
            else:
                output[item["ifname"]]["master"] = ""
            for ip in item['gwip']:
                output[item["ifname"]][ip] = {}
                output[item["ifname"]][ip]["admin_state"] = "down"
                output[item["ifname"]][ip]["oper_state"] = "down"
                if item["table_distinguisher"] == "IPv6":
                    iplist = get_value(state_data, item["ifname"], "v6GwIp", [])
                    if ip in iplist:
                        output[item["ifname"]][ip]["admin_state"] = "up"
                        output[item["ifname"]][ip]["oper_state"] = get_value(state_data, item["ifname"], "oper", "down")
                    totalgwipv6 = totalgwipv6 + 1
                    if output[item["ifname"]][ip]["admin_state"] == "up":
                        adminupgwipv6 = adminupgwipv6 + 1
                    if output[item["ifname"]][ip]["oper_state"] == "up":
                        operupgwipv6 = operupgwipv6 + 1
                else:
                    iplist = get_value(state_data, item["ifname"], "v4GwIp", [])
                    if ip in iplist:
                        output[item["ifname"]][ip]["admin_state"] = "up"
                        output[item["ifname"]][ip]["oper_state"] = get_value(state_data, item["ifname"], "oper", "down")
                    totalgwipv4 = totalgwipv4 + 1
                    if output[item["ifname"]][ip]["admin_state"] == "up":
                        adminupgwipv4 = adminupgwipv4 + 1
                    if output[item["ifname"]][ip]["oper_state"] == "up":
                        operupgwipv4 = operupgwipv4 + 1

    output["counters"] = {}
    output["counters"]["totalgw"] = {'IPv4':totalgwipv4, 'IPv6':totalgwipv6}
    output["counters"]["adminupgw"] = {'IPv4':adminupgwipv4, 'IPv6':adminupgwipv6}
    output["counters"]["operupgw"] = {'IPv4':operupgwipv4, 'IPv6':operupgwipv6}

    return output


def invoke_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None
    output = {}
    
    keypath = cc.Path('/restconf/data/sonic-sag:sonic-sag/SAG/SAG_LIST')
    res = api.get(keypath)
    output["sag"] = res.content
    keypath = cc.Path('/restconf/data/sonic-sag:sonic-sag/SAG_GLOBAL/SAG_GLOBAL_LIST')
    res = api.get(keypath)
    output["global"] = res.content
    keypath = cc.Path('/restconf/data/sonic-sag:sonic-sag/SAG_INTF/SAG_INTF_LIST')
    res = api.get(keypath)
    output["sagstate"] = res.content
    if func == 'get_ip_sag':
        output["family"] = "IPv4"
    else:
        output["family"] = "IPv6"
    return output
    


def run(func, args):
    response = invoke_api(func, args[1:])

    api_response = response
    if "sonic-sag:SAG_LIST" in api_response["sag"]:
        api_response["miscmap"] = get_if_master_and_oper(api_response["sag"]["sonic-sag:SAG_LIST"], api_response["sagstate"]["sonic-sag:SAG_INTF_LIST"])
    #print(api_response)
    show_cli_output(args[0], api_response)

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])
