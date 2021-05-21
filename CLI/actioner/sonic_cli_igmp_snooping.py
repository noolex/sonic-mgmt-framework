#!/usr/bin/python
###########################################################################
#
# Copyright 2019 Dell, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###########################################################################

import sys
import json
import collections
import re
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output

l2mc_default_values_map = {
        "querier"           :   False,
        "fast-leave"        :   False,
        "version"           :   2,
        "query-interval"    :   125,
        "lmqi"              :   1000,
        "query-mrt"         :   10
        }
def invoke(func, args):
    body = None
    is_update_oper = False
    aa = cc.ApiClient()
    # Get the rules of all ACL table entries.
    if func == 'get_igmp_snooping_interfaces_interface_state':
        if len(args) >= 2:
            if args[1].lower() == 'snooping':
                if len(args) == 2 or args[2] == '\|':
                    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance=default/protocols/protocol=IGMP_SNOOPING,IGMP-SNOOPING/openconfig-network-instance-deviation:igmp-snooping/interfaces')
                    return aa.get(keypath)
                elif args[2].lower() == 'vlan':
                    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance=default/protocols/protocol=IGMP_SNOOPING,IGMP-SNOOPING/openconfig-network-instance-deviation:igmp-snooping/interfaces/interface=Vlan{vlanid}',
                    vlanid=args[3])
                    return aa.get(keypath)
                elif args[2].lower() == 'groups':
                    if len(args) == 3 or args[3] == '\|':
                        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance=default/protocols/protocol=IGMP_SNOOPING,IGMP-SNOOPING/openconfig-network-instance-deviation:igmp-snooping/interfaces')            
                        return aa.get(keypath)
                    elif len(args) > 3 and args[3].lower() == 'vlan':
                        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance=default/protocols/protocol=IGMP_SNOOPING,IGMP-SNOOPING/openconfig-network-instance-deviation:igmp-snooping/interfaces/interface=Vlan{vlanid}',
                        vlanid=args[4])
                        return aa.get(keypath)                    

    elif func == 'patch_igmp_snooping_interfaces_interface_config' : 
        #keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance=default/protocols/protocol=IGMP_SNOOPING,IGMP-SNOOPING/openconfig-network-instance-deviation:igmp-snooping/interfaces/interface={vlanid}',
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance=default/protocols/protocol=IGMP_SNOOPING,IGMP-SNOOPING/openconfig-network-instance-deviation:igmp-snooping',
                vlanid=args[0])
        
        body=collections.defaultdict(dict)
        
        if len(args) == 1 :
            body = { "openconfig-network-instance-deviation:igmp-snooping": {
                       "interfaces": {
                           "interface": [
                            {
                              "name": args[0],
                              "config" : {
                              "enabled": True
                              }
                            } 
                            ]
                        }
                   }}
            
        elif args[1] == 'querier' :
            body = { "openconfig-network-instance-deviation:igmp-snooping": { 
                       "interfaces": {
                         "interface": [
                         {
                            "name": args[0],
                            "config" : {
                            "querier": True
                            }
                        }
                        ]
                   }}}
            
        elif args[1] == 'fast-leave' :
            body = { "openconfig-network-instance-deviation:igmp-snooping": {
                        "interfaces": {
                            "interface": [
                            {
                                "name": args[0],
                                "config" : {
                                "fast-leave": True
                                }
                            }
                            ]
                            }
                        }
                   }
            
        elif args[1] == 'version' :
            body = { "openconfig-network-instance-deviation:igmp-snooping": {
                        "interfaces": {
                            "interface": [
                            {
                                "name": args[0],
                                "config" : {
                                    "version": int(args[2])
                                    }
                                }
                            ]
                            }
                        }
                   }
            
        elif args[1] == 'query-interval' :
            body = { "openconfig-network-instance-deviation:igmp-snooping": {
                        "interfaces": {
                            "interface": [
                                {
                                    "name": args[0],
                                    "config" : {
                                        "query-interval": int(args[2])
                                        }
                                    }
                                ]
                            }
                        }
                   }
            
        elif args[1] == 'last-member-query-interval' :
            body = { "openconfig-network-instance-deviation:igmp-snooping": {
                        "interfaces": {
                            "interface": [
                                {
                                    "name": args[0],
                                    "config" : {
                                        "last-member-query-interval": int(args[2])
                                        }
                                    }
                                ]
                            }
                        }
                   }
            
        elif args[1] == 'query-max-response-time' :
            body = { "openconfig-network-instance-deviation:igmp-snooping": { 
                        "interfaces": {
                            "interface": [
                                {
                                    "name": args[0],
                                    "config" : {
                                        "query-max-response-time": int(args[2])
                                        }
                                    }
                                ]
                            }
                        }
                   }
            
        elif args[1] == 'mrouter' :
            body = { "openconfig-network-instance-deviation:igmp-snooping": {
                        "interfaces": {
                            "interface": [
                                {
                                    "name": args[0],
                                    "config" : {
                                        "mrouter-interface": [(args[3])]
                                        }
                                    }
                                ]
                            }
                        }
                   }

        elif args[1] == 'static-group' :
            body = {"openconfig-network-instance-deviation:igmp-snooping":{"interfaces":{"interface":[{"config":{"name":args[0]},"name":args[0],"staticgrps":{"static-multicast-group":[{"config":{"outgoing-interface":[args[4]]},"group":args[2],"source-addr":"0.0.0.0"}]}}]}}}
        else:    
            print("%Error: Invalid command")
            exit(1)
        return aa.patch(keypath, body)
    elif func == 'delete_igmp_snooping_interfaces_interface_config' :
        keypath = None
        
        if len(args) == 1 :
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance=default/protocols/protocol=IGMP_SNOOPING,IGMP-SNOOPING/openconfig-network-instance-deviation:igmp-snooping/interfaces/interface={vlanid}',
                vlanid=args[0])
        elif args[1] == 'querier' :
            is_update_oper = True;
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance=default/protocols/protocol=IGMP_SNOOPING,IGMP-SNOOPING/openconfig-network-instance-deviation:igmp-snooping',
                vlanid=args[0])
            body = { "openconfig-network-instance-deviation:igmp-snooping": {
                        "interfaces": {
                            "interface": [
                            {
                                "name": args[0],
                                "config" : {
                                "querier": l2mc_default_values_map['querier']
                                }
                            }
                            ]
                            }
                        }
                   }
        elif args[1] == 'fast-leave' :
            is_update_oper = True
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance=default/protocols/protocol=IGMP_SNOOPING,IGMP-SNOOPING/openconfig-network-instance-deviation:igmp-snooping',
                vlanid=args[0])
            body = { "openconfig-network-instance-deviation:igmp-snooping": {
                        "interfaces": {
                            "interface": [
                            {
                                "name": args[0],
                                "config" : {
                                "fast-leave": l2mc_default_values_map['fast-leave']
                                }
                            }
                            ]
                            }
                        }
                   }
        elif args[1] == 'version' :
            is_update_oper = True
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance=default/protocols/protocol=IGMP_SNOOPING,IGMP-SNOOPING/openconfig-network-instance-deviation:igmp-snooping',
                vlanid=args[0])
            body = { "openconfig-network-instance-deviation:igmp-snooping": {
                        "interfaces": {
                            "interface": [
                            {
                                "name": args[0],
                                "config" : {
                                "version": l2mc_default_values_map['version']
                                }
                            }
                            ]
                            }
                        }
                   }
        elif args[1] == 'query-interval' :
            is_update_oper = True
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance=default/protocols/protocol=IGMP_SNOOPING,IGMP-SNOOPING/openconfig-network-instance-deviation:igmp-snooping',
                vlanid=args[0])
            body = { "openconfig-network-instance-deviation:igmp-snooping": {
                        "interfaces": {
                            "interface": [
                            {
                                "name": args[0],
                                "config" : {
                                "query-interval": l2mc_default_values_map['query-interval']
                                }
                            }
                            ]
                            }
                        }
                   }
        elif args[1] == 'last-member-query-interval' :
            is_update_oper = True
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance=default/protocols/protocol=IGMP_SNOOPING,IGMP-SNOOPING/openconfig-network-instance-deviation:igmp-snooping',
                vlanid=args[0])
            body = { "openconfig-network-instance-deviation:igmp-snooping": {
                        "interfaces": {
                            "interface": [
                            {
                                "name": args[0],
                                "config" : {
                                "last-member-query-interval": l2mc_default_values_map['lmqi']
                                }
                            }
                            ]
                            }
                        }
                   }
        elif args[1] == 'query-max-response-time' :
            is_update_oper = True
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance=default/protocols/protocol=IGMP_SNOOPING,IGMP-SNOOPING/openconfig-network-instance-deviation:igmp-snooping',
                vlanid=args[0])
            body = { "openconfig-network-instance-deviation:igmp-snooping": {
                        "interfaces": {
                            "interface": [
                            {
                                "name": args[0],
                                "config" : {
                                "query-max-response-time": l2mc_default_values_map['query-mrt']
                                }
                            }
                            ]
                            }
                        }
                   }
        elif args[1] == 'mrouter' :
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance=default/protocols/protocol=IGMP_SNOOPING,IGMP-SNOOPING/openconfig-network-instance-deviation:igmp-snooping/interfaces/interface={vlanid}/config/mrouter-interface={ifname}',
                vlanid=args[0], ifname=args[3])
        elif args[1] == 'static-group' :
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance=default/protocols/protocol=IGMP_SNOOPING,IGMP-SNOOPING/openconfig-network-instance-deviation:igmp-snooping/interfaces/interface={vlanid}/staticgrps/static-multicast-group={grpAddr},0.0.0.0/config/outgoing-interface={ifname}',
                vlanid=args[0], grpAddr=args[2], ifname=args[4])
            api_response = aa.delete (keypath)
            if api_response.ok():
                keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance=default/protocols/protocol=IGMP_SNOOPING,IGMP-SNOOPING/openconfig-network-instance-deviation:igmp-snooping/interfaces/interface={vlanid}/staticgrps/static-multicast-group={grpAddr},0.0.0.0/config/outgoing-interface',
                                  vlanid=args[0], grpAddr=args[2])
                get_response = aa.get(keypath)
                if get_response.ok() and len(get_response.content) == 0:
                    keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance=default/protocols/protocol=IGMP_SNOOPING,IGMP-SNOOPING/openconfig-network-instance-deviation:igmp-snooping/interfaces/interface={vlanid}/staticgrps/static-multicast-group={grpAddr},0.0.0.0',
                        vlanid=args[0], grpAddr=args[2])
                    return aa.delete (keypath)
                else:
                    return api_response
            else:
                return api_response
        else:    
            print("%Error: Invalid command")
            exit(1)
            
        if is_update_oper:
            return aa.patch (keypath, body)
        else:
            return aa.delete (keypath)
    else:
        print("%Error: not implemented")
        exit(1)

def run(func, args):
    try:
        api_response = invoke(func, args)
        if api_response.ok():
            response = api_response.content
            if response is None:
                return
            elif len(args) >= 3 and args[2].lower() == 'groups':
                if 'openconfig-network-instance-deviation:interfaces' in response.keys():
                    value = response['openconfig-network-instance-deviation:interfaces']
                    if value is None:
                        return
                    show_cli_output('show_igmp_snooping-groups.j2', value)
                elif 'openconfig-network-instance-deviation:interface' in response.keys():
                    show_cli_output('show_igmp_snooping-groups.j2', response)
            elif (len(args) >= 2 and args[1].lower() == 'snooping') or (len(args) >= 4 and args[2].lower() == 'vlan'):
                if 'openconfig-network-instance-deviation:interfaces' in response.keys():
                    value = response['openconfig-network-instance-deviation:interfaces']
                    if value is None:
                        return
                    show_cli_output(args[0], value)
                elif 'openconfig-network-instance-deviation:interface' in response.keys():
                    show_cli_output(args[0], response)
            else:
                print "%Error: Invalid command"
        else:
            #error response
            print api_response.error_message()

    except Exception:
        # system/network error
        print "%Error: Transaction Failure"

if __name__ == '__main__':
    pipestr().write(sys.argv)
    #pdb.set_trace()
    run(sys.argv[1], sys.argv[2:])

