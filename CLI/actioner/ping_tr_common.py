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

INVALID_IFNAME  = -1
DEFAULT_IFNAME  = 0
STD_IFNAME      = 1
STD_SUBIFNAME   = 2
NATIVE_IFNAME   = 3
NATIVE_SUBIFNAME= 4
MGMT_IFNAME     = 5

def get_alias(interface):
    isSubIntf = False
    tmpIntf = interface
    subIntfId = ""

    #if 'interface' is a subinteface, separate interface name and its ID
    result = re.search('(\s*)(Eth)(\s*)(\d+/\d+/*\d*)(\.\d+)', tmpIntf, re.IGNORECASE)
    if result:
        isSubIntf = True
        tmpIntf = result.group(2) + result.group(4)
        subIntfId = result.group(5)

    path = cc.Path('/restconf/data/sonic-port:sonic-port/PORT_TABLE/PORT_TABLE_LIST={name}/alias', name=tmpIntf)
    response = api.get(path)
    if response is None:
        return None

    if response.ok():
        response = response.content
        if response is None:
            return None

        interface = response.get('sonic-port:alias')
        if interface and isSubIntf:
            result = re.search('(\s*)(Ethernet)(\d+)', interface, re.IGNORECASE)
            if result:
                interface = "Eth" + result.group(3) + subIntfId

        return interface

def print_and_log(msg):
    print "% Error:", msg
    log.syslog(log.LOG_ERR, msg)

def getIfName(args, cmd):

    intfSwitch = '-I'
    if cmd == 'traceroute':
        intfSwitch = '-i'

    stdNaming = is_intf_naming_mode_std()

    # Check for interfaces, order is important.
    # Regex for subinterfaces should come first.

    #Check for subinterface
    result = re.search('('+intfSwitch+'\s*)(Ethernet|PortChannel)(\s*)(\d+\.\d+)(\s+|$)', args, re.IGNORECASE)
    if result:
        if stdNaming: #For std naming we shouldn't come here
            return None, INVALID_IFNAME
        if result.group(2).startswith("Eth"):
            ifName = "Eth" + result.group(4)
        elif result.group(2).startswith("Port"):
            ifName = "Po" + result.group(4)
        return ifName, NATIVE_SUBIFNAME

    #Check for subinterface with alias
    result = re.search('('+intfSwitch+'\s*)(Eth)(\s*)(\d+/\d+/*\d*\.\d+)(\s+|$)', args, re.IGNORECASE)
    if result:
        if not stdNaming:
            return None, INVALID_IFNAME
        if result.group(2).startswith("Eth"):
            ifName = "Eth" + result.group(4)
        ifName = get_alias(ifName)
        return ifName, STD_SUBIFNAME

    #Check for interface
    result = re.search('('+intfSwitch+'\s*)(Ethernet)(\s*)(\d+)(\s+|$)', args, re.IGNORECASE)
    if result:
        if stdNaming: #For std naming we shouldn't come here
            return None, INVALID_IFNAME
        ifName = result.group(2) + result.group(4)
        return ifName, NATIVE_IFNAME

    #Check for interface with alias
    result = re.search('('+intfSwitch+'\s*)(Eth)(\s*)(\d+/\d+/*\d*)(\s+|$)', args, re.IGNORECASE)
    if result:
        if not stdNaming:
            return None, INVALID_IFNAME
        ifName = result.group(2) + result.group(4)
        ifName = get_alias(ifName)
        return ifName, STD_IFNAME

    #Check for mgmt interface
    result = re.search('('+intfSwitch+'\s*)(Management)(\s*)(\d+)(\s+|$)', args, re.IGNORECASE)
    if result:
        ifName = "eth" + result.group(4)
        return ifName, MGMT_IFNAME

    #Check for other interfaces
    result = re.search('('+intfSwitch+'\s*)(PortChannel|Loopback|Vlan)(\s*)(\d+)(\s+|$)', args, re.IGNORECASE)
    if result:
        ifName = result.group(2) + result.group(4)
        return ifName, DEFAULT_IFNAME

    return None, INVALID_IFNAME

def transform_input(args, cmd):
    ifName = ""
    isSubIntf = False

    ifName, nameType = getIfName(args, cmd)
    stdNaming = is_intf_naming_mode_std()

    if ifName is None or nameType == INVALID_IFNAME:
        return args

    intfSwitch = '-I'
    if cmd == 'traceroute':
        intfSwitch = '-i'

    # Substitute interface name in the args based on interface type.
    if nameType == NATIVE_IFNAME:
        args = re.sub('('+intfSwitch+')(\s*)(Ethernet\s*\d+)(\s+v|$)', '\g<1>' + " " + ifName + " ", args, re.IGNORECASE)
        return args.strip()

    if nameType == NATIVE_SUBIFNAME:
        args = re.sub('('+intfSwitch+')(\s*)(Ethernet|PortChannel)(\s*\d+\.\d+)(\s+|$)', '\g<1>' + " " + ifName + " ", args, re.IGNORECASE)
        return args.strip()

    if nameType == STD_IFNAME:
        args = re.sub('('+intfSwitch+')(\s*)(Eth)(\s*)(\d+/\d+/*\d*)(\s+|$)', '\g<1>' + " " + ifName + " ", args, re.IGNORECASE)
        return args.strip()

    if nameType == STD_SUBIFNAME:
        args = re.sub('('+intfSwitch+')(\s*)(Eth|PortChannel)(\s*)(\d+/\d+/*\d*\.\d+)(\s+|$)', '\g<1>' + " " + ifName + " ", args, re.IGNORECASE)
        return args.strip()

    if nameType == MGMT_IFNAME:
        args = re.sub('('+intfSwitch+')(\s*)(Management\s*\d+)(\s+|$)', '\g<1>' + " " + ifName + " ", args, re.IGNORECASE)
        return args.strip()

    if nameType == DEFAULT_IFNAME:
        args = re.sub('('+intfSwitch+')(\s*)(PortChannel|Loopback|Vlan)(\s*)(\d+)(\s+|$)', '\g<1>' + " " + ifName + " ", args, re.IGNORECASE)
        return args.strip()

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
