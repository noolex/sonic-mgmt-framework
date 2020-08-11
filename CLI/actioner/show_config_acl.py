#!/usr/bin/python

import cli_client as cc
#from collections import OrderedDict
#from natsort import natsorted
#import sonic_cli_acl

def mac_acl_table_cb(render_tables):
    acl_client = cc.ApiClient()
    cmd_str = ''
    keypath = cc.Path('/restconf/data/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST')
    response = acl_client.get(keypath)
    content = response.content
    if 'access-list-name' in render_tables:
        for keys in content['sonic-acl:ACL_TABLE_LIST']:
            if 'type' in keys:
                if keys['type'] == 'L2' and keys['aclname'] == render_tables['access-list-name']:
                    cmd_str+='mac access-list {}'.format(keys['aclname'])
    return 'CB_SUCCESS', cmd_str, True

def ipv4_acl_table_cb(render_tables):
    acl_client = cc.ApiClient()
    cmd_str = ''
    keypath = cc.Path('/restconf/data/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST')
    response = acl_client.get(keypath)
    content = response.content
    if 'access-list-name' in render_tables:
        for keys in content['sonic-acl:ACL_TABLE_LIST']:
            if 'type' in keys:
                if keys['type'] == 'L3' and keys['aclname'] == render_tables['access-list-name']:
                    cmd_str+='ip access-list {}'.format(keys['aclname'])
    return 'CB_SUCCESS', cmd_str, True

def ipv6_acl_table_cb(render_tables):
    acl_client = cc.ApiClient()
    cmd_str = ''
    keypath = cc.Path('/restconf/data/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST')
    response = acl_client.get(keypath)
    content = response.content
    if 'access-list-name' in render_tables:
        for keys in content['sonic-acl:ACL_TABLE_LIST']:
            if 'type' in keys:
                if keys['type'] == 'L3V6' and keys['aclname'] == render_tables['access-list-name']:
                    cmd_str+='ipv6 access-list {}'.format(keys['aclname'])
    return 'CB_SUCCESS', cmd_str, True

def acl_bind_cb(render_tables):
    cmd_str = ''
    cmd_str += str(render_tables)
    return 'CB_SUCCESS', cmd_str, True

def mac_acl_rule_cb(render_tables):
    acl_client = cc.ApiClient()
    cmd_str = ''
    cmd_str += str(render_tables)
    return 'CB_SUCCESS', cmd_str, True


