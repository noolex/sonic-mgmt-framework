
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

import re
import syslog
import cli_client as cc

def name_to_int_val(ifName):
    val = 0
    if ifName.startswith('Eth'):
        tk = ifName.split('.')
        plist = re.findall(r'\d+', tk[0])
        val = 0
        if len(plist) == 1:  #ex: Ethernet40
           val = int(plist[0]) * 10000
        elif len(plist) == 2:  #ex: Eth1/5
           val= int(plist[0]+plist[1].zfill(3)+'000000')
        elif len(plist) == 3:  #ex: Eth1/5/2
           val= int(plist[0]+plist[1].zfill(3)+plist[2].zfill(2)+'0000')

        if len(tk) == 2:   #ex: 2345 in Eth1/1.2345
           val += int(tk[1])
    elif ifName.startswith('PortChannel'):
        val = 2000000000 + int(ifName[11:])
    elif ifName.startswith('Vlan'):
        val = 3000000000 + int(ifName[4:])

    return val

def isMgmtVrfEnabled(cc):
    api = cc.ApiClient()
    try:
        request = "/restconf/data/openconfig-network-instance:network-instances/network-instance=mgmt/state/enabled/"

        response = api.get(request)
        response = response.content
        response = response.get('openconfig-network-instance:enabled')
        if response is None:
            return False
        elif response is False:
            return False
        else:
            return True
    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, str(e))
        return False

def is_intf_naming_mode_std():
    api = cc.ApiClient()
    try:
        path = cc.Path('/restconf/data/sonic-device-metadata:sonic-device-metadata/DEVICE_METADATA/DEVICE_METADATA_LIST={name}/intf_naming_mode', name="localhost")
        response = api.get(path)
        if response is None:
            return False

        if response.ok():
            response = response.content
            if response is None:
                return False

        response = response.get('sonic-device-metadata:intf_naming_mode')
        if response is None:
            return False

        if "standard" in response.lower():
            return True

        return False

    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, str(e))
        return False
