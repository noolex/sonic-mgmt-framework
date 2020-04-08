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

def print_and_log(inMsg):
    msg = "Error: ping6 unsuccessful"
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
        cmd = "ping -6 " + args + " -I " + vrfName
        cmd = re.sub('-I\s*Management', '-I eth', cmd)
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
        cmd = "ping -6 " + args
        cmd = re.sub('-I\s*Management', '-I eth', cmd)
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
    if len(sys.argv) > 1 and sys.argv[1] == "vrf":
        run_vrf(sys.argv[2:])
    else:
        run(sys.argv)
