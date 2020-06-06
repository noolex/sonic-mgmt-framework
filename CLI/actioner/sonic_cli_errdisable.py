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


def delete_openconfig_errdisable_udld():
    body = { "openconfig-errdisable-ext:udld": False}
    uri = cc.Path('/restconf/data/openconfig-errdisable-ext:errdisable/config/udld')  
    return aa.delete(uri, body)


def delete_openconfig_errdisable_cause(args):
    if args[0] == "udld":
        return delete_openconfig_errdisable_udld()
    return None


def delete_openconfig_errdisable_interval(args):
    body = { "openconfig-errdisable-ext:interval": int(args[0])}
    uri = cc.Path('/restconf/data/openconfig-errdisable-ext:errdisable/config/interval')  
    return aa.delete(uri, body)


def patch_openconfig_errdisable_udld():
    body = { "openconfig-errdisable-ext:udld": True}
    uri = cc.Path('/restconf/data/openconfig-errdisable-ext:errdisable/config/udld')  
    return aa.patch(uri, body)


def patch_openconfig_errdisable_cause(args):
    if args[0] == "udld":
        return patch_openconfig_errdisable_udld()
    return None


def patch_openconfig_errdisable_interval(args):
    body = { "openconfig-errdisable-ext:interval": int(args[0])}
    uri = cc.Path('/restconf/data/openconfig-errdisable-ext:errdisable/config/interval')  
    return aa.patch(uri, body)


def show_errdisable_recovery(args):
    uri = cc.Path('/restconf/data/openconfig-errdisable-ext:errdisable')  
    output = {}
    api_response = aa.get(uri, None)
    if api_response.ok():
        output.update(api_response.content)
    return output


request_handlers = {
        #show
        'show_errdisable_recovery': show_errdisable_recovery,
        #config
        #'post_openconfig_errdisable': post_openconfig_errdisable, 
        'patch_openconfig_errdisable_interval': patch_openconfig_errdisable_interval, 
        'patch_openconfig_errdisable_cause': patch_openconfig_errdisable_cause, 
        #delete
        #'delete_openconfig_errdisable': delete_openconfig_errdisable, 
        'delete_openconfig_errdisable_interval': delete_openconfig_errdisable_interval, 
        'delete_openconfig_errdisable_cause': delete_openconfig_errdisable_cause 
}

response_handlers = {
        #show
        'show_errdisable_recovery': generic_show_response_handler,
        #config
        #'post_openconfig_errdisable': generic_set_response_handler, 
        'patch_openconfig_errdisable_interval': generic_set_response_handler, 
        'patch_openconfig_errdisable_cause': generic_set_response_handler, 
        #delete
        #'delete_openconfig_errdisable': generic_delete_response_handler, 
        'delete_openconfig_errdisable_interval': generic_delete_response_handler, 
        'delete_openconfig_errdisable_cause': generic_delete_response_handler 
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
            if 'show_errdisable_recovery' in op_str:
                return 0
            else:
                return -1

        response_handlers[op_str](resp, new_args)
    except Exception as e:
        print("%Error: {}".format(str(e)))
        sys.exit(-1)

    return 0

