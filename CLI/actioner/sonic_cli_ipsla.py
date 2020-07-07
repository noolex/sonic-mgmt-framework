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

    # IP SLA show
    if func == 'get_ipsla':
        if len(args) == 1:
            keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas')
            return aa.get(keypath)
        elif len(args) == 2 and args[1] == 'x':
            keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={id}', id=args[0])
            return aa.get(keypath)
        else:
            keypath = cc.Path('/restconf/operations/sonic-ip-sla:get-ipsla-history')
            body = {"sonic-ip-sla:input": {"ip_sla_id": args[0]}}
            return aa.post(keypath, body)


    # IP SLA delete
    if func == 'del_ipsla' :
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config', slaid=args[0])
        return aa.delete(keypath)

    # IP SLA set
    if func == 'post_ipsla' :

        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config', slaid=args[0])

        body=collections.defaultdict(dict)
        body = {"openconfig-ip-sla:config": {"ip-sla-id": int(args[0])}}
        return aa.patch(keypath, body)

    # IP SLA frequency delete
    if func == 'del_freq' :
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/frequency', slaid=args[0])
        return aa.delete(keypath)

    # IP SLA frequency set
    if func == 'patch_freq' :

        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config', slaid=args[0])

        body=collections.defaultdict(dict)
        body = {"openconfig-ip-sla:config": {"frequency": int(args[1])}}
        return aa.patch(keypath, body)


    # IP SLA threshold delete
    if func == 'del_threshold' :
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/threshold', slaid=args[0])
        return aa.delete(keypath)

    # IP SLA threshold set
    if func == 'patch_threshold' :

        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config', slaid=args[0])

        body=collections.defaultdict(dict)
        body = {"openconfig-ip-sla:config": {"threshold": int(args[1])}}
        return aa.patch(keypath, body)

    # IP SLA timeout delete
    if func == 'del_timeout' :
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/timeout', slaid=args[0])
        return aa.delete(keypath)

    # IP SLA timeout set
    if func == 'patch_timeout' :

        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config', slaid=args[0])

        body=collections.defaultdict(dict)
        body = {"openconfig-ip-sla:config": {"timeout": int(args[1])}}
        return aa.patch(keypath, body)

    # IP SLA icmp-echo delete
    if func == 'del_icmp' :
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/icmp-source-ip', slaid=args[0])
        aa.delete(keypath)
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/icmp-source-interface', slaid=args[0])
        aa.delete(keypath)
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/icmp-size', slaid=args[0])
        aa.delete(keypath)
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/icmp-vrf', slaid=args[0])
        aa.delete(keypath)
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/icmp-ttl', slaid=args[0])
        aa.delete(keypath)
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/icmp-tos', slaid=args[0])
        aa.delete(keypath)
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/icmp-dst-ip', slaid=args[0])
        return aa.delete(keypath)

    # IP SLA icmp-echo set
    if func == 'patch_icmp' :

        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config', slaid=args[0])

        body=collections.defaultdict(dict)
        if len(args) == 2:
            body = {"openconfig-ip-sla:config": {"icmp-dst-ip":args[1]}}
        else:
            body = {"openconfig-ip-sla:config": {"icmp-dst-ip":args[1],"icmp-vrf":args[2]}}
        return aa.patch(keypath, body)

    # IP SLA tcp-connect delete
    if func == 'del_tcp' :
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/tcp-source-ip', slaid=args[0])
        aa.delete(keypath)
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/tcp-source-interface', slaid=args[0])
        aa.delete(keypath)
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/tcp-source-port', slaid=args[0])
        aa.delete(keypath)
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/tcp-dst-port', slaid=args[0])
        aa.delete(keypath)
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/tcp-vrf', slaid=args[0])
        aa.delete(keypath)
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/tcp-ttl', slaid=args[0])
        aa.delete(keypath)
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/tcp-tos', slaid=args[0])
        aa.delete(keypath)
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/tcp-dst-ip', slaid=args[0])
        return aa.delete(keypath)

    # IP SLA tcp-connect set
    if func == 'patch_tcp' :

        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config', slaid=args[0])

        body=collections.defaultdict(dict)
        if len(args) == 3:
            body = {"openconfig-ip-sla:config": {"tcp-dst-ip":args[1],"tcp-dst-port":args[2]}}
        else:
            body = {"openconfig-ip-sla:config": {"tcp-dst-ip":args[1],"tcp-dst-port":args[2],"tcp-vrf":args[3]}}
        return aa.patch(keypath, body)

    # IP SLA icmp-echo source-ip delete
    if func == 'del_icmp_src_ip' :
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/icmp-source-ip', slaid=args[0])
        return aa.delete(keypath)

    # IP SLA icmp-echo source-ip set
    if func == 'patch_icmp_src_ip' :

        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config', slaid=args[0])

        body=collections.defaultdict(dict)
        body = {"openconfig-ip-sla:config": {"icmp-source-ip":args[1]}}
        return aa.patch(keypath, body)

    # IP SLA icmp-echo source-if delete
    if func == 'del_icmp_src_if' :
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/icmp-source-interface', slaid=args[0])
        return aa.delete(keypath)

    # IP SLA icmp-echo source-if set
    if func == 'patch_icmp_src_if' :

        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config', slaid=args[0])

        body=collections.defaultdict(dict)
        body = {"openconfig-ip-sla:config": {"icmp-source-interface":args[1]}}
        return aa.patch(keypath, body)

    # IP SLA icmp-echo data-size delete
    if func == 'del_icmp_data_size' :
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/icmp-size', slaid=args[0])
        return aa.delete(keypath)

    # IP SLA icmp-echo data-size set
    if func == 'patch_icmp_data_size' :

        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config', slaid=args[0])

        body=collections.defaultdict(dict)
        body = {"openconfig-ip-sla:config": {"icmp-size": int(args[1])}}
        return aa.patch(keypath, body)

    # IP SLA icmp-echo vrf delete
    if func == 'del_icmp_vrf' :
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/icmp-vrf', slaid=args[0])
        return aa.delete(keypath)

    # IP SLA icmp-echo vrf set
    if func == 'patch_icmp_vrf' :

        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config', slaid=args[0])

        body=collections.defaultdict(dict)
        body = {"openconfig-ip-sla:config": {"icmp-vrf":args[1]}}
        return aa.patch(keypath, body)

    # IP SLA icmp-echo ttl delete
    if func == 'del_icmp_ttl' :
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/icmp-ttl', slaid=args[0])
        return aa.delete(keypath)

    # IP SLA icmp-echo ttl set
    if func == 'patch_icmp_ttl' :

        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config', slaid=args[0])

        body=collections.defaultdict(dict)
        body = {"openconfig-ip-sla:config": {"icmp-ttl": int(args[1])}}
        return aa.patch(keypath, body)

    # IP SLA icmp-echo tos delete
    if func == 'del_icmp_tos' :
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/icmp-tos', slaid=args[0])
        return aa.delete(keypath)

    # IP SLA icmp-echo tos set
    if func == 'patch_icmp_tos' :

        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config', slaid=args[0])

        body=collections.defaultdict(dict)
        body = {"openconfig-ip-sla:config": {"icmp-tos": int(args[1])}}
        return aa.patch(keypath, body)



    # IP SLA tcp-connect source-ip delete
    if func == 'del_tcp_src_ip' :
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/tcp-source-ip', slaid=args[0])
        return aa.delete(keypath)

    # IP SLA tcp-connect source-ip set
    if func == 'patch_tcp_src_ip' :

        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config', slaid=args[0])

        body=collections.defaultdict(dict)
        body = {"openconfig-ip-sla:config": {"tcp-source-ip":args[1]}}
        return aa.patch(keypath, body)

    # IP SLA tcp-connect source-if delete
    if func == 'del_tcp_src_if' :
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/tcp-source-interface', slaid=args[0])
        return aa.delete(keypath)

    # IP SLA tcp-connect source-if set
    if func == 'patch_tcp_src_if' :

        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config', slaid=args[0])

        body=collections.defaultdict(dict)
        body = {"openconfig-ip-sla:config": {"tcp-source-interface":args[1]}}
        return aa.patch(keypath, body)

    # IP SLA tcp-connect vrf delete
    if func == 'del_tcp_vrf' :
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/tcp-vrf', slaid=args[0])
        return aa.delete(keypath)

    # IP SLA tcp-connect vrf set
    if func == 'patch_tcp_vrf' :

        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config', slaid=args[0])

        body=collections.defaultdict(dict)
        body = {"openconfig-ip-sla:config": {"tcp-vrf":args[1]}}
        return aa.patch(keypath, body)

    # IP SLA tcp-connect tos delete
    if func == 'del_tcp_tos' :
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/tcp-tos', slaid=args[0])
        return aa.delete(keypath)

    # IP SLA tcp-connect tos set
    if func == 'patch_tcp_tos' :

        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config', slaid=args[0])

        body=collections.defaultdict(dict)
        body = {"openconfig-ip-sla:config": {"tcp-tos": int(args[1])}}
        return aa.patch(keypath, body)

    # IP SLA tcp-connect ttl delete
    if func == 'del_tcp_ttl' :
        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config/tcp-ttl', slaid=args[0])
        return aa.delete(keypath)

    # IP SLA tcp-connect ttl set
    if func == 'patch_tcp_ttl' :

        keypath = cc.Path('/restconf/data/openconfig-ip-sla:ip-slas/ip-sla={slaid}/config', slaid=args[0])

        body=collections.defaultdict(dict)
        body = {"openconfig-ip-sla:config": {"tcp-ttl": int(args[1])}}
        return aa.patch(keypath, body)

    else:
        print("%Error: not implemented")
        exit(1)


def run(func, args):
    try:
        api_response = invoke(func, args)

        if api_response.ok():
            response = api_response.content
            print(response)
            if response is None:
                pass
            elif 'openconfig-ip-sla:ip-sla' in response.keys():
                print("**single entity**")
                show_cli_output("show_ipsla.j2", response)
                return
            elif 'openconfig-ip-sla:ip-slas' in response.keys():
                print("**summary**")
                show_cli_output("show_ipsla_summary.j2", response)
                return
            else:
                print("**history**")
                show_cli_output("show_ipsla_summary.j2", response)
        else:
            print(api_response.error_message())
            return 1

    except:
            # system/network error
            raise


if __name__ == '__main__':
    pipestr().write(sys.argv)
    #pdb.set_trace()
    run(sys.argv[1], sys.argv[2:])
