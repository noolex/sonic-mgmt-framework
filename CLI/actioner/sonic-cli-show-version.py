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

import syslog as log
import sys
import time
import json
import ast
import cli_client as cc
import urllib3
from scripts.render_cli import show_cli_output

urllib3.disable_warnings()

def invoke(func, args):
    body = None
    aa = cc.ApiClient()

    if func == 'get_openconfig_platform_components_component':
        keypath = cc.Path('/restconf/data/openconfig-platform:components/component=%s'%args[0])
        return aa.get(keypath)
    else:
        return body

def run(func, args):
    try:
        api_response = invoke(func,args)

        if api_response.ok():
            response = api_response.content
            if response is not None and len(response) is not 0:
                if 'openconfig-platform:component' in response:
                    show_ver_comp = response['openconfig-platform:component']
                    show_ver_compo = show_ver_comp[0]
                    if 'openconfig-platform-ext:software' in show_ver_compo:
                        responseContent = show_ver_compo['openconfig-platform-ext:software']
                    else:
                        return
                else:
                    return
            else:
                return
        else:
            return
        show_cli_output(sys.argv[3], responseContent)
    except Exception as e:
        log.syslog(log.LOG_ERR, str(e))
        print 'Error Transaction'

if __name__ == '__main__':

    func = sys.argv[1]
    run(func, sys.argv[2:])
