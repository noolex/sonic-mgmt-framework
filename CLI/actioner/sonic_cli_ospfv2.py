#!/usr/bin/python
###########################################################################
#
# Copyright 2020 Broadcom.
# The term Broadcom refers to Broadcom Inc. and/or its subsidiaries.
#
###########################################################################

import sys
import time
import json
import ast
from rpipe_utils import pipestr
import cli_client as cc
from scripts.render_cli import show_cli_output

ospf_config_cli_log_enabled = False
def ospf_cli_log(log_string) :
    global ospf_config_cli_log_enabled
    if ospf_config_cli_log_enabled :
        print(log_string)

############## OSPF uris
def get_ospf_router_nw_instance_uri(vrf_name) :
    ospf_router_nwinst_uri = '/restconf/data/openconfig-network-instance:network-instances'
    ospf_router_nwinst_uri += '/network-instance={}'.format(vrf_name)
    return ospf_router_nwinst_uri

def get_ospf_router_uri(vrf_name, instance_id='ospfv2'):
    ospf_router_global_patch_uri = get_ospf_router_nw_instance_uri(vrf_name)
    ospf_router_global_patch_uri += '/protocols/protocol=OSPF,ospfv2/ospfv2'
    return ospf_router_global_patch_uri

def add_key_to_config_data(cfg_body, key_data):
    if len(cfg_body) == 0:
        cfg_body.update({ "config" : key_data })
    elif "config" in cfg_body.keys():
        cfg_body["config"].update(key_data)

def add_cfg_body_to_uri_body(uri_body, cfg_body):
    ospf_cli_log("add_cfg_body_to_uri_body: {} {}".format(uri_body, cfg_body))
    for key, data in cfg_body.items() :
        uri_body.update({ key : data })
    ospf_cli_log("add_cfg_body_to_uri_body: updated uri body {}".format(uri_body))

def validate_delete_response(response):
    if response == None :
        print("validate_delete_response: None Response received")
        return response
    elif response.ok() :
        return response
    elif response.status_code in [ 401, 500 ] :
        ospf_cli_log("validate_delete_response: Error code {}".format(response.status_code))
        ospf_cli_log("validate_delete_response: Ignoring error {}".format( response.error_message()))
        response.status_code = 204
        response.content = None
        return response
    ospf_cli_log("validate_delete_response: {} {}".format(response.status_code, response.error_message()))
    return response

############## OSPF router config
def patch_ospf_router_config(api, vrf_name, cfg_body={}) :
    ospf_cli_log("patch_ospf_router_config: {} {}".format(vrf_name, cfg_body))
    ospf_rtr_uri = get_ospf_router_nw_instance_uri(vrf_name)
    keypath = cc.Path(ospf_rtr_uri)
    ospf_rtr_uri_body = {
        "openconfig-network-instance:network-instance": [{
            "name": vrf_name,
            "protocols" : {
                "protocol": [{
                    "identifier":"OSPF", "name":"ospfv2",
                    "ospfv2": cfg_body
                     }] } }] }
    ospf_cli_log("patch_ospf_router_config: {} body {}".format(ospf_rtr_uri, ospf_rtr_uri_body))
    response = api.patch(keypath, ospf_rtr_uri_body)
    return response

def delete_ospf_router_config(api, vrf_name, cfg_field='') :
    ospf_cli_log("delete_ospf_router_config: {} {}".format(vrf_name, cfg_field))
    ospf_rtr_uri = get_ospf_router_uri(vrf_name, 'ospfv2')
    if cfg_field != '' :
         ospf_rtr_uri += '/{}'.format(cfg_field)
    ospf_cli_log("delete_ospf_router_config: uri {}".format(ospf_rtr_uri))
    keypath = cc.Path(ospf_rtr_uri)
    response = api.delete(keypath)
    return validate_delete_response(response)

############## OSPF router global config
def patch_ospf_router_global_config(api, vrf_name, cfg_body={}) :
    ospf_cli_log("patch_ospf_router_global_config: {} {}".format(vrf_name, cfg_body))
    ospf_rtr_gbl_uri = get_ospf_router_uri(vrf_name)
    keypath = cc.Path(ospf_rtr_gbl_uri)

    key_data = {"openconfig-ospfv2-ext:enable": True}
    add_key_to_config_data(cfg_body, key_data)

    ospf_rtr_gbl_uri_body = {
        "ospfv2" : {
             "global" : cfg_body
        } }

    uri_cfg_body = ospf_rtr_gbl_uri_body["ospfv2"]["global"]
    add_cfg_body_to_uri_body(uri_cfg_body, cfg_body)

    ospf_cli_log("patch_ospf_router_global_config: {} body {}".format(ospf_rtr_gbl_uri, ospf_rtr_gbl_uri_body))
    response = api.patch(keypath, ospf_rtr_gbl_uri_body)
    return response

def delete_ospf_router_global_config(api, vrf_name, cfg_field='') :
    ospf_cli_log("delete_ospf_router_global_config: {} {}".format(vrf_name, cfg_field))
    ospf_rtr_gbl_uri = get_ospf_router_uri(vrf_name, 'ospfv2')
    ospf_rtr_gbl_uri += '/global'
    if cfg_field != '' :
        ospf_rtr_gbl_uri += '/{}'.format(cfg_field)
    ospf_cli_log("delete_ospf_router_global_config: uri {}".format(ospf_rtr_gbl_uri))
    keypath = cc.Path(ospf_rtr_gbl_uri)
    response = api.delete(keypath)
    return validate_delete_response(response)

############## OSPF Area config
def patch_ospf_router_area_config(api, vrf_name, area_id, cfg_body={}) :
    ospf_cli_log("patch_ospf_router_area_config: {} {} {}".format(vrf_name, area_id, cfg_body))
    ospf_rtr_area_uri = get_ospf_router_uri(vrf_name)
    keypath = cc.Path(ospf_rtr_area_uri)

    key_data = {"identifier": area_id }
    add_key_to_config_data(cfg_body, key_data)

    ospf_rtr_area_uri_body = {
        "ospfv2" : {
            "openconfig-network-instance:areas": {
                 "area": [{
                     "identifier": area_id
                  }] } } }

    uri_cfg_body = ospf_rtr_area_uri_body["ospfv2"]["openconfig-network-instance:areas"]["area"][0]
    add_cfg_body_to_uri_body(uri_cfg_body, cfg_body)

    ospf_cli_log("patch_ospf_router_area_config: {} body {}".format(ospf_rtr_area_uri, ospf_rtr_area_uri_body))
    response = api.patch(keypath, ospf_rtr_area_uri_body)
    return response

def delete_ospf_router_area_config(api, vrf_name, area_id, cfg_field='') :
    ospf_cli_log("delete_ospf_router_area_config: {} {} {}".format(vrf_name, area_id, cfg_field))
    ospf_rtr_area_uri = get_ospf_router_uri(vrf_name, 'ospfv2')
    ospf_rtr_area_uri += '/areas/area={}'.format(area_id)
    if cfg_field != '' :
        ospf_rtr_area_uri += '/{}'.format(cfg_field)
    ospf_cli_log("delete_ospf_router_area_config: uri {}".format(ospf_rtr_area_uri))
    keypath = cc.Path(ospf_rtr_area_uri)
    response = api.delete(keypath)
    return validate_delete_response(response)


############## OSPF Area network config
def patch_ospf_router_network_config(api, vrf_name, area_id, network, cfg_body={}) :
    ospf_cli_log("patch_ospf_router_network_config: {} {} {} {}".format(vrf_name, area_id, network, cfg_body))
    ospf_rtr_area_nw_uri = get_ospf_router_uri(vrf_name)
    keypath = cc.Path(ospf_rtr_area_nw_uri)

    key_data = {"openconfig-ospfv2-ext:address-prefix": network }
    add_key_to_config_data(cfg_body, key_data)

    ospf_rtr_area_nw_uri_body = {
        "ospfv2" : {
            "openconfig-network-instance:areas": {
                "area": [{
                    "identifier": area_id,
                    "openconfig-ospfv2-ext:networks": {
                        "network" : [{
                            "address-prefix" : network
                         }] } }] } } }

    temp_entry = ospf_rtr_area_nw_uri_body["ospfv2"]["openconfig-network-instance:areas"]["area"][0]
    uri_cfg_body = temp_entry["openconfig-ospfv2-ext:networks"]["network"][0]
    add_cfg_body_to_uri_body(uri_cfg_body, cfg_body)

    ospf_cli_log("patch_ospf_router_network_config: {} body {}".format(ospf_rtr_area_nw_uri, ospf_rtr_area_nw_uri_body))
    response = api.patch(keypath, ospf_rtr_area_nw_uri_body)
    return response

def delete_ospf_router_network_config(api, vrf_name, area_id, network, cfg_field='') :
    ospf_cli_log("delete_ospf_router_network_config: {} {} {} {}".format(vrf_name, area_id, network, cfg_field))
    ospf_rtr_area_nw_uri = get_ospf_router_uri(vrf_name, 'ospfv2')
    ospf_rtr_area_nw_uri += '/areas/area={}'.format(area_id)
    ospf_rtr_area_nw_uri += '/openconfig-ospfv2-ext:networks/network={nw_prefix}'
    if cfg_field != '' :
        ospf_rtr_area_nw_uri += '/{}'.format(cfg_field)
    ospf_cli_log("delete_ospf_router_network_config: uri {} {}".format(ospf_rtr_area_nw_uri, network))
    keypath = cc.Path(ospf_rtr_area_nw_uri, nw_prefix=network)
    response = api.delete(keypath)
    return validate_delete_response(response)


############## OSPF Virtual link config
def patch_ospf_router_vlink_config(api, vrf_name, area_id, link_id, cfg_body={}) :
    ospf_cli_log("patch_ospf_router_vlink_config: {} {} {} {}".format(vrf_name, area_id, link_id, cfg_body))
    ospf_rtr_vlink_uri = get_ospf_router_uri(vrf_name)
    keypath = cc.Path(ospf_rtr_vlink_uri)

    key_data = {"remote-router-id": link_id, "openconfig-ospfv2-ext:enable": True}
    add_key_to_config_data(cfg_body, key_data)

    ospf_rtr_vlink_uri_body = { "ospfv2" :  {
        "openconfig-network-instance:areas": {
            "area": [ {
                "identifier": area_id,
                "virtual-links": {
                    "virtual-link": [{
                        "remote-router-id": link_id
                     }] } }] } } }

    temp_entry = ospf_rtr_vlink_uri_body["ospfv2"]["openconfig-network-instance:areas"]["area"][0]
    uri_cfg_body = temp_entry["virtual-links"]["virtual-link"][0]
    add_cfg_body_to_uri_body(uri_cfg_body, cfg_body)

    ospf_cli_log("patch_ospf_router_vlink_config: {} body {}".format(ospf_rtr_vlink_uri, ospf_rtr_vlink_uri_body))
    response = api.patch(keypath, ospf_rtr_vlink_uri_body)
    return response

def delete_ospf_router_vlink_config(api, vrf_name, area_id, link_id, cfg_field='') :
    ospf_cli_log("delete_ospf_router_vlink_config: {} {} {} {}".format(vrf_name, area_id, link_id, cfg_field))
    ospf_rtr_vlink_uri = get_ospf_router_uri(vrf_name, 'ospfv2')
    ospf_rtr_vlink_uri += '/areas/area={}'.format(area_id)
    ospf_rtr_vlink_uri += '/virtual-links/virtual-link={}'.format(link_id)
    if cfg_field != '' :
        ospf_rtr_vlink_uri += '/{}'.format(cfg_field)
    ospf_cli_log("delete_ospf_router_vlink_config: uri {}".format(ospf_rtr_vlink_uri))
    keypath = cc.Path(ospf_rtr_vlink_uri)
    response = api.delete(keypath)
    return validate_delete_response(response)

############## OSPF Area address range config
def patch_ospf_router_addr_range_config(api, vrf_name, area_id, addr_range, cfg_body={}) :
    ospf_cli_log("patch_ospf_router_addr_range_config: {} {} {} {}".format(vrf_name, area_id, addr_range, cfg_body))
    ospf_rtr_range_uri = get_ospf_router_uri(vrf_name)
    keypath = cc.Path(ospf_rtr_range_uri)

    key_data = {"openconfig-ospfv2-ext:address-prefix": addr_range }
    add_key_to_config_data(cfg_body, key_data)

    ospf_rtr_range_uri_body = {
        "ospfv2" : {
            "global" : {
                "inter-area-propagation-policies" : {
                    "openconfig-ospfv2-ext:inter-area-policy" : [{
                        "src-area" : area_id,
                            "ranges" : {
                                "range" : [{
                                    "address-prefix" : addr_range
                                 }] } }] } } } }

    temp_entry = ospf_rtr_range_uri_body["ospfv2"]["global"]["inter-area-propagation-policies"]
    temp_entry = temp_entry["openconfig-ospfv2-ext:inter-area-policy"][0]
    uri_cfg_body = temp_entry["ranges"]["range"][0]
    add_cfg_body_to_uri_body(uri_cfg_body, cfg_body)

    ospf_cli_log("patch_ospf_router_addr_range_config: {} body {}".format(ospf_rtr_range_uri, ospf_rtr_range_uri_body))
    response = api.patch(keypath, ospf_rtr_range_uri_body)
    return response

def delete_ospf_router_addr_range_config(api, vrf_name, area_id, addr_range, cfg_field='') :
    ospf_cli_log("delete_ospf_router_addr_range_config: {} {} {} {}".format(vrf_name, area_id, addr_range, cfg_field))
    ospf_rtr_range_uri = get_ospf_router_uri(vrf_name, 'ospfv2')
    ospf_rtr_range_uri += '/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={}'.format(area_id)
    ospf_rtr_range_uri += '/ranges/range={range_prefix}'
    if cfg_field != '' :
        ospf_rtr_range_uri += '/{}'.format(cfg_field)
    ospf_cli_log("delete_ospf_router_addr_range_config: uri {} {}".format(ospf_rtr_range_uri, addr_range))
    keypath = cc.Path(ospf_rtr_range_uri, range_prefix=addr_range)
    response = api.delete(keypath)
    return validate_delete_response(response)


############## OSPF Area Policy config
def patch_ospf_router_area_policy_config(api, vrf_name, area_id, cfg_body={}) :
    ospf_cli_log("patch_ospf_router_area_policy_config: {} {} {}".format(vrf_name, area_id, cfg_body))
    ospf_rtr_apolicy_uri = get_ospf_router_uri(vrf_name)
    keypath = cc.Path(ospf_rtr_apolicy_uri)

    key_data = { "src-area": area_id}
    add_key_to_config_data(cfg_body, key_data)

    ospf_rtr_apolicy_uri_body = {
        "ospfv2" : {
            "global" : {
                "inter-area-propagation-policies" : {
                    "openconfig-ospfv2-ext:inter-area-policy" : [{
                        "src-area" : area_id
                     }] } } } }

    temp_entry = ospf_rtr_apolicy_uri_body["ospfv2"]["global"]["inter-area-propagation-policies"]
    uri_cfg_body = temp_entry["openconfig-ospfv2-ext:inter-area-policy"][0]
    add_cfg_body_to_uri_body(uri_cfg_body, cfg_body)

    ospf_cli_log("patch_ospf_router_area_policy_config: {} body {}".format(ospf_rtr_apolicy_uri, ospf_rtr_apolicy_uri_body))
    response = api.patch(keypath, ospf_rtr_apolicy_uri_body)
    return response

def delete_ospf_router_area_policy_config(api, vrf_name, area_id, cfg_field='') :
    ospf_cli_log("delete_ospf_router_area_policy_config: {} {} {}".format(vrf_name, area_id, cfg_field))
    ospf_rtr_apolicy_uri = get_ospf_router_uri(vrf_name, 'ospfv2')
    ospf_rtr_apolicy_uri += '/global/inter-area-propagation-policies/openconfig-ospfv2-ext:inter-area-policy={}'.format(area_id)
    if cfg_field != '' :
        ospf_rtr_apolicy_uri += '/{}'.format(cfg_field)
    ospf_cli_log("delete_ospf_router_area_policy_config: uri {}".format(ospf_rtr_apolicy_uri))
    keypath = cc.Path(ospf_rtr_apolicy_uri)
    response = api.delete(keypath)
    return validate_delete_response(response)


############## OSPF Redistribute route config
def patch_ospf_router_resdistribute_config(api, vrf_name, protocol, direction, cfg_body={}) :
    ospf_cli_log("patch_ospf_router_resdistribute_config: {} {} {} {}".format(vrf_name, protocol, direction, cfg_body))
    ospf_rtr_redist_uri = get_ospf_router_uri(vrf_name)
    keypath = cc.Path(ospf_rtr_redist_uri)

    key_data = {"protocol": protocol, "direction": direction }
    add_key_to_config_data(cfg_body, key_data)

    ospf_rtr_redist_uri_body = {
        "ospfv2" : {
            "global": {
                "openconfig-ospfv2-ext:route-distribution-policies": {
                    "distribute-list": [ {
                        "protocol": protocol,
                        "direction": direction
                     } ] } } } }

    temp_entry = ospf_rtr_redist_uri_body["ospfv2"]["global"]
    uri_cfg_body = temp_entry["openconfig-ospfv2-ext:route-distribution-policies"]["distribute-list"][0]
    add_cfg_body_to_uri_body(uri_cfg_body, cfg_body)

    ospf_cli_log("patch_ospf_router_resdistribute_config: {} body {}".format(ospf_rtr_redist_uri, ospf_rtr_redist_uri_body))
    response = api.patch(keypath, ospf_rtr_redist_uri_body)
    return response

def delete_ospf_router_resdistribute_config(api, vrf_name, protocol, direction, cfg_field='') :
    ospf_cli_log("delete_ospf_router_resdistribute_config: {} {} {} {}".format(vrf_name, protocol, direction, cfg_field))
    ospf_rtr_redist_uri = get_ospf_router_uri(vrf_name, 'ospfv2')
    ospf_rtr_redist_uri += '/global/openconfig-ospfv2-ext:route-distribution-policies'
    ospf_rtr_redist_uri += '/distribute-list={},{}'.format(protocol, direction)
    if cfg_field != '' :
        ospf_rtr_redist_uri += '/{}'.format(cfg_field)
    ospf_cli_log("delete_ospf_router_resdistribute_config: uri {}".format(ospf_rtr_redist_uri))
    keypath = cc.Path(ospf_rtr_redist_uri)
    response = api.delete(keypath)
    return validate_delete_response(response)

############## OSPF Passive interface config
def patch_ospf_router_passive_interface_config(api, vrf_name, intf_name, if_addr, cfg_body={}) :
    ospf_cli_log("patch_ospf_router_passive_interface_config: {} {} {} {}".format(vrf_name, intf_name, if_addr, cfg_body))
    ospf_rtr_pif_uri = get_ospf_router_uri(vrf_name)
    keypath = cc.Path(ospf_rtr_pif_uri)

    key_data = {"name": intf_name, "address": if_addr }
    add_key_to_config_data(cfg_body, key_data)

    ospf_rtr_pif_uri_body = {
        "ospfv2" : {
            "global": {
                "openconfig-ospfv2-ext:passive-interfaces": {
                    "passive-interface": [ {
                        "name": intf_name,
                        "address": if_addr
                     } ] } } } }

    temp_entry = ospf_rtr_pif_uri_body["ospfv2"]["global"]
    uri_cfg_body = temp_entry["openconfig-ospfv2-ext:passive-interfaces"]["passive-interface"][0]
    add_cfg_body_to_uri_body(uri_cfg_body, cfg_body)

    ospf_cli_log("patch_ospf_router_passive_interface_config: {} body {}".format(ospf_rtr_pif_uri, ospf_rtr_pif_uri_body))
    response = api.patch(keypath, ospf_rtr_pif_uri_body)
    return response

def delete_ospf_router_passive_interface_config(api, vrf_name, intf_name, if_addr, cfg_field='') :
    ospf_cli_log("delete_ospf_router_passive_interface_config: {} {} {} {}".format(vrf_name, intf_name, if_addr, cfg_field))
    ospf_rtr_pif_uri = get_ospf_router_uri(vrf_name, 'ospfv2')
    ospf_rtr_pif_uri += '/global/openconfig-ospfv2-ext:passive-interfaces'
    ospf_rtr_pif_uri += '/passive-interface={},{}'.format(intf_name, if_addr)
    if cfg_field != '' :
        ospf_rtr_pif_uri += '/{}'.format(cfg_field)
    ospf_cli_log("delete_ospf_router_passive_interface_config: uri {}".format(ospf_rtr_pif_uri))
    keypath = cc.Path(ospf_rtr_pif_uri)
    response = api.delete(keypath)
    return validate_delete_response(response)

############## OSPF interface config
def get_ospf_intf_uri(intf_name, sub_intf=0):
    ospf_intf_patch_uri = '/restconf/data/openconfig-interfaces:interfaces/interface={}'.format(intf_name)
    ospf_intf_patch_uri += '/subinterfaces/subinterface={}'.format(sub_intf)
    return ospf_intf_patch_uri

def patch_ospf_interface_config(api, intf_name, intf_addr, cfg_body={}) :
    ospf_cli_log("patch_ospf_interface_config: {} {} {}".format(intf_name, intf_addr, cfg_body))
    ospf_intf_uri = get_ospf_intf_uri(intf_name, 0)
    keypath = cc.Path(ospf_intf_uri)

    key_data = {"address": intf_addr }
    add_key_to_config_data(cfg_body, key_data)

    ospf_intf_uri_body = {
        "openconfig-interfaces:subinterface": [{
            "index": 0,
            "openconfig-if-ip:ipv4": {
                 "openconfig-ospfv2-ext:ospfv2": {
                     "if-addresses": [{
                         "address": intf_addr
                      }] } }  }] }

    temp_entry = ospf_intf_uri_body["openconfig-interfaces:subinterface"][0]
    temp_entry = temp_entry["openconfig-if-ip:ipv4"]["openconfig-ospfv2-ext:ospfv2"]
    uri_cfg_body = temp_entry["if-addresses"][0]
    add_cfg_body_to_uri_body(uri_cfg_body, cfg_body)

    ospf_cli_log("patch_ospf_interface_config: {} body {}".format(ospf_intf_uri, ospf_intf_uri_body))
    response = api.patch(keypath, ospf_intf_uri_body)
    return response

def delete_ospf_interface_config(api, intf_name, intf_addr, cfg_field) :
    ospf_cli_log("delete_ospf_interface_config: {} {} {}".format(intf_name, intf_addr, cfg_field))
    ospf_intf_uri = get_ospf_intf_uri(intf_name, 0)
    ospf_intf_uri += '/openconfig-if-ip:ipv4/openconfig-ospfv2-ext:ospfv2'
    if intf_addr != '' :
        ospf_intf_uri += '/if-addresses={}'.format(intf_addr)
        if cfg_field != '' :
            ospf_intf_uri += '/{}'.format(cfg_field)
    ospf_cli_log("delete_ospf_interface_config: uri {}".format(ospf_intf_uri))
    keypath = cc.Path(ospf_intf_uri)
    response = api.delete(keypath)
    return validate_delete_response(response)

############## OSPF utility apis
def area_to_dotted(area):
    areastr = "{}".format(area)
    if areastr.isdigit():
        areaInt = int(area)
        b0 = ((areaInt >> 24) & 0xff)
        b1 = ((areaInt >> 16) & 0xff)
        b2 = ((areaInt >> 8) & 0xff)
        b3 = ((areaInt & 0xff))
        areaDotted = "{}.{}.{}.{}".format(b0, b1, b2, b3)
        return areaDotted
    else :
        return areastr

def cli_to_db_protocol_map(cli_protocol):
    db_protocol = None
    protocol_map = { "ospf" : "OSPF",
                     "bgp" : "BGP",
                     "static" : "STATIC",
                     "kernel": "KERNEL",
                     "connected" : "DIRECTLY_CONNECTED",
                     "table" : "DEFAULT_ROUTE" }
    if cli_protocol != None :
        if cli_protocol in protocol_map.keys() :
            db_protocol = protocol_map[cli_protocol]
    return db_protocol


############## OSPF CLI invoke function
def invoke_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None

    #Ospf router config
    if func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_config':
        body = { "global" : { "config" : {"openconfig-ospfv2-ext:enable": True} } }
        return patch_ospf_router_config(api, args[0], body)

    elif func == 'delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global':
        return delete_ospf_router_config(api, args[0], "global")

    #Ospf router global config commands
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_config_router_id':
        body = { "config" : {"router-id": args[1]} }
        return patch_ospf_router_global_config(api, args[0], body)

    elif func == 'delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_config_router_id':
        return delete_ospf_router_global_config(api, args[0], 'config/router-id')

    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_config_log_adjacency_changes':
        logtype = ""
        for arg in args:
            if (arg == "detail"):
                logtype = "detail"

        if (logtype != ""):
            body = { "config" : {"openconfig-ospfv2-ext:log-adjacency-state-changes": "DETAIL"} }
        else:
            body = { "config" : {"openconfig-ospfv2-ext:log-adjacency-state-changes": "BRIEF"}}

        return patch_ospf_router_global_config(api, args[0], body)

    elif func == 'delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_config_log_adjacency_changes':
        logtype = ""
        for arg in args:
            if (arg == "detail"):
                logtype = "detail"

        if (logtype != ""):
            body = { "config" : {"openconfig-ospfv2-ext:log-adjacency-state-changes": "BRIEF"}}
            return patch_ospf_router_global_config(api, args[0], body)
        else:
            return delete_ospf_router_global_config(api, args[0], 'config/openconfig-ospfv2-ext:log-adjacency-state-changes')

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_auto_cost_reference_bandwidth':
        body = { "config" : {"openconfig-ospfv2-ext:auto-cost-reference-bandwidth": int(args[1])} }
        return patch_ospf_router_global_config(api, args[0], body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_auto_cost_reference_bandwidth':
        return delete_ospf_router_global_config(api, args[0], 'config/openconfig-ospfv2-ext:auto-cost-reference-bandwidth')

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_write_multiplier':
        body = { "config" : {"openconfig-ospfv2-ext:write-multiplier": int(args[1])} }
        return patch_ospf_router_global_config(api, args[0], body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_write_multiplier':
        return delete_ospf_router_global_config(api, args[0], 'config/openconfig-ospfv2-ext:write-multiplier')

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config':
        vrf = args[0]
        abrtypecmdval = ""
        routeridval = ""

        i = 0
        for arg in args:
            if (arg == "abr-type"):
                abrtypecmdval = args[i + 1]
            if (arg == "router-id"):
                routeridval = args[i + 1]
            i = i + 1

        if (abrtypecmdval != ""):
            body = { "config" : {"openconfig-ospfv2-ext:abr-type": abrtypecmdval.upper()} }
            return patch_ospf_router_global_config(api, args[0], body)

        if (routeridval != ""):
            body = { "config" : {"openconfig-network-instance:router-id": routeridval} }
            return patch_ospf_router_global_config(api, args[0], body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config':
        vrf = args[0]
        abrtypecmd = ""
        routeridcmd = ""

        for arg in args:
            if (arg == "abr-type"):
                abrtypecmd = "abr-type"
            if (arg == "router-id"):
                routeridcmd = "router-id"

        if (abrtypecmd != ""):
            return delete_ospf_router_global_config(api, args[0], 'config/openconfig-ospfv2-ext:abr-type')

        if (routeridcmd != ""):
            return delete_ospf_router_global_config(api, args[0], 'config/router-id')

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_ospf_rfc1583_compatible':
        body = { "config" : {"openconfig-ospfv2-ext:ospf-rfc1583-compatible": True} }
        return patch_ospf_router_global_config(api, args[0], body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_ospf_rfc1583_compatible':
        return delete_ospf_router_global_config(api, args[0], 'config/openconfig-ospfv2-ext:ospf-rfc1583-compatible')

    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_config_default_metric':
        body = {"config": {"default-metric": int(args[1])}}
        return patch_ospf_router_global_config(api, args[0], body)

    elif func == 'delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_config_default_metric':
        return delete_ospf_router_global_config(api, args[0], 'config/openconfig-ospfv2-ext:default-metric')

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_passive_interface':
        vrf = args[0]
        cmdtype = ""

        for arg in args[1:]:
            if (arg == "default"):
                cmdtype = "default"

        if (cmdtype != ""):
            body = { "config" : {"openconfig-ospfv2-ext:passive-interface-default": True} }
            return patch_ospf_router_global_config(api, args[0], body)
        else:
            return patch_ospf_router_passive_interface_config(api, args[0], args[1], args[2])

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_config_passive_interface':
        vrf = args[0]
        cmdtype = ""

        for arg in args[1:]:
            if (arg == "default"):
                cmdtype = "default"

        if (cmdtype != ""):
            return delete_ospf_router_global_config(api, args[0], 'config/openconfig-ospfv2-ext:passive-interface-default')
        else:
            return delete_ospf_router_passive_interface_config(api, args[0], args[1], args[2])

    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_timers':
        vrf = args[0]
        minarrival_val = ""
        throttletype = ""
        spfdelay = ""
        spfinitial = ""
        spfhold = ""
        lsadelayval = ""

        i = 0
        for arg in args:
            if (arg == "throttle"):
                throttletype = args[i + 1]
                if (throttletype == "spf"):
                    spfinitial  = args[i + 2]
                    spfmax      = args[i + 3]
                    spfthrottle = args[i + 4]
                else:
                    lsadelayval = args[i + 3]
            elif (arg == "min-arrival"):
                minarrival_val = args[i + 1]
            i = i + 1

        if (throttletype == ""):
            body = { "timers" : { "lsa-generation" : { "config" : {"openconfig-ospfv2-ext:minimum-arrival": int(minarrival_val)}}}}
            return patch_ospf_router_global_config(api, args[0], body)

        if (throttletype == "spf"):
            cfg_body = { "initial-delay": int(spfinitial), "maximum-delay": int(spfmax),
                         "openconfig-ospfv2-ext:throttle-delay": int(spfthrottle) }
            body = { "timers" : { "openconfig-network-instance:spf": { "config": cfg_body }} }
            return patch_ospf_router_global_config(api, args[0], body)
        else:
            body = { "timers" : { "lsa-generation" : { "config" : {"openconfig-ospfv2-ext:minimum-interval": int(lsadelayval)}}}}
            return patch_ospf_router_global_config(api, args[0], body)


    elif func == 'delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_ospfv2_global_timers':
        vrf = args[0]
        throttletype = ""

        i = 0
        for arg in args:
            if (arg == "throttle"):
                throttletype = args[i + 1]
            i = i + 1

        if (throttletype == ""):
            return delete_ospf_router_global_config(api, args[0], 'timers/lsa-generation/config/openconfig-ospfv2-ext:minimum-arrival')

        if (throttletype == "spf"):
            response = delete_ospf_router_global_config(api, args[0], 'timers/spf/config/initial-delay')
            if response.ok() == False : return response

            response = delete_ospf_router_global_config(api, args[0], 'timers/spf/config/maximum-delay')
            if response.ok() == False : return response

            response = delete_ospf_router_global_config(api, args[0], 'timers/spf/config/openconfig-ospfv2-ext:throttle-delay')
            if response.ok() == False : return response
        else:
            response = delete_ospf_router_global_config(api, args[0], 'timers/lsa-generation/config/openconfig-ospfv2-ext:minimum-interval')

        return response

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_max_metric_config':
        vrf = args[0]
        metrictypeadmin = ""
        sratupmetricval = ""

        i = 0
        for arg in args:
            if (arg == "administrative"):
                metrictypeadmin = "administrative:"
            if (arg == "on-startup"):
                sratupmetricval = args[i + 1]
            i = i +1

        if (metrictypeadmin != ""):
            body = { "timers" : { "max-metric" : { "config" : {"openconfig-ospfv2-ext:administrative": True}}}}
            return patch_ospf_router_global_config(api, args[0], body)
        else:
            body = { "timers" : { "max-metric" : { "config" : {"openconfig-ospfv2-ext:on-startup": int(sratupmetricval)} }}}
            return patch_ospf_router_global_config(api, args[0], body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_max_metric_config':
        vrf = args[0]
        metrictypeadmin = ""

        for arg in args:
            if (arg == "administrative"):
                metrictypeadmin = "administrative:"

        if (metrictypeadmin != ""):
            return delete_ospf_router_global_config(api, args[0], 'timers/max-metric/config/openconfig-ospfv2-ext:administrative')
        else:
            return delete_ospf_router_global_config(api, args[0], 'timers/max-metric/config/openconfig-ospfv2-ext:on-startup')

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_lsa_generation_config_refresh_timer':
        body = { "timers" : { "lsa-generation" : { "config" : {"openconfig-ospfv2-ext:refresh-timer": int(args[1])}}}}
        return patch_ospf_router_global_config(api, args[0], body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_timers_lsa_generation_config_refresh_timer':
        return delete_ospf_router_global_config(api, args[0], 'timers/lsa-generation/config/openconfig-ospfv2-ext:refresh-timer')

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distance_config':
        vrf = args[0]
        extdistance = ""
        interareadist = ""
        intraareadist = ""
        ospfcmd = ""
        response = ""

        i = 0
        for arg in args:
            if ("external" == arg):
                extdistance = args[i + 1]
            if ("inter-area" == arg):
                interareadist = args[i + 1]
            if ("intra-area" == arg):
                intraareadist = args[i + 1]
            if ("ospf" == arg):
                ospfcmd = "ospf"
            i = i + 1

        if (extdistance == "" and interareadist == "" and intraareadist == "" and ospfcmd == ""):
            body = { "openconfig-ospfv2-ext:distance" : { "config" : {"openconfig-ospfv2-ext:all": int(args[2])}}}
            response = patch_ospf_router_global_config(api, args[0], body)
            if response.ok() == False : return response

        if (extdistance != ""):
            body = { "openconfig-ospfv2-ext:distance" : { "config" : {"openconfig-ospfv2-ext:external": int(extdistance)}}}
            response = patch_ospf_router_global_config(api, args[0], body)
            if response.ok() == False : return response

        if (intraareadist != ""):
            body = { "openconfig-ospfv2-ext:distance" : { "config" : {"openconfig-ospfv2-ext:intra-area": int(intraareadist)}}}
            response = patch_ospf_router_global_config(api, args[0], body)
            if response.ok() == False : return response

        if (interareadist != ""):
            body = { "openconfig-ospfv2-ext:distance" : { "config" : {"openconfig-ospfv2-ext:inter-area": int(interareadist)}}}
            response = patch_ospf_router_global_config(api, args[0], body)
            if response.ok() == False : return response

        return response

    #Ospf router Route distribution commands
    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distance_config':
        vrf = args[0]
        extcmd = ""
        interareacmd = ""
        intraareacmd = ""
        ospfcmd = ""
        response = ""

        i = 0
        for arg in args:
            if ("external" == arg):
                extcmd = "external"
            if ("inter-area" == arg):
                interareacmd = "inter-area"
            if ("intra-area" == arg):
                intraareacmd = "intra-area"
            if ("ospf" == arg):
                ospfcmd = "ospf"
            i = i + 1

        if (extcmd == "" and interareacmd == "" and intraareacmd == "" and ospfcmd == ""):
            response = delete_ospf_router_global_config(api, args[0], 'openconfig-ospfv2-ext:distance/config/all')
            if response.ok() == False : return response

        if (extcmd != ""):
            response = delete_ospf_router_global_config(api, args[0], 'openconfig-ospfv2-ext:distance/config/external')
            if response.ok() == False : return response

        if (intraareacmd != ""):
            response = delete_ospf_router_global_config(api, args[0], 'openconfig-ospfv2-ext:distance/config/intra-area')
            if response.ok() == False : return response

        if (interareacmd != ""):
            response = delete_ospf_router_global_config(api, args[0], 'openconfig-ospfv2-ext:distance/config/inter-area')
            if response.ok() == False : return response

        return response

    #--------Ospf router default origin commands
    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_import':
        vrf = args[0]
        alwayscmd = ""
        metricval = ""
        metrictypeval = ""
        routemap = ""

        body = { "config" : {} }
        i = 0
        for arg in args:
            if ("always" == arg):
                alwayscmd = "always"
                body["config"].update({"openconfig-ospfv2-ext:always": True})
            if ("metric" == arg):
                metricval = args[i + 1]
                if (metricval != ""):
                    body["config"].update({"openconfig-ospfv2-ext:metric": int(metricval)})
            if ("metric-type" == arg):
                metrictypeval = args[i + 1]
                if ("1" == metrictypeval):
                    body["config"].update({"openconfig-ospfv2-ext:metric-type": "TYPE_1"})
                if ("2" == metrictypeval):
                    body["config"].update({"openconfig-ospfv2-ext:metric-type": "TYPE_2"})
            if ("route-map" == arg):
                routemapval = args[i + 1]
                if (routemapval != ""):
                    body["config"].update({"openconfig-ospfv2-ext:route-map": routemapval})
            i = i + 1

        if (alwayscmd == "" and  metricval == "" and metrictypeval == "" and routemapval == ""):
            response = patch_ospf_router_resdistribute_config(api, vrf, "DEFAULT_ROUTE", "IMPORT")
            if response.ok() == False : return response
        elif len(body["config"]) :
            response = patch_ospf_router_resdistribute_config(api, vrf, "DEFAULT_ROUTE", "IMPORT", body)

        return response

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_access_list':
        exportprotocol = cli_to_db_protocol_map(args[1])
        body = { "config" : {"openconfig-ospfv2-ext:access-list": (args[2])}}
        return patch_ospf_router_resdistribute_config(api, args[0], exportprotocol, "EXPORT", body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_access_list':
        exportprotocol = cli_to_db_protocol_map(args[1])
        return delete_ospf_router_resdistribute_config(api, args[0], exportprotocol, "EXPORT", 'config/access-list')

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_import':
        vrf = args[0]
        alwayscmd = ""
        metriccmd = ""
        metrictypecmd = ""
        routemapcmd = ""

        i = 0
        for arg in args:
            if ("always" == arg):
                alwayscmd = "always"
            if ("metric" == arg):
                metriccmd = "metriccmd"
            if ("metric-type" == arg):
                metrictypecmd = "metrictypecmd"
            if ("route-map" == arg):
                routemapcmd = "routemapcmd"
            i = i + 1

        if (alwayscmd == "" and  metriccmd == "" and metrictypecmd == "" and routemapcmd == ""):
            response = delete_ospf_router_resdistribute_config(api, vrf, "DEFAULT_ROUTE", "IMPORT")
            if response.ok() == False : return response

        if (alwayscmd != ""):
            response = delete_ospf_router_resdistribute_config(api, vrf, "DEFAULT_ROUTE", "IMPORT", 'config/always')
            if response.ok() == False : return response

        if (metriccmd != ""):
            response = delete_ospf_router_resdistribute_config(api, vrf, "DEFAULT_ROUTE", "IMPORT", 'config/metric')
            if response.ok() == False : return response

        if (metrictypecmd != ""):
            response = delete_ospf_router_resdistribute_config(api, vrf, "DEFAULT_ROUTE", "IMPORT", 'config/metric-type')
            if response.ok() == False : return response

        if (routemapcmd != ""):
            response = delete_ospf_router_resdistribute_config(api, vrf, "DEFAULT_ROUTE", "IMPORT", 'config/route-map')
            if response.ok() == False : return response

        return response

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_always':
        body = { "config" : {"openconfig-ospfv2-ext:always": True} }
        return  patch_ospf_router_resdistribute_config(api, args[0], 'DEFAULT_ROUTE', "IMPORT", body)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_metric':
        body = { "config" : {"openconfig-ospfv2-ext:metric": int(args[2])} }
        return patch_ospf_router_resdistribute_config(api, args[0], "DEFAULT_ROUTE", "IMPORT", body)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_metric_type':
        body = {}
        if ("1" == args[2]):
            body = {"config" : {"openconfig-ospfv2-ext:metric-type": "TYPE_1" }}
        elif ("2" == args[2]):
            body = {"config" : {"openconfig-ospfv2-ext:metric-type": "TYPE_2" }}

        if len(body) :
            return patch_ospf_router_resdistribute_config(api, args[0], "DEFAULT_ROUTE", "IMPORT", body)

    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_route_map_default':
        routemapval = args[2]
        body = {"config" : {"openconfig-ospfv2-ext:route-map": routemapval} }
        return patch_ospf_router_resdistribute_config(api, args[0], "DEFAULT_ROUTE", "IMPORT", body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_distribute_list_config_route_map_default':
        return delete_ospf_router_resdistribute_config(api, vrf, "DEFAULT_ROUTE", "IMPORT", 'config/route-map')


    #--------Ospf router Redistribute commands
    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_redistribute_list_config_import':
        vrf = args[0]
        protocol = ""
        metricval = ""
        metrictypeval = ""
        routemapval = ""
        importprotocol = cli_to_db_protocol_map(args[1])

        body = { "config" : {} }
        i = 0
        for arg in args:
            if ("metric" == arg):
                metricval = args[i + 1]
                if (metricval != ""):
                    body["config"].update({"openconfig-ospfv2-ext:metric": int(metricval)})
            if ("metric-type" == arg):
                metrictypeval = args[i + 1]
                if ("1" == metrictypeval):
                    body["config"].update({"openconfig-ospfv2-ext:metric-type": "TYPE_1"})
                if ("2" == metrictypeval):
                    body["config"].update({"openconfig-ospfv2-ext:metric-type": "TYPE_2"})
            if ("route-map" == arg):
                routemapval = args[i + 1]
                if (routemapval != ""):
                    body["config"].update({"openconfig-ospfv2-ext:route-map": routemapval})
            i = i + 1

        if (metricval == "" and metrictypeval == "" and routemapval == ""):
            response = patch_ospf_router_resdistribute_config(api, vrf, importprotocol, "IMPORT")
            if response.ok() == False : return response
        elif len(body) :
            response = patch_ospf_router_resdistribute_config(api, vrf, importprotocol, "IMPORT", body)

        return response

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_global_route_distribution_policies_redistribute_list_config_import':
        vrf = args[0]
        protocol = ""
        metriccmd = ""
        metrictypecmd = ""
        routemapcmd = ""
        importprotocol = cli_to_db_protocol_map(args[1])

        i = 0
        for arg in args:
            if (arg == "metric"):
                metriccmd = "metric"
            elif (arg == "metric-type"):
                metrictypecmd = "metric-type"
            elif (arg == "route-map"):
                routemapcmd = "route-map"
            i = i + 1

        if (metriccmd == "" and metrictypecmd == "" and routemapcmd == ""):
            response = delete_ospf_router_resdistribute_config(api, vrf, importprotocol, "IMPORT")
            if response.ok() == False : return response

        if (metriccmd != ""):
            response = delete_ospf_router_resdistribute_config(api, vrf, importprotocol, "IMPORT", 'config/metric')
            if response.ok() == False : return response

        if (metrictypecmd != ""):
            response = delete_ospf_router_resdistribute_config(api, vrf, importprotocol, "IMPORT", 'config/metric-type')
            if response.ok() == False : return response

        if (routemapcmd != ""):
            response = delete_ospf_router_resdistribute_config(api, vrf, importprotocol, "IMPORT", 'config/always')
            if response.ok() == False : return response

        return response

    #--------Ospf router Area and its sub commands
    elif func == 'patch_openconfig_ospfv2_area':
        vrf = args[0]
        areaidval = area_to_dotted(args[1])
        vlinkid = ""

        i = 0
        for arg in args:

            if (arg == "authentication"):
                if (len(args[i:]) > 1 and args[i + 1] == "message-digest"):
                    body = { "config" : {"openconfig-ospfv2-ext:authentication-type": "MD5HMAC"}}
                    return patch_ospf_router_area_config(api, vrf, areaidval, body)
                else:
                    body = { "config" : {"openconfig-ospfv2-ext:authentication-type": "TEXT"}}
                    return patch_ospf_router_area_config(api, vrf, areaidval, body)

            elif (arg == "default-cost"):
                body = { "openconfig-ospfv2-ext:stub" : { "config" : { "openconfig-ospfv2-ext:default-cost": int(args[i + 1])} }}
                return patch_ospf_router_area_config(api, vrf, areaidval, body)

            elif (arg == "filter-list"):
                prefixname = args[i + 2]
                direction = args[i + 3]
                if (direction == "in"):
                    body = { "openconfig-ospfv2-ext:filter-list-in" : { "config" : {"openconfig-ospfv2-ext:name": prefixname} }}
                    return patch_ospf_router_area_policy_config(api, vrf, areaidval, body)
                elif (direction == "out"):
                    body = { "openconfig-ospfv2-ext:filter-list-out" : { "config" : {"openconfig-ospfv2-ext:name": prefixname} }}
                    return patch_ospf_router_area_policy_config(api, vrf, areaidval, body)

            elif (arg == "shortcut"):
                shortcuttype = ""
                if args[i + 1] != "" :
                    shortcuttype = args[i + 1].upper()
                body = {"config": {"openconfig-ospfv2-ext:shortcut": shortcuttype} }
                return patch_ospf_router_area_config(api, vrf, areaidval, body)

            elif (arg == "stub"):
                if (len(args[i:]) > 1):
                    body = { "openconfig-ospfv2-ext:stub" : { "config" : {"openconfig-ospfv2-ext:enable": True, "no-summary": True}}}
                    return patch_ospf_router_area_config(api, vrf, areaidval, body)
                else:
                    body = { "openconfig-ospfv2-ext:stub" : { "config" : { "openconfig-ospfv2-ext:enable": True} }}
                    return patch_ospf_router_area_config(api, vrf, areaidval, body)

            elif (arg == "range"):
                addr_range = args[i + 1]

                if (len(args[(i + 1):]) == 1):
                    return patch_ospf_router_addr_range_config(api, vrf, areaidval, addr_range)

                body = {"config": {} }
                j = i + 1
                for rangearg in args[j:]:
                    if (rangearg == "advertise"):
                        body["config"].update({"openconfig-ospfv2-ext:advertise": True })
                    elif (rangearg == "cost"):
                        body["config"].update( {"openconfig-ospfv2-ext:metric": int(args[j + 1])} )
                    elif (rangearg == "not-advertise"):
                        body["config"].update({"openconfig-ospfv2-ext:advertise": False })
                    elif (rangearg == "substitute"):
                        body["config"].update({"openconfig-ospfv2-ext:substitue-prefix": args[j + 1]} )
                    j = j + 1

                if len(body["config"]) :
                    return patch_ospf_router_addr_range_config(api, vrf, areaidval, addr_range, body)

            elif (arg == "virtual-link"):
                vlinkid = args[i + 1]

                if (len(args[(i + 1):]) == 1):
                     body = { "config" : {"openconfig-ospfv2-ext:enable": True} }
                     return patch_ospf_router_vlink_config(api, vrf, areaidval, vlinkid)

                j = i
                for vlinkarg in args[i:]:
                    if (vlinkarg == "dead-interval"):
                        body = { "config" : {"openconfig-ospfv2-ext:dead-interval": int(args[j + 1])}}
                        return patch_ospf_router_vlink_config(api, vrf, areaidval, vlinkid, body)

                    if (vlinkarg == "hello-interval"):
                        body = { "config" : {"openconfig-ospfv2-ext:hello-interval": int(args[j + 1])} }
                        return patch_ospf_router_vlink_config(api, vrf, areaidval, vlinkid, body)

                    if  (vlinkarg == "retransmit-interval"):
                        body = { "config" : {"openconfig-ospfv2-ext:retransmission-interval": int(args[j + 1])}}
                        response = patch_ospf_router_vlink_config(api, vrf, areaidval, vlinkid, body)
                        if response.ok() == False : return response

                    if (vlinkarg == "transmit-delay"):
                        body = { "config" : {"openconfig-ospfv2-ext:transmit-delay": int(args[j + 1])}}
                        return patch_ospf_router_vlink_config(api, vrf, areaidval, vlinkid, body)

                    if (vlinkarg == "authentication"):
                        if (args[j + 1] == "null"):
                            body = { "config" : {"openconfig-ospfv2-ext:authentication-type": "NONE"}}
                            response = patch_ospf_router_vlink_config(api, vrf, areaidval, vlinkid, body)
                            if response.ok() == False : return response
                        elif (args[j + 1] == "message-digest") :
                            if (len(args[(j + 1):]) > 1):
                                body = { "config" : {"openconfig-ospfv2-ext:authentication-type": "MD5HMAC",
                                                     "openconfig-ospfv2-ext:authentication-key-id": int(args[j + 3]),
                                                     "openconfig-ospfv2-ext:authentication-md5-key": args[j + 5] }}
                                response = patch_ospf_router_vlink_config(api, vrf, areaidval, vlinkid, body)
                                if response.ok() == False : return response
                            else :
                                body = { "config" : {"openconfig-ospfv2-ext:authentication-type": "MD5HMAC"} }
                                response = patch_ospf_router_vlink_config(api, vrf, areaidval, vlinkid, body)
                                if response.ok() == False : return response
                        else :
                            body = { "config" : {"openconfig-ospfv2-ext:authentication-type": "TEXT"}}
                            response = patch_ospf_router_vlink_config(api, vrf, areaidval, vlinkid, body)
                            if response.ok() == False : return response

                    if (vlinkarg == "authentication-key"):
                        body = { "config" : {"openconfig-ospfv2-ext:authentication-key": args[j + 1]}}
                        response = patch_ospf_router_vlink_config(api, vrf, areaidval, vlinkid, body)
                        if response.ok() == False : return response

                    j = j + 1

                return response
            i = i + 1

    elif func == 'delete_openconfig_ospfv2_area':
        vrf = args[0]
        areaidval = area_to_dotted(args[1])
        vlinkid = ""
        response = None

        i = 0
        for arg in args:
            if (arg == "authentication"):
                return delete_ospf_router_area_config(api, vrf, areaidval, 'config/openconfig-ospfv2-ext:authentication-type')

            elif (arg == "default-cost"):
                return delete_ospf_router_area_config(api, vrf, areaidval, 'openconfig-ospfv2-ext:stub/config/default-cost')

            if (arg == "filter-list"):
                direction = args[i + 2]
                if (direction == "in"):
                    return delete_ospf_router_area_policy_config(api, vrf, areaidval, 'filter-list-in')
                elif (direction == "out"):
                    return delete_ospf_router_area_policy_config(api, vrf, areaidval, 'filter-list-out')

            elif (arg == "shortcut"):
                return delete_ospf_router_area_config(api, vrf, areaidval, 'config/openconfig-ospfv2-ext:shortcut')

            elif (arg == "stub"):
                if (len(args[i:]) > 1):
                    return  delete_ospf_router_area_config(api, vrf, areaidval, 'openconfig-ospfv2-ext:stub/config/no-summary')
                else:
                    return delete_ospf_router_area_config(api, vrf, areaidval, 'openconfig-ospfv2-ext:stub')

            elif (arg == "range"):
                addr_range = args[i + 1]

                if (len(args[(i + 1):]) == 1):
                    return delete_ospf_router_addr_range_config(api, vrf, areaidval, addr_range)

                j = i + 1
                for rangearg in args[j:]:
                    if (rangearg == "advertise"):
                        if (len(args[j:]) > 1):
                            return delete_ospf_router_addr_range_config(api, vrf, area_to_dotted(areaidval), addr_range, 'config/metric')
                        else:
                            return delete_ospf_router_addr_range_config(api, vrf, area_to_dotted(areaidval), addr_range, 'config/advertise')
                    elif (rangearg == "cost"):
                        return delete_ospf_router_addr_range_config(api, vrf, area_to_dotted(areaidval), addr_range, 'config/metric')
                    elif (rangearg == "not-advertise"):
                        return delete_ospf_router_addr_range_config(api, vrf, area_to_dotted(areaidval), addr_range, 'config/advertise')
                    elif (rangearg == "substitute"):
                        return delete_ospf_router_addr_range_config(api, vrf, area_to_dotted(areaidval), addr_range, 'config/substitue-prefix')
                    j = j + 1

            elif (arg == "virtual-link"):
                vlinkid = args[i +1]

                if (len(args[(i + 1):]) == 1):
                    return delete_ospf_router_vlink_config(api, vrf, areaidval, vlinkid)

                j = i + 1
                for vlinkarg in args[i:]:
                    if (vlinkarg == "dead-interval"):
                        return delete_ospf_router_vlink_config(api, vrf, areaidval, vlinkid, 'config/openconfig-ospfv2-ext:dead-interval')
                    if (vlinkarg == "hello-interval"):
                        return delete_ospf_router_vlink_config(api, vrf, areaidval, vlinkid, 'config/openconfig-ospfv2-ext:hello-interval')
                    if  (vlinkarg == "retransmit-interval"):
                        return delete_ospf_router_vlink_config(api, vrf, areaidval, vlinkid, 'config/openconfig-ospfv2-ext:retransmission-interval')
                    if (vlinkarg == "transmit-delay"):
                        return delete_ospf_router_vlink_config(api, vrf, areaidval, vlinkid, 'config/openconfig-ospfv2-ext:transmit-delay')
                    if (vlinkarg == "authentication"):
                        if (args[j] == "null"):
                            response = delete_ospf_router_vlink_config(api, vrf, areaidval, vlinkid, 'config/openconfig-ospfv2-ext:authentication-type')
                            if response.ok() == False : return response
                        elif (args[j] == "message-digest"):
                            response = delete_ospf_router_vlink_config(api, vrf, areaidval, vlinkid, 'config/openconfig-ospfv2-ext:authentication-type')
                            if response.ok() == False : return response
                            response = delete_ospf_router_vlink_config(api, vrf, areaidval, vlinkid, 'config/openconfig-ospfv2-ext:authentication-key-id')
                            if response.ok() == False : return response
                            response = delete_ospf_router_vlink_config(api, vrf, areaidval, vlinkid, 'config/openconfig-ospfv2-ext:authentication-md5-key')
                            if response.ok() == False : return response
                    if (vlinkarg == "authentication-key"):
                        response = delete_ospf_router_vlink_config(api, vrf, areaidval, vlinkid, 'config/openconfig-ospfv2-ext:authentication-key')
                        if response.ok() == False : return response
                    j = j + 1

                return response
            i = i + 1

    #-------- Ospf router network comamnds
    elif func == 'patch_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_networks_network_config':
        vrf = args[0]
        areaidval = area_to_dotted(args[1])

        body = { "config": { "address-prefix": args[2] }}
        return patch_ospf_router_network_config(api, vrf, areaidval, args[2], body)

    elif func == 'delete_openconfig_ospfv2_ext_network_instances_network_instance_protocols_protocol_ospfv2_areas_area_networks_network':
        vrf = args[0]
        areaidval = area_to_dotted(args[1])
        return delete_ospf_router_network_config(api, vrf, areaidval, args[2])

    #-------- Ospf interface comamnds
    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_vrf' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        cfg_body = { "config" : {"vrf": args[1]} }
        return patch_ospf_interface_config(api, if_name, if_address, cfg_body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_vrf' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        return delete_ospf_interface_config(api, if_name, if_address, 'config/vrf')

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_area_id' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        area_id = int(args[1]) if args[1].isdigit() else args[1]
        cfg_body = { "config" : {"area-id": area_id}}
        return patch_ospf_interface_config(api, if_name, if_address, cfg_body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_area_id' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        return delete_ospf_interface_config(api, if_name, if_address, 'config/area-id')

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_type' :
        if_name = args[0]
        if_address = "0.0.0.0"
        auth_type = "TEXT"
        auth_type_map = { "null" : "NONE", "message-digest" : "MD5HMAC" }

        if len(args) == 2 :
           if args[1] in auth_type_map.keys() :
               auth_type = auth_type_map[args[1]]
           else :
               if_address = args[1] if (args[1] != "") else "0.0.0.0"
        elif len(args) >= 3 :
           if args[1] in auth_type_map.keys() :
               auth_type = auth_type_map[args[1]]
           if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"

        cfg_body = { "config" : {"authentication-type" : auth_type}}
        return patch_ospf_interface_config(api, if_name, if_address, cfg_body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_type' :
        if_name = args[0]
        if_address = "0.0.0.0"
        auth_type_map = { "null" : "NONE", "message-digest" : "MD5HMAC" }

        if len(args) == 2 :
           if  args[1] not in auth_type_map.keys() :
               if_address = args[1] if (args[1] != "") else "0.0.0.0"
        elif len(args) >= 3 :
           if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"

        return delete_ospf_interface_config(api, if_name, if_address, 'config/authentication-type')

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_key' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        cfg_body = { "config" : {"authentication-key": args[1]}}
        return patch_ospf_interface_config(api, if_name, if_address, cfg_body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_key' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        return delete_ospf_interface_config(api, if_name, if_address, 'config/authentication-key')

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_key_id' :
        if_name = args[0]
        if_address = args[3] if (len(args) >= 4 and args[3] != "") else "0.0.0.0"
        cfg_body = { "config" : { "authentication-key-id": int(args[1]), "authentication-md5-key": args[2]} }
        return patch_ospf_interface_config(api, if_name, if_address, cfg_body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_key_id' :
        if_name = args[0]
        if_address = args[3] if (len(args) >= 4 and args[3] != "") else "0.0.0.0"
        response = delete_ospf_interface_config(api, if_name, if_address, 'config/authentication-key-id')
        if response.ok() == False : return response
        return delete_ospf_interface_config(api, if_name, if_address, 'config/authentication-md5-key')

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_md5_key' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        cfg_body = { "config" : {"authentication-md5-key": args[1]} }
        return patch_ospf_interface_config(api, if_name, if_address, cfg_body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_authentication_md5_key' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        return delete_ospf_interface_config(api, if_name, if_address, 'config/authentication-md5-key')

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_bfd' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        cfg_body = { "config" : {"bfd-enable": True }}
        return patch_ospf_interface_config(api, if_name, if_address, cfg_body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_bfd' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        return delete_ospf_interface_config(api, if_name, if_address, 'config/bfd-enable')

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_cost' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        cfg_body = { "config" : {"metric": int(args[1])} }
        return patch_ospf_interface_config(api, if_name, if_address, cfg_body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_cost' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        return delete_ospf_interface_config(api, if_name, if_address, 'config/metric')

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_mtu_ignore' :
        if_name = args[0]
        if_address = args[1] if (len(args) >= 2 and args[1] != "") else "0.0.0.0"
        cfg_body = { "config" : {"mtu-ignore": True} }
        return patch_ospf_interface_config(api, if_name, if_address, cfg_body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_mtu_ignore' :
        if_name = args[0]
        if_address = args[1] if (len(args) >= 2 and args[1] != "") else "0.0.0.0"
        return delete_ospf_interface_config(api, if_name, if_address, 'config/mtu-ignore')

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_network_type' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        network_type = "POINT_TO_POINT_NETWORK" if args[1] == "point-to-point" else "BROADCAST_NETWORK"
        cfg_body = { "config" : {"network-type": network_type} }
        return patch_ospf_interface_config(api, if_name, if_address, cfg_body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_network_type' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        return delete_ospf_interface_config(api, if_name, if_address, 'config/network-type')

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_priority' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        cfg_body = { "config" : {"priority": int(args[1])} }
        return patch_ospf_interface_config(api, if_name, if_address, cfg_body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_priority' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        return delete_ospf_interface_config(api, if_name, if_address, 'config/priority')

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_dead_interval' :
        if_name = args[0]
        if_address = args[3] if (len(args) >= 4 and args[3] != "") else "0.0.0.0"

        deadtype = args[1]
        if deadtype != "" and deadtype == 'deadinterval' :
            cfg_body = { "config" : { "dead-interval": int(args[2]), "dead-interval-minimal": False }}
            return patch_ospf_interface_config(api, if_name, if_address, cfg_body)
        elif deadtype != "" and deadtype == 'minimal' :
            cfg_body = { "config" : { "hello-multiplier": int(args[2]), "dead-interval-minimal": True }}
            return patch_ospf_interface_config(api, if_name, if_address, cfg_body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_dead_interval' :
        if_name = args[0]
        if_address = "0.0.0.0"
        deadtype = ''
        if len(args) >= 2 and args[1] != '' : deadtype = args[1]
        #print("System arguments - args {} deadtype {}".format(args, deadtype))
        if deadtype == 'minimal' :
            if len(args) >= 3 and args[2] != '' : if_address = args[2]
            response = delete_ospf_interface_config(api, if_name, if_address, 'config/dead-interval-minimal')
            if response.ok() == False : return response
            response = delete_ospf_interface_config(api, if_name, if_address, 'config/dead-interval')
            if response.ok() == False : return response
            return delete_ospf_interface_config(api, if_name, if_address, 'config/hello-multiplier')
        else :
            if deadtype == 'ip-address' :
                if len(args) >= 3 and args[2] != '' : if_address = args[2]
            else :
                if len(args) >= 2 and args[1] != '' : if_address = args[1]
            response = delete_ospf_interface_config(api, if_name, if_address, 'config/dead-interval-minimal')
            if response.ok() == False : return response
            response = delete_ospf_interface_config(api, if_name, if_address, 'config/hello-multiplier')
            if response.ok() == False : return response
            return delete_ospf_interface_config(api, if_name, if_address, 'config/dead-interval')

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_hello_multiplier' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        cfg_body = { "config" : {"hello-multiplier": int(args[1])} }
        return patch_ospf_interface_config(api, if_name, if_address, cfg_body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_hello_multiplier' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        return delete_ospf_interface_config(api, if_name, if_address, 'config/hello-multiplier')

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_hello_interval' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        cfg_body = { "config" : {"hello-interval": int(args[1])} }
        return patch_ospf_interface_config(api, if_name, if_address, cfg_body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_hello_interval' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        return delete_ospf_interface_config(api, if_name, if_address, 'config/hello-interval')

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_retransmit_interval' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        cfg_body = { "config" : {"retransmission-interval": int(args[1])} }
        return patch_ospf_interface_config(api, if_name, if_address, cfg_body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_retransmit_interval' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        return delete_ospf_interface_config(api, if_name, if_address, 'config/retransmission-interval')

    elif func == 'patch_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_transmit_delay' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        cfg_body = { "config" : {"transmit-delay": int(args[1])} }
        return patch_ospf_interface_config(api, if_name, if_address, cfg_body)

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_config_transmit_delay' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        return delete_ospf_interface_config(api, if_name, if_address, 'config/transmit-delay')

    elif func == 'delete_openconfig_interfaces_interface_subinterfaces_subinterface_ip_ospf_unconfig' :
        if_name = args[0]
        if_address = args[2] if (len(args) >= 3 and args[2] != "") else "0.0.0.0"
        return delete_ospf_interface_config(api, if_name, '', '')

    else:
        body = {}

    return api.cli_not_implemented(func)



def run(func, args):
    response = invoke_api(func, args)

    if response.ok():
	if response.content is not None:
	    print("Failed")
    else:
        print(response.error_message())

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    #print("System arguments - {}".format(sys.argv))

    run(func, sys.argv[2:])
