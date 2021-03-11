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

def get_sonic_inmemory_logging(args):
    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/operations/openconfig-system-ext:show-sys-in-memory-log')
    if len(args) >= 2:
        body = { "openconfig-system-ext:input":{"num-lines": int(args[1])}}
    else:
        body = { "openconfig-system-ext:input":{"num-lines": 0}}
    templ=args[0]
    api_response = aa.post(keypath, body)

    try:
        if api_response.ok():
           response = api_response.content
           if response is not None and 'openconfig-system-ext:output' in response:
                show_cli_output(templ, response)
    except Exception as e:
        raise e

def get_openconfig_system_inmemory_logging_count(args):
    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/operations/openconfig-system-ext:sys-in-memory-log-count')
    body = None
    templ=args[0]
    api_response = aa.post(keypath, body)

    try:
        if api_response.ok():
           response = api_response.content
           if response is not None and 'openconfig-system-ext:output' in response:
              show_cli_output(templ, response['openconfig-system-ext:output']['result'])
    except Exception as e:
        raise e


def run(func, args):
    if func == 'get_openconfig_system_in_memory_logging':
        get_sonic_inmemory_logging(args)
        return 0

    if func == 'get_openconfig_system_in_memory_logging_count':
        get_openconfig_system_inmemory_logging_count(args)
        return 0
    return 0

if __name__ == '__main__':
    import sys
    from rpipe_utils import pipestr

    pipestr().write(sys.argv)
    func = sys.argv[1]
    if func == 'get_openconfig_system_in_memory_logging':
        get_sonic_inmemory_logging(sys.argv[2:])
    elif func == 'get_openconfig_system_in_memory_logging_count':
        get_openconfig_system_inmemory_logging_count(sys.argv[2:])
    else:
        run(func, sys.argv[2:])

