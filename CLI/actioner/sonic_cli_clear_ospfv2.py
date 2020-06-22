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

def clear_ospf_api(args):
   api = cc.ApiClient()
   keypath = []
   body = None
   vrfname = ""
   ifname = ""

   #print("clear_ospf_api: args {}".format(args))
   if len(args) >= 1 :
      _, ifname = args[0].split("=")

   if len(args) >= 2 :
      _, vrfname = args[1].split("=")
   
   keypath = cc.Path('/restconf/operations/sonic-ospfv2-clear:clear-ospfv2')

   if vrfname != "" :
       if ifname != "" :
           body = {"sonic-ospfv2-clear:input": { "vrf-name" : vrfname, "interface" : ifname } }
       else :
           body = {"sonic-ospfv2-clear:input": { "vrf-name" : vrfname, "interface-all" : True } }
   else :
       if ifname != "" :
           body = {"sonic-ospfv2-clear:input": { "interface" : ifname } }
       else :
           body = {"sonic-ospfv2-clear:input": { "interface-all" : True } }

   return api.post(keypath, body)


def run(func, args):
    #print("Run clear_ospf_api args {}".format(args))
    if func == 'clear_ospfv2':
        response = clear_ospf_api(args)
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
