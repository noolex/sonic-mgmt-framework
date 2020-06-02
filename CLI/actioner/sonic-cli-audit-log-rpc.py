from collections import OrderedDict
import sys
import json
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
import cli_client as cc

def run(func, args):
    aa = cc.ApiClient()
    if func == 'rpc_sonic_auditlog_show_auditlog':
        keypath = cc.Path('/restconf/operations/sonic-auditlog:show-auditlog')
        body = { "sonic-auditlog:input": {} }
        response = aa.post(keypath, body)
        if response.ok():
            print("AUDIT LOG")
            print(response.content["sonic-show-auditlog:output"]["audit-content"])
        else:
            print "%Error: Transaction Failure "
            print(response.error_message())
            print(response.status_code)

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])

