import sys
import time
import json
import ast
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output

PARAM_PATCH_PREFIX='patch_sonic_wred_profile_sonic_wred_profile_wred_profile_wred_profile_list_'
PARAM_PATCH_PREFIX_LEN=len(PARAM_PATCH_PREFIX)
PARAM_DELETE_PREFIX='delete_sonic_wred_profile_sonic_wred_profile_wred_profile_wred_profile_list_'
PARAM_DELETE_PREFIX_LEN=len(PARAM_DELETE_PREFIX)

def invoke(func, args=[]):
    api = cc.ApiClient()

    # Get the rules of all ECN table entries.
    if func == 'get_sonic_wred_profile_sonic_wred_profile_wred_profile':
        path = cc.Path('/restconf/data/sonic-wred-profile:sonic-wred-profile/WRED_PROFILE')
        return api.get(path)
    elif func == 'get_sonic_wred_profile_sonic_wred_profile_wred_profile_wred_profile_list':
        path = cc.Path('/restconf/data/sonic-wred-profile:sonic-wred-profile/WRED_PROFILE/WRED_PROFILE_LIST={name}', name=args[0])
        return api.get(path)
    elif func == 'patch_sonic_wred_profile_sonic_wred_profile_wred_profile_wred_profile_list':
        path = cc.Path('/restconf/data/sonic-wred-profile:sonic-wred-profile/WRED_PROFILE/WRED_PROFILE_LIST={name}', name=args[0])
        body = {"sonic-wred-profile:WRED_PROFILE_LIST" : [{"name" : args[0]}]}
        return api.patch(path, body)
    elif func == 'delete_sonic_wred_profile_sonic_wred_profile_wred_profile_wred_profile_list':
        path = cc.Path('/restconf/data/sonic-wred-profile:sonic-wred-profile/WRED_PROFILE/WRED_PROFILE_LIST={name}', name=args[0])
        return api.delete(path)
    elif func[0:PARAM_PATCH_PREFIX_LEN] == PARAM_PATCH_PREFIX:
        path = cc.Path('/restconf/data/sonic-wred-profile:sonic-wred-profile/WRED_PROFILE/WRED_PROFILE_LIST={name}/'+func[PARAM_PATCH_PREFIX_LEN:], name=args[0])
        body = { "sonic-wred-profile:"+func[PARAM_PATCH_PREFIX_LEN:] :  (args[1]) }
        return api.patch(path, body)
    elif func[0:PARAM_DELETE_PREFIX_LEN] == PARAM_DELETE_PREFIX:
        path = cc.Path('/restconf/data/sonic-wred-profile:sonic-wred-profile/WRED_PROFILE/WRED_PROFILE_LIST={name}/'+func[PARAM_DELETE_PREFIX_LEN:], name=args[0])
        return api.delete(path)

    return api.cli_not_implemented(func)


def run(func, args):

    response = invoke(func, args)

    if response.ok():
        if response.content is not None:
            api_response = response.content
            
            #print api_response
            #print sys.argv[2:]

            if 'sonic-wred-profile:WRED_PROFILE' in api_response:
                value = api_response['sonic-wred-profile:WRED_PROFILE']
                if 'WRED_PROFILE_LIST' in value:
                    tup = value['WRED_PROFILE_LIST']

            if api_response is None:
                print("Failed")
            else:
                if func == 'get_sonic_wred_profile_sonic_wred_profile_wred_profile_wred_profile_list':
                     show_cli_output(args[1], api_response)
                elif func == 'get_sonic_wred_profile_sonic_wred_profile_wred_profile':
                     show_cli_output(args[0], api_response)
                else:
                     return

    else:
        print response.error_message()



if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])
