
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




def show_render_if_cmd(table_rec, attr_name, cmd_prfx, cmd_str):

    if cmd_str:
        cmd_str+= ";"
    if attr_name in table_rec:
        intf = table_rec[attr_name]
        if intf.startswith('Eth'):
           cmd_str = cmd_prfx + intf
        elif intf.startswith('Vlan'):
           intf_split = intf.split('Vlan')
           cmd_str = cmd_prfx + 'Vlan ' + intf_split[1]
        elif intf.startswith('PortChannel'):
           intf_split = intf.split('PortChannel')
           cmd_str = cmd_prfx +  'PortChannel ' + intf_split[1]
        elif intf.startswith('Loopback'):
           intf_split = intf.split('Loopback')
           cmd_str = cmd_prfx +  'Loopback ' + intf_split[1]
        elif intf.startswith('eth0'):
           cmd_str = cmd_prfx +  'Management 0'
        else:
           pass
    return cmd_str


def show_get_if_cmd(render_tables, table_name, attr_name, cmd_prfx):

    cmd_str = ''
    table_inst = None
    if table_name in render_tables:
       table_inst = render_tables[table_name]
       if type(table_inst) == list:
          for inst in table_inst:
              cmd_str = show_render_if_cmd(inst, attr_name, cmd_prfx, cmd_str)
       else:
          cmd_str = show_render_if_cmd(table_inst, attr_name, cmd_prfx, cmd_str)

    return 'CB_SUCCESS', cmd_str



def show_dns_source_if(render_tables):

    cmd_prfx = 'ip name-server source-interface '
    return show_get_if_cmd(render_tables,
                           'sonic-system-dns:sonic-system-dns/DNS/DNS_LIST',
                           'src_intf',
                           cmd_prfx)


def show_ntp_source_if(render_tables):

    cmd_prfx = 'ntp source-interface  '
    return show_get_if_cmd(render_tables,
                           'sonic-system-ntp:sonic-system-ntp/NTP/NTP_LIST',
                           'src_intf',
                           cmd_prfx)

def show_tacacs_source_if(render_tables):

    cmd_prfx = 'tacacs-server source-interface '
    return show_get_if_cmd(render_tables,
                           'sonic-system-tacacs:sonic-system-tacacs/TACPLUS/TACPLUS_LIST',
                           'src_intf',
                           cmd_prfx)


def show_sflow_source_if(render_tables):

    cmd_prfx = 'sflow agent-id '
    return show_get_if_cmd(render_tables,
                           'sonic-sflow:sonic-sflow/SFLOW/SFLOW_LIST',
                           'agent_id',
                           cmd_prfx)

def show_mac_source_if(render_tables):
    cmd_prfx = 'mac-address add address '
    table_name = 'sonic-fdb:sonic-fdb/FDB'
    cmd_str = ''
    if table_name in render_tables:
        if 'FDB_LIST' in render_tables[table_name]:
            table_inst = render_tables[table_name]['FDB_LIST']
            for inst in table_inst:
                temp_cmd_prfx = cmd_prfx + inst['mac-address'] + ' '
                temp_cmd_str = ''
                temp_cmd_str = show_render_if_cmd(inst, 'vlan', temp_cmd_prfx, temp_cmd_prfx)
                temp_cmd_str += ' '
                temp_cmd_str = show_render_if_cmd(inst, 'port', temp_cmd_str, temp_cmd_str)
                cmd_str = cmd_str+';'+temp_cmd_str
    return 'CB_SUCCESS', cmd_str

