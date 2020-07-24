#!/usr/bin/python
###########################################################################
#
# Copyright 2020 Broadcom. The term Broadcom refers to Broadcom Inc. and/or
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
# modeled after sonic-cli-pfm.py

import sys
from collections import OrderedDict
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
import cli_client as cc
import sonic_intf_utils as ifutils

def run(func, args):

    api = cc.ApiClient()

    path = None
    template = None
    last = len(args)
    if_list = []
    if_name = ' '

    dom_dict = OrderedDict()
    dom_loopback_support_keys = ['lb-host-side-input-support', 'lb-host-side-output-support',
                                 'lb-media-side-input-support', 'lb-media-side-output-support',
                                 'lb-per-lane-host-side-support', 'lb-per-lane-media-side-support',
                                 'lb-simul-host-media-side-support']
    dom_loopback_status_keys = ['lb-host-side-input', 'lb-host-side-output',
                                'lb-media-side-input', 'lb-media-side-output',
                                'lb-per-lane-host-side', 'lb-per-lane-media-side',
                                'lb-simul-host-media-side']
    dom_parameter_keys = ['lol-lane-1', 'lol-lane-2', 'lol-lane-3', 'lol-lane-4',
                          'lol-lane-5', 'lol-lane-6', 'lol-lane-7', 'lol-lane-8',
                          'los-lane-1', 'los-lane-2', 'los-lane-3', 'los-lane-4',
                          'los-lane-5', 'los-lane-6', 'los-lane-7', 'los-lane-8',
                          'tx-bias-lane-1', 'tx-bias-lane-2', 'tx-bias-lane-3', 'tx-bias-lane-4',
                          'tx-bias-lane-5', 'tx-bias-lane-6', 'tx-bias-lane-7', 'tx-bias-lane-8',
                          'rx-power-lane-1', 'rx-power-lane-2', 'rx-power-lane-3', 'rx-power-lane-4',
                          'rx-power-lane-5', 'rx-power-lane-6', 'rx-power-lane-7', 'rx-power-lane-8',
                          'tx-power-lane-1', 'tx-power-lane-2', 'tx-power-lane-3', 'tx-power-lane-4',
                          'tx-power-lane-5', 'tx-power-lane-6', 'tx-power-lane-7', 'tx-power-lane-8',
                          'voltage', 'temperature']

    xcvrInfo = OrderedDict()

    aa = cc.ApiClient()

    for idx in range(0, last):
        # pull out the interface name
        if  "Ethernet" in args[idx]:
            if_name = args[idx]
            # print (if_name)
            break
        func += "-"
        func += args[idx]

    # print (func)

    # If interface name is blank, get a list of all ports
    if if_name == ' ':
        path = cc.Path('/restconf/data/sonic-port:sonic-port/PORT/PORT_LIST')
        response = aa.get(path)
        if not response.ok():
            # print "all interfaces path is not good", response.content
            return
        try:
            for d in response.content['sonic-port:PORT_LIST']:
                if_list.append(d['ifname'])
        except:
            return
    else:
        # Single Interface
        if_list.append(if_name)



    if func == "show-interface-transceiver-diagnostics-loopback-capability":
        # Get loopback capability
        template = "show_xcvr_loopback_capability.j2"
        # print "---->", template
    elif func == "show-interface-transceiver-diagnostics-params":
        template = "show_xcvr_oper_params.j2"
        # print "---->", template
    elif func == "show-interface-transceiver-diagnostics-loopback-controls":
        template = "show_xcvr_oper_params.j2"
        # print "---->", template
    else:
        # if not a 'show' command, then this is a config command
        if 'enable' in func:
            on = 'True'
        else:
            on = 'False'

        for nm in if_list:
            if '/' in nm:
                nm = nm.replace('/', '%2F')

            if 'media-side-input' in func:
                keypath = cc.Path('/restconf/data/openconfig-platform:components/component={name}/openconfig-platform-transceiver:transceiver/config/openconfig-platform-ext:lb-media-side-input-enable', name=nm)
                body = { "openconfig-platform-ext:lb-media-side-input-enable":  (on) }
                print("keypath = {}".format(keypath))
                print("body = {}".format(body))
                return api.patch(keypath, body)

            if 'host-side-input' in func:
                keypath = cc.Path('/restconf/data/openconfig-platform:components/component={name}/openconfig-platform-transceiver:transceiver/config/openconfig-platform-ext:lb-host-side-input-enable', name=nm)
                body = { "openconfig-platform-ext:lb-host-side-input-enable":  (on) }
                print("keypath = {}".format(keypath))
                print("body = {}".format(body))
                return api.patch(keypath, body)

            print("Unsupported diagnostic loopback")
            print " "
        return


    for nm in if_list:
        if '/' in nm:
            nm = nm.replace('/', '%2F')
        path = cc.Path('/restconf/data/openconfig-platform:components/component=' + nm)
        response = aa.get(path)
        try:
            xcvrInfo[nm] = response.content['openconfig-platform:component'][0]
            # print response.content
        except:
            xcvrInfo[nm] = {}
    # Clean up the data
    cli_dict = OrderedDict()
    for val in sorted(xcvrInfo.keys(), key=lambda x: ifutils.name_to_int_val(x)):
        d2 = OrderedDict()
        try:
            d = xcvrInfo[val]['openconfig-platform-transceiver:transceiver']['state']
            # print "---> d unformatted == "
            # print d
            for k  in d:
                # print("processing {}".format(k))
                if ':' in k:
                    a = k.split(':')[1]
                    # print("key is {}".format(a))
                    if a in dom_loopback_support_keys and func == "show-interface-transceiver-diagnostics-loopback-capability": 
                        value = d[k]
                        # print "   k[1] = {}".format(type(k[1]))
                        # print "value of key {} = {}".format(a,value)
                        dom_dict[a]=value
                    elif a in dom_parameter_keys and func == "show-interface-transceiver-diagnostics-params":
                        value = d[k]
                        # print "   k[1] = {}".format(type(k[1]))
                        # print "value of key {} = {}".format(a,value)
                        dom_dict[a]=value
                    elif a in dom_loopback_status_keys and func == "show-interface-transceiver-diagnostics-loopback-controls":
                        value = d[k]
                        # print "   k[1] = {}".format(type(k[1]))
                        # print "value of key {} = {}".format(a,value)
                        dom_dict[a]=value
                    else:
                        # print("---->key will not be used<----")
                        continue
                else:
                    continue
        except:
            continue

        cli_dict[val] = (val, dom_dict)
    try:
        # print cli_dict
        for k in cli_dict:
            show_cli_output(template, (True, cli_dict[k]))
    except Exception as e:
        pass
    return
    
if __name__ == '__main__':
    pipestr().write(sys.argv)
    # pdb.set_trace()
    run(sys.argv[1], sys.argv[2:])
