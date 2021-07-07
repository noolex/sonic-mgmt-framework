#!/usr/bin/python
import sys
import time
import json
import ast
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
import cli_client as cc
import re
import requests
import urllib3
import string
from collections import OrderedDict 
urllib3.disable_warnings()

def invoke(func, args):
    body = None
    aa = cc.ApiClient()

    if func == 'patch_openconfig_platform_port_components_component_port_breakout_mode_config':
        path = cc.Path('/restconf/data/openconfig-platform:components/component={name}/port/config/openconfig-port-media-fec-ext:media-fec-mode', name=args[0])
        body = { "openconfig-port-media-fec-ext:media-fec-mode": args[1]}
        print("path %s body %s"%(str(path), str(body)))
        return aa.patch(path,body)

    elif func == 'delete_openconfig_platform_port_components_component_port_config_media_fec_mode':
        interface = args[0]
        path = cc.Path('/restconf/data/openconfig-platform:components/component={port}/port/config/openconfig-port-media-fec-ext:media-fec-mode',port=interface)
        get_resp = aa.get(path)
        if get_resp.ok() and get_resp.content:
            return aa.delete(path)
        else:
            return aa._make_error_response('%Error: No change in port media-fec mode')

def run(func, args):
    try:
        api_response = invoke(func, args)
        print str(api_response.content)
        if not api_response.ok():
            print api_response.error_message()

    except Exception as ex:
        print(ex)
        print("%Error: Transaction Failure")

if __name__ == '__main__':

    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])
