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
import cli_client as cc
import urllib3
from render_cli import show_cli_output
from collections import OrderedDict
from struct import unpack
from base64 import b64decode
import sonic_intf_utils as ifutils

urllib3.disable_warnings()

PSU_CNT = 2
PSU_FAN_CNT = 1
FAN_CNT = 10

def convert4BytesToStr(b):
    return unpack('>f', b64decode(b))[0]

def decodePsuStats(psu):
    if 'power-supply' not in psu or 'state' not in psu['power-supply']:
        return
    if 'openconfig-platform-psu:output-current' in psu['power-supply']['state']:
        psu['power-supply']['state']['openconfig-platform-psu:output-current'] = \
            convert4BytesToStr(psu['power-supply']['state']['openconfig-platform-psu:output-current'])
    if 'openconfig-platform-psu:output-power' in psu['power-supply']['state']:
        psu['power-supply']['state']['openconfig-platform-psu:output-power'] = \
            convert4BytesToStr(psu['power-supply']['state']['openconfig-platform-psu:output-power'])
    if 'openconfig-platform-psu:output-voltage' in psu['power-supply']['state']:
        psu['power-supply']['state']['openconfig-platform-psu:output-voltage'] = \
            convert4BytesToStr(psu['power-supply']['state']['openconfig-platform-psu:output-voltage'])

def run(func, args):
    aa = cc.ApiClient()
    template = sys.argv[3]
    response = None
    try:
        if func == 'get_openconfig_platform_components_component':
            path = cc.Path('/restconf/data/openconfig-platform:components/component=%s'%args[0])
            response = aa.get(path)
            if response.ok():
                show_cli_output(template, response.content)
            else:
                print response.error_message()
                return
        elif (func == 'get_openconfig_platform_components_component_psu_status' or
            func == 'get_openconfig_platform_components_component_psu_summary'):
            template = sys.argv[2]
            psuInfo = OrderedDict()
            for i in range(1, PSU_CNT + 1):
                path = cc.Path('/restconf/data/openconfig-platform:components/component=PSU %s'%i)
                response = aa.get(path)
                if not response.ok():
                    print response.error_message()
                    return
                if (len(response.content) == 0 or
                    not ('openconfig-platform:component' in response.content) or
                    len(response.content['openconfig-platform:component']) == 0 or
                    not ('name' in response.content['openconfig-platform:component'][0])):
                    continue
                psuName = response.content['openconfig-platform:component'][0]['name']
                psuInfo[psuName] = response.content['openconfig-platform:component'][0]
                decodePsuStats(psuInfo[psuName])
                for j in range(1, PSU_FAN_CNT + 1):
                    path = cc.Path('/restconf/data/openconfig-platform:components/component=PSU {} FAN {}'.format(i, j))
                    response = aa.get(path)
                    if not response.ok():
                        print response.error_message()
                        return
                    if (len(response.content) == 0 or
                        not ('openconfig-platform:component' in response.content) or
                        len(response.content['openconfig-platform:component']) == 0 or
                        not ('name' in response.content['openconfig-platform:component'][0])):
                        continue
                    fanName = response.content['openconfig-platform:component'][0]['name']
                    psuInfo[psuName][fanName] = response.content['openconfig-platform:component'][0]
            show_cli_output(template, psuInfo)
        elif func == 'get_openconfig_platform_components_component_fan_status':
            template = sys.argv[2]
            fanInfo = OrderedDict()
            for i in range(1, FAN_CNT + 1):
                path = cc.Path('/restconf/data/openconfig-platform:components/component=FAN %s'%i)
                response = aa.get(path)
                if not response.ok():
                    print response.error_message()
                    return
                if (len(response.content) == 0 or
                    not ('openconfig-platform:component' in response.content) or
                    len(response.content['openconfig-platform:component']) == 0 or
                    not ('name' in response.content['openconfig-platform:component'][0])):
                    continue
                fanName = response.content['openconfig-platform:component'][0]['name']
                fanInfo[fanName] = response.content['openconfig-platform:component'][0]
            show_cli_output(template, fanInfo)
        elif func == 'get_openconfig_platform_components_component_transceiver_status':
            if_name = sys.argv[2]
            template = sys.argv[3]
            xcvrInfo = OrderedDict()
            summary = False
            if_list = []

            if if_name in ["Ethernet_SUMMARY", "Ethernet_ALL"]:
                summary = (True if (if_name == "Ethernet_SUMMARY") else False)
                # Get list of ports
                path = cc.Path('/restconf/data/sonic-port:sonic-port/PORT/PORT_LIST')
                response = aa.get(path)
                if not response.ok():
                    print(response.content)
                    return
                try:
                    for d in response.content['sonic-port:PORT_LIST']:
                        if_list.append(d['ifname'])
                except:
                    return
            else:
                # Singleton
                if_list.append(if_name)

            for nm in if_list:
                n = nm
                if '/' in nm:
                    n = nm.replace('/', '%2F')
                path = cc.Path('/restconf/data/openconfig-platform:components/component=' + n)
                response = aa.get(path)
                try:
                    xcvrInfo[nm] = response.content['openconfig-platform:component'][0]
                except:
                    xcvrInfo[nm] = {}

            # Clean up the data
            cli_dict = OrderedDict()
            for val in sorted(xcvrInfo.keys(),  key=lambda x: ifutils.name_to_int_val(x)):
                d2 = OrderedDict()
                try:
                    d = xcvrInfo[val]['openconfig-platform-transceiver:transceiver']['state']
                    for k  in d:
                        a = k
                        b = d[k]
                        if ':' in k:
                            a = k.split(':')[1]
                        if ':' in d[k]:
                            b = d[k].split(':')[1]
                        if a in ['connector-type', 'form-factor']:
                            b = b.replace('_CONNECTOR', '')
                            b = b.replace('_PLUS', '+')
                            b = b.replace('_', '-')

                        d2[a] = b
                except:
                    d2.update( {'present':'NOT-PRESENT' })
                cli_dict[val] = (val,d2)
            try:
                if summary:
                    show_cli_output(template, (True, cli_dict))
                else:
                    for k in cli_dict:
                        show_cli_output(template, (False, cli_dict[k]))
            except Exception as e:
                pass
    except Exception as e:
        print("%Error: Transaction Failure")
        return

if __name__ == '__main__':

    func = sys.argv[1]
    run(func, sys.argv[2:])

