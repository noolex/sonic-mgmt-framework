#!/usr/bin/python
import sys
from scripts.render_cli import show_cli_output
import cli_client as cc

def invoke(func, args):
    body = None
    cl = cc.ApiClient()
    msg = None

    if func in ['info', 'list']:
        path = cc.Path('/restconf/data/openconfig-system:system/openconfig-system-ext:systemd-coredump/core-file-records')
        return cl.get(path)
    elif func in ['config']:
        path = cc.Path('/restconf/data/openconfig-system:system/openconfig-system-ext:systemd-coredump/config')
        return cl.get(path)
    else: 
        path = cc.Path('/restconf/data/openconfig-system:system/openconfig-system-ext:systemd-coredump/config')
        if func == 'enable' or func == 'disable':
            body = {
                       "openconfig-system-ext:config": {
                           "enable": False if  func == 'disable' else True
                       }
                   }
        else:
            return None

        return cl.patch(path,body)

def show_coredump_record(args, value):
    found = False
    search_key = None
    if len(args) >= 2:
        search_key = args[1]
    records = value.get('core-file-record')
    if records is not None:
        for r in records:
            if search_key is None or \
               r['state']['pid'] == search_key or search_key in r['state']['executable']:
                if found:
                    print('\n')
                show_cli_output(args[0], r['state'])
                found = True
    if not found:
        print('Core file information not found')

def run(func, args):
    try:
        api_response = invoke(func, args)
        if api_response is None:
            print("Invalid input parameters")
            return -1
        elif api_response.ok():
            if api_response.content is not None:
                response = api_response.content
                if 'openconfig-system-ext:core-file-records' in response.keys():
                    value = response['openconfig-system-ext:core-file-records']
                    if value is not None:
                        if func != 'info':
                            show_cli_output(args[0], value)
                        else:
                            show_coredump_record(args, value)
                elif 'openconfig-system-ext:config' in response.keys():
                    value = response['openconfig-system-ext:config']
                    if func == 'config':
                        show_cli_output(args[0], value)
                else:
                    if func in ['info', 'list']:
                        print('No core dump files')
        else:
            print(api_response.error_message())
            return -1
    except Exception as ex:
        print(ex)
        print("%Error: Transaction Failure")
        return -1
