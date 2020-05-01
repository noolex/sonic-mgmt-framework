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
    if func == 'get_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers', name=args[0] )
        return api.get(path)
    if func == 'patch_openconfig_qos_qos_scheduler_policies_scheduler_policy':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/config', name=args[0] )
        body = {"openconfig-qos:config" : {"name": args[0]}}
        return api.patch(path, body)
    if func =="delete_openconfig_qos_qos_scheduler_policies_scheduler_policy":
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}', name=args[0] )
        return api.delete(path)
    if func == 'patch_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}', name=args[0], sequence=args[1])
        body = {}
        return api.patch(path, body)
    if func =="delete_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler":
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}', name=args[0], sequence=args[1])
        return api.delete(path)

    if func == 'patch_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_config_priority':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/config/priority', name=args[0], sequence=args[1])
        body = {"openconfig-qos:priority": "STRICT"}
        return api.patch(path, body)

    if func == 'delete_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_config_priority':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/config/priority', name=args[0], sequence=args[1])
        return api.delete(path)

    if func == 'patch_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_config_weight':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/config/openconfig-qos-ext:weight', name=args[0], sequence=args[1])
        body = {"openconfig-qos-ext:weight": int(args[2])}
        return api.patch(path, body)

    if func == 'patch_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_two_rate_three_color_config_cir':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/two-rate-three-color/config/cir', name=args[0], sequence=args[1])
        body = {"openconfig-qos:cir": args[2]}
        return api.patch(path, body)

    if func == 'patch_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_two_rate_three_color_config_pir':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/two-rate-three-color/config/pir', name=args[0], sequence=args[1])
        body = {"openconfig-qos:pir": args[2]}
        return api.patch(path, body)

    if func == 'patch_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_two_rate_three_color_config_bc':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/two-rate-three-color/config/bc', name=args[0], sequence=args[1])
        body = {"openconfig-qos:bc": int(args[2])}
        return api.patch(path, body)

    if func == 'patch_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_two_rate_three_color_config_be':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/two-rate-three-color/config/be', name=args[0], sequence=args[1])
        body = {"openconfig-qos:be": int(args[2])}
        return api.patch(path, body)

    return api.cli_not_implemented(func)


def run(func, args):

    print args
    response = invoke(func, args)

    if response.ok():
        if response.content is not None:
            api_response = response.content
            
            #print api_response
            #print sys.argv[2:]

            if func == 'get_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers':
                show_cli_output('show_qos_scheduler.j2', response)

    else:
        print response.error_message()



if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])
