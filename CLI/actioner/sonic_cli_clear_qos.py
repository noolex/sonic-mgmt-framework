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

def clear_qos_api(args):
   api = cc.ApiClient()
   keypath = []
   body = None
   countertype = "queue"
   counteroptions = ""
   exact_intf = False
   exact = False
   ifname = ""
   queue = ""
   pg = ""
   queuetype = "both"
   pgcountertype = "both"
   persistent = ""
   watermark = ""
   buffthresbreach = ""
   wred = ""
   i = 0
   for arg in args:
        if "priority-group" == arg:
           countertype = "priority-group"
        elif "counters" == arg:
           counteroptions = "counters"
        elif "watermark" == arg:
           counteroptions = "watermarks"
        elif "persistent-watermark" == arg:
           counteroptions = "watermarks"
           persistent = True
        elif "wred" == arg:
           wred = True
        elif "unicast" == arg:
           queuetype = arg
        elif "multicast" == arg:
           queuetype = arg
        elif "headroom" == arg:
           pgcountertype = arg
        elif "shared" == arg:
           pgcountertype = arg
        elif "interface" == arg:
           ifname = args[i+1] + args[i+2]
           exact_intf = True
        elif "queue" == arg:
           if i !=  1:
              queue = args[i+1]
              queue = ifname + ":" + queue
              exact = True
        elif "priority-group" == arg:
           if i !=  1:
              pg = args[i+1]
              pg = ifname + ":" + pg
              exact = True
        else:
           pass
        i = i + 1

   keypath = cc.Path('/restconf/operations/sonic-qos-clear:clear-qos')
   if countertype == "queue":
      if counteroptions == "counters":
         if exact == True:
            body = {"sonic-qos-clear:input": { "counter-type": countertype, "counters": { "queue": queue }}}
         elif exact_intf == True:
            body = {"sonic-qos-clear:input": { "counter-type": countertype, "counters": { "interface": ifname}}}
         else:
            body = {"sonic-qos-clear:input": { "counter-type": countertype, "counters": { "all": True}}}
      elif counteroptions == "watermarks":
         if exact == True:
            body = {"sonic-qos-clear:input": { "counter-type": countertype, "watermarks": { "persistent": persistent, "queue-type": queuetype, "queue": queue}}}
         elif exact_intf == True:
            body = {"sonic-qos-clear:input": { "counter-type": countertype, "watermarks": { "persistent": persistent, "queue-type": queuetype, "interface": ifname}}}
         else:
            body = {"sonic-qos-clear:input": { "counter-type": countertype, "watermarks": { "persistent": persistent, "queue-type": queuetype,  "all": True}}}
   elif countertype == "priority-group":
      if counteroptions == "counters":
         if exact == True:
            body = {"sonic-qos-clear:input": { "counter-type": countertype, "counters": { "priority-group": pg }}}
         elif exact_intf == True:
            body = {"sonic-qos-clear:input": { "counter-type": countertype, "counters": { "interface": ifname}}}
         else:
            body = {"sonic-qos-clear:input": { "counter-type": countertype, "counters": { "all": True}}}
      elif counteroptions == "watermarks":
         if exact == True:
            body = {"sonic-qos-clear:input": { "counter-type": countertype, "watermarks": { "persistent": persistent, "pg-type": pgcountertype, "priority-group": pg}}}
         elif exact_intf == True:
            body = {"sonic-qos-clear:input": { "counter-type": countertype, "watermarks": { "persistent": persistent, "pg-type": pgcountertype, "interface": ifname}}}
         else:
            body = {"sonic-qos-clear:input": { "counter-type": countertype, "watermarks": { "persistent": persistent, "pg-type": pgcountertype, "all": True}}}
   else:
       pass
   return api.post(keypath, body)

def run(func, args):
    if func == 'clear_qos':
        response = clear_qos_api(args)
        if response.ok():
            if response.content is not None:
                # Get Command Output
                api_response = response.content
                if api_response is None:
                    print("%Error: Clear failed")
                    sys.exit(1)
                else:
                    output = api_response["sonic-qos-clear:output"]
                    if output["response"] != "Success: Cleared Counters":
                       print output["response"]
        else:
            print response.error_message()
            sys.exit(1)
    else:
       return

if __name__ == '__main__':

#    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])
