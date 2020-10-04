###########################################################################
#
# Copyright 2020 Broadcom. The term Broadcom refers to Broadcom Inc. and/or
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

cfgmap = {
    'polling_interval'                    : 'crm polling interval',
    'acl_group_threshold_type'            : 'crm thresholds acl group type',
    'acl_group_high_threshold'            : 'crm thresholds acl group high',
    'acl_group_low_threshold'             : 'crm thresholds acl group low',
    'acl_counter_threshold_type'          : 'crm thresholds acl group counter type',
    'acl_counter_high_threshold'          : 'crm thresholds acl group counter high',
    'acl_counter_low_threshold'           : 'crm thresholds acl group counter low',
    'acl_entry_threshold_type'            : 'crm thresholds acl group entry type',
    'acl_entry_high_threshold'            : 'crm thresholds acl group entry high',
    'acl_entry_low_threshold'             : 'crm thresholds acl group entry low',
    'acl_table_threshold_type'            : 'crm thresholds acl table type',
    'acl_table_high_threshold'            : 'crm thresholds acl table high',
    'acl_table_low_threshold'             : 'crm thresholds acl table low',
    'dnat_entry_threshold_type'           : 'crm thresholds dnat type',
    'dnat_entry_high_threshold'           : 'crm thresholds dnat high',
    'dnat_entry_low_threshold'            : 'crm thresholds dnat low',
    'fdb_entry_threshold_type'            : 'crm thresholds fdb type',
    'fdb_entry_high_threshold'            : 'crm thresholds fdb high',
    'fdb_entry_low_threshold'             : 'crm thresholds fdb low',
    'ipmc_entry_threshold_type'           : 'crm thresholds ipmc type',
    'ipmc_entry_high_threshold'           : 'crm thresholds ipmc high',
    'ipmc_entry_low_threshold'            : 'crm thresholds ipmc low',
    'ipv4_neighbor_threshold_type'        : 'crm thresholds ipv4 neighbor type',
    'ipv4_neighbor_high_threshold'        : 'crm thresholds ipv4 neighbor high',
    'ipv4_neighbor_low_threshold'         : 'crm thresholds ipv4 neighbor low',
    'ipv4_nexthop_threshold_type'         : 'crm thresholds ipv4 nexthop type',
    'ipv4_nexthop_high_threshold'         : 'crm thresholds ipv4 nexthop high',
    'ipv4_nexthop_low_threshold'          : 'crm thresholds ipv4 nexthop low',
    'ipv4_route_threshold_type'           : 'crm thresholds ipv4 route type',
    'ipv4_route_high_threshold'           : 'crm thresholds ipv4 route high',
    'ipv4_route_low_threshold'            : 'crm thresholds ipv4 route low',
    'ipv6_neighbor_threshold_type'        : 'crm thresholds ipv6 neighbor type',
    'ipv6_neighbor_high_threshold'        : 'crm thresholds ipv6 neighbor high',
    'ipv6_neighbor_low_threshold'         : 'crm thresholds ipv6 neighbor low',
    'ipv6_nexthop_threshold_type'         : 'crm thresholds ipv6 nexthop type',
    'ipv6_nexthop_high_threshold'         : 'crm thresholds ipv6 nexthop high',
    'ipv6_nexthop_low_threshold'          : 'crm thresholds ipv6 nexthop low',
    'ipv6_route_threshold_type'           : 'crm thresholds ipv6 route type',
    'ipv6_route_high_threshold'           : 'crm thresholds ipv6 route high',
    'ipv6_route_low_threshold'            : 'crm thresholds ipv6 route low',
    'nexthop_group_member_threshold_type' : 'crm thresholds nexthop group member type',
    'nexthop_group_member_high_threshold' : 'crm thresholds nexthop group member high',
    'nexthop_group_member_low_threshold'  : 'crm thresholds nexthop group member low',
    'nexthop_group_threshold_type'        : 'crm thresholds nexthop group object type',
    'nexthop_group_high_threshold'        : 'crm thresholds nexthop group object high',
    'nexthop_group_low_threshold'         : 'crm thresholds nexthop group object low',
    'snat_entry_threshold_type'           : 'crm thresholds snat type',
    'snat_entry_high_threshold'           : 'crm thresholds snat high',
    'snat_entry_low_threshold'            : 'crm thresholds snat low'
}

def get_crm_config(info, field, prefix):
    cfg_str = ""
    if field in info:
        cfg_str = "{0} {1}".format(prefix, info[field])
    return cfg_str

def show_crm_config(render_tables):
    info = {}
    conf = []

    # skip if render_tables is None
    if render_tables is None:
        return 'CB_SUCCESS', ''

    if 'sonic-system-crm:sonic-system-crm/CRM' in render_tables:
        if 'CRM_LIST' in render_tables['sonic-system-crm:sonic-system-crm/CRM']:
            info = render_tables['sonic-system-crm:sonic-system-crm/CRM']['CRM_LIST'][0]

    # skip if render_tables['sonic-system-crm:sonic-system-crm/CRM']['CRM_LIST'][0] is not available
    if not info:
        return 'CB_SUCCESS', ''

    # sort dictionary by value (i.e. config command)
    for field, prefix in sorted(cfgmap.items(), key=lambda x: x[1]):
        cmd = get_crm_config(info, field, prefix)
        if len(cmd) > 0:
            conf.append(cmd)

    return 'CB_SUCCESS', "\n".join(conf)
