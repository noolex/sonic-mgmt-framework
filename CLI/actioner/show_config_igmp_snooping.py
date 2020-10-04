###########################################################################
#
# Copyright 2020 Broadcom.  The term "Broadcom" refers to Broadcom Inc. and/or
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

def show_igmp_snooping_intf_config(render_tables):
    cmd_str = ''
    cmd_end = ';'
    cmd_prefix = 'ip igmp snooping'
    vlan_key = ''
    if 'name' in render_tables:
        vlan_key = render_tables['name']

    if 'sonic-igmp-snooping:sonic-igmp-snooping/CFG_L2MC_TABLE/CFG_L2MC_TABLE_LIST' in render_tables:
        igmps_intfs = render_tables['sonic-igmp-snooping:sonic-igmp-snooping/CFG_L2MC_TABLE/CFG_L2MC_TABLE_LIST']
        for igmps in igmps_intfs:
            if vlan_key == igmps['vlan-name']:
                if 'enabled' in igmps:
                    cmd_str += cmd_prefix + cmd_end
                if 'querier' in igmps and igmps['querier'] == True:
                    cmd_str += cmd_prefix + ' querier' + cmd_end
                if 'fast-leave' in igmps and igmps['fast-leave'] == True:
                    cmd_str += cmd_prefix + ' fast-leave' + cmd_end
                if 'query-interval' in igmps:
                    cmd_str += cmd_prefix + ' query-interval {}'.format(igmps['query-interval']) + cmd_end
                if 'last-member-query-interval' in igmps:
                    cmd_str += cmd_prefix + ' last-member-query-interval {}'.format(igmps['last-member-query-interval']) + cmd_end
                if 'query-max-response-time' in igmps:
                    cmd_str += cmd_prefix + ' query-max-response-time {}'.format(igmps['query-max-response-time']) + cmd_end
                if 'version' in igmps:
                    cmd_str += cmd_prefix + ' version {}'.format(igmps['version']) + cmd_end
    
    status, sub_cmd_str = show_mrouterports(render_tables, vlan_key, cmd_prefix)
    if status == 'CB_SUCCESS' :
        cmd_str += sub_cmd_str + cmd_end
    
    status, sub_cmd_str = show_multicast_static_grps(render_tables, vlan_key, cmd_prefix)
    if status == 'CB_SUCCESS' :
        cmd_str += sub_cmd_str + cmd_end

    return 'CB_SUCCESS', cmd_str

def show_mrouterports(render_tables, vlan_key, cmd_prefix):
    cmd_str = ''
    cmd_end = ';'

    if 'sonic-igmp-snooping:sonic-igmp-snooping/CFG_L2MC_MROUTER_TABLE/CFG_L2MC_MROUTER_TABLE_LIST' in render_tables:
        mrouter_intfs = render_tables['sonic-igmp-snooping:sonic-igmp-snooping/CFG_L2MC_MROUTER_TABLE/CFG_L2MC_MROUTER_TABLE_LIST']
        for mrouter in mrouter_intfs:
            if vlan_key == mrouter['vlan-name']:
                cmd_str += cmd_prefix + ' mrouter interface ' + str(mrouter['mrouter-intf']) + cmd_end
    return 'CB_SUCCESS', cmd_str

def show_multicast_static_grps(render_tables, vlan_key, cmd_prefix):
    cmd_str = ''
    cmd_end = ';'

    if 'sonic-igmp-snooping:sonic-igmp-snooping/CFG_L2MC_STATIC_MEMBER_TABLE/CFG_L2MC_STATIC_MEMBER_TABLE_LIST' in render_tables:
        igmpgrps = render_tables['sonic-igmp-snooping:sonic-igmp-snooping/CFG_L2MC_STATIC_MEMBER_TABLE/CFG_L2MC_STATIC_MEMBER_TABLE_LIST']
        for igmpgrp in igmpgrps:
            if vlan_key == igmpgrp['vlan-name']:
                cmd_str += cmd_prefix + ' static-group ' + igmpgrp['group-addr'] + ' interface ' + str(igmpgrp['out-intf']) + cmd_end
    return 'CB_SUCCESS', cmd_str
