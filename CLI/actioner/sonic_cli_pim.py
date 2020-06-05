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
    path_prefix = '/restconf/data/openconfig-network-instance:network-instances/network-instance='
    intf = ""
    vrf = ""

    #patch global config
    if func == 'patch_pim_global_config':
        #get vrf, needed for keypath
        vrf = inputDict.get('vrf')
        if vrf == None or vrf == "":
            vrf = "default"

        #generate keypath
        path = path_prefix + vrf + '/protocols/protocol=PIM,pim/pim/global'
        keypath = cc.Path(path)

        #generate body based on the input
        if inputDict.get('jpi') is not None:
            body = {"openconfig-network-instance:global": {"openconfig-pim-ext:config": {"join-prune-interval": float(inputDict.get('jpi'))}}}
        elif inputDict.get('kat') is not None:
            body = {"openconfig-network-instance:global": {"openconfig-pim-ext:config": {"keep-alive-timer": float(inputDict.get('kat'))}}}
        elif inputDict.get('pln') is not None:
            body = {"openconfig-network-instance:global": {"ssm": {"config": {"ssm-ranges": inputDict.get('pln')}}}}
        elif inputDict.get('ecmp') is not None:
            body = {"openconfig-network-instance:global": {"openconfig-pim-ext:config": {"ecmp-enabled": True}}}
        elif inputDict.get('rebalance') is not None:
            body = {"openconfig-network-instance:global": {"openconfig-pim-ext:config": {"ecmp-rebalance-enabled": True}}}

    #del global config
    if func == 'del_pim_global_config':
        #get vrf, needed for keypath
        vrf = inputDict.get('vrf')
        if vrf == None or vrf == "":
            vrf = "default"

        #generate keypath
        path = path_prefix + vrf + '/protocols/protocol=PIM,pim/pim/global'

        #generate del request based on the input
        if inputDict.get('jpi') is not None:
            path = path + "/openconfig-pim-ext:config/join-prune-interval"
        elif inputDict.get('kat') is not None:
            path = path + "/openconfig-pim-ext:config/keep-alive-timer"
        elif inputDict.get('pln') is not None:
            path = path + "/ssm/config/ssm-ranges"
        elif inputDict.get('ecmp') is not None:
            path = path + "openconfig-pim-ext:config/ecmp-enabled"
        elif inputDict.get('kat') is not None:
            path = path + "openconfig-pim-ext:config/ecmp-rebalance-enabled"

        keypath = cc.Path(path)

    #interface level config common code
    if func.startswith('patch_pim_interface'):
        #get interface, needed for VRF lookup and keypath
        intf = inputDict.get('intf')
        if intf is None:
            return None, None

        #get vrf, needed for keypath
        vrf=get_vrf(intf)

    #patch/delete interface level config
    if func.endswith('config_mode'):
        path = path_prefix + vrf + '/protocols/protocol=PIM,pim/pim/interfaces/interface=' + intf + '/config/mode'
        keypath = cc.Path(path)
        if func.startswith('patch'):
            body ={"mode": "PIM_MODE_SPARSE"}

    if func.endswith('config_drprio'):
        path = path_prefix + vrf + '/protocols/protocol=PIM,pim/pim/interfaces/interface=' + intf + '/config/mode'
        keypath = cc.Path(path)
        if func.startswith('patch'):
            body = {"dr-priority": float(inputDict.get('drprio'))}

    if func.endswith('config_hello'):
        path = path_prefix + vrf + '/protocols/protocol=PIM,pim/pim/interfaces/interface=' + intf + '/config/mode'
        keypath = cc.Path(path)
        if func.startswith('patch'):
            body = {"hello-interval": float(inputDict.get('hello'))}

    if func.endswith('config_bfd'):
        path = path_prefix + vrf + '/protocols/protocol=PIM,pim/pim/interfaces/interface=' + intf + '/config/mode'
        keypath = cc.Path(path)
        if func.startswith('patch'):
            body = {"bfd-enabled": True}

    return keypath, body

def get_vrf(intf):
    request = ''

    if intf.startswith('Ethernet'):
        request = '/restconf/data/sonic-interface:sonic-interface/INTERFACE/INTERFACE_LIST=' + intf + '/vrf_name'
    elif intf.startswith('Vlan'):
        request = '/restconf/data/sonic-vlan-interface:sonic-vlan-interface/VLAN_INTERFACE/VLAN_INTERFACE_LIST=' + intf + '/vrf_name'
    elif intf.startswith('PortChannel'):
        request =  '/restconf/data/sonic-portchannel-interface:sonic-portchannel-interface/PORTCHANNEL_INTERFACE/PORTCHANNEL_INTERFACE_LIST=' + intf + '/vrf_name'
    else:
        return 'default'

    keypath = cc.Path(request)

    try:
        response = apiClient.get(keypath)
        if response is  None:
            return 'default'

        response = response.content
        if response is  None:
            return 'default'

        vrf = response.get('sonic-interface:vrf_name')
        if vrf is None or vrf == '':
            return 'default'
        return vrf

    except Exception as e:
        log.syslog(log.LOG_ERR, str(e))
        print "% Error: Internal error"

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

    if func.startswith("patch"):
        apiClient.patch(keypath, body)
    if func.startswith("del"):
        apiClient.delete(keypath)

    return 0

if __name__ == '__main__':
    pipestr().write(sys.argv)
    status = run(sys.argv[1], sys.argv[2:])
    inputDict = {}
    if status != 0:
        sys.exit(0)
