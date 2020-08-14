###########################################################################
#
# Copyright 2020 Broadcom. The term Broadcom refers to Broadcom Inc. and/or
# its subsidiaries.
#
###########################################################################


def show_sag4_config(render_tables):
    cmd_str = ''

    if 'sonic-vlan:sonic-vlan/VLAN/VLAN_LIST' in render_tables:

        ifname = render_tables['name']

        if 'sonic-sag:sonic-sag/SAG/SAG_LIST' in render_tables:
            table_all_inst = render_tables['sonic-sag:sonic-sag/SAG/SAG_LIST']

            for table_inst in table_all_inst:

                if ifname != table_inst['ifname']:
                    continue

                if 'IPv4' != table_inst['table_distinguisher']:
                    continue

                if 'gwip' in table_inst:
                    gwips = table_inst['gwip']
                    for gwip in gwips:
                        cmd_str += 'ip anycast-address ' + str(gwip) + ';'

    return 'CB_SUCCESS', cmd_str

def show_sag6_config(render_tables):
    cmd_str = ''

    if 'sonic-vlan:sonic-vlan/VLAN/VLAN_LIST' in render_tables:

        ifname = render_tables['name']

        if 'sonic-sag:sonic-sag/SAG/SAG_LIST' in render_tables:
            table_all_inst = render_tables['sonic-sag:sonic-sag/SAG/SAG_LIST']

            for table_inst in table_all_inst:

                if ifname != table_inst['ifname']:
                    continue

                if 'IPv6' != table_inst['table_distinguisher']:
                    continue

                if 'gwip' in table_inst:
                    gwips = table_inst['gwip']
                    for gwip in gwips:
                        cmd_str += 'ipv6 anycast-address ' + str(gwip) + ';'

    return 'CB_SUCCESS', cmd_str

def show_sag4_global(render_tables):
    cmd_str = ''

    if 'sonic-sag:sonic-sag/SAG_GLOBAL/SAG_GLOBAL_LIST' in render_tables:
        sag_global_all = render_tables['sonic-sag:sonic-sag/SAG_GLOBAL/SAG_GLOBAL_LIST']

        for sag_global in sag_global_all:
            if 'IPv4' in sag_global:
                if 'enable' == sag_global['IPv4']:
                    cmd_str = 'ip anycast-address enable'

    return 'CB_SUCCESS', cmd_str

def show_sag6_global(render_tables):
    cmd_str = ''

    if 'sonic-sag:sonic-sag/SAG_GLOBAL/SAG_GLOBAL_LIST' in render_tables:
        sag_global_all = render_tables['sonic-sag:sonic-sag/SAG_GLOBAL/SAG_GLOBAL_LIST']

        for sag_global in sag_global_all:
            if 'IPv6' in sag_global:
                if 'enable' == sag_global['IPv6']:
                    cmd_str = 'ipv6 anycast-address enable'

    return 'CB_SUCCESS', cmd_str
