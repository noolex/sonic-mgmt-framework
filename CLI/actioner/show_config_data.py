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

from show_config_if_cmd import *
from show_config_interface import *
from show_config_bgp import *
from show_config_table_sort import *
from show_config_ptp import *
<<<<<<< HEAD
from show_config_routemap import *
||||||| merged common ancestors
<<<<<<<<< Temporary merge branch 1
||||||||| merged common ancestors
from show_config_dns import *
=========
from show_config_dns import *
=======
from show_config_dns import *
>>>>>>> origin/broadcom_sonic_3.x_share
from show_config_copp import *

view_dependency= \
{'configure-router-bgp':['configure-router-bgp-ipv4', 'configure-router-bgp-ipv6', 'configure-router-bgp-l2vpn',
                         'configure-router-bgp-nbr'],
'configure-router-bgp-nbr':['configure-router-bgp-nbr-ipv4', 'configure-router-bgp-nbr-ipv6', 'configure-router-bgp-nbr-l2vpn']}

config_view_hierarchy= \
<<<<<<< HEAD
['configure', 'config-if-CPU', 'configure-vlan', 'configure-lo', 'configure-vxlan', 'configure-if-mgmt',  'configure-if', 'configure-lag', 'configure-route-map', 'configure-router-bgp', 'copp-action']
||||||| merged common ancestors
<<<<<<<<< Temporary merge branch 1
['configure', 'config-if-CPU', 'configure-vlan', 'configure-lo', 'configure-if-mgmt',  'configure-if', 'configure-lag', 'configure-router-bgp']

||||||||| merged common ancestors
['configure', 'configure-vlan', 'configure-lo', 'configure-if-mgmt',  'configure-if', 'configure-lag', 'configure-router-bgp']

=========
['configure', 'configure-vlan', 'configure-lo', 'configure-vxlan', 'configure-if-mgmt',  'configure-if', 'configure-lag', 'configure-router-bgp', 'copp-action' ]
>>>>>>>>> Temporary merge branch 2
=======
['configure', 'config-if-CPU', 'configure-vlan', 'configure-lo', 'configure-if-mgmt',  'configure-if', 'configure-lag', 'configure-router-bgp, 'configure-vxlan', 'copp-action']
>>>>>>> origin/broadcom_sonic_3.x_share

render_filelst  = {}

render_cb_dict  = {'router_bgp_neighbor'    : show_router_bgp_neighbor_cmd,
                  'if_channel_group'        : show_if_channel_group_cmd,
                  'if_switchport_access'    : show_if_switchport_access,
                  'if_switchport_trunk'     : show_if_switchport_trunk,
                  'interface_loopback'      : show_if_loopback,
                  'interface_portchannel'   : show_interface_portchannel,
                  'if_lag_mclag'            : show_if_lag_mclag,
                  'interface_management'    : show_interface_management,
                  'if_management_autoneg'   : show_if_management_autoneg,
                  'tacacs_server_source_if' : show_tacacs_source_if,
                  'dns_server_source_if'    : show_dns_source_if,
                  'ntp_server_source_if'    : show_ntp_source_if,
                  'ptp_mode'                : show_ptp_mode,
                  'ptp_domain_profile'      : show_ptp_domain_profile,
                  'ptp_two_step'            : show_ptp_two_step,
                  'ptp_network_transport'   : show_ptp_network_transport,
                  'ptp_master_table'        : show_ptp_master_table,
<<<<<<< HEAD
                  'ipv4_eth_dhcp_relay'     : show_ipv4_eth_dhcp_relay,
                  'ipv4_po_dhcp_relay'      : show_ipv4_po_dhcp_relay,
                  'ipv4_vlan_dhcp_relay'    : show_ipv4_vlan_dhcp_relay,
                  'ipv6_eth_dhcp_relay'     : show_ipv6_eth_dhcp_relay,
                  'ipv6_po_dhcp_relay'      : show_ipv6_po_dhcp_relay,
                  'ipv6_vlan_dhcp_relay'    : show_ipv6_vlan_dhcp_relay,
                  'ipv4_eth_ip_address'     : show_ipv4_eth_ip_address,
                  'ipv4_vlan_ip_address'    : show_ipv4_vlan_ip_address,
                  'ipv4_lag_ip_address'     : show_ipv4_lag_ip_address,
                  'ipv4_mgmt_ip_address'    : show_ipv4_mgmt_ip_address,
                  'ipv4_lo_ip_address'      : show_ipv4_lo_ip_address,
                  'ipv6_eth_ip_address'     : show_ipv6_eth_ip_address,
                  'ipv6_vlan_ip_address'    : show_ipv6_vlan_ip_address,
                  'ipv6_lag_ip_address'     : show_ipv6_lag_ip_address,
                  'ipv6_mgmt_ip_address'    : show_ipv6_mgmt_ip_address,
                  'ipv6_lo_ip_address'      : show_ipv6_lo_ip_address,
                  'sflow_source_if'         : show_sflow_source_if,
                  'routemap_set_community'  : show_routemap_setcommunity,
                  'routemap_set_extcommunity' : show_routemap_setextcommunity,
                  'routemap_match_interface'  : show_routemap_matchintf,
                  'routemap_match_peer'     : show_routemap_matchpeer,
                  'routemap_match_tag'      : show_routemap_matchtag,
                  'mac_source_if'           : show_mac_source_if,
||||||| merged common ancestors
<<<<<<<<< Temporary merge branch 1
                  'sflow_source_if'         : show_sflow_source_if,
                  'dns_server_source_if'    : show_dns_source_if
||||||||| merged common ancestors
                  'dns_server_source_if'    : show_dns_source_if
=========
                  'dns_server_source_if'    : show_dns_source_if,
=======
                  'dns_server_source_if'    : show_dns_source_if,
>>>>>>> origin/broadcom_sonic_3.x_share
                  'copp_police'             : show_copp_police
<<<<<<< HEAD
||||||| merged common ancestors
>>>>>>>>> Temporary merge branch 2
=======
                  'sflow_source_if'         : show_sflow_source_if,
>>>>>>> origin/broadcom_sonic_3.x_share
 }
table_sort_cb_dict = {'PORT_LIST' : natsort_list }
