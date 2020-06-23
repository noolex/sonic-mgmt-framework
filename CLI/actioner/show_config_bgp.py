
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

def util_show_router_bgp_af_nw_cmd(render_tables, af):
    cmd_str = ''
    if 'sonic-bgp-global:sonic-bgp-global/BGP_GLOBALS_AF_NETWORK/BGP_GLOBALS_AF_NETWORK_LIST' in render_tables:
        rmap = render_tables['sonic-bgp-global:sonic-bgp-global/BGP_GLOBALS_AF_NETWORK/BGP_GLOBALS_AF_NETWORK_LIST']
        for item in rmap:
            cmd_prefix = 'network '
            if 'afi_safi' in item and item['afi_safi'] != af:
                continue
            if 'ip_prefix' in item:
                cmd_str = cmd_str + cmd_prefix + item['ip_prefix']
                if 'backdoor' in item:
                    cmd_str = cmd_str + ' backdoor'
                if 'policy' in item:
                    cmd_str = cmd_str + ' route-map ' + item['policy']
                cmd_str = cmd_str + ' ;'

    return 'CB_SUCCESS', cmd_str

def util_show_router_bgp_af_ag_cmd(render_tables, af):
    cmd_str = ''
    if 'sonic-bgp-global:sonic-bgp-global/BGP_GLOBALS_AF_AGGREGATE_ADDR/BGP_GLOBALS_AF_AGGREGATE_ADDR_LIST' in render_tables:
        rmap = render_tables['sonic-bgp-global:sonic-bgp-global/BGP_GLOBALS_AF_AGGREGATE_ADDR/BGP_GLOBALS_AF_AGGREGATE_ADDR_LIST']
        for item in rmap:
            cmd_prefix = 'aggregate-address '
            if 'afi_safi' in item and item['afi_safi'] != af:
                continue
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

def util_show_router_bgp_af_redist_cmd(render_tables, af):
    cmd_str = ''
    if 'sonic-route-common:sonic-route-common/ROUTE_REDISTRIBUTE/ROUTE_REDISTRIBUTE_LIST' in render_tables:
        rmap = render_tables['sonic-route-common:sonic-route-common/ROUTE_REDISTRIBUTE/ROUTE_REDISTRIBUTE_LIST']
        for item in rmap:
            cmd_prefix = 'redistribute'
            if 'addr_family' in item and item['addr_family'] != af:
                continue
            if 'src_protocol' in item:
                cmd_str = cmd_str + cmd_prefix + ' ' + item['src_protocol']
                if 'route_map' in item:
                    cmd_str = cmd_str + ' route-map'
                    for rtm in item['route_map']:
                        cmd_str = cmd_str + ' ' + rtm
                if 'metric' in item:
                    cmd_str = cmd_str + ' metric ' + str(item['metric'])
                cmd_str = cmd_str + ' ;'

    return 'CB_SUCCESS', cmd_str

def show_router_bgp_af_ipv4_nw_cmd(render_tables):
    return util_show_router_bgp_af_nw_cmd(render_tables, 'ipv4_unicast')

def show_router_bgp_af_ipv4_ag_cmd(render_tables):
    return util_show_router_bgp_af_ag_cmd(render_tables, 'ipv4_unicast')

def show_router_bgp_af_ipv4_redist_cmd(render_tables):
    return util_show_router_bgp_af_redist_cmd(render_tables, 'ipv4')

def show_router_bgp_af_ipv6_nw_cmd(render_tables):
    return util_show_router_bgp_af_nw_cmd(render_tables, 'ipv6_unicast')

def show_router_bgp_af_ipv6_ag_cmd(render_tables):
    return util_show_router_bgp_af_ag_cmd(render_tables, 'ipv6_unicast')

def show_router_bgp_af_ipv6_redist_cmd(render_tables):
    return util_show_router_bgp_af_redist_cmd(render_tables, 'ipv6')
