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

# Route map related
def show_routemap_setcommunity(render_tables):
    cmd_str = ''

    if 'sonic-route-map:sonic-route-map/ROUTE_MAP/ROUTE_MAP_LIST' in render_tables:
        rmap = render_tables['sonic-route-map:sonic-route-map/ROUTE_MAP/ROUTE_MAP_LIST']
        if 'set_community_inline' in rmap:
            coms = rmap['set_community_inline']
            cmd_str = 'set community ' + ' '.join(coms)  

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


# IPv4/IPv6 prefix lists related

def show_prefix_lists(render_tables, ip_mode):
    cmd_str = ''
    temp = {}
    # Fetch IPv4 or Ipv6 mode and store from PREFIX_SET_LIST table and then filter PREFIX_LIST
    if 'sonic-routing-policy-sets:sonic-routing-policy-sets/PREFIX_SET/PREFIX_SET_LIST' in render_tables:
        prefix_set = render_tables['sonic-routing-policy-sets:sonic-routing-policy-sets/PREFIX_SET/PREFIX_SET_LIST']
        for temp_prefix in prefix_set:
            name = temp_prefix["name"]
            if 'mode' in temp_prefix:
               temp[name] = temp_prefix["mode"]

    if 'sonic-routing-policy-sets:sonic-routing-policy-sets/PREFIX/PREFIX_LIST' in render_tables:
        prefix_list = render_tables['sonic-routing-policy-sets:sonic-routing-policy-sets/PREFIX/PREFIX_LIST']
        for prefix in prefix_list:
            mode = ''
            mask_range_str = ''
            prefix_name = prefix["set_name"]

            # Display only IP or IPv6 prefixes based on request.
            if temp[prefix_name] != ip_mode:
               continue
            if temp[prefix_name] == "IPv4":
               cmd_prfx = 'ip prefix-list '
            elif temp[prefix_name] == "IPv6":
               cmd_prfx = 'ipv6 prefix-list '
            else:
               continue

            mask_range = prefix['masklength_range']

            if 'action' in prefix:
                if mask_range != "exact":
                   prefix_val = prefix['ip_prefix'].split("/")
                   mask_range_val = prefix['masklength_range'].split("..")
                   if prefix_val[1] == mask_range_val[0]:
                      mask_range_str = " le " + mask_range_val[1]
                   else:
                      mask_range_str = " ge " + mask_range_val[0] + " le " + mask_range_val[1]

                cmd_str = cmd_str + cmd_prfx + prefix['set_name'] + " " + prefix['action'] + " " + prefix['ip_prefix'] + mask_range_str + ";" ;

    return 'CB_SUCCESS', cmd_str

def show_v4prefix_lists(render_tables):
    return show_prefix_lists(render_tables, "IPv4")

def show_v6prefix_lists(render_tables):
    return show_prefix_lists(render_tables, "IPv6")
