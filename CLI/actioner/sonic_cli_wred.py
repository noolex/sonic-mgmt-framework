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
kb_to_bytes = 1024
def invoke(func, args=[]):
    api = cc.ApiClient()

    # Get the rules of all ECN table entries.
    if func == 'get_openconfig_qos_ext_qos_wred_profiles':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-ext:wred-profiles')
        return api.get(path)
    elif func == 'get_openconfig_qos_ext_qos_wred_profiles_wred_profile':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-ext:wred-profiles/wred-profile={name}', name=args[0])
        return api.get(path)
    elif func == 'patch_list_openconfig_qos_ext_qos_wred_profiles':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-ext:wred-profiles/')
        body = {"openconfig-qos-ext:wred-profiles" : {"wred-profile": [{ "name": args[0], "config": { "name": args[0]}}]}}
        return api.patch(path, body)
    elif func == 'patch_openconfig_qos_ext_qos_wred_profiles_wred_profile_config_green':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-ext:wred-profiles/wred-profile={name}/config', name=args[0])
        g_min_val = int(args[1]) * kb_to_bytes
        g_min_val_str = str(g_min_val)
        g_max_val = int(args[2]) * kb_to_bytes
        g_max_val_str = str(g_max_val)
        body = {"openconfig-qos-ext:config" : {"green-min-threshold" : g_min_val_str,
                                               "green-max-threshold" : g_max_val_str,
                                               "green-drop-probability" : args[3],
                                               "wred-green-enable" : True} }
        return api.patch(path, body)
    elif func == 'patch_openconfig_qos_ext_qos_wred_profiles_wred_profile_config_yellow':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-ext:wred-profiles/wred-profile={name}/config', name=args[0])
        y_min_val = int(args[1]) * kb_to_bytes
        y_min_val_str = str(y_min_val)
        y_max_val = int(args[2]) * kb_to_bytes
        y_max_val_str = str(y_max_val)
        body = {"openconfig-qos-ext:config" : {"yellow-min-threshold" : y_min_val_str,
                                               "yellow-max-threshold" : y_max_val_str,
                                               "yellow-drop-probability" : args[3],
                                               "wred-yellow-enable" : True} }
        return api.patch(path, body)
    elif func == 'patch_openconfig_qos_ext_qos_wred_profiles_wred_profile_config_red':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-ext:wred-profiles/wred-profile={name}/config', name=args[0])
        r_min_val = int(args[1]) * kb_to_bytes
        r_min_val_str = str(r_min_val)
        r_max_val = int(args[2]) * kb_to_bytes
        r_max_val_str = str(r_max_val)
        body = {"openconfig-qos-ext:config" : {"red-min-threshold" : r_min_val_str,
                                               "red-max-threshold" : r_max_val_str,
                                               "red-drop-probability" : args[3],
                                               "wred-red-enable" : True} }
        return api.patch(path, body)
    elif func == 'patch_openconfig_qos_ext_qos_wred_profiles_wred_profile_config_ecn':
        path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-ext:wred-profiles/wred-profile={name}/config/ecn', name=args[0])
        ecn = args[1].upper()
        body = { "openconfig-qos-ext:"+func[PARAM_PATCH_PREFIX_LEN:] :  ecn }
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

    try:
       response = invoke(func, args)

       if response.ok():
          if response.content is not None:
             api_response = response.content
             if api_response is None:
                print("%Error: Internal error")
             else:
                if func == 'get_openconfig_qos_ext_qos_wred_profiles_wred_profile':
                     show_cli_output(args[1], api_response)
                elif func == 'get_openconfig_qos_ext_qos_wred_profiles':
                     show_cli_output(args[0], api_response)
                else:
                     return
       else:
          print response.error_message()
    except Exception as e:
        print("% Error: Internal error: " + str(e))

if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])
