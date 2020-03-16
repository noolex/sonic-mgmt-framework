import sys
import json
import collections
import re
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
from swsssdk import ConfigDBConnector

def invoke_api(func, args):
    body = None
    api = cc.ApiClient()

    # Set/Get the rules of all THRESHOLD_TABLE entries.
    if func == 'patch_sonic_threshold_sonic_threshold_threshold_table_threshold_table_list_threshold':
	path = cc.Path('/restconf/data/sonic-threshold:sonic-threshold/THRESHOLD_TABLE/THRESHOLD_TABLE_LIST={buffer},{threshold_buffer_type},{interface_name},{buffer_index_per_port}/threshold', buffer = args[1], threshold_buffer_type = args[3], interface_name = args[5], buffer_index_per_port = args[2] )
        body = { "sonic-threshold:threshold":  int(args[4]) }
        return api.patch(path, body)

    if func == 'delete_sonic_threshold_sonic_threshold_threshold_table_threshold_table_list_threshold':
	path = cc.Path('/restconf/data/sonic-threshold:sonic-threshold/THRESHOLD_TABLE/THRESHOLD_TABLE_LIST={buffer},{threshold_buffer_type},{interface_name},{buffer_index_per_port}/threshold', buffer = args[2], threshold_buffer_type = args[4], interface_name = args[5], buffer_index_per_port = args[3] )
	return api.delete(path)
    else:
       body = {}
    return api.cli_not_implemented(func)

def run(func, args):
    try:
         api_response = invoke_api(func, args)

         if api_response.ok():
             response = api_response.content
             if response is None:
                 pass
         else:
             #error response
             print(api_response.error_message())

    except:
             # system/network error
             raise

if __name__ == '__main__':
     pipestr().write(sys.argv)
     run(sys.argv[1], sys.argv[2:])
