#!/usr/bin/python

import syslog as log
import sys
import os
import json
import collections
import re
import cli_client as cc
import time
from scripts.render_cli import show_cli_output

def stp_mode_get():
    global g_stp_resp

    aa = cc.ApiClient()
    g_stp_resp = aa.get('/restconf/data/openconfig-spanning-tree:stp/global/config/enabled-protocol', None, False)
    if not g_stp_resp.ok():
        return 0

    if not 'openconfig-spanning-tree:enabled-protocol' in g_stp_resp.content:
        return 0

    if g_stp_resp['openconfig-spanning-tree:enabled-protocol'][0] == "openconfig-spanning-tree-ext:PVST":
        return -1
    elif g_stp_resp['openconfig-spanning-tree:enabled-protocol'][0] == "openconfig-spanning-tree-types:RAPID_PVST":
        return -1

    return 0

## Run an external command
def run_get_sonic_infra_reboot(func, argv):
    templ = argv[2]
    process_msg = True 
    if argv[1] == "null": 
       cmd=argv[0]
    else:
       cmd=argv[0] + " " + argv[1]
       if argv[1] == '-h':
          process_msg = False

    if not os.getenv('KLISH_CLI_USER'):
       data={"Param":"sudo %s" %cmd}
    else:
       user_string = "-u {}".format(os.getenv('KLISH_CLI_USER'))
       data={"Param":"sudo %s %s" %(cmd, user_string)}

    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/operations/openconfig-system-ext:reboot-ops')
    body = { "openconfig-system-ext:input":data}

    if cmd == "warm-reboot" and stp_mode_get() == -1:
        print("Error: warm-reboot not allowed as spanning-tree is enabled")
        return

    if process_msg:
       print("%s in process ....."%cmd) 

    api_response = aa.post(keypath, body)

    if process_msg:
       time.sleep(1)

    try:
        if api_response.ok():
           response = api_response.content
           if response is not None and 'openconfig-system-ext:output' in response:
              show_cli_output(templ, response['openconfig-system-ext:output']['result'])
    except Exception as e:
        log.syslog(log.LOG_ERR, str(e))
        print "%Error: Traction Failure"

def run_get_openconfig_infra_state(func, argv):
    aa = cc.ApiClient()
    templ = argv[1]
    if argv[0] == "clock":
       path = cc.Path('/restconf/data/openconfig-system:system/openconfig-system-ext:infra/state/clock')
    elif argv[0] == "uptime":
       path = cc.Path('/restconf/data/openconfig-system:system/openconfig-system-ext:infra/state/uptime')
    elif argv[0] == "reboot-cause":
       path = cc.Path('/restconf/data/openconfig-system:system/openconfig-system-ext:infra/state/reboot-cause')
    elif argv[0] == "user-list":
       path = cc.Path('/restconf/data/openconfig-system:system/openconfig-system-ext:infra/state/show-user-list')
    else:
       print "%Error: invalid state command"
    api_response = aa.get(path)
    if api_response.ok():
        if api_response.content is not None:
            response = api_response.content
            show_cli_output(templ, response)
    else:
        print api_response.error_message()

def run_get_sonic_infra_config(func, argv):
    templ = argv[1]
    process_msg = True
    cmd=argv[0]

    data={"Param":" %s" %cmd}

    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/operations/sonic-system-infra:config')
    body = { "sonic-system-infra:input":data}

    print("config %s in process ....."%cmd) 

    api_response = aa.post(keypath, body)

    try:
        if api_response.ok():
           response = api_response.content
           if response is not None and 'sonic-system-infra:output' in response:
              show_cli_output(templ, response['sonic-system-infra:output']['result'])
    except Exception as e:
        log.syslog(log.LOG_ERR, str(e))
        print "%Error: Traction Failure"


def run_set_openconfig_logger(func, argv):
    templ = argv[0]
    messages = (" ".join(argv[2:])).strip('"')
    data={"Messages":" %s" %messages}
    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/operations/openconfig-system-ext:logger')
    body = { "openconfig-system-ext:input":data}
    api_response = aa.post(keypath, body)
    try:
        if api_response.ok():
           response = api_response.content
           show_cli_output(templ, response['openconfig-system-ext:output']['result'])
    except Exception as e:
        print "%Error: Traction Failure"



def invoke(func, argv):
    if func == "get_sonic_infra_reboot":
         run_get_sonic_infra_reboot(func, argv)
    elif func == "get_openconfig_infra_state":
         run_get_openconfig_infra_state(func, argv) 
    elif func == "get_openconfig_infra_config":
         run_get_sonic_infra_config(func, argv)
    elif func == "set_openconfig_logger":
         run_set_openconfig_logger(func, argv)
    else:
         print "%Error: invalid command"


## Main function
def run(func, args):

    argv = []
    for x in args:
        if x == "\|":
            break;
        argv.append(x.rstrip("\n"))

    invoke(func.rstrip("\n"), argv)

