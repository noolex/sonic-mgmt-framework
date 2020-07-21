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
import time
import json
import ast
from rpipe_utils import pipestr
import cli_client as cc
import collections

IDENTIFIER='STATIC'
NAME1='static'

restconf_map = {

    'openconfig_network_instance_network_instances_network_instance_protocols_protocol_static_routes_static_next_hops_next_hop' :
        '/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/static-routes',
}
restconf_map_del = {

    'openconfig_network_instance_network_instances_network_instance_protocols_protocol_static_routes_static_next_hops_next_hop' :
        '/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/static-routes/static={prefix}/next-hops/next-hop={index}',
}

def invoke_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    op, attr = func.split('_', 1)
    uri = restconf_map[attr]
       
    if op == 'patch':
        if attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_static_routes_static_next_hops_next_hop':
            body =  { "openconfig-network-instance:static-routes": { "static": [
                      {
                       "prefix": args[1],
                       "next-hops": { "next-hop": [ {
                          "index": "",
                          "config": {
                             "index": ""
                          }}]
                       }}
                    ]}} 
            conf_ip = "false"
            index_v = ''
            if ((args[2] != 'interface') and (args[2] != 'blackhole')):
                # its the ip address
                body["openconfig-network-instance:static-routes"]["static"][0]["next-hops"]["next-hop"][0]["config"]["next-hop"] =args[2]
                index_v =  args[2]
                conf_ip ="true"

            i = 2 
            while(i<len(args)): 
                if args[i].isdigit():
                    body["openconfig-network-instance:static-routes"]["static"][0]["next-hops"]["next-hop"][0]["config"]["metric"]=int(args[i])
                elif args[i]=='interface':
                    i+=1
                    body["openconfig-network-instance:static-routes"]["static"][0]["next-hops"]["next-hop"][0]["interface-ref"] = {"config": {"interface": args[i]}}
                    index_v =  args[i]
                    if  conf_ip == "true" : index_v = index_v +  '_' + args[2]
                elif args[i] == 'nexthop-vrf':
                    i+=1
                    body["openconfig-network-instance:static-routes"]["static"][0]["next-hops"]["next-hop"][0]["config"]["nexthop-network-instance"] =args[i]
                    index_v = index_v +  '_' + args[i]
                elif args[i] == 'blackhole':
                    body["openconfig-network-instance:static-routes"]["static"][0]["next-hops"]["next-hop"][0]["config"]["blackhole"] =True
                    index_v = "DROP"

                i+=1

            keypath = cc.Path(uri,
                      name=args[0], identifier = IDENTIFIER, name1=NAME1)
            body["openconfig-network-instance:static-routes"]["static"][0]["next-hops"]["next-hop"][0]["index"] = index_v 
            body["openconfig-network-instance:static-routes"]["static"][0]["next-hops"]["next-hop"][0]["config"]["index"] = index_v
            return api.patch(keypath, body)
        else:  
            return api.cli_not_implemented(func)     
    elif op == 'delete':
        uri = restconf_map_del[attr]
        if attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_static_routes_static_next_hops_next_hop':
            i = 2
            index_v = ''
            conf_ip = "false"
            if ((args[2] != 'interface') and (args[2] != 'blackhole')):
                index_v =  args[2]
                conf_ip ="true"
            while(i<len(args)):
                if args[i]=='interface':
                    i+=1
                    index_v =  args[i]
                    if conf_ip =="true": index_v = index_v +  '_' + args[2]
                elif args[i] == 'nexthop-vrf':
                    i+=1
                    index_v = index_v +  '_' + args[i]
                elif args[i] == 'blackhole':
                    index_v = "DROP"

                i+=1

            keypath = cc.Path(uri,
                      name=args[0], identifier = IDENTIFIER, name1=NAME1, prefix = args[1], index=index_v)
            return api.delete(keypath) 
        else:
            return api.cli_not_implemented(func)
    return api.cli_not_implemented(func) 

def run(func, args):
    try:
        response = invoke_api(func, args)
        if not response.ok():
           print(response.error_message())
    except Exception as e:
        print("%Error: Static Route Transaction Failure")

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])

