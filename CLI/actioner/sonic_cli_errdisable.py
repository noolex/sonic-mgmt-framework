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

from scripts.render_cli import show_cli_output
import cli_client as cc
import sys
import re
from sonic_cli_if_range import eth_intf_range_expand

aa = cc.ApiClient()

def generic_set_response_handler(response, args):
    if not response.ok():
        print(response.error_message())


def generic_delete_response_handler(response, args):
    if response.ok():
        resp_content = response.content
        if resp_content is not None:
            print("%Error: {}".format(str(resp_content)))
    elif response.status_code != '404':
        print(response.error_message())


def generic_show_response_handler(output_data, args):
    j2_tmpl = args[0]
    show_cli_output(j2_tmpl, output_data)


def delete_openconfig_errdisable_cause(args):
    if args[0] not in ["udld", "bpduguard", "link-flap"]:
        print('%Error Invalid cause : {}'.format(args[0]))
        return None

    body = {}
    if args[0] == "udld":
        uri = cc.Path('/restconf/data/openconfig-errdisable-ext:errdisable/config/cause=UDLD')  
    elif args[0] == "bpduguard":
        uri = cc.Path('/restconf/data/openconfig-errdisable-ext:errdisable/config/cause=BPDUGUARD')
    elif args[0] == "link-flap":
        uri = cc.Path('/restconf/data/openconfig-errdisable-ext:errdisable/config/cause=LINK_FLAP')
    return aa.delete(uri, body)


def delete_openconfig_errdisable_interval(args):
    body = { "openconfig-errdisable-ext:interval": int(args[0])}
    uri = cc.Path('/restconf/data/openconfig-errdisable-ext:errdisable/config/interval')  
    return aa.delete(uri, body)

def delete_openconfig_errdisable_port(args):
    body = {}
    uri = cc.Path('/restconf/data/openconfig-errdisable-ext:errdisable-port/port={}/link-flap'.format(args[0]))
    return aa.delete(uri, body)

def delete_openconfig_errdisable_port_range(args):
    ifrange = args[0].split("=")[1]
    if ifrange.startswith("Eth"):
        ifrangelist = eth_intf_range_expand(ifrange)
    else:
        print('%Error: not supported on this interface type')
    body = {}
    for intf in ifrangelist:
        uri = cc.Path('/restconf/data/openconfig-errdisable-ext:errdisable-port/port={}/link-flap'.format(intf))
        ret = aa.delete(uri, body)
    return ret

def patch_openconfig_errdisable_cause(args):
    if args[0] not in ["udld", "bpduguard", "link-flap"]:
        print('%Error Invalid cause : {}'.format(args[0]))
        return None
    param = args[0].replace("-", "_")
    body = { "openconfig-errdisable-ext:cause": [param.upper()]}
    uri = cc.Path('/restconf/data/openconfig-errdisable-ext:errdisable/config/cause')  
    return aa.patch(uri, body)


def patch_openconfig_errdisable_interval(args):
    body = { "openconfig-errdisable-ext:interval": int(args[0])}
    uri = cc.Path('/restconf/data/openconfig-errdisable-ext:errdisable/config/interval')  
    return aa.patch(uri, body)

def patch_openconfig_errdisable_port(args):
    if int(args[2]) >= int(args[3]):
        print('%Error: recovery-interval should be greater than sampling-interval')
        return None
    body = {"openconfig-errdisable-ext:link-flap": {
                "config": {
                    "error-disable": "on",
                    "flap-threshold": int(args[1]),
                    "sampling-interval": int(args[2]),
                    "recovery-interval": int(args[3])}
                 }
            }
    uri = cc.Path('/restconf/data/openconfig-errdisable-ext:errdisable-port/port={}/link-flap'.format(args[0]))
    return aa.patch(uri, body)

def patch_openconfig_errdisable_port_range(args):
    if int(args[2]) >= int(args[3]):
        print('%Error: recovery-interval should be greater than sampling-interval')
        return None
    ifrange = args[0].split("=")[1]
    if ifrange.startswith("Eth"):
        ifrangelist = eth_intf_range_expand(ifrange)
    else:
        print('%Error: not supported on this interface type')
    body = {"openconfig-errdisable-ext:port": []}
    for intf in ifrangelist:
        body["openconfig-errdisable-ext:port"].append({
              "name": intf,
              "config": {
                "name": intf },
               "link-flap": {
                 "config": {
                   "error-disable": "on",
                   "flap-threshold": int(args[1]),
                   "sampling-interval": int(args[2]),
                   "recovery-interval": int(args[3])
                  }
                }
              })

    uri = cc.Path('/restconf/data/openconfig-errdisable-ext:errdisable-port/port')
    return aa.patch(uri, body)

def show_errdisable_recovery(args):
    uri = cc.Path('/restconf/data/openconfig-errdisable-ext:errdisable')  
    output = {}
    api_response = aa.get(uri, None)
    if api_response.ok() and api_response.content is not None:
        output.update(api_response.content)
    return output


def show_errdisable_link_flap(args):
    uri = cc.Path('/restconf/data/openconfig-errdisable-ext:errdisable-port/port')
    output = {}
    api_response = aa.get(uri, None)
    if api_response.ok() and api_response.content is not None:
        output.update(api_response.content)
    return output


request_handlers = {
        #show
        'show_errdisable_recovery': show_errdisable_recovery,
        'show_errdisable_link_flap': show_errdisable_link_flap,
        #config
        #'post_openconfig_errdisable': post_openconfig_errdisable, 
        'patch_openconfig_errdisable_interval': patch_openconfig_errdisable_interval, 
        'patch_openconfig_errdisable_cause': patch_openconfig_errdisable_cause, 
        'patch_openconfig_errdisable_port': patch_openconfig_errdisable_port,
        'patch_openconfig_errdisable_port_range': patch_openconfig_errdisable_port_range,
        #delete
        #'delete_openconfig_errdisable': delete_openconfig_errdisable, 
        'delete_openconfig_errdisable_interval': delete_openconfig_errdisable_interval, 
        'delete_openconfig_errdisable_cause': delete_openconfig_errdisable_cause,
        'delete_openconfig_errdisable_port': delete_openconfig_errdisable_port,
        'delete_openconfig_errdisable_port_range': delete_openconfig_errdisable_port_range
}

response_handlers = {
        #show
        'show_errdisable_recovery': generic_show_response_handler,
        'show_errdisable_link_flap': generic_show_response_handler,
        #config
        #'post_openconfig_errdisable': generic_set_response_handler, 
        'patch_openconfig_errdisable_interval': generic_set_response_handler, 
        'patch_openconfig_errdisable_cause': generic_set_response_handler, 
        'patch_openconfig_errdisable_port': generic_set_response_handler, 
        'patch_openconfig_errdisable_port_range': generic_set_response_handler, 
        #delete
        #'delete_openconfig_errdisable': generic_delete_response_handler, 
        'delete_openconfig_errdisable_interval': generic_delete_response_handler, 
        'delete_openconfig_errdisable_cause': generic_delete_response_handler, 
        'delete_openconfig_errdisable_port': generic_delete_response_handler,
        'delete_openconfig_errdisable_port_range': generic_delete_response_handler
}


def run(op_str, args):
    try:
        new_args = []
        for arg in args:
            if isinstance(arg, str):
                arg = arg.strip()

            if arg == 'True':
                arg = True
            elif arg == 'False':
                arg = False

            new_args.append(arg)

        op_str = op_str.strip()

        resp = request_handlers[op_str](new_args)
        if not resp:
            if 'show_errdisable_recovery' in op_str or 'show_errdisable_link_flap' in op_str:
                return 0
            else:
                return -1

        response_handlers[op_str](resp, new_args)
    except Exception as e:
        print("%Error: {}".format(str(e)))
        sys.exit(-1)

    return 0

