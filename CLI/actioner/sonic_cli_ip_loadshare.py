#!/usr/bin/python
###########################################################################
#
# Copyright 2019 BRCM, Inc.
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
import collections
import re
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
import ast
import subprocess


def invoke(func, args):
    body = None
    aa = cc.ApiClient()

    # nothing
    if func == '':
        keypath = cc.Path('')
        return aa.get(keypath)

    if func == 'patch_loadshare_ipv4_config':
        keypath = cc.Path('/restconf/data/openconfig-loadshare-mode-ext:ipv4-attrs')        
        if args[0] == 'ipv4-l4-src-port':
            body = {"openconfig-loadshare-mode-ext:ipv4-attrs": {"config": {"ipv4": "ipv4", "ipv4-l4-src-port": True}}}
        elif args[0] == 'ipv4-l4-dst-port':
            body = {"openconfig-loadshare-mode-ext:ipv4-attrs": {"config": {"ipv4": "ipv4", "ipv4-l4-dst-port": True}}}
        elif args[0] == 'ipv4-src-ip':
            body = {"openconfig-loadshare-mode-ext:ipv4-attrs": {"config": {"ipv4": "ipv4", "ipv4-src-ip": True}}}
        elif args[0] == 'ipv4-dst-ip':
            body = {"openconfig-loadshare-mode-ext:ipv4-attrs": {"config": {"ipv4": "ipv4", "ipv4-dst-ip": True}}}
        elif args[0] == 'ipv4-ip-proto':
            body = {"openconfig-loadshare-mode-ext:ipv4-attrs": {"config": {"ipv4": "ipv4", "ipv4-ip-proto": True}}}
        return aa.patch(keypath, body)

    elif func == 'delete_loadshare_ipv4_config':
        keypath = cc.Path('/restconf/data/openconfig-loadshare-mode-ext:ipv4-attrs')        
        if args[0] == 'ipv4-l4-src-port':
            body = {"openconfig-loadshare-mode-ext:ipv4-attrs": {"config": {"ipv4": "ipv4", "ipv4-l4-src-port": False}}}
        elif args[0] == 'ipv4-l4-dst-port':
            body = {"openconfig-loadshare-mode-ext:ipv4-attrs": {"config": {"ipv4": "ipv4", "ipv4-l4-dst-port": False}}}
        elif args[0] == 'ipv4-src-ip':
            body = {"openconfig-loadshare-mode-ext:ipv4-attrs": {"config": {"ipv4": "ipv4", "ipv4-src-ip": False}}}
        elif args[0] == 'ipv4-dst-ip':
            body = {"openconfig-loadshare-mode-ext:ipv4-attrs": {"config": {"ipv4": "ipv4", "ipv4-dst-ip": False}}}
        elif args[0] == 'ipv4-ip-proto':
            body = {"openconfig-loadshare-mode-ext:ipv4-attrs": {"config": {"ipv4": "ipv4", "ipv4-ip-proto": False}}}
        return aa.patch(keypath, body)

    if func == 'patch_loadshare_ipv6_config':
        keypath = cc.Path('/restconf/data/openconfig-loadshare-mode-ext:ipv6-attrs')        
        if args[0] == 'ipv6-l4-src-port':
            body = {"openconfig-loadshare-mode-ext:ipv6-attrs": {"config": {"ipv6": "ipv6", "ipv6-l4-src-port": True}}}
        elif args[0] == 'ipv6-l4-dst-port':
            body = {"openconfig-loadshare-mode-ext:ipv6-attrs": {"config": {"ipv6": "ipv6", "ipv6-l4-dst-port": True}}}
        elif args[0] == 'ipv6-src-ip':
            body = {"openconfig-loadshare-mode-ext:ipv6-attrs": {"config": {"ipv6": "ipv6", "ipv6-src-ip": True}}}
        elif args[0] == 'ipv6-dst-ip':
            body = {"openconfig-loadshare-mode-ext:ipv6-attrs": {"config": {"ipv6": "ipv6", "ipv6-dst-ip": True}}}
        elif args[0] == 'ipv6-next-hdr':
            body = {"openconfig-loadshare-mode-ext:ipv6-attrs": {"config": {"ipv6": "ipv6", "ipv6-next-hdr": True}}}
        return aa.patch(keypath, body)

    elif func == 'delete_loadshare_ipv6_config':
        keypath = cc.Path('/restconf/data/openconfig-loadshare-mode-ext:ipv6-attrs')        
        if args[0] == 'ipv6-l4-src-port':
            body = {"openconfig-loadshare-mode-ext:ipv6-attrs": {"config": {"ipv6": "ipv6", "ipv6-l4-src-port": False}}}
        elif args[0] == 'ipv6-l4-dst-port':
            body = {"openconfig-loadshare-mode-ext:ipv6-attrs": {"config": {"ipv6": "ipv6", "ipv6-l4-dst-port": False}}}
        elif args[0] == 'ipv6-src-ip':
            body = {"openconfig-loadshare-mode-ext:ipv6-attrs": {"config": {"ipv6": "ipv6", "ipv6-src-ip": False}}}
        elif args[0] == 'ipv6-dst-ip':
            body = {"openconfig-loadshare-mode-ext:ipv6-attrs": {"config": {"ipv6": "ipv6", "ipv6-dst-ip": False}}}
        elif args[0] == 'ipv6-next-hdr':
            body = {"openconfig-loadshare-mode-ext:ipv6-attrs": {"config": {"ipv6": "ipv6", "ipv6-next-hdr": False}}}
        return aa.patch(keypath, body)

    if func == 'patch_loadshare_seed_config':
        keypath = cc.Path('/restconf/data/openconfig-loadshare-mode-ext:seed-attrs')        
        body = {"openconfig-loadshare-mode-ext:seed-attrs": {"config": {"hash": "hash", "ecmp-hash-seed": int(args[0])}}}
        return aa.patch(keypath, body)

    elif func == 'delete_loadshare_seed_config':
        keypath = cc.Path('/restconf/data/openconfig-loadshare-mode-ext:seed-attrs')        
        return aa.delete(keypath)

    if func == 'get_load_share':
        keypath = cc.Path('/restconf/data/openconfig-loadshare-mode-ext:seed-attrs/state')
        return aa.get(keypath)

def run(func, args):
    try:
        api_response = invoke(func, args)
        if api_response.ok():
            response = api_response.content
            if response is None:
                pass
            elif 'openconfig-loadshare-mode-ext:state' in response.keys():
                show_cli_output("show_ip_loadshare.j2", response)
                return

    except:
        # system/network error
        raise

if __name__ == '__main__':
    pipestr().write(sys.argv)
    #pdb.set_trace()
    run(sys.argv[1], sys.argv[2:])
