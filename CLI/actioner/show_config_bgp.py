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

from show_config_if_cmd import show_get_if_cmd

def show_bgp_cmn_upd_src_cmd(render_tables, name):

  cmd_prfx = 'update-source interface '
  status, cmd_str = show_get_if_cmd(render_tables,
                                    name,
                                    'local_addr',
                                    cmd_prfx)
  if not cmd_str:
      if name in render_tables:
          inst = render_tables[name]
          if 'local_addr' in inst:
              cmd_str = "update-source " + inst['local_addr']

  return 'CB_SUCCESS', cmd_str

def show_bgp_cmn_af_flist_cmd(render_tables, name):
  cmd_str = ''
  if name in render_tables:
      af_inst = render_tables[name]
      cmd_prfx = 'filter-list '
      if 'filter_list_in' in af_inst:
          cmd_str += cmd_prfx + af_inst['filter_list_in'] + " in;"
      if 'filter_list_out' in af_inst:
          cmd_str += cmd_prfx + af_inst['filter_list_out'] + " out;"

  return 'CB_SUCCESS', cmd_str

def show_bgp_cmn_af_plist_cmd(render_tables, name):
  cmd_str = ''
  if name in render_tables:
      af_inst = render_tables[name]
      cmd_prfx = 'prefix-list '
      if 'prefix_list_in' in af_inst:
          cmd_str += cmd_prfx + af_inst['prefix_list_in'] + " in;"
      if 'prefix_list_out' in af_inst:
          cmd_str += cmd_prfx + af_inst['prefix_list_out'] + " out;"

  return 'CB_SUCCESS', cmd_str

def show_bgp_cmn_af_rmap_cmd(render_tables, name):
  cmd_str = ''
  if name in render_tables:
      af_inst = render_tables[name]
      cmd_prfx = 'route-map '
      if 'route_map_in' in af_inst:
          rmap_list_in = af_inst['route_map_in']
          for rmap in rmap_list_in:
              cmd_str += cmd_prfx + rmap + " in;"
      if 'route_map_out' in af_inst:
          rmap_list_out = af_inst['route_map_out']
          for rmap in rmap_list_out:
              cmd_str += cmd_prfx + rmap + " out;"

  return 'CB_SUCCESS', cmd_str

def show_bgp_cmn_af_attr_cmd(render_tables, name):
  cmd_str = ''
  aspath = ''
  med = ''
  nexthop = ''
  if name in render_tables:
      pgaf_inst = render_tables[name]
      cmd_prfx = 'attribute-unchanged'
      if 'unchanged_as_path' in pgaf_inst and pgaf_inst['unchanged_as_path'] == True:
         aspath = ' as-path'
      if 'unchanged_med' in pgaf_inst and pgaf_inst['unchanged_med']== True:
         med = ' med'
      if 'unchanged_nexthop' in pgaf_inst and pgaf_inst['unchanged_nexthop'] == True:
         nexthop = ' next-hop'

      if aspath and med and nexthop:
         cmd_str = cmd_prfx
      elif aspath or med or nexthop:
         cmd_str = cmd_prfx + aspath + med + nexthop

  return 'CB_SUCCESS', cmd_str

def show_bgp_cmn_af_max_prefix_cmd(render_tables, name):
  cmd_str = ''
  if name in render_tables:
      af_inst = render_tables[name]
      cmd_prfx = 'maximum-prefix'
      if 'max_prefix_limit' in af_inst:
         cmd_str += cmd_prfx + ' ' + str(af_inst['max_prefix_limit'])
         if 'max_prefix_warning_threshold' in af_inst:
            cmd_str += ' ' + str(af_inst['max_prefix_warning_threshold'])
         if 'max_prefix_warning_only' in af_inst and af_inst['max_prefix_warning_only']== True:
            cmd_str += ' warning-only'
         if 'max_prefix_restart_interval' in af_inst:
            cmd_str += ' restart ' + str(af_inst['max_prefix_restart_interval'])

  return 'CB_SUCCESS', cmd_str

def show_bgp_cmn_af_allowas_cmd(render_tables, name):
  cmd_str = ''
  if name in render_tables:
      af_inst = render_tables[name]
      cmd_prfx = 'allowas-in'
      if 'allow_as_in' in af_inst and af_inst['allow_as_in'] == True:
         cmd_str += cmd_prfx
         if 'allow_as_origin' in af_inst and af_inst['allow_as_origin'] == True:
            cmd_str += ' origin'
         elif 'allow_as_count' in af_inst:
            cmd_str += ' ' + str(af_inst['allow_as_count'])

  return 'CB_SUCCESS', cmd_str



# BGP NBR Ipv4 and ipv6 and l2vpn family
def show_bgp_nbr_upd_src_cmd(render_tables):
    return show_bgp_cmn_upd_src_cmd(render_tables,
           'sonic-bgp-neighbor:sonic-bgp-neighbor/BGP_NEIGHBOR/BGP_NEIGHBOR_LIST')

def show_bgp_nbr_af_rmap(render_tables):
    return show_bgp_cmn_af_rmap_cmd(render_tables,
           'sonic-bgp-neighbor:sonic-bgp-neighbor/BGP_NEIGHBOR_AF/BGP_NEIGHBOR_AF_LIST')

def show_bgp_nbr_af_flist_cmd(render_tables):
    return show_bgp_cmn_af_flist_cmd(render_tables,
           'sonic-bgp-neighbor:sonic-bgp-neighbor/BGP_NEIGHBOR_AF/BGP_NEIGHBOR_AF_LIST')

def show_bgp_nbr_af_plist_cmd(render_tables):
    return show_bgp_cmn_af_plist_cmd(render_tables,
           'sonic-bgp-neighbor:sonic-bgp-neighbor/BGP_NEIGHBOR_AF/BGP_NEIGHBOR_AF_LIST')

def show_bgp_nbr_af_attr_cmd(render_tables):
    return show_bgp_cmn_af_attr_cmd(render_tables,
           'sonic-bgp-neighbor:sonic-bgp-neighbor/BGP_NEIGHBOR_AF/BGP_NEIGHBOR_AF_LIST')

def show_bgp_nbr_af_max_prefix_cmd(render_tables):
    return show_bgp_cmn_af_max_prefix_cmd(render_tables,
           'sonic-bgp-neighbor:sonic-bgp-neighbor/BGP_NEIGHBOR_AF/BGP_NEIGHBOR_AF_LIST')

def show_bgp_nbr_af_allowas_cmd(render_tables):
    return show_bgp_cmn_af_allowas_cmd(render_tables,
           'sonic-bgp-neighbor:sonic-bgp-neighbor/BGP_NEIGHBOR_AF/BGP_NEIGHBOR_AF_LIST')

# BGP peer group Ipv4 and ipv6 and l2vpn family
def show_bgp_pg_upd_src_cmd(render_tables):
    return show_bgp_cmn_upd_src_cmd(render_tables,
           'sonic-bgp-peergroup:sonic-bgp-peergroup/BGP_PEER_GROUP/BGP_PEER_GROUP_LIST')

def show_bgp_pg_af_attr_cmd(render_tables):
    return show_bgp_cmn_af_attr_cmd(render_tables,
           'sonic-bgp-peergroup:sonic-bgp-peergroup/BGP_PEER_GROUP_AF/BGP_PEER_GROUP_AF_LIST')

def show_bgp_pg_af_flist_cmd(render_tables):
    return show_bgp_cmn_af_flist_cmd(render_tables,
           'sonic-bgp-peergroup:sonic-bgp-peergroup/BGP_PEER_GROUP_AF/BGP_PEER_GROUP_AF_LIST')

def show_bgp_pg_af_plist_cmd(render_tables):
    return show_bgp_cmn_af_plist_cmd(render_tables,
           'sonic-bgp-peergroup:sonic-bgp-peergroup/BGP_PEER_GROUP_AF/BGP_PEER_GROUP_AF_LIST')

def show_bgp_pg_af_rmap_cmd(render_tables):
    return show_bgp_cmn_af_rmap_cmd(render_tables,
           'sonic-bgp-peergroup:sonic-bgp-peergroup/BGP_PEER_GROUP_AF/BGP_PEER_GROUP_AF_LIST')

def show_bgp_pg_af_max_prefix_cmd(render_tables):
    return show_bgp_cmn_af_max_prefix_cmd(render_tables,
           'sonic-bgp-peergroup:sonic-bgp-peergroup/BGP_PEER_GROUP_AF/BGP_PEER_GROUP_AF_LIST')

def show_bgp_pg_af_allowas_cmd(render_tables):
    return show_bgp_cmn_af_allowas_cmd(render_tables,
           'sonic-bgp-peergroup:sonic-bgp-peergroup/BGP_PEER_GROUP_AF/BGP_PEER_GROUP_AF_LIST')

def show_router_bgp_confed_cmd(render_tables):
  cmd_str = ''
  if 'sonic-bgp-global:sonic-bgp-global/BGP_GLOBALS/BGP_GLOBALS_LIST' in render_tables:
      inst = render_tables['sonic-bgp-global:sonic-bgp-global/BGP_GLOBALS/BGP_GLOBALS_LIST']
      cmd_prfx = 'confederation '
      if 'confed_id' in inst:
         cmd_str = cmd_prfx + 'identifier ' + str(inst['confed_id']) + ';'
      if 'confed_peers' in inst:
         for peer in inst['confed_peers']:
             cmd_str += cmd_prfx + 'peers ' + str(peer) + ';'

  return 'CB_SUCCESS', cmd_str

def show_router_bgp_neighbor_cmd(render_tables):

  cmd_prfx = 'neighbor interface '
  status, cmd_str = show_get_if_cmd(render_tables,
                                    'sonic-bgp-neighbor:sonic-bgp-neighbor/BGP_NEIGHBOR/BGP_NEIGHBOR_LIST',
                                    'neighbor',
                                    cmd_prfx)
  if not cmd_str:
      if 'sonic-bgp-neighbor:sonic-bgp-neighbor/BGP_NEIGHBOR/BGP_NEIGHBOR_LIST' in render_tables:
          neighbor_inst = render_tables['sonic-bgp-neighbor:sonic-bgp-neighbor/BGP_NEIGHBOR/BGP_NEIGHBOR_LIST']
          if 'neighbor' in neighbor_inst:
              neighbor = neighbor_inst['neighbor']
              cmd_str = 'neighbor ' + neighbor

  return 'CB_SUCCESS', cmd_str

def show_router_bgp_cmd(render_tables):
    cmd_str = ''
    if 'sonic-bgp-global:sonic-bgp-global/BGP_GLOBALS/BGP_GLOBALS_LIST' in render_tables:
        cmd_prefix = 'router bgp'
        rmap = render_tables['sonic-bgp-global:sonic-bgp-global/BGP_GLOBALS/BGP_GLOBALS_LIST']
        if 'local_asn' in rmap:
            cmd_str = cmd_prefix + ' ' + str(rmap['local_asn'])
        if 'vrf_name' in rmap and rmap['vrf_name'] != 'default':
            cmd_str = cmd_str + ' vrf ' + rmap['vrf_name']

    return 'CB_SUCCESS', cmd_str

def show_router_bgp_af_nw_cmd(render_tables):
    cmd_str = ''
    vrf_name = render_tables['vrf-name']
    afi_safi = render_tables['afi-safi']
    if 'sonic-bgp-global:sonic-bgp-global/BGP_GLOBALS_AF_NETWORK/BGP_GLOBALS_AF_NETWORK_LIST' in render_tables:
        rmap = render_tables['sonic-bgp-global:sonic-bgp-global/BGP_GLOBALS_AF_NETWORK/BGP_GLOBALS_AF_NETWORK_LIST']
        for item in rmap:
            cmd_prefix = 'network '
            if ('vrf_name' in item and item['vrf_name'] == vrf_name)  and ('afi_safi' in item and item['afi_safi'] == afi_safi):
                if 'ip_prefix' in item:
                    cmd_str = cmd_str + cmd_prefix + item['ip_prefix']
                    if 'backdoor' in item:
                        cmd_str = cmd_str + ' backdoor'
                    if 'policy' in item:
                        cmd_str = cmd_str + ' route-map ' + item['policy']
                    cmd_str = cmd_str + ' ;'

    return 'CB_SUCCESS', cmd_str

def show_router_bgp_af_ag_cmd(render_tables):
    cmd_str = ''
    vrf_name = render_tables['vrf-name']
    afi_safi = render_tables['afi-safi']
    if 'sonic-bgp-global:sonic-bgp-global/BGP_GLOBALS_AF_AGGREGATE_ADDR/BGP_GLOBALS_AF_AGGREGATE_ADDR_LIST' in render_tables:
        rmap = render_tables['sonic-bgp-global:sonic-bgp-global/BGP_GLOBALS_AF_AGGREGATE_ADDR/BGP_GLOBALS_AF_AGGREGATE_ADDR_LIST']
        for item in rmap:
            cmd_prefix = 'aggregate-address '
            if ('vrf_name' in item and item['vrf_name'] == vrf_name)  and ('afi_safi' in item and item['afi_safi'] == afi_safi):
                if 'ip_prefix' in item:
                    cmd_str = cmd_str + cmd_prefix + item['ip_prefix']
                    if 'as_set' in item:
                        cmd_str = cmd_str + ' as-set'
                    if 'summary_only' in item:
                        cmd_str = cmd_str + ' summary-only'
                    if 'policy' in item:
                        cmd_str = cmd_str + ' route-map ' + item['policy']
                    cmd_str = cmd_str + ' ;'

    return 'CB_SUCCESS', cmd_str

def show_router_bgp_af_redist_cmd(render_tables):
    cmd_str = ''
    vrf_name = render_tables['vrf-name']
    afi_safi = render_tables['afi-safi']
    if 'sonic-route-common:sonic-route-common/ROUTE_REDISTRIBUTE/ROUTE_REDISTRIBUTE_LIST' in render_tables:
        rmap = render_tables['sonic-route-common:sonic-route-common/ROUTE_REDISTRIBUTE/ROUTE_REDISTRIBUTE_LIST']
        for item in rmap:
            cmd_prefix = 'redistribute'
            if ('vrf_name' in item and item['vrf_name'] == vrf_name)  and ('addr_family' in item and (item['addr_family'] in afi_safi)):
                if 'src_protocol' in item:
                    proto = item['src_protocol']
                    if proto == 'ospf3':
                       #in CLI its 'ospfv3'
                       proto = 'ospfv3'
                    cmd_str = cmd_str + cmd_prefix + ' ' + proto
                    if 'route_map' in item:
                        cmd_str = cmd_str + ' route-map'
                        for rtm in item['route_map']:
                            cmd_str = cmd_str + ' ' + rtm
                    if 'metric' in item:
                        cmd_str = cmd_str + ' metric ' + str(item['metric'])
                    cmd_str = cmd_str + ' ;'

    return 'CB_SUCCESS', cmd_str

def show_bgpcom_lists(render_tables):
  cmd_str = ''

  if 'sonic-routing-policy-sets:sonic-routing-policy-sets/COMMUNITY_SET/COMMUNITY_SET_LIST' in render_tables:
      com_list = render_tables['sonic-routing-policy-sets:sonic-routing-policy-sets/COMMUNITY_SET/COMMUNITY_SET_LIST']
      cmd_prfx = 'bgp community-list '
      for com in com_list:
          if 'set_type' in com:
              com_type = com['set_type'].lower()
              if 'name' in com:
                  name = com['name'] + " "
                  act_str = ''
                  if 'match_action' in com :
                      # show only ALL, ANY is optional, do not show
                      if com['match_action'] == "ALL":
                         act_str = " all "
                      if 'community_member' in com:
                          member_str = ''
                          asn = []
                          # For EXPANDED type, each leaf-list members will appear as
                          # separate CLI command.
                          # For STANDARD type other than multiple AA:NN, all other will
                          # be combined to single CLI command, more than one AA:NN will
                          # appear as separate CLI
                          for member in com['community_member']:
                              if com_type == "standard":
                                 if ':' in member:
                                     if ':' not in member_str:
                                         if member_str:
                                            member_str +=" "
                                         member_str += member
                                     else:
                                         # more than one AA:NN store it here and show it as
                                         # separate CLI at the end.
                                         asn.append(member)
                                 else:
                                     if member_str:
                                        member_str +=" "
                                     member_str += member
                              else:
                                  cmd_str += cmd_prfx + com_type +" " + name + member + act_str + ";"

                          if com_type == "standard":
                             cmd_str += cmd_prfx + com_type +" " + name + member_str + act_str + ";"

                             # show stored AA:NN as separate CLI
                             for member in asn:
                                 cmd_str += cmd_prfx + com_type +" " + name + member + act_str + ";"

  return 'CB_SUCCESS', cmd_str

def show_bgpextcom_lists(render_tables):
  cmd_str = ''

  if 'sonic-routing-policy-sets:sonic-routing-policy-sets/EXTENDED_COMMUNITY_SET/EXTENDED_COMMUNITY_SET_LIST' in render_tables:
      extcom_list = render_tables['sonic-routing-policy-sets:sonic-routing-policy-sets/EXTENDED_COMMUNITY_SET/EXTENDED_COMMUNITY_SET_LIST']
      cmd_prfx = 'bgp extcommunity-list '
      for extcom in extcom_list:
          if 'set_type' in extcom:
              if 'name' in extcom:
                  if 'match_action' in extcom:
                      act_str = ''
                      # ANY is optional, do not show. show only ALL
                      if extcom['match_action'] == "ALL":
                         act_str = " all "
                      if 'community_member' in extcom:
                          for member in extcom['community_member']:
                              member_str = ''
                              if 'route-target:' in member:
                                 member_str += "rt " + member[13:]
                              elif 'route-origin:' in member:
                                 member_str += "soo " + member[13:]
                              elif member:
                                 # Expanded type case
                                 member_str += member

                              cmd_str += cmd_prfx + extcom['set_type'].lower() +" " + extcom['name'] + " " + member_str + act_str + ";"

  return 'CB_SUCCESS', cmd_str

def show_bgpaspath_lists(render_tables):
  cmd_str = ''

  if 'sonic-routing-policy-sets:sonic-routing-policy-sets/AS_PATH_SET/AS_PATH_SET_LIST' in render_tables:
      aspath_list = render_tables['sonic-routing-policy-sets:sonic-routing-policy-sets/AS_PATH_SET/AS_PATH_SET_LIST']
      cmd_prfx = 'bgp as-path-list '
      for aspath in aspath_list:
          if 'name' in aspath:
              if 'as_path_set_member' in aspath:
                  for member in aspath['as_path_set_member']:
                      cmd_str += cmd_prfx + aspath['name']+ " " + member + ";"

  return 'CB_SUCCESS', cmd_str

def util_show_router_bgp_af_rt(render_tables, sonic_uri):
    cmd_str=''
    if sonic_uri in render_tables:
        cmd_prfx = "route-target"
        af_map = render_tables[sonic_uri]

        rt_imp = rt_exp = []
        if 'import-rts' in af_map:
            rt_imp = af_map['import-rts']
        if 'export-rts' in af_map:
            rt_exp = af_map['export-rts']

        if len(rt_imp) > 0:
            for rt in rt_imp:
                if len(rt_exp) > 0 and rt in rt_exp:
                    cmd_str = cmd_str + cmd_prfx + ' both ' + rt + ';'
                else:
                    cmd_str = cmd_str + cmd_prfx + ' import ' + rt + ';'

        if len(rt_exp) > 0:
            for rt in rt_exp:
                if rt not in rt_imp:
                    cmd_str = cmd_str + cmd_prfx + ' export ' + rt + ';'

    return 'CB_SUCCESS', cmd_str

def show_router_bgp_af_l2vpn_rt_cmd(render_tables):
    return util_show_router_bgp_af_rt(render_tables, 'sonic-bgp-global:sonic-bgp-global/BGP_GLOBALS_AF/BGP_GLOBALS_AF_LIST')

def show_router_bgp_af_l2vpn_vni_rt_cmd(render_tables):
    return util_show_router_bgp_af_rt(render_tables, 'sonic-bgp-global:sonic-bgp-global/BGP_GLOBALS_EVPN_VNI/BGP_GLOBALS_EVPN_VNI_LIST')
