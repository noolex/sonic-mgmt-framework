#!/usr/bin/python
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

import sys
import json
import collections
import re
import cli_client as cc
from rpipe_utils import pipestr

def invoke(func, args):
    body = None
    aa = cc.ApiClient()

    commandType = func
    
    isDel = False
    if func.startswith('del_') :
        isDel = True
        commandType = func.split('del_')[1]
   
    field_val = None
    bodyParam = None
    
    modName = "openconfig-aaa-ldap-ext:"
    baseLdapUri = "/restconf/data/openconfig-system:system/aaa/server-groups/server-group=LDAP/"
               
    if commandType == 'ldap_server_config':
        if isDel == False :
            keypath = cc.Path(baseLdapUri+'servers/server={address}', address=args[0])
            body = {   "openconfig-system:server": [ {
                       "address": args[0],
                       "config": {
                           "address": args[0],
                       },
                       modName+"ldap": {
                           "config": {
                           }
                       }
                  } ]
               }
            
            configObj = body["openconfig-system:server"][0][modName+"ldap"]["config"]
            
            for elem in args:
                if elem == 'use-type':
                    configObj["use-type"] = args[args.index(elem)+1].upper()
                elif elem == 'port':
                    configObj["port"] = int(args[args.index(elem)+1])
                elif elem == 'priority':
                    configObj["priority"] = int(args[args.index(elem)+1])
                elif elem == 'ssl':
                    configObj["ssl"] = args[args.index(elem)+1].upper()
                    
            return aa.patch(keypath, body)
        else:
            objName = None
            if args[1] == 'use-type':
                objName = 'use-type'
            elif args[1] == 'port':
                objName = 'port'
            elif args[1] == 'priority':
                objName = 'priority'
            elif args[1] == 'ssl':
                objName = 'ssl'
            
            keypath = cc.Path(baseLdapUri+'servers/server={address}/'+modName+'ldap/config/'+objName, address=args[0])
            return aa.delete(keypath)     
    elif commandType == 'ldap_map_config':
        mapName = ""
        if args[0] == "attribute":
            mapName = "ATTRIBUTE"
        elif args[0] == "objectclass":
            mapName = "OBJECTCLASS"
        elif args[0] == "default-attribute-value":
            mapName = "DEFAULT_ATTRIBUTE_VALUE"
        elif args[0] == "override-attribute-value":
            mapName = "OVERRIDE_ATTRIBUTE_VALUE"
        
        if isDel == False :
            keypath = cc.Path(baseLdapUri+modName+'ldap/maps/map='+mapName+','+args[1]+'/config/to')
            body = { modName+"to": args[3] } 
            return aa.patch(keypath, body)
        else:
            keypath = cc.Path(baseLdapUri+modName+'ldap/maps/map='+mapName+','+args[1]+'/config/to')
            return aa.delete(keypath)
    else:
        print("%Error: not implemented")
        exit(1)

def run(func, args):
    try:
        api_response = invoke(func, args)
        if api_response.ok():
            response = api_response.content
            if response is None:
                return
            else:
                print "%Error: Invalid command"
        else:
            #error response
            print api_response.error_message()

    except Exception as e:
            # system/network error
            print "%Error: Transaction Failure"


if __name__ == '__main__':
    pipestr().write(sys.argv)
    #pdb.set_trace()
    run(sys.argv[1], sys.argv[2:])
