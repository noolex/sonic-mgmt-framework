#!/usr/bin/python

import cli_client as cc
from collections import OrderedDict
#from natsort import natsorted
import sonic_cli_acl

def mac_acl_table_cb(render_tables):
    acl_client = cc.ApiClient()
    data = OrderedDict()
    cmd_str = ''
    keypath = cc.Path('/restconf/data/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST')
    response = acl_client.get(keypath)

    if response.ok() is False:
        return 'CB_SUCCESS', cmd_str, True

    content = response.content
    acl_type='ACL_L2'
    acl_exists = 0

    #Retrieve the acl_name from request
    input_str = render_tables['access-list-name']

    if 'access-list-name' in render_tables:
        for keys in content['sonic-acl:ACL_TABLE_LIST']:
            if 'type' in keys:
                if keys['type'] == 'L2' and keys['aclname'] == render_tables['access-list-name']:
                    cmd_str+='mac access-list {}'.format(keys['aclname'])
                    acl_exists=1

    #Proceed only for the access-list received in render_tables
    if not acl_exists:
        return 'CB_SUCCESS', cmd_str, True

    #Retrieve the complete ACL SET 
    #keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/')
    #Retrieve acl-set corresponding to the ACL name and type
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set={name},{acl_type}', name=input_str, acl_type=acl_type)
    response = acl_client.get(keypath)

    if response.ok() is False:
        return 'CB_SUCCESS', cmd_str, True

    content = response.content
    #for acl_set in content['openconfig-acl:acl-sets']['acl-set']:
    for acl_set in content['openconfig-acl:acl-set']:
        if acl_set['type'] != 'openconfig-acl:ACL_L2':
            continue
        #Convert the OCYANG format 'acl-set' to user format 'data'
        sonic_cli_acl.__convert_oc_acl_set_to_user_fmt(acl_set, data)

    #Proceed for L2 data
    if 'mac' in data:
        for acl_name_data in data['mac']:
            #Proceed for the acl_name in request
            if acl_name_data == input_str:
                rules = data['mac'][str(acl_name_data)]
                if 'description' in rules:
                    cmd_str+="\n remark {}".format(rules['description'])
                num_rules = len(rules['rules'])
                seq_num_list=[]
                #Store sequence numbers in a list
                for rule in rules['rules']:
                    seq_num_list.append(rule)
                #Loop for number of rules    
                for rule_iter in range(num_rules):
                    cmd_str+="\n"
                    seq_num = seq_num_list[rule_iter]
                    rule = rules['rules'][seq_num]
                    rule_data = rule['rule_data']
                    #rule_data can contain integers. Convert all to list of strings
                    rule_data_str_list = [str(i) for i in rule_data]
                    cmd_str+=" seq {} ".format(seq_num)
                    cmd_str+=' '.join(rule_data_str_list)
                    if 'description' in rule:
                        cmd_str+=" remark {}".format(rule['description'])

    return 'CB_SUCCESS', cmd_str, True

def ipv4_acl_table_cb(render_tables):
    acl_client = cc.ApiClient()
    data = OrderedDict()
    cmd_str = ''
    keypath = cc.Path('/restconf/data/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST')
    response = acl_client.get(keypath)

    if response.ok() is False:
        return 'CB_SUCCESS', cmd_str, True

    content = response.content
    acl_type='ACL_IPV4'
    acl_exists = 0

    #Retrieve the acl_name from request
    input_str = render_tables['access-list-name']

    if 'access-list-name' in render_tables:
        for keys in content['sonic-acl:ACL_TABLE_LIST']:
            if 'type' in keys:
                if keys['type'] == 'L3' and keys['aclname'] == render_tables['access-list-name']:
                    cmd_str+='ip access-list {}'.format(keys['aclname'])
                    acl_exists=1

    #Proceed only for the access-list received in render_tables
    if not acl_exists:
        return 'CB_SUCCESS', cmd_str, True

    #Retrieve the complete ACL SET 
    #keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/')
    #Retrieve acl-set corresponding to the ACL name and type
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set={name},{acl_type}', name=input_str, acl_type=acl_type)
    response = acl_client.get(keypath)

    if response.ok() is False:
        return 'CB_SUCCESS', cmd_str, True

    content = response.content
    #for acl_set in content['openconfig-acl:acl-sets']['acl-set']:
    for acl_set in content['openconfig-acl:acl-set']:
        if acl_set['type'] != 'openconfig-acl:ACL_IPV4':
            continue
        #Convert the OCYANG format 'acl-set' to user format 'data'
        sonic_cli_acl.__convert_oc_acl_set_to_user_fmt(acl_set, data)

    #Proceed for IPV4 data
    if 'ip' in data:
        for acl_name_data in data['ip']:
            #Proceed for the acl_name in request
            if acl_name_data == input_str:
                rules = data['ip'][str(acl_name_data)]
                if 'description' in rules:
                    cmd_str+="\n remark {}".format(rules['description'])
                num_rules = len(rules['rules'])
                seq_num_list=[]
                #Store sequence numbers in a list
                for rule in rules['rules']:
                    seq_num_list.append(rule)
                #Loop for number of rules    
                for rule_iter in range(num_rules):
                    cmd_str+="\n"
                    seq_num = seq_num_list[rule_iter]
                    rule = rules['rules'][seq_num]
                    rule_data = rule['rule_data']
                    #rule_data can contain integers. Convert all to list of strings
                    rule_data_str_list = [str(i) for i in rule_data]
                    cmd_str+=" seq {} ".format(seq_num)
                    cmd_str+=' '.join(rule_data_str_list)
                    if 'description' in rule:
                        cmd_str+=" remark {}".format(rule['description'])

    return 'CB_SUCCESS', cmd_str, True

def ipv6_acl_table_cb(render_tables):
    acl_client = cc.ApiClient()
    data = OrderedDict()
    cmd_str = ''
    keypath = cc.Path('/restconf/data/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST')
    response = acl_client.get(keypath)

    if response.ok() is False:
        return 'CB_SUCCESS', cmd_str, True

    content = response.content
    acl_type='ACL_IPV6'
    acl_exists = 0

    #Retrieve the acl_name from request
    input_str = render_tables['access-list-name']

    if 'access-list-name' in render_tables:
        for keys in content['sonic-acl:ACL_TABLE_LIST']:
            if 'type' in keys:
                if keys['type'] == 'L3V6' and keys['aclname'] == render_tables['access-list-name']:
                    cmd_str+='ipv6 access-list {}'.format(keys['aclname'])
                    acl_exists=1

    #Proceed only for the access-list received in render_tables
    if not acl_exists:
        return 'CB_SUCCESS', cmd_str, True

    #Retrieve the complete ACL SET 
    #keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/')
    #Retrieve acl-set corresponding to the ACL name and type
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/acl-sets/acl-set={name},{acl_type}', name=input_str, acl_type=acl_type)
    response = acl_client.get(keypath)

    if response.ok() is False:
        return 'CB_SUCCESS', cmd_str, True

    content = response.content
    #for acl_set in content['openconfig-acl:acl-sets']['acl-set']:
    for acl_set in content['openconfig-acl:acl-set']:
        if acl_set['type'] != 'openconfig-acl:ACL_IPV6':
            continue
        #Convert the OCYANG format 'acl-set' to user format 'data'
        sonic_cli_acl.__convert_oc_acl_set_to_user_fmt(acl_set, data)

    #Proceed for IPV6 data
    if 'ipv6' in data:
        for acl_name_data in data['ipv6']:
            #Proceed for the acl_name in request
            if acl_name_data == input_str:
                rules = data['ipv6'][str(acl_name_data)]
                if 'description' in rules:
                    cmd_str+="\n remark {}".format(rules['description'])
                num_rules = len(rules['rules'])
                seq_num_list=[]
                #Store sequence numbers in a list
                for rule in rules['rules']:
                    seq_num_list.append(rule)
                #Loop for number of rules    
                for rule_iter in range(num_rules):
                    cmd_str+="\n"
                    seq_num = seq_num_list[rule_iter]
                    rule = rules['rules'][seq_num]
                    rule_data = rule['rule_data']
                    #rule_data can contain integers. Convert all to list of strings
                    rule_data_str_list = [str(i) for i in rule_data]
                    cmd_str+=" seq {} ".format(seq_num)
                    cmd_str+=' '.join(rule_data_str_list)
                    if 'description' in rule:
                        cmd_str+=" remark {}".format(rule['description'])

    return 'CB_SUCCESS', cmd_str, True

def acl_bind_cb(render_tables):
    acl_client = cc.ApiClient()
    cmd_str = ''
    input_string =str(render_tables['name'])
    keypath = cc.Path('/restconf/data/openconfig-acl:acl/interfaces/interface={intfname}',intfname=input_string)
    #keypath = cc.Path('/restconf/data/sonic-acl:sonic-acl/ACL_BINDING_TABLE/ACL_BINDING_TABLE_LIST')
    #keypath = cc.Path('/restconf/data/sonic-acl:sonic-acl/ACL_BINDING_TABLE/ACL_BINDING_TABLE_LIST={intfname},{stage}',intfname=input_string,stage='INGRESS')
    response = acl_client.get(keypath)

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
    response = acl_client.get(keypath)

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
    response = acl_client.get(keypath)

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
