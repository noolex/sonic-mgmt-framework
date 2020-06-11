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
    if func == 'get_openconfig_qos_maps_ext_qos_dscp_maps' :
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:dscp-maps')
        return api.get(path)

    if func == 'get_openconfig_qos_maps_ext_qos_dscp_maps_dscp_map' :
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:dscp-maps/dscp-map={name}', name=args[0])
        return api.get(path)

    if func == 'get_openconfig_qos_maps_ext_qos_dot1p_maps' :
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:dot1p-maps')
        return api.get(path)

    if func == 'get_openconfig_qos_maps_ext_qos_dot1p_maps_dot1p_map' :
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:dot1p-maps/dot1p-map={name}', name=args[0])
        return api.get(path)

    if func == 'get_openconfig_qos_maps_ext_qos_tc_queue_maps' :
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-queue-maps')
        return api.get(path)

    if func == 'get_openconfig_qos_maps_ext_qos_tc_queue_maps_tc_queue_map' :
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-queue-maps/forwarding-group-queue-map={name}', name=args[0])
        return api.get(path)

    if func == 'get_openconfig_qos_maps_ext_qos_tc_pg_maps' :
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-priority-group-maps')
        return api.get(path)

    if func == 'get_openconfig_qos_maps_ext_qos_tc_pg_maps_tc_pg_map' :
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-priority-group-maps/forwarding-group-priority-group-map={name}', name=args[0])
        return api.get(path)

    return api.cli_not_implemented(func)

def run(func, args):

    try:
       response = invoke(func, args)

       if response.ok():
          if response.content is not None:
             api_response = response.content

             if api_response is None:
                print("%Error: Internal error")
             else:
                if func == 'get_openconfig_qos_maps_ext_qos_dscp_maps_dscp_map':
                     show_cli_output(args[1], api_response)
                elif func == 'get_openconfig_qos_maps_ext_qos_dscp_maps':
                     show_cli_output(args[0], api_response)
                elif func == 'get_openconfig_qos_maps_ext_qos_dot1p_maps_dot1p_map':
                     show_cli_output(args[1], api_response)
                elif func == 'get_openconfig_qos_maps_ext_qos_dot1p_maps':
                     show_cli_output(args[0], api_response)
                elif func == 'get_openconfig_qos_maps_ext_qos_tc_queue_maps_tc_queue_map':
                     show_cli_output(args[1], api_response)
                elif func == 'get_openconfig_qos_maps_ext_qos_tc_queue_maps':
                     show_cli_output(args[0], api_response)
                elif func == 'get_openconfig_qos_maps_ext_qos_tc_pg_maps_tc_pg_map':
                     show_cli_output(args[1], api_response)
                elif func == 'get_openconfig_qos_maps_ext_qos_tc_pg_maps':
                     show_cli_output(args[0], api_response)

       else:
            print response.error_message()
    except Exception as e:
        print("% Error: Internal error: " + str(e))

if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])
