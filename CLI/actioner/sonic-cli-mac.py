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
import syslog
import time
import json
import ast
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
import urllib3

urllib3.disable_warnings()

MAC_DAMPENING_DEFAULT_THRESHOLD = 5
MAC_DAMPENING_DEFAULT_INTERVAL  = 5

def mac_fill_count(mac_entries):
    static = dynamic = 0
    static = mac_entries['openconfig-network-instance-ext:static-count']
    dynamic = mac_entries['openconfig-network-instance-ext:dynamic-count']
    mac_entry_table = {'vlan-mac': (static + dynamic),
                       'static-mac': static,
                       'dynamic-mac': dynamic,
                       'total-mac': (static + dynamic)
    }
    return mac_entry_table

def fill_mac_info(mac_entry):
    if (('vlan' not in mac_entry) or ('mac-address' not in mac_entry) or ('state' not in mac_entry)):
        return
    if ('openconfig-vxlan:peer' in mac_entry):
        mac_entry_table = {'Vlan':mac_entry['vlan'],
                           'mac-address':mac_entry['mac-address'],
                           'entry-type': mac_entry['state']['entry-type'],
                           'port': "VxLAN DIP: " + mac_entry['openconfig-vxlan:peer']['state']['peer-ip']
                          }
    elif ('interface' in mac_entry):
        mac_entry_table = {'Vlan':mac_entry['vlan'],
                           'mac-address':mac_entry['mac-address'],
                           'entry-type': mac_entry['state']['entry-type'],
                           'port': mac_entry['interface']['interface-ref']['state']['interface']
                          }
    else:
        return 
    return mac_entry_table

def fill_mac_table_list_info(mac_table_list, mac_entry):
    mac_table_entry = fill_mac_info(mac_entry)
    if mac_table_entry is not None:
        mac_table_list.append(mac_table_entry)
 
def invoke(func, args):
    body = None
    aa = cc.ApiClient()

    if func == 'get_openconfig_network_instance_network_instances_network_instance_fdb_mac_table_entries':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/fdb/mac-table/entries', name='default')
        return aa.get(keypath)
    elif func == 'add_openconfig_network_instance_network_instances_network_instance_fdb_mac_table_entries':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/fdb/mac-table',name='default')
        body = {"openconfig-network-instance:mac-table":{"entries":{"entry":[{"mac-address":args[0],"vlan":int(args[1].lower().strip("vlan")),"config":{"mac-address":args[0],"vlan":int(args[1].lower().strip("vlan"))},"interface":{"interface-ref":{"config":{"interface":args[2],"subinterface":0}}},"openconfig-vxlan:peer":{}}]}}}
        return aa.patch(keypath, body)
    elif func == 'del_openconfig_network_instance_network_instances_network_instance_fdb_mac_table_entries':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/fdb/mac-table/entries/entry={macaddress},{vlan}', 
                name='default', macaddress=args[0], vlan=args[1].lower().strip("vlan"))
        return aa.delete(keypath)
    elif func == 'add_openconfig_network_instance_network_instances_network_instance_fdb_config_mac_aging_time':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/fdb/config/mac-aging-time',name='default')
        body = {"openconfig-network-instance:mac-aging-time":int(args[0])}
        return aa.patch(keypath, body)
    elif func == 'delete_openconfig_network_instance_network_instances_network_instance_fdb_config_mac_aging_time':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/fdb/config/mac-aging-time',name='default')
        return aa.delete(keypath)
    elif func == 'get_openconfig_network_instance_network_instances_network_instance_fdb_config_mac_aging_time':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/fdb/config/mac-aging-time', name='default')
        return aa.get(keypath)
    elif func == 'rpc_sonic_fdb_clear_fdb':
        keypath = cc.Path('/restconf/operations/sonic-fdb:clear_fdb')
        body = {"sonic-fdb:input": { args[0]: args[1]}}
        return aa.post(keypath, body)
    elif func == 'get_openconfig_network_instance_ext_network_instances_network_instance_fdb_state':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/fdb/state', name='default')
        return aa.get(keypath)
    elif func == 'patch_list_sonic_mac_dampening_sonic_mac_dampening_mac_dampening_mac_dampening_list':
        keypath = cc.Path('/restconf/data/sonic-mac-dampening:sonic-mac-dampening/MAC_DAMPENING/MAC_DAMPENING_LIST')
        if args[0] == "threshold":
            body = {
                    "sonic-mac-dampening:MAC_DAMPENING_LIST": [
                        {
                            "config": "config",
                            "threshold": int(args[1])
                            }
                        ]
                    }
        elif args[0] == "interval":
            body = {
                    "sonic-mac-dampening:MAC_DAMPENING_LIST": [
                        {
                            "config": "config",
                            "interval": int(args[1])
                        }
                      ]
                    }
        return aa.patch(keypath,body)
    elif func == 'get_list_sonic_mac_dampening_sonic_mac_dampening_mac_dampening_mac_dampening_list':
        keypath = cc.Path('/restconf/data/sonic-mac-dampening:sonic-mac-dampening/MAC_DAMPENING/MAC_DAMPENING_LIST')
        api_response = aa.get(keypath)
        if api_response.ok():
            response = api_response.content
            if response is not None and len(response) is not 0:
                print_content = response['sonic-mac-dampening:MAC_DAMPENING_LIST']
                threshold = MAC_DAMPENING_DEFAULT_THRESHOLD
                interval  = MAC_DAMPENING_DEFAULT_INTERVAL
                if "threshold" in print_content[0] and print_content[0]['threshold'] is not None:
                    threshold = print_content[0]['threshold']
                if "interval" in print_content[0] and print_content[0]['interval'] is not None:
                    interval = print_content[0]['interval']
                 
                print "MAC Move Dampening Threshold : {}".format(threshold)
                print "MAC Move Dampening Interval  : {}".format(interval)
    elif func == 'get_openconfig_mac_dampening_network_instances_network_instance_mac_dampening_state':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance=default/openconfig-mac-dampening:mac-dampening/state')
        api_response = aa.get(keypath)
        if api_response.ok():
            response = api_response.content
            if response is not None and len(response) is not 0:
                if 'interfaces' in response['openconfig-mac-dampening:state']:
                    print_content = response['openconfig-mac-dampening:state']['interfaces']
                    output = "\nPorts disabled due to MAC Dampening:\n\n"
                    for interface in print_content:
                        output = output + interface + "\n"
                    print output    
    elif func == 'delete_sonic_mac_dampening_sonic_mac_dampening_mac_dampening_mac_dampening_list_threshold':
        keypath = cc.Path('/restconf/data/sonic-mac-dampening:sonic-mac-dampening/MAC_DAMPENING/MAC_DAMPENING_LIST={config}/threshold', config=args[0])
        return aa.delete(keypath)
    elif func == 'delete_sonic_mac_dampening_sonic_mac_dampening_mac_dampening_mac_dampening_list_interval':
        keypath = cc.Path('/restconf/data/sonic-mac-dampening:sonic-mac-dampening/MAC_DAMPENING/MAC_DAMPENING_LIST={config}/interval', config=args[0])
        return aa.delete(keypath)
    elif func == 'delete_sonic_mac_dampening_sonic_mac_dampening_mac_dampening':
        keypath = cc.Path('/restconf/data/sonic-mac-dampening:sonic-mac-dampening/MAC_DAMPENING')
        return aa.delete(keypath)
    elif func == 'rpc_clear_mac_damp_disabled_ports':
        keypath = cc.Path('/restconf/operations/sonic-mac-dampening:clear-mac-dampening-disabled-ports')
        body = {"sonic-mac-dampening:input": dict()}
        if len(args) != 0:
            body["sonic-mac-dampening:input"]["ifname"] = args[0]
        else:
            body["sonic-mac-dampening:input"]["ifname"] = "ALL"
        return aa.post(keypath, body)
    else:
        return body

def run(func, args):
    try:
        api_response = invoke(func,args)
        if api_response is not None and api_response.errors():
            print api_response.error_message()
            return

        if api_response is not None and  api_response.ok():
            response = api_response.content
            if response is not None and len(response) is not 0:
                if 'openconfig-network-instance:entries' in response:
                    mac_entries = response['openconfig-network-instance:entries']['entry']
                elif 'openconfig-network-instance:state' in response:
                    mac_entries = response['openconfig-network-instance:state']
                elif 'openconfig-network-instance:mac-aging-time' in response:
                    show_cli_output(args[0], response)
                    return
                else:
                    return
            else:
                return
        if func == 'get_list_sonic_mac_dampening_sonic_mac_dampening_mac_dampening_mac_dampening_list' or func == 'get_openconfig_mac_dampening_network_instances_network_instance_mac_dampening_state':
            return
        
        mac_table_list = [] 
        if func == 'get_openconfig_network_instance_network_instances_network_instance_fdb_mac_table_entries':
            if args[1] == 'show': #### -- show mac address table --- ###
                for mac_entry in mac_entries:
                    fill_mac_table_list_info(mac_table_list, mac_entry)

            elif args[1] == 'mac-addr': #### -- show mac address table [address <mac-address>]--- ###
                for mac_entry in mac_entries:
                    if args[2] == mac_entry['mac-address'].lower():
                        fill_mac_table_list_info(mac_table_list, mac_entry)

            elif args[1] == 'vlan': #### -- show mac address table [vlan <vlan-id>]--- ###
                for mac_entry in mac_entries:
                    if (int(args[2].lower().strip("vlan")) == mac_entry['vlan']):
                        fill_mac_table_list_info(mac_table_list, mac_entry)
 
            elif args[1] == 'interface': #### -- show mac address table [interface {Ethernet <id> | Portchannel <id>}]--- ###
                for mac_entry in mac_entries:
                    if 'interface' in mac_entry:
                        if args[2] == mac_entry['interface']['interface-ref']['state']['interface']:
                            fill_mac_table_list_info(mac_table_list, mac_entry)

            #### -- show mac address table [static {address <mac-address> | vlan <vlan-id> | interface {Ethernet <id>| Portchannel <id>}}]--- ###
            elif args[1] == 'static':
                if args[2] == 'address':
                    for mac_entry in mac_entries:
                        if args[3] == mac_entry['mac-address'].lower() and mac_entry['state']['entry-type'] == 'STATIC':
                            fill_mac_table_list_info(mac_table_list, mac_entry)

                elif args[2] == 'vlan':
                    for mac_entry in mac_entries:
                        if (int(args[3].lower().strip("vlan")) == mac_entry['vlan']) and mac_entry['state']['entry-type'] == 'STATIC':
                            fill_mac_table_list_info(mac_table_list, mac_entry)
                
                elif args[2] == 'interface':
                    for mac_entry in mac_entries:
                        if 'interface' in mac_entry:
                            if args[3] == mac_entry['interface']['interface-ref']['state']['interface'] and mac_entry['state']['entry-type'] == 'STATIC':
                                fill_mac_table_list_info(mac_table_list, mac_entry)

                else:
                    for mac_entry in mac_entries:
                        if mac_entry['state']['entry-type'] == 'STATIC':
                            fill_mac_table_list_info(mac_table_list, mac_entry)

            #### -- show mac address table [dynamic {address <mac-address> | vlan <vlan-id> | interface {Ethernet <id>| Portchannel <id>}}]--- ###
            elif args[1] == 'dynamic':
                if args[2] == 'address':
                    for mac_entry in mac_entries:
                        if args[3] == mac_entry['mac-address'].lower() and mac_entry['state']['entry-type'] == 'DYNAMIC':
                            fill_mac_table_list_info(mac_table_list, mac_entry)

                elif args[2] == 'vlan':
                    for mac_entry in mac_entries:
                        if (int(args[3].lower().strip("vlan")) == mac_entry['vlan']) and mac_entry['state']['entry-type'] == 'DYNAMIC':
                            fill_mac_table_list_info(mac_table_list, mac_entry)

                elif args[2] == 'interface':
                    for mac_entry in mac_entries:
                        if 'interface' in mac_entry:
                            if args[3] == mac_entry['interface']['interface-ref']['state']['interface'] and mac_entry['state']['entry-type'] == 'DYNAMIC':
                                fill_mac_table_list_info(mac_table_list, mac_entry)

                else:
                    for mac_entry in mac_entries:
                        if mac_entry['state']['entry-type'] == 'DYNAMIC':
                            fill_mac_table_list_info(mac_table_list, mac_entry)
        elif func == 'get_openconfig_network_instance_ext_network_instances_network_instance_fdb_state':
            if args[1] == 'count': #### -- show mac address table count --- ###
                mac_table_list.append(mac_fill_count(mac_entries))
        show_cli_output(args[0], mac_table_list)
        return
    except Exception as e:
        print "% Error: Internal error"
        syslog.syslog(syslog.LOG_ERR, str(e))

if __name__ == '__main__':

    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])
