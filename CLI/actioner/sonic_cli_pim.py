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

    vrfName = inputDict.get('vrf')
    if vrfName == None or vrfName == "":
        vrfName = "default"

    if func == 'patch_openconfig_pim_ext_network_instances_network_instance_protocols_protocol_pim_global_config':
        path='/restconf/data/openconfig-network-instance:network-instances/network-instance=' + vrfName + '/protocols/protocol=PIM,pim/pim/global'
        keypath = cc.Path(path)
        if inputDict.get('jpi') is not None:
            body = {"openconfig-network-instance:global": {"openconfig-pim-ext:config": { "join-prune-interval": float(inputDict.get('jpi'))}}}
        elif inputDict.get('kat') is not None:
            body = {"openconfig-network-instance:global": {"openconfig-pim-ext:config": { "keep-alive-timer": float(inputDict.get('kat'))}}}
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

def run(func, args):
    global inputDict
    status = 0

    process_args(args)

    # create a body block
    keypath, body = get_keypath(func, args)
    if keypath is None:
        print("% Error: Internal error")
        return 1

    if (func == 'patch_openconfig_pim_ext_network_instances_network_instance_protocols_protocol_pim_global_config'):
        apiClient.patch(keypath, body)

    return 0

if __name__ == '__main__':
    pipestr().write(sys.argv)
    status = run(sys.argv[1], sys.argv[2:])
    inputDict = {}
    if status != 0:
        sys.exit(0)
