from collections import OrderedDict
import netaddr
import sys
import json
from rpipe_utils import pipestr
import cli_client as cc
from scripts.render_cli import show_cli_output

def getPrefixAndLen(item):
    ip = netaddr.IPNetwork(item)
    return (ip.value, ip.prefixlen)

ShowOpts = [ "summary", "bgp", "connected", "static" ]
def invoke_api(func, args):
    body = None
<<<<<<< HEAD
    vrfname = "default"
    prefix = None
    options = None
    af = "IPv4"
||||||| merged common ancestors
    vrfname = ""
    prefix = ""
    af = ""
=======
    vrfname = ""
    prefix = ""
    protocol_name = ""
    af = ""
>>>>>>> origin/broadcom_sonic_3.x_share
    api = cc.ApiClient()
    i = 0
    for arg in args:
        if "vrf" == arg:
           vrfname = args[i+1]
        elif "ipv4" == arg:
           af = "IPv4"
        elif "ipv6" == arg:
           af = "IPv6"
        elif "prefix" == arg:
           prefix = args[i+1]
<<<<<<< HEAD
        elif arg in ShowOpts:
           options = arg
||||||| merged common ancestors
=======
        elif "ospf" == arg:
           protocol_name = "ospf"
>>>>>>> origin/broadcom_sonic_3.x_share
        else:
           pass
        i = i + 1

    keypath = cc.Path('/restconf/operations/sonic-ip-show:show-ip-route')
<<<<<<< HEAD
    inputs = {"vrf-name":vrfname, "family":af}
    if prefix:
        inputs['prefix'] = prefix
    elif options:
        inputs[options] = True
    body = {"sonic-ip-show:input": inputs}
||||||| merged common ancestors
    body = {"sonic-ip-show:input": { "vrf-name": vrfname, "family": af, "prefix": prefix}}
=======
    body = {"sonic-ip-show:input": { "vrf-name": vrfname, "family": af, "prefix": prefix, "protocol-name": protocol_name}}
>>>>>>> origin/broadcom_sonic_3.x_share
    response = api.post(keypath, body)
    return response

def run(func, args):
    try:
        response = invoke_api(func, args)
        if not response.ok():
            #error response
            print response.error_message()
            exit(1)

        d = response.content['sonic-ip-show:output']['response']
        if len(d) != 0 and "warning" not in d:
           d = json.loads(d)

           if func == 'show_ip_route_summary':
               if len(args) >= 6 and args[4] == 'vrf' and args[5] != 'default':
                    d['vrfname'] = args[5]
               show_cli_output(args[0], d)
               return

           routes = d
           keys = sorted(routes,key=getPrefixAndLen)
           temp = OrderedDict()
           for key in keys:
               temp[key] = routes[key]
           d = temp
           show_cli_output(args[0], d)

    except:
        # system/network error
        print "%Error: Transaction Failure"

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])
