###########################################################################
#
# Copyright 2020 Dell, Inc.
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


def show_wred_policy (render_tables, color):
    cmd_str = ''
    wred_key = ''
    if 'wname' in render_tables:
       wred_key = render_tables['wname']

    if 'sonic-wred-profile:sonic-wred-profile/WRED_PROFILE/WRED_PROFILE_LIST' in render_tables:
        wred = render_tables['sonic-wred-profile:sonic-wred-profile/WRED_PROFILE/WRED_PROFILE_LIST']

        if 'name' in wred:
            if wred_key == wred['name']:
               if color == 'green' and 'wred_green_enable' in wred and 'green_min_threshold' in wred and 'green_max_threshold' in wred and 'green_drop_probability' in wred:
                   if wred['wred_green_enable'] == True:
                      g_min = int(wred['green_min_threshold'])/1024
                      g_max = int(wred['green_max_threshold'])/1024
                      cmd_str += ' green minimum-threshold ' + str(g_min) + ' maximum-threshold ' + str(g_max) +  ' drop-probability ' + wred['green_drop_probability'] + ';'
               if color == 'yellow' and 'wred_yellow_enable' in wred and 'yellow_min_threshold' in wred and 'yellow_max_threshold' in wred and 'yellow_drop_probability' in wred:
                   if wred['wred_yellow_enable'] == True:
                      y_min = int(wred['yellow_min_threshold'])/1024
                      y_max = int(wred['yellow_max_threshold'])/1024
                      cmd_str += ' yellow minimum-threshold ' + str(y_min) + ' maximum-threshold ' + str(y_max) +  ' drop-probability ' + wred['yellow_drop_probability'] + ';'
               if color == 'red' and 'wred_red_enable' in wred and 'red_min_threshold' in wred and 'red_max_threshold' in wred and 'red_drop_probability' in wred:
                   if wred['wred_red_enable'] == True:
                      r_min = int(wred['red_min_threshold'])/1024
                      r_max = int(wred['red_max_threshold'])/1024
                      cmd_str += ' red minimum-threshold ' + str(r_min) + ' maximum-threshold ' + str(r_max) +  ' drop-probability ' + wred['red_drop_probability'] + ';'

               if 'ecn' in wred:
                   cmd_str += ' ecn ' +  wred['ecn'].lstrip('ecn_') + ';'

    return 'CB_SUCCESS', cmd_str


def show_wred_policy_green(render_tables):
    return show_wred_policy(render_tables, 'green')

def show_wred_policy_yellow(render_tables):
    return show_wred_policy(render_tables, 'yellow')

def show_wred_policy_red(render_tables):
    return show_wred_policy(render_tables, 'red')


def convert_db_to_config_format(name, prefix):
    prefix = '[' + prefix + '|'
    name = name.rstrip(']')
    name = name.lstrip(prefix)
    return name


def show_queue_wred_policy(render_tables):
    cmd_str = ''
    ifkey = ''

    if 'name' in render_tables:
       ifkey = render_tables['name']
    if 'sonic-queue:sonic-queue/QUEUE/QUEUE_LIST' in render_tables:
        queue_inst = render_tables['sonic-queue:sonic-queue/QUEUE/QUEUE_LIST']

        for queue in queue_inst:
            if 'ifname' in queue and 'wred_profile' in queue:
                if ifkey == queue['ifname']:
                   wred = convert_db_to_config_format(queue['wred_profile'], 'WRED_PROFILE')
                   cmd_str += 'queue ' + queue['qindex'] + ' wred-policy ' + wred + ';'

    return 'CB_SUCCESS', cmd_str

map_type_name_to_abnf = {
    'dscp_to_tc_map'  : 'DSCP_TO_TC_MAP',
    'dot1p_to_tc_map' : 'DOT1P_TO_TC_MAP',
    'tc_to_queue_map' : 'TC_TO_QUEUE_MAP',
    'tc_to_pg_map'    : 'TC_TO_PRIORITY_GROUP_MAP',
    'tc_to_dscp_map'  : 'TC_TO_DSCP_MAP',
    'tc_to_dot1p_map' : 'TC_TO_DOT1P_MAP',
    'pfc_to_queue_map' : 'MAP_PFC_PRIORITY_TO_QUEUE'
}

map_type_name_to_cmd = {
    'dscp_to_tc_map'  : 'dscp-tc',
    'dot1p_to_tc_map' : 'dot1p-tc',
    'tc_to_queue_map' : 'tc-queue',
    'tc_to_pg_map'    : 'tc-pg',
    'tc_to_dscp_map'  : 'tc-dscp',
    'tc_to_dot1p_map' : 'tc-dot1p',
    'pfc_to_queue_map' : 'pfc-priority-queue'
}


def show_qos_int_maps(render_tables, map_type):
    cmd_str = ''
    ifkey = ''

    if 'name' in render_tables:
       ifkey = render_tables['name']

    if 'sonic-port-qos-map:sonic-port-qos-map/PORT_QOS_MAP/PORT_QOS_MAP_LIST' in render_tables:
        port_qos_map_list = render_tables['sonic-port-qos-map:sonic-port-qos-map/PORT_QOS_MAP/PORT_QOS_MAP_LIST']

        for port_qos_map in port_qos_map_list:
            if 'ifname' not in port_qos_map:
               continue
            if ifkey != port_qos_map['ifname']:
               continue
            if map_type in port_qos_map:
               cmd_str += 'qos-map ' + map_type_name_to_cmd[map_type] + ' ' + convert_db_to_config_format(port_qos_map[map_type], map_type_name_to_abnf[map_type]) + ';'

    return 'CB_SUCCESS', cmd_str


def show_qos_intf_map_dscp_tc(render_tables):
    return show_qos_int_maps(render_tables, 'dscp_to_tc_map')

def show_qos_intf_map_dot1p_tc(render_tables):
    return show_qos_int_maps(render_tables, 'dot1p_to_tc_map')

def show_qos_intf_map_tc_queue(render_tables):
    return show_qos_int_maps(render_tables, 'tc_to_queue_map')

def show_qos_intf_map_tc_pg(render_tables):
    return show_qos_int_maps(render_tables, 'tc_to_pg_map')

def show_qos_intf_map_tc_dscp(render_tables):
    return show_qos_int_maps(render_tables, 'tc_to_dscp_map')

def show_qos_intf_map_tc_dot1p(render_tables):
    return show_qos_int_maps(render_tables, 'tc_to_dot1p_map')

def show_qos_intf_map_pfc_queue(render_tables):
    return show_qos_int_maps(render_tables, 'pfc_to_queue_map')

def show_qos_intf_pfc(render_tables):
    cmd_str = ''
    ifkey = ''

    if 'name' in render_tables:
       ifkey = render_tables['name']

    if 'sonic-port-qos-map:sonic-port-qos-map/PORT_QOS_MAP/PORT_QOS_MAP_LIST' in render_tables:
        port_qos_map_list = render_tables['sonic-port-qos-map:sonic-port-qos-map/PORT_QOS_MAP/PORT_QOS_MAP_LIST']

        for port_qos_map in port_qos_map_list:
            if 'ifname' not in port_qos_map:
               continue
            if ifkey != port_qos_map['ifname']:
               continue
            if 'pfc_enable' in port_qos_map:
               priorities = port_qos_map['pfc_enable'].split(',')
               for prio in priorities:
                   cmd_str += 'pfc priority ' + prio + ';'
    
    if 'sonic-port:sonic-port/PORT/PORT_LIST' in render_tables:
        port_inst = render_tables['sonic-port:sonic-port/PORT/PORT_LIST']
        if 'ifname' in port_inst:
           if ifkey == port_inst['ifname']:
              if 'pfc_asym' in port_inst:
                 if port_inst['pfc_asym'] == 'on':
                    cmd_str += 'pfc asymmetric' + ';'

    return 'CB_SUCCESS', cmd_str

