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
    if func == 'get_openconfig_qos_qos_interfaces_interface_output_queues_queue_state':
        path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/output/queues/queue={name}/state', interface_id=args[0], name=args[1] )
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
    if func == 'get_list_openconfig_qos_ext_qos_threshold_breaches_breach':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-ext:threshold-breaches/breach')
        return api.get(path)
    if func == 'patch_openconfig_qos_ext_qos_queues_queue_wred_config_wred_profile':
        path = cc.Path('/restconf/data/openconfig-qos:qos/queues/queue={name}/wred/config/openconfig-qos-ext:wred-profile', name=args[0])
        body = {"openconfig-qos-ext:wred-profile" : args[1]}
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

    return api.cli_not_implemented(func)


def run(func, args):

    response = invoke(func, args)

    if response.ok():
        if response.content is not None:
            api_response = response.content
            
            #print api_response
            #print sys.argv[2:]

            if func == 'get_openconfig_qos_qos_interfaces_interface_output_queues_queue_state':
                show_cli_output('show_qos_interface_queue_counters.j2', response)
            elif func == 'get_openconfig_qos_qos_interfaces_interface_output_queues':
                show_cli_output(sys.argv[3], response['openconfig-qos:queues'])
            elif func == 'get_openconfig_qos_qos_interfaces':
                show_cli_output(sys.argv[2], response['openconfig-qos:interfaces'])
            elif func == 'get_openconfig_qos_ext_qos_interfaces_interface_input_priority_groups':
                show_cli_output(sys.argv[3], response['openconfig-qos-ext:priority-groups'])
            elif func == 'get_list_openconfig_qos_ext_qos_threshold_breaches_breach':
                show_cli_output('show_qos_queue_threshold_breaches.j2', response)
            elif func == 'get_openconfig_qos_qos_queues_queue':
                show_cli_output('show_qos_queue_config.j2', response)
            elif func == 'get_openconfig_qos_qos_interface_scheduler_policy_config':
                show_cli_output('show_qos_interface_config.j2', response)

    else:
        print response.error_message()



if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])
