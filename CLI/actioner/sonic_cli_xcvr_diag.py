#!/usr/bin/python
###########################################################################
#
# Copyright 2021 Broadcom. The term Broadcom refers to Broadcom Inc. and/or
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

OC_PLAT = "/restconf/data/openconfig-platform:components/component"

def getXcvrDiagURI(intf):
    return "{0}={1}/openconfig-platform-transceiver:transceiver/openconfig-platform-transceiver-ext:diagnostics".format(OC_PLAT, intf)

def getLoopbackConfigURI(intf, attr):
    return "{0}={1}/openconfig-platform-transceiver:transceiver/openconfig-platform-transceiver-ext:diagnostics/loopbacks/config/{2}".format(OC_PLAT, intf, attr)

def getPatternConfigURI(intf, attr):
    return "{0}={1}/openconfig-platform-transceiver:transceiver/openconfig-platform-transceiver-ext:diagnostics/patterns/config/{2}".format(OC_PLAT, intf, attr)

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

    aa = cc.ApiClient()
    path = None
    template = None
    last = len(args)
    if_name = None
    if_list = []
    xcvr_tmp = OrderedDict()
    xcvrInfo = OrderedDict()

    for idx in range(0, last):
        # pull out the interface name
        if (if_name is None) and args[idx].startswith("Eth"):
            if_name = args[idx]
            continue
        func += "-"
        func += args[idx]

    #print ("func='{0}'".format(func))
    #print ("intf='{0}'".format(if_name))

    if if_name is not None:
        if_list.append(if_name)
    else:
        path = cc.Path(OC_PLAT)
        resp = aa.get(path)
        key = 'openconfig-platform:component'
        if resp.ok() and (resp.content is not None) and (key in resp.content):
            for row in resp.content[key]:
                name = row.get('name')
                if (name is None) or (not name.startswith('Eth')):
                    continue
                if (row.get('openconfig-platform-transceiver:transceiver') is None):
                    continue
                if_list.append(name)

    # Initialize the xcvrInfo
    for intf in natsorted(if_list):
        xcvrInfo[intf] = {}

    if func.startswith('show-'):

        for intf in natsorted(if_list):
            path = cc.Path(getXcvrDiagURI(intf))
            resp = aa.get(path)
            if resp.ok() and (resp.content is not None):
                for key in resp.content.keys():
                    xcvrInfo[intf].update(resp.content[key])

        #print("DEBUG: {0}".format(json.dumps(xcvrInfo, indent=4)))

        if func.find("show-interface-transceiver-diagnostics-capability") >= 0:
            template = "show_interface_xcvr_diag_capability.j2"
        elif func.find("show-interface-transceiver-diagnostics-status") >= 0:
            template = "show_interface_xcvr_diag_status.j2"
        show_cli_output(template, xcvrInfo)

    elif func.find('interface-transceiver-diagnostics-loopback') >= 0:

        for nm in natsorted(xcvrInfo.keys()):
            if 'media-side-input' in func:
                keypath = cc.Path(getLoopbackConfigURI(nm, 'lb-media-input-enabled'))
                if func.startswith('no-'):
                    body = { "openconfig-platform-transceiver-ext:lb-media-input-enabled": False }
                    aa.patch(keypath, body)
                else:
                    body = { "openconfig-platform-transceiver-ext:lb-media-input-enabled": True }
                    aa.patch(keypath, body)
            elif 'media-side-output' in func:
                keypath = cc.Path(getLoopbackConfigURI(nm, 'lb-media-output-enabled'))
                if func.startswith('no-'):
                    body = { "openconfig-platform-transceiver-ext:lb-media-output-enabled": False }
                    aa.patch(keypath, body)
                else:
                    body = { "openconfig-platform-transceiver-ext:lb-media-output-enabled": True }
                    aa.patch(keypath, body)
            elif 'host-side-input' in func:
                keypath = cc.Path(getLoopbackConfigURI(nm, 'lb-host-input-enabled'))
                if func.startswith('no-'):
                    body = { "openconfig-platform-transceiver-ext:lb-host-input-enabled": False }
                    aa.patch(keypath, body)
                else:
                    body = { "openconfig-platform-transceiver-ext:lb-host-input-enabled": True }
                    aa.patch(keypath, body)
            elif 'host-side-output' in func:
                keypath = cc.Path(getLoopbackConfigURI(nm, 'lb-host-output-enabled'))
                if func.startswith('no-'):
                    body = { "openconfig-platform-transceiver-ext:lb-host-output-enabled": False }
                    aa.patch(keypath, body)
                else:
                    body = { "openconfig-platform-transceiver-ext:lb-host-output-enabled": True }
                    aa.patch(keypath, body)
            else:
                print("Unknown diagnostic loopback control: {0}".format(func))

    elif func.find('interface-transceiver-diagnostics-pattern') >= 0:

        for nm in natsorted(xcvrInfo.keys()):
            if 'checker-host' in func:
                keypath = cc.Path(getPatternConfigURI(nm, 'pattern-chk-host-enabled'))
                if func.startswith('no-'):
                    body = { "openconfig-platform-transceiver-ext:pattern-chk-host-enabled": False }
                    aa.patch(keypath, body)
                else:
                    body = { "openconfig-platform-transceiver-ext:pattern-chk-host-enabled": True }
                    aa.patch(keypath, body)
            elif 'checker-media' in func:
                keypath = cc.Path(getPatternConfigURI(nm, 'pattern-chk-media-enabled'))
                if func.startswith('no-'):
                    body = { "openconfig-platform-transceiver-ext:pattern-chk-media-enabled": False }
                    aa.patch(keypath, body)
                else:
                    body = { "openconfig-platform-transceiver-ext:pattern-chk-media-enabled": True }
                    aa.patch(keypath, body)
            elif 'generator-host' in func:
                keypath = cc.Path(getPatternConfigURI(nm, 'pattern-gen-host-enabled'))
                if func.startswith('no-'):
                    body = { "openconfig-platform-transceiver-ext:pattern-gen-host-enabled": False }
                    aa.patch(keypath, body)
                else:
                    body = { "openconfig-platform-transceiver-ext:pattern-gen-host-enabled": True }
                    aa.patch(keypath, body)
            elif 'generator-media' in func:
                keypath = cc.Path(getPatternConfigURI(nm, 'pattern-gen-media-enabled'))
                if func.startswith('no-'):
                    body = { "openconfig-platform-transceiver-ext:pattern-gen-media-enabled": False }
                    aa.patch(keypath, body)
                else:
                    body = { "openconfig-platform-transceiver-ext:pattern-gen-media-enabled": True }
                    aa.patch(keypath, body)
            else:
                print("Unknown diagnostic pattern control: {0}".format(func))

    return

if __name__ == '__main__':
    pipestr().write(sys.argv)
    # pdb.set_trace()
    run(sys.argv[1], sys.argv[2:])
