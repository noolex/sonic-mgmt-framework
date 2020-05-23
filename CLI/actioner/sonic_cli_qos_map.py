#!/usr/bin/python
import sys
import time
import json
import ast
import cli_client as cc
from collections import OrderedDict
from scripts.render_cli import show_cli_output
from rpipe_utils import pipestr

def invoke(func, args=[]):
    api = cc.ApiClient()
    if func == 'get_openconfig_qos_dscp_tc_map' :
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:dscp-maps/dscp-map={name}', name=args[0])
        return api.get(path)

    if func == 'get_openconfig_qos_dot1p_tc_map' :
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:dot1p-maps/dot1p-map={name}', name=args[0])
        return api.get(path)

    return api.cli_not_implemented(func)

def run(func, args):

    response = invoke(func, args)

    if response.ok():
        if response.content is not None:
            api_response = response.content
            
            if api_response is None:
                return

            #print api_response

            if func == 'get_openconfig_qos_dscp_tc_map':
                 show_cli_output("show_qos_map.j2", api_response)
            if func == 'get_openconfig_qos_dot1p_tc_map':
                 show_cli_output("show_qos_map_dot1p.j2", api_response)

    else:
        print response.error_message()



if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])
