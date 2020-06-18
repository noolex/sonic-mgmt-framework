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

from show_config_if_cmd import show_get_if_cmd

def show_routemap_setcommunity(render_tables):
    cmd_str = ''

    if 'sonic-route-map:sonic-route-map/ROUTE_MAP/ROUTE_MAP_LIST' in render_tables:
        rmap = render_tables['sonic-route-map:sonic-route-map/ROUTE_MAP/ROUTE_MAP_LIST']
        if 'set_community_inline' in rmap:
            coms = rmap['set_community_inline']
            cmd_prfx = 'set community '
            #it is leaf list, if thee is more then one means use would have
            # done using "additive". if its only one no additive is needed.
            for item in coms:
               if cmd_str:
                  cmd_str = cmd_str + cmd_prfx + item + " additive;"
               else:
                  cmd_str = cmd_str + cmd_prfx + item + ";"

    return 'CB_SUCCESS', cmd_str

def show_routemap_setextcommunity(render_tables):
    cmd_str = ''

    if 'sonic-route-map:sonic-route-map/ROUTE_MAP/ROUTE_MAP_LIST' in render_tables:
        rmap = render_tables['sonic-route-map:sonic-route-map/ROUTE_MAP/ROUTE_MAP_LIST']
        if 'set_ext_community_inline' in rmap:
            coms = rmap['set_ext_community_inline']
            for item in coms:
               #leaf list will come like "route-target:44:22,route-target:77:99"
               # remove route-target/route-origin and show"
               if 'route-target' in item:
                  cmd_str = cmd_str + "set extcommunity rt " + item[13:] + ";"
               elif 'route-origin' in item:
                  cmd_str = cmd_str + "set extcommunity soo " + item[13:] + ";"

    return 'CB_SUCCESS', cmd_str

def show_routemap_matchintf(render_tables):
    cmd_prfx = 'match interface '
    return show_get_if_cmd(render_tables,
                           'sonic-route-map:sonic-route-map/ROUTE_MAP/ROUTE_MAP_LIST',
                           'match_interface',
                           cmd_prfx)

def show_routemap_matchpeer(render_tables):
    cmd_str = ''
    if 'sonic-route-map:sonic-route-map/ROUTE_MAP/ROUTE_MAP_LIST' in render_tables:
        rmap = render_tables['sonic-route-map:sonic-route-map/ROUTE_MAP/ROUTE_MAP_LIST']
        if 'match_neighbor' in rmap:
            peers = rmap['match_neighbor']
            cmd_prfx = 'match peer '
            # even though its leaf list of peers, currently only one is supported.
            # in future if we support more than one, based on how we accept,
            # the show runn has to be changed.
            for peer in peers:
                if peer.startswith('Eth'):
                   cmd_str = cmd_prfx + peer
                elif peer.startswith('Vlan'):
                   intf_split = peer.split('Vlan')
                   cmd_str = cmd_prfx + 'Vlan ' + intf_split[1]
                elif peer.startswith('PortChannel'):
                   intf_split = peer.split('PortChannel')
                   cmd_str = cmd_prfx +  'PortChannel ' + intf_split[1]
                elif len(peer) > 0:
                   cmd_str = cmd_prfx + peer
                else:
                   pass

    return 'CB_SUCCESS', cmd_str

def show_routemap_matchtag(render_tables):
    cmd_str = ''
    if 'sonic-route-map:sonic-route-map/ROUTE_MAP/ROUTE_MAP_LIST' in render_tables:
        rmap = render_tables['sonic-route-map:sonic-route-map/ROUTE_MAP/ROUTE_MAP_LIST']
        if 'match_tag' in rmap:
            tags = rmap['match_tag']
            cmd_prfx = 'match tag '
            # even though its leaf list of tags, currently only one is supported.
            # in future if we support more than one, based on how we accept,
            # the show runn has to be changed.
            for tag in tags:
                cmd_str = cmd_prfx + str(tag)

    return 'CB_SUCCESS', cmd_str

