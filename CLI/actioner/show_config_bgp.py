
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
