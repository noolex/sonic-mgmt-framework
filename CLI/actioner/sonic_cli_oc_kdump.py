#!/usr/bin/python
import sys
from scripts.render_cli import show_cli_output
import cli_client as cc

def invoke(func, args):
    body = None
    cl = cc.ApiClient()
    msg = None

    if func in ['memory', 'num_dumps']:
        path = cc.Path('/restconf/data/openconfig-system:system/openconfig-system-ext:kdump/state')
        return cl.get(path)
    elif func in ['status']:
        path = cc.Path('/restconf/data/openconfig-system:system/openconfig-system-ext:kdump/state')
        return cl.get(path)
    elif func in ['files', 'log']:
        path = cc.Path('/restconf/data/openconfig-system:system/openconfig-system-ext:kdump/kdump-records')
        return cl.get(path)
    else: 
        msg = "Kdump configuration has been updated in the startup configuration"
        mem_msg = "\nKdump updated memory will be only operational after the system reboots"
        path = cc.Path('/restconf/data/openconfig-system:system/openconfig-system-ext:kdump/config')
        if func == 'enable' or func == 'disable':
            body = {
                       "openconfig-system-ext:config": {
                           "enable": False if  func == 'disable' else True
                       }
                   }
            msg = msg + "\nKdump configuration changes will be applied after the system reboots"
        elif func == 'config':
            param = args[0]
            value = args[1]
            if param == 'memory':
                msg = msg + mem_msg
            elif param == 'max-dumps':
                value = int(args[1])
            else:
                return None
            body = {
                       "openconfig-system-ext:config": {
                          param : value
                       }
                   }
        elif func == 'reset':
            if args[0] == 'memory':
                msg = msg + mem_msg
            elif args[0] != 'max-dumps':
                return None
            path = cc.Path('/restconf/data/openconfig-system:system/openconfig-system-ext:kdump/config/{}'.format(args[0]))
            res = cl.delete(path)
            if res.ok():
               print(msg)
            return res
        else:
            return None

        res = cl.patch(path,body)
        if res.ok():
            print(msg)

        return res

def show_kdump_record(args, value):
    lines = None
    if len(args) == 2:
        record_num = args[1]
    elif len(args) == 3:
        record_num = args[1]
        lines = args[2]
    kdump_records = value.get('kdump-record')
    if kdump_records is not None and \
       int(record_num) <= len(kdump_records) and int(record_num) > 0:
        r = sorted(kdump_records, reverse=True)[int(record_num)-1]
        if r['state']['vmcore-diagnostic-message'] != '':
            show_cli_output(args[0], "File: {}".format(r['state']['vmcore-diagnostic-message-file']))
            if lines is not None:
                output_lines = r['state']['vmcore-diagnostic-message'].split('\n')[-(int(lines)+1):]
                show_cli_output(args[0], "\n".join(output_lines))
            else:
                show_cli_output(args[0], r['state']['vmcore-diagnostic-message'])
            return
    show_cli_output(args[0], 'Kernel crash log not found')

def run(func, args):
    try:
        api_response = invoke(func, args)
        if api_response is None:
            print("Invalid input parameters")
            return -1
        elif api_response.ok():
            if api_response.content is not None:
                response = api_response.content
                if 'openconfig-system-ext:state' in list(response.keys()):
                    value = response['openconfig-system-ext:state']
                    if value is not None:
                        show_cli_output(args[0], value)
                        if func == 'status':
                            run('files', ['show_oc_kdump_files.j2'])
                elif 'openconfig-system-ext:kdump-records' in list(response.keys()):
                    value = response['openconfig-system-ext:kdump-records']
                    if value is not None:
                        if func != 'log':
                            show_cli_output(args[0], value)
                        else:
                            show_kdump_record(args, value)
                else:
                    if func in ['status', 'files', 'log']:
                        print('No kernel core dump files')

        else:
            print(api_response.error_message())
            return -1
    except Exception as ex:
        print(ex)
        print("%Error: Transaction Failure")
        return -1
