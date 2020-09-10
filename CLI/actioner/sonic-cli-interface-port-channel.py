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
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
from ipaddress import ip_interface

import urllib3
urllib3.disable_warnings()


def invoke_api(func, args=[]):
    api = cc.ApiClient()

    if func == 'get_sonic_portchannel_sonic_portchannel_lag_table':
        path = cc.Path('/restconf/data/sonic-portchannel:sonic-portchannel/LAG_TABLE')
        return api.get(path)

    if func == 'get_sonic_portchannel_sonic_portchannel_lag_table_lag_table_list':
        path = cc.Path('/restconf/data/sonic-portchannel:sonic-portchannel/LAG_TABLE/LAG_TABLE_LIST={lagname}', lagname=args[0])
        return api.get(path)

    if func == 'get_sonic_portchannel_sonic_portchannel_lag_member_table':
        path = cc.Path('/restconf/data/sonic-portchannel:sonic-portchannel/LAG_MEMBER_TABLE')
        return api.get(path)
        
    if func == 'get_sonic_portchannel_sonic_portchannel_portchannel':
        path = cc.Path('/restconf/data/sonic-portchannel:sonic-portchannel/PORTCHANNEL')
        return api.get(path)

    if func == 'get_sonic_portchannel_sonic_portchannel_portchannel_portchannel_list':
        path = cc.Path('/restconf/data/sonic-portchannel:sonic-portchannel/PORTCHANNEL/PORTCHANNEL_LIST={lagname}', lagname=args[0])
        return api.get(path)

    if func == 'get_openconfig_lacp_lacp_interfaces':
        path = cc.Path('/restconf/data/openconfig-lacp:lacp/interfaces')
        return api.get(path)
        
    if func == 'get_openconfig_lacp_lacp_interfaces_interface':
        path = cc.Path('/restconf/data/openconfig-lacp:lacp/interfaces/interface={name}', name=args[0])
        return api.get(path)        
            
    if func == 'get_openconfig_interfaces_interfaces_interface_state_counters':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/state/counters', name=args[0])
        return api.get(path)

    if func == 'get_sonic_portchannel_sonic_portchannel_portchannel_global_portchannel_global_list':
        path = cc.Path('/restconf/data/sonic-portchannel:sonic-portchannel/PORTCHANNEL_GLOBAL')
        return api.get(path)
    if func == 'get_sonic_portchannel_sonic_portchannel_ip_addr_list':
        path = cc.Path('/restconf/data/sonic-portchannel-interface:sonic-portchannel-interface/PORTCHANNEL_INTERFACE/PORTCHANNEL_INTERFACE_IPADDR_LIST')
        return api.get(path)
 
    return api.cli_not_implemented(func)
    
def filter_address(api_response,lagName):
    output ={}
    ipv4_addr =[]
    ipv6_addr =[]
    ipList = api_response['sonic-portchannel-interface:PORTCHANNEL_INTERFACE_IPADDR_LIST']
    for ip in ipList:
        if ip_interface(ip['ip_prefix']).ip.version == 6:
            ipv6_addr.append(ip)
        else:
            ipv4_addr.append(ip)
    output['ipv4'] = ipv4_addr
    output['ipv6'] = ipv6_addr
    return output

def get_lag_data(lagName):

    api_response = {}
    output = {}
    args = [lagName]

    try:
        if lagName == "all": #get_all_portchannels
            portchannel_func = 'get_sonic_portchannel_sonic_portchannel_lag_table'
            portchannel_conf_func = 'get_sonic_portchannel_sonic_portchannel_portchannel'
	    portchannel_ip = 'get_sonic_portchannel_sonic_portchannel_ip_addr_list'
        else :
            portchannel_func = 'get_sonic_portchannel_sonic_portchannel_lag_table_lag_table_list'
            portchannel_conf_func = 'get_sonic_portchannel_sonic_portchannel_portchannel_portchannel_list'
    	    portchannel_ip = 'get_sonic_portchannel_sonic_portchannel_ip_addr_list'
        output = {}
        response = invoke_api(portchannel_func, args)
        if response.ok():
            if response.content is not None:
                # Get Command Output
                api_response = response.content
                if 'sonic-portchannel:LAG_TABLE' not in api_response.keys():
                    output['sonic-portchannel:LAG_TABLE'] = {}
                    if 'sonic-portchannel:LAG_TABLE_LIST' in api_response.keys():
                        output['sonic-portchannel:LAG_TABLE']['LAG_TABLE_LIST'] = api_response['sonic-portchannel:LAG_TABLE_LIST']
                else:
                    output = api_response        

        responseIp = invoke_api(portchannel_ip,args)
        if responseIp.ok():
            if responseIp.content is not None:
                api_response = responseIp.content
                if 'sonic-portchannel-interface:PORTCHANNEL_INTERFACE_IPADDR_LIST' in api_response.keys():
                    output_filter = filter_address(api_response,lagName)
                    output['sonic-portchannel-interface:PORTCHANNEL_INTERFACE_IPADDR_LIST:ipv4'] = output_filter['ipv4']
                    output['sonic-portchannel-interface:PORTCHANNEL_INTERFACE_IPADDR_LIST:ipv6'] = output_filter['ipv6']
					
        # GET Config params
        resp = invoke_api(portchannel_conf_func, args)
        if resp.ok():
            if resp.content is not None:
                # Get Command Output
                api_resp = resp.content

                if 'sonic-portchannel:PORTCHANNEL' not in api_resp.keys():
                    output['sonic-portchannel:PORTCHANNEL'] = {}
                    if 'sonic-portchannel:PORTCHANNEL_LIST' in api_resp.keys():
                        output['sonic-portchannel:PORTCHANNEL']['PORTCHANNEL_LIST'] = api_resp['sonic-portchannel:PORTCHANNEL_LIST']
                else:
                    output.update( api_resp )

        # GET LAG Members
        resp2 = invoke_api('get_sonic_portchannel_sonic_portchannel_lag_member_table', args)
        if resp2.ok():
            if resp2.content is not None:
                # Get Command Output
                api_resp2 = resp2.content
                output.update( api_resp2 )

    except Exception as e:
        print("Exception when calling get_lag_data : %s\n" %(e))

    return output


def get_lacp_data(lagName):

    api_response1 = {}
    resp = {}
    args = [lagName]

    try:
        if lagName == "all":
            lacp_func = 'get_openconfig_lacp_lacp_interfaces'
        else :
            lacp_func = 'get_openconfig_lacp_lacp_interfaces_interface'

        response = invoke_api(lacp_func, args)
        if response.ok():
            if response.content is not None:
                # Get Command Output
                api_response1 = response.content
                #api_response1 = aa1.api_client.sanitize_for_serialization(api_response1)
                if 'openconfig-lacp:interfaces' not in api_response1.keys():
                    resp['openconfig-lacp:interfaces'] = {}
                    if 'openconfig-lacp:interface' in api_response1.keys():
                        resp['openconfig-lacp:interfaces']['interface'] = api_response1['openconfig-lacp:interface']
                else:
                     resp = api_response1
                
    except Exception as e:
        print("Exception when calling get_lacp_data : %s\n" %(e))
    
    return resp

    
def get_counters(api_response):

    try:
        response = {}
        if 'sonic-portchannel:LAG_TABLE' not in api_response.keys():
            response['sonic-portchannel:LAG_TABLE'] = {}
            if 'sonic-portchannel:LAG_TABLE_LIST' in api_response.keys():
                response['sonic-portchannel:LAG_TABLE']['LAG_TABLE_LIST'] = api_response['sonic-portchannel:LAG_TABLE_LIST']
        else:
            response = api_response
        
        if 'LAG_TABLE_LIST' in response['sonic-portchannel:LAG_TABLE']:
          for po_intf in response['sonic-portchannel:LAG_TABLE']['LAG_TABLE_LIST']:        
            resp = invoke_api('get_openconfig_interfaces_interfaces_interface_state_counters', [po_intf['lagname']])
            if resp.ok():
                if resp.content is not None:
                    # Get Command Output
                    resp = resp.content
                    po_intf["counters"] = resp

    except Exception as e:
        print("Exception when calling get_counters : %s\n" %(e))

def get_global_config_data():

    try:
        lacp_func = 'get_sonic_portchannel_sonic_portchannel_portchannel_global_portchannel_global_list'

        args = []
        value = {}
        api_response = invoke_api(lacp_func, args)
        if api_response.ok():
            response = api_response.content
            if response == '':
                value = "Disabled"
            elif response is not None:
                if 'sonic-portchannel:PORTCHANNEL_GLOBAL' in response:
                    value = response['sonic-portchannel:PORTCHANNEL_GLOBAL']['PORTCHANNEL_GLOBAL_LIST']

    except Exception as e:
        print("Exception when calling get_global_config_data : %s\n" %(e))

    return value

def run():

    if sys.argv[1] == "get_all_portchannels":
        iflist = ["all"]
        template_file = sys.argv[2]
    else:
        iflist = sys.argv[2].rstrip().split(',') 
        template_file = sys.argv[3]

    global_config_response = get_global_config_data()

    for intf in iflist:
        api_response = get_lag_data(intf)
        api_response1 = get_lacp_data(intf)
        get_counters(api_response)

        # Combine Outputs
        response = {"portchannel": api_response, "lacp": api_response1, "global": global_config_response}

        # Check for PortChannel existence
        if 'LAG_TABLE_LIST' not in response['portchannel']['sonic-portchannel:LAG_TABLE'] or \
            'admin_status' not in response['portchannel']['sonic-portchannel:LAG_TABLE']['LAG_TABLE_LIST'][0].keys():
            response = {}

        show_cli_output(template_file, response)


if __name__ == '__main__':

    pipestr().write(sys.argv)
    run()

