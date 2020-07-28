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
from collections import OrderedDict 
urllib3.disable_warnings()

def invoke(func, args):
    body = None
    aa = cc.ApiClient()

    if func == 'dependencies':
        interface = args[0]
        path = cc.Path('/restconf/operations/sonic-port-breakout:breakout_dependencies')
        body = {"sonic-port-breakout:input": {"ifname": interface}}
        return aa.post(path, body)
    elif func == 'modes':
        path = cc.Path('/restconf/operations/sonic-port-breakout:breakout_capabilities')
        return aa.post(path, body)
    elif func == 'patch_openconfig_platform_port_components_component_port_breakout_mode_config':
        interface = args[0]
        speed_map = {"4x10G":"SPEED_10GB", "1x100G":"SPEED_100GB", "1x40G":"SPEED_40GB",
                      "4x25G":"SPEED_25GB", "2x50G":"SPEED_50GB", "1x400G":"SPEED_400GB",
                      "4x100G":"SPEED_100GB", "4x50G":"SPEED_50GB", "2x100G":"SPEED_100GB", "2x200G":"SPEED_200GB"}
        path = cc.Path('/restconf/data/openconfig-platform:components/component={port}/port/openconfig-platform-port:breakout-mode/config',port=interface)
        body = {"openconfig-platform-port:config": {"num-channels": int(args[1][0]),"channel-speed": speed_map.get(args[1])}}
        return aa.patch(path,body)

    elif func == 'delete_openconfig_platform_port_components_component_port_breakout_mode_config':
        interface = args[0]
        path = cc.Path('/restconf/data/openconfig-platform:components/component={port}/port/openconfig-platform-port:breakout-mode/config',port=interface)
        return aa.delete(path)
    else:
        if len(args)<3:
            start = 1
            end = 74
            temp = args[1]
        else:
            start = int(args[0].split("/")[1])
            end = start
            temp = args[3]
        resp = cc.Response(requests.Response())
        resp.content = OrderedDict()

        for port in range(start, end+1):
            interface = "1/"+str(port)
            path = cc.Path('/restconf/data/openconfig-platform:components/component={port}/port/openconfig-platform-port:breakout-mode/config',port=interface)
            config_resp = aa.get(path)
            path = cc.Path('/restconf/data/openconfig-platform:components/component={port}/port/openconfig-platform-port:breakout-mode/state',port=interface)
            state_resp = aa.get(path)
            if config_resp.ok() and config_resp.content:
                if state_resp.ok() and state_resp.content:
                    config_resp.content["openconfig-platform-port:config"].update(state_resp.content.pop('openconfig-platform-port:state'))
                else:
                    config_resp.content["openconfig-platform-port:config"]["openconfig-port-breakout-ext:status"] = "Completed"
            elif state_resp.ok() and state_resp.content:
                state_resp.content["openconfig-platform-port:config"] = OrderedDict()
                state = state_resp.content.pop('openconfig-platform-port:state')
                state_resp.content["openconfig-platform-port:config"]["openconfig-port-breakout-ext:status"]=state.pop('openconfig-port-breakout-ext:status')
                state_resp.content["openconfig-platform-port:config"]["openconfig-port-breakout-ext:members"]=state.pop('openconfig-port-breakout-ext:members')
                resp.content[interface] = state_resp.content.pop("openconfig-platform-port:config")
                continue
            if config_resp.content:
                resp.content[interface] = config_resp.content.pop("openconfig-platform-port:config")
        resp.status_code = config_resp.status_code
        return resp


def run(func, args):
    try:
        api_response = invoke(func, args)
        if api_response.ok():
            if api_response.content is not None:
                if func == 'dependencies':
                    temp = args[1]
                elif func == 'modes':
                    temp = args[1]
                elif len(args) > 3:
                   temp = args[3]
                else:
                   temp = args[1]

                show_cli_output(temp, api_response.content)
        else:
            print api_response.error_message()

    except Exception as ex:
        print(ex)
        print("%Error: Transaction Failure")

if __name__ == '__main__':

    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])
