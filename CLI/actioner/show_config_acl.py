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

def acl_bind_cb(render_tables):
    acl_client = cc.ApiClient()
    cmd_str = ''
    input_string =str(render_tables['name'])
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/interfaces/interface={intfname}', intfname=input_string)
    response = acl_client.get(keypath, depth=None, ignore404=False)

    if response.ok() is False:
        return 'CB_SUCCESS', cmd_str, True

    content = response.content

    if 'openconfig-acl:interface' not in content:
        return 'CB_SUCCESS', cmd_str, True

    for keys in content['openconfig-acl:interface']:
        #Ingress bindings
        if 'ingress-acl-sets' in keys:
            ingress_sets = content['openconfig-acl:interface'][0]['ingress-acl-sets']
            #Retrieve the number of bindings
            acl_entries = ingress_sets['ingress-acl-set']
            length = len(acl_entries)
            for type_iter in range(length):
                acl_entry = acl_entries[type_iter]
                config = acl_entry['config']
                acl_name = config['set-name']
                acl_type = config['type']
                if acl_type == 'openconfig-acl:ACL_L2':
                    cmd_str+=" mac access-group {} in".format(acl_name)
                    cmd_str+="\n"
                elif acl_type == 'openconfig-acl:ACL_IPV4':
                    cmd_str+=" ip access-group {} in".format(acl_name)
                    cmd_str+="\n"
                elif acl_type == 'openconfig-acl:ACL_IPV6':
                    cmd_str+=" ipv6 access-group {} in".format(acl_name)
                    cmd_str+="\n"
        #Egress bindings
        if 'egress-acl-sets' in keys:
            egress_sets = content['openconfig-acl:interface'][0]['egress-acl-sets']
            acl_entries = egress_sets['egress-acl-set']
            length = len(acl_entries)
            for type_iter in range(length):
                acl_entry = acl_entries[type_iter]
                config = acl_entry['config']
                acl_name = config['set-name']
                acl_type = config['type']
                if acl_type == 'openconfig-acl:ACL_L2':
                    cmd_str+=" mac access-group {} out".format(acl_name)
                    cmd_str+="\n"
                elif acl_type == 'openconfig-acl:ACL_IPV4':
                    cmd_str+=" ip access-group {} out".format(acl_name)
                    cmd_str+="\n"
                elif acl_type == 'openconfig-acl:ACL_IPV6':
                    cmd_str+=" ipv6 access-group {} out".format(acl_name)
                    cmd_str+="\n"

    return 'CB_SUCCESS', cmd_str, True

def acl_global_bind_cb(render_tables):
    acl_client = cc.ApiClient()
    cmd_str = ''
    config_present = 0
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/openconfig-acl-ext:global/ingress-acl-sets')
    response = acl_client.get(keypath, depth=10, ignore404=False)

    if response.ok() is False:
        return 'CB_SUCCESS', cmd_str, True

    content = response.content

    if 'openconfig-acl-ext:ingress-acl-sets' in content:
        acl_entries = content['openconfig-acl-ext:ingress-acl-sets']['ingress-acl-set']
        length = len(acl_entries)
        for type_iter in range(length):
            acl_entry = acl_entries[type_iter]
            config = acl_entry['config']
            acl_name = config['set-name']
            acl_type = config['type']
            config_present = 1
            if acl_type == 'openconfig-acl:ACL_L2':
                cmd_str+="mac access-group {} in".format(acl_name)
                cmd_str+="\n"
            elif acl_type == 'openconfig-acl:ACL_IPV4':
                cmd_str+="ip access-group {} in".format(acl_name)
                cmd_str+="\n"
            elif acl_type == 'openconfig-acl:ACL_IPV6':
                cmd_str+="ipv6 access-group {} in".format(acl_name)
                cmd_str+="\n"

    keypath = cc.Path('/restconf/data/openconfig-acl:acl/openconfig-acl-ext:global/egress-acl-sets')
    response = acl_client.get(keypath, None, False)

    if response.ok() is False:
        return 'CB_SUCCESS', cmd_str, True

    content = response.content
    if 'openconfig-acl-ext:egress-acl-sets' in content:
        acl_entries = content['openconfig-acl-ext:egress-acl-sets']['egress-acl-set']
        length = len(acl_entries)
        for type_iter in range(length):
            acl_entry = acl_entries[type_iter]
            config = acl_entry['config']
            acl_name = config['set-name']
            acl_type = config['type']
            config_present = 1
            if acl_type == 'openconfig-acl:ACL_L2':
                cmd_str+="mac access-group {} out".format(acl_name)
                cmd_str+="\n"
            elif acl_type == 'openconfig-acl:ACL_IPV4':
                cmd_str+="ip access-group {} out".format(acl_name)
                cmd_str+="\n"
            elif acl_type == 'openconfig-acl:ACL_IPV6':
                cmd_str+="ipv6 access-group {} out".format(acl_name)
                cmd_str+="\n"

    if config_present:
        cmd_str+="\n!\n"
    return 'CB_SUCCESS', cmd_str, True
