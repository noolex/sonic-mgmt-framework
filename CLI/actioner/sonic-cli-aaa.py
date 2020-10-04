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


def do_show_aaa(content):

    # show aaa authentication already done

    # show aaa authorization
    if ( 'openconfig-system:aaa' in content ) \
       and ( 'authorization' in content['openconfig-system:aaa'] ) \
       and ( 'openconfig-aaa-ext:login' in \
           content['openconfig-system:aaa']['authorization'] ) \
       and ( 'config' in \
           content['openconfig-system:aaa']['authorization']\
               ['openconfig-aaa-ext:login'] ) \
       and ( 'authorization-method' in \
           content['openconfig-system:aaa']['authorization']\
               ['openconfig-aaa-ext:login']['config'] ):
       show_cli_output( 'show_aaa_authorization.j2', \
           content['openconfig-system:aaa']['authorization']\
               ['openconfig-aaa-ext:login']['config'] )

    # show aaa name-service
    if ( 'openconfig-system:aaa' in content ) \
       and ( 'openconfig-aaa-ext:name-service' in \
           content['openconfig-system:aaa'] ) \
       and ( 'config' in content['openconfig-system:aaa']\
           ['openconfig-aaa-ext:name-service'] ) \
       and ( len(content['openconfig-system:aaa']\
           ['openconfig-aaa-ext:name-service']['config'] ) != 0):
       show_cli_output( 'show_aaa_name_service.j2', \
           content['openconfig-system:aaa']['openconfig-aaa-ext:name-service']\
           ['config'] )

def invoke_api(func, args):
    body = None
    api = cc.ApiClient()

    # Set/Get aaa configuration
    failthrough='False'
    authmethod=[]

    if func == 'patch_openconfig_system_ext_system_aaa_authentication_config_failthrough':
       path = cc.Path('/restconf/data/openconfig-system:system/aaa/authentication/config/openconfig-system-ext:failthrough')
       if args[0] == 'True':
           failthrough = 'True'
       body = { "openconfig-system-ext:failthrough": failthrough}
       return api.put(path, body)
    elif func == 'patch_openconfig_system_system_aaa_authentication_config_authentication_method':
       path = cc.Path('/restconf/data/openconfig-system:system/aaa/authentication/config/authentication-method')
       # tricky logic: xml sends frist selection and values of both local and tacacs+ params
       # when user selects "local tacacs+", actioner receives "local local tacacs+"
       # when user selects "tacacs+ local", actioner receives "tacacs+ local tacacs+"

       authmethod.append(args[0])
       if len(args) == 3:
           if args[0] == args[1]:
               authmethod.append(args[2])
           else:
               authmethod.append(args[1])
       else:
           pass
       body = { "openconfig-system:authentication-method": authmethod}
       return api.patch(path, body)
    elif func == 'patch_openconfig_system_system_aaa_authentication_config_login':
       # Industry Standard CLI
       path = cc.Path('/restconf/data/openconfig-system:system/aaa/authentication/config/authentication-method')
       if args[0] == "group":
           authmethod.append(args[1])
       else:
           authmethod.append(args[0])

       if len(args) == 3:
           authmethod.append(args[2])

       body = { "openconfig-system:authentication-method": authmethod}
       return api.patch(path, body)
    elif func == 'get_openconfig_system_system_aaa_authentication_config':
       path = cc.Path('/restconf/data/openconfig-system:system/aaa/authentication/config')
       return api.get(path)
       # The above is the earlier style of "show aaa"
    elif func == 'get_openconfig_system_system_aaa':
       path = cc.Path('/restconf/data/openconfig-system:system/aaa/authentication/config')
       get_response = api.get(path)
       if get_response.ok() and ( get_response.content is not None ) :
            show_cli_output(args[0], get_response.content)
       path = cc.Path('/restconf/data/openconfig-system:system/aaa')
       get_response = api.get(path)
       if not get_response.ok():
           print("%Error: Invalid Response")
           return
       do_show_aaa(get_response.content)
       return get_response
    else:
       body = {}

    return api.cli_not_implemented(func)

def run(func, args):
    response = invoke_api(func, args)
    if response.ok():
        if response.content is not None:
            # Get Command Output
            api_response = response.content

            if api_response is None:
                print("%Error: Transaction Failure")
            elif func == 'get_openconfig_system_system_aaa_authentication_config':
                show_cli_output(args[0], api_response)
            else:
                return
    else:
        print(response.error_message())

if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])

