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
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output

def invoke(func, args):
    body = None
    aa = cc.ApiClient()
    if func == 'rpc_sonic_mgmt_interface_renew_dhcp_lease':
        keypath = cc.Path('/restconf/operations/sonic-mgmt-interface:renew_dhcp_lease')
        body = {"sonic-mgmt-interface:input":{"portname":args[0]}}
        return aa.post(keypath, body)
    else:
        return 

def run(func, args):
    try:
        api_response = invoke(func,args)
        status = api_response.content["sonic-mgmt-interface:output"]
        if status["status"] != 0:
            print status["status-detail"]
    except:
        print "%Error: Transaction Failure"
    return

if __name__ == '__main__':
    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])
