#!/usr/bin/python
import sys
import time
import json
import ast
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
import cli_client as cc
import re
import urllib3
import string
from collections import OrderedDict 
urllib3.disable_warnings()

def invoke(func, args):
    body = None
    aa = cc.ApiClient()

    if func == 'rpc_sonic_port_breakout_breakout_dependencies':
        interface = args[1]

        path = cc.Path('/restconf/operations/sonic-port-breakout:breakout_dependencies')
        body = {"sonic-port-breakout:input": {"ifname": interface}}
        return aa.post(path, body)
    elif func == 'rpc_sonic_port_breakout_breakout_capabilities':
        path = cc.Path('/restconf/operations/sonic-port-breakout:breakout_capabilities')
        return aa.post(path, body)
    elif func == 'get_openconfig_platform_port_components_component_port_breakout_mode_state':
        if len(args)<2:
            start = 1
            end = 74
        else:
            start = int(args[1].split("/")[1])
            end = start
        resp = OrderedDict()
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
                resp[interface] = state_resp.content.pop("openconfig-platform-port:config")
                continue
            if config_resp.content:
                resp[interface] = config_resp.content.pop("openconfig-platform-port:config")
        show_cli_output(args[0], resp)
        return config_resp

    else:
        interface = args[0]
        speed_map = {"4x10G":"SPEED_10GB", "1x100G":"SPEED_100GB", "1x40G":"SPEED_40GB",
                      "4x25G":"SPEED_25GB", "2x50G":"SPEED_50GB", "1x400G":"SPEED_400GB",
                      "4x100G":"SPEED_100GB", "4x50G":"SPEED_50GB", "2x100G":"SPEED_100GB", "2x200G":"SPEED_200GB"}
        path = cc.Path('/restconf/data/openconfig-platform:components/component={port}/port/openconfig-platform-port:breakout-mode/config',port=interface)

        if 1 == len(args):
            return aa.delete(path)
        else:
            body = {"openconfig-platform-port:config": {"num-channels": int(args[1][0]),"channel-speed": speed_map.get(args[1])}}
            return aa.patch(path,body)


def run(func, args):
    try:
        api_response = invoke(func, args)
        if api_response.ok():
            if api_response.content is not None:
                show_cli_output(args[0], api_response.content)
        else:
            print api_response.error_message()

    except Exception as ex:
        print(ex)
        print("%Error: Transaction Failure")

if __name__ == '__main__':

    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])
