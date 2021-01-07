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

import cli_client as cc
from collections import OrderedDict
import sonic_cli_acl
import cli_log as log


acl_client = cc.ApiClient()


def __build_acl_config_cache(acl_type, acl_name, cache):
    log.log_debug("Building ACL Cache for {},{}".format(acl_type, acl_name))
    if acl_name is not None:
        cache['_acl_cache_'] = dict()
        keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set={name},{acl_type}', name=acl_name,
                          acl_type=acl_type)
        response = acl_client.get(keypath, depth=None, ignore404=False)
        if response.ok():
            cache['_acl_cache_'][(acl_type, acl_name)] = response.content['openconfig-acl:acl-set'][0]
            log.log_debug("ACL cache added for {},{}".format(acl_type, acl_name))
        else:
            log.log_debug(response.error_message())
    elif '_acl_cache_' not in cache:
        cache['_acl_cache_'] = dict()
        keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set')
        response = acl_client.get(keypath, depth=None, ignore404=False)
        if response.ok():
            for acl_set in response.content['openconfig-acl:acl-set']:
                oc_acl_type = acl_set['type'].split(':')[-1]
                if (acl_type and oc_acl_type == acl_type) or (acl_type is None):
                    cache['_acl_cache_'][(oc_acl_type, acl_set['name'])] = acl_set
                    log.log_debug("ACL cache added for {},{}".format(oc_acl_type, acl_set['name']))
                else:
                    log.log_debug("Not storing ACL {},{}".format(oc_acl_type, acl_set['name']))
        else:
            log.log_debug(response.error_message())
    else:
        log.log_debug("ACL Cache already exists")


def __build_acl_binding_cache(intf_type, ifname, cache):
    log.log_debug("ACL Interface {},{} specific show running".format(intf_type, ifname))
    if ifname:
        keypath = cc.Path('/restconf/data/openconfig-acl:acl/interfaces/interface={intfname}', intfname=ifname)
        response = acl_client.get(keypath, depth=None, ignore404=False)
        if response.ok() is False:
            log.log_error("Resp not success")
            return
        if 'openconfig-acl:interface' not in response.content:
            log.log_debug("'openconfig-acl:interface' not found in response {}".format(str(response.content)))
            return
        cache[ifname] = {'openconfig-acl:interface': response.content['openconfig-acl:interface'][0]}
    else:
        keypath = cc.Path('/restconf/data/openconfig-acl:acl/interfaces/interface')
        response = acl_client.get(keypath, depth=None, ignore404=False)
        if response.ok():
            for intf_data in response.content['openconfig-acl:interface']:
                if (intf_type and intf_data['id'].startswith(intf_type)) or (intf_type is None):
                    cache[intf_data['id']] = {'openconfig-acl:interface': intf_data}
                else:
                    log.log_debug("Not storing cache for {}".format(intf_data['id']))
        else:
            log.log_debug("Resp not success")
            return


def __show_running_acl(in_acl_type, in_acl_name, cache):
    log.log_debug("Show running for ACL {},{}".format(in_acl_type, in_acl_name))
    add_ex = False
    cmd_str = ''
    for (acl_type, acl_name), acl_set in cache['_acl_cache_'].items():
        if in_acl_type and acl_type != in_acl_type:
            continue
        if in_acl_name and acl_name != in_acl_name:
            continue

        user_acl_type = sonic_cli_acl.__convert_oc_acl_type_to_user_fmt(acl_type)
        if add_ex:
            cmd_str += "\n!\n"
        cmd_str += '{} access-list {}'.format(user_acl_type, acl_name)
        add_ex = True
        # Convert the OCYANG format 'acl-set' to user format 'data'
        data = OrderedDict()
        sonic_cli_acl.__convert_oc_acl_set_to_user_fmt(acl_set, data)
        acl_data = data[user_acl_type][acl_name]
        if 'description' in acl_data:
            cmd_str += "\n remark {}".format(acl_data['description'])

        # Loop for number of rules
        for seq_num, rule in acl_data['rules'].items():
            cmd_str += "\n"
            rule_data = rule['rule_data']
            # rule_data can contain integers. Convert all to list of strings
            rule_data_str_list = [str(i) for i in rule_data]
            cmd_str += " seq {} {}".format(seq_num, ' '.join(rule_data_str_list))
            if 'description' in rule:
                cmd_str += " remark {}".format(rule['description'])
    return cmd_str


def show_running_mac_acl_table_cb(render_tables):
    return 'CB_SUCCESS', __show_running_acl('ACL_L2', render_tables.get('name'), render_tables[__name__]), True


def show_running_ipv4_acl_table_cb(render_tables):
    return 'CB_SUCCESS', __show_running_acl('ACL_IPV4', render_tables.get('name'), render_tables[__name__]), True


def show_running_ipv6_acl_table_cb(render_tables):
    return 'CB_SUCCESS', __show_running_acl('ACL_IPV6', render_tables.get('name'), render_tables[__name__]), True


def __display_acl_bindings(data, direction, prefix):
    cmd_str = ''
    for acl_entry in data:
        config = acl_entry['config']
        acl_name = config['set-name']
        acl_type = config['type']
        if acl_type == 'openconfig-acl:ACL_L2':
            cmd_str += "{}mac access-group {} {};".format(prefix, acl_name, direction)
        elif acl_type == 'openconfig-acl:ACL_IPV4':
            cmd_str += "{}ip access-group {} {};".format(prefix, acl_name, direction)
        elif acl_type == 'openconfig-acl:ACL_IPV6':
            cmd_str += "{}ipv6 access-group {} {};".format(prefix, acl_name, direction)

    return cmd_str


def __show_running_acl_binding(keypath, root, data, prefix):
    # log.log_debug("Show ACL binding for {},{},{},{}".format(keypath, root, data, prefix))
    cmd_str = ''
    if keypath:
        response = acl_client.get(keypath, depth=None, ignore404=False)

        if response.ok() is False:
            log.log_debug("Resp not success")
            return ''
        if root not in response.content:
            log.log_debug("Root not found in response {}".format(str(response.content)))
            return ''

        content = response.content
        data = content[root]
    else:
        data = data[root]

    for key in ['ingress-acl-sets', 'egress-acl-sets']:
        try:
            acl_sets = data[key][key[:-1]]
            direction = 'in'
            if key.startswith('egress'):
                direction = 'out'
            cmd_str += __display_acl_bindings(acl_sets, direction, prefix)
        except KeyError as e:
            log.log_debug('KeyError::' + str(e))
        except Exception as e:
            log.log_debug(str(e))
    return cmd_str


def show_running_acl_intf_bind_cb(render_tables):
    # log.log_debug("ACL binding callback for {}".format(str(render_tables)))
    cmd_str = ''
    if render_tables['name'] in render_tables[__name__]:
        cmd_str = __show_running_acl_binding(None, 'openconfig-acl:interface',
                                             render_tables[__name__][render_tables['name']], '')
    return 'CB_SUCCESS', cmd_str, True


def show_running_acl_global_bind_cb(render_tables):
    # log.log_debug("Show Global ACL bindings for {}".format(str(render_tables)))
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/openconfig-acl-ext:global')
    cmd_str = __show_running_acl_binding(keypath, 'openconfig-acl-ext:global', None, '')
    return 'CB_SUCCESS', cmd_str, True


def show_running_acl_ctrl_plane_bind_cb(render_tables):
    # log.log_debug("Show CtrlPlane ACL bindings for {}".format(str(render_tables)))
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/openconfig-acl-ext:control-plane')
    cmd_str = __show_running_acl_binding(keypath, 'openconfig-acl-ext:control-plane', None, ' ')
    return 'CB_SUCCESS', cmd_str, False


def show_running_config_hardware(render_tables):
    return 'CB_SUCCESS', 'hardware', True


def show_running_config_hardware_acl(render_tables):
    return 'CB_SUCCESS', 'access-list', True


def show_running_config_hardware_acl_counter_mode(render_tables):
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/config/openconfig-acl-ext:counter-capability')
    response = acl_client.get(keypath, depth=None, ignore404=False)
    if not response.ok() or not bool(response.content):
        return 'CB_SUCCESS', 'counters per-entry', False
    if response.content["openconfig-acl-ext:counter-capability"] == "openconfig-acl:AGGREGATE_ONLY":
        return 'CB_SUCCESS', 'counters per-entry', False
    else:
        return 'CB_SUCCESS', 'counters per-interface-entry', False


def show_running_config_acl_start_callback(context, cache):
    log.log_debug("ACL Context={}".format(str(context)))
    if context['view_name'] == '':
        log.log_debug("All ACLs and Interfaces config")
        __build_acl_config_cache(None, None, cache)
        __build_acl_binding_cache(None, None, cache)
    elif not bool(context['view_keys']):
        if (context['view_name'] == 'configure-if') or (context['view_name'] == 'configure-subif'):
            log.log_debug('All ethernet interfaces')
            __build_acl_binding_cache('Eth', None, cache)
        elif context['view_name'] == 'configure-vlan':
            log.log_debug('All VLAN interfaces')
            __build_acl_binding_cache('Vlan', None, cache)
        elif context['view_name'] == 'configure-lag':
            log.log_debug("All LAG interfaces")
            __build_acl_binding_cache('PortChannel', None, cache)
        elif context['view_name'] == 'configure-mac-acl':
            __build_acl_config_cache('ACL_L2', None, cache)
        elif context['view_name'] == 'configure-ipv4-acl':
            __build_acl_config_cache('ACL_IPV4', None, cache)
        elif context['view_name'] == 'configure-ipv6-acl':
            __build_acl_config_cache('ACL_IPV6', None, cache)
    elif context['view_name'] in ['configure-if', 'configure-subif', 'configure-vlan', 'configure-lag']:
        __build_acl_binding_cache(None, context['view_keys']['name'], cache)
    elif context['view_name'] == 'configure-mac-acl':
        __build_acl_config_cache('ACL_L2', context['view_keys']['access-list-name'], cache)
    elif context['view_name'] == 'configure-ipv4-acl':
        __build_acl_config_cache('ACL_IPV4', context['view_keys']['access-list-name'], cache)
    elif context['view_name'] == 'configure-ipv6-acl':
        __build_acl_config_cache('ACL_IPV6', context['view_keys']['access-list-name'], cache)


def show_running_config_line_vty_view_cb(render_tables):
    return 'CB_SUCCESS', 'line vty', True
