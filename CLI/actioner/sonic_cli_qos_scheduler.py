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
    if func == 'get_openconfig_qos_qos_scheduler_policies':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies')
        return api.get(path)
    if func == 'get_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers', name=args[0])
        return api.get(path)

    if func == 'patch_openconfig_qos_qos_scheduler_policies':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/')
        body = {"openconfig-qos:scheduler-policies": {"scheduler-policy": [{"name": args[0], "config" : {"name": args[0]}}]}}
        return api.patch(path, body)

    if func =="delete_openconfig_qos_qos_scheduler_policies_scheduler_policy":
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}', name=args[0] )
        return api.delete(path)

    if func == 'patch_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/')
        body = {"openconfig-qos:scheduler-policies": {"scheduler-policy": [{"name": args[0], "config" : {"name": args[0]}, "schedulers": {"scheduler": [{"sequence": int(args[1])}]}}]}}
        return api.patch(path, body)

    if func =="delete_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler":
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}', name=args[0], sequence=args[1])
        return api.delete(path)

    if func == 'patch_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_config_priority':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/config/priority', name=args[0], sequence=args[1])
        body = {"openconfig-qos:priority": args[2]}
        return api.patch(path, body)

    if func == 'delete_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_config_priority':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/config/priority', name=args[0], sequence=args[1])
        return api.delete(path)

    if func == 'patch_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_config_meter_type':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/config/openconfig-qos-ext:meter-type', name=args[0], sequence=args[1])
        body = {"openconfig-qos-ext:meter-type": args[2]}
        return api.patch(path, body)

    if func == 'delete_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_config_meter_type':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/config/openconfig-qos-ext:meter-type', name=args[0], sequence=args[1])
        return api.delete(path)

    if func == 'patch_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_config_weight':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/config/openconfig-qos-ext:weight', name=args[0], sequence=args[1])
        body = {"openconfig-qos-ext:weight": int(args[2])}
        return api.patch(path, body)

    if func == 'delete_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_config_weight':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/config/openconfig-qos-ext:weight', name=args[0], sequence=args[1])
        return api.delete(path)

    if func == 'patch_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_two_rate_three_color_config_cir':
        cir_val = int(args[2]) * 1000
        cir_str = str(cir_val)
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/two-rate-three-color/config/cir', name=args[0], sequence=args[1])
        body = {"openconfig-qos:cir": cir_str}
        return api.patch(path, body)

    if func == 'patch_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_two_rate_three_color_config_cir_cpu':
        cir_val = int(args[2])
        cir_str = str(cir_val)
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/two-rate-three-color/config/cir', name=args[0], sequence=args[1])
        body = {"openconfig-qos:cir": cir_str}
        return api.patch(path, body)

    if func == 'patch_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_two_rate_three_color_config_pir':
        pir_val = int(args[2]) * 1000
        pir_str = str(pir_val)
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/two-rate-three-color/config/pir', name=args[0], sequence=args[1])
        body = {"openconfig-qos:pir": pir_str}
        return api.patch(path, body)

    if func == 'patch_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_two_rate_three_color_config_pir_cpu':
        pir_val = int(args[2])
        pir_str = str(pir_val)
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/two-rate-three-color/config/pir', name=args[0], sequence=args[1])
        body = {"openconfig-qos:pir": pir_str}
        return api.patch(path, body)

    if func == 'patch_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_two_rate_three_color_config_bc':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/two-rate-three-color/config/bc', name=args[0], sequence=args[1])
        body = {"openconfig-qos:bc": int(args[2])}
        return api.patch(path, body)

    if func == 'patch_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_two_rate_three_color_config_be':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/two-rate-three-color/config/be', name=args[0], sequence=args[1])
        body = {"openconfig-qos:be": int(args[2])}
        return api.patch(path, body)

    if func == 'delete_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_two_rate_three_color_config_cir':    
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/two-rate-three-color/config/cir', name=args[0], sequence=args[1])
        return api.delete(path)

    if func == 'delete_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_two_rate_three_color_config_pir':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/two-rate-three-color/config/pir', name=args[0], sequence=args[1])
        return api.delete(path)

    if func == 'delete_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_two_rate_three_color_config_bc':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/two-rate-three-color/config/bc', name=args[0], sequence=args[1])
        return api.delete(path)

    if func == 'delete_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers_scheduler_two_rate_three_color_config_be':
        path = cc.Path('/restconf/data/openconfig-qos:qos/scheduler-policies/scheduler-policy={name}/schedulers/scheduler={sequence}/two-rate-three-color/config/be', name=args[0], sequence=args[1])
        return api.delete(path)

    return api.cli_not_implemented(func)


def run(func, args):

    response = invoke(func, args)

    if response.ok():
        if response.content is not None:
            api_response = response.content

            #print api_response
            if func == 'get_openconfig_qos_qos_scheduler_policies_scheduler_policy_schedulers':
                show_cli_output(args[1], api_response)
            elif func == 'get_openconfig_qos_qos_scheduler_policies':
                show_cli_output(args[0], api_response)
            else:
                pass
    else:
        print response.error_message()



if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])
