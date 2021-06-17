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
from show_config_if_cmd import show_render_if_cmd

# show_tacacs_global_key renders running config for 'tacacs-server key'
def show_tacacs_global_key(render_tables):
    cmd = ''
    entry = get_tacacs_entry(render_tables)
    for key, value in entry.items():
        if ('passkey' == key):
            cmd = 'tacacs-server key ' + entry.get('passkey') + ' encrypted'
    return 'CB_SUCCESS', cmd

# get_tacacs_entry returns global TACPLUS entry
# Returns an empty dict if no matching entry found.
def get_tacacs_entry(data):
    for entry in data.get('sonic-system-tacacs:sonic-system-tacacs/TACPLUS/TACPLUS_LIST', []):
        if entry.get('type') == 'global':
            return entry
    return {}

# To show the running configuration of the 'tacacs-server host'
def show_tacacs_host_config(render_tables):
    cmd = ''
    for entry in render_tables.get('sonic-system-tacacs:sonic-system-tacacs/TACPLUS_SERVER/TACPLUS_SERVER_LIST', []):
        if cmd != '':
            cmd += ';'
        cmd += 'tacacs-server host ' + entry.get('ipaddress')
        auth_port = entry.get('tcp_port')
        if auth_port != None:
            cmd += ' port ' + str(auth_port)
        if entry.get('timeout') != None:
            cmd += ' timeout ' + str(entry.get('timeout'))
        if entry.get('passkey') != None:
            cmd += ' key ' + entry.get('passkey')
            cmd += ' encrypted '
        if entry.get('auth_type') != None:
            cmd += ' type ' + entry.get('auth_type')
        priority = entry.get('priority')
        if priority != None:
            cmd += ' priority ' + str(priority)
        if entry.get('vrf') != None:
            cmd += ' vrf ' + entry.get('vrf')

    return 'CB_SUCCESS', cmd
