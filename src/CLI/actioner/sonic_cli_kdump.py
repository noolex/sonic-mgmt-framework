#!/usr/bin/python

import sys
import os
import json
import collections
import re
import cli_client as cc
from scripts.render_cli import show_cli_output

templ = "show_kdump.j2"

## Run an external command
def run_config_cmd(templ, data):
    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/operations/sonic-kdump:kdump-config')
    body = { "sonic-kdump:input":data}

    api_response = aa.post(keypath, body)
    if api_response.ok():
        response = api_response.content
        if response is not None and 'sonic-kdump:output' in response:
            show_cli_output(templ, response['sonic-kdump:output']['result'])
    else:
        print(api_response.error_message())

## Run an external command
def run_show_cmd(templ, data):
    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/operations/sonic-kdump:kdump-state')
    body = { "sonic-kdump:input":data}

    api_response = aa.post(keypath, body)
    if api_response.ok():
        response = api_response.content
        if response is not None and 'sonic-kdump:output' in response:
            show_cli_output(templ, response['sonic-kdump:output']['result'])
    else:
        print(api_response.error_message())

## Run a kdump 'show' command
def kdump_show_cmd(templ, cmd):
    run_show_cmd(templ, {})

## Display kdump status
def cmd_show_status(templ):
    run_show_cmd(templ, {"Param":"status"})

## Display kdump memory
def cmd_show_memory(templ):
    run_show_cmd(templ, {"Param":"memory"})

## Display kdump num_dumps
def cmd_show_num_dumps(templ):
    run_show_cmd(templ, {"Param":"num_dumps"})

## Display kdump files
def cmd_show_files(templ):
    run_show_cmd(templ, {"Param":"files"})

## Display kdump log
def cmd_show_log(templ, record, lines=None):
    if lines is None:
        run_show_cmd(templ, {"Param":"log %s" % record})
    else:
        run_show_cmd(templ, {"Param":"log %s %s" % (record, lines)})

## Enable kdump
def cmd_enable(templ):
    run_config_cmd(templ, {"Enabled":True, "Num_Dumps":0, "Memory":""})

## Disable kdump
def cmd_disable(templ):
    run_config_cmd(templ, {"Enabled":False, "Num_Dumps":0, "Memory":""})

## Set memory allocated for kdump
def cmd_set_memory(templ, memory):
    run_config_cmd(templ, {"Enabled":False, "Num_Dumps":0, "Memory":memory})

## Set max numbers of kernel core files
def cmd_set_num_dumps(templ, num_dumps):
    run_config_cmd(templ, {"Enabled":False, "Num_Dumps":num_dumps, "Memory":""})

## Handle configure command: kdump
def invoke_enable(argv):
    if len(argv) == 0:
        cmd_enable(templ)

## Handle configure command: no kdump
def invoke_disable(argv):
    if len(argv) == 0:
        cmd_disable(templ)

## Handle configure commands: no kdump [memory] [num_dumps]
def invoke_reset(argv):
    if len(argv) == 1:
        if argv[0] == "memory":
            cmd_set_memory(templ, "0M-2G:256M,2G-4G:320M,4G-8G:384M,8G-:448M")
        elif argv[0] == "num_dumps":
            cmd_set_num_dumps(templ, int(3))

## Handle configure commands: kdump [memory] [num_dumps]
def invoke_config(argv):
    if len(argv) == 2:
        if argv[0] == "memory":
            cmd_set_memory(templ, argv[1])
        elif argv[0] == "num_dumps":
            cmd_set_num_dumps(templ, int(argv[1]))

## Handle show commands: show kdump [status] [memory] [num_dumps] [files] [log]
def invoke_show(argv):
    if len(argv) == 1:
        if argv[0] == "status":
            cmd_show_status(templ)
        elif argv[0] == "memory":
            cmd_show_memory(templ)
        elif argv[0] == "num_dumps":
            cmd_show_num_dumps(templ)
        elif argv[0] == "files":
            cmd_show_files(templ)
    elif len(argv) == 2:
        if argv[0] == "log":
            cmd_show_log(templ, argv[1])
    elif len(argv) == 3:
        if argv[0] == "log":
            cmd_show_log(templ, argv[1], argv[2])

## Invoke operation to perform
def invoke(func, argv):
    if func == "enable":
        invoke_enable(argv)
    elif func == "disable":
        invoke_disable(argv)
    elif func == "reset":
        invoke_reset(argv)
    elif func == "config":
        invoke_config(argv)
    elif func == "show":
        invoke_show(argv)

## Main function
def run(func, args):

    argv = []
    for x in args:
        if x == "\|":
            break;
        argv.append(x.rstrip("\n"))

    invoke(func.rstrip("\n"), argv)
