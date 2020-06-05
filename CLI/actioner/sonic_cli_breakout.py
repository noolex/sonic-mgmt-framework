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
        
    elif func == 'get_openconfig_platform_port_components_component_port_breakout_mode_config':
        if len(args)<2:
            print("Not supported currently")
            interface = ""
        else:
            interface = args[1]
        path = cc.Path('/restconf/data/openconfig-platform:components/component=%s/port/openconfig-platform-port:breakout-mode/config'%interface)
        config_resp = aa.get(path)
        path = cc.Path('/restconf/data/sonic-port-breakout:sonic-port-breakout/PORT_BREAKOUT/PORT_BREAKOUT_LIST=%s/status'%interface)
        state_resp = aa.get(path)
        if config_resp.ok() and config_resp.content:
            if state_resp.ok() and state_resp.content:
                config_resp.content["openconfig-platform-port:config"].update(state_resp.content)
            else:
                config_resp.content["openconfig-platform-port:config"]["sonic-port-breakout:status"] = "Completed"
        elif state_resp.ok() and state_resp.content:
	    state_resp.content["openconfig-platform-port:config"] = OrderedDict()
       	    state_resp.content["openconfig-platform-port:config"]["sonic-port-breakout:status"]=state_resp.content.pop('sonic-port-breakout:status')
            return state_resp
        return config_resp

    else:
        interface = args[0]
        speed_map = {"4x10G":"SPEED_10GB", "1x100G":"SPEED_100GB", "1x40G":"SPEED_40GB",
                      "4x25G":"SPEED_25GB", "2x50G":"SPEED_50GB", "1x400G":"SPEED_400GB",
                      "4x100G":"SPEED_100GB", "4x50G":"SPEED_50GB", "2x100G":"SPEED_100GB", "2x200G":"SPEED_200GB"}
        path = cc.Path('/restconf/data/openconfig-platform:components/component=%s/port/openconfig-platform-port:breakout-mode/config'%interface)

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
                response = api_response.content
                if 'openconfig-platform-port:config' in response.keys():
                   value = response.pop('openconfig-platform-port:config')
                   response[args[1]] = value
                   if value is not None:
                       show_cli_output(args[0], response)
                   else:
                        print "Port not in breakout mode"
                elif 'sonic-port-breakout:output' in response.keys():
                    show_cli_output(args[0], response)
        else:
            print api_response.error_message()

    except Exception as ex:
        print(ex)
        print("%Error: Transaction Failure")

if __name__ == '__main__':

    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])
