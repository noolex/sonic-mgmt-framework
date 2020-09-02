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
from sonic_intf_utils import is_intf_naming_mode_std
import re

#Invalid chars
blocked_chars = frozenset(['&', ';', '<', '>', '|', '`', '\''])
api = cc.ApiClient()

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

def transform_input(args, cmd):
    if is_intf_naming_mode_std():
        if 'ping' in cmd.lower():
            result = re.search('(-I\s*)(Eth\d+/\d+/*\d*)', args, re.IGNORECASE)
        else:
            result = re.search('(-i\s*)(Eth\d+/\d+/*\d*)', args, re.IGNORECASE)

        if (result is not None):
            interface = result.group(2)
            alias = get_alias(interface)
            if alias is None:
                return None

            if 'ping' in cmd.lower():
                args = re.sub('(-I\s*)(Eth\d+/\d+/*\d*)', '\g<1>' + alias, args, re.IGNORECASE)
            else:
                args = re.sub('(-i\s*)(Eth\d+/\d+/*\d*)', '\g<1>' + alias, args, re.IGNORECASE)
            print "Using the native name:", alias, "for the interface:", interface

    #remove space betetween Interface Type and Interface ID.
    args = re.sub(r"(PortChannel|Ethernet|Management|Loopback|Vlan)(\s+)(\d+)", "\g<1>\g<3>", args)

    #convert 'Management' to 'eth'
    if 'ping' in cmd.lower():
        args = re.sub('-I\s*Management', '-I eth', args)
    else:
        args = re.sub('-i\s*Management', '-i eth', args)
    return args

def validate_input(args, isVrf, cmd):
    if len(args) == 0:
        print_and_log("The command is not completed.")
        return False

    if(set(args) & blocked_chars):
        print_and_log("Invalid argument")
        return False

    if ("fe80:" in args.lower()
        or "ff01:" in args.lower()
        or "ff02:" in args.lower()):
        if isVrf:
            print_and_log("VRF name does not work with link-local IPv6 addresses")
            return False
        if 'ping' in cmd.lower():
            result = re.search('(\s*-I\s*)', args)
        else:
            result = re.search('(\s*-i\s*)', args)
        if not result:
            print_and_log("Interface name is required for link-local IPv6 addresses")
            return False

    return True
