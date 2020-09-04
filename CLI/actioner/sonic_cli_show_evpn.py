#!/usr/bin/python
###########################################################################
#
# Copyright 2019 Broadcom, Inc.
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
import os

def run(func, args):
    full_cmd = os.getenv('USER_COMMAND', None).split('|')[0]
    if func == "get_evpn":
        keypath = cc.Path('/restconf/operations/sonic-bgp-show:show-bgp-evpn')
        body = {"sonic-bgp-show:input": { "cmd":full_cmd }}
        response = cc.ApiClient().post(keypath, body, response_type='string')
        if not response:
            print "No response"
            return 1
        if response.ok():
            if response.content is not None:
                content = response.content
                content = content[39:-3].replace('\u003e', '>')
                show_cli_output("dump.j2", content)
        else:
            print response.error_message()
            return 1
        return
