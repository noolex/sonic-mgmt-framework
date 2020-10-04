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
import time
import json
import ast
from rpipe_utils import pipestr
import cli_client as cc
from scripts.render_cli import show_cli_output
import traceback

import urllib3
urllib3.disable_warnings()

nat_type_map = {"snat" : "SNAT", "dnat": "DNAT"}
nat_protocol_map = {"icmp": "1", "tcp": "6", "udp": "17"}
clear_nat_map = {"translations": "ENTRIES", "statistics": "STATISTICS"}
config = True

def invoke_api(func, args=[]):
    global config

    api = cc.ApiClient()

    # Enable/Disable NAT Feature
    if func == 'patch_openconfig_nat_nat_instances_instance_config_enable':
        path = cc.Path('/restconf/data/openconfig-nat:nat/instances/instance={id}/config/enable', id=args[0])
        if args[1] == "True":
           body = { "openconfig-nat:enable": True }
        else:
           body = { "openconfig-nat:enable": False }
        return api.patch(path,body)

    # Config NAT/NAPT Static translation entry
    elif func == 'patch_nat_napt_mapping_table':
        nat_id = args[0]
        global_ip = args[1].split("=")[1]
        port_type = args[2].split("=")[1]
        global_port = args[3].split("=")[1]
        local_ip = args[4].split("=")[1]
        local_port = args[5].split("=")[1]
        nat_type = args[6].split("=")[1]
        twice_nat_id = args[7].split("=")[1]

        if port_type == "":
            path = cc.Path('/restconf/data/openconfig-nat:nat/instances/instance={natid}/nat-mapping-table', natid=nat_id)
            body = { "openconfig-nat:nat-mapping-table": { "nat-mapping-entry": [ { "external-address": global_ip, "config": { "external-address": global_ip, "internal-address": local_ip } } ] }}

            if local_port != "" :
                body["openconfig-nat:nat-mapping-table"]["nat-mapping-entry"][0]["config"].update( {"internal-port": int(local_port) } )
            if nat_type != "" :
                body["openconfig-nat:nat-mapping-table"]["nat-mapping-entry"][0]["config"].update( {"type": nat_type_map[nat_type] } )
            if twice_nat_id != "" :
                body["openconfig-nat:nat-mapping-table"]["nat-mapping-entry"][0]["config"].update( {"twice-nat-id": int(twice_nat_id) } )
        else:
            path = cc.Path('/restconf/data/openconfig-nat:nat/instances/instance={natid}/napt-mapping-table', natid=nat_id)
            body = { "openconfig-nat:napt-mapping-table": { "napt-mapping-entry": [ { "external-address": global_ip, "protocol": int(nat_protocol_map[port_type]), "external-port": int(global_port), "config": { "external-address": global_ip, "protocol": int(nat_protocol_map[port_type]), "external-port": int(global_port), "internal-address": local_ip } } ] }}

            if local_port != "" :
                body["openconfig-nat:napt-mapping-table"]["napt-mapping-entry"][0]["config"].update( {"internal-port": int(local_port) } )
            if nat_type != "" :
                body["openconfig-nat:napt-mapping-table"]["napt-mapping-entry"][0]["config"].update( {"type": nat_type_map[nat_type] } )
            if twice_nat_id != "" :
                body["openconfig-nat:napt-mapping-table"]["napt-mapping-entry"][0]["config"].update( {"twice-nat-id": int(twice_nat_id) } )

        return api.patch(path, body)


    # Remove NAT/NAPT Static translation entry
    elif func == 'delete_nat_napt_mapping_table':
        nat_id = args[0]
        global_ip = args[1].split("=")[1]
        port_type = args[2].split("=")[1]
        global_port = args[3].split("=")[1]

        if global_ip == "":
            # Remove all static entries
            path = cc.Path('/restconf/data/openconfig-nat:nat/instances/instance={natid}/nat-mapping-table', natid=nat_id)
            api.delete(path)
            path = cc.Path('/restconf/data/openconfig-nat:nat/instances/instance={natid}/napt-mapping-table', natid=nat_id)
            return api.delete(path)

        if port_type == "":
            # Remove specific NAT entry
            path = cc.Path('/restconf/data/openconfig-nat:nat/instances/instance={natid}/nat-mapping-table/nat-mapping-entry={externaladdress}', natid=nat_id, externaladdress=global_ip)
        else:
            # Remove specific NAPT entry
            path = cc.Path('/restconf/data/openconfig-nat:nat/instances/instance={natid}/napt-mapping-table/napt-mapping-entry={externaladdress},{protocol},{externalport}', natid=nat_id,externaladdress=global_ip,protocol=nat_protocol_map[port_type],externalport=global_port) 

        return api.delete(path)


    # Config NAT Pool
    elif func == 'patch_openconfig_nat_nat_instances_instance_nat_pool_nat_pool_entry_config':
        if not ((args[2].find(":")) == -1):
            return api._make_error_response('%Error: NAT supports IPV4 addresses only')
        path = cc.Path('/restconf/data/openconfig-nat:nat/instances/instance={id}/nat-pool', id=args[0])
        body = { "openconfig-nat:nat-pool": { "nat-pool-entry": [ { "pool-name": args[1], "config": { "pool-name": args[1], "nat-ip": args[2] } } ] }}
        if len(args) > 3:
            body["openconfig-nat:nat-pool"]["nat-pool-entry"][0]["config"].update( {"nat-port": args[3] } )

        return api.patch(path, body)

    # Config NAT Binding
    elif func == 'patch_openconfig_nat_nat_instances_instance_nat_acl_pool_binding_nat_acl_pool_binding_entry_config':
        path = cc.Path('/restconf/data/openconfig-nat:nat/instances/instance={id}/nat-acl-pool-binding', id=args[0])

        body = { "openconfig-nat:nat-acl-pool-binding": { "nat-acl-pool-binding-entry": [ { "name": args[1], "config": { "name": args[1], "nat-pool": args[2] } } ] }}

        # ACL Name
        acl_name = args[3].split("=")[1]
        if acl_name != "" :
            body["openconfig-nat:nat-acl-pool-binding"]["nat-acl-pool-binding-entry"][0]["config"].update( {"access-list": acl_name } )

        # NAT Type
        nat_type = args[4].split("=")[1]
        if nat_type != "":
            body["openconfig-nat:nat-acl-pool-binding"]["nat-acl-pool-binding-entry"][0]["config"].update( {"type": nat_type_map[nat_type] } )

        # Twice NAT ID
        twice_nat_id = args[5].split("=")[1]
        if twice_nat_id != "":
            body["openconfig-nat:nat-acl-pool-binding"]["nat-acl-pool-binding-entry"][0]["config"].update( {"twice-nat-id": int(twice_nat_id) } )

        return api.patch(path, body)

    # Config NAT Zone
    elif func == 'patch_openconfig_interfaces_ext_interfaces_interface_nat_zone_config_nat_zone':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-interfaces-ext:nat-zone/config/nat-zone', name=args[1])
        body = { "openconfig-interfaces-ext:nat-zone": int(args[2]) }
        return api.patch(path, body)

    # Remove NAT Zone
    elif func == 'delete_openconfig_interfaces_ext_interfaces_interface_nat_zone_config_nat_zone':
        path = cc.Path('/restconf/data/openconfig-interfaces:interfaces/interface={name}/openconfig-interfaces-ext:nat-zone/config/nat-zone', name=args[1])
        return api.delete(path)

    # Clear NAT Translations/Statistics
    elif func == 'rpc_nat_clear':
        path = cc.Path('/restconf/operations/sonic-nat:clear_nat')
        body = {"sonic-nat:input":{"nat-param": clear_nat_map[args[1]]}}
        return api.post(path,body)


    # Get NAT Global Config
    elif func == 'get_openconfig_nat_nat_instances_instance_config':
        config = False
        path = cc.Path('/restconf/data/openconfig-nat:nat/instances/instance={id}/config', id=args[0])
        return api.get(path)

    # Get NAT Bindings
    elif func == 'get_openconfig_nat_nat_instances_instance_nat_acl_pool_binding':
        config = False
        path = cc.Path('/restconf/data/openconfig-nat:nat/instances/instance={id}/nat-acl-pool-binding', id=args[0])
        return api.get(path)

    # Get NAT Pools
    elif func == 'get_openconfig_nat_nat_instances_instance_nat_pool':
        config = False
        path = cc.Path('/restconf/data/openconfig-nat:nat/instances/instance={id}/nat-pool', id=args[0])
        return api.get(path)

    ## Get NAT Translations
    elif func == 'get_openconfig_nat_nat_instances_instance_nat_mapping_table':
        config = False
        path = cc.Path('/restconf/data/openconfig-nat:nat/instances/instance={id}/nat-mapping-table', id=args[0])
        return api.get(path)

    elif func == 'get_openconfig_nat_nat_instances_instance_napt_mapping_table':
        config = False
        path = cc.Path('/restconf/data/openconfig-nat:nat/instances/instance={id}/napt-mapping-table', id=args[0])
        return api.get(path)

    elif func == 'get_openconfig_nat_nat_instances_instance_nat_twice_mapping_table':
        config = False
        path = cc.Path('/restconf/data/openconfig-nat:nat/instances/instance={id}/nat-twice-mapping-table', id=args[0])
        return api.get(path)

    elif func == 'get_openconfig_nat_nat_instances_instance_napt_twice_mapping_table':
        config = False
        path = cc.Path('/restconf/data/openconfig-nat:nat/instances/instance={id}/napt-twice-mapping-table', id=args[0])
        return api.get(path)

    # Get all L3 interfaces (needed for NAT Zone)
    elif func == 'get_sonic_interface_sonic_interface_interface':
        config = False
        path = cc.Path('/restconf/data/sonic-interface:sonic-interface/INTERFACE')
        return api.get(path)

    elif func == 'get_sonic_vlan_interface_sonic_vlan_interface_vlan_interface':
        config = False
        path = cc.Path('/restconf/data/sonic-vlan-interface:sonic-vlan-interface/VLAN_INTERFACE')
        return api.get(path)

    elif func == 'get_sonic_portchannel_interface_sonic_portchannel_interface_portchannel_interface':
        config = False
        path = cc.Path('/restconf/data/sonic-portchannel-interface:sonic-portchannel-interface/PORTCHANNEL_INTERFACE')
        return api.get(path)

    elif func == 'get_sonic_loopback_interface_sonic_loopback_interface_loopback_interface':
        config = False
        path = cc.Path('/restconf/data/sonic-loopback-interface:sonic-loopback-interface/LOOPBACK_INTERFACE')
        return api.get(path)

    else:
        return api.cli_not_implemented(func)


def get_response_dict(response):
    api_response = {}

    if response.ok():
        if response.content is not None:
            # Get Command Output
            api_response = response.content
    else:
        print response.error_message()

    return api_response

def get_nat_napt_tables(args):
    response = {}

    resp = invoke_api('get_openconfig_nat_nat_instances_instance_nat_mapping_table', args)
    resp = get_response_dict(resp)
    response.update(resp)

    resp = invoke_api('get_openconfig_nat_nat_instances_instance_napt_mapping_table', args)
    resp = get_response_dict(resp)
    response.update(resp)

    return response

def get_twice_nat_napt_tables(args):
    response = {}

    resp = invoke_api('get_openconfig_nat_nat_instances_instance_nat_twice_mapping_table', args)
    resp = get_response_dict(resp)
    response.update(resp)

    resp = invoke_api('get_openconfig_nat_nat_instances_instance_napt_twice_mapping_table', args)
    resp = get_response_dict(resp)
    response.update(resp)


    return response
    

def get_nat_translations(func, args):
    response = {}
    resp = get_nat_napt_tables(args)
    response.update(resp)

    resp = get_twice_nat_napt_tables(args)
    response.update(resp)

    return response

 
def get_nat_zones(func,args):
    output  = {}

    # Get INTERFACE Table
    response = invoke_api("get_sonic_interface_sonic_interface_interface")
    api_response = get_response_dict(response)

    if 'sonic-interface:INTERFACE' in api_response and \
          'INTERFACE_LIST' in api_response['sonic-interface:INTERFACE']:
        for val in api_response['sonic-interface:INTERFACE']['INTERFACE_LIST']:
            if 'nat_zone' in val and 'portname' in val:
                output.update( {val['portname']: val['nat_zone']} )


    # Get VLAN_INTERFACE table
    response1 = invoke_api("get_sonic_vlan_interface_sonic_vlan_interface_vlan_interface")
    api_response1 = get_response_dict(response1)

    if 'sonic-vlan-interface:VLAN_INTERFACE' in api_response1 and \
          'VLAN_INTERFACE_LIST' in api_response1['sonic-vlan-interface:VLAN_INTERFACE']:
        for val in api_response1['sonic-vlan-interface:VLAN_INTERFACE']['VLAN_INTERFACE_LIST']:
            if 'nat_zone' in val and 'vlanName' in val:
                output.update( {val['vlanName']: val['nat_zone']} )

    # Get PORTCHANNEL_INTERFACE table
    response2 = invoke_api("get_sonic_portchannel_interface_sonic_portchannel_interface_portchannel_interface")
    api_response2 = get_response_dict(response2)

    if 'sonic-portchannel-interface:PORTCHANNEL_INTERFACE' in api_response2 and \
          'PORTCHANNEL_INTERFACE_LIST' in api_response2['sonic-portchannel-interface:PORTCHANNEL_INTERFACE']:
        for val in api_response2['sonic-portchannel-interface:PORTCHANNEL_INTERFACE']['PORTCHANNEL_INTERFACE_LIST']:
            if 'nat_zone' in val and 'pch_name' in val:
                output.update( {val['pch_name']: val['nat_zone']} )

    # Get LOOPBACK_INTERFACE table
    response3 = invoke_api("get_sonic_loopback_interface_sonic_loopback_interface_loopback_interface")
    api_response3 = get_response_dict(response3)

    if 'sonic-loopback-interface:LOOPBACK_INTERFACE' in api_response3 and \
          'LOOPBACK_INTERFACE_LIST' in api_response3['sonic-loopback-interface:LOOPBACK_INTERFACE']:
        for val in api_response3['sonic-loopback-interface:LOOPBACK_INTERFACE']['LOOPBACK_INTERFACE_LIST']:
            if 'nat_zone' in val and 'loIfName' in val:
                output.update( {val['loIfName']: val['nat_zone']} )

    return output



def get_count(count, table_name, l):

    table_count_map = {
                        'openconfig-nat:nat-mapping-table': ['static_nat', 'dynamic_nat'],
                        'openconfig-nat:napt-mapping-table': ['static_napt', 'dynamic_napt'],
                        'openconfig-nat:nat-twice-mapping-table': ['static_twice_nat', 'dynamic_twice_nat'],
                        'openconfig-nat:napt-twice-mapping-table': ['static_twice_napt', 'dynamic_twice_napt'],
                      }
    if 'state' in l:
        count['total_entries'] += 1

    if 'state' in l and 'entry-type' in l['state']:
        if l['state']['entry-type'] == 'openconfig-nat:STATIC':
            count[table_count_map[table_name][0]]+=1;
        else:
            count[table_count_map[table_name][1]]+=1;

    if 'state' in l and 'type' in l['state']:
        if l['state']['type'] == 'openconfig-nat:SNAT':
            count['snat_snapt']+=1;
        else:
            count['dnat_dnapt']+=1
    return
    

def get_nat_translations_count(func, args):
    response = get_nat_translations(func, args)
    count = { 'static_nat': 0, 
              'static_napt': 0,
              'dynamic_nat': 0,
              'dynamic_napt': 0,
              'static_twice_nat': 0,
              'static_twice_napt': 0,
              'dynamic_twice_nat': 0,
              'dynamic_twice_napt': 0,
              'snat_snapt': 0,
              'dnat_dnapt': 0,
              'total_entries': 0
	     }

    for key in response:
        for entry in response[key]:
            for l in response[key][entry]:
                get_count(count, key, l)

    return count

def get_stats(key, l):

    stats = { "protocol": "all",
              "source": "---",
              "destination": "---",
              "pkts": "0",
              "bytes": "0"}

    if key == "openconfig-nat:napt-mapping-table" or key == "openconfig-nat:napt-twice-mapping-table" : 
        for k,v in nat_protocol_map.items():
            if v ==  str(l["protocol"]):
                stats["protocol"] = k

    if key == "openconfig-nat:nat-mapping-table":
        if 'type' in l['state'] and l['state']['type'] == 'openconfig-nat:SNAT' :
            stats["source"] = l['external-address']
        elif 'type' in l['state'] and l['state']['type'] == 'openconfig-nat:DNAT' :
            stats["destination"] = l['external-address']
    elif key == "openconfig-nat:napt-mapping-table":
        addr = l['external-address']+":"+str(l['external-port'])
        if 'type' in l['state'] and l['state']['type'] == 'openconfig-nat:SNAT' :
            stats["source"] = addr
        elif 'type' in l['state'] and l['state']['type'] == 'openconfig-nat:DNAT' :
            stats["destination"] = addr
    elif key == "openconfig-nat:nat-twice-mapping-table":
        stats["source"] = l["src-ip"]
        stats["destination"] = l["dst-ip"]
    else:
        stats["source"] = l["src-ip"]+":"+str(l["src-port"])
        stats["destination"] = l["dst-ip"]+":"+str(l["dst-port"])

    if 'state' in l and 'counters' in l['state']:
        if 'nat-translations-bytes' in l['state']['counters']:
            stats["bytes"] = l['state']['counters']['nat-translations-bytes']
        if 'nat-translations-pkts' in l['state']['counters']:
            stats["pkts"] = l['state']['counters']['nat-translations-pkts']

    return stats 


def get_nat_statistics(func, args):
    resp = []
    response = get_nat_translations(func, args)

    for key in response:
        for entry in response[key]:
            for l in response[key][entry]:
                if 'state' in l and 'counters' in l['state']:
                    stats = get_stats(key, l) 
                    if stats is not None:
                        resp.append(stats)
                    
 
    return resp

def get_configs(table_name, l):
    configs = {
                'nat_type': "dnat",
                'ip_protocol': "all",
                'global_ip': "",
                'global_l4_port': "----",
                'local_ip': "",
                'local_l4_port': "----",
                'twice_nat_id': "----"
              }
    if 'config' not in  l:
        return None

    # IP Protocol
    if 'openconfig-nat:napt-mapping-table' == table_name:
        if 'config' in l and 'protocol' in l['config']:
            proto = l['config']['protocol']
        for key,val in nat_protocol_map.items():
            if val ==  str(proto):
                configs['ip_protocol'] = key

    # Nat Type
    if 'config' in l and 'type' in l['config']:
        if l['config']['type'] == "openconfig-nat:SNAT":
            configs['nat_type'] = "snat"

    # Global IP
    if 'config' in l and 'external-address' in l['config']:
        configs['global_ip'] = l['config']['external-address']

    # Global L4 Port
    if 'config' in l and 'external-port' in l['config']:
        configs['global_l4_port'] = l['config']['external-port']

    # Local IP
    if 'config' in l and 'internal-address' in l['config']:
        configs['local_ip'] = l['config']['internal-address']

    # Local L4 Port
    if 'config' in l and 'internal-port' in l['config']:
        configs['local_l4_port'] = l['config']['internal-port']

    # Twice NAT ID
    if 'config' in l and 'twice-nat-id' in l['config']:
        configs['twice_nat_id'] = l['config']['twice-nat-id']
    
    return configs        


def get_nat_static_configs(func,args):
    response = get_nat_napt_tables(args)
    resp = []

    for key in response:
        for entry in response[key]:
            for l in response[key][entry]:
                configs = get_configs(key, l)
                if configs is not None:
                    resp.append(configs)

    return resp

def get_nat_configs(func, args):
    api_response = {}

    # Get Global data
    response = invoke_api('get_openconfig_nat_nat_instances_instance_config', args)
    api_response['globals'] = get_response_dict(response)

    # Get Static configs
    api_response['static'] = get_nat_static_configs(func,args)

    # Get Pools
    response = invoke_api('get_openconfig_nat_nat_instances_instance_nat_pool', args)
    api_response['pools'] = get_response_dict(response)

    # Get Bindings
    response = invoke_api('get_openconfig_nat_nat_instances_instance_nat_acl_pool_binding', args)
    api_response['bindings'] = get_response_dict(response)

    # Get Zones
    api_response['zones'] = get_nat_zones(func,args)

    return api_response
    
def get_nat_output(func, args):
    nat_subcommand = args[1].split("=")[1]
    config_subcommand = args[2].split("=")[1]
    count = args[3].split("=")[1]

    api_response = {}
    file_template = ''

    if nat_subcommand == 'statistics':
        api_response = get_nat_statistics(func,args)
        file_template = 'show_nat_statistics.j2' 
    elif nat_subcommand == 'translations':
        if count == '':
            api_response = get_nat_translations(func,args)
            file_template = 'show_nat_translations.j2'
        else:
            api_response = get_nat_translations_count(func,args)
            file_template = 'show_nat_translations_count.j2'
    else:
        if config_subcommand == '':
            api_response = get_nat_configs(func,args)
            file_template = 'show_nat_configs.j2'
        elif config_subcommand == 'static':
            api_response = get_nat_static_configs(func,args)
            file_template = 'show_nat_static_configs.j2'
        elif config_subcommand == 'zones':
            api_response = get_nat_zones(func,args)
            file_template = 'show_nat_zones.j2'
        elif config_subcommand == 'pool':
            response = invoke_api('get_openconfig_nat_nat_instances_instance_nat_pool', args)
            api_response = get_response_dict(response)
            file_template = 'show_nat_pool.j2'
        elif config_subcommand == 'bindings':
            response = invoke_api('get_openconfig_nat_nat_instances_instance_nat_acl_pool_binding', args)
            api_response = get_response_dict(response)
            file_template = 'show_nat_bindings.j2'
        elif config_subcommand == 'globalvalues':
            response = invoke_api('get_openconfig_nat_nat_instances_instance_config', args)
            api_response = get_response_dict(response)
            file_template = 'show_nat_global_config.j2'

    return api_response, file_template

def run(func, args):
    global config

    try:
       config = True

       args.insert(0,"0")  # NAT instance 0
       api_response = {}
       file_template = ''

       if func == 'show_nat_commands':
           api_response,file_template = get_nat_output(func, args)
       else:
           response = invoke_api(func, args)
           api_response = get_response_dict(response)

       if config == False:
           show_cli_output(file_template, api_response)
 
    except Exception as e:
        print("Failure: %s\n" %(e))


if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])

