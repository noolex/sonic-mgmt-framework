#!/usr/bin/python
import sys
import cli_client as cc
from scripts.render_cli import show_cli_output
import readline

def prompt(msg):
    prompt_msg = msg + " [y/N]: "
    x = raw_input(prompt_msg)
    while x.lower() != "y" and  x.lower() != "n":
        print ("Invalid input, expected [y/N]")
        x = raw_input(prompt_msg)
    if x.lower() == "n":
        return False
    else:
        return True

def invoke_api(func, args):

    api = cc.ApiClient()

    if func ==  'get_sonic_profiles_sonic_profiles':
        path = cc.Path('/restconf/data/sonic-config-mgmt:sonic-default-config-profiles/DEFAULT_CONFIG_PROFILES')
        return api.get(path)
    elif func ==  'set_sonic_profiles_sonic_profiles':
        path = cc.Path('/restconf/operations/sonic-config-mgmt:factory-default-profile')
        body = {
                   "sonic-config-mgmt:input": {
                      "profile-name" : args[0]
                   }
               }
        return api.post(path, body)

def run(func, args):
      try:
           if func ==  'set_sonic_profiles_sonic_profiles':
               if len(args) < 2 or args[1].strip() != 'confirm':
                   confirmed = prompt ("Device configuration will be erased.  You may lose connectivity, continue?")
                   if not confirmed:
                       return

           api_response = invoke_api(func, args)
           if api_response.ok():
                response = api_response.content
                if response is None:
                    print "%Error: No response received. Transaction Failure"
                    return -1
                else:
                    if 'sonic-config-mgmt:output' in response:
                        status = response["sonic-config-mgmt:output"]
                        if status["status"] != 0:
                            print(status["status-detail"])
                    else:
                        if func ==  'get_sonic_profiles_sonic_profiles':
                            show_cli_output(args[0], api_response.content['sonic-config-mgmt:DEFAULT_CONFIG_PROFILES'])
           else:
                if func ==  'set_sonic_profiles_sonic_profiles':
                    print "Applying factory default configuration.  This may take 120--180 seconds and also result in a reboot."
      except:
            # system/network error
            print "%Error: Transaction Failure"
            return -1
