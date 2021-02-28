#!/usr/bin/python
###########################################################################
#
# Copyright 2020 Dell, Inc.
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
from rpipe_utils import pipestr
from render_cli import show_cli_output
from sonic_intf_utils import name_to_int_val
import cli_client as cc
import re
import urllib3
urllib3.disable_warnings()

def print_exception(e):
    if e.body != "":
        body = json.loads(e.body)
        if "ietf-restconf:errors" in body:
            err = body["ietf-restconf:errors"]
            if "error" in err:
                errDict = {}
                for dict in err["error"]:
                    for k, v in dict.iteritems():
                        errDict[k] = v
                if "error-message" in errDict:
                    print("% Error: " + errDict["error-message"])
                    return
    else:
        print("% Error: Transaction failure.")
    return

def invoke_api(func, args=[]):
    api = cc.ApiClient()

    if func == 'put_sonic_sflow_sonic_sflow_sflow_collector_sflow_collector_list':
        path = cc.Path('/restconf/data/openconfig-sampling:sampling/sflow/collectors')
        body = {"openconfig-sampling:collectors": {
                "collector": [
                {
                    "address": args[0],
                    "port": int(args[1]),
                    "vrf": args[2],
                    "config": {
                        "address": args[0],
                        "port": int(args[1]),
                        "vrf": args[2]
                    }
                }]}}
        return api.put(path, body)
    elif func == 'delete_sonic_sflow_sonic_sflow_sflow_collector_sflow_collector_list':
        name = args[0] + ',' + args[1] + ',' + args[2]
        path = cc.Path('/restconf/data/openconfig-sampling:sampling/sflow/collectors/collector=' + name)
        return api.delete(path)

    elif func == 'patch_sonic_sflow_sonic_sflow_sflow_session_sflow_session_list_sample_rate':
        path = cc.Path('/restconf/data/openconfig-sampling:sampling/sflow/interfaces')
        body = {"openconfig-sampling:interfaces": {
                "interface": [{
                    "name": args[0],
                    "config": {
                        "name": args[0],
                        "sampling-rate": int(args[1])
               }}]}}
        return api.patch(path, body)
    elif func == 'delete_sonic_sflow_sonic_sflow_sflow_session_sflow_session_list_sample_rate':
        path = cc.Path('/restconf/data/openconfig-sampling:sampling/sflow/interfaces/interface={ifname}/config/sampling-rate',
                       ifname=args[0])
        return api.delete(path)
    elif func == 'patch_sonic_sflow_sonic_sflow_sflow_session_sflow_session_list_admin_state':
        path = cc.Path('/restconf/data/openconfig-sampling:sampling/sflow/interfaces')
        body = {"openconfig-sampling:interfaces": {
                "interface": [{
                    "name": args[0],
                    "config": {
                        "name": args[0],
                        "enabled": (args[1] == "up"),
               }}]}}
        return api.patch(path, body)
    elif func == 'patch_sonic_sflow_sonic_sflow_sflow_sflow_list_admin_state':
        path = cc.Path('/restconf/data/openconfig-sampling:sampling/sflow/config/enabled')
        body = {
              "openconfig-sampling:enabled": (args[0] == "up")
        }
        return api.patch(path, body)
    elif func == 'patch_sonic_sflow_sonic_sflow_sflow_sflow_list_agent_id':
        path = cc.Path('/restconf/data/openconfig-sampling:sampling/sflow/config/openconfig-sampling-ext:agent')
        body = {
              "openconfig-sampling-ext:agent": args[0]
        }
        return api.patch(path, body)
    elif func == 'patch_sonic_sflow_sonic_sflow_sflow_sflow_list_polling_interval':
        path = cc.Path('/restconf/data/openconfig-sampling:sampling/sflow/config/openconfig-sampling-ext:polling-interval')
        body = {
              "openconfig-sampling-ext:polling-interval": int(args[0])
        }
        return api.patch(path, body)
    elif func == 'delete_sonic_sflow_sonic_sflow_sflow_sflow_list_polling_interval':
        path = cc.Path('/restconf/data/openconfig-sampling:sampling/sflow/config/openconfig-sampling-ext:polling-interval')
        return api.delete(path)
    elif func == 'delete_sonic_sflow_sonic_sflow_sflow_sflow_list_agent_id':
        path = cc.Path('/restconf/data/openconfig-sampling:sampling/sflow/config/openconfig-sampling-ext:agent')
        return api.delete(path)
    elif func == 'get_sonic_sflow_sonic_sflow_sflow_session_table':
        path = cc.Path('/restconf/data/openconfig-sampling:sampling/sflow/interfaces')
        return api.get(path)
    elif func == 'get_sonic_sflow_sonic_sflow':
        path = cc.Path('/restconf/data/openconfig-sampling:sampling/sflow')
        return api.get(path)

    return api.cli_not_implemented(fn)


def run(func, args):
    try:
        response = invoke_api(func, args)

        if (response.ok() is False):
            print response.error_message()
            return 1

        if func == 'get_sonic_sflow_sonic_sflow_sflow_session_table':
            sess_lst = [[]]
            if response.content:
                sess_lst = response.content['openconfig-sampling:interfaces']['interface']
                sess_lst = [sorted(sess_lst, key=lambda x : name_to_int_val(x['name']))]
            show_cli_output(args[0], sess_lst)

        elif func == 'get_sonic_sflow_sonic_sflow':
            show_cli_output(args[0], response.content)

    except Exception as e:
        print("% Error: Internal error: " + str(e))
        return 1
    return 0

if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]
    ret = run(func, sys.argv[2:])
    sys.exit(ret)
