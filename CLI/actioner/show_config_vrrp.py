###########################################################################
#
# Copyright 2020 Broadcom. The term Broadcom refers to Broadcom Inc. and/or
# its subsidiaries.
#
###########################################################################

def show_vrrp_track_config(render_tables, table_inst, afi):
    cmd_str = ''

    if 'sonic-vrrp:sonic-vrrp' in render_tables:
        if 'VRRP_TRACK' in render_tables['sonic-vrrp:sonic-vrrp'] and afi == 'ipv4':
            if 'VRRP_TRACK_LIST' in render_tables['sonic-vrrp:sonic-vrrp']['VRRP_TRACK']:
                track_all_inst = render_tables['sonic-vrrp:sonic-vrrp']['VRRP_TRACK']['VRRP_TRACK_LIST']
        elif 'VRRP6_TRACK' in render_tables['sonic-vrrp:sonic-vrrp'] and afi == 'ipv6':
            if 'VRRP6_TRACK_LIST' in render_tables['sonic-vrrp:sonic-vrrp']['VRRP6_TRACK']:
                track_all_inst = render_tables['sonic-vrrp:sonic-vrrp']['VRRP6_TRACK']['VRRP6_TRACK_LIST']
        else:
            return cmd_str

    for track_inst in track_all_inst:
        if table_inst['ifname'] != track_inst['baseifname']:
            continue
        if table_inst['vrid'] != track_inst['idkey']:
            continue

        cmd_str += ' track-interface ' + track_inst['trackifname'] + ' weight ' +  str(track_inst['priority_increment']) + ';'

    return cmd_str

def show_vrrp_common(render_table, table_inst, afi):
    cmd_str = ''
    if 'priority' in table_inst:
        cmd_str += ' priority ' + str(table_inst['priority']) + ';'
    if 'pre_empt' in table_inst:
        if 'True' == table_inst['pre_empt']:
            cmd_str += ' preempt ' + ';'
        else:
            cmd_str += ' no preempt ' + ';'
    if 'version' in table_inst:
        cmd_str += ' version ' + str(table_inst['version']) + ';'
    if 'adv_interval' in table_inst:
        cmd_str += ' advertisement-interval ' + str(table_inst['adv_interval']) + ';'
    if 'vip' in table_inst:
        vips = table_inst['vip']
        for vip in vips:
            cmd_str += ' vip ' + str(vip) + ';'

    cmd_str += show_vrrp_track_config(render_table, table_inst, afi)

    return cmd_str


def show_vrrp_config(render_tables):
    cmd_str = ''

    ifname = render_tables['name']
    if 'sonic-vrrp:sonic-vrrp/VRRP/VRRP_LIST' in render_tables:

        table_all_inst = render_tables['sonic-vrrp:sonic-vrrp/VRRP/VRRP_LIST']

        for table_inst in table_all_inst:

            if ifname != table_inst['ifname']:
                continue

            cmd_prefix = 'vrrp'
            if 'vrid' in table_inst:
                cmd_str += cmd_prefix + ' ' + str(table_inst['vrid']) + ' address-family ipv4' + ';'
                cmd_str += show_vrrp_common(render_tables, table_inst, 'ipv4')

    if 'sonic-vrrp:sonic-vrrp/VRRP6/VRRP6_LIST' in render_tables:

        table_all_inst = render_tables['sonic-vrrp:sonic-vrrp/VRRP6/VRRP6_LIST']

        for table_inst in table_all_inst:

            if ifname != table_inst['ifname']:
                continue

            cmd_prefix = 'vrrp'
            if 'vrid' in table_inst:
                cmd_str += cmd_prefix + ' ' + str(table_inst['vrid']) + ' address-family ipv6' + ';'
                cmd_str += show_vrrp_common(render_tables, table_inst, 'ipv6')

    return 'CB_SUCCESS', cmd_str
