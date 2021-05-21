import sys
import json
import collections
import re
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
from swsssdk import ConfigDBConnector
import urllib3
urllib3.disable_warnings()

def invoke_api(func, args):
    body = None
    api = cc.ApiClient()

    # Set/Get the rules of all DROP MONITOR table entries.

    if func == 'get_openconfig_system_ext_system_swresource':
      path = cc.Path('/restconf/data/openconfig-system:system/openconfig-system-ext:swresource')
      return api.get(path)


    elif func == 'patch_openconfig_system_ext_system_swresource':
       path = cc.Path('/restconf/data/openconfig-system:system/openconfig-system-ext:swresource')
       if args[0] == "min":
	       flowlimit = "MIN"
       elif args[0] == "none":
               flowlimit = "NONE"

       body =  {
                "openconfig-system-ext:swresource": {
                         "resource": [
                           {
                            "name": "DROP_MONITOR",
                            "config": {
                            "name": "DROP_MONITOR",
                            "flows": flowlimit
                             }
                            }
                                     ]
                                                     }
                }

       return api.patch(path, body)


    elif func == 'delete_openconfig_system_ext_system_swresource':
        path = cc.Path('/restconf/data/openconfig-system:system/openconfig-system-ext:swresource',)
        return api.delete(path)

    # check paths and data
    elif func == 'patch_openconfig_system_ext_system_swresource_routes':
        path = cc.Path('/restconf/data/openconfig-system:system/openconfig-system-ext:swresource')

        if args[0] == "default":
	        routescale = "DEFAULT"
        elif args[0] == "max":
            routescale = "MAX"

        print "L2, L3 host and route scaling numbers may change. Config save, reboot is required for this change to take effect"

        body =  {
                "openconfig-system-ext:swresource": {
                        "resource": [
                                        {
                                        "name": "ROUTE_SCALE",
                                        "config": {
                                            "name": "ROUTE_SCALE",
                                            "routes": routescale
                                            }
                                        }
                                    ]
                        }
                }

        return api.patch(path, body)


    return api.cli_not_implemented(func)

def run(func, args):

    response = invoke_api(func, args)
    if response.ok():
        if response.content is not None:
            # Get Command Output
            api_response = response.content

            if api_response is None:
                print("Failed")
            elif func == 'get_openconfig_system_ext_system_swresource':
                show_cli_output(args[0], api_response)
            else:
                return

    else:
            api_response = response.content
            if "ietf-restconf:errors" in api_response:
                 err = api_response["ietf-restconf:errors"]
                 if "error" in err:
                     errList = err["error"]

                     errDict = {}
                     for dict in errList:
                         for k, v in dict.iteritems():
                              errDict[k] = v

                     if "error-message" in errDict:
                         print "%Error: " + errDict["error-message"]
                         return
                     print "%Error: Transaction Failure"
                     return
            print response.error_message()
            print "%Error: Transaction Failure"

if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])
