#!/usr/bin/python
###########################################################################
#
# Copyright 2019 Dell, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###########################################################################

import sys
import time
import json
import ast
from rpipe_utils import pipestr
import cli_client as cc
from scripts.render_cli import show_cli_output
import traceback

import urllib3
urllib3.disable_warnings()


def invoke_api(func, args=[]):
    global config

    api = cc.ApiClient()

    # Get Alias Mode
    if func == 'get_sonic_device_metadata_sonic_device_metadata_device_metadata_device_metadata_list_aliasmode':
        path = cc.Path('/restconf/data/sonic-device-metadata:sonic-device-metadata/DEVICE_METADATA/DEVICE_METADATA_LIST={name}/aliasMode', name="localhost")
        return api.get(path)

    else:
        return api.cli_not_implemented(func)

def run(func, args):

    try:
        response = invoke_api(func, args)
        if response.ok():
            if response.content is not None:
                # Get Command Output
                api_response = response.content
                if not api_response:
                    api_response = {'sonic-device-metadata:aliasMode': False}
                show_cli_output(args[0], api_response)
 
    except Exception as e:
        print("Failure: %s\n" %(e))


if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])

