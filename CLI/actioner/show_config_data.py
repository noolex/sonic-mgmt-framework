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
from show_config_routepolicy import *
from show_config_copp import *
from show_config_static_routes import *
from show_config_mirror import *
from show_config_qos_map import *
from show_config_qos import *
from show_config_logging import *
from show_config_nat import *
from show_config_ip_helper import *
from show_config_pim import *

view_dependency= \
{'configure-router-bgp':['configure-router-bgp-ipv4', 'configure-router-bgp-ipv6', 'configure-router-bgp-l2vpn',
                         'configure-router-bgp-template', 'configure-router-bgp-nbr'],
'configure-router-bgp-template':['configure-router-bgp-template-ipv4', 'configure-router-bgp-template-ipv6', 'configure-router-bgp-template-l2vpn'],
'configure-router-bgp-nbr':['configure-router-bgp-nbr-ipv4', 'configure-router-bgp-nbr-ipv6', 'configure-router-bgp-nbr-l2vpn'],
'configure-router-bgp-l2vpn':['configure-router-bgp-l2vpn-vni']}


config_view_hierarchy= \
      ['configure',
       'configure-nat',
       'configure-wred',
       'configure-qos-scheduler-policy',
       'configure-dscp-tc-map',
       'configure-dot1p-tc-map',
       'configure-tc-queue-map',
       'configure-tc-pg-map',
       'configure-pfc-priority-queue-map',
       'configure-tc-dot1p-map',
       'configure-tc-dscp-map',
       'config-if-CPU',
       'configure-vlan',
       'configure-lo',
       'configure-if-mgmt',
       'configure-if',
       'configure-lag',
       'configure-route-map',
       'configure-router-bgp',
       'configure-vxlan',
       'copp-action',
       'configure-mclag',
       'configure-mirror']

render_filelst  = {}

render_cb_dict  = {'router_bgp'             : show_router_bgp_cmd,
                  'router_bgp_neighbor'     : show_router_bgp_neighbor_cmd,
                   'router_bgp_confed'      : show_router_bgp_confed_cmd,
                  'bgp_nbr_upd_src'         : show_bgp_nbr_upd_src_cmd,
                  'bgp_pg_upd_src'          : show_bgp_pg_upd_src_cmd,
                  'bgp_nbr_af_rmap'         : show_bgp_nbr_af_rmap,
                  'bgp_nbr_af_flist'        : show_bgp_nbr_af_flist_cmd,
                  'bgp_nbr_af_plist'        : show_bgp_nbr_af_plist_cmd,
                  'bgp_nbr_af_attr'         : show_bgp_nbr_af_attr_cmd,
                  'bgp_nbr_af_max_prefix'   : show_bgp_nbr_af_max_prefix_cmd,
                  'bgp_nbr_af_allowas'      : show_bgp_nbr_af_allowas_cmd,
                  'bgp_pg_af_rmap'          : show_bgp_pg_af_rmap_cmd,
                  'bgp_pg_af_flist'         : show_bgp_pg_af_flist_cmd,
                  'bgp_pg_af_plist'         : show_bgp_pg_af_plist_cmd,
                  'bgp_pg_af_attr'          : show_bgp_pg_af_attr_cmd,
                  'bgp_pg_af_max_prefix'    : show_bgp_pg_af_max_prefix_cmd,
                  'bgp_pg_af_allowas'       : show_bgp_pg_af_allowas_cmd,
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
                  'routemap_set_community'  : show_routemap_setcommunity,
                  'routemap_set_extcommunity' : show_routemap_setextcommunity,
                  'routemap_match_interface'  : show_routemap_matchintf,
                  'routemap_match_peer'     : show_routemap_matchpeer,
                  'routemap_match_tag'      : show_routemap_matchtag,
                  'mac_source_if'           : show_mac_source_if,
                  'copp_police'             : show_copp_police,
                  'sflow_source_if'         : show_sflow_source_if,
                  'qos_map_dscp_tc_cb'      : qos_map_dscp_tc_cb,
                  'qos_map_dot1p_tc_cb'     : qos_map_dot1p_tc_cb,
                  'qos_map_tc_queue_cb'     : qos_map_tc_queue_cb,
                  'qos_map_tc_pg_cb'        : qos_map_tc_pg_cb,
                  'qos_map_pfc_queue_cb'    : qos_map_pfc_queue_cb,
                  'qos_map_tc_dot1p_cb'     : qos_map_tc_dot1p_cb,
                  'qos_map_tc_dscp_cb'      : qos_map_tc_dscp_cb,
                  'bgp_af_ipv4_nw'          : show_router_bgp_af_nw_cmd,
                  'bgp_af_ipv4_ag'          : show_router_bgp_af_ag_cmd,
                  'bgp_af_ipv4_redist'      : show_router_bgp_af_redist_cmd,
                  'bgp_af_ipv6_nw'          : show_router_bgp_af_nw_cmd,
                  'bgp_af_ipv6_ag'          : show_router_bgp_af_ag_cmd,
                  'bgp_af_ipv6_redist'      : show_router_bgp_af_redist_cmd,
                  'bgp_af_l2vpn_rt'         : show_router_bgp_af_l2vpn_rt_cmd,
                  'bgp_af_l2vpn_vni_rt'     : show_router_bgp_af_l2vpn_vni_rt_cmd,
                  'v4prefix_lists_cmd'      : show_v4prefix_lists,
                  'v6prefix_lists_cmd'      : show_v6prefix_lists,
                  'static_routes_entry'     : show_ntwk_static_v4route,
                  'static_routes_v6entry'   : show_ntwk_static_v6route,
                  'bgp_com_list'            : show_bgpcom_lists,
                  'bgp_extcom_list'         : show_bgpextcom_lists,
                  'bgp_aspath_list'         : show_bgpaspath_lists,
                  'qos_wred_policy_green'   : show_wred_policy_green,
                  'qos_wred_policy_yellow'  : show_wred_policy_yellow,
                  'qos_wred_policy_red'     : show_wred_policy_red,
                  'queue_wred_policy'       : show_queue_wred_policy,
                  'qos_scheduler_policy_cb' : show_scheduler_policy,
                  'qos_scheduler_policy_q_cb' : show_scheduler_policy_q,
                  'qos_scheduler_policy_port_cb' : show_scheduler_policy_port,
                  'qos_intf_map_dscp_tc'    : show_qos_intf_map_dscp_tc,
                  'qos_intf_map_dot1p_tc'   : show_qos_intf_map_dot1p_tc,
                  'qos_intf_map_tc_queue'   : show_qos_intf_map_tc_queue,
                  'qos_intf_map_tc_pg'      : show_qos_intf_map_tc_pg,
                  'qos_intf_map_tc_dscp'    : show_qos_intf_map_tc_dscp,
                  'qos_intf_map_tc_dot1p'   : show_qos_intf_map_tc_dot1p,
                  'qos_intf_map_pfc_queue'  : show_qos_intf_map_pfc_queue,
                  'qos_intf_pfc'            : show_qos_intf_pfc,
                  'qos_intf_sched_policy'   : show_qos_intf_scheduler_policy,
                  'nat_napt_entry'          : show_nat_napt_entry,
                  'logging_server_cmd'      : show_logging_server_cmd,
                  'nat_napt_entry'          : show_nat_napt_entry,
                  'ip_helper_address'       : show_ip_helper_address,
                  'ip_helper_include_ports' : show_ip_helper_include_ports,
                  'ip_helper_exclude_ports' : show_ip_helper_exclude_ports,
                  'pim_ipv4_gbl'            : show_pim_ipv4_gbl,
                  'mirror_session'          : show_mirror_session
 }

table_sort_cb_dict = {'PORT_LIST' : natsort_list }
