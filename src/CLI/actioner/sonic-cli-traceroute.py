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
import subprocess
import re

#Invalid chars
blocked_chars = frozenset(['&', ';', '<', '>', '|', '`', '\''])

def contains_valid_intf(args):
    op = re.search(r' -I\s*Vlan(409[0-5]|40[0-8][0-9]|[1-3][0-9]{3}|[1-9][0-9]{2}|[1-9][0-9]|[1-9])(\s+|$)', args)
    if op is not None:
        return True
    op = re.search(r' -I\s*Ethernet([1-3][0-9]{3}|[1-9][0-9]{2}|[1-9][0-9]|[0-9])(\s+|$)', args)
    if op is not None:
        return True
    op = re.search(r' -I\s*Management([1-3][0-9]{3}|[1-9][0-9]{2}|[1-9][0-9]|[0-9])(\s+|$)', args)
    if op is not None:
        return True
    op = re.search(r' -I\s*PortChannel([1-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-6])(\s+|$)', args)
    if op is not None:
        return True
    op = re.search(r' -I\s*Loopback([0-9]|[1-8][0-9]|9[0-9]|[1-8][0-9]{2}|9[0-8][0-9]|99[0-9]|[1-8][0-9]{3}|9[0-8][0-9]{2}|99[0-8][0-9]|999[0-9]|1[0-5][0-9]{3}|16[0-2][0-9]{2}|163[0-7][0-9]|1638[0-3])(\s+|$)', args)
    if op is not None:
        return True
    return False

def print_and_log(inMsg):
    msg = "Error: traceroute unsuccessful"
    logMsg = msg + " : " + inMsg
    print msg
    log.syslog(log.LOG_ERR, logMsg)

def run_vrf(args):
    vrfName = args[0]
    args = " ".join(args[1:])
    if(set(args) & blocked_chars):
        print "%Error: Invalid argument."
        sys.exit(1)
    try:
        if len(args) == 0:
            args = "-h"
        cmd = "traceroute " + args + " -i " + vrfName
        cmd = re.sub('-i\s*Management', '-i eth', cmd)
        cmdList = cmd.split(' ')
        subprocess.call(cmdList, shell=False)

    except KeyboardInterrupt:
        # May be triggered when Ctrl + C is used to stop script execution
        return
    except Exception as e:
        print_and_log(str(e))
        return

def run(args):
    args = " ".join(args[1:])
    if(set(args) & blocked_chars):
        print "%Error: Invalid argument."
        sys.exit(1)
    try:
        if len(args) == 0:
            args = "-h"
        cmd = "traceroute " + args
        cmd = re.sub('-i\s*Management', '-i eth', cmd)
        cmdList = cmd.split(' ')
        subprocess.call(cmdList, shell=False)

    except KeyboardInterrupt:
        # May be triggered when Ctrl + C is used to stop script execution
        return
    except Exception as e:
        print_and_log(str(e))
        return

if __name__ == '__main__':
    pipestr().write(sys.argv)

    #check if valid interface is provided or not
    args = " ".join(sys.argv[0:])
    if " -i" in args:
        if contains_valid_intf(args) is False:
            print("Invalid interface, valid options are Ethernet<id>|Management<id>|Vlan<id>|PortChannel<id>|Loopback<id>")
            sys.exit(1)

    if len(sys.argv) > 1 and sys.argv[1] == "vrf":
        run_vrf(sys.argv[2:])
    else:
        run(sys.argv)

