def show_pim_ipv4_gbl(render_tables):
    cmd_list = ''

    if 'sonic-pim:sonic-pim/PIM_GLOBALS/PIM_GLOBALS_LIST' in render_tables:
        for vrf_inst in render_tables['sonic-pim:sonic-pim/PIM_GLOBALS/PIM_GLOBALS_LIST']:
            if 'vrf-name' not in vrf_inst: continue
            if not ((vrf_inst['vrf-name'] == 'default') or (vrf_inst['vrf-name'].find('Vrf') == 0)): continue
            if 'address-family' not in vrf_inst: continue
            if (vrf_inst['address-family'] != 'ipv4'): continue
            vrf_inst_cmd_prfx = 'ip pim vrf ' + vrf_inst['vrf-name']
            cmd_delimiter = ';'
            if 'join-prune-interval' in vrf_inst:
                cmd_str = vrf_inst_cmd_prfx + ' join-prune-interval ' + str(vrf_inst['join-prune-interval'])
                cmd_list += cmd_str + cmd_delimiter
            if 'keep-alive-timer' in vrf_inst:
                cmd_str = vrf_inst_cmd_prfx + ' keep-alive-timer ' + str(vrf_inst['keep-alive-timer'])
                cmd_list += cmd_str + cmd_delimiter
            if 'ssm-ranges' in vrf_inst:
                cmd_str = vrf_inst_cmd_prfx + ' ssm prefix-list ' + vrf_inst['ssm-ranges']
                cmd_list += cmd_str + cmd_delimiter
            if 'ecmp-enabled' in vrf_inst and vrf_inst['ecmp-enabled'] == True:
                cmd_str = vrf_inst_cmd_prfx + ' ecmp'
                cmd_list += cmd_str + cmd_delimiter
            if 'ecmp-rebalance-enabled' in vrf_inst and vrf_inst['ecmp-rebalance-enabled'] == True:
                cmd_str = vrf_inst_cmd_prfx + ' ecmp rebalance'
                cmd_list += cmd_str + cmd_delimiter

    return 'CB_SUCCESS', cmd_list
