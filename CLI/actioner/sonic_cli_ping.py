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
import ping_tr_common as ptc
import urllib3
urllib3.disable_warnings()
import subprocess
import re

def do_ping_vrf(args, ping_type, vrfName):
    try:
        if ping_type == "ping6":
            if vrfName.lower() == 'mgmt':
                cmd = "sudo cgexec -g l3mdev:" + vrfName + " ping -6 " + args
            else:
                cmd = "ping -I " + vrfName + " " + args
        else:
            if vrfName.lower() == 'mgmt':
                cmd = "sudo cgexec -g l3mdev:" + vrfName + " ping " + args
            else:
                cmd = "ping -I " + vrfName + " " + args

        cmd = re.sub('-I\s*Management', '-I eth', cmd)
        cmdList = cmd.split(' ')
        subprocess.call(cmdList, shell=False)

    except KeyboardInterrupt:
        # May be triggered when Ctrl + C is used to stop script execution
        return
    except Exception as e:
        ptc.print_and_log("Internal error")
        log.syslog(log.LOG_ERR, str(e))
        return

def do_ping(args, ping_type):
    try:
        if ping_type == "ping6":
            cmd = "ping -6 " + args
        else:
            cmd = "ping " + args

        cmd = re.sub('-I\s*Management', '-I eth', cmd)
        cmdList = cmd.split(' ')
        subprocess.call(cmdList, shell=False)

    except KeyboardInterrupt:
        # May be triggered when Ctrl + C is used to stop script execution
        return
    except Exception as e:
        ptc.print_and_log("Internal error")
        log.syslog(log.LOG_ERR, str(e))
        return

def transform_input(args):
    result = re.search('(-I\s*)(Eth\d+/\d+/*\d*)', args, re.IGNORECASE)
    if (result is not None) and (ptc.is_std_mode()):
        interface = result.group(2)
        alias = ptc.get_alias(interface)
        if alias is None:
            return None

        args = re.sub('(-I\s*)(Eth\d+/\d+/*\d*)', '\g<1>' + alias, args, re.IGNORECASE)
        print "Using the native name:", alias, "for the interface:", interface

    #remove space betetween Interface Type and Interface ID.
    args = re.sub(r"(PortChannel|Ethernet|Management|Loopback|Vlan)(\s+)(\d+)", "\g<1>\g<3>", args)
    return args

def validate_input(args, isVrf):
    if len(args) == 0:
        ptc.print_and_log("The command is not completed.")
        return False

    if(set(args) & ptc.blocked_chars):
        ptc.print_and_log("Invalid argument")
        return False

    if ("fe80:" in args.lower()
        or "ff01:" in args.lower()
        or "ff02:" in args.lower()):
        if isVrf:
            ptc.print_and_log("VRF name does not work with link-local IPv6 addresses")
            return False
        result = re.search('(\s*-I\s*)', args)
        if not result:
            ptc.print_and_log("Interface name is required for link-local IPv6 addresses")
            return False

    return True

def run(func, argv):
    isVrf = False

    if argv[0] == "vrf":
        args = " ".join(argv[2:])
        isVrf = True
    else:
        args = " ".join(argv[0:])

    valid = validate_input(args, isVrf)
    if not valid:
        return -1

    args = transform_input(args)
    if not args:
        return -1

    if isVrf:
        do_ping_vrf(args, func, argv[1])
    else:
        do_ping(args, func)

if __name__ == '__main__':
    pipestr().write(sys.argv)
    status = run(sys.argv[1], sys.argv[2:])
    if status != 0:
        sys.exit(0)
