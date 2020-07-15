#!/usr/bin/python
import sys
import time
import json
import ast
import cli_client as cc
from collections import OrderedDict
from scripts.render_cli import show_cli_output
from rpipe_utils import pipestr
import sonic_intf_utils as ifutils

def invoke(func, args=[]):
    api = cc.ApiClient()
    if func == 'get_openconfig_qos_qos_interfaces_interface_output_queues_queue_state':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/output/queues/queue={name}/state', interface_id=args[0], name=args[0] + ":" + str(args[1]) )
        return api.get(path)
    if func == 'get_openconfig_qos_qos_interfaces_interface_output_queues':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/output/queues', interface_id=args[0])
        return api.get(path)
    if func == 'get_openconfig_qos_ext_qos_interfaces_interface_input_priority_groups':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/input/openconfig-qos-ext:priority-groups', interface_id=args[0])
        return api.get(path)
    if func == 'get_openconfig_qos_qos_interfaces':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces')
        return api.get(path)
    if func == 'get_openconfig_qos_qos_interfaces_interface_maps':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/openconfig-qos-maps-ext:interface-maps/config', interface_id=args[0])
        return api.get(path)
    if func == 'get_list_openconfig_qos_ext_qos_threshold_breaches_breach':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-ext:threshold-breaches/breach')
        return api.get(path)
    if func == 'patch_openconfig_qos_ext_qos_queues_queue_wred_config_wred_profile':
        path = cc.Path('/restconf/data/openconfig-qos:qos/queues/')
        body = {"openconfig-qos:queues": {"queue": [{"name": args[0], "wred": {"config": {"openconfig-qos-ext:wred-profile" : args[1]}}}]}}
        return api.patch(path, body)
    if func == 'delete_openconfig_qos_ext_qos_queues_queue_wred_config_wred_profile':
        path = cc.Path('/restconf/data/openconfig-qos:qos/queues/queue={name}/wred/config/openconfig-qos-ext:wred-profile', name=args[0])
        return api.delete(path)
    if func == 'get_openconfig_qos_qos_queues_queue':
        path = cc.Path('/restconf/data/openconfig-qos:qos/queues/queue={name}', name=args[0])
        return api.get(path)
    if func == 'patch_openconfig_qos_qos_interfaces_interface_output_scheduler_policy_config_name':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/output/scheduler-policy/config/name', interface_id=args[0])
        body = {"openconfig-qos:name": args[1]}
        return api.patch(path, body)
    if func == 'delete_openconfig_qos_qos_interfaces_interface_output_scheduler_policy_config_name':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/output/scheduler-policy/config/name', interface_id=args[0])
        return api.delete(path)
    if func == 'get_openconfig_qos_qos_interface_scheduler_policy_config':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/output/scheduler-policy/config', interface_id=args[0])
        return api.get(path)
    if func == 'patch_openconfig_qos_maps_ext_qos_interfaces_interface_interface_maps_config_dscp_tc_map':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/openconfig-qos-maps-ext:interface-maps/config', interface_id=args[0])
        body = {"openconfig-qos-maps-ext:config": { "dscp-to-forwarding-group": args[1]} }
        return api.patch(path, body)
    if func == 'patch_openconfig_qos_maps_ext_qos_interfaces_interface_interface_maps_config_dot1p_tc_map':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/openconfig-qos-maps-ext:interface-maps/config', interface_id=args[0])
        body = {"openconfig-qos-maps-ext:config": { "dot1p-to-forwarding-group": args[1]} }
        return api.patch(path, body)
    if func == 'patch_openconfig_qos_ext_qos_interfaces_interface_pfc_pfc_priorities_pfc_priority_config_enable':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/openconfig-qos-ext:pfc/pfc-priorities', interface_id=args[0])
        prio = int(args[1])
        body = {"openconfig-qos-ext:pfc-priorities", {"openconfig-qos-ext:pfc-priority":[{"dot1p":prio,"config":{"dot1p":prio,"enable":True}}]}}
        return api.patch(path, body)
    if func == 'delete_openconfig_qos_ext_qos_interfaces_interface_pfc_pfc_priorities_pfc_priority_config_enable':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/openconfig-qos-ext:pfc/pfc-priorities', interface_id=args[0])
        prio = int(args[1])
        body = {"openconfig-qos-ext:pfc-priorities", {"openconfig-qos-ext:pfc-priority":[{"dot1p":prio,"config":{"dot1p":prio,"enable":False}}]}}
        return api.patch(path, body)

    if func == 'delete_openconfig_qos_ext_qos_interfaces_interface_pfc_pfc_priorities':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={intf_name}/openconfig-qos-ext:pfc/pfc-priorities', intf_name=args[0])
        return api.delete(path)

    if func == 'patch_openconfig_qos_ext_qos_interfaces_interface_pfc_config_asymmetric':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={intf_name}/openconfig-qos-ext:pfc/config/asymmetric', intf_name=args[0])
        body = {"openconfig-qos-ext:asymmetric" : True}
        return api.patch(path, body)
    if func == 'delete_openconfig_qos_ext_qos_interfaces_interface_pfc_config_asymmetric':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={intf_name}/openconfig-qos-ext:pfc/config/asymmetric', intf_name=args[0])
        return api.delete(path)
    if func == 'get_openconfig_qos_ext_qos_interfaces_interface_pfc':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/openconfig-qos-ext:pfc', interface_id=args[0])
        return api.get(path)
    if func == 'patch_openconfig_qos_maps_ext_qos_interfaces_interface_interface_maps_config_tc_queue_map':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/openconfig-qos-maps-ext:interface-maps/config', interface_id=args[0])
        body = {"openconfig-qos-maps-ext:config": { "forwarding-group-to-queue": args[1]} }
        return api.patch(path, body)
    if func == 'patch_openconfig_qos_maps_ext_qos_interfaces_interface_interface_maps_config_tc_pg_map':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/openconfig-qos-maps-ext:interface-maps/config', interface_id=args[0])
        body = {"openconfig-qos-maps-ext:config": { "forwarding-group-to-priority-group": args[1]} }
        return api.patch(path, body)
    if func == 'patch_openconfig_qos_maps_ext_qos_interfaces_interface_interface_maps_config_pfc_priority_queue_map':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/openconfig-qos-maps-ext:interface-maps/config', interface_id=args[0])
        body = {"openconfig-qos-maps-ext:config": { "pfc-priority-to-queue": args[1]} }
        return api.patch(path, body)
    if func == 'get_openconfig_qos_ext_qos_interfaces_interface_pfc_summary':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces')
        return api.get(path)
    if func == 'patch_openconfig_qos_maps_ext_qos_interfaces_interface_interface_maps_config_forwarding_group_to_dscp':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/openconfig-qos-maps-ext:interface-maps/config', interface_id=args[0])
        body = {"openconfig-qos-maps-ext:config": { "forwarding-group-to-dscp": args[1]} }
        return api.patch(path, body)
    if func == 'patch_openconfig_qos_maps_ext_qos_interfaces_interface_interface_maps_config_forwarding_group_to_dot1p':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/openconfig-qos-maps-ext:interface-maps/config', interface_id=args[0])
        body = {"openconfig-qos-maps-ext:config": { "forwarding-group-to-dot1p": args[1]} }
        return api.patch(path, body)

    return api.cli_not_implemented(func)

def getQId(item):
    name = item['name']
    if name.find(":"):
        na = name.split(':')
        naid = int(na[1])
        return naid
    return qName

def getIfId(item):
    ifName = item['interface-id']
    return ifutils.name_to_int_val(ifName)

def run(func, args):

    try:
       response = invoke(func, args)

       if response.ok():
          if response.content is not None:
             api_response = response.content

             if func == 'get_openconfig_qos_qos_interfaces_interface_output_queues_queue_state':
                if 'openconfig-qos:state' in api_response:
                   show_cli_output('show_qos_interface_queue_counters.j2', response)
             elif func == 'get_openconfig_qos_qos_interfaces_interface_output_queues':
                if 'openconfig-qos:queues' in api_response:
                    value = api_response['openconfig-qos:queues']
                    if 'queue' in value:
                        tup = value['queue']
                        value['queue'] = sorted(tup, key=getQId)
                    show_cli_output(sys.argv[3], response['openconfig-qos:queues'])
             elif func == 'get_openconfig_qos_qos_interfaces':
                if 'openconfig-qos:interfaces' in api_response:
                    value = api_response['openconfig-qos:interfaces']
                    if 'interface' in value:
                        tup = value['interface']
                        value['interface'] = sorted(tup, key=getIfId)
                for valdic in api_response['openconfig-qos:interfaces']['interface']:
                    if 'output' in valdic:
                        if 'queue' in valdic['output']['queues']:
                           tup = valdic['output']['queues']['queue']
                           valdic['output']['queues']['queue'] = sorted(tup, key=getQId)
                    elif 'input' in valdic:
                        if 'priority-group' in valdic['input']['openconfig-qos-ext:priority-groups']:
                           tup = valdic['input']['openconfig-qos-ext:priority-groups']['priority-group']
                           valdic['input']['openconfig-qos-ext:priority-groups']['priority-group'] = sorted(tup, key=getQId)
                show_cli_output(sys.argv[2], response['openconfig-qos:interfaces'])
             elif func == 'get_openconfig_qos_ext_qos_interfaces_interface_input_priority_groups':
                if 'openconfig-qos-ext:priority-groups' in api_response:
                    value = api_response['openconfig-qos-ext:priority-groups']
                    if 'priority-group' in value:
                        tup = value['priority-group']
                        value['priority-group'] = sorted(tup, key=getQId)
                    show_cli_output(sys.argv[3], response['openconfig-qos-ext:priority-groups'])
             elif func == 'get_list_openconfig_qos_ext_qos_threshold_breaches_breach':
                show_cli_output('show_qos_queue_threshold_breaches.j2', response)
             elif func == 'get_openconfig_qos_qos_queues_queue':
                show_cli_output('show_qos_queue_config.j2', response)
             elif func == 'get_openconfig_qos_qos_interface_scheduler_policy_config':
                show_cli_output('show_qos_interface_config.j2', response)
             elif func == 'get_openconfig_qos_qos_interfaces_interface_maps':
                show_cli_output('show_qos_interface_config.j2', response)
             elif func == 'get_openconfig_qos_ext_qos_interfaces_interface_pfc':
                show_cli_output('show_qos_interface_config.j2', response)
             elif func == 'get_openconfig_qos_ext_qos_interfaces_interface_pfc_summary':
                if 'openconfig-qos:interfaces' in api_response:
                    value = api_response['openconfig-qos:interfaces']
                    if 'interface' in value:
                        tup = value['interface']
                        value['interface'] = sorted(tup, key=getIfId)
                show_cli_output('show_qos_interface_pfc_summary.j2', response['openconfig-qos:interfaces'])
       else:
          if response.status_code != 404:
              print response.error_message()

    except Exception as e:
        syslog.syslog(syslog.LOG_DEBUG, "Exception: " + traceback.format_exc())
        print("%Error: Transaction Failure")
        return 1

if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])
