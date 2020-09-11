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
    baseServerGrpUri = "/restconf/data/openconfig-system:system/aaa/server-groups/server-group"
    baseLdapUri = "/restconf/data/openconfig-system:system/aaa/server-groups/server-group=LDAP/"

    if commandType == 'ldap_global_config' :
        ldap_type = "LDAP"
    elif commandType == 'ldap_nss_config' :
        ldap_type = "LDAP_NSS"
    elif commandType == 'ldap_pam_config' :
        ldap_type = "LDAP_PAM"
    elif commandType == 'ldap_sudo_config' : 
        ldap_type = "LDAP_SUDO"
               
    if commandType == 'ldap_global_config' or commandType == 'ldap_nss_config' or commandType == 'ldap_pam_config' or commandType == 'ldap_sudo_config':
        if isDel == False :
            field_val = args[1]
            field_val = field_val.replace("\\\\", "\\")
            
        if args[0] == "timelimit" :
            field_name = "search-time-limit"
            if isDel == False:
                bodyParam = int(field_val)
        elif args[0] == "bind-timelimit" :
            field_name = "bind-time-limit"
            if isDel == False:
                bodyParam = int(field_val)
        elif args[0] == "idle-timelimit" :
            field_name = "idle-time-limit"
            if isDel == False:
                bodyParam = int(field_val)
        elif args[0] == "retry" :
            field_name = "retransmit-attempts"
            if isDel == False:
                bodyParam = int(field_val)
        elif args[0] == "port" :
            field_name = "port"
            if isDel == False:
                bodyParam = int(field_val)
        elif args[0] == "version" :
            field_name = "version"
            if isDel == False:
                bodyParam = int(field_val)
        elif args[0] == "base" :
            field_name = "base"
            bodyParam = field_val
        elif args[0] == "ssl" :
            field_name = "ssl"
            if isDel == False:
                bodyParam = field_val.upper()
        elif args[0] == "binddn" :
            field_name = "bind-dn"
            bodyParam = field_val            
        elif args[0] == "bindpw" :
            field_name = "bind-pw"
            bodyParam = field_val            
        elif args[0] == "scope" :
            field_name = "scope"
            if isDel == False:
                bodyParam = field_val.upper()            
        elif args[0] == "nss-base-passwd" :
            field_name = "nss-base-passwd"
            bodyParam = field_val            
        elif args[0] == "nss-base-group" :
            field_name = "nss-base-group"
            bodyParam = field_val            
        elif args[0] == "nss-base-shadow" :
            field_name = "nss-base-shadow"
            bodyParam = field_val            
        elif args[0] == "nss-base-netgroup" :
            field_name = "nss-base-netgroup"
            bodyParam = field_val            
        elif args[0] == "nss-base-sudoers" :
            field_name = "nss-base-sudoers"
            bodyParam = field_val            
        elif args[0] == "nss-initgroups-ignoreusers" :
            field_name = "nss-initgroups-ignoreusers"
            bodyParam = field_val            
        elif args[0] == "sudoers-base" :
            field_name = "sudoers-base"
            bodyParam = field_val            
        elif args[0] == "pam-filter" :
            field_name = "pam-filter"
            bodyParam = field_val            
        elif args[0] == "pam-login-attribute" :
            field_name = "pam-login-attribute"
            bodyParam = field_val            
        elif args[0] == "pam-group-dn" :
            field_name = "pam-group-dn"
            bodyParam = field_val            
        elif args[0] == "pam-member-attribute" :
            field_name = "pam-member-attribute"
            bodyParam = field_val            
        
        if isDel == False :
            keypath = cc.Path(baseServerGrpUri)
            body = {"openconfig-system:server-group":[{"name":ldap_type,"config":{"name":ldap_type}, modName+"ldap":{"config":{field_name:bodyParam}}}]}            
            return aa.patch(keypath, body)
        else:
            keypath = cc.Path('/restconf/data/openconfig-system:system/aaa/server-groups/server-group={ldapType}/'+modName+'ldap/config/{fieldName}',
            ldapType=ldap_type, fieldName=field_name)
            return aa.delete (keypath)
               
    elif commandType == 'ldap_server_config':
        if isDel == False :
            keypath = cc.Path(baseServerGrpUri)
            body = {"openconfig-system:server-group":[{"name":"LDAP","config":{"name":"LDAP"}, "servers":{"server":[{"address":args[0],"config":{"address":args[0]},"openconfig-aaa-ldap-ext:ldap":{"config":{}}}]}}]}
            configObj = body["openconfig-system:server-group"][0]["servers"]["server"][0][modName+"ldap"]["config"]
            for elem in args:
                if elem == 'use-type':
                    configObj["use-type"] = args[args.index(elem)+1].upper()
                elif elem == 'port':
                    configObj["port"] = int(args[args.index(elem)+1])
                elif elem == 'priority':
                    configObj["priority"] = int(args[args.index(elem)+1])
                elif elem == 'ssl':
                    configObj["ssl"] = args[args.index(elem)+1].upper()
                elif elem == 'retry':
                    configObj["retransmit-attempts"] = int(args[args.index(elem)+1])
            return aa.patch(keypath, body)
        else:
            objName = None
            if len(args) > 1: 
                if args[1] == 'use-type':
                    objName = 'use-type'
                elif args[1] == 'port':
                    objName = 'port'
                elif args[1] == 'priority':
                    objName = 'priority'
                elif args[1] == 'ssl':
                    objName = 'ssl'
                elif args[1] == 'retry':
                    objName = 'retransmit-attempts'
                keypath = cc.Path(baseLdapUri+'servers/server={address}/'+modName+'ldap/config/'+objName, address=args[0])
            else:   
                keypath = cc.Path(baseLdapUri+'servers/server={address}', address=args[0])
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
            keypath = cc.Path(baseServerGrpUri)
            body = {"openconfig-system:server-group":[{"name":"LDAP","config":{"name":"LDAP"},"openconfig-aaa-ldap-ext:ldap":{"maps":{"map":[{"config":{"to":args[3].replace("\\\\", "\\")},"from":args[1].replace("\\\\", "\\"),"name":mapName}]}}}]}
            return aa.patch(keypath, body)
        else:
            keyVal = args[1].replace("\\\\", "\\")
            keypath = cc.Path(baseLdapUri+modName+'ldap/maps/map='+mapName+','+keyVal.replace("/","%2F"))
            return aa.delete(keypath)
    elif func == 'ldap_server_src_if_config':
        path = cc.Path('/restconf/data/openconfig-system:system/aaa/server-groups/server-group=LDAP/openconfig-aaa-ldap-ext:ldap/config/source-interface')
        body = { "openconfig-aaa-ldap-ext:source-interface": args[0] if args[0] != 'Management0' else 'eth0' }
        return aa.patch(path, body)
    elif func == 'ldap_server_vrf_config':
        path = cc.Path('/restconf/data/openconfig-system:system/aaa/server-groups/server-group=LDAP/openconfig-aaa-ldap-ext:ldap/config/vrf-name')
        body = { "openconfig-aaa-ldap-ext:vrf-name": args[0]}
        return aa.patch(path, body)
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

    except Exception:
        # system/network error
        print "%Error: Transaction Failure"


if __name__ == '__main__':
    pipestr().write(sys.argv)
    #pdb.set_trace()
    run(sys.argv[1], sys.argv[2:])
