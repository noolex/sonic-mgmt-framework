################################################################################
#                                                                              #
#  Copyright 2020 Broadcom. The term Broadcom refers to Broadcom Inc. and/or   #
#  its subsidiaries.                                                           #
#                                                                              #
#  Licensed under the Apache License, Version 2.0 (the "License");             #
#  you may not use this file except in compliance with the License.            #
#  You may obtain a copy of the License at                                     #
#                                                                              #
#     http://www.apache.org/licenses/LICENSE-2.0                               #
#                                                                              #
#  Unless required by applicable law or agreed to in writing, software         #
#  distributed under the License is distributed on an "AS IS" BASIS,           #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    #
#  See the License for the specific language governing permissions and         #
#  limitations under the License.                                              #
#                                                                              #
################################################################################

from show_config_if_cmd import show_render_if_cmd

# show_ldap_server_src_intf renders running config for 'ldap-server source-interface'
def show_ldap_server_src_intf(render_tables):
    entry = get_ldap_entry(render_tables, 'global')
    cmd = show_render_if_cmd(entry, 'src_intf', 'ldap-server source-interface ', '')
    return 'CB_SUCCESS', cmd

# get_ldap_entry returns LDAP_LIST entry with given ldap_type.
# Returns an empty dict if no matching entry found.
def get_ldap_entry(data, ldap_type):
    for entry in data.get('sonic-system-ldap:sonic-system-ldap/LDAP/LDAP_LIST', []):
        if entry.get('ldap_type') == ldap_type:
            return entry 
    return {}

# To show the running configuration of the ldap-server map
def show_ldap_map_config(render_tables):

    cmd_str = ''
    cmd_prfx = 'ldap-server map '
    if 'sonic-system-ldap:sonic-system-ldap/LDAP_MAP/LDAP_MAP_LIST' in render_tables:
        for ldap_map_inst in render_tables['sonic-system-ldap:sonic-system-ldap/LDAP_MAP/LDAP_MAP_LIST']:
            mapName = ""
            if ldap_map_inst['name'] == 'ATTRIBUTE':
                mapName = 'attribute '
            elif ldap_map_inst['name'] == 'OBJECTCLASS':
                mapName = 'objectclass '
            elif ldap_map_inst['name'] == 'DEFAULT_ATTRIBUTE_VALUE':
                mapName = 'default-attribute-value ' 
            elif ldap_map_inst['name'] == 'OVERRIDE_ATTRIBUTE_VALUE':
                mapName = 'override-attribute-value '
            cmd_str += cmd_prfx + mapName + ldap_map_inst['from'] + ' to ' + ldap_map_inst['to'] + ';'                
            
    return 'CB_SUCCESS', cmd_str
