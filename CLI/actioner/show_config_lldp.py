#!/usr/bin/python

###########################################################################
#
# Copyright 2020 Broadcom. The term Broadcom refers to Broadcom Inc. and/or
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

def show_lldp_mode_config(render_tables):
    cmd_str = ''
    if 'sonic-lldp:sonic-lldp/LLDP/LLDP_LIST' in render_tables:
        lldp_global = render_tables['sonic-lldp:sonic-lldp/LLDP/LLDP_LIST']
        if 'mode' in lldp_global[0]:
            if lldp_global[0]['mode'] == "RECEIVE":
                cmd_str = "lldp receive"
            elif lldp_global[0]['mode'] == "TRANSMIT":
                cmd_str = "lldp transmit"

    return 'CB_SUCCESS', cmd_str

def show_lldp_intf_mode_config(render_tables):
    cmd_str = ''
    if 'name' in render_tables:
        ifname_key = render_tables['name']
        if 'sonic-lldp:sonic-lldp/LLDP_PORT/LLDP_PORT_LIST' in render_tables:
            for lldp_port in render_tables['sonic-lldp:sonic-lldp/LLDP_PORT/LLDP_PORT_LIST']:
                if 'ifname' in lldp_port:
                    if ifname_key == lldp_port['ifname']:
                        if 'mode' in lldp_port:
                            if lldp_port['mode'] == "RECEIVE":
                                cmd_str = "lldp receive"
                            elif lldp_port['mode'] == "TRANSMIT":
                                cmd_str = "lldp transmit"

    return 'CB_SUCCESS', cmd_str

def show_lldp_tlv_select_config(render_tables):
    cmd_str = [] 
    if 'sonic-lldp:sonic-lldp/LLDP/LLDP_LIST' in render_tables:
        lldp_global = render_tables['sonic-lldp:sonic-lldp/LLDP/LLDP_LIST']
        if 'supp_mgmt_address_tlv' in lldp_global[0]:
            if lldp_global[0]['supp_mgmt_address_tlv'] == True:
                cmd_str.append('no lldp tlv-select management-address')

        if 'supp_system_capabilities_tlv' in lldp_global[0]:
            if lldp_global[0]['supp_system_capabilities_tlv'] == True:
                cmd_str.append('no lldp tlv-select system-capabilities')

    return 'CB_SUCCESS', ';'.join(cmd_str)
