#!/usr/bin/python

import syslog as log
import sys
import os
import json
import collections
import re
import cli_client as cc
from scripts.render_cli import show_cli_output

def stp_mode_get():
    global g_stp_resp

    aa = cc.ApiClient()
    g_stp_resp = aa.get('/restconf/data/openconfig-spanning-tree:stp/global/config/enabled-protocol', None)
    if not g_stp_resp.ok():
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

    data={"Param":"sudo %s" %cmd}

    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/operations/sonic-system-infra:reboot-ops')
    body = { "sonic-system-infra:input":data}

    if cmd == "warm-reboot" and stp_mode_get() == -1:
        print("Error: warm-reboot not allowed as spanning-tree is enabled")
        return

    if process_msg:
       print("%s in process ....."%cmd) 

    api_response = aa.post(keypath, body)

    try:
        if api_response.ok():
           response = api_response.content
           if response is not None and 'sonic-system-infra:output' in response:
              show_cli_output(templ, response['sonic-system-infra:output']['result'])
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
    else:
       print "%Error: invalid state command"
    api_response = aa.get(path)
    if api_response.ok():
        if api_response.content is not None:
            response = api_response.content
            show_cli_output(templ, response)


def invoke(func, argv):
    if func == "get_sonic_infra_reboot":
         run_get_sonic_infra_reboot(func, argv)
    elif func == "get_openconfig_infra_state":
         run_get_openconfig_infra_state(func, argv) 
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

