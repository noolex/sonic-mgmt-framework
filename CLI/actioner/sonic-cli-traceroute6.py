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
    op = re.search(r'-i\s*(Ethernet|Loopback|Management|PortChannel|Vlan)', args)
    if op is not None:
        return True
    return False

def print_and_log(msg):
    print "% Error: ", msg
    log.syslog(log.LOG_ERR, msg)

def run_vrf(args):
    vrfName = args[0]
    args = " ".join(args[1:])
    args = re.sub(r"(PortChannel|Ethernet|Management|Loopback|Vlan)(\s+)(\d+)", "\g<1>\g<3>", args)
    try:
        if len(args) == 0:
            print_and_log("The command is not completed.")
            return
        cmd = "traceroute -6 " + args + " -i " + vrfName
        cmd = re.sub('-i\s*Management', '-i eth', cmd)
        cmdList = cmd.split(' ')
        subprocess.call(cmdList, shell=False)

    except KeyboardInterrupt:
        # May be triggered when Ctrl + C is used to stop script execution
        return
    except Exception as e:
        print_and_log("Internal error")
        log.syslog(log.LOG_ERR, str(e))
        return

def run(args):
    args = " ".join(args[1:])
    args = re.sub(r"(PortChannel|Ethernet|Management|Loopback|Vlan)(\s+)(\d+)", "\g<1>\g<3>", args)
    try:
        if len(args) == 0:
            print_and_log("The command is not completed.")
            return
        cmd = "traceroute -6 " + args
        cmd = re.sub('-i\s*Management', '-i eth', cmd)
        cmdList = cmd.split(' ')
        subprocess.call(cmdList, shell=False)

    except KeyboardInterrupt:
        # May be triggered when Ctrl + C is used to stop script execution
        return
    except Exception as e:
        print_and_log("Internal error")
        log.syslog(log.LOG_ERR, str(e))
        return

def validate_input(args):
    if(set(args) & blocked_chars):
        print_and_log("Invalid argument")
        return False
    #check if valid interface is provided or not
    if " -i" in args:
        if "vrf" in args:
            print_and_log("VRF name is not allowed with -i option")
            return False
        if contains_valid_intf(args) is False:
            print_and_log("Invalid interface, valid options are Ethernet<id>|Management<id>|Vlan<id>|PortChannel<id>|Loopback<id>")
            return False
    if ("fe80:" in args.lower()
        or "ff01:" in args.lower()
        or "ff02:" in args.lower()):
        if "vrf" in args:
            print_and_log("VRF name is not allowed for IPv6 addresses with link-local scope")
            return False
        if " -i" not in args:
            print_and_log("Interface name was missing")
            return False
    return True

if __name__ == '__main__':
    pipestr().write(sys.argv)

    args = " ".join(sys.argv[0:])
    if validate_input(args) is False:
        sys.exit(1)

    if len(sys.argv) > 1 and sys.argv[1] == "vrf":
        run_vrf(sys.argv[2:])
    else:
        run(sys.argv)
