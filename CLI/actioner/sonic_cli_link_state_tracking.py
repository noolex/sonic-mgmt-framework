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

import re
import os
import cli_client as cc
from rpipe_utils import pipestr
import scripts.render_cli as cli
import cli_log as log
import traceback


class SonicLinkStateTrackingCLIError(RuntimeError):
    """Indicates CLI processing errors that needs to be displayed to user"""
    pass


def create_link_state_tracking_group(args):
    aa = cc.ApiClient()
    body = {
        "openconfig-lst-ext:lst-group": [
        {
          "name": args[0],
          "config": {
            "name": args[0]
          }
        }
      ]
    }
    uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/lst-groups/lst-group')
    return aa.patch(uri, body)


def delete_link_state_tracking_group(args):
    aa = cc.ApiClient()
    uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/lst-groups/lst-group={name}', name=args[0])
    return aa.delete(uri)


def set_link_state_tracking_group_description(args):
    aa = cc.ApiClient()
    uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/lst-groups/lst-group={name}/config/description', name=args[0])

    descr = args[1]
    full_cmd = os.getenv('USER_COMMAND', None)
    match = re.search('description (["]?.*["]?)', full_cmd)
    if match:
        descr = match.group(1)
        if descr.startswith('"'):
            descr = descr[1:-1]

    body = {
        "openconfig-lst-ext:description": descr
    }
    return aa.patch(uri, body)


def delete_link_state_tracking_group_description(args):
    aa = cc.ApiClient()
    uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/lst-groups/lst-group={name}/config/description', name=args[0])
    return aa.delete(uri)


def set_link_state_tracking_group_timeout(args):
    timeout = int(args[1])
    if timeout > 1800:
        raise RuntimeError("Timeout not in range 1-1800")

    aa = cc.ApiClient()
    uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/lst-groups/lst-group={name}/config/timeout', name=args[0])
    body = {
        "openconfig-lst-ext:timeout": timeout
    }
    return aa.patch(uri, body)


def delete_link_state_tracking_group_timeout(args):
    aa = cc.ApiClient()
    uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/lst-groups/lst-group={name}/config/timeout', name=args[0])
    return aa.delete(uri)


def set_link_state_tracking_group_downstream(args):
    aa = cc.ApiClient()
    uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/interfaces/interface')
    body = {
        "openconfig-lst-ext:interface": [
        {
          "id": args[1],
          "config": {
            "id": args[1]
          },
          "interface-ref": {
            "config": {
              "interface": args[1]
            }
          },
          "downstream-group": {
            "config": {
              "group-name": args[0]
            }
          }
        }
      ]
    }
    return aa.patch(uri, body)


def delete_link_state_tracking_group_downstream(args):
    aa = cc.ApiClient()
    if len(args) == 2:
        uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/interfaces/interface={downstr}/downstream-group', downstr=args[1])
    else:
        uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/interfaces/interface={downstr}/downstream-group', downstr=args[0])
    return aa.delete(uri)


def set_link_state_tracking_group_upstream(args):
    aa = cc.ApiClient()
    uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/interfaces/interface')
    body = {
       "openconfig-lst-ext:interface": [
        {
          "id": args[1],
          "config": {
            "id": args[1]
          },
          "interface-ref": {
            "config": {
              "interface": args[1]
            }
          },
          "upstream-groups": {
            "upstream-group": [
              {
                "group-name": args[0],
                "config": {
                  "group-name": args[0]
                }
              }
            ]
          }
        }
      ]
    }

    return aa.patch(uri, body)


def delete_link_state_tracking_group_upstream(args):
    aa = cc.ApiClient()
    if len(args) == 2:
        uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/interfaces/interface={upstr}/upstream-groups/upstream-group={grp_name}', grp_name=args[0], upstr=args[1])
    else:
        uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/interfaces/interface={upstr}/upstream-groups', upstr=args[0])
    return aa.delete(uri)

def delete_link_state_tracking_group_binding(args):
    if args[0] == 'upstream':
        return delete_link_state_tracking_group_upstream(args[1:])
    else:
        return delete_link_state_tracking_group_downstream(args[1:])

def set_link_state_tracking_group_all_mclag_downstream(args):
    aa = cc.ApiClient()
    uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/lst-groups/lst-group={grp_name}/config/all-mclags-downstream', grp_name=args[0])
    body = {
        "openconfig-lst-ext:all-mclags-downstream": True
    }
    return aa.patch(uri, body)

def delete_link_state_tracking_group_all_mclag_downstream(args):
    aa = cc.ApiClient()
    uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/lst-groups/lst-group={grp_name}/config/all-mclags-downstream', grp_name=args[0])
    return aa.delete(uri)

def show_link_state_tracking_group_info(args):
    aa = cc.ApiClient()
    if len(args):
        uri = cc.Path('/restconf/data/sonic-link-state-tracking:sonic-link-state-tracking/INTF_TRACKING_TABLE/INTF_TRACKING_TABLE_LIST={grp_name}', grp_name=args[0])
    else:
        uri = cc.Path('/restconf/data/sonic-link-state-tracking:sonic-link-state-tracking/INTF_TRACKING_TABLE/INTF_TRACKING_TABLE_LIST')
    return aa.get(uri, None, False)


def generic_set_response_handler(response, args):
    if response.ok():
        resp_content = response.content
        if resp_content is not None:
            raise SonicLinkStateTrackingCLIError(str(resp_content))
    else:
        try:
            error_data = response.content['ietf-restconf:errors']['error'][0]
            if 'error-app-tag' in error_data and error_data['error-app-tag'] == 'too-many-elements':
                raise SonicLinkStateTrackingCLIError('Exceeds maximum number of link state group')
            else:
                raise SonicLinkStateTrackingCLIError(response.error_message())
        except Exception:
            raise SonicLinkStateTrackingCLIError(response.error_message())


def generic_delete_response_handler(response, args):
    if response.ok():
        resp_content = response.content
        if resp_content is not None:
            raise SonicLinkStateTrackingCLIError(str(resp_content))
    elif response.status_code != '404':
        try:
            error_data = response.content['ietf-restconf:errors']['error'][0]
            if 'error-app-tag' in error_data and error_data['error-app-tag'] == 'too-many-elements':
                raise SonicLinkStateTrackingCLIError('Exceeds maximum number of link state group')
            else:
                raise SonicLinkStateTrackingCLIError(response.error_message())
        except Exception:
            raise SonicLinkStateTrackingCLIError(response.error_message())


def show_link_state_tracking_group_data(groups, details):
    output = ""
    for data in groups:
        output = output + 'Name: {}'.format(data['name']) + '\n'
        descr = data.get('description', "")
        output = output + 'Description: {}'.format(descr if " " not in descr else '"{}"'.format(descr)) + '\n'
        output = output + 'Timeout: {}'.format(data.get('timeout', "")) + '\n'

        if details:
            output = output + 'Upstream:' + '\n'
            for upstr, status in zip(data.get('upstream', []), data.get('upstream_status', [])):
                if status == "":
                    output = output + '    {}'.format(upstr) + '\n'
                else:
                    output = output + '    {} ({})'.format(upstr, status) + '\n'

            output = output + 'Downstream:' + '\n'
            for downstr, status in zip(data.get('downstream', []), data.get('downstream_status', [])):
                if status == "":
                    output = output + '    {}'.format(downstr) + '\n'
                else:
                    output = output + '    {} ({})'.format(downstr, status) + '\n'
        output = output + '' + '\n'
    cli.write(output)


def show_link_state_tracking_group_response_handler(response, args):
    if response.ok():
        data = response.content
        if bool(data):
            show_link_state_tracking_group_data(data['sonic-link-state-tracking:INTF_TRACKING_TABLE_LIST'], len(args) > 0)
        elif len(args) > 0:
            raise SonicLinkStateTrackingCLIError("Group not found")
    elif str(response.status_code) == '404':
        if len(args) > 0:
            raise SonicLinkStateTrackingCLIError("Group not found")
    else:
        raise SonicLinkStateTrackingCLIError(response.error_message())


request_handlers = {
    'create_link_state_tracking_group': create_link_state_tracking_group,
    'delete_link_state_tracking_group': delete_link_state_tracking_group,
    'set_link_state_tracking_group_description': set_link_state_tracking_group_description,
    'delete_link_state_tracking_group_description': delete_link_state_tracking_group_description,
    'set_link_state_tracking_group_timeout': set_link_state_tracking_group_timeout,
    'delete_link_state_tracking_group_timeout': delete_link_state_tracking_group_timeout,
    'set_link_state_tracking_group_downstream': set_link_state_tracking_group_downstream,
    'set_link_state_tracking_group_all_mclag_downstream': set_link_state_tracking_group_all_mclag_downstream,
    'delete_link_state_tracking_group_all_mclag_downstream': delete_link_state_tracking_group_all_mclag_downstream,
    'set_link_state_tracking_group_upstream': set_link_state_tracking_group_upstream,
    'delete_link_state_tracking_group_binding': delete_link_state_tracking_group_binding,
    'show_link_state_tracking_group_info': show_link_state_tracking_group_info
}

response_handlers = {
    'create_link_state_tracking_group': generic_set_response_handler,
    'delete_link_state_tracking_group': generic_delete_response_handler,
    'set_link_state_tracking_group_description': generic_set_response_handler,
    'delete_link_state_tracking_group_description': generic_delete_response_handler,
    'set_link_state_tracking_group_timeout': generic_set_response_handler,
    'delete_link_state_tracking_group_timeout': generic_delete_response_handler,
    'set_link_state_tracking_group_downstream': generic_set_response_handler,
    'set_link_state_tracking_group_all_mclag_downstream': generic_set_response_handler,
    'delete_link_state_tracking_group_all_mclag_downstream': generic_set_response_handler,
    'set_link_state_tracking_group_upstream': generic_set_response_handler,
    'delete_link_state_tracking_group_binding': generic_delete_response_handler,
    'show_link_state_tracking_group_info': show_link_state_tracking_group_response_handler
}


def run(op_str, args):
    try:
        full_cmd = os.getenv('USER_COMMAND', None)
        if full_cmd is not None:
            pipestr().write(full_cmd.split())
        resp = request_handlers[op_str](args)
        response_handlers[op_str](resp, args)
    except SonicLinkStateTrackingCLIError as e:
        print("%Error: {}".format(e.message))
        return -1
    except Exception as e:
        log.log_error(traceback.format_exc())
        print('%Error: Encountered exception "{}"'.format(str(e)))
        return -1
    return


# Show running config related
def show_running_lst_group(render_tables):
    status = 'CB_FAIL'
    output = list()

    aa = cc.ApiClient()
    if 'group' in render_tables:
        response = aa.get('/restconf/data/openconfig-lst-ext:lst/lst-groups/lst-group={}'.format(render_tables['group']))
        if response.ok():
            status = 'CB_SUCCESS'
            if bool(response.content):
                group = response.content["openconfig-lst-ext:lst-group"][0]
                __show_running_config_group(output, group)

    else:
        response = aa.get('/restconf/data/openconfig-lst-ext:lst/lst-groups')
        if response.ok():
            status = 'CB_SUCCESS'
            if bool(response.content):
                groups = response.content["openconfig-lst-ext:lst-groups"]["lst-group"]
                for group in groups:
                    __show_running_config_group(output, group)

    return status, ';'.join(output), True


def __show_running_config_group(output, grp_data):
    config = grp_data['config']
    output.append('link state track {}'.format(config['name']))
    if 'timeout' in config:
        output.append('  timeout {}'.format(config['timeout']))
    if 'description' in config:
        descr = config['description']
        if " " in descr:
            descr = '"{}"'.format(descr)
        output.append('  description {}'.format(descr))
    if 'all-mclags-downstream' in config and config['all-mclags-downstream']:
        output.append('  downstream all-mclag')


def show_running_lst_interface(render_tables):
    status = 'CB_FAIL'
    output = []
    aa = cc.ApiClient()
    response = aa.get('/restconf/data/openconfig-lst-ext:lst/interfaces/interface={id}'.format(id=render_tables['name']))
    if response.ok():
        status = 'CB_SUCCESS'
        data = response.content['openconfig-lst-ext:interface'][0]
        if 'upstream-groups' in data:
            upstr_grps = data['upstream-groups']['upstream-group']
            for grp in upstr_grps:
                output.append('link state track {} upstream'.format(grp['group-name']))

        if 'downstream-group' in data:
            if 'config' in data['downstream-group']:
                output.append('link state track {} downstream'.format(data['downstream-group']['config']['group-name']))

    return status, ';'.join(output), True

