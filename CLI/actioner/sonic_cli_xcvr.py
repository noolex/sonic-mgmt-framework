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
import json
from natsort import natsorted
from collections import OrderedDict
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
import cli_client as cc
import sonic_intf_utils as ifutils

def run(func, args):

    # omit pipe arguments
    if '\\|' in args:
        args = args[:args.index('\\|')]
    if '|' in args:
        args = args[:args.index('|')]
    # a workaround for 'do' command
    if func == "do":
        func = args[0]
        args = args[1:]

    uri_oc_plat = "/restconf/data/openconfig-platform:components"

    aa = cc.ApiClient()
    path = None
    template = None
    last = len(args)
    if_name = None
    xcvr_tmp = OrderedDict()
    xcvrInfo = OrderedDict()

    for idx in range(0, last):
        # pull out the interface name
        if args[idx].startswith("Eth"):
            if_name = args[idx]
            if idx < last - 1:
                if_name += args[idx + 1]
            break
        func += "-"
        func += args[idx]

    #print ("func={0}".format(func))
    #print ("if_name='{0}'".format(if_name))

    if if_name is None:
        path = cc.Path(uri_oc_plat)
        resp = aa.get(path)
        key1 = 'openconfig-platform:components'
        key2 = 'component'
        if resp.ok() and (resp.content is not None) and (key1 in resp.content) and (key2 in resp.content[key1]):
            for row in resp.content[key1][key2]:
                name = row.get('name')
                if (name is None) or (not name.startswith('Eth')):
                    continue
                xcvr_tmp[name] = row
    else:
        path = cc.Path("{0}/component={1}".format(uri_oc_plat, if_name.replace('/', '%2F')))
        resp = aa.get(path)
        key = 'openconfig-platform:component'
        if resp.ok() and (resp.content is not None) and (key in resp.content):
            # The 1st row is our only interest
            for row in resp.content[key]:
                xcvr_tmp[if_name] = row
                break

    for intf in natsorted(xcvr_tmp.keys()):
        xcvrInfo[intf] = xcvr_tmp[intf]

    #print("DEBUG: {0}".format(json.dumps(xcvrInfo, indent=4)))

    if func.startswith('show-'):
        if func == "show-interface-transceiver-diagnostics-loopback-capability":
            template = "show_xcvr_loopback_capability.j2"
        elif func == "show-interface-transceiver-params":
            template = "show_xcvr_oper_params.j2"
        elif func == "show-interface-transceiver-diagnostics-loopback-controls":
            template = "show_xcvr_loopback_ctrl.j2"

        # print "---->", template
        show_cli_output(template, xcvrInfo)
    else:
        # if not a 'show' command, then this is a config command
        if func.startswith('no-'):
            on = 'False'
        else:
            on = 'True'

        for nm in natsorted(xcvrInfo.keys()):
            if 'media-side-input' in func:
                keypath = cc.Path('/restconf/data/openconfig-platform:components/component={name}/openconfig-platform-transceiver:transceiver/config/openconfig-platform-ext:lb-media-side-input-enable', name=nm)
                body = { "openconfig-platform-ext:lb-media-side-input-enable":  (on) }
                # print("keypath = {}".format(keypath))
                # print("body = {}".format(body))
                return aa.patch(keypath, body)

            if 'host-side-input' in func:
                keypath = cc.Path('/restconf/data/openconfig-platform:components/component={name}/openconfig-platform-transceiver:transceiver/config/openconfig-platform-ext:lb-host-side-input-enable', name=nm)
                body = { "openconfig-platform-ext:lb-host-side-input-enable":  (on) }
                # print("keypath = {}".format(keypath))
                # print("body = {}".format(body))
                return aa.patch(keypath, body)

            # print("Unsupported diagnostic loopback")
            # print " "
    return

if __name__ == '__main__':
    pipestr().write(sys.argv)
    # pdb.set_trace()
    run(sys.argv[1], sys.argv[2:])
