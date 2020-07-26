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
###########################################################################


def show_ip_sla_icmp_config(render_tables):
    cmd_str = ''
    if 'sonic-ip-sla:sonic-ip-sla/IP_SLA/IP_SLA_LIST' in render_tables:
        cmd_prefix = 'icmp-echo'
        table_inst = render_tables['sonic-ip-sla:sonic-ip-sla/IP_SLA/IP_SLA_LIST']
        if 'icmp_dst_ip' in table_inst:
            cmd_str = cmd_prefix + ' ' + str(table_inst['icmp_dst_ip']) + ';'
        if 'icmp_source_ip' in table_inst:
            cmd_str += ' source-address ' + str(table_inst['icmp_source_ip']) + ';'
        if 'icmp_source_interface' in table_inst:
            cmd_str += ' source-interface ' + str(table_inst['icmp_source_interface']) + ';'
        if 'icmp_source_vrf' in table_inst:
            cmd_str += ' source-vrf ' + str(table_inst['icmp_source_vrf']) + ';'
        if 'icmp_size' in table_inst:
            cmd_str += ' request-data-size ' + str(table_inst['icmp_size']) + ';'
        if 'icmp_ttl' in table_inst:
            cmd_str += ' ttl ' + str(table_inst['icmp_ttl']) + ';'
        if 'icmp_tos' in table_inst:
            cmd_str += ' tos ' + str(table_inst['icmp_tos']) + ';'

    return cmd_str



def show_ip_sla_tcp_config(render_tables):
    cmd_str = ''
    if 'sonic-ip-sla:sonic-ip-sla/IP_SLA/IP_SLA_LIST' in render_tables:
        cmd_prefix = 'tcp-connect'
        table_inst = render_tables['sonic-ip-sla:sonic-ip-sla/IP_SLA/IP_SLA_LIST']
        if 'tcp_dst_ip' in table_inst:
            cmd_str = cmd_prefix + ' ' + str(table_inst['tcp_dst_ip']) + ';'
            if 'tcp_dst_port' in table_inst:
                cmd_str = cmd_prefix + ' ' + str(table_inst['tcp_dst_ip']) + ' port ' + str(table_inst['tcp_dst_port']) + ';'
 
        if 'tcp_source_ip' in table_inst:
            cmd_str += ' source-address ' + str(table_inst['tcp_source_ip']) + ';'
        if 'tcp_source_interface' in table_inst:
            cmd_str += ' source-interface ' + str(table_inst['tcp_source_interface']) + ';'
        if 'tcp_source_vrf' in table_inst:
            cmd_str += ' source-vrf ' + str(table_inst['tcp_source_vrf']) + ';'
        if 'tcp_source_port' in table_inst:
            cmd_str += ' source-port ' + str(table_inst['tcp_source_port']) + ';'
        if 'tcp_ttl' in table_inst:
            cmd_str += ' ttl ' + str(table_inst['tcp_ttl']) + ';'
        if 'tcp_tos' in table_inst:
            cmd_str += ' tos ' + str(table_inst['tcp_tos']) + ';'

    return cmd_str


def show_ip_sla_config(render_tables):
    cmd_str = ''

    if 'sonic-ip-sla:sonic-ip-sla/IP_SLA/IP_SLA_LIST' in render_tables:
        table_name = 'sonic-ip-sla:sonic-ip-sla/IP_SLA'
        table_inst = render_tables['sonic-ip-sla:sonic-ip-sla/IP_SLA/IP_SLA_LIST']
        cmd_prefix = 'ip sla'
        if 'ip_sla_id' in table_inst:
            cmd_str = cmd_prefix + ' ' + str(table_inst['ip_sla_id']) + ';'
        if 'frequency' in table_inst:
            cmd_str += ' frequency ' + str(table_inst['frequency']) + ';'
        if 'threshold' in table_inst:
            cmd_str += ' threshold ' + str(table_inst['threshold']) + ';'
        if 'timeout' in table_inst:
            cmd_str += ' timeout ' + str(table_inst['timeout']) + ';'
        if 'tcp_dst_ip' in table_inst:
            cmd_str += show_ip_sla_tcp_config(render_tables) 
        if 'icmp_dst_ip' in table_inst:
            cmd_str += show_ip_sla_icmp_config(render_tables) 
    
    return 'CB_SUCCESS', cmd_str

