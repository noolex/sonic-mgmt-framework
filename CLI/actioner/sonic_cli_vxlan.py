#!/usr/bin/python
###########################################################################
#
# Copyright 2019 Broadcom.  The term "Broadcom" refers to Broadcom Inc. and/or
# its subsidiaries.
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
import pdb
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output

vxlan_global_info = []

def config_response_handler(api_response, func, args):
    if api_response.ok():
        resp_content = api_response.content
        if resp_content is not None:
            print("Error: {}".format(str(resp_content)))
    else:
        try:
            error_data = api_response.content['ietf-restconf:errors']['error'][0]
            err_app_tag = 'NOERROR'
            err_msg = 'NOERROR'
            err_tag = 'NOERROR'

            if 'error-app-tag' in error_data: 
               err_app_tag = error_data['error-app-tag'] 

            if 'error-message' in error_data: 
               err_msg = error_data['error-message']

            if 'error-tag' in error_data: 
               err_tag = error_data['error-tag']

            if err_app_tag is not 'NOERROR': 
                #err_app_tag = error_data['error-app-tag'] 
                #err_msg = error_data['error-message']
                if err_app_tag == 'too-many-elements':
                   if (func == 'patch_sonic_vxlan_sonic_vxlan_vxlan_tunnel_vxlan_tunnel_list'):
                     print('Error: VTEP already configured')
                   elif (func == 'patch_sonic_vxlan_sonic_vxlan_evpn_nvo_evpn_nvo_list'):
                     print('Error: EVPN NVO already configured')
                elif err_app_tag == 'not-unique-vlanid':
                   print('Error: Vlan Id already mapped')
                elif err_app_tag == 'not-unique-vni':
                   print('Error: VNI Id already mapped')
                elif err_app_tag == 'vnid-invalid':
                   print('Error: Invalid VNI. Valid range [1 to 16777215]')
                elif err_app_tag == 'invalid-vtep-name':
                   print('Error: VTEP name should start with "vtep"')
                elif err_app_tag == 'instance-required':
                   if err_msg is not None:
                      print("Error: {}".format(err_msg))
                   else:
                      print err_app_tag
                else :
                   if err_msg is not None:
                      print("{}".format(err_msg))
                   else:
                      print('Error: err-app-tag {}'.format(str(err_app_tag)))
            elif err_tag is not 'NOERROR': 
                if (func == 'delete_sonic_vxlan_sonic_vxlan_vxlan_tunnel_vxlan_tunnel_list'):
                    print("Error: Please delete EVPN NVO and VLAN VNI mappings.")
                elif (func == 'delete_sonic_vxlan_sonic_vxlan_vxlan_tunnel_map_vxlan_tunnel_map_list'):
                    vidstr = args[0]
                    vnid = args[1]
                    print("Error: Please check VLAN {}, VNI {} mapping is configured".format(vidstr, vnid))
                else:
                    print("Error: {}".format(err_tag))
            else:
                print error_data
                print(api_response.error_message())

        except Exception as e:
            print(api_response.error_message())

def invoke(func, args):
    body = None
    aa = cc.ApiClient()


    #[un]configure VTEP 
    if (func == 'patch_sonic_vxlan_sonic_vxlan_vxlan_tunnel_vxlan_tunnel_list' or
        func == 'delete_sonic_vxlan_sonic_vxlan_vxlan_tunnel_vxlan_tunnel_list'):
        keypath = cc.Path('/restconf/data/sonic-vxlan:sonic-vxlan/VXLAN_TUNNEL/VXLAN_TUNNEL_LIST={name}', name=args[0])

        if (func.startswith("patch") is True):
            return aa.patch(keypath)
        else:
            keypath_nvo = cc.Path('/restconf/data/sonic-vxlan:sonic-vxlan/EVPN_NVO/EVPN_NVO_LIST={name}', name='nvo1')
            api_response = aa.get(keypath_nvo)
            response = api_response.content
            if len(response) != 0:
                response = aa.delete(keypath_nvo)
                if response.ok():
                    return aa.delete(keypath)
                else:
                    return response
            else:
                return aa.delete(keypath)


    #[un]configure VTEP srcip
    if (func == 'patch_sonic_vxlan_sonic_vxlan_vxlan_tunnel_vxlan_tunnel_list_src_ip' or
        func == 'delete_sonic_vxlan_sonic_vxlan_vxlan_tunnel_vxlan_tunnel_list_src_ip'):
        keypath = cc.Path('/restconf/data/sonic-vxlan:sonic-vxlan/VXLAN_TUNNEL/VXLAN_TUNNEL_LIST={name}/src_ip', name=args[0][6:])

        if (func.startswith("patch") is True):
            body = {
              "sonic-vxlan:src_ip": args[1]
            }
            response = aa.patch(keypath, body)
            if response.ok():
                keypath = cc.Path('/restconf/data/sonic-vxlan:sonic-vxlan/EVPN_NVO/EVPN_NVO_LIST={name}', name='nvo1')
                body = {
                "sonic-vxlan:EVPN_NVO_LIST": [
                    {
                    "name": 'nvo1',
                    "source_vtep": args[0][6:] 
                    }
                ]
                }
                return aa.patch(keypath, body)
            else:
                return response
        else:
            keypath_nvo = cc.Path('/restconf/data/sonic-vxlan:sonic-vxlan/EVPN_NVO/EVPN_NVO_LIST={name}', name='nvo1')
            api_response = aa.get(keypath_nvo)
            response = api_response.content
            if len(response) != 0:
                response = aa.delete(keypath_nvo)
                if response.ok():
                    return aa.delete(keypath)
                else:
                    return response
            else:
                return aa.delete(keypath)

    if (func == 'patch_sonic_vxlan_sonic_vxlan_vxlan_tunnel_vxlan_tunnel_list_qos_mode'):
        keypath = cc.Path('/restconf/data/sonic-vxlan:sonic-vxlan/VXLAN_TUNNEL/VXLAN_TUNNEL_LIST={name}', name=args[0][6:])
        print func
        print args

        dscp_val = 0
        if (len(args) == 3):
            dscp_val = int(args[2])

        body = {
                "sonic-vxlan:VXLAN_TUNNEL_LIST": [
                    {
                        "name":args[0][6:],
                        "qos-mode":args[1],
                        "dscp":dscp_val
                    } 
                ]
        }

        response = aa.patch(keypath,body)
        return response 

    #[un]configure Tunnel Map
    if (func == 'patch_sonic_vxlan_sonic_vxlan_vxlan_tunnel_map_vxlan_tunnel_map_list' or
        func == 'delete_sonic_vxlan_sonic_vxlan_vxlan_tunnel_map_vxlan_tunnel_map_list'):
        if args[0] == "vrf":
            keypath = cc.Path('/restconf/data/sonic-vrf:sonic-vrf/VRF/VRF_LIST={vrf_name}/vni', vrf_name=args[3])
            if (func.startswith("patch") is True):
                body = { "sonic-vrf:vni": int(args[2])}
            else:
                 body = { "sonic-vrf:vni": 0}

            api_response =  aa.patch(keypath, body)
            config_response_handler(api_response, func, args)
            return api_response
        else:
            fail = 0
            keypath = cc.Path('/restconf/data/sonic-vxlan:sonic-vxlan/VXLAN_TUNNEL_MAP/VXLAN_TUNNEL_MAP_LIST')
            maplist = []
            countinput = 0

            if (len(args) == 5):
                countinput = int(args[4])
            else:
                countinput = 1

            for count in range(countinput):
              vidstr = str(int(args[3]) + count)
              vnid = int(args[2]) + count
              vnistr = str(vnid)
              mapname = 'map_'+ vnistr + '_' + 'Vlan' + vidstr
              resp_args = [vidstr, vnistr]

              if (func.startswith("delete") is True):
                delkeypath = cc.Path('/restconf/data/sonic-vxlan:sonic-vxlan/VXLAN_TUNNEL_MAP/VXLAN_TUNNEL_MAP_LIST={name},{mapname1}', name=args[1][6:], mapname1=mapname)
                api_response = aa.delete(delkeypath)
                config_response_handler(api_response, func, resp_args)

              else:
                listobj = {
                    "name": args[1][6:],
                    "mapname": mapname,
                    "vlan": 'Vlan' + vidstr,
                    "vni": vnid
                    }
                maplist.append(listobj)

            if (func.startswith("patch") is True):
               body = {
                   "sonic-vxlan:VXLAN_TUNNEL_MAP_LIST": maplist
               }
               api_response =  aa.patch(keypath, body)
               config_response_handler(api_response, func, args)

        return api_response

    if func == "get_list_sonic_vxlan_sonic_vxlan_vxlan_tunnel_vxlan_tunnel_list":
        keypath = cc.Path('/restconf/data/sonic-vxlan:sonic-vxlan/VXLAN_TUNNEL/VXLAN_TUNNEL_LIST')
        return aa.get(keypath)

    if func == "get_list_sonic_vxlan_sonic_vxlan_evpn_nvo_evpn_nvo_list":
        keypath = cc.Path('/restconf/data/sonic-vxlan:sonic-vxlan/EVPN_NVO/EVPN_NVO_LIST')
        return aa.get(keypath)

    if func == "get_sonic_loopback_interface_sonic_loopback_interface_loopback_interface":
        keypath = cc.Path('/restconf/data/sonic-loopback-interface:sonic-loopback-interface/LOOPBACK_INTERFACE')
        return aa.get(keypath)

    if func == "get_list_sonic_vxlan_sonic_vxlan_vxlan_tunnel_map_vxlan_tunnel_map_list":
        keypath = cc.Path('/restconf/data/sonic-vxlan:sonic-vxlan/VXLAN_TUNNEL_MAP/VXLAN_TUNNEL_MAP_LIST')
        return aa.get(keypath)

    if func == "get_list_sonic_vxlan_tunnel_vrf_vni_map_list":
        keypath = cc.Path('/restconf/data/sonic-vrf:sonic-vrf/VRF/VRF_LIST')
        return aa.get(keypath)

    if func == "get_list_sonic_vxlan_sonic_vxlan_vxlan_tunnel_table_vxlan_tunnel_table_list":
        keypath = cc.Path('/restconf/data/sonic-vxlan:sonic-vxlan/VXLAN_TUNNEL_TABLE/VXLAN_TUNNEL_TABLE_LIST')
        return aa.get(keypath)

    if func == "get_list_sonic_vxlan_sonic_vxlan_evpn_remote_vni_table_evpn_remote_vni_table_list":
        keypath = cc.Path('/restconf/data/sonic-vxlan:sonic-vxlan/EVPN_REMOTE_VNI_TABLE/EVPN_REMOTE_VNI_TABLE_LIST')
        return aa.get(keypath)

    if func == "get_list_sonic_vxlan_sonic_vxlan_fdb_table_vxlan_fdb_table_list":
        keypath = cc.Path('/restconf/data/sonic-vxlan:sonic-vxlan/VXLAN_FDB_TABLE/VXLAN_FDB_TABLE_LIST')
        return aa.get(keypath)

    #[un]configure VRF VNI MAP
    if (func == 'patch_sonic_vxlan_map_vrf_vni_list' or
        func == 'delete_sonic_vxlan_map_vrf_vni_list'):
        #keypath = cc.Path('/restconf/data/sonic-vrf:sonic-vrf/VRF/VRF_LIST={vrf_name}', vrf_name=args[2])
        keypath = cc.Path('/restconf/data/sonic-vrf:sonic-vrf/VRF/VRF_LIST={vrf_name}/vni', vrf_name=args[2])

        if (func.startswith("patch") is True):
        #body = {
        #   "sonic-vrf:VRF_LIST": [
        #       {
        #            "vrf_name": args[2],
        #            "vni": int(args[1])
        #       }
        #   ]
        # }
            body = { "sonic-vrf:vni": int(args[1])}
        else:
            body = { "sonic-vrf:vni": 0}
        return aa.patch(keypath, body)

    #[un]configure Neighbour Suppression
    if (func == 'patch_sonic_vxlan_sonic_vxlan_suppress_vlan_neigh_suppress_vlan_neigh_list' or
        func == 'delete_sonic_vxlan_sonic_vxlan_suppress_vlan_neigh_suppress_vlan_neigh_list'):
        print args[0]
        keypath = cc.Path('/restconf/data/sonic-vxlan:sonic-vxlan/SUPPRESS_VLAN_NEIGH/SUPPRESS_VLAN_NEIGH_LIST={name}', name=args[0])

        if (func.startswith("patch") is True):
            body = {
                "sonic-vxlan:SUPPRESS_VLAN_NEIGH_LIST": [
                {
                    "name": args[0],
                    "suppress": 'on'
                }
             ]
            }
            return aa.patch(keypath, body)
        else:
            return aa.delete(keypath)
    else:
        print("Error: not implemented")
        exit(1)

    return api_response

#show vxlan interface 
def vxlan_show_vxlan_interface(args):
    print ""
    api_response = invoke("get_list_sonic_vxlan_sonic_vxlan_vxlan_tunnel_vxlan_tunnel_list", args)
    if api_response.ok():
        response = api_response.content
    if response is None:
        print("no vxlan configuration")
    elif response is not None:
        if len(response) != 0:
            tunnel_list = response['sonic-vxlan:VXLAN_TUNNEL_LIST']
            for item in tunnel_list:
                source_vtep_ip = item['src_ip']
            show_cli_output(args[0],response)

    api_response = invoke("get_list_sonic_vxlan_sonic_vxlan_evpn_nvo_evpn_nvo_list", args)                                                                      
    if api_response.ok():
        response = api_response.content
        if response is None:
            print("no evpn configuration")
        elif response is not None:
            if len(response) != 0:
                show_cli_output(args[0],response)

    api_response = invoke("get_sonic_loopback_interface_sonic_loopback_interface_loopback_interface", args)                                                                      
    if api_response.ok():
        response = api_response.content
        if response is None:
            print("no evpn configuration")
        elif response is not None:
            if len(response) != 0:
                found = False
                if 'sonic-loopback-interface:LOOPBACK_INTERFACE' in response:
                    loopback_intf_container = response['sonic-loopback-interface:LOOPBACK_INTERFACE']
                    if 'LOOPBACK_INTERFACE_IPADDR_LIST' in loopback_intf_container:
                        loopback_ipaddr_list = loopback_intf_container['LOOPBACK_INTERFACE_IPADDR_LIST']
                        for item in loopback_ipaddr_list:
                            loop_if_prefix = item['ip_prefix']
                            loop_if_prefix = loop_if_prefix.split('/')
                            loop_if_ipaddr = loop_if_prefix[0]
                            if source_vtep_ip == loop_if_ipaddr:
                                response['sonic-loopback-interface:LOOPBACK_INTERFACE']['src_if'] = item['loIfName']
                                found = True
                                break 
                if found is False: 
                    response['sonic-loopback-interface:LOOPBACK_INTERFACE']['src_if'] = "Not Configured"
                show_cli_output(args[0],response)
    return

#show vxlan vlan vni map 
def vxlan_show_vxlan_vlanvnimap(args):
    print("")
    api_response = invoke("get_list_sonic_vxlan_sonic_vxlan_vxlan_tunnel_map_vxlan_tunnel_map_list", args)
    if api_response.ok():
        response = api_response.content
    if response is None:
        print("no vxlan configuration")
    elif response is not None:
        if (args[1] == 'show'):
            if len(response) != 0:
                show_cli_output(args[0], response)
        elif (args[1] == 'count'):
            if 'sonic-vxlan:VXLAN_TUNNEL_MAP_LIST' in response:
                vlan_vni_map_list = response['sonic-vxlan:VXLAN_TUNNEL_MAP_LIST']
                vlan_vni_map_list_len = str(len(vlan_vni_map_list))
                print("Total Count: " + vlan_vni_map_list_len)
            else:
                print("Total Count: 0")
    return

#show vxlan vrf vni map 
def vxlan_show_vxlan_vrfvnimap(args):
    print("")
    iter_len = 0
    api_response = invoke("get_list_sonic_vxlan_tunnel_vrf_vni_map_list", args)
    if api_response.ok():
        response = api_response.content
    if response is None:
        print("no vrf configuration")
    elif response is not None:
        if len(response) != 0:
            if (args[1] == 'show'):
                vrf_list = response['sonic-vrf:VRF_LIST'][0]
                for iter in vrf_list:
                    iter_len = len(iter)
                    if (iter_len == 3):
                        show_cli_output(args[0], response)
            elif (args[1] == 'count'):
                vrf_map_count = 0
                if 'sonic-vrf:VRF_LIST' in response:
                    vrf_map_list = response['sonic-vrf:VRF_LIST']
                    for tunnel in vrf_map_list:
                        if 'vni' in tunnel and tunnel['vni'] != '' and tunnel['vni'] != 0:
                            vrf_map_count += 1
                    print("Total Count: " + str(vrf_map_count))
                else:
                    print("Total Count: 0")
    return

#show vxlan tunnel 
def vxlan_show_vxlan_tunnel(args):
    print("")
    api_response = invoke("get_list_sonic_vxlan_sonic_vxlan_vxlan_tunnel_table_vxlan_tunnel_table_list", args)
    if api_response.ok():
        response = api_response.content
    if response is None:
        print("no vxlan configuration")
    elif response is not None:
        if (args[1] == 'show'):
            if len(response) != 0:
                show_cli_output(args[0], response)
        elif (args[1] == 'count'):
            if 'sonic-vxlan:VXLAN_TUNNEL_TABLE_LIST' in response:
                tnl_list = response['sonic-vxlan:VXLAN_TUNNEL_TABLE_LIST']
                tnl_list_len = str(len(tnl_list))
                print("Total Count: " + tnl_list_len)
            else:
                print("Total Count: 0")
    return

#show vxlan evpn remote vni
def vxlan_show_vxlan_evpn_remote_vni(args):
    print("")
    arg_length = len(args);
    api_response = invoke("get_list_sonic_vxlan_sonic_vxlan_evpn_remote_vni_table_evpn_remote_vni_table_list", args)
    if api_response.ok():
        response = api_response.content
    if response is None:
        print("no vxlan evpn remote vni entires")
    elif response is not None:
        if 'sonic-vxlan:EVPN_REMOTE_VNI_TABLE_LIST' in response:
            index = 0
            while (index < len(response['sonic-vxlan:EVPN_REMOTE_VNI_TABLE_LIST'])):
                iter = response['sonic-vxlan:EVPN_REMOTE_VNI_TABLE_LIST'][index] 
                if (arg_length == 3 and (args[2] != iter['remote_vtep'])):
                    response['sonic-vxlan:EVPN_REMOTE_VNI_TABLE_LIST'].pop(index)
                else:
                    index = index + 1
            if (args[1] == 'show'):
                show_cli_output(args[0], response)
            elif (args[1] == 'count'):
                if 'sonic-vxlan:EVPN_REMOTE_VNI_TABLE_LIST' in response:
                    remote_vni_list = response['sonic-vxlan:EVPN_REMOTE_VNI_TABLE_LIST']
                    remote_vni_list_len = str(len(remote_vni_list))
                    print("Total Count: " + remote_vni_list_len)
                else:
                    print("Total Count: 0")
        else:
            print("Total Count: 0")
    return

#show vxlan evpn remote mac
def vxlan_show_vxlan_evpn_remote_mac(args):
    print("")
    arg_length = len(args);
    api_response = invoke("get_list_sonic_vxlan_sonic_vxlan_fdb_table_vxlan_fdb_table_list", args)
    if api_response.ok():
        response = api_response.content
    if response is None:
        print("no vxlan fdb entries")
    elif response is not None:
        if 'sonic-vxlan:VXLAN_FDB_TABLE_LIST' in response:
            index = 0
            while (index < len(response['sonic-vxlan:VXLAN_FDB_TABLE_LIST'])):
                iter = response['sonic-vxlan:VXLAN_FDB_TABLE_LIST'][index] 
                if (arg_length == 3 and (args[2] != iter['remote_vtep'])):
                    response['sonic-vxlan:VXLAN_FDB_TABLE_LIST'].pop(index)
                else:
                    index = index + 1
            if (args[1] == 'show'):
                show_cli_output(args[0], response)
            elif (args[1] == 'count'):
                if 'sonic-vxlan:VXLAN_FDB_TABLE_LIST' in response:
                    remote_mac_list = response['sonic-vxlan:VXLAN_FDB_TABLE_LIST']
                    remote_mac_list_len = str(len(remote_mac_list))
                    print("Total Count: " + remote_mac_list_len)
                else:
                    print("Total Count: 0")
        else:
            print("Total Count: 0")
    return

def run(func, args):
    #show commands
    try:
        #show vxlan brief command
        if func == 'show_vxlan_interface':
            vxlan_show_vxlan_interface(args)
            return
        if func == 'show_vxlan_vlanvnimap':
            vxlan_show_vxlan_vlanvnimap(args)
            return
        if func == 'show_vxlan_vrfvnimap':
            vxlan_show_vxlan_vrfvnimap(args)
            return
        if func == 'show_vxlan_tunnel':
            vxlan_show_vxlan_tunnel(args)
            return
        if func == 'show_vxlan_remote_vni':
            vxlan_show_vxlan_evpn_remote_vni(args)
            return
        if func == 'show_vxlan_remote_mac':
            vxlan_show_vxlan_evpn_remote_mac(args)
            return

    except Exception as e:
            print(sys.exc_value)
            return


    #config commands
    try:
        api_response = invoke(func, args)

        if (func != 'patch_sonic_vxlan_sonic_vxlan_vxlan_tunnel_map_vxlan_tunnel_map_list' and
            func != 'delete_sonic_vxlan_sonic_vxlan_vxlan_tunnel_map_vxlan_tunnel_map_list'):
          config_response_handler(api_response,func,args)

    except:
            # system/network error
            print("Error: Transaction Failure")


if __name__ == '__main__':
    pipestr().write(sys.argv)
    #pdb.set_trace()
    run(sys.argv[1], sys.argv[2:])
