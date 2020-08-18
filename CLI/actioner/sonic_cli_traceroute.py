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

def run_vrf(args, tr_type, vrfName):
    if len(args) == 0:
        ptc.print_and_log("The command is not complete.")
        return
    try:
        args = re.sub(r"(PortChannel|Ethernet|Management|Loopback|Vlan)(\s+)(\d+)", "\g<1>\g<3>", args)
        if tr_type == "traceroute6":
            if vrfName.lower() == 'mgmt':
                cmd = "sudo cgexec -g l3mdev:" + vrfName + " traceroute -6 " + args
            else:
                cmd = "traceroute -i " + vrfName + " " + args
        else:
            if vrfName.lower() == 'mgmt':
                cmd = "sudo cgexec -g l3mdev:" + vrfName + " traceroute " + args
            else:
                cmd = "traceroute -i " + vrfName + " " + args

        cmd = re.sub('-i\s*Management', '-i eth', cmd)
        cmdList = cmd.split(' ')
        subprocess.call(cmdList, shell=False)

    except KeyboardInterrupt:
        # May be triggered when Ctrl + C is used to stop script execution
        return
    except Exception as e:
        ptc.print_and_log("Internal error")
        log.syslog(log.LOG_ERR, str(e))
        return

def run(args, tr_type):
    if len(args) == 0:
        ptc.print_and_log("The command is not complete.")
        return
    try:
        args = re.sub(r"(PortChannel|Ethernet|Management|Loopback|Vlan)(\s+)(\d+)", "\g<1>\g<3>", args)
        if tr_type == "traceroute6":
            cmd = "traceroute -6 " + args
        else:
            cmd = "traceroute " + args
        cmd = re.sub('-i\s*Management', '-i eth', cmd)
        cmdList = cmd.split(' ')
        subprocess.call(cmdList, shell=False)

    except KeyboardInterrupt:
        # May be triggered when Ctrl + C is used to stop script execution
        return
    except Exception as e:
        ptc.print_and_log("Internal error")
        log.syslog(log.LOG_ERR, str(e))
        return

def validate_input(args, isVrf):
    if(set(args) & ptc.blocked_chars):
        ptc.print_and_log("Invalid argument")
        return False, args

    result = re.search('(-i\s*)(Eth\d+/\d+/*\d*)', args, re.IGNORECASE)
    if (result is not None) and (ptc.is_std_mode()):
        interface = result.group(2)
        alias = ptc.get_alias(interface)
        if alias is None:
            return False, args
        args = re.sub('(-i\s*)(Eth\d+/\d+/*\d*)', '\g<1>' + alias, args, re.IGNORECASE)

    if ("fe80:" in args.lower()
        or "ff01:" in args.lower()
        or "ff02:" in args.lower()):
        if isVrf:
            ptc.print_and_log("VRF name does not work with link-local IPv6 addresses")
            return False, args
        result = re.search('(\s*-i\s*)', args)
        if not result:
			ptc.print_and_log("Interface name is required for link-local IPv6 addresses")
            return False, args
    return True, args

if __name__ == '__main__':
    pipestr().write(sys.argv)
    isVrf = False

    if len(sys.argv) > 2 and sys.argv[2] == "vrf":
        args = " ".join(sys.argv[4:])
        isVrf = True
    else:
        args = " ".join(sys.argv[2:])

    status, args = validate_input(args, isVrf)
    if status is False:
        sys.exit(1)

    if isVrf:
        run_vrf(args, sys.argv[1], sys.argv[3])
    else:
        run(args, sys.argv[1])
