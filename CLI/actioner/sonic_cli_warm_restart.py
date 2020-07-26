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
import collections
from rpipe_utils import pipestr
import cli_client as cc
from scripts.render_cli import show_cli_output

def invoke_api(func, args=[]):
    api = cc.ApiClient()

    # Warm restart state information
    if func == 'get_openconfig_warm_restart_warm_restart_status_submodules':
        path = cc.Path('/restconf/data/openconfig-warm-restart:warm-restart/status')
        return api.get(path)

    # Warm restart system service enable
    if func == 'patch_openconfig_warm_restart_warm_restart_config_enable':
        path = cc.Path('/restconf/data/openconfig-warm-restart:warm-restart')
        body = {
                 "openconfig-warm-restart:warm-restart" : {
                   "config" : {
                     "enable" : True
                   }
                 }
               }
        return api.patch(path,body)

    # Warm restart BGP/TEAMD/SWSS service enable
    if func == 'patch_openconfig_warm_restart_warm_restart_enable_modules_config_enable':
        path = cc.Path('/restconf/data/openconfig-warm-restart:warm-restart/enable')
        body = {
                 "openconfig-warm-restart:enable": {
                   "modules": [
                     {
                       "module": args[0].upper(),
                       "config": {
                         "module": args[0].upper(),
                         "enable": True if args[1] == "true" else False
                       }
                     }
                   ]
                 }
               }
        return api.patch(path,body) 
    
    # Warm restart BGP eoiu config
    if func == 'patch_openconfig_warm_restart_warm_restart_config_bgp_eoiu':
        path = cc.Path('/restconf/data/openconfig-warm-restart:warm-restart')
        body = {
                 "openconfig-warm-restart:warm-restart" : {
                   "config" : {
                     "bgp-eoiu" : True if args[1] == "true" else False
                   }
                 }
               }
        return api.patch(path,body)

    # Warm restart BGP, SWSS, TEAMD timer config
    if func == 'patch_openconfig_warm_restart_warm_restart_timers_timer_config_value':
        path = cc.Path('/restconf/data/openconfig-warm-restart:warm-restart/timers')
        body = {
           "openconfig-warm-restart:timers": {
             "timer": [
               {
                 "submodule": args[0].upper(),
                 "config": {
                   "submodule": args[0].upper(),
                   "value": int(args[1])
                 }
               }
             ]
           }
         }
        return api.patch(path,body)

    # Disable warm restart system service
    if func == 'delete_openconfig_warm_restart_warm_restart_config_enable':
        path = cc.Path('/restconf/data/openconfig-warm-restart:warm-restart/config/enable')
        return api.delete(path)

    # Disable warm restart BGP, SWSS, TEAMD service
    if func == 'delete_openconfig_warm_restart_warm_restart_enable_modules_config_enable':
        path = cc.Path('/restconf/data/openconfig-warm-restart:warm-restart/enable/modules={module}/config/enable', module=args[0].upper())
        return api.delete(path)

    # Disable warm restart BGP EOIU flag
    if func == 'delete_openconfig_warm_restart_warm_restart_config_bgp_eoiu':
        path = cc.Path('/restconf/data/openconfig-warm-restart:warm-restart/config/bgp-eoiu')
        return api.delete(path)

    # Disable warm restart BGP, SWSS , TEAMD timer
    if func == 'delete_openconfig_warm_restart_warm_restart_timers_timer_config_value':
        path = cc.Path('/restconf/data/openconfig-warm-restart:warm-restart/timers/timer={submodule}/config/value', submodule=args[0].upper())
        return api.delete(path)

    return api.cli_not_implemented(func)

def run(func, args):
    response = invoke_api(func, args)
    if response.ok():
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            show_cli_output(args[0], api_response)
    else:
        print response.error_message()

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])
