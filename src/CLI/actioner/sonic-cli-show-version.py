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
import cli_client as cc
import urllib3
from scripts.render_cli import show_cli_output

urllib3.disable_warnings()

def run(func, args):
    aa = cc.ApiClient()

    path = cc.Path('/restconf/data/openconfig-platform:components/component=%s'%args[0])
    api_response = aa.get(path)
    if api_response.ok() and "openconfig-platform:state" in api_response.content:
        response = api_response.content
        versionResponse = response["openconfig-platform:state"]
        responseContent = {"software-version": versionResponse['software-version']}
        show_cli_output(sys.argv[3], responseContent)
        print 'RESPONSE::: '+str(responseContent)
    else:
        print api_response.error_message()


if __name__ == '__main__':

    func = sys.argv[1]
    run(func, sys.argv[2:])

