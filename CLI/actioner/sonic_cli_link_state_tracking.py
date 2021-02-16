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
import time

lst_client = cc.ApiClient()


class SonicLinkStateTrackingCLIError(RuntimeError):
    """Indicates CLI processing errors that needs to be displayed to user"""
    pass


def create_link_state_tracking_group(args):
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
    return lst_client.patch(uri, body)


def delete_link_state_tracking_group(args):
    uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/lst-groups/lst-group={name}', name=args[0])
    return lst_client.delete(uri)


def set_link_state_tracking_group_description(args):
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
    return lst_client.patch(uri, body)


def delete_link_state_tracking_group_description(args):
    uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/lst-groups/lst-group={name}/config/description', name=args[0])
    return lst_client.delete(uri)


def set_link_state_tracking_group_timeout(args):
    timeout = int(args[1])
    if timeout > 1800:
        raise RuntimeError("Timeout not in range 1-1800")

    uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/lst-groups/lst-group={name}/config/timeout', name=args[0])
    body = {
        "openconfig-lst-ext:timeout": timeout
    }
    return lst_client.patch(uri, body)


def delete_link_state_tracking_group_timeout(args):
    uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/lst-groups/lst-group={name}/config/timeout', name=args[0])
    return lst_client.delete(uri)


def set_link_state_tracking_group_downstream(args):
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
    return lst_client.patch(uri, body)


def delete_link_state_tracking_group_downstream(args):
    if len(args) == 2:
        uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/interfaces/interface={downstr}/downstream-group',
                      downstr=args[1])
    else:
        uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/interfaces/interface={downstr}/downstream-group',
                      downstr=args[0])
    return lst_client.delete(uri)


def set_link_state_tracking_group_upstream(args):
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

    return lst_client.patch(uri, body)


def delete_link_state_tracking_group_upstream(args):
    group_name = None
    if "name=" in args[0]:
        name=args[0].split("=",1)
        group_name = name[1]
        
    if group_name is None:
        uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/interfaces/interface={upstr}/upstream-groups',
                      upstr=args[0])
    else:
        uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/interfaces/interface={upstr}/upstream-groups/upstream-group={grp_name}',
                      grp_name=group_name, upstr=args[1])
    return lst_client.delete(uri)

def delete_link_state_tracking_group_binding(args):
    intf_dir = None
    next_arg_index = 1

    if "grp_dir=" in args[0]:
        temp=args[0].split("=",1)
        intf_dir = temp[1]

    if not intf_dir and "name=" in args[1]:
        temp=args[1].split("=",1)
        intf_dir = temp[1]
        next_arg_index = 2

    if intf_dir == 'upstream':
        return delete_link_state_tracking_group_upstream(args[next_arg_index:])
    else:
        return delete_link_state_tracking_group_downstream(args[next_arg_index:])

def set_link_state_tracking_group_threshold(args):
    uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/lst-groups/lst-group={grp_name}/config', grp_name=args[0])
    body = {
        "openconfig-lst-ext:config": {
            "name": args[0],
        }
    }

    params = args[1:]
    for key, val in zip(params[::2], params[1::2]):
        if key == "type" and val == "percentage":
            body["openconfig-lst-ext:config"]["threshold-type"] = "ONLINE_PERCENTAGE"
        elif key == 'up' or key == 'down':
            body["openconfig-lst-ext:config"]["threshold-{}".format(key)] = val

    return lst_client.patch(uri, body)

def delete_link_state_tracking_group_threshold(args):
    if len(args) > 1:
        uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/lst-groups/lst-group={grp_name}/config/threshold-{op}', grp_name=args[0], op=args[1])
    else:
        uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/lst-groups/lst-group={grp_name}/config/threshold-type', grp_name=args[0])
    return lst_client.delete(uri)

def set_link_state_tracking_group_all_mclag_downstream(args):
    uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/lst-groups/lst-group={grp_name}/config/all-mclags-downstream',
                  grp_name=args[0])
    body = {
        "openconfig-lst-ext:all-mclags-downstream": True
    }
    return lst_client.patch(uri, body)

def delete_link_state_tracking_group_all_mclag_downstream(args):
    uri = cc.Path('/restconf/data/openconfig-lst-ext:lst/lst-groups/lst-group={grp_name}/config/all-mclags-downstream',
                  grp_name=args[0])
    return lst_client.delete(uri)

def show_link_state_tracking_group_info(args):
    if len(args):
        uri = cc.Path('/restconf/data/sonic-link-state-tracking:sonic-link-state-tracking/INTF_TRACKING_TABLE/INTF_TRACKING_TABLE_LIST={grp_name}',
                      grp_name=args[0])
    else:
        uri = cc.Path('/restconf/data/sonic-link-state-tracking:sonic-link-state-tracking/INTF_TRACKING_TABLE/INTF_TRACKING_TABLE_LIST')
    return lst_client.get(uri, depth=None, ignore404=False)


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
        timeout = int(data.get('timeout', 60))
        output = output + 'Timeout: {}'.format(timeout) + '\n'

        if details:
            rem_time = 0
            now_time = int(time.time())
            start_time = int(data['bringup_start_time'])
            if 0 != start_time:
                rem_time = timeout - (now_time - start_time)
            output = output + 'Startup remaining time: {} seconds'.format(rem_time) + '\n'

            if data.get('threshold_type', None):
                if data['threshold_type'] == 'ONLINE_PERCENTAGE':
                    output = output + "Threshold type: Online-percentage\n"
                output = output + "Threshold up: {}\n".format(int(float(data['threshold_up'])))
                output = output + "Threshold down: {}\n".format(int(float(data['threshold_down'])))

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
            show_link_state_tracking_group_data(data['sonic-link-state-tracking:INTF_TRACKING_TABLE_LIST'],
                                                len(args) > 0)
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
    'set_link_state_tracking_group_threshold': set_link_state_tracking_group_threshold,
    'delete_link_state_tracking_group_threshold': delete_link_state_tracking_group_threshold,
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
    'set_link_state_tracking_group_threshold': generic_set_response_handler,
    'delete_link_state_tracking_group_threshold': generic_delete_response_handler,
    'show_link_state_tracking_group_info': show_link_state_tracking_group_response_handler
}


def run(op_str, args):
    try:
        log.log_debug("Op:{} Args:{}".format(op_str, str(args)));
        full_cmd = os.getenv('USER_COMMAND', None)
        if full_cmd is not None:
            pipestr().write(full_cmd.split())
        resp = request_handlers[op_str](args)
        response_handlers[op_str](resp, args)
    except SonicLinkStateTrackingCLIError as e:
        if e.message.startswith("%Error"):
            print(e.message)
        else:
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

    if 'group' in render_tables:
        response = lst_client.get(cc.Path('/restconf/data/openconfig-lst-ext:lst/lst-groups/lst-group={group}',
                                          group=render_tables['group']), depth=None, ignore404=False)
        if response.ok():
            status = 'CB_SUCCESS'
            if bool(response.content):
                group = response.content["openconfig-lst-ext:lst-group"][0]
                __show_running_config_group(output, group)

    else:
        response = lst_client.get('/restconf/data/openconfig-lst-ext:lst/lst-groups', depth=None, ignore404=False)
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
    thr_cmd = 'threshold'
    if config.get('threshold-type') == "openconfig-lst-ext:ONLINE_PERCENTAGE":
        thr_cmd += " type percentage"
    if config.get('threshold-up'):
        thr_cmd += " up {}".format(int(config.get('threshold-up')))
    if config.get('threshold-down'):
        thr_cmd += " down {}".format(int(config.get('threshold-down')))
    if thr_cmd != 'threshold':
        output.append('  ' + thr_cmd)


def show_running_lst_interface(render_tables):
    status = 'CB_SUCCESS'
    output = []
    if render_tables['name'] in render_tables[__name__]:
        data = render_tables[__name__][render_tables['name']]
        if 'upstream-groups' in data:
            upstr_grps = data['upstream-groups']['upstream-group']
            for grp in upstr_grps:
                output.append('link state track {} upstream'.format(grp['group-name']))

        if 'downstream-group' in data:
            if 'config' in data['downstream-group']:
                output.append('link state track {} downstream'.format(data['downstream-group']['config']['group-name']))
    else:
        log.log_debug("No LST config for {}".format(render_tables['name']))

    return status, ';'.join(output), True


def __build_lst_interface_bind_cache(intf_type, ifname, cache):
    log.log_debug("LST Interface {},{} specific show running".format(intf_type, ifname))
    if ifname:
        keypath = cc.Path('/restconf/data/openconfig-lst-ext:lst/interfaces/interface={id}', id=ifname)
        response = lst_client.get(keypath, depth=None, ignore404=False)
        if response.ok() is False:
            log.log_debug("Resp not success")
            return
        if 'openconfig-lst-ext:interface' not in response.content:
            log.log_debug("'openconfig-lst-ext:interface' not found in response {}".format(str(response.content)))
            return
        cache[ifname] = response.content['openconfig-lst-ext:interface'][0]
    else:
        keypath = cc.Path('/restconf/data/openconfig-lst-ext:lst/interfaces/interface')
        response = lst_client.get(keypath, depth=None, ignore404=False)
        if response.ok():
            for intf_data in response.content['openconfig-lst-ext:interface']:
                if (intf_type and intf_data['id'].startswith(intf_type)) or (intf_type is None):
                    cache[intf_data['id']] = intf_data
                else:
                    log.log_debug("Not storing cache for {}".format(intf_data['id']))
        else:
            log.log_debug("Resp not success")
            return


def show_running_config_lst_start_callback(context, cache):
    log.log_debug("LST Context={}".format(str(context)))
    if context['view_name'] == '':
        log.log_debug("All LST and Interfaces config")
        __build_lst_interface_bind_cache(None, None, cache)
    elif not bool(context['view_keys']):
        if context['view_name'] == 'configure-if':
            log.log_debug('All ethernet interfaces')
            __build_lst_interface_bind_cache('Eth', None, cache)
        elif context['view_name'] == 'configure-vlan':
            log.log_debug('All VLAN interfaces')
            __build_lst_interface_bind_cache('Vlan', None, cache)
        elif context['view_name'] == 'configure-lag':
            log.log_debug("All LAG interfaces")
            __build_lst_interface_bind_cache('PortChannel', None, cache)
    else:
        __build_lst_interface_bind_cache(None, context['view_keys']['name'], cache)
