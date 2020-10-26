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

from ipaddress import ip_interface
from itertools import groupby
from operator import itemgetter


def show_if_channel_group_cmd(render_tables):
    cmd_str = ''

    if 'name' in render_tables:
       ifname_key = render_tables['name']
       if 'sonic-portchannel:sonic-portchannel/PORTCHANNEL_MEMBER/PORTCHANNEL_MEMBER_LIST' in render_tables:
           for channel_member in render_tables['sonic-portchannel:sonic-portchannel/PORTCHANNEL_MEMBER/PORTCHANNEL_MEMBER_LIST']:
              if 'ifname' in channel_member:
                  if ifname_key == channel_member['ifname']:
                      lag_id = channel_member['name'].lstrip('PortChannel')
                      cmd_str = 'channel-group ' + lag_id
                  
    return 'CB_SUCCESS', cmd_str

def show_if_vrf_binding(render_tables):
    cmd_str = ''
    vrf_name = ''
    if 'name' not in render_tables:
        return 'CB_SUCCESS', cmd_str
    
    if 'sonic-interface:sonic-interface/INTERFACE/INTERFACE_LIST' in render_tables:
        intfdata = render_tables['sonic-interface:sonic-interface/INTERFACE/INTERFACE_LIST']
        key = 'portname'
    elif 'sonic-vlan-interface:sonic-vlan-interface/VLAN_INTERFACE/VLAN_INTERFACE_LIST' in render_tables:
        intfdata = render_tables['sonic-vlan-interface:sonic-vlan-interface/VLAN_INTERFACE/VLAN_INTERFACE_LIST']
        key = 'vlanName'
    elif 'sonic-portchannel-interface:sonic-portchannel-interface/PORTCHANNEL_INTERFACE/PORTCHANNEL_INTERFACE_LIST' in render_tables:
        intfdata = render_tables['sonic-portchannel-interface:sonic-portchannel-interface/PORTCHANNEL_INTERFACE/PORTCHANNEL_INTERFACE_LIST']
        key = 'pch_name'
    elif 'sonic-loopback-interface:sonic-loopback-interface/LOOPBACK_INTERFACE/LOOPBACK_INTERFACE_LIST' in render_tables:
        intfdata = render_tables['sonic-loopback-interface:sonic-loopback-interface/LOOPBACK_INTERFACE/LOOPBACK_INTERFACE_LIST']
        key = 'loIfName'
    else:
        return 'CB_SUCCESS', cmd_str

    for item in intfdata:
        if render_tables['name'] == item[key] and 'vrf_name' in item:
            cmd_str = 'ip vrf forwarding ' + item['vrf_name']
            break  
        
    return 'CB_SUCCESS', cmd_str

def show_if_switchport_access(render_tables):
    cmd_str = ''

    if 'name' in render_tables:
       ifname_key = render_tables['name']
       if 'sonic-vlan:sonic-vlan/VLAN_MEMBER/VLAN_MEMBER_LIST' in render_tables:
           for vlan_member in render_tables['sonic-vlan:sonic-vlan/VLAN_MEMBER/VLAN_MEMBER_LIST']:
              if 'ifname' in vlan_member:
                  if ifname_key == vlan_member['ifname'] and vlan_member['tagging_mode']=='untagged':
                      vlan_id = vlan_member['name'].lstrip('Vlan')
                      cmd_str = 'switchport access Vlan ' + vlan_id

    return 'CB_SUCCESS', cmd_str



def find_ranges(vlan_lst):
    ranges = []
    vlan_lst.sort()
    for k, g in groupby(enumerate(vlan_lst), lambda (i,x):i-x):
        group = map(itemgetter(1), g)
        ranges.append((group[0], group[-1]))
    vlan_list_str = ''
    for range in ranges:
       if vlan_list_str:
           vlan_list_str += ','
       if range[0] == range[1]:
           vlan_list_str += str(range[0])
       else:
           vlan_list_str = vlan_list_str + str(range[0]) + "-" + str(range[1])
    return vlan_list_str


def show_if_switchport_trunk(render_tables):
    cmd_str = ''
    vlan_lst = []
    if 'name' in render_tables:
       ifname_key = render_tables['name']
       if 'sonic-vlan:sonic-vlan/VLAN_MEMBER/VLAN_MEMBER_LIST' in render_tables:
           for vlan_member in render_tables['sonic-vlan:sonic-vlan/VLAN_MEMBER/VLAN_MEMBER_LIST']:
              if 'ifname' in vlan_member:
                if ifname_key == vlan_member['ifname'] and vlan_member['tagging_mode']=='tagged':
                   vlan_id = vlan_member['name'].lstrip('Vlan')
                   vlan_lst.append(int(vlan_id))
    if vlan_lst:
       vstr = find_ranges(vlan_lst)
       if vstr:
          cmd_str = 'switchport trunk allowed Vlan add ' + vstr

    return 'CB_SUCCESS', cmd_str

def show_interface_portchannel(render_tables):
    cmd_str = ''

    if 'name' in render_tables:
        ifname_key = render_tables['name']
        if 'sonic-portchannel:sonic-portchannel/PORTCHANNEL/PORTCHANNEL_LIST' in render_tables:
              portchannel = render_tables['sonic-portchannel:sonic-portchannel/PORTCHANNEL/PORTCHANNEL_LIST']
              if 'name' in portchannel:
                  if ifname_key == portchannel['name']:
                      cmd_str = 'interface PortChannel ' + ifname_key.lstrip('PortChannel')
                      if 'min_links' in portchannel:
                          cmd_str += " min-links "
                          cmd_str += str(portchannel['min_links'])
                      if 'static' in portchannel:
                          if portchannel['static']:
                              cmd_str += " mode on"
                          else:
                              cmd_str += " mode active"
                      if 'fallback' in portchannel and portchannel['fallback']:
                          cmd_str += ' fallback'
                      if 'fast_rate' in portchannel and portchannel['fast_rate']:
                          cmd_str += ' fast_rate'

    return 'CB_SUCCESS', cmd_str

def show_if_lag_config(render_tables):
    cmd_str = ''

    if 'name' in render_tables:
        ifname_key = render_tables['name']
        if 'sonic-portchannel:sonic-portchannel/PORTCHANNEL/PORTCHANNEL_LIST' in render_tables:
              portchannel = render_tables['sonic-portchannel:sonic-portchannel/PORTCHANNEL/PORTCHANNEL_LIST']
              if 'name' in portchannel:
                  if ifname_key == portchannel['name']:
                      if 'graceful_shutdown_mode' in portchannel:
                          if portchannel['graceful_shutdown_mode'] == 'enable':
                              cmd_str += "graceful-shutdown"
                          if portchannel['graceful_shutdown_mode'] == 'disable':
                              cmd_str += "no graceful-shutdown"

    return 'CB_SUCCESS', cmd_str

def show_if_lag_mclag(render_tables):
   cmd_str = ''

   if 'name' in render_tables:
       ifname_key = render_tables['name']
       if 'sonic-mclag:sonic-mclag/MCLAG_INTERFACE/MCLAG_INTERFACE_LIST' in render_tables:
             for mclag_if in render_tables['sonic-mclag:sonic-mclag/MCLAG_INTERFACE/MCLAG_INTERFACE_LIST']:
                 if 'if_name' in mclag_if:
                    if ifname_key == mclag_if['if_name']:
                       if 'domain_id' in mclag_if:
                           cmd_str = 'mclag ' + str(mclag_if['domain_id'])
   return 'CB_SUCCESS', cmd_str    
        

def show_interface_management(render_tables):
    return 'CB_SUCCESS','interface Management 0'


def show_if_management_autoneg(render_tables):
    cmd_str = ''

    if 'name' in render_tables:
        ifname_key = render_tables['name']
        if 'sonic-mgmt-port:sonic-mgmt-port/MGMT_PORT/MGMT_PORT_LIST' in render_tables:
              port = render_tables['sonic-mgmt-port:sonic-mgmt-port/MGMT_PORT/MGMT_PORT_LIST']
              if 'ifname' in port:
                  if ifname_key == port['ifname']:
                      if 'autoneg' in port:
                         if port['autoneg']:
                             cmd_str = "autoneg on"
                         else:
                             cmd_str = "autoneg off"

    return 'CB_SUCCESS', cmd_str

def show_if_loopback(render_tables):
  cmd_str = ''

  if 'name' in render_tables:
      ifname = render_tables['name']
      cmd_str = "interface Loopback " + ifname.lstrip('Loopback')
  return 'CB_SUCCESS', cmd_str




def show_dhcp_relay(if_name, intf, if_name_key, cmd_str, cmd_prfx):

   if cmd_str:
      cmd_str += ';'

   if if_name in intf:
      port = intf[if_name]
      if if_name_key == port:
         dhcp_server_str = ''
         if 'dhcp_servers' in intf and cmd_prfx== 'ip dhcp-relay':
           for server in intf['dhcp_servers']:
               dhcp_server_str += ' '
               dhcp_server_str += server
           if dhcp_server_str:
               cmd_str += cmd_prfx
               cmd_str += dhcp_server_str
               if 'dhcp_server_vrf' in intf:
                   cmd_str += " "
                   cmd_str += 'vrf '
                   cmd_str += intf['dhcp_server_vrf']
         if 'dhcpv6_servers' in intf and cmd_prfx== 'ipv6 dhcp-relay':
           for server in intf['dhcpv6_servers']:
               dhcp_server_str += ' '
               dhcp_server_str += server
           if dhcp_server_str:
               cmd_str += cmd_prfx
               cmd_str += dhcp_server_str
               if 'dhcpv6_server_vrf' in intf:
                   cmd_str += " "
                   cmd_str += 'vrf '
                   cmd_str += intf['dhcpv6_server_vrf']               


   return  cmd_str




def show_ip_dhcp_relay(render_tables, table_name, key_name, if_name, cmd_prfx):

   cmd_str = '' 
   intf_list = None
   if_name_key = None
   if key_name in render_tables:
     if_name_key = render_tables[key_name]
   if table_name in render_tables:
     intf_list = render_tables[table_name]

   if type(intf_list) == list:
     for intf in intf_list:
         cmd_str = show_dhcp_relay(if_name, intf, if_name_key, cmd_str, cmd_prfx)

   elif intf_list:
         cmd_str = show_dhcp_relay(if_name, intf_list, if_name_key, cmd_str, cmd_prfx)

   return 'CB_SUCCESS', cmd_str 

   
def show_ipv4_eth_dhcp_relay(render_tables):
   return show_ip_dhcp_relay(render_tables, 
                             'sonic-interface:sonic-interface/INTERFACE/INTERFACE_LIST',
                             'name',
                             'portname',
                             'ip dhcp-relay')

def show_ipv4_po_dhcp_relay(render_tables):
   return show_ip_dhcp_relay(render_tables, 
                             'sonic-portchannel-interface:sonic-portchannel-interface/PORTCHANNEL_INTERFACE/PORTCHANNEL_INTERFACE_LIST',
                             'name',
                             'pch_name',
                             'ip dhcp-relay')

def show_ipv4_vlan_dhcp_relay(render_tables):
   return show_ip_dhcp_relay(render_tables, 
                             'sonic-vlan:sonic-vlan/VLAN/VLAN_LIST',
                             'name',
                             'name',
                             'ip dhcp-relay')

def show_ipv6_eth_dhcp_relay(render_tables):
   return show_ip_dhcp_relay(render_tables, 
                             'sonic-interface:sonic-interface/INTERFACE/INTERFACE_LIST',
                             'name',
                             'portname',
                             'ipv6 dhcp-relay')

def show_ipv6_po_dhcp_relay(render_tables):
   return show_ip_dhcp_relay(render_tables, 
                             'sonic-portchannel-interface:sonic-portchannel-interface/PORTCHANNEL_INTERFACE/PORTCHANNEL_INTERFACE_LIST',
                             'name',
                             'pch_name',
                             'ipv6 dhcp-relay')

def show_ipv6_vlan_dhcp_relay(render_tables):
   return show_ip_dhcp_relay(render_tables, 
                             'sonic-vlan:sonic-vlan/VLAN/VLAN_LIST',
                             'name',
                             'name',
                             'ipv6 dhcp-relay')



def show_ip_address(render_tables, table_name, key_name, table_key_name, cmd_prfx):

   cmd_str = ''
   if_name_key = None
   if key_name in render_tables:
     if_name_key = render_tables[key_name]
   if table_name in render_tables:
     ip_addr_list = render_tables[table_name]
     for ip_addr_rec in ip_addr_list:
         if table_key_name in ip_addr_rec:
            intf = ip_addr_rec[table_key_name]
            if if_name_key == intf:
               if 'ip_prefix' in ip_addr_rec:
                  ip_addr = ip_addr_rec['ip_prefix']
                  cmd = ''
                  if ip_interface(ip_addr).ip.version == 6 and cmd_prfx == 'ipv6 address':
                      cmd = cmd_prfx + ' ' + ip_addr
                      if cmd_str:
                         cmd_str += ';'
                      cmd_str += cmd
                  elif ip_interface(ip_addr).ip.version == 4 and cmd_prfx == 'ip address':
                      cmd = cmd_prfx + ' ' + ip_addr
                      if 'secondary' in ip_addr_rec:
                          sec_val = ip_addr_rec['secondary']
                          if sec_val == True:
                              cmd += " secondary"
                      if cmd_str:
                         cmd_str += ';'
                      cmd_str += cmd
                  if  'gwaddr' in ip_addr_rec and cmd:
                      cmd = ' gwaddr ' + ip_addr_rec['gwaddr']
                      cmd_str += cmd

   return 'CB_SUCCESS', cmd_str

def show_ipv4_eth_ip_address(render_tables):
    return show_ip_address(render_tables,
                          'sonic-interface:sonic-interface/INTERFACE/INTERFACE_IPADDR_LIST',
                          'name',
                          'portname',
                          'ip address')

def show_ipv4_vlan_ip_address(render_tables):
    return show_ip_address(render_tables,
                          'sonic-vlan-interface:sonic-vlan-interface/VLAN_INTERFACE/VLAN_INTERFACE_IPADDR_LIST',
                          'name',
                          'vlanName',
                          'ip address')    


def show_ipv4_lag_ip_address(render_tables):
    return show_ip_address(render_tables,
                          'sonic-portchannel-interface:sonic-portchannel-interface/PORTCHANNEL_INTERFACE/PORTCHANNEL_INTERFACE_IPADDR_LIST',
                          'name',
                          'pch_name',
                          'ip address')


def show_ipv4_mgmt_ip_address(render_tables):
    return show_ip_address(render_tables,
                          'sonic-mgmt-interface:sonic-mgmt-interface/MGMT_INTERFACE/MGMT_INTERFACE_IPADDR_LIST',
                          'name',
                          'portname',
                          'ip address')

def show_ipv4_lo_ip_address(render_tables):
    return show_ip_address(render_tables,
                          'sonic-loopback-interface:sonic-loopback-interface/LOOPBACK_INTERFACE/LOOPBACK_INTERFACE_IPADDR_LIST',
                          'name',
                          'loIfName',
                          'ip address')


def show_ipv6_eth_ip_address(render_tables):
    return show_ip_address(render_tables,
                          'sonic-interface:sonic-interface/INTERFACE/INTERFACE_IPADDR_LIST',
                          'name',
                          'portname',
                          'ipv6 address')

def show_ipv6_vlan_ip_address(render_tables):
    return show_ip_address(render_tables,
                          'sonic-vlan-interface:sonic-vlan-interface/VLAN_INTERFACE/VLAN_INTERFACE_IPADDR_LIST',
                          'name',
                          'vlanName',
                          'ipv6 address')    


def show_ipv6_lag_ip_address(render_tables):
    return show_ip_address(render_tables,
                          'sonic-portchannel-interface:sonic-portchannel-interface/PORTCHANNEL_INTERFACE/PORTCHANNEL_INTERFACE_IPADDR_LIST',
                          'name',
                          'pch_name',
                          'ipv6 address')


def show_ipv6_mgmt_ip_address(render_tables):
    return show_ip_address(render_tables,
                          'sonic-mgmt-interface:sonic-mgmt-interface/MGMT_INTERFACE/MGMT_INTERFACE_IPADDR_LIST',
                          'name',
                          'portname',
                          'ipv6 address')

def show_ipv6_lo_ip_address(render_tables):
    return show_ip_address(render_tables,
                          'sonic-loopback-interface:sonic-loopback-interface/LOOPBACK_INTERFACE/LOOPBACK_INTERFACE_IPADDR_LIST',
                          'name',
                          'loIfName',
                          'ipv6 address')
