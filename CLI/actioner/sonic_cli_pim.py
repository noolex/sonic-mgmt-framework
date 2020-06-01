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

import syslog as log
import sys
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output

import urllib3
urllib3.disable_warnings()

#Define globals
inputDict = {}
apiClient = cc.ApiClient()

def get_keypath(func,args):
    keypath = None
    body = None

    return keypath, body

def process_args(args):
  global inputDict

  for arg in args:
        tmp = arg.split(":", 1)
        if not len(tmp) == 2:
            continue
        if tmp[1] == "":
            tmp[1] = None
        inputDict[tmp[0]] = tmp[1]

def run(args):
    global inputDict
    status = 0
    func=""

    process_args(args)
    print("Input dict: ", inputDict)

    # create a body block
    keypath, body = get_keypath(func, args)

    inputDict = {}
    return status

if __name__ == '__main__':
    pipestr().write(sys.argv)
    status = run(sys.argv[1:])
    if status != 0:
        sys.exit(0)
