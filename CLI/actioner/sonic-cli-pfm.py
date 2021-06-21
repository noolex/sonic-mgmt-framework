#!/usr/bin/python
###########################################################################
#
# Copyright 2020 Dell, Inc.
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
    if 'openconfig-platform-psu:temperature' in psu['power-supply']['state']:
        psu['power-supply']['state']['openconfig-platform-psu:temperature'] = \
            convert4BytesToStr(psu['power-supply']['state']['openconfig-platform-psu:temperature'])
    if 'openconfig-platform-psu:input-current' in psu['power-supply']['state']:
        psu['power-supply']['state']['openconfig-platform-psu:input-current'] = \
            convert4BytesToStr(psu['power-supply']['state']['openconfig-platform-psu:input-current'])
    if 'openconfig-platform-ext:input-power' in psu['power-supply']['state']:
        psu['power-supply']['state']['openconfig-platform-ext:input-power'] = \
            convert4BytesToStr(psu['power-supply']['state']['openconfig-platform-ext:input-power'])
    if 'openconfig-platform-psu:input-voltage' in psu['power-supply']['state']:
        psu['power-supply']['state']['openconfig-platform-psu:input-voltage'] = \
            convert4BytesToStr(psu['power-supply']['state']['openconfig-platform-psu:input-voltage'])

def run(func, args):

    # set of operational, non-static, keys to omit from output of a transceiver
    dom_op_params_keys = ['lb-host-side-input-support', 'lb-host-side-output-support',
                          'lb-media-side-input-support', 'lb-media-side-output-support',
                          'lb-per-lane-host-side-support', 'lb-per-lane-media-side-support',
                          'lb-simul-host-media-side-support',
                          'lb-host-side-input-enable', 'lb-host-side-output-enable',
                          'lb-media-side-input-enable', 'lb-media-side-output-enable',
                          'lb-per-lane-host-side-enable', 'lb-per-lane-media-side-enable',
                          'lb-simul-host-media-side-enable',
                          'lol-lane-1', 'lol-lane-2', 'lol-lane-3', 'lol-lane-4',
                          'lol-lane-5', 'lol-lane-6', 'lol-lane-7', 'lol-lane-8',
                          'los-lane-1', 'los-lane-2', 'los-lane-3', 'los-lane-4',
                          'los-lane-5', 'los-lane-6', 'los-lane-7', 'los-lane-8',
                          'tx-bias-lane-1', 'tx-bias-lane-2', 'tx-bias-lane-3', 'tx-bias-lane-4',
                          'tx-bias-lane-5', 'tx-bias-lane-6', 'tx-bias-lane-7', 'tx-bias-lane-8',
                          'rx-power-lane-1', 'rx-power-lane-2', 'rx-power-lane-3', 'rx-power-lane-4',
                          'rx-power-lane-5', 'rx-power-lane-6', 'rx-power-lane-7', 'rx-power-lane-8',
                          'tx-power-lane-1', 'tx-power-lane-2', 'tx-power-lane-3', 'tx-power-lane-4',
                          'tx-power-lane-5', 'tx-power-lane-6', 'tx-power-lane-7', 'tx-power-lane-8',
                          'voltage', 'temperature']


    aa = cc.ApiClient()
    template = sys.argv[3]
    response = None
    hasValidComp = False
    try:
        if func == 'get_openconfig_platform_components_component':
            path = cc.Path('/restconf/data/openconfig-platform:components/component=%s'%args[0])
            response = aa.get(path)
            if response.ok():
                if response.content is None:
                    response.content = OrderedDict()
                show_cli_output(template, response.content)
            else:
                print response.error_message()
                return 1
        elif (func == 'get_openconfig_platform_components_component_psu_status' or
            func == 'get_openconfig_platform_components_component_psu_summary'):
            template = sys.argv[2]
            psuInfo = OrderedDict()
            for i in xrange(1, sys.maxsize):
                path = cc.Path('/restconf/data/openconfig-platform:components/component=PSU %s'%i)
                response = aa.get(path)
                if not response.ok():
                    if not hasValidComp:
                        print response.error_message()
                        return 1
                    break
                if response.content == None:
                    break
                hasValidComp = True
                if (response.content is None or len(response.content) == 0 or
                    not ('openconfig-platform:component' in response.content) or
                    len(response.content['openconfig-platform:component']) == 0 or
                    len(response.content['openconfig-platform:component'][0]) < 2 or
                    not ('name' in response.content['openconfig-platform:component'][0])):
                    break
                psuName = response.content['openconfig-platform:component'][0]['name']
                psuInfo[psuName] = response.content['openconfig-platform:component'][0]
                decodePsuStats(psuInfo[psuName])
                for j in xrange(1, sys.maxsize):
                    path = cc.Path('/restconf/data/openconfig-platform:components/component=PSU {} FAN {}'.format(i, j))
                    response = aa.get(path)
                    if not response.ok():
                        if not hasValidComp:
                            print response.error_message()
                            return 1
                        break
                    if (response.content is None or len(response.content) == 0 or
                        not ('openconfig-platform:component' in response.content) or
                        len(response.content['openconfig-platform:component']) == 0 or
                        len(response.content['openconfig-platform:component'][0]) < 2 or
                        not ('name' in response.content['openconfig-platform:component'][0])):
                        break
                    fanName = response.content['openconfig-platform:component'][0]['name']
                    psuInfo[psuName][fanName] = response.content['openconfig-platform:component'][0]
            show_cli_output(template, psuInfo)
        elif func == 'get_openconfig_platform_components_component_fan_status':
            template = sys.argv[2]
            fanInfo = OrderedDict()
            for i in xrange(1, sys.maxsize):
                path = cc.Path('/restconf/data/openconfig-platform:components/component=FAN %s'%i)
                response = aa.get(path)
                if not response.ok():
                    if not hasValidComp:
                        print response.error_message()
                        return 1
                    break
                if response.content is None:
                    break
                hasValidComp = True
                if (response.content is None or len(response.content) == 0 or
                    not ('openconfig-platform:component' in response.content) or
                    len(response.content['openconfig-platform:component']) == 0 or
                    len(response.content['openconfig-platform:component'][0]) < 2 or
                    not ('name' in response.content['openconfig-platform:component'][0])):
                    break
                fanName = response.content['openconfig-platform:component'][0]['name']
                fanInfo[fanName] = response.content['openconfig-platform:component'][0]
            show_cli_output(template, fanInfo)
        elif func == 'get_openconfig_platform_components_component_transceiver_status':
            if_name = args[0]
            template = args[1]
            xcvrInfo = OrderedDict()
            summary = False
            if_list = []

            if if_name in ["Ethernet_SUMMARY", "Ethernet_ALL"]:
                summary = (True if (if_name == "Ethernet_SUMMARY") else False)
                # Get list of ports
                path = cc.Path('/restconf/data/sonic-port:sonic-port/PORT/PORT_LIST')
                response = aa.get(path)
                if not response.ok():
                    print response.error_message()
                    return 1
                if not response.content is None:
                    try:
                        for d in response.content['sonic-port:PORT_LIST']:
                            if_list.append(d['ifname'])
                    except:
                        return 1
            elif if_name == 'Ethernet_X_SUMMARY':
                summary = True
                if args[2] == 'do':
                    if_name = args[6]
                else:
                    if_name = args[5]
                if_list.append(if_name)
            else:
                # Singleton
                if_list.append(if_name)

            for nm in if_list:
                n = nm
                if '/' in nm:
                    n = nm.replace('/', '%2F')
                path = cc.Path('/restconf/data/openconfig-platform:components/component=' + n)
                response = aa.get(path)
                if not response.ok():
                    print response.error_message()
                    return 1
                if response.content is None:
                    xcvrInfo[nm] = {}
                    continue
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
                        if a in dom_op_params_keys:
                            continue

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
        elif func == 'get_openconfig_platform_components_component_temperature':
            template = sys.argv[2]
            tempInfo = OrderedDict()
            for i in xrange(1, sys.maxsize):
                path = cc.Path('/restconf/data/openconfig-platform:components/component=TEMP %s'%i)
                response = aa.get(path)
                if not response.ok():
                    if not hasValidComp:
                        print response.error_message()
                        return 1
                    break
                if response.content is None:
                    break
                hasValidComp = True
                if (response.content is None or len(response.content) == 0 or
                    not ('openconfig-platform:component' in response.content) or
                    len(response.content['openconfig-platform:component']) == 0 or
                    not ('state' in response.content['openconfig-platform:component'][0])):
                    break
                tempName = response.content['openconfig-platform:component'][0]['state']['name']
		if 'temperature' in response.content['openconfig-platform:component'][0]['state']:
                    tempInfo[tempName] = response.content['openconfig-platform:component'][0]['state']['temperature']
                else:
                    tempInfo[tempName] = OrderedDict()
            tempInfo = OrderedDict(sorted(tempInfo.items()))
            show_cli_output(template, tempInfo)
        elif func == 'get_openconfig_platform_components_component_firmware':
            template = sys.argv[2]
            firmInfo = OrderedDict()
            for i in xrange(1, 10):
                path = cc.Path('/restconf/data/openconfig-platform:components/component=FIRMWARE %s'%i)
                response = aa.get(path)
                if not response.ok():
                    if not hasValidComp:
                        print response.error_message()
                        return 1
                    break
                if response.content is None:
                    break
                hasValidComp = True
                if (response.content is None or len(response.content) == 0 or
                    not ('openconfig-platform:component' in response.content) or
                    len(response.content['openconfig-platform:component']) == 0 or
                    not ('state' in response.content['openconfig-platform:component'][0])):
                    break
                firmName = response.content['openconfig-platform:component'][0]['state']['name']
                resp = response.content['openconfig-platform:component'][0]
                chassisName = 'N/A'
                moduleName = 'N/A'

                if ('chassis' in resp and 'state' in resp['chassis'] and
                    'openconfig-platform-ext:name' in resp['chassis']['state']):
                    chassisName = resp['chassis']['state']['openconfig-platform-ext:name']
                if ('chassis' in resp and 'state' in resp['chassis'] and
                    'openconfig-platform-ext:module' in resp['chassis']['state']):
                    chassisName = resp['chassis']['state']['openconfig-platform-ext:module']

                if chassisName not in firmInfo:
                    firmInfo[chassisName] = OrderedDict()
                if moduleName not in firmInfo[chassisName]:
                    firmInfo[chassisName][moduleName] = OrderedDict()
                firmInfo[chassisName][moduleName][firmName] = resp['state']

            firmInfo = OrderedDict(sorted(firmInfo.items()))
            for chassis in firmInfo:
                firmInfo[chassis] = OrderedDict(sorted(firmInfo[chassis].items()))
                for module in firmInfo[chassis]:
                    firmInfo[chassis][module] = OrderedDict(sorted(firmInfo[chassis][module].items()))
            show_cli_output(template, firmInfo)
    except Exception as e:
        print("%Error: Transaction Failure")
        return 1
    return 0

if __name__ == '__main__':

    func = sys.argv[1]
    ret = run(func, sys.argv[2:])
    sys.exit(ret)

