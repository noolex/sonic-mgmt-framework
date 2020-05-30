from collections import OrderedDict
import sys
import json
from rpipe_utils import pipestr
import cli_client as cc
from scripts.render_cli import show_cli_output

ShowOpts = [ "summary", "bgp", "connected", "static" ]
def invoke_api(func, args):
    body = None
    api = cc.ApiClient()
    response = "May 28 19:16:01.418649 sonic INFO sshd[30598]: Accepted password for admin from 10.14.8.140 port 43486 ssh2\n
    May 28 19:16:01.606913 sonic INFO sshd[30598]: pam_unix(sshd:session): session opened for user admin by (uid=0)\n
    "
    return response

def run(func, args):
    try:
        response = invoke_api(func, args)
        if not response.ok():
            #error response
            print response.error_message()
            exit(1)
        print(response.content)

#        d = response.content['sonic-ip-show:output']['response']
#        if len(d) != 0 and "warning" not in d:
#           d = json.loads(d)
#
#           if func == 'show_ip_route_summary':
#               if len(args) >= 6 and args[4] == 'vrf' and args[5] != 'default':
#                    d['vrfname'] = args[5]
#               show_cli_output(args[0], d)
#               return
#
#           routes = d
#           keys = sorted(routes,key=getPrefixAndLen)
#           temp = OrderedDict()
#           for key in keys:
#               temp[key] = routes[key]
#           d = temp
#           show_cli_output(args[0], d)

    except:
        # system/network error
        print "%Error: Transaction Failure"

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])
