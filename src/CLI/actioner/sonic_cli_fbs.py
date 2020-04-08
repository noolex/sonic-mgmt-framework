#!/usr/bin/python
###########################################################################
#
# Copyright 2019 Broadcom.  The term "Broadcom" refers to Broadcom Inc. and/or
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
import collections
from collections import OrderedDict
import cli_client as cc
from scripts.render_cli import show_cli_output
import ipaddress
import traceback
import json
import cli_log as log
import os
import re


fbs_client = cc.ApiClient()


def create_policy(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_TABLE/POLICY_TABLE_LIST')
    body = dict()
    body["POLICY_TABLE_LIST"] = [{
        "policy_name": args[0],
        "TYPE": args[1].upper(),
    }]
    return fbs_client.patch(keypath, body)


def delete_policy(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_TABLE/POLICY_TABLE_LIST={policy_name}', policy_name=args[0])
    return fbs_client.delete(keypath)


def set_policy_description(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_TABLE/POLICY_TABLE_LIST={policy_name}/DESCRIPTION', policy_name=args[0])
    if len(args) > 2:
        body = {'DESCRIPTION': '"{}"'.format(" ".join(args[1:]))}
    else:
        body = {'DESCRIPTION': args[1]}
    return fbs_client.patch(keypath, body)


def clear_policy_description(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_TABLE/POLICY_TABLE_LIST={policy_name}/DESCRIPTION', policy_name=args[0])
    return fbs_client.delete(keypath)


def create_classifier(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/CLASSIFIER_TABLE/CLASSIFIER_TABLE_LIST')
    body = dict()
    body["CLASSIFIER_TABLE_LIST"] = [{
        "classifier_name": args[0],
        "MATCH_TYPE": args[1].upper(),
    }]
    return fbs_client.patch(keypath, body)


def delete_classifier(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/CLASSIFIER_TABLE/CLASSIFIER_TABLE_LIST={classifier_name}', classifier_name=args[0])
    return fbs_client.delete(keypath)


def set_classifier_description(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/CLASSIFIER_TABLE/CLASSIFIER_TABLE_LIST={classifier_name}/DESCRIPTION', classifier_name=args[0])
    if len(args) > 2:
        body = {'DESCRIPTION': '"{}"'.format(" ".join(args[1:]))}
    else:
        body = {'DESCRIPTION': args[1]}
    return fbs_client.patch(keypath, body)


def clear_classifier_description(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/CLASSIFIER_TABLE/CLASSIFIER_TABLE_LIST={classifier_name}/DESCRIPTION', classifier_name=args[0])
    return fbs_client.delete(keypath)


def set_classifier_match_acl(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/CLASSIFIER_TABLE/CLASSIFIER_TABLE_LIST={classifier_name}/ACL_NAME', classifier_name=args[0])
    if 'mac' == args[1]:
        acl_name = args[2] + '_ACL_L2'
    elif 'ip' == args[1]:
        acl_name = args[2] + '_ACL_IPV4'
    elif 'ipv6' == args[1]:
        acl_name = args[2] + '_ACL_IPV6'
    else:
        print('Unknown ACL Type')
        return

    body = {'ACL_NAME': acl_name}

    return fbs_client.patch(keypath, body)


def clear_classifier_match_acl(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/CLASSIFIER_TABLE/CLASSIFIER_TABLE_LIST={classifier_name}/ACL_NAME', classifier_name=args[0])
    return fbs_client.delete(keypath)


def create_flow(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_SECTIONS_TABLE/POLICY_SECTIONS_TABLE_LIST')
    body = dict()
    body["POLICY_SECTIONS_TABLE_LIST"] = [{
        "policy_name": args[0],
        "classifier_name": args[1],
        "PRIORITY": int(args[2]),
    }]
    return fbs_client.patch(keypath, body)


def delete_flow(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_SECTIONS_TABLE/POLICY_SECTIONS_TABLE_LIST={policy_name},{classifier_name}',
                      policy_name=args[0], classifier_name=args[1])
    return fbs_client.delete(keypath)


def set_flow_description(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_SECTIONS_TABLE/POLICY_SECTIONS_TABLE_LIST={policy_name},{classifier_name}/DESCRIPTION',
                      policy_name=args[0], classifier_name=args[1])
    if len(args) > 3:
        body = {'DESCRIPTION': '"{}"'.format(" ".join(args[2:]))}
    else:
        body = {'DESCRIPTION': args[2]}
    return fbs_client.patch(keypath, body)


def clear_flow_description(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_SECTIONS_TABLE/POLICY_SECTIONS_TABLE_LIST={policy_name},{classifier_name}/DESCRIPTION',
                      policy_name=args[0], classifier_name=args[1])
    return fbs_client.delete(keypath)


def set_pcp_remarking_action(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_SECTIONS_TABLE/POLICY_SECTIONS_TABLE_LIST={policy_name},{classifier_name}/SET_PCP',
                      policy_name=args[0], classifier_name=args[1])
    body = {'SET_PCP': int(args[2])}
    return fbs_client.patch(keypath, body)


def clear_pcp_remarking_action(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_SECTIONS_TABLE/POLICY_SECTIONS_TABLE_LIST={policy_name},{classifier_name}/SET_PCP',
                      policy_name=args[0], classifier_name=args[1])
    return fbs_client.delete(keypath)


def set_dscp_remarking_action(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_SECTIONS_TABLE/POLICY_SECTIONS_TABLE_LIST={policy_name},{classifier_name}/SET_DSCP',
                      policy_name=args[0], classifier_name=args[1])
    body = {'SET_DSCP': int(args[2])}
    return fbs_client.patch(keypath, body)


def clear_dscp_remarking_action(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_SECTIONS_TABLE/POLICY_SECTIONS_TABLE_LIST={policy_name},{classifier_name}/SET_DSCP',
                      policy_name=args[0], classifier_name=args[1])
    return fbs_client.delete(keypath)


def set_policer(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_SECTIONS_TABLE/POLICY_SECTIONS_TABLE_LIST={policy_name},{classifier_name}',
                      policy_name=args[0], classifier_name=args[1])
    body = dict()
    data = {
        "policy_name": args[0],
        "classifier_name": args[1]
    }

    index = 2
    while index < len(args):
        if args[index] == 'cir':
            key = 'SET_POLICER_CIR'
            value = args[index + 1]
            if value.endswith('kbps'):
                value = value.replace('kbps', '000')
            elif value.endswith('mbps'):
                value = value.replace('mbps', '000000')
            elif value.endswith('gbps'):
                value = value.replace('gbps', '000000000')
            elif value.endswith('tbps'):
                value = value.replace('tbps', '000000000000')
            elif value.endswith('bps'):
                value = value.replace('bps', '')
        elif args[index] == 'cbs':
            key = 'SET_POLICER_CBS'
            value = args[index + 1]
            if value.endswith('KB'):
                value = value.replace('KB', '000')
            elif value.endswith('MB'):
                value = value.replace('MB', '000000')
            elif value.endswith('GB'):
                value = value.replace('GB', '000000000')
            elif value.endswith('TB'):
                value = value.replace('TB', '000000000000')
            elif value.endswith('B'):
                value = value.replace('B', '')
        elif args[index] == 'pir':
            key = 'SET_POLICER_PIR'
            value = args[index+1]
            if value.endswith('kbps'):
                value = value.replace('kbps', '000')
            elif value.endswith('mbps'):
                value = value.replace('mbps', '000000')
            elif value.endswith('gbps'):
                value = value.replace('gbps', '000000000')
            elif value.endswith('tbps'):
                value = value.replace('tbps', '000000000000')
            elif value.endswith('bps'):
                value = value.replace('bps', '')
        elif args[index] == 'pbs':
            key = 'SET_POLICER_PBS'
            value = args[index + 1]
            if value.endswith('KB'):
                value = value.replace('KB', '000')
            elif value.endswith('MB'):
                value = value.replace('MB', '000000')
            elif value.endswith('GB'):
                value = value.replace('GB', '000000000')
            elif value.endswith('TB'):
                value = value.replace('TB', '000000000000')
            elif value.endswith('B'):
                value = value.replace('B', '')
        else:
            print('%Error: Unknown argument {}'.format(args[index]))
            return

        data[key] = int(value)
        index += 2

    body["POLICY_SECTIONS_TABLE_LIST"] = [data]
    return fbs_client.patch(keypath, body)


def clear_policer(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_SECTIONS_TABLE/POLICY_SECTIONS_TABLE_LIST={policy_name},{classifier_name}',
                      policy_name=args[0], classifier_name=args[1])
    response = fbs_client.get(keypath)
    if response.ok():
        data = response.content
        if len(args) == 2:
            delete_params = ['SET_POLICER_PBS', 'SET_POLICER_PIR', 'SET_POLICER_CBS', 'SET_POLICER_CIR']
        else:
            delete_params = []
            for feat in args[2:]:
                delete_params.append('SET_POLICER_' + feat.upper())

        for feat in delete_params:
            if feat in data['sonic-flow-based-services:POLICY_SECTIONS_TABLE_LIST'][0].keys():
                del data['sonic-flow-based-services:POLICY_SECTIONS_TABLE_LIST'][0][feat]

        return fbs_client.put(keypath, data)
    else:
        print('Error:{}'.format(response.error_message()))


def bind_policy(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_BINDING_TABLE/POLICY_BINDING_TABLE_LIST={interface_name}',
                      interface_name=args[3] if len(args) == 4 else "Switch")
    body = {'{}_{}_POLICY'.format('INGRESS' if args[2] =='in' else "EGRESS", args[1].upper()): args[0]}
    return fbs_client.post(keypath, body)


def unbind_policy(args):
    keypath = cc.Path('/restconf/data/sonic-flow-based-services:sonic-flow-based-services/POLICY_BINDING_TABLE/POLICY_BINDING_TABLE_LIST={interface_name}/{policy_dir}_{policy_type}_POLICY',
                      interface_name=(args[2] if len(args) == 3 else "Switch"), policy_dir=('INGRESS' if args[1] =='in' else "EGRESS"), policy_type=args[0].upper())
    return fbs_client.delete(keypath)





def show_policy(args):
    print('Not implemented')


def show_classifier(args):
    print('Not implemented')


def show_policy_summary(args):
    print('Not implemented')


def show_details_by_policy(args):
    print('Not implemented')


def show_details_by_interface(args):
    print('Not implemented')


########################################################################################################################
#                                                  Response handlers                                                   #
########################################################################################################################
def handle_generic_set_response(response, args):
    if response.ok():
        resp_content = response.content
        if resp_content is not None:
            print("{}".format(str(resp_content)))
        return 0
    else:
        try:
            error_data = response.errors().get('error', list())[0]
            if 'error-app-tag' in error_data and error_data['error-app-tag'] == 'too-many-elements':
                print('Error: Exceeds maximum number of ACL / ACL Rules')
            else:
                print(response.error_message())
        except Exception as e:
            print(response.error_message())

        return -1


def handle_generic_delete_response(response, args):
    if response.ok():
        resp_content = response.content
        if resp_content is not None:
            print("%Error: {}".format(str(resp_content)))
            return -1

        return 0
    elif response.status_code != '404':
        try:
            error_data = response.errors().get('error', list())[0]
            if 'error-app-tag' in error_data and error_data['error-app-tag'] == 'too-many-elements':
                print('Error: Exceeds maximum number of ACL / ACL Rules')
            else:
                print(response.error_message())
        except Exception as e:
            log.log_error(str(e))
            print(response.error_message())
        return -1


def handle_show_policy_response(args):
    pass


def handle_show_classifier_response(args):
    pass


def handle_show_policy_summary_response(args):
    pass


def handle_show_details_by_policy_response(args):
    pass


def handle_show_details_by_interface_response(args):
    pass


########################################################################################################################
#
########################################################################################################################

request_handlers = {
    'create_policy': create_policy,
    'delete_policy': delete_policy,
    'set_policy_description': set_policy_description,
    'clear_policy_description': clear_policy_description,
    'create_classifier': create_classifier,
    'delete_classifier': delete_classifier,
    'set_classifier_description': set_classifier_description,
    'clear_classifier_description': clear_classifier_description,
    'set_classifier_match_acl': set_classifier_match_acl,
    'clear_classifier_match_acl': clear_classifier_match_acl,
    'create_flow': create_flow,
    'delete_flow': delete_flow,
    'set_flow_description': set_flow_description,
    'clear_flow_description': clear_flow_description,
    'set_pcp_remarking_action': set_pcp_remarking_action,
    'clear_pcp_remarking_action': clear_pcp_remarking_action,
    'set_dscp_remarking_action': set_dscp_remarking_action,
    'clear_dscp_remarking_action': clear_dscp_remarking_action,
    'set_policer': set_policer,
    'clear_policer': clear_policer,
    'bind_policy': bind_policy,
    'unbind_policy': unbind_policy,

    'show_policy': show_policy,
    'show_classifier': show_classifier,
    'show_policy_summary': show_policy_summary,
    'show_details_by_policy': show_details_by_policy,
    'show_details_by_interface': show_details_by_interface
}


response_handlers = {
    'create_policy': handle_generic_set_response,
    'delete_policy': handle_generic_delete_response,
    'set_policy_description': handle_generic_set_response,
    'clear_policy_description': handle_generic_delete_response,
    'create_classifier': handle_generic_set_response,
    'delete_classifier': handle_generic_delete_response,
    'set_classifier_description': handle_generic_set_response,
    'clear_classifier_description': handle_generic_delete_response,
    'set_classifier_match_acl': handle_generic_set_response,
    'clear_classifier_match_acl': handle_generic_delete_response,
    'create_flow': handle_generic_set_response,
    'delete_flow': handle_generic_delete_response,
    'set_flow_description': handle_generic_set_response,
    'clear_flow_description': handle_generic_delete_response,
    'set_pcp_remarking_action': handle_generic_set_response,
    'clear_pcp_remarking_action': handle_generic_delete_response,
    'set_dscp_remarking_action': handle_generic_set_response,
    'clear_dscp_remarking_action': handle_generic_delete_response,
    'set_policer': handle_generic_set_response,
    'clear_policer': handle_generic_delete_response,
    'bind_policy': handle_generic_set_response,
    'unbind_policy': handle_generic_delete_response,

    'show_policy': handle_show_policy_response,
    'show_classifier': handle_show_classifier_response,
    'show_policy_summary': handle_show_policy_summary_response,
    'show_details_by_policy': handle_show_details_by_policy_response,
    'show_details_by_interface': handle_show_details_by_interface_response
}


def run(op_str, args):
    try:
        log.log_debug(str(args))
        resp = request_handlers[op_str](args)
        if resp:
            return response_handlers[op_str](resp, args)
    except Exception as e:
        log.log_error(traceback.format_exc())
        print('%Error: Encountered exception "{}"'.format(str(e)))
        return -1
    return 0


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2:])
