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
 
import syslog as log
import sonic_cli_stp as cli_stp

g_err_transaction_fail = '%Error: Transaction Failure'

def ret_err(console_err_msg, syslog_msg):
    if len(syslog_msg) != 0:
        log.syslog(log.LOG_ERR, str(syslog_msg))
    return 'CB_SUCCESS', console_err_msg


def show_config_spanning_tree_global_max_age(render_tables):
    cmd_str = ''
    if 'sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST' not in render_tables:
        return 'CB_SUCCESS', cmd_str

    if len(render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST']) == 0:
        return 'CB_SUCCESS', cmd_str

    db_entry = render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST'][0]

    if 'max_age' in db_entry.keys() and db_entry['max_age'] != 20:
        cmd_str = 'spanning-tree max-age ' + str(db_entry['max_age'])

    return 'CB_SUCCESS', cmd_str

def show_config_spanning_tree_global_loop_guard(render_tables):
    cmd_str = ''
    if 'sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST' not in render_tables:
        return 'CB_SUCCESS', cmd_str

    if len(render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST']) == 0:
        return 'CB_SUCCESS', cmd_str

    db_entry = render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST'][0]

    if 'loop_guard' in db_entry.keys() and db_entry['loop_guard'] != False:
        cmd_str = 'spanning-tree loopguard default'

    return 'CB_SUCCESS', cmd_str

def show_config_spanning_tree_global_portfast(render_tables):
    cmd_str = ''
    if 'sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST' not in render_tables:
        return 'CB_SUCCESS', cmd_str

    if len(render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST']) == 0:
        return 'CB_SUCCESS', cmd_str

    db_entry = render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST'][0]

    if 'portfast' in db_entry.keys() and db_entry['portfast'] != False:
        cmd_str = 'spanning-tree portfast default'

    return 'CB_SUCCESS', cmd_str

def show_config_spanning_tree_global_hello_time(render_tables):
    cmd_str = ''
    if 'sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST' not in render_tables:
        return 'CB_SUCCESS', cmd_str

    if len(render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST']) == 0:
        return 'CB_SUCCESS', cmd_str

    db_entry = render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST'][0]

    if 'hello_time' in db_entry.keys() and db_entry['hello_time'] != 2:
        cmd_str = 'spanning-tree hello-time ' + str(db_entry['hello_time'])

    return 'CB_SUCCESS', cmd_str


def show_config_spanning_tree_global_priority(render_tables):
    cmd_str = ''
    if 'sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST' not in render_tables:
        return 'CB_SUCCESS', cmd_str

    if len(render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST']) == 0:
        return 'CB_SUCCESS', cmd_str

    db_entry = render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST'][0]

    if 'priority' in db_entry.keys() and db_entry['priority'] != 32768:
        cmd_str = 'spanning-tree priority ' + str(db_entry['priority'])

    return 'CB_SUCCESS', cmd_str



def show_config_spanning_tree_global_fwd_delay(render_tables):
    cmd_str = ''
    if 'sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST' not in render_tables:
        return 'CB_SUCCESS', cmd_str

    if len(render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST']) == 0:
        return 'CB_SUCCESS', cmd_str

    db_entry = render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST'][0]

    if 'forward_delay' in db_entry.keys() and db_entry['forward_delay'] != 15:
        cmd_str = 'spanning-tree forward-time ' + str(db_entry['forward_delay'])

    return 'CB_SUCCESS', cmd_str


def show_config_spanning_tree_global_root_guard_time(render_tables):
    cmd_str = ''
    if 'sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST' not in render_tables:
        return 'CB_SUCCESS', cmd_str

    if len(render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST']) == 0:
        return 'CB_SUCCESS', cmd_str

    db_entry = render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST'][0]

    if 'rootguard_timeout' in db_entry.keys() and db_entry['rootguard_timeout'] != 30:
        cmd_str = 'spanning-tree guard root timeout ' + str(db_entry['rootguard_timeout'])

    return 'CB_SUCCESS', cmd_str


def show_config_spanning_tree_vlan(render_tables):
    cmd_str = ''

    if 'sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST' not in render_tables:
        return 'CB_SUCCESS', cmd_str

    if len(render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST']) == 0:
        return 'CB_SUCCESS', cmd_str

    db_entry = render_tables['sonic-spanning-tree:sonic-spanning-tree/STP/STP_LIST'][0]
    
    missing_fields = [field for field in ['forward_delay', 'hello_time', 'max_age', 'priority'] if field not in db_entry.keys()]
    if len(missing_fields) != 0:
        return ret_err(g_err_transaction_fail, 'keys : {} not found in STP-GLOBAL'.format(missing_fields))
        
    g_stp = {}
    g_stp['forwarding-delay'] = db_entry['forward_delay']
    g_stp['hello-time'] = db_entry['hello_time']
    g_stp['max-age'] = db_entry['max_age']
    g_stp['bridge-priority'] = db_entry['priority']

    vlist = []
    if 'sonic-spanning-tree:sonic-spanning-tree/STP_VLAN/STP_VLAN_LIST' in render_tables:
        for db_entry in render_tables['sonic-spanning-tree:sonic-spanning-tree/STP_VLAN/STP_VLAN_LIST']:
            if 'name' not in db_entry.keys():
                continue;

            vdata = {}
            vid = int(db_entry['name'][len('Vlan'):])
            vdata['vlan-id'] = vid
            vdata['config'] = {}
            if 'forward_delay' in db_entry:
                vdata['config']['forwarding-delay'] = db_entry['forward_delay']
            if 'hello_time' in db_entry:
                vdata['config']['hello-time'] = db_entry['hello_time']
            if 'max_age' in db_entry:
                vdata['config']['max-age'] = db_entry['max_age']
            if 'priority' in db_entry:
                vdata['config']['bridge-priority'] = db_entry['priority']
            vlist.append(vdata)

    cli_stp.show_run_config_vlan(vlist, g_stp)
    return 'CB_SUCCESS', cmd_str


def show_config_no_spanning_tree_vlan(render_tables):
    cmd_str = ''
    disabled_vlans = []
    if 'sonic-spanning-tree:sonic-spanning-tree/STP_VLAN/STP_VLAN_LIST' in render_tables:
        for db_entry in render_tables['sonic-spanning-tree:sonic-spanning-tree/STP_VLAN/STP_VLAN_LIST']:
            if 'enabled' in db_entry.keys() and db_entry["enabled"] == False:
                disabled_vlans.append(db_entry['name'][4:])

    if len(disabled_vlans) != 0:
        disabled_vlans = [int(vlanid) for vlanid in disabled_vlans]
        disabled_vlans = sorted(disabled_vlans)

        cmd_str = "no spanning-tree vlan " + cli_stp.convert_list_to_range_groups(disabled_vlans)

    return 'CB_SUCCESS', cmd_str


def show_config_spanning_tree_intf_vlan(render_tables):
    cmd_str = ''
    cmd_list = []
    vpdata = {'cost':{}, 'prio':{}}

    if 'name' not in render_tables.keys():
        return ret_err(g_err_transaction_fail, 'key:name not found in render_tables')

    if 'sonic-spanning-tree:sonic-spanning-tree/STP_VLAN_PORT/STP_VLAN_PORT_LIST' in render_tables \
            and 'sonic-spanning-tree:sonic-spanning-tree/STP_PORT/STP_PORT_LIST' in render_tables:

        for db_entry in render_tables['sonic-spanning-tree:sonic-spanning-tree/STP_VLAN_PORT/STP_VLAN_PORT_LIST']:
            if 'ifname' not in db_entry.keys():
                return ret_err(g_err_transaction_fail, 'key:ifname not found in STP_VLAN_PORT_DB, render_table[name] = {}'.format(render_tables['name']))

            if render_tables['name'] != db_entry['ifname']:
                continue

            if 'vlan-name' not in db_entry.keys():
                return ret_err(g_err_transaction_fail, 'key:vlan-name not found in STP_VLAN_PORT_DB - {}'.format(db_entry['ifname']))

            vlan_name = db_entry['vlan-name']
            vlanid = vlan_name[len('Vlan'):]
            if 'path_cost' in db_entry.keys():
                key = int(db_entry['path_cost'])
                if key in vpdata['cost'].keys():
                    vpdata['cost'][key].append(int(vlanid))
                else:
                    vpdata['cost'][key] = [int(vlanid)]
            if 'priority' in db_entry.keys():
                key = int(db_entry['priority'])
                if key in vpdata['prio'].keys():
                    vpdata['prio'][key].append(int(vlanid))
                else:
                    vpdata['prio'][key] = [int(vlanid)]

    for cost in sorted(vpdata['cost'].keys()):
        vrange = cli_stp.convert_list_to_range_groups(vpdata['cost'][cost])
        cmd_list.append('spanning-tree vlan ' + vrange + ' cost ' + str(cost))
    for prio in sorted(vpdata['prio'].keys()):
        vrange = cli_stp.convert_list_to_range_groups(vpdata['prio'][prio])
        cmd_list.append('spanning-tree vlan ' + vrange + ' port-priority ' + str(prio))
    
    if cmd_list:
        cmd_str = ';'.join(cmd_list)
    return 'CB_SUCCESS', cmd_str


def show_config_spanning_tree_intf(render_tables):
    cmd_str = ''
    cmd_list = []

    if 'name' not in render_tables.keys():
        return ret_err(g_err_transaction_fail, 'key:name not found in render_tables')

    cmd_prfx = 'spanning-tree '
    if 'sonic-spanning-tree:sonic-spanning-tree/STP_PORT/STP_PORT_LIST' in render_tables:
        for db_entry in render_tables['sonic-spanning-tree:sonic-spanning-tree/STP_PORT/STP_PORT_LIST']:

            if 'ifname' not in db_entry.keys():
                return ret_err(g_err_transaction_fail, 'key:ifname not found in STP_PORT_DB, render_table[name] = {}'.format(render_tables['name']))

            if render_tables['name'] != db_entry['ifname']:
                continue

            #print all
            if 'bpdu_filter' in db_entry:
                if db_entry['bpdu_filter'] == 'enable':
                    cmd_list.append(cmd_prfx + 'bpdufilter enable')
                elif db_entry['bpdu_filter'] == 'disable':
                    cmd_list.append(cmd_prfx + 'bpdufilter disable')
            if 'bpdu_guard' and 'bpdu_guard_do_disable' in db_entry:
                if db_entry['bpdu_guard_do_disable']:
                    cmd_list.append(cmd_prfx + 'bpduguard port-shutdown')
                elif db_entry['bpdu_guard']:
                    cmd_list.append(cmd_prfx + 'bpduguard')

            if 'path_cost' in db_entry:
                cmd_list.append(cmd_prfx + 'cost ' + str(db_entry['path_cost']))

            if 'link_type' in db_entry and db_entry['link_type'] != 'auto':
                cmd_list.append(cmd_prfx + 'link-type ' + db_entry['link_type'])

            if 'priority' in db_entry:
                cmd_list.append(cmd_prfx + 'port-priority ' + str(db_entry['priority']))

            if 'edge_port' in db_entry and db_entry['edge_port']:
                cmd_list.append(cmd_prfx + 'port type edge')

            if 'uplink_fast' in db_entry and db_entry['uplink_fast']:
                cmd_list.append(cmd_prfx + 'uplinkfast')

    if cmd_list:
        cmd_str = ';'.join(cmd_list)
    return 'CB_SUCCESS', cmd_str

def show_config_spanning_tree_intf_guard(render_tables):
    cmd_str = ''
    cmd_list = []

    if 'name' not in render_tables.keys():
        return ret_err(g_err_transaction_fail, 'key:name not found in render_tables')

    cmd_prfx = 'spanning-tree '
    if 'sonic-spanning-tree:sonic-spanning-tree/STP_PORT/STP_PORT_LIST' in render_tables:
        for db_entry in render_tables['sonic-spanning-tree:sonic-spanning-tree/STP_PORT/STP_PORT_LIST']:

            if 'ifname' not in db_entry.keys():
                return ret_err(g_err_transaction_fail, 'key:ifname not found in STP_PORT_DB, render_table[name] = {}'.format(render_tables['name']))

            if render_tables['name'] != db_entry['ifname']:
                continue

            if 'root_guard' in db_entry and db_entry['root_guard']:
                cmd_list.append(cmd_prfx + 'guard root')
            elif 'loop_guard' in db_entry and db_entry['loop_guard'] == 'true':
                cmd_list.append(cmd_prfx + 'guard loop')
            elif 'loop_guard' in db_entry and db_entry['loop_guard'] == 'none':
                cmd_list.append(cmd_prfx + 'guard none')

    if cmd_list:
        cmd_str = ';'.join(cmd_list)
    return 'CB_SUCCESS', cmd_str



