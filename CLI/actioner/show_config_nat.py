###########################################################################
#
# Copyright 2019 Broadcom, Inc.
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

def show_nat_napt_table_entry(render_tables, table_name, ip_key, protocol_key, port_key):
   cmd_str = ""
   if table_name in render_tables:
       nat_entry_list = render_tables[table_name]
       for nat_entry in nat_entry_list:
           cmd_str += "static "
           if protocol_key in nat_entry: 
               cmd_str += nat_entry[protocol_key].lower()
               cmd_str += " "
           else:
               cmd_str += "basic "
           cmd_str += nat_entry['global_ip'] 
           cmd_str += " "
           if port_key in nat_entry:
               cmd_str += str(nat_entry[port_key])
               cmd_str += " "
           cmd_str += nat_entry['local_ip'] 
           cmd_str += " "
           if 'local_port' in nat_entry:
               cmd_str += str(nat_entry['local_port'])
               cmd_str += " "
           if 'twice_nat_id' in nat_entry:
               cmd_str += "twice-nat-id "+ str(nat_entry['twice_nat_id'])
           cmd_str += "\n "
   return  cmd_str


def show_nat_napt_entry(render_tables):
   napt_cmd_str = show_nat_napt_table_entry(render_tables,
                  'sonic-nat:sonic-nat/STATIC_NAPT/STATIC_NAPT_LIST',
                  'global_ip',
                  'ip_protocol',
                  'global_l4_port')
   nat_cmd_str = show_nat_napt_table_entry(render_tables,
                  'sonic-nat:sonic-nat/STATIC_NAT/STATIC_NAT_LIST',
                  'global_ip', "NULL", "NULL")
   cmd_str = napt_cmd_str + nat_cmd_str 
   return 'CB_SUCCESS', cmd_str

