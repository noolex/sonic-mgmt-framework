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

def show_config_spanning_tree_global_max_age(render_tables):
    cmd_str = ''
    if 'sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST' not in render_tables:
        return 'CB_SUCCESS', cmd_str

    db_entry = render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST'][0]

    if db_entry['max_age'] != 20:
        cmd_str = 'spanning-tree max-age ' + str(db_entry['max_age'])

    return 'CB_SUCCESS', cmd_str


def show_config_spanning_tree_global_hello_time(render_tables):
    cmd_str = ''
    if 'sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST' not in render_tables:
        return 'CB_SUCCESS', cmd_str

    db_entry = render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST'][0]

    if db_entry['hello_time'] != 2:
        cmd_str = 'spanning-tree hello-time ' + str(db_entry['hello_time'])

    return 'CB_SUCCESS', cmd_str


def show_config_spanning_tree_global_priority(render_tables):
    cmd_str = ''
    if 'sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST' not in render_tables:
        return 'CB_SUCCESS', cmd_str

    db_entry = render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST'][0]

    if db_entry['priority'] != 32768:
        cmd_str = 'spanning-tree priority ' + str(db_entry['priority'])

    return 'CB_SUCCESS', cmd_str



def show_config_spanning_tree_global_fwd_delay(render_tables):
    cmd_str = ''
    if 'sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST' not in render_tables:
        return 'CB_SUCCESS', cmd_str

    db_entry = render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST'][0]

    if db_entry['forward_delay'] != 15:
        cmd_str = 'spanning-tree forward-time ' + str(db_entry['forward_delay'])

    return 'CB_SUCCESS', cmd_str


def show_config_spanning_tree_global_root_guard_time(render_tables):
    cmd_str = ''
    if 'sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST' not in render_tables:
        return 'CB_SUCCESS', cmd_str

    db_entry = render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST'][0]

    if 'rootguard_timeout' in db_entry.keys() and db_entry['rootguard_timeout'] != 30:
        cmd_str = 'spanning-tree guard root timeout ' + str(db_entry['rootguard_timeout'])

    return 'CB_SUCCESS', cmd_str


def show_config_spanning_tree_vlan(render_tables):
    cmd_str = ''
    cmd_sep = ';'

    if 'sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST' not in render_tables:
        return 'CB_SUCCESS', cmd_str

    db_entry = render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST'][0]
    global_fwd_delay = db_entry['forward_delay']
    global_hello_time = db_entry['hello_time']
    global_max_age = db_entry['max_age']
    global_br_prio = db_entry['priority']



    if 'sonic-spanning-tree:sonic-spanning-tree/STP_VLAN/STP_VLAN_LIST' in render_tables:
        for db_entry in render_tables['sonic-spanning-tree:sonic-spanning-tree/STP_VLAN/STP_VLAN_LIST']:
            cmd_prfx = cmd_sep + "spanning-tree vlan " + str(db_entry['vlanid']) + ' '
            if db_entry["forward_delay"] != global_fwd_delay:
                cmd_str += cmd_prfx + 'forward-time ' + str(db_entry['forward_delay'])
            if db_entry["hello_time"] != global_hello_time:
                cmd_str += cmd_prfx + 'hello-time ' + str(db_entry['hello_time'])
            if db_entry["max_age"] != global_max_age:
                cmd_str += cmd_prfx + 'max-age ' + str(db_entry['max_age'])
            if db_entry["priority"] != global_br_prio:
                cmd_str += cmd_prfx + 'priority ' + str(db_entry['priority'])

    return 'CB_SUCCESS', cmd_str


def show_config_no_spanning_tree_vlan(render_tables):
    cmd_str = ''
    if 'sonic-spanning-tree:sonic-spanning-tree/STP_VLAN/STP_VLAN_LIST' in render_tables:
        for db_entry in render_tables['sonic-spanning-tree:sonic-spanning-tree/STP_VLAN/STP_VLAN_LIST']:
            if not db_entry["enabled"]:
                if cmd_str:
                    cmd_str = cmd_str + ';' + "no spanning-tree vlan " + str(db_entry['vlanid'])
                else:
                    cmd_str = "no spanning-tree vlan " + str(db_entry['vlanid'])

    return 'CB_SUCCESS', cmd_str



def show_config_spanning_tree_intf_vlan(render_tables):
    cmd_str = ''

    if 'sonic-spanning-tree:sonic-spanning-tree/STP_VLAN_PORT/STP_VLAN_PORT_LIST' in render_tables \
            and 'sonic-spanning-tree:sonic-spanning-tree/STP_PORT/STP_PORT_LIST' in render_tables:
        for db_entry in render_tables['sonic-spanning-tree:sonic-spanning-tree/STP_VLAN_PORT/STP_VLAN_PORT_LIST']:
            if render_tables['name'] != db_entry['ifname']:
                continue

            vlan_name = db_entry['vlan-name']
            vlanid = vlan_name[len('Vlan'):]
            cmd_prfx = 'spanning-tree vlan ' + vlanid + ' '
            if 'path_cost' in db_entry.keys():
                cmd_str = cmd_str + ';' + cmd_prfx + 'cost ' + str(db_entry['path_cost'])
            if 'priority' in db_entry.keys():
                cmd_str = cmd_str + ';' + cmd_prfx + 'port-priority ' + str(db_entry['priority'])

    return 'CB_SUCCESS', cmd_str


def show_config_spanning_tree_intf(render_tables):
    cmd_str = ''

    cmd_prfx = 'spanning-tree '
    if 'sonic-spanning-tree:sonic-spanning-tree/STP_PORT/STP_PORT_LIST' in render_tables:
        for db_entry in render_tables['sonic-spanning-tree:sonic-spanning-tree/STP_PORT/STP_PORT_LIST']:
            if render_tables['name'] != db_entry['ifname']:
                continue

            #print all
            if 'bpdu_filter' in db_entry:
                if db_entry['bpdu_filter'] == 'enable':
                    cmd_str = cmd_str + ';' + cmd_prfx + 'bpdufilter enable'
                elif db_entry['bpdu_filter'] == 'disable':
                    cmd_str = cmd_str + ';' + cmd_prfx + 'bpdufilter disable'
            if 'bpdu_guard' and 'bpdu_guard_do_disable' in db_entry:
                if db_entry['bpdu_guard_do_disable']:
                    cmd_str = cmd_str + ';' + cmd_prfx + 'bpduguard port-shutdown'
                elif db_entry['bpdu_guard']:
                    cmd_str = cmd_str + ';' + cmd_prfx + 'bpduguard'

            if 'path_cost' in db_entry:
                cmd_str = cmd_str + ';' + cmd_prfx + 'cost ' + str(db_entry['path_cost'])

            if 'link_type' in db_entry and db_entry['link_type'] != 'auto':
                cmd_str = cmd_str + ';' + cmd_prfx + 'link-type ' + db_entry['link_type']

            if 'priority' in db_entry:
                cmd_str = cmd_str + ';' + cmd_prfx + 'port-priority ' + str(db_entry['priority'])

            if 'edge_port' in db_entry and db_entry['edge_port']:
                cmd_str = cmd_str + ';' + cmd_prfx + 'port type edge'

            if 'uplink_fast' in db_entry and db_entry['uplink_fast']:
                cmd_str = cmd_str + ';' + cmd_prfx + 'uplinkfast'

            if 'root_guard' in db_entry and db_entry['root_guard']:
                cmd_str = cmd_str + ';' + cmd_prfx + 'guard root'


    return 'CB_SUCCESS', cmd_str



