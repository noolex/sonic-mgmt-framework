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

import sys
import json
from datetime import datetime
from natsort import natsorted
from collections import OrderedDict
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
import cli_client as cc
import sonic_intf_utils as ifutils

aa = cc.ApiClient()

def getRangedPortNameList(name):
    if name is None:
        return []

    list = [name]
    if (not name.startswith('Eth')) or ('-' not in name):
        return list

    try:
        if name.startswith('Ethernet'):
            ids = name[8:].split('-')
            if len(ids) >= 2:
                start = int(ids[0], 10)
                stop = int(ids[1], 10) + 1
                list = []
                for id in range(start, stop, 1):
                    list.append("Ethernet{0}".format(id))
        elif name.startswith('Eth'):
            ids = name[3:].split('-')
            if len(ids) >= 2:
                prefix = ids[0][0:ids[0].rindex('/') + 1]
                start = int(ids[0][len(prefix):], 10)
                stop = int(ids[1][len(prefix):], 10) + 1
                list = []
                for id in range(start, stop, 1):
                    list.append("Eth{0}{1}".format(prefix, id))
    except:
        list = [name]

    return list

def getPortList(if_name = None):
    list = []
    path = cc.Path("/restconf/data/sonic-port:sonic-port/PORT/PORT_LIST")
    resp = aa.get(path, None, False)
    if resp.ok() and (resp.content is not None) and ('sonic-port:PORT_LIST' in resp.content):
        filter = getRangedPortNameList(if_name)
        for port in resp.content['sonic-port:PORT_LIST']:
            name = port.get('ifname')
            if (name is None) or (not name.startswith('Eth')):
                continue
            if len(filter) > 0:
                if name in filter:
                    list.append(name)
            else:
                list.append(name)
    return list

def getXcvrDomURI(intf):
    uri = "/restconf/data/openconfig-platform-diagnostics:transceiver-dom/transceiver-dom-info"
    if intf is not None and len(intf) > 0:
        uri += "={0}/state".format(intf.replace("/", "%2F"))
    return uri

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

    path = None
    last = len(args)
    tmpl = None
    if_name = None
    if_list = []
    xd_dict = OrderedDict()

    for idx in range(0, last):
        # pull out the interface name
        if (if_name is None) and args[idx].startswith("Eth"):
            if_name = args[idx]
            continue
        func += "-"
        func += args[idx]

    #print ("### file='{0}'".format(__file__))
    #print ("### func='{0}'".format(func))

    if_list = getPortList(if_name)
    #print("### if_list='{0}'".format(if_list))
    if len(if_list) < 1:
        return

    # Initialize the cable-diag list
    for intf in natsorted(if_list):
        xd_dict[intf] = {}

    if func.startswith('show-'):
        if len(if_list) == 1:
            path = cc.Path(getXcvrDomURI(if_list[0]))
        else:
            path = cc.Path(getXcvrDomURI(None))

        resp = aa.get(path)
        data = []
        if resp.ok() and resp.content is not None:
            if len(if_list) == 1:
                info = resp.content['openconfig-platform-diagnostics:state']
                xd_dict[if_list[0]].update(info)
            else:
                for info in resp.content['openconfig-platform-diagnostics:transceiver-dom-info']:
                    if ('ifname' not in info) or ('state' not in info):
                        continue
                    if info['ifname'] not in if_list:
                        continue
                    if not info['ifname'].startswith('Eth'):
                        continue
                    xd_dict[info['ifname']].update(info['state'])

        if func.find("summary") >= 0:
            tmpl = "show_interface_xcvr_dom_summary.j2"
        else:
            tmpl = "show_interface_xcvr_dom.j2"
        show_cli_output(tmpl, xd_dict)

    return

if __name__ == '__main__':
    pipestr().write(sys.argv)
    # pdb.set_trace()
    run(sys.argv[1], sys.argv[2:])
