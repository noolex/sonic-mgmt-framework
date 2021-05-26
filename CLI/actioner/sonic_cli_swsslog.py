#!/usr/bin/python
###########################################################################
#
# Copyright 2019 Broadcom. The term Broadcom refers to Broadcom Inc. and/or
# its subsidiaries.
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

def set_openconfig_loglevel_severity(args):
    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/operations/openconfig-system-ext:set-loglevel-severity')
    if args[3]=="yes":
       is_sai = True
    else:
       is_sai = False 
    body = { "openconfig-system-ext:input":{"loglevel": args[1], "component-name":args[2], "sai-component": is_sai}}
    api_response = aa.post(keypath, body)
    templ = args[0]

    try:
        if api_response.ok():
           response = api_response.content
           if response is not None and 'openconfig-system-ext:output' in response:
              show_cli_output(templ, response)
    except Exception as e:
        print("%Error: Traction Failure: " + e)

def get_openconfig_loglevel_from_db(args):
    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/operations/openconfig-system-ext:get-loglevel-severity')
    body = None
    api_response = aa.post(keypath, body)
    templ = args[0]

    try:
        if api_response.ok():
           response = api_response.content
           if response is not None and 'openconfig-system-ext:output' in response:
              show_cli_output(templ, response)
    except Exception as e:
        print("%Error: Traction Failure: " + e)

def run(func, args):
    if func == 'set_openconfig_loglevel_severity':
        set_openconfig_loglevel_severity(args)
        return 0

    if func == 'get_openconfig_loglevel_from_db':
        get_openconfig_loglevel_from_db(args)
        return 0


if __name__ == '__main__':
    import sys
    from rpipe_utils import pipestr

    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])

