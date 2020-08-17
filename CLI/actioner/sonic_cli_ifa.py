#!/usr/bin/python
###########################################################################
#
# Copyright 2019 Dell, Inc.
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
import json
import collections
import re
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
import urllib3
urllib3.disable_warnings()

def invoke_api(func, args):
    body = None
    api = cc.ApiClient()

    # Set/Get the rules of all IFA table entries.
    if func == 'get_sonic_ifa_sonic_ifa_tam_int_ifa_feature_table':
       path = cc.Path('/restconf/data/sonic-ifa:sonic-ifa/TAM_INT_IFA_FEATURE_TABLE')
       return api.get(path)
    elif func == 'get_sonic_ifa_sonic_ifa_tam_int_ifa_flow_table':
        if (len(args) == 2) and (args[1] != "all"):
           path = cc.Path('/restconf/data/sonic-ifa:sonic-ifa/TAM_INT_IFA_FLOW_TABLE/TAM_INT_IFA_FLOW_TABLE_LIST={name}', name=args[1])
        else:
           path = cc.Path('/restconf/data/sonic-ifa:sonic-ifa/TAM_INT_IFA_FLOW_TABLE')

        return api.get(path)

    elif func == 'patch_sonic_ifa_sonic_ifa_tam_int_ifa_feature_table_tam_int_ifa_feature_table_list_enable':
       path = cc.Path('/restconf/data/sonic-ifa:sonic-ifa/TAM_INT_IFA_FEATURE_TABLE/TAM_INT_IFA_FEATURE_TABLE_LIST')

       if args[0] == 'enable':
           body = { "sonic-ifa:TAM_INT_IFA_FEATURE_TABLE_LIST": [{"name": 'feature', "enable": True}] }
       else:
           body = { "sonic-ifa:TAM_INT_IFA_FEATURE_TABLE_LIST": [{"name": 'feature', "enable": False}] }
       return api.patch(path, body)

    elif func == 'patch_sonic_ifa_sonic_ifa_tam_int_ifa_flow_table_tam_int_ifa_flow_table_list':
       path = cc.Path('/restconf/data/sonic-ifa:sonic-ifa/TAM_INT_IFA_FLOW_TABLE/TAM_INT_IFA_FLOW_TABLE_LIST')
       bodydict = {"name": args[0], "acl-rule-name": args[1], "acl-table-name": args[2]}
       for i in range(len(args)):
           if args[i] == "sv":
               if args[i+1] != "cv":
                   bodydict["sampling-rate"] = int(args[i+1])
           elif args[i] == "cv":
               if i+1 < len(args):
                   bodydict["collector-name"] = args[i+1]
           else:
               pass
       body = { "sonic-ifa:TAM_INT_IFA_FLOW_TABLE_LIST": [ bodydict ] }
       return api.patch(path, body)

    elif func == 'delete_sonic_ifa_sonic_ifa_tam_int_ifa_flow_table_tam_int_ifa_flow_table_list':
        if args[0] != "all": 
            path = cc.Path('/restconf/data/sonic-ifa:sonic-ifa/TAM_INT_IFA_FLOW_TABLE/TAM_INT_IFA_FLOW_TABLE_LIST={name}', name=args[0])
        else:
            path = cc.Path('/restconf/data/sonic-ifa:sonic-ifa/TAM_INT_IFA_FLOW_TABLE/TAM_INT_IFA_FLOW_TABLE_LIST')

        return api.delete(path)

    else:
       body = {}

    return api.cli_not_implemented(func)

def run(func, args):

    if func == 'get_tam_ifa_status':
        get_tam_ifa_status(args)
        return
    elif func == 'get_tam_ifa_flow_stats':
        get_tam_ifa_flow_stats(args)
        return

    response = invoke_api(func, args)
    if response.ok():
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if 'sonic-ifa:sonic-ifa' in api_response:
                value = api_response['sonic-ifa:sonic-ifa']
                if 'TAM_INT_IFA_FEATURE_TABLE' in value:
                    tup = value['TAM_INT_IFA_FEATURE_TABLE']
                elif 'TAM_INT_IFA_FLOW_TABLE' in value:
                    tup = value['TAM_INT_IFA_FLOW_TABLE']
                else:
                    api_response = None

            if api_response is None:
                print("Failed")
            elif func == 'get_sonic_ifa_sonic_ifa_tam_int_ifa_feature_table':
                show_cli_output(args[0], api_response)
            elif func == 'get_sonic_ifa_sonic_ifa_tam_int_ifa_flow_table':
                show_cli_output(args[0], api_response)
            else:
                return
    else:
        if response.status_code != 404:
            print response.error_message()

def get_tam_ifa_status(args):
    api_response = {}
    api = cc.ApiClient()

    path = cc.Path('/restconf/data/sonic-tam:sonic-tam/TAM_DEVICE_TABLE')
    response = api.get(path)
    if response.ok():
        if response.content:
            api_response['device'] = response.content['sonic-tam:TAM_DEVICE_TABLE']['TAM_DEVICE_TABLE_LIST']

    path = cc.Path('/restconf/data/sonic-tam:sonic-tam/TAM_COLLECTOR_TABLE')
    response = api.get(path)
    if response.ok():
        if response.content:
            api_response['collector'] = response.content['sonic-tam:TAM_COLLECTOR_TABLE']['TAM_COLLECTOR_TABLE_LIST']

    path = cc.Path('/restconf/data/sonic-ifa:sonic-ifa/TAM_INT_IFA_FEATURE_TABLE')
    response = api.get(path)
    if response.ok():
        if response.content:
            api_response['feature'] = response.content['sonic-ifa:TAM_INT_IFA_FEATURE_TABLE']['TAM_INT_IFA_FEATURE_TABLE_LIST']

    path = cc.Path('/restconf/data/sonic-ifa:sonic-ifa/TAM_INT_IFA_FLOW_TABLE')
    response = api.get(path)
    if response.ok():
        if response.content:
            api_response['flow'] = response.content['sonic-ifa:TAM_INT_IFA_FLOW_TABLE']['TAM_INT_IFA_FLOW_TABLE_LIST']

    show_cli_output("show_tam_ifa_status.j2", api_response)

def get_tam_ifa_flow_stats(args):
    api_response = {}
    api = cc.ApiClient()

    if (len(args) == 1) and (args[0] != "all"):
       path = cc.Path('/restconf/data/sonic-ifa:sonic-ifa/TAM_INT_IFA_FLOW_TABLE/TAM_INT_IFA_FLOW_TABLE_LIST={name}', name=args[0])
    else:
       path = cc.Path('/restconf/data/sonic-ifa:sonic-ifa/TAM_INT_IFA_FLOW_TABLE')

    response = api.get(path)

    if response.ok():
        if response.content:
            if (len(args) == 1) and (args[0] != "all"):
                api_response = response.content['sonic-ifa:TAM_INT_IFA_FLOW_TABLE_LIST']
            else:
                api_response = response.content['sonic-ifa:TAM_INT_IFA_FLOW_TABLE']['TAM_INT_IFA_FLOW_TABLE_LIST']

            for i in range(len(api_response)):
                api_response[i]['Packets'] = 0
                api_response[i]['Bytes'] = 0

                path = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets')
                acl_info = api.get(path)
                if acl_info.ok():
                    if acl_info.content:
                        acl_list = acl_info.content["openconfig-acl:acl-sets"]["acl-set"]
                        for acl in acl_list:
                            if acl['name'] == api_response[i]['acl-table-name']:
                                rule = api_response[i]['acl-rule-name']
                                # tokenize the rulename with '_' and fetch last number
                                tmpseq = (rule.split("_", 1))[-1]
                                acl_entry_list = acl["acl-entries"]["acl-entry"]
                                for entry in acl_entry_list:
                                    if int(tmpseq) == int(entry["sequence-id"]):
                                        api_response[i]['Packets'] = entry["state"]["matched-packets"]
                                        api_response[i]['Bytes'] = entry["state"]["matched-octets"]

    show_cli_output("show_tam_ifa_flow_stats.j2", api_response)

if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]
    if func == 'get_tam_ifa_status':
        get_tam_ifa_status(sys.argv[2:])
    elif func == 'get_tam_ifa_flow_stats':
        get_tam_ifa_flow_stats(sys.argv[2:])
    else:
        run(func, sys.argv[2:])

