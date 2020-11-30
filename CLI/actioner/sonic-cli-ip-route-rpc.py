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

ShowOpts = [ "summary", "bgp", "connected", "static", "ospf" ]
def invoke_api(func, args):
    body = None
    vrfname = "default"
    prefix = None
    options = None
    address = None
    af = "IPv4"
    protocol_name = None
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
        elif "address" == arg:
           address = args[i+1]
        elif arg in ShowOpts:
           options = arg
        else:
           pass
        i = i + 1

    keypath = cc.Path('/restconf/operations/sonic-ip-show:show-ip-route')
    inputs = {"vrf-name":vrfname, "family":af}
    if prefix:
        inputs['prefix'] = prefix
    elif address:
        inputs['address'] = address
    elif options:
        inputs[options] = True
    body = {"sonic-ip-show:input": inputs}
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
                   if args[5] != 'all':
                       d = { args[5] : d }
               else:
                   d = { 'default' : d }

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
