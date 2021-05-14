#!/usr/bin/python

import syslog as log
import sys
import os
import json
import collections
import re
import cli_client as cc
import time
from scripts.render_cli import show_cli_output

def invoke(func, argv):
    aa = cc.ApiClient()
    if func == "show_locator_led_chassis":
         keypath = cc.Path('/restconf/operations/openconfig-system-ext:show-locator-led-chassis')
    elif func == "locator_led_chassis_on":
         keypath = cc.Path('/restconf/operations/openconfig-system-ext:locator-led-chassis-on')
    elif func == "locator_led_chassis_off":
         keypath = cc.Path('/restconf/operations/openconfig-system-ext:locator-led-chassis-off')
    else:
         print("%Error: invalid command")
    body = None
    templ=argv[0]
    api_response = aa.post(keypath, body)

    try:
        if api_response.ok():
           response = api_response.content
           if response is not None:
              show_cli_output(templ, response)

    except Exception as e:
        raise e



## Main function
def run(func, args):

    argv = []
    for x in args:
        if x == "\|":
            break;
        argv.append(x.rstrip("\n"))

    invoke(func.rstrip("\n"), argv)

