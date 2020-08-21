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

        cmdList = cmd.split(' ')
        subprocess.call(cmdList, shell=False)

    except KeyboardInterrupt:
        # May be triggered when Ctrl + C is used to stop script execution
        return
    except Exception as e:
        ptc.print_and_log("Internal error")
        log.syslog(log.LOG_ERR, str(e))
        return

def run(func, argv):
    isVrf = False

    if argv[0] == "vrf":
        args = " ".join(argv[2:])
        isVrf = True
    else:
        args = " ".join(argv[0:])

    valid = ptc.validate_input(args, isVrf, func)
    if not valid:
        return -1

    args = ptc.transform_input(args, func)
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
