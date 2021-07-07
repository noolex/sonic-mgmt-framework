#!/usr/bin/python
import sys
import time
import json
import ast
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
import cli_client as cc
import re
import requests
import urllib3
import string
import syslog as log
from collections import OrderedDict 
urllib3.disable_warnings()

g_err_transaction_fail = '%Error: Transaction Failure'

def invoke(func, args):
    body = None
    aa = cc.ApiClient()

    if func == 'patch_openconfig_platform_port_components_component_port_config_media_fec_mode':
        path = cc.Path('/restconf/data/openconfig-platform:components/component={name}/port/config/openconfig-port-media-fec-ext:media-fec-mode', name=(args[0]))
        body = { "openconfig-port-media-fec-ext:media-fec-mode": args[1].upper()}
        return aa.patch(path,body)

    elif func == 'delete_openconfig_platform_port_components_component_port_config_media_fec_mode':
        interface = (args[0])
        path = cc.Path('/restconf/data/openconfig-platform:components/component={port}/port/config/openconfig-port-media-fec-ext:media-fec-mode',port=interface)
        get_resp = aa.get(path)
        if get_resp.ok() and get_resp.content:
            return aa.delete(path)
        else:
            return aa._make_error_response('%Error: No change in port media-fec mode')

def run(func, args):
    try:
        api_response = invoke(func, args)
        if not api_response.ok():
            print api_response.error_message()

    except Exception as ex:
        print(ex)
        print("%Error: Transaction Failure")

if __name__ == '__main__':

    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])

def ret_err(console_err_msg, syslog_msg):
    if len(syslog_msg) != 0:
        log.syslog(log.LOG_ERR, str(syslog_msg))
    return 'CB_SUCCESS', console_err_msg

def show_running_media_fec_mode(render_tables):
    cmd_str = ''
    cmd_list = []

    if 'sonic-port:sonic-port/PORT/PORT_LIST' in render_tables:
       for db_entry in render_tables['sonic-port:sonic-port/PORT/PORT_LIST']:
           if 'index' not in db_entry.keys():
               log.syslog(log.LOG_ERR, 'key:index not found in PORT_DB, render_table = {}'.format(str(db_entry)))
               continue
           if 'media-fec-mode' not in db_entry.keys():
               continue
           cmd_list.append('interface media-fec port 1/' + str(db_entry['index']) + ' mode ' + db_entry['media-fec-mode'])
    cmd_str = ';'.join(cmd_list) 
    return 'CB_SUCCESS', cmd_str
