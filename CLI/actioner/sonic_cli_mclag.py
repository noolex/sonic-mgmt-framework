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
import time
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output

MCLAG_DEFAULT_DELAY_RESTORE = 300

def invoke(func, args):
    body = None
    aa = cc.ApiClient()

    #######################################
    # Configure  MCLAG Domain Table - START
    #######################################

    # Create MCLAG Domain
    if (func == 'patch_list_sonic_mclag_sonic_mclag_mclag_domain_mclag_domain_list'):
        #keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_DOMAIN/MCLAG_DOMAIN_LIST={domain_id}', domain_id=args[0])
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_DOMAIN/MCLAG_DOMAIN_LIST')
        body =  {
            "sonic-mclag:MCLAG_DOMAIN_LIST": [
            { 
                    "domain_id": int(args[0])
            }
            ]
        }
        return aa.patch(keypath, body)



    #[un]configure local IP Address
    if (func == 'patch_sonic_mclag_sonic_mclag_mclag_domain_mclag_domain_list_source_ip' or
        func == 'delete_sonic_mclag_sonic_mclag_mclag_domain_mclag_domain_list_source_ip'):
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_DOMAIN/MCLAG_DOMAIN_LIST={domain_id}/source_ip', domain_id=args[0])

        if (func.startswith("patch") is True):
            body = {
                "sonic-mclag:source_ip": args[1]
            }
            return aa.patch(keypath, body)
        else:
            return aa.delete(keypath)

    #[un]configure Peer IP Address
    if (func == 'patch_sonic_mclag_sonic_mclag_mclag_domain_mclag_domain_list_peer_ip' or
        func == 'delete_sonic_mclag_sonic_mclag_mclag_domain_mclag_domain_list_peer_ip'):
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_DOMAIN/MCLAG_DOMAIN_LIST={domain_id}/peer_ip', domain_id=args[0])

        if (func.startswith("patch") is True):
            body = {
                "sonic-mclag:peer_ip": args[1]
            }
            return aa.patch(keypath, body)
        else:
            return aa.delete(keypath)

    #[un]configure Peer Link
    if (func == 'patch_sonic_mclag_sonic_mclag_mclag_domain_mclag_domain_list_peer_link' or
        func == 'delete_sonic_mclag_sonic_mclag_mclag_domain_mclag_domain_list_peer_link'):
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_DOMAIN/MCLAG_DOMAIN_LIST={domain_id}/peer_link', domain_id=args[0])

        if (func.startswith("patch") is True):
            if_name = None
            if_name = args[1]
            body = {
                "sonic-mclag:peer_link": if_name
            }
            return aa.patch(keypath, body)
        else:
            return aa.delete(keypath)

    #[un]configure Keepalive interval 
    if (func == 'patch_sonic_mclag_sonic_mclag_mclag_domain_mclag_domain_list_keepalive_interval' or
        func == 'delete_sonic_mclag_sonic_mclag_mclag_domain_mclag_domain_list_keepalive_interval'):
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_DOMAIN/MCLAG_DOMAIN_LIST={domain_id}/keepalive_interval', domain_id=args[0])

        if (func.startswith("patch") is True):
            body = {
                "sonic-mclag:keepalive_interval": int(args[1])
            }
            return aa.patch(keypath, body)
        else:
            return aa.delete(keypath)

    #configure session Timeout
    if (func == 'patch_sonic_mclag_sonic_mclag_mclag_domain_mclag_domain_list_session_timeout' or
        func == 'delete_sonic_mclag_sonic_mclag_mclag_domain_mclag_domain_list_session_timeout'):
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_DOMAIN/MCLAG_DOMAIN_LIST={domain_id}/session_timeout', domain_id=args[0])

        if (func.startswith("patch") is True):
            body = {
                "sonic-mclag:session_timeout": int(args[1])
            }
            return aa.patch(keypath, body)
        else:
            return aa.delete(keypath)

	#[un]configure mclag system Mac
    if (func == 'patch_sonic_mclag_sonic_mclag_mclag_domain_mclag_domain_list_mclag_system_mac' or
        func == 'delete_sonic_mclag_sonic_mclag_mclag_domain_mclag_domain_list_mclag_system_mac'):
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_DOMAIN/MCLAG_DOMAIN_LIST={domain_id}/mclag_system_mac', domain_id=args[0])

        if (func.startswith("patch") is True):
            body = {
                "sonic-mclag:mclag_system_mac": args[1]
            }
            return aa.patch(keypath, body)
        else:
            return aa.delete(keypath)

    #Configure and unconfigure delay restore time
    if (func == 'patch_sonic_mclag_sonic_mclag_mclag_domain_mclag_domain_list_delay_restore' or
        func == 'delete_sonic_mclag_sonic_mclag_mclag_domain_mclag_domain_list_delay_restore'):
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_DOMAIN/MCLAG_DOMAIN_LIST={domain_id}/delay_restore', domain_id=args[0])

        if (func.startswith("patch") is True):
            body = {
                "sonic-mclag:delay_restore": int(args[1])
            }
            return aa.patch(keypath, body)
        else:
            return aa.delete(keypath)

    #delete MCLAG Domain 
    if (func == 'delete_sonic_mclag_sonic_mclag_mclag_domain_mclag_domain_list'):
        api_response = invoke("get_sonic_mclag_sonic_mclag", args[1:])
        response = {}
        if api_response.ok():
            response = api_response.content
            if len(response) != 0 and 'MCLAG_DOMAIN' in response['sonic-mclag:sonic-mclag']:
                mclag_local_if_list  = []
                if "MCLAG_INTERFACE" in response["sonic-mclag:sonic-mclag"]:
                    mclag_local_if_list = response['sonic-mclag:sonic-mclag']['MCLAG_INTERFACE']['MCLAG_INTERFACE_LIST']
                    for list_item  in mclag_local_if_list:
                        dmid=list_item["domain_id"]
                        if str(args[0]) == str(dmid):
                            iname=list_item["if_name"]
                            print("Removing interface "+ str(iname)+" from domain "+str(dmid))
                            keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_INTERFACE/MCLAG_INTERFACE_LIST={domain_id},{if_name}', domain_id=args[0], if_name=iname)
                            aa.delete(keypath)
                mclag_unique_ip_list  = []
                if "MCLAG_UNIQUE_IP" in response["sonic-mclag:sonic-mclag"]:
                    mclag_unique_ip_list = response['sonic-mclag:sonic-mclag']['MCLAG_UNIQUE_IP']['MCLAG_UNIQUE_IP_LIST']
                    for list_item  in mclag_unique_ip_list:
                        iname=list_item["if_name"]
                        print("Removing mclag-separate-ip from "+ str(iname))
                        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_UNIQUE_IP/MCLAG_UNIQUE_IP_LIST={if_name}', if_name=iname)
                        aa.delete(keypath)
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_DOMAIN/MCLAG_DOMAIN_LIST={domain_id}', domain_id=args[0])
        return aa.delete(keypath)

    

    #######################################
    # Configure  MCLAG Domain Table - END
    #######################################


    #######################################
    # Configure  MCLAG Interface Table - START
    #######################################
    if (func == 'patch_sonic_mclag_sonic_mclag_mclag_interface_mclag_interface_list'):
        #keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_INTERFACE/MCLAG_INTERFACE_LIST={domain_id},{if_name}',
        #        domain_id=args[0], if_name=args[1])
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_INTERFACE/MCLAG_INTERFACE_LIST' )
        body = {
            "sonic-mclag:MCLAG_INTERFACE_LIST": [
            {
                "domain_id":int(args[0]),
                "if_name":args[1],
                "if_type":"PortChannel"
            }
          ]
        }
        return aa.patch(keypath, body)

    if (func == 'delete_sonic_mclag_sonic_mclag_mclag_interface_mclag_interface_list'):
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_INTERFACE/MCLAG_INTERFACE_LIST={domain_id},{if_name}',
                domain_id=(args[0]), if_name=args[1])
        return aa.delete(keypath)

    #######################################
    # Configure  MCLAG Domain Table - END
    #######################################

    #######################################
    # Configure  MCLAG Unique IP Table - START
    #######################################
    if (func == 'patch_sonic_mclag_seperate_ip_list'):
        #keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_UNIQUE_IP/MCLAG_UNIQUE_IP_LIST={if_name}',
        #        if_name=args[0])
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_UNIQUE_IP/MCLAG_UNIQUE_IP_LIST' )
        body = {
            "sonic-mclag:MCLAG_UNIQUE_IP_LIST": [
            {
                "if_name":args[0],
                "unique_ip":"enable"
            }
          ]
        }
        return aa.patch(keypath, body)

    if (func == 'delete_sonic_mclag_seperate_ip_list'):
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_UNIQUE_IP/MCLAG_UNIQUE_IP_LIST={if_name}',
                if_name=args[0])
        return aa.delete(keypath)

    #######################################
    # Configure  MCLAG Unique IP Table - END
    #######################################

    #######################################
    # Configure  MCLAG Gateway Mac Table - START
    #######################################
    if (func == 'patch_sonic_mclag_gw_mac_list'):
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_GW_MAC/MCLAG_GW_MAC_LIST')
        body = {
            "sonic-mclag:MCLAG_GW_MAC_LIST": [
            {
                "gw_mac":args[0],
                "gw_mac_en":"enable"
            }
          ]
        }
        return aa.patch(keypath, body)

    if (func == 'delete_sonic_mclag_gw_mac_list'):
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_GW_MAC/MCLAG_GW_MAC_LIST={gw_mac}',
                gw_mac=args[0])
        return aa.delete(keypath)

    #######################################
    # Configure  MCLAG Gateway Mac Table - END
    #######################################

    #######################################
    # Get  APIs   - START
    #######################################
    if func == 'get_sonic_mclag_sonic_mclag':
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag')
        return aa.get(keypath, depth=None, ignore404=False)

    if func == 'get_sonic_mclag_sonic_mclag_mclag_domain':
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_DOMAIN')
        return aa.get(keypath)

    if func == 'get_sonic_mclag_sonic_mclag_mclag_interface_mclag_interface_list':
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_INTERFACE/MCLAG_INTERFACE_LIST={domain_id},{if_name}', domain_id=args[1], if_name=args[0])
        return aa.get(keypath, depth=None, ignore404=False)

    if func == 'get_sonic_mclag_sonic_mclag_mclag_local_intf_table_mclag_local_intf_table_list':
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_LOCAL_INTF_TABLE/MCLAG_LOCAL_INTF_TABLE_LIST={if_name}', if_name=args[0])
        return aa.get(keypath)

    if func == 'get_sonic_mclag_sonic_mclag_mclag_remote_intf_table_mclag_remote_intf_table_list':
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_REMOTE_INTF_TABLE/MCLAG_REMOTE_INTF_TABLE_LIST={domain_id},{if_name}', domain_id=args[1], if_name=args[0])
        return aa.get(keypath, depth=None, ignore404=False)

    if func == 'get_sonic_mclag_sonic_mclag_mclag_table':
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_TABLE')
        return aa.get(keypath)

    if func == 'get_sonic_mclag_separate_ip_list':
        keypath = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_UNIQUE_IP/MCLAG_UNIQUE_IP_LIST')
        #keypath = cc.Path('/restconf/data/openconfig-mclag:mclag/vlan-interfaces/vlan-interface')
        return aa.get(keypath)

    #######################################
    # Get  APIs   - END
    #######################################

    else:
        print("%Error: not implemented")
        exit(1)

def mclag_get_portchannel_traffic_disable(po_name):
    ''' call LAG Table Rest API to get LAG Admin Status '''
    traffic_disable = 'No'

    aa = cc.ApiClient()
    path = cc.Path('/restconf/data/sonic-portchannel:sonic-portchannel/LAG_TABLE/LAG_TABLE_LIST={lagname}/traffic_disable', lagname=po_name)
    api_response = aa.get(path)
    if api_response.ok():
        response = api_response.content
        if response is not None and len(response) != 0:
            if response['sonic-portchannel:traffic_disable']:
                traffic_disable = 'Yes'

    return traffic_disable


def mclag_get_local_if_port_isolate(po_name):
    ''' call MCLAG Local Interface state Table Rest API to get Port isolate property setting '''
    port_isolate = 'No'

    aa = cc.ApiClient()
    path = cc.Path('/restconf/data/sonic-mclag:sonic-mclag/MCLAG_LOCAL_INTF_TABLE/MCLAG_LOCAL_INTF_TABLE_LIST={if_name}/port_isolate_peer_link', if_name=po_name)
    api_response = aa.get(path)
    if api_response.ok():
        response = api_response.content
        if response is not None and len(response) != 0:
            if response['sonic-mclag:port_isolate_peer_link']:
                port_isolate = 'Yes'

    return port_isolate




def mclag_get_portchannel_oper_status(po_name):
    ''' call LAG Table Rest API to get LAG Admin Status '''
    po_oper_status = 'down'

    aa = cc.ApiClient()
    path = cc.Path('/restconf/data/sonic-portchannel:sonic-portchannel/LAG_TABLE/LAG_TABLE_LIST={lagname}/oper_status', lagname=po_name)
    api_response = aa.get(path)
    if api_response.ok():
        response = api_response.content
        if response is not None and len(response) != 0:
            po_oper_status = response['sonic-portchannel:oper_status']
    return po_oper_status



def mclag_get_ethernet_if_oper_status(if_name):
    ''' call Ethernet iface Rest API to get Ethernet if Admin Status '''
    if_oper_status = 'down'

    aa = cc.ApiClient()
    path = cc.Path('/restconf/data/sonic-port:sonic-port/PORT_TABLE/PORT_TABLE_LIST={ifname}/oper_status', ifname=if_name)
    api_response = aa.get(path)
    if api_response.ok():
        response = api_response.content
        if len(response) != 0:
            if_oper_status = response['sonic-port:oper_status']
    return if_oper_status



def mclag_get_remote_if_oper_status(if_name, remote_if_list):
    if_oper_status = "unknown"

    for list_item in remote_if_list:
        if list_item["if_name"] == if_name:
            for k,v in list_item.iteritems():
                if k == "oper_status":
                    if_oper_status = v
    return if_oper_status


#returns True or False and also returns value corresponding to the field
def mclag_is_element_in_list(list_to_search, field):
    for list_item in list_to_search:
        for  k,v  in list_item.iteritems():
            if (k == field):
                return True
    return False



def mclag_convert_list_to_dict(list_to_converted, field = None, value = None):
    converted_dict = {}
    for  list_item in list_to_converted:
        if ((field is None) or list_item[field] == value):
            for k, v in list_item.iteritems():
                converted_dict[k] = v
    return converted_dict;

def mclag_get_peer_link_status(peer_link_name):
    peer_link_status = ""
    if peer_link_name is not None:
        if peer_link_name.startswith("Ethernet"):
            peer_link_status = mclag_get_ethernet_if_oper_status(peer_link_name)
        elif peer_link_name.startswith("PortChannel"):
            peer_link_status = mclag_get_portchannel_oper_status(peer_link_name)
    return peer_link_status

def mclag_get_mclag_intf_dict(local_if_list, remote_if_list):
    mclag_intf_dict = {}
    count = 0

    for list_item in local_if_list:
       for k,v in list_item.iteritems():
           if k == "if_name":
               mclag_intf_dict[v] = {}
               if_local_status  = mclag_get_portchannel_oper_status(v)
               if_remote_status = mclag_get_remote_if_oper_status(v, remote_if_list)
               mclag_intf_dict[v]["local_if_status"] = if_local_status
               mclag_intf_dict[v]["remote_if_status"] = if_remote_status
               mclag_intf_dict[v]["if_name"] = v
               mclag_intf_dict[v]["traffic_disable"] = mclag_get_portchannel_traffic_disable(v)
               mclag_intf_dict[v]["port_isolate"]    = mclag_get_local_if_port_isolate(v)
               count += 1
    return count, mclag_intf_dict

#show mclag interface command
def mclag_show_mclag_interface(args):
    mclag_iface_info = {}

    api_response = invoke("get_sonic_mclag_sonic_mclag_mclag_interface_mclag_interface_list", args[1:])
    if api_response.ok():
        response = api_response.content
        if len(response) != 0:
            mclag_local_if  = []
            mclag_remote_if = []
            mclag_local_if = response['sonic-mclag:MCLAG_INTERFACE_LIST']
            if not mclag_is_element_in_list(mclag_local_if, "if_type"):
                print("MCLAG Interface not configured in this domain")
                return

            api_response = invoke("get_sonic_mclag_sonic_mclag_mclag_remote_intf_table_mclag_remote_intf_table_list", args[1:])
            if api_response.ok():
                response = api_response.content
                if response is not None and len(response) != 0:
                    mclag_remote_if = response['sonic-mclag:MCLAG_REMOTE_INTF_TABLE_LIST']
            
            count, mclag_iface_info = mclag_get_mclag_intf_dict(mclag_local_if, mclag_remote_if)
            show_cli_output(args[0], mclag_iface_info)
        else:
            print("No MCLAG Interface " + args[1] + " in MCLAG domain " + args[2] + " or domain not found")
   
    else:
        if api_response.status_code != 404:
            print api_response.error_message()
        else:
            print("No MCLAG Interface " + args[1] + " in MCLAG domain " + args[2] + " or domain not found")

    return

#show mclag brief
def mclag_show_mclag_brief(args):
    mclag_info = {}
    mclag_info['domain_info'] = {}
    mclag_info['domain_info'] = {}
    mclag_info['gateway_mac_info'] = {}
    mclag_info['delay_restore_info'] = {}
    mclag_info['mclag_iface_info'] = {}
    count_of_mclag_ifaces = 0

    api_response = invoke("get_sonic_mclag_sonic_mclag", args[1:])
    response = {}
    if api_response.ok():
        response = api_response.content
        if response is not None and len(response) != 0 and 'MCLAG_DOMAIN' in response['sonic-mclag:sonic-mclag']:
            #{"MCLAG_DOMAIN_LIST":[{"domain_id":"5","peer_ip":"192.168.1.2","peer_link":"PortChannel30","source_ip":"192.168.1.1"}]}
            domain_cfg_info = {}
            #set default values - somehow it is not picking up from rest API, need to check
            domain_cfg_info = mclag_convert_list_to_dict(response['sonic-mclag:sonic-mclag']['MCLAG_DOMAIN']['MCLAG_DOMAIN_LIST'])
            #set default values if the values are filled - somehow get rest api not returning default values
            if domain_cfg_info.get("keepalive_interval") is None:
                domain_cfg_info['keepalive_interval'] = 1;
            if domain_cfg_info.get("session_timeout") is None:
                domain_cfg_info['session_timeout']   = 30;
            if domain_cfg_info.get("delay_restore") is None:
                domain_cfg_info['delay_restore'] = MCLAG_DEFAULT_DELAY_RESTORE;
            peer_link_name = domain_cfg_info.get("peer_link")
            domain_cfg_info['peer_link_status'] = mclag_get_peer_link_status(peer_link_name)

            domain_state_info = {}
            #domain_state_info  = {"oper_status":"down", "role":"", "system_mac":""}
            if "MCLAG_TABLE" in response["sonic-mclag:sonic-mclag"]:
                domain_state_info = mclag_convert_list_to_dict(response['sonic-mclag:sonic-mclag']['MCLAG_TABLE']['MCLAG_TABLE_LIST'], "domain_id", domain_cfg_info['domain_id'])
            if domain_state_info.get("delay_restore_start_time") is None:
                domain_state_info['delay_restore_time_left'] = 0
            else:
                start_time = long(domain_state_info.get("delay_restore_start_time"))
                if start_time == 0:
                    domain_state_info['delay_restore_time_left'] = 0
                else:
                    elapse_time = long(float(time.time())) - start_time
                    if (elapse_time < domain_cfg_info['delay_restore']):
                        domain_state_info['delay_restore_time_left'] = domain_cfg_info['delay_restore'] - elapse_time
                    else:
                        domain_state_info['delay_restore_time_left'] = 0;
            mclag_info['domain_info'] = domain_cfg_info.copy()
            mclag_info['domain_info'].update(domain_state_info)

            mclag_info['gateway_mac_info'] = {}
            if "MCLAG_GW_MAC" in response["sonic-mclag:sonic-mclag"]:
                mclag_gw_mac_list = response['sonic-mclag:sonic-mclag']['MCLAG_GW_MAC']['MCLAG_GW_MAC_LIST']
                gateway_mac_info = {}
                #MCLAG_GW_MAC_LIST always has only one entry
                for list_item  in mclag_gw_mac_list:
                    gateway_mac=list_item["gw_mac"]
                    gateway_mac_info['gateway_mac']=gateway_mac
                mclag_info['gateway_mac_info'].update(gateway_mac_info)

            mclag_local_if_list  = []
            if "MCLAG_INTERFACE" in response["sonic-mclag:sonic-mclag"]:
                mclag_local_if_list = response['sonic-mclag:sonic-mclag']['MCLAG_INTERFACE']['MCLAG_INTERFACE_LIST']
            
            mclag_remote_if_list = []
            #mclag_remote_if_list = [{"domain_id":"5", "if_name":"PortChannel50", "oper_status":"down"}, {"domain_id":"5", "if_name":"PortChannel60", "oper_status":"up"}]
            if "MCLAG_REMOTE_INTF_TABLE" in response["sonic-mclag:sonic-mclag"]:
                mclag_remote_if_list = response['sonic-mclag:sonic-mclag']['MCLAG_REMOTE_INTF_TABLE']['MCLAG_REMOTE_INTF_TABLE_LIST']
            
            mclag_info['mclag_iface_info'] = {}
            count_of_mclag_ifaces, mclag_info['mclag_iface_info'] = mclag_get_mclag_intf_dict(mclag_local_if_list, mclag_remote_if_list)
            mclag_info['domain_info']['number_of_mclag_ifaces'] = count_of_mclag_ifaces
            show_cli_output(args[0], mclag_info)
        else:
            print("MCLAG Not Configured")

    else:
        #error response
        print api_response
        print api_response.error_message()

    return

#show mclag separate_ip_interfaces
def mclag_show_mclag_separate_ip(args):

    api_response = invoke("get_sonic_mclag_separate_ip_list", args)
    response = {}
    if api_response.ok():
        response = api_response.content
        if response is not None and len(response) != 0:
            show_cli_output(args[0], response)
        else:
            print("MCLAG separate IP interface not configured")

    else:
        #error response
        print api_response
        print api_response.error_message()

    return

def run(func, args):

    #show commands
    try:
        #show mclag brief command
        if func == 'show_mclag_brief':
            mclag_show_mclag_brief(args)
            return 0
        if func == 'show_mclag_interface':
            mclag_show_mclag_interface(args)
            return 0
        if func == 'show_mclag_separate_ip':
            mclag_show_mclag_separate_ip(args)
            return 0

    except Exception as e:
            print sys.exc_value
            return 1


    #config commands
    try:
        api_response = invoke(func, args)
        
        if api_response.ok():
            response = api_response.content
            if response is not None:
                print("Error: {}".format(str(response)))
        else:
            try:
                error_data = api_response.content['ietf-restconf:errors']['error'][0]
                err_app_tag = 'NOERROR'

                if 'error-app-tag' in error_data: 
                    err_app_tag = error_data['error-app-tag'] 

                if err_app_tag is not 'NOERROR': 
                    if err_app_tag == 'too-many-elements':
                       if (func == 'patch_list_sonic_mclag_sonic_mclag_mclag_domain_mclag_domain_list'):
                         print('Error: MCLAG already configured')
                         return 1

                if 'error-message' in error_data:
                    err_msg = error_data['error-message'] 
                    if err_msg == 'Entry not found':
                        print("Entry not found")
                        return 1
                    else:
                        print("Error: {}".format(str(api_response.error_message())))
                elif 'error-type' in error_data and error_data['error-type'] == 'application':
                    if 'error-tag' in error_data and error_data['error-tag'] == 'invalid-value':
                        if func == 'delete_sonic_mclag_sonic_mclag_mclag_domain_mclag_domain_list':
                            print("{}  Possibily Dependent MCLAG config not removed".format(str(api_response.error_message())))
                            return 1
                    else:
                            print("Error: Application/CVL Failure {}".format(str(api_response.error_message())))
                            return 1
                else:
                    print("Error: {}".format(str(api_response.error_message())))
                    return 1
            except Exception as e:
                print("%Error: {}".format(str(e)))
                return 1
    except Exception as e:
        print("%Error: {}".format(str(e)))
        return 1

    return 0

if __name__ == '__main__':
    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])

