import sys
import time
import json
import ast
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output

PARAM_PATCH_PREFIX='patch_openconfig_qos_ext_qos_wred_profiles_wred_profile_config_'
PARAM_PATCH_PREFIX_LEN=len(PARAM_PATCH_PREFIX)
PARAM_DELETE_PREFIX='delete_openconfig_qos_ext_qos_wred_profiles_wred_profile_config_'
PARAM_DELETE_PREFIX_LEN=len(PARAM_DELETE_PREFIX)

def invoke(func, args=[]):
    api = cc.ApiClient()

    # Get the rules of all ECN table entries.
    if func == 'get_openconfig_qos_ext_qos_wred_profiles':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-ext:wred-profiles')
        return api.get(path)
    elif func == 'get_openconfig_qos_ext_qos_wred_profiles_wred_profile':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-ext:wred-profiles/wred-profile={name}', name=args[0])
        return api.get(path)
    elif func == 'patch_list_openconfig_qos_ext_qos_wred_profiles_wred_profile':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-ext:wred-profiles/wred-profile={name}', name=args[0])
        body = {"openconfig-qos-ext:wred-profile" : [{ "name": args[0], "config": { "name": args[0]}}]}
        return api.patch(path, body)
    elif func == 'patch_openconfig_qos_ext_qos_wred_profiles_wred_profile_config_green':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-ext:wred-profiles/wred-profile={name}/config', name=args[0])
        body = {"openconfig-qos-ext:config" : {"green_min_threshold" : args[1],
                                               "green_max_threshold" : args[2],
                                               "green_drop_rate" : args[3]} }
        return api.patch(path, body)
    elif func == 'patch_openconfig_qos_ext_qos_wred_profiles_wred_profile_config_yellow':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-ext:wred-profiles/wred-profile={name}/config', name=args[0])
        body = {"openconfig-qos-ext:config" : {"yellow_min_threshold" : args[1],
                                               "yellow_max_threshold" : args[2],
                                               "yellow_drop_rate" : args[3]} }
        return api.patch(path, body)
    elif func == 'patch_openconfig_qos_ext_qos_wred_profiles_wred_profile_config_red':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-ext:wred-profiles/wred-profile={name}/config', name=args[0])
        body = {"openconfig-qos-ext:config" : {"red_min_threshold" : args[1],
                                               "red_max_threshold" : args[2],
                                               "red_drop_rate" : args[3]} }
        return api.patch(path, body)
    elif func[0:PARAM_PATCH_PREFIX_LEN] == PARAM_PATCH_PREFIX:
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-ext:wred-profiles/wred-profile={name}/config/'+func[PARAM_PATCH_PREFIX_LEN:], name=args[0])
        body = { "openconfig-qos-ext:"+func[PARAM_PATCH_PREFIX_LEN:] :  (args[1]) }
        return api.patch(path, body)
    elif func[0:PARAM_DELETE_PREFIX_LEN] == PARAM_DELETE_PREFIX:
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-ext:wred-profiles/wred-profile={name}/config/'+func[PARAM_DELETE_PREFIX_LEN:], name=args[0])
        return api.delete(path)

    return api.cli_not_implemented(func)


def run(func, args):

    response = invoke(func, args)

    if response.ok():
        if response.content is not None:
            api_response = response.content
            
            #print api_response
            #print sys.argv[2:]

            if api_response is None:
                print("Failed")
            else:
                if func == 'get_openconfig_qos_ext_qos_wred_profiles_wred_profile':
                     show_cli_output(args[1], api_response)
                elif func == 'get_openconfig_qos_ext_qos_wred_profiles':
                     show_cli_output(args[0], api_response)
                else:
                     return

    else:
        print response.error_message()



if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])
