#!/usr/bin/python
import cli_client as cc
from collections import OrderedDict
import sonic_cli_acl
import cli_log as log


acl_client = cc.ApiClient()


def __show_running_acl(render_tables, acl_type):
    snc_acl_type = sonic_cli_acl.__convert_oc_acl_type_to_sonic_fmt(acl_type)
    log.log_debug("Tables to render are {} for type {}/{}".format(str(render_tables), acl_type, snc_acl_type))
    data = OrderedDict()
    cmd_str = ''
    acl_names = list()

    if 'access-list-name' in render_tables:
        #Retrieve the acl_name from request
        acl_names.append(render_tables['access-list-name'])
    else:
        keypath = cc.Path('/restconf/data/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST')
        response = acl_client.get(keypath, depth=None, ignore404=False)
        if not response.ok() or not bool(response.content):
            log.log_debug("No ACLs configured")
            return cmd_str

        content = response.content
        for keys in content['sonic-acl:ACL_TABLE_LIST']:
            if keys['type'] == snc_acl_type:
                acl_names.append(keys['aclname'])

    add_ex = False
    for acl_name in acl_names:
        keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set={name},{acl_type}', name=acl_name, acl_type=acl_type)
        response = acl_client.get(keypath, depth=None, ignore404=False)
        if response.ok():
            user_acl_type = sonic_cli_acl.__convert_oc_acl_type_to_user_fmt(acl_type)
            if add_ex:
                cmd_str += "\n!\n"
            cmd_str += '{} access-list {}'.format(user_acl_type, acl_name)
            add_ex = True
            for acl_set in response.content['openconfig-acl:acl-set']:
                #Convert the OCYANG format 'acl-set' to user format 'data'
                sonic_cli_acl.__convert_oc_acl_set_to_user_fmt(acl_set, data)
                acl_data = data[user_acl_type][acl_name]
                if 'description' in acl_data:
                    cmd_str+="\n remark {}".format(acl_data['description'])

                #Loop for number of rules
                for seq_num, rule in acl_data['rules'].items():
                    cmd_str += "\n"
                    rule_data = rule['rule_data']
                    #rule_data can contain integers. Convert all to list of strings
                    rule_data_str_list = [str(i) for i in rule_data]
                    cmd_str += " seq {} {}".format(seq_num, ' '.join(rule_data_str_list))
                    if 'description' in rule:
                        cmd_str += " remark {}".format(rule['description'])
    return cmd_str

def mac_acl_table_cb(render_tables):
    return 'CB_SUCCESS', __show_running_acl(render_tables, 'ACL_L2'), True

def ipv4_acl_table_cb(render_tables):
    return 'CB_SUCCESS', __show_running_acl(render_tables, 'ACL_IPV4'), True

def ipv6_acl_table_cb(render_tables):
    return 'CB_SUCCESS', __show_running_acl(render_tables, 'ACL_IPV6'), True

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

def __show_running_acl_binding(keypath, root, is_list, prefix):
    response = acl_client.get(keypath, depth=None, ignore404=False)

    if response.ok() is False:
        log.log_debug("Resp not success")
        return ''
    if root not in response.content:
        log.log_debug("Root not found in response {}".format(str(response.content)))
        return ''

    cmd_str = ''
    content = response.content
    data = content[root]
    if is_list:
        data = data[0]

    for key in ['ingress-acl-sets', 'egress-acl-sets']:
        try:
            acl_sets = data[key][key[:-1]]
            direction = 'in'
            if key.startswith('egress'):
                direction = 'out'
            cmd_str += __display_acl_bindings(acl_sets, direction, prefix)
        except KeyError:
            pass
    return cmd_str


def acl_bind_cb(render_tables):
    log.log_debug("Show ACL bindings for {}".format(str(render_tables)))
    input_string = str(render_tables['name'])
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/interfaces/interface={intfname}', intfname=input_string)
    cmd_str = __show_running_acl_binding(keypath, 'openconfig-acl:interface', True, '')
    return 'CB_SUCCESS', cmd_str, True

def acl_global_bind_cb(render_tables):
    log.log_debug("Show Global ACL bindings for {}".format(str(render_tables)))
    cmd_str = ''
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/openconfig-acl-ext:global')
    cmd_str = __show_running_acl_binding(keypath, 'openconfig-acl-ext:global', False, '')
    return 'CB_SUCCESS', cmd_str, True

def acl_ctrl_plane_bind_cb(render_tables):
    log.log_debug("Show CtrlPlane ACL bindings for {}".format(str(render_tables)))
    cmd_str = 'line vty;'
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/openconfig-acl-ext:control-plane')
    cmd_str += __show_running_acl_binding(keypath, 'openconfig-acl-ext:control-plane', False, ' ')
    return 'CB_SUCCESS', cmd_str, True

def show_running_config_hardware(render_tables):
    return 'CB_SUCCESS', 'hardware', True

def show_running_config_hardware_acl(render_tables):
    return 'CB_SUCCESS', 'access-list', True

def show_running_config_hardware_acl_counter_mode(render_tables):
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/openconfig-acl-ext:control-plane')
    response = acl_client.get(keypath, depth=None, ignore404=False)
    if not response.ok() or not bool(response.content):
        return 'CB_SUCCESS', 'counters per-entry', False
    if response.content["openconfig-acl-ext:counter-capability"] == "openconfig-acl:AGGREGATE_ONLY":
        return 'CB_SUCCESS', 'counters per-entry', False
    else:
        return 'CB_SUCCESS', 'counters per-interface-entry', False

