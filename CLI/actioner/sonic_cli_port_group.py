#!/usr/bin/python
import sys
import time
import json
import ast
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
import cli_client as cc
import requests
import re
import urllib3
import string
from collections import OrderedDict 
urllib3.disable_warnings()

def invoke(func, args):
    body = None
    resp = None
    aa = cc.ApiClient()

    if func == 'get_openconfig_port_group_port_groups_openconfig_port_group_port_groups_state':
        resp = cc.Response(requests.Response())
        resp.content = {}
        path = cc.Path('/restconf/data/openconfig-port-group:port-groups/port-group')
        rsp = aa.get(path)
        if rsp.content and 'openconfig-port-group:port-group' in rsp.content:
            for pg in rsp.content['openconfig-port-group:port-group']:
                if 'state' in pg:
                     resp.content[pg['id']] = pg['state']
                else:
                    break
        if (resp is not None) or (not resp.content) or (len(resp.content)<1):
            resp.set_error_message("Port-group is not supported")
        return resp
    else:
        speed_map = {"10GIGE":"SPEED_10GB",
                    "25GIGE":"SPEED_25GB",
                    "1GIGE":"SPEED_1GB",
                    "no": ""}

        if len(args) == 1:
            path = cc.Path('/restconf/data/openconfig-port-group:port-groups/port-group={group}/config/speed',group=args[0])
            return aa.delete(path)
        elif args[1] not in speed_map:
            return aa._make_error_response('%Error: Unsupported speed')
        else:
            path = cc.Path('/restconf/data/openconfig-port-group:port-groups/port-group')
            body = {"openconfig-port-group:port-group": [{
                       "id": args[0],
                       "config": {"openconfig-port-group:speed":  speed_map.get(args[1])}}]}
            return aa.patch(path,body)
    return None

if __name__ == '__main__':

    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])


def run(func, args):
    try:
        api_response = invoke(func, args)
        if api_response is not None:
            if api_response.content:
                if func == 'get_openconfig_port_group_port_groups_openconfig_port_group_port_groups_state':
                    show_cli_output(args[0], api_response.content)
            	elif not api_response.ok():
                    print api_response.error_message()
            elif not api_response.ok():
                print api_response.error_message()

    except Exception as ex:
        print(ex)
        print("%Error: Transaction Failure")

