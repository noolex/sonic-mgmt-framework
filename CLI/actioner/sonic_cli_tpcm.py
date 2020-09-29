#!/usr/bin/python
import sys
import time
import json
import ast
from rpipe_utils import pipestr
import cli_client as cc
from scripts.render_cli import show_cli_output

def run_tpcm_list(argv):
    aa = cc.ApiClient()
    templ = argv[0]
    path = cc.Path('/restconf/data/openconfig-system:system/openconfig-system-ext:tpcm/state/tpcm-image-list')
    api_response = aa.get(path)
    if api_response.ok():
        if api_response.content is not None:
            response = api_response.content
            show_cli_output(templ, response)

def build_body(func, method, argv):
    body=""
    args_list=[]
    parameters = { "args" : "string",
                   "skip" : "string",
                   "docker-name" : "string",
                   "image-name" : "string",
                   "remote-server" : "string",
                   "username" : "string",
                   "password" : "string" }
    if func == 'tpcm_uninstall':
       if argv[2] != 'null':
          parameters["skip"] = argv[2]
       parameters["docker-name"] = argv[0]
    else: 
       if func == 'tpcm_install':
          parameters["docker-name"] = argv[4]
          if 'args' in argv:
              value_index = argv.index('args')+1
              args_list = argv[value_index:]

       if func == 'tpcm_upgrade':
          parameters["docker-name"] = argv[4]
          if 'skip_data_migration' in argv:
              value_index = argv.index('skip_data_migration') + 1
              parameters["skip"] = argv[value_index]
          if 'args' in argv:
              value_index = argv.index('args') + 1
              if '"' in argv[value_index]:
                   args_list = argv[value_index:]
              else:
                   args_list = argv[value_index]

    
       if method == 'scp' or method == 'sftp':
           parameters['remote-server']=argv[6]
           parameters["username"] = argv[argv.index('username') + 1]
           parameters["password"] = argv[argv.index('password') + 1]
           parameters["image-name"] = argv[argv.index('filename') + 1]
       else:
           parameters["image-name"] = argv[6] 
       
       if args_list:
           parameters['args']=  " ".join(args_list)

    if func == 'tpcm_install':
       body = {"openconfig-system-ext:input":{"docker-name":parameters['docker-name'],"image-source":method,"image-name":parameters['image-name'],"remote-server":parameters['remote-server'],"username":parameters['username'],"password":parameters['password'],"args":parameters['args']}}
 
    elif func == 'tpcm_upgrade':
       body = {"openconfig-system-ext:input":{"docker-name":parameters['docker-name'],"image-source":method,"image-name":parameters['image-name'],"remote-server":parameters['remote-server'],"username":parameters['username'],"password":parameters['password'],"skip-data-migration":parameters['skip'], "args":parameters['args']}}
    elif func == 'tpcm_uninstall':
       body = {"openconfig-system-ext:input":{"docker-name":parameters['docker-name'],"clean-data":parameters['skip']}}
    return body 


def run_tpcm_install(func, method, argv):
    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/operations/openconfig-system-ext:tpcm-install')
    templ = argv[0]

    body  = build_body(func, method, argv)
    
    print "\nInstallation in process .....\n"

    api_response = aa.post(keypath, body)

    if api_response.ok():
        if api_response.content is not None:
            response = api_response.content
            show_cli_output(templ, response)
    else:
        print api_response.error_message()



def run_tpcm_upgrade(func, method, argv):
    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/operations/openconfig-system-ext:tpcm-upgrade')
    templ = argv[0]

    body  = build_body(func, method, argv)

    print "\nUpgrade in process .....\n"

    api_response = aa.post(keypath, body)

    if api_response.ok():
        if api_response.content is not None:
            response = api_response.content
            show_cli_output(templ, response)
    else:
        print api_response.error_message()

def run_tpcm_uninstall(func, method, argv):
    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/operations/openconfig-system-ext:tpcm-uninstall')
    templ = argv[1]

    body  = build_body(func, method, argv)

    print "\nUninstallation in process .....\n"

    api_response = aa.post(keypath, body)

    if api_response.ok():
        if api_response.content is not None:
            response = api_response.content
            show_cli_output(templ, response)
    else:
        print api_response.error_message()


def run(func, args):
    if func == 'tpcm_list':
       run_tpcm_list(args)
    if func == 'tpcm_install':
       run_tpcm_install(func, args[5], args[0:])
    if func == 'tpcm_uninstall':
       run_tpcm_uninstall(func, args[0],  args[1:])
    if func == 'tpcm_upgrade':
       run_tpcm_upgrade(func, args[5], args[0:])
    return 


