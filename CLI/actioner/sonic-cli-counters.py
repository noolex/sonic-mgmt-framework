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
import time
import json
import ast
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
import readline

def prompt(msg):
    prompt_msg = msg + " [confirm y/N]: "
    x = raw_input(prompt_msg)
    while x.lower() != "y" and  x.lower() != "n":
        print ("Invalid input, expected [y/N]")
        x = raw_input(prompt_msg)
    if x.lower() == "n":
        return False 
    else:
        return True

def invoke(func, args):
    body = None
    clearit = False
    aa = cc.ApiClient()
    if func == 'rpc_interfaces_clear_counters':
        if args[0] == "all":
            clearit = prompt("Clear all Interface counters")
        elif args[0] == "PortChannel":
            clearit = prompt("Clear all PortChannel interface counters")
        elif args[0] == "Eth" or args[0] == "Ethernet":
            args[0] = "Ethernet"
            clearit = prompt("Clear all Ethernet interface counters")
        else:
            clearit = prompt("Clear counters for " + args[0])

        if clearit == True:
            keypath = cc.Path('/restconf/operations/openconfig-interfaces-ext:clear-counters')
            body = {"openconfig-interfaces-ext:input":{"interface-param":args[0]}}
            return aa.post(keypath, body)

    return None

def run(func, args):
    try:
        api_response = invoke(func,args)
        if api_response is not None:
            status = api_response.content["openconfig-interfaces-ext:output"]
            if status["status"] != 0:
                print status["status-detail"]
    except:
        print "%Error: Transaction Failure"
    return


if __name__ == '__main__':
    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])


