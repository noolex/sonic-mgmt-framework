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
import cli_client as cc
from rpipe_utils import pipestr

def clear_bfd_api(args):
    api = cc.ApiClient()
    keypath = []
    body = None
    remoteaddress = ""
    localaddress = ""
    vrfname = ""
    ifname = ""
    mhop = ""
    i = 5
    for arg in args[5:]:
        if "vrf" == arg:
           vrfname = args[i+1]
        elif "peer" == arg:
           remoteaddress = args[i+1]
        elif "interface" == arg:
           ifname = args[i+1]
        elif "multihop" == arg:
            mhop = "multihop"
        elif "local-address" == arg:
           localaddress = args[i+1]
        else:
           pass
        i = i + 1
    keypath = cc.Path('/restconf/operations/sonic-bfd-clear:clear-bfd')
    body = {"sonic-bfd-clear:input": { "remote-address": remoteaddress, "vrf": vrfname, "interface": ifname, "local-address": localaddress, "multihop": mhop}}
    return api.post(keypath, body)

def run(func, args):
    if func == 'clear_bfd':
        response = clear_bfd_api(args)
        if response.ok():
            if response.content is not None:
                # Get Command Output
                api_response = response.content
                if api_response is None:
                    print("Failed")
                    sys.exit(1)
        else:
            print response.error_message()
            sys.exit(1)
    else:
       return

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])
