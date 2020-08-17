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
from show_config_errdisable import *
from show_config_spanning_tree import *
from show_config_routepolicy import *
from show_config_copp import *
from show_config_crm import *
from show_config_snmp import *
from show_config_mirror import *
from show_config_static_routes import *
from show_config_fbs import *
from show_config_qos_map import *
from show_config_qos import *
from show_config_logging import *
from show_config_ldap import *
from show_config_radius import *
from show_config_aaa import *
from show_config_nat import *
from show_config_ospfv2 import *
from show_config_ip_helper import *
from show_config_pim import *
from sonic_cli_link_state_tracking import show_running_lst_group, show_running_lst_interface
from show_config_vxlan import *
from show_config_ipsla import *
from show_config_lldp import *
from show_config_igmp_snooping import *
from show_config_tam import *
from show_config_bfd import *
from show_config_swresource import *
from show_config_sag import *
from show_config_vrrp import *
from show_config_acl import *

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
       'configure-link-state-track',
       'configure-mac-acl',
       'configure-ipv4-acl',
       'configure-ipv6-acl',
       'config-if-CPU',
       'configure-vlan',
       'configure-lo',
       'configure-if-mgmt',
       'configure-if',
       'configure-lag',
       'configure-route-map',
       'configure-router-bgp',
       'configure-router-ospf',
       'configure-vxlan',
       'configure-${fbs-class-type}-classifier',
       'copp-action',
       'configure-policy',
       'configure-mclag',
       'configure-mirror',
       'configure-tam',
       'configure-ipsla',
       'configure-bfd',
       'configure-switch-resource',
       'configure-vrrp']

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
                  'routemap_set_metric'       : show_routemap_set_metric,
                  'routemap_match_interface'  : show_routemap_matchintf,
                  'routemap_match_peer'     : show_routemap_matchpeer,
                  'routemap_match_tag'      : show_routemap_matchtag,
                  'mac_source_if'           : show_mac_source_if,
                  'fbs_classifier_render'   : show_running_fbs_classifier,
                  'fbs_policy_render'       : show_running_fbs_policy,
                  'fbs_service_policy_render' : show_running_fbs_service_policy,
                  'copp_police'             : show_copp_police,
                  'crm_config'              : show_crm_config,
                  'snmp_agentaddress'       : show_snmp_agentaddress,
                  'snmp_contact'            : show_snmp_contact,
                  'snmp_community'          : show_snmp_community,
                  'snmp_engine'             : show_snmp_engine,
                  'snmp_group'              : show_snmp_group,
                  'snmp_host'               : show_snmp_host,
                  'snmp_location'           : show_snmp_location,
                  'snmp_traps'              : show_snmp_traps,
                  'snmp_user'               : show_snmp_user,
                  'snmp_view'               : show_snmp_view,
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
                  'qos_intf_pfc_wd'         : show_qos_intf_pfc_wd,
                  'qos_pfc_wd'              : show_qos_pfc_wd,
                  'show_running_lst_group'  : show_running_lst_group,
                  'show_running_lst_interface': show_running_lst_interface,
                  'vlanvrfvnimap'           : show_vlanvrfvnimap,
                  'logging_server_cmd'      : show_logging_server_cmd,
                  'ldap_server_src_intf'    : show_ldap_server_src_intf,
                  'radius_statistics_config': show_radius_statistics_config,
                  'radius_host_config'      : show_radius_host_config,
                  'aaa_config'              : show_aaa_config,
                  'nat_napt_entry'          : show_nat_napt_entry,
                  'ip_helper_address'       : show_ip_helper_address,
                  'ip_helper_include_ports' : show_ip_helper_include_ports,
                  'ip_helper_exclude_ports' : show_ip_helper_exclude_ports,
                  'pim_ipv4_gbl'            : show_pim_ipv4_gbl,
                  'router_ospf'             : show_router_ospf_config,
                  'router_ospf_area'        : show_router_ospf_area_config,
                  'router_ospf_area_network' : show_router_ospf_area_network_config,
                  'router_ospf_area_vlink'   : show_router_ospf_area_vlink_config,
                  'router_ospf_area_addr_range' : show_router_ospf_area_addr_range_config,
                  'router_ospf_distribute_route' : show_router_ospf_distribute_route_config,
                  'router_ospf_passive_interface' : show_router_ospf_passive_interface_config,
                  'interface_ip_ospf' : show_interface_ip_ospf_config,
                  'mirror_session'          : show_mirror_session,
                  'errdisable_cause'        : show_config_errdisable_cause,
                  'lldp_mode'               : show_lldp_mode_config,
                  'lldp_intf_mode'          : show_lldp_intf_mode_config,
                  'lldp_tlv_select'         : show_lldp_tlv_select_config,
                  'ldap_map_config'         : show_ldap_map_config,
                  'igmp_snooping_config'    : show_igmp_snooping_intf_config,
                  'if_lag_config'           : show_if_lag_config,
		  'tam_config'              : show_tam_config,
                  'ip_sla_config'           : show_ip_sla_config,
                  'bfd_config'              : show_bfd_config,
		  'switch_resource_flow_scale_entry' : show_switch_resource_flow_scale_entry,
                  'ldap_map_config'         : show_ldap_map_config,
                  'spanning_tree_vlan'      : show_config_spanning_tree_vlan,
                  'no_spanning_tree_vlan'   : show_config_no_spanning_tree_vlan,
                  'spanning_tree_intf'      : show_config_spanning_tree_intf,
                  'spanning_tree_intf_vlan' : show_config_spanning_tree_intf_vlan,
                  'spanning_tree_global_hello_time'  : show_config_spanning_tree_global_hello_time,
                  'spanning_tree_global_max_age'     : show_config_spanning_tree_global_max_age,
                  'spanning_tree_global_priority'    : show_config_spanning_tree_global_priority,
                  'spanning_tree_global_fwd_delay'   : show_config_spanning_tree_global_fwd_delay,
                  'spanning_tree_global_root_guard_timeout' : show_config_spanning_tree_global_root_guard_time,
                  'sag4_global'             : show_sag4_global,
                  'sag6_global'             : show_sag6_global,
                  'sag4_config'             : show_sag4_config,
                  'sag6_config'             : show_sag6_config,
                  'vrrp_config'             : show_vrrp_config,
                  'mac_acl_table_cb'        : mac_acl_table_cb,
                  'ipv4_acl_table_cb'       : ipv4_acl_table_cb,
                  'ipv6_acl_table_cb'       : ipv6_acl_table_cb,
                  'username_config'         : show_username_config,
 }

table_sort_cb_dict = {'PORT_LIST' : natsort_list }
