#!/usr/bin/python
import sys
import time
import json
import ast
import cli_client as cc
from collections import OrderedDict
from scripts.render_cli import show_cli_output
from rpipe_utils import pipestr

def get_list_from_range(val_lists):
    lst = val_lists.split(',')
    lst = [sub.replace('-', '..') for sub in lst]
    new = []

    for val in lst:
       if '..' not in val:
          new.append(int(val))
       else:
          limit = val.split('..')
          for i in range(int(limit[0]),int(limit[1])+1):
             new.append(int(i))
    return new

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

    if func == 'get_openconfig_qos_maps_ext_qos_forwarding_group_dscp_maps' :
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-dscp-maps')
        return api.get(path)

    if func == 'get_openconfig_qos_maps_ext_qos_forwarding_group_dscp_maps_forwarding_group_dscp_map' :
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-dscp-maps/forwarding-group-dscp-map={name}', name=args[0])
        return api.get(path)

    if func == 'get_openconfig_qos_maps_ext_qos_forwarding_group_dot1p_maps' :
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-dot1p-maps')
        return api.get(path)

    if func == 'get_openconfig_qos_maps_ext_qos_forwarding_group_dot1p_maps_forwarding_group_dot1p_map' :
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-dot1p-maps/forwarding-group-dot1p-map={name}', name=args[0])
        return api.get(path)

    if func == 'get_openconfig_qos_maps_ext_qos_pfc_priority_maps' :
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:pfc-priority-queue-maps')
        return api.get(path)

    if func == 'get_openconfig_qos_maps_ext_qos_pfc_priority_maps_pfc_priority_map' :
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:pfc-priority-queue-maps/pfc-priority-queue-map={name}', name=args[0])
        return api.get(path)

    if func == 'patch_dscp_map_entries':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:dscp-maps/dscp-map={map_name}/dscp-map-entries', map_name=args[0])
        new = get_list_from_range(args[1])
        body={"openconfig-qos-maps-ext:dscp-map-entries": {"dscp-map-entry": [{"dscp":dscp, "config": {"fwd-group": str(args[2])}} for dscp in new]}}
        return api.patch(path, body)
    if func == 'delete_dscp_map_entries':
        new = get_list_from_range(args[1])
        for item in new:
           path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:dscp-maps/dscp-map={map_name}/dscp-map-entries/dscp-map-entry={dscp}', map_name=args[0], dscp=str(item))
           response = api.delete(path)
           if response.ok() == False:
              if response.status_code != 404:
                 print response.error_message()
        return response

    if func == 'patch_dot1p_map_entries':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:dot1p-maps/dot1p-map={map_name}/dot1p-map-entries', map_name=args[0])
        new = get_list_from_range(args[1])
        body={"openconfig-qos-maps-ext:dot1p-map-entries": {"dot1p-map-entry": [{"dot1p":dot1p, "config": {"fwd-group": str(args[2])}} for dot1p in new]}}
        return api.patch(path, body)
    if func == 'delete_dot1p_map_entries':
        new = get_list_from_range(args[1])
        for item in new:
           path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:dot1p-maps/dot1p-map={map_name}/dot1p-map-entries/dot1p-map-entry={dot1p}', map_name=args[0], dot1p=str(item))
           response = api.delete(path)
           if response.ok() == False:
              if response.status_code != 404:
                 print response.error_message()
        return response

    if func == 'patch_pfc_priority_map_entries':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:pfc-priority-queue-maps/pfc-priority-queue-map={map_name}/pfc-priority-queue-map-entries', map_name=args[0])
        new = get_list_from_range(args[1])
        body={"openconfig-qos-maps-ext:pfc-priority-queue-map-entries": {"pfc-priority-queue-map-entry": [{"dot1p":dot1p, "config": {"output-queue-index": int(args[2])}} for dot1p in new]}}
        return api.patch(path, body)

    if func == 'delete_pfc_priority_map_entries':
        new = get_list_from_range(args[1])
        for item in new:
           path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:pfc-priority-queue-maps/pfc-priority-queue-map={map_name}/pfc-priority-queue-map-entries/pfc-priority-queue-map-entry={dot1p}', map_name=args[0], dot1p=str(item))
           response = api.delete(path)
           if response.ok() == False:
              if response.status_code != 404:
                 print response.error_message()
        return response

    if func == 'patch_tc_dot1p_map_entries':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-dot1p-maps/forwarding-group-dot1p-map={map_name}/forwarding-group-dot1p-map-entries', map_name=args[0])
        new = get_list_from_range(args[1])
        body={"openconfig-qos-maps-ext:forwarding-group-dot1p-map-entries": {"forwarding-group-dot1p-map-entry": [{"fwd-group":str(fwdgrp), "config": {"dot1p": int(args[2])}} for fwdgrp in new]}}
        return api.patch(path, body)

    if func == 'delete_tc_dot1p_map_entries':
        new = get_list_from_range(args[1])
        for item in new:
           path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-dot1p-maps/forwarding-group-dot1p-map={map_name}/forwarding-group-dot1p-map-entries/forwarding-group-dot1p-map-entry={fwdgrp}', map_name=args[0], fwdgrp=str(item))
           response = api.delete(path)
           if response.ok() == False:
              if response.status_code != 404:
                 print response.error_message()
        return response

    if func == 'patch_tc_dscp_map_entries':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-dscp-maps/forwarding-group-dscp-map={map_name}/forwarding-group-dscp-map-entries', map_name=args[0])
        new = get_list_from_range(args[1])
        body={"openconfig-qos-maps-ext:forwarding-group-dscp-map-entries": {"forwarding-group-dscp-map-entry": [{"fwd-group":str(fwdgrp), "config": {"dscp": int(args[2])}} for fwdgrp in new]}}
        return api.patch(path, body)

    if func == 'delete_tc_dscp_map_entries':
        new = get_list_from_range(args[1])
        for item in new:
           path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-dscp-maps/forwarding-group-dscp-map={map_name}/forwarding-group-dscp-map-entries/forwarding-group-dscp-map-entry={fwdgrp}', map_name=args[0], fwdgrp=str(item))
           response = api.delete(path)
           if response.ok() == False:
              if response.status_code != 404:
                 print response.error_message()
        return response

    if func == 'patch_tc_pg_map_entries':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-priority-group-maps/forwarding-group-priority-group-map={map_name}/forwarding-group-priority-group-map-entries', map_name=args[0])
        new = get_list_from_range(args[1])
        body={"openconfig-qos-maps-ext:forwarding-group-priority-group-map-entries": {"forwarding-group-priority-group-map-entry": [{"fwd-group":str(fwdgrp), "config": {"priority-group-index": int(args[2])}} for fwdgrp in new]}}
        return api.patch(path, body)

    if func == 'delete_tc_pg_map_entries':
        new = get_list_from_range(args[1])
        for item in new:
           path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-priority-group-maps/forwarding-group-priority-group-map={map_name}/forwarding-group-priority-group-map-entries/forwarding-group-priority-group-map-entry={fwdgrp}', map_name=args[0], fwdgrp=str(item))
           response = api.delete(path)
           if response.ok() == False:
              if response.status_code != 404:
                 print response.error_message()
        return response

    if func == 'patch_tc_queue_map_entries':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-queue-maps/forwarding-group-queue-map={map_name}/forwarding-group-queue-map-entries', map_name=args[0])
        new = get_list_from_range(args[1])
        body={"openconfig-qos-maps-ext:forwarding-group-queue-map-entries": {"forwarding-group-queue-map-entry": [{"fwd-group":str(fwdgrp), "config": {"output-queue-index": int(args[2])}} for fwdgrp in new]}}
        return api.patch(path, body)

    if func == 'delete_tc_queue_map_entries':
        new = get_list_from_range(args[1])
        for item in new:
           path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-queue-maps/forwarding-group-queue-map={map_name}/forwarding-group-queue-map-entries/forwarding-group-queue-map-entry={fwdgrp}', map_name=args[0], fwdgrp=str(item))
           response = api.delete(path)
           if response.ok() == False:
              if response.status_code != 404:
                 print response.error_message()
        return response

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
                elif func == 'get_openconfig_qos_maps_ext_qos_forwarding_group_dscp_maps_forwarding_group_dscp_map':
                     show_cli_output(args[1], api_response)
                elif func == 'get_openconfig_qos_maps_ext_qos_forwarding_group_dscp_maps':
                     show_cli_output(args[0], api_response)
                elif func == 'get_openconfig_qos_maps_ext_qos_forwarding_group_dot1p_maps_forwarding_group_dot1p_map':
                     show_cli_output(args[1], api_response)
                elif func == 'get_openconfig_qos_maps_ext_qos_forwarding_group_dot1p_maps':
                     show_cli_output(args[0], api_response)
                elif func == 'get_openconfig_qos_maps_ext_qos_pfc_priority_maps_pfc_priority_map':
                     show_cli_output(args[1], api_response)
                elif func == 'get_openconfig_qos_maps_ext_qos_pfc_priority_maps':
                     show_cli_output(args[0], api_response)

       else:
            print response.error_message()
    except Exception as e:
        print("% Error: Internal error: " + str(e))

if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])
