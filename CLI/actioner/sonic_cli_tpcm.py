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

def build_options(func, method, argv):
    parameters = { "args" : ["null"],
                   "skip" : "null",
                   "username" : "null",
                   "password" : "null",
                   "filename" : "null" }
    options_cmd=[]
 
    if func == 'tpcm_install':
       if method == 'scp' or method == 'sftp':
          parameters["args"] = argv[6:]
       else:
          parameters["args"] = argv[3:]

    if func == 'tpcm_upgrade':
       if method == 'scp' or  method =='sftp':
          parameters["skip"] = argv[6]
          parameters["args"] = argv[7:]
       else:
          parameters["skip"] = argv[3]
          parameters["args"] = argv[4:]

    if method == 'scp' or method == 'sftp':
       parameters["username"] = argv[3]
       parameters["password"] = argv[4]
       parameters["filename"] = argv[1]

    if func == 'tpcm_uninstall':
       parameters["skip"] = argv[2]
       
    if parameters["username"] != "null":
       options_cmd.append("--username")
       options_cmd.append(parameters["username"])
       
    if parameters["password"] != "null":
       options_cmd.append("--password")
       options_cmd.append(parameters["password"])
       
    if parameters["filename"] != "null":
       options_cmd.append("--filename")
       options_cmd.append(parameters["filename"])

    args_string = " ".join(parameters["args"])
    if args_string != "null":
       options_cmd.append("--args ")
       options_cmd.append("'")
       options_cmd.append(args_string)
       options_cmd.append("'")
       
    if parameters["skip"] == "yes":
       if func == 'tpcm_upgrade':
           options_cmd.append("--skip_data_migration")
       elif func == 'tpcm_uninstall':
           options_cmd.append("--clean_data")
       
    return options_cmd 


def run_tpcm_install(func, method, argv):
    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/operations/sonic-tpcm:tpcm-install')
    templ = argv[2]

    docker_name="name " + argv[0]
    if method == "scp" or method == "sftp":
       image_name= method + " " + argv[5]
    else:
       image_name= method + " " + argv[1]

    options_list = build_options(func, method, argv)

    body = {"sonic-tpcm:input":{"options":' '.join(options_list),"docker-name":docker_name, "image-name": image_name}}

    print "\nInstallation in process .....\n"

    api_response = aa.post(keypath, body)

    if api_response.ok():
        if api_response.content is not None:
            response = api_response.content
            show_cli_output(templ, response)


def run_tpcm_upgrade(func, method, argv):
    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/operations/sonic-tpcm:tpcm-upgrade')
    templ = argv[2]
    docker_name="name " + argv[0]
    if method == "scp" or method == "sftp":
       image_name= method + " " + argv[5]
    else:
       image_name= method + " " + argv[1]
    options_list = build_options(func,method, argv)

    body = {"sonic-tpcm:input":{"options":' '.join(options_list),"docker-name":docker_name, "image-name": image_name}}

    print "\nUpgrade in process .....\n"

    api_response = aa.post(keypath, body)

    if api_response.ok():
        if api_response.content is not None:
            response = api_response.content
            show_cli_output(templ, response)

def run_tpcm_uninstall(func, method, argv):
    aa = cc.ApiClient()
    keypath = cc.Path('/restconf/operations/sonic-tpcm:tpcm-uninstall')
    templ = argv[1]

    options_list = build_options(func,method, argv)
    docker_name="name " + argv[0]

    body = {"sonic-tpcm:input":{"options":' '.join(options_list),"docker-name":docker_name}}

    print "\nUninstallation in process .....\n"

    api_response = aa.post(keypath, body)

    if api_response.ok():
        if api_response.content is not None:
            response = api_response.content
            show_cli_output(templ, response)


def run(func, args):
    if func == 'tpcm_list':
       run_tpcm_list(args)
    if func == 'tpcm_install':
       run_tpcm_install(func, args[0], args[1:])
    if func == 'tpcm_uninstall':
       run_tpcm_uninstall(func, args[0],  args[1:])
    if func == 'tpcm_upgrade':
       run_tpcm_upgrade(func, args[0], args[1:])
    return 


if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])
