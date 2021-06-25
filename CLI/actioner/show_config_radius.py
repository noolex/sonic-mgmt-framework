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

# show_radius_global_key renders running config for 'radius-server key'
def show_radius_global_key(render_tables):
    cmd = ''
    entry = get_radius_entry(render_tables)
    if ('passkey' in entry) and entry['passkey']:
        cmd = 'radius-server key ' + entry.get('passkey') + ' encrypted'
    return 'CB_SUCCESS', cmd

# show_radius_statistics_config renders running config for 'radius-server statistics'
def show_radius_statistics_config(render_tables):
    cmd = ''
    entry = get_radius_entry(render_tables)
    if ( 'statistics' in entry ) and entry['statistics']:
        cmd = 'radius-server statistics enable'
    return 'CB_SUCCESS', cmd

# get_radius_entry returns global RADIUS_LIST entry
# Returns an empty dict if no matching entry found.
def get_radius_entry(data):
    for entry in data.get('sonic-system-radius:sonic-system-radius/RADIUS/RADIUS_LIST', []):
        if entry.get('global_key') == 'global':
            return entry 
    return {}

# To show the running configuration of the 'radius-server host'
def show_radius_host_config(render_tables):
    cmd = ''
    for entry in render_tables.get('sonic-system-radius:sonic-system-radius/RADIUS_SERVER/RADIUS_SERVER_LIST', []):
        if cmd != '':
            cmd += ';'
        cmd += 'radius-server host ' + entry.get('ipaddress')
        auth_port = entry.get('auth_port')
        if auth_port != None:
            cmd += ' auth-port ' + str(auth_port)
        if entry.get('timeout') != None:
            cmd += ' timeout ' + str(entry.get('timeout'))
        if entry.get('retransmit') != None:
            cmd += ' retransmit ' + str(entry.get('retransmit'))
        if entry.get('passkey') != None:
            cmd += ' key ' + entry.get('passkey')
            cmd += ' encrypted '
        if entry.get('auth_type') != None:
            cmd += ' auth-type ' + entry.get('auth_type')
        priority = entry.get('priority')
        if priority != None:
            cmd += ' priority ' + str(priority)
        if entry.get('vrf') != None:
            cmd += ' vrf ' + entry.get('vrf')
        src_intf = entry.get('src_intf')
        if src_intf != None:
            cmd += ' source-interface ' + \
                   show_render_if_cmd( entry, 'src_intf', '', None)

    return 'CB_SUCCESS', cmd
