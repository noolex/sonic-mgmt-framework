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
import cli_client as cc
import urllib3
urllib3.disable_warnings()

#Invalid chars
blocked_chars = frozenset(['&', ';', '<', '>', '|', '`', '\''])
api = cc.ApiClient()

def is_std_mode():
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
    else:
        return False

def get_alias(interface):
    path = cc.Path('/restconf/data/sonic-port:sonic-port/PORT_TABLE/PORT_TABLE_LIST={name}/alias', name=interface)
    response = api.get(path)

    if response is None:
        return None

    if response.ok():
        response = response.content
        if response is None:
            return None

        interface = response.get('sonic-port:alias')
        return interface

def print_and_log(msg):
    print "% Error:", msg
    log.syslog(log.LOG_ERR, msg)
