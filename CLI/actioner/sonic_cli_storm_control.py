#!/usr/bin/python
import sys
import time
import json
import ast
import traceback
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
import cli_client as cc


import urllib3
urllib3.disable_warnings()
plugins = dict()

def show(args):
    arg_length = len(args)
    body = None
    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/data/sonic-storm-control:sonic-storm-control/PORT_STORM_CONTROL/PORT_STORM_CONTROL_LIST')
    response = aa.get(keypath)
    if (arg_length == 1):
        show_cli_output(args[0],response)
    else:
        index = 0
        while (index <len(response['sonic-storm-control:PORT_STORM_CONTROL_LIST'])):
            iter = response['sonic-storm-control:PORT_STORM_CONTROL_LIST'][index]
            if (arg_length == 2 and (args[1] != iter['ifname'])):
                response['sonic-storm-control:PORT_STORM_CONTROL_LIST'].pop(index)
            else:
                index = index+1
        show_cli_output(args[0],response)
    return

def generate_body(func, args):
    body = None
    aa = cc.ApiClient()
    if func == 'patch_list_sonic_storm_control_sonic_storm_control_port_storm_control_port_storm_control_list':
        keypath = cc.Path('/restconf/data/sonic-storm-control:sonic-storm-control/PORT_STORM_CONTROL/PORT_STORM_CONTROL_LIST')
        #keypath = []
        body = {
                   "sonic-storm-control:PORT_STORM_CONTROL_LIST":
                   [
                       {
                           "ifname":args[0],
                           "storm_type":args[1],
                           "kbps":args[2]
                       }
                   ]
                }
        return aa.patch(keypath,body)
    elif func == 'delete_sonic_storm_control_sonic_storm_control_port_storm_control_port_storm_control_list':
        keypath = cc.Path('/restconf/data/sonic-storm-control:sonic-storm-control/PORT_STORM_CONTROL/PORT_STORM_CONTROL_LIST={ifname},{storm_type}',ifname=args[0],storm_type=args[1])
        return aa.delete(keypath)

def run(func, args):
    try:
        if func == 'get_list_sonic_storm_control_sonic_storm_control_port_storm_control_port_storm_control_list':
            show(args)
            return

        api_response = generate_body(func, args)
        response = api_response.content
        if api_response.ok():
            if response is not None:
                print ("Error: {}".format(str(response)))
        else:
            error_data = response['ietf-restconf:errors']['error'][0]
            err_msg = 'NOERROR'
            if 'error-message' in error_data:
                err_msg = error_data['error-message']
            if err_msg is not 'NOERROR':
                print (err_msg)
            else:
                print ("Error: {}".format(str(response)))
    except:
        print "%Error: Transaction Failure"
        traceback.print_exc()

if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])
