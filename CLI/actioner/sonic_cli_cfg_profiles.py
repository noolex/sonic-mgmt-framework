#!/usr/bin/python
import sys
import cli_client as cc
from scripts.render_cli import show_cli_output

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
                    print "Device configuration is being modified. You may lose connectivity."
      except:
            # system/network error
            print "%Error: Transaction Failure"
            return -1
