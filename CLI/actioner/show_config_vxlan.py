###########################################################################
#
# Copyright 2019 Broadcom.  The term "Broadcom" refers to Broadcom Inc. and/or
# its subsidiaries.
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

def show_vlanvrfvnimap(render_tables):
    cmd_str = ''
    vrf_cmd_str = ''

    if 'sonic-vxlan:sonic-vxlan/VXLAN_TUNNEL_MAP/VXLAN_TUNNEL_MAP_LIST' in render_tables:
       for vlan_vni_map in render_tables['sonic-vxlan:sonic-vxlan/VXLAN_TUNNEL_MAP/VXLAN_TUNNEL_MAP_LIST']:
            cmd_str += 'map vni ' + str(vlan_vni_map['vni']) + ' ' + 'vlan ' + vlan_vni_map['vlan'].lstrip('Vlan')  + ';'
    

    if 'sonic-vrf:sonic-vrf/VRF/VRF_LIST' in render_tables:
        for vrf_vni_map in render_tables['sonic-vrf:sonic-vrf/VRF/VRF_LIST']:
            if 'vni' in vrf_vni_map and vrf_vni_map['vni'] != 0:
               vrf_cmd_str += 'map vni ' + str(vrf_vni_map['vni']) + ' ' + 'vrf ' + vrf_vni_map['vrf_name'] + ';'

    cmd_str += vrf_cmd_str
    return 'CB_SUCCESS', cmd_str
