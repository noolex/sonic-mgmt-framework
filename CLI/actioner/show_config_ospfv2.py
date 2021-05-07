###########################################################################
#
# Copyright 2020 Broadcom. The term Broadcom refers to Broadcom Inc. and/or
# its subsidiaries.
#
###########################################################################

from show_config_if_cmd import show_get_if_cmd

ospf_debug_log_config = False

def ospf_debug_log_enable() :
    global ospf_debug_log_config
    ospf_debug_log_config = True

def ospf_debug_log_disable() :
    global ospf_debug_log_config
    ospf_debug_log_config = False

def ospf_debug_print(prt_Str) :
    global ospf_debug_log_config
    if ospf_debug_log_config :
       print(prt_Str)

def ospf_get_key_value(in_map, key_name) :
    if key_name == None or key_name == '' :
        return False, key_name, 'Key name empty'
    if in_map == None :
        return False, key_name, 'Record map null'
    if key_name not in in_map :
        return False, key_name, 'Key not found'
    return True, key_name, in_map[key_name]

def ospf_generate_command(in_map, key_name, cmd_prefix, match_value={}, cmd_suffix=' ;') :
    cmd_str = ''
    if in_map == None :
        return ''
    if key_name == None or key_name == '' :
        return ''

    #ospf_debug_print("ospf_generate_command: key {} inmap {} ".format(key_name, in_map))
    if key_name in in_map :
        if len(match_value) :
            for key, value in list(match_value.items()) :
                if in_map[key_name] == key :
                    if value != '' :
                        cmd_str = '{} {} {}'.format(cmd_prefix, value, cmd_suffix)
                    else :
                        cmd_str = '{} {}'.format(cmd_prefix, cmd_suffix)
        else :
            value = in_map[key_name]
            cmd_str = '{} {} {}'.format(cmd_prefix, value, cmd_suffix)

    return cmd_str


def show_router_ospf_config(render_tables):
    cmd_str = ''
    cmd_end = ' ;'

    #ospf_debug_log_disable()
    #ospf_debug_log_enable()
    ospf_debug_print("show_router_ospf_config: render_tables {}".format(render_tables))

    present, name, vrf_name = ospf_get_key_value(render_tables, 'vrf-name')
    if present == False :
        ospf_debug_print("show_router_ospf_config: vrf_name not present ")
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_router_ospf_config: vrf_name {} present".format(vrf_name))

    tbl_path = 'sonic-ospfv2:sonic-ospfv2/OSPFV2_ROUTER/OSPFV2_ROUTER_LIST'
    present, tbl_path, tbl_rec_list = ospf_get_key_value(render_tables, tbl_path)
    if present == False :
        ospf_debug_print("show_router_ospf_config: OSPFV2_ROUTER_LIST not Found ")
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_router_ospf_config: OSPFV2_ROUTER_LIST present {}".format(tbl_rec_list))

    if not isinstance(tbl_rec_list, list) :
        tbl_rec_list = [ tbl_rec_list ]

    for tbl_rec in tbl_rec_list :
        vrf_p, _, vrf_v = ospf_get_key_value(tbl_rec, 'vrf_name')
        if vrf_v != 'default':
            cmd_str += 'router ospf vrf ' + vrf_v + cmd_end
        else :
            cmd_str += 'router ospf ' + cmd_end

        cmd_str += ospf_generate_command(tbl_rec, 'router-id', ' ospf router-id')

        match_value = { 'CISCO' : 'cisco', 'IBM' : 'ibm', 'SHORTCUT': 'shortcut', 'STANDARD' : 'standard' }
        cmd_str += ospf_generate_command(tbl_rec, 'abr-type', ' ospf abr-type', match_value=match_value)

        cmd_str += ospf_generate_command(tbl_rec, 'auto-cost-reference-bandwidth', ' auto-cost reference-bandwidth')

        match_value = { True : '' }
        cmd_str += ospf_generate_command(tbl_rec, 'ospf-rfc1583-compatible', ' compatible rfc1583', match_value=match_value)

        cmd_str += ospf_generate_command(tbl_rec, 'default-metric', ' default-metric')

        cmd_str += ospf_generate_command(tbl_rec, 'distance-all',  ' distance')

        dist_intra, _, dist_intra_value = ospf_get_key_value(tbl_rec, 'distance-intra-area')
        dist_inter, _, dist_inter_value = ospf_get_key_value(tbl_rec, 'distance-inter-area')
        dist_extrn, _, dist_extrn_value = ospf_get_key_value(tbl_rec, 'distance-external')
        if dist_intra or dist_inter or dist_extrn :
            cmd_str += ' distance ospf'
            if dist_intra :
                cmd_str += ' intra-area {}'.format(dist_intra_value)
            if dist_inter :
                cmd_str += ' inter-area {}'.format(dist_inter_value)
            if dist_extrn :
                cmd_str += ' external {}'.format(dist_extrn_value)
            cmd_str += cmd_end

        match_value = { 'BRIEF' : '', 'DETAIL' : 'detail' }
        cmd_str += ospf_generate_command(tbl_rec, 'log-adjacency-changes', ' log-adjacency-changes', match_value=match_value)

        match_value = { True : 'administrative' }
        cmd_str += ospf_generate_command(tbl_rec, 'max-metric-administrative', ' max-metric router-lsa', match_value=match_value)
        cmd_str += ospf_generate_command(tbl_rec, 'max-metric-on-shutdown', ' max-metric router-lsa on-shutdown')
        cmd_str += ospf_generate_command(tbl_rec, 'max-metric-on-startup',  ' max-metric router-lsa on-startup')

        match_value = { True : 'default' }
        cmd_str += ospf_generate_command(tbl_rec, 'passive-interface-default', ' passive-interface', match_value=match_value)

        cmd_str += ospf_generate_command(tbl_rec, 'lsa-refresh-timer',  ' refresh timer')

        spf_throttle, _, spf_throttle_value = ospf_get_key_value(tbl_rec, 'spf-throttle-delay')
        spf_initial, _, spf_initial_value = ospf_get_key_value(tbl_rec, 'spf-initial-delay')
        spf_maximum, _, spf_maximum_value = ospf_get_key_value(tbl_rec, 'spf-maximum-delay')
        if (spf_throttle or spf_initial or spf_maximum) :
            if spf_throttle == False : spf_throttle_value = '0'
            if spf_throttle == False : spf_initial_value = '50'
            if spf_maximum == False : spf_maximum_value = '5000'
            cmd_str += ' timers throttle spf {} {} {}'.format(spf_throttle_value, spf_initial_value, spf_maximum_value)
            cmd_str += cmd_end

        cmd_str += ospf_generate_command(tbl_rec, 'lsa-min-interval-timer', ' timers throttle lsa all')

        cmd_str += ospf_generate_command(tbl_rec, 'lsa-min-arrival-timer', ' timers lsa min-arrival')

        cmd_str += ospf_generate_command(tbl_rec, 'write-multiplier', ' write-multiplier')

    status, sub_cmd_str = show_router_ospf_distribute_route_config(render_tables)
    if status == 'CB_SUCCESS' :
        cmd_str += sub_cmd_str

    ospf_debug_print("show_router_ospf_config: cmd_str {}".format(cmd_str))
    return 'CB_SUCCESS', cmd_str


def show_router_ospf_passive_interface_config(render_tables):
    cmd_str = ''
    cmd_end = ' ;'

    #ospf_debug_log_enable()
    #ospf_debug_log_disable()
    ospf_debug_print("show_router_ospf_passive_interface_config: render_tables {}".format(render_tables))

    present, name, vrf_name = ospf_get_key_value(render_tables, 'vrf-name')
    if present == False :
        ospf_debug_print("show_router_ospf_passive_interface_config: vrf_name not present")
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_router_ospf_passive_interface_config: vrf_name {} present".format(vrf_name))

    tbl_path = 'sonic-ospfv2:sonic-ospfv2/OSPFV2_ROUTER_PASSIVE_INTERFACE/OSPFV2_ROUTER_PASSIVE_INTERFACE_LIST'
    present, tbl_path, tbl_rec_list = ospf_get_key_value(render_tables, tbl_path)
    if present == False :
        ospf_debug_print("show_router_ospf_passive_interface_config: PASSIVE_INTERFACE_LIST not present")
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_router_ospf_passive_interface_config: PASSIVE_INTERFACE_LIST {}".format(tbl_rec_list))

    if not isinstance(tbl_rec_list, list) :
        tbl_rec_list = [ tbl_rec_list ]

    for tbl_rec in tbl_rec_list :
        vrf_p, _, vrf_v = ospf_get_key_value(tbl_rec, 'vrf_name')
        if vrf_p == False :
            ospf_debug_print("show_router_ospf_passive_interface_config: vrf field not present")
            continue

        if vrf_v != vrf_name :
            ospf_debug_print("show_router_ospf_passive_interface_config: vrf names {} != {}".format(vrf_v, vrf_name))
            continue

        intf_p, _, intf_v = ospf_get_key_value(tbl_rec, 'name')
        addr_p, _, addr_v = ospf_get_key_value(tbl_rec, 'address')
        nonp_p, _, nonp_v = ospf_get_key_value(tbl_rec, 'non-passive')

        temp_cmd = ''
        if intf_p :
           temp_cmd += 'passive-interface {}'.format(intf_v)
           if addr_p and addr_v != '' and addr_v != '0.0.0.0' :
               temp_cmd += ' {}'.format(addr_v)
           if nonp_p and nonp_v == True :
               temp_cmd += ' non-passive'

           cmd_str += temp_cmd + cmd_end


    ospf_debug_print("show_router_ospf_passive_interface_config: cmd_str {}".format(cmd_str))
    return 'CB_SUCCESS', cmd_str



def show_router_ospf_area_config(render_tables):
    cmd_str = ''
    cmd_end = ' ;'

    #ospf_debug_log_enable()
    #ospf_debug_log_disable()
    ospf_debug_print("show_router_ospf_area_config: render_tables {}".format(render_tables))

    present, name, vrf_name = ospf_get_key_value(render_tables, 'vrf-name')
    if present == False :
        ospf_debug_print("show_router_ospf_area_config: vrf_name not present")
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_router_ospf_area_config: vrf_name {} present".format(vrf_name))

    tbl_path = 'sonic-ospfv2:sonic-ospfv2/OSPFV2_ROUTER_AREA/OSPFV2_ROUTER_AREA_LIST'
    present, tbl_path, tbl_rec_list = ospf_get_key_value(render_tables, tbl_path)
    if present == False :
        ospf_debug_print("show_router_ospf_area_config: AREA_LIST not present")
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_router_ospf_area_config: AREA_LIST {}".format(tbl_rec_list))

    if not isinstance(tbl_rec_list, list) :
        tbl_rec_list = [ tbl_rec_list ]

    for tbl_rec in tbl_rec_list :
        vrf_p, _, vrf_v = ospf_get_key_value(tbl_rec, 'vrf_name')
        if vrf_p == False :
            ospf_debug_print("show_router_ospf_area_config: vrf field not present")
            continue

        if vrf_v != vrf_name :
            ospf_debug_print("show_router_ospf_area_config: vrf names {} != {}".format(vrf_v, vrf_name))
            continue

        area_p, _, area_v = ospf_get_key_value(tbl_rec, 'area-id')
        if area_p == False:
            continue

        cmd_str_len = len(cmd_str)
        cmd_area_prefix = 'area {}'.format(area_v)

        match_value = { 'TEXT' : '', 'MD5HMAC' : 'message-digest' }
        cmd_prefix = cmd_area_prefix + ' authentication'
        cmd_str += ospf_generate_command(tbl_rec, 'authentication', cmd_prefix, match_value=match_value)

        match_value = { True : 'no-summary' }
        cmd_prefix = cmd_area_prefix + ' stub'
        temp_str = ospf_generate_command(tbl_rec, 'stub-no-summary', cmd_prefix, match_value=match_value)
        if temp_str != '' :
            cmd_str += temp_str
        else :
            match_value = { True : 'stub' }
            cmd_str += ospf_generate_command(tbl_rec, 'stub', cmd_area_prefix, match_value=match_value)

        cmd_prefix = cmd_area_prefix + ' default-cost'
        cmd_str += ospf_generate_command(tbl_rec, 'stub-default-cost', cmd_prefix)

        cmd_prefix = cmd_area_prefix + ' filter-list prefix'
        cmd_suffix = 'in' + cmd_end
        cmd_str += ospf_generate_command(tbl_rec, 'filter-list-in', cmd_prefix, cmd_suffix=cmd_suffix)

        cmd_prefix = cmd_area_prefix + ' filter-list prefix'
        cmd_suffix = 'out' + cmd_end
        cmd_str += ospf_generate_command(tbl_rec, 'filter-list-out', cmd_prefix, cmd_suffix=cmd_suffix)

        cmd_prefix = cmd_area_prefix + ' shortcut'
        match_value = { 'ENABLE' : 'enable', 'DISABLE' : 'disable', 'DEFAULT' : 'default'}
        cmd_str += ospf_generate_command(tbl_rec, 'shortcut', cmd_prefix, match_value=match_value)

        if cmd_str_len == len(cmd_str) :
            cmd_str += cmd_area_prefix + cmd_end

    status, sub_cmd_str = show_router_ospf_area_vlink_config(render_tables)
    if status == 'CB_SUCCESS' :
        cmd_str += sub_cmd_str

    status, sub_cmd_str = show_router_ospf_area_addr_range_config(render_tables)
    if status == 'CB_SUCCESS' :
        cmd_str += sub_cmd_str

    ospf_debug_print("show_router_ospf_area_config: cmd_str {}".format(cmd_str))
    return 'CB_SUCCESS', cmd_str


def show_router_ospf_area_network_config(render_tables):
    cmd_str = ''
    cmd_end = ' ;'

    #ospf_debug_log_enable()
    #ospf_debug_log_disable()
    ospf_debug_print("show_router_ospf_area_network_config: render_tables {}".format(render_tables))

    present, name, vrf_name = ospf_get_key_value(render_tables, 'vrf-name')
    if present == False :
        ospf_debug_print("show_router_ospf_area_network_config: vrf_name not present")
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_router_ospf_area_network_config: vrf_name {} present".format(vrf_name))

    tbl_path = 'sonic-ospfv2:sonic-ospfv2/OSPFV2_ROUTER_AREA_NETWORK/OSPFV2_ROUTER_AREA_NETWORK_LIST'
    present, tbl_path, tbl_rec_list = ospf_get_key_value(render_tables, tbl_path)
    if present == False :
        ospf_debug_print("show_router_ospf_area_network_config: AREA_NETWORK_LIST not present")
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_router_ospf_area_network_config: AREA_NETWORK_LIST {}".format(tbl_rec_list))

    if not isinstance(tbl_rec_list, list) :
        tbl_rec_list = [ tbl_rec_list ]

    for tbl_rec in tbl_rec_list :
        vrf_p, _, vrf_v = ospf_get_key_value(tbl_rec, 'vrf_name')
        if vrf_p == False :
            ospf_debug_print("show_router_ospf_area_network_config: vrf field not present")
            continue

        if vrf_v != vrf_name :
            ospf_debug_print("show_router_ospf_area_network_config: vrf names {} != {}".format(vrf_v, vrf_name))
            continue

        area_p, _, area_v = ospf_get_key_value(tbl_rec, 'area-id')
        if area_p == False :
            continue

        prefix_p, _, prefix_v = ospf_get_key_value(tbl_rec, 'prefix')
        if prefix_p :
            cmd_str += 'network {} area {}'.format(prefix_v, area_v)
            cmd_str += cmd_end

    ospf_debug_print("show_router_ospf_area_network_config: cmd_str {}".format(cmd_str))
    return 'CB_SUCCESS', cmd_str


def show_router_ospf_area_vlink_config(render_tables):
    cmd_str = ''
    cmd_end = ' ;'

    #ospf_debug_log_enable()
    #ospf_debug_log_disable()

    ospf_debug_print("show_router_ospf_area_vlink_config: render_tables {}".format(render_tables))

    present, name, vrf_name = ospf_get_key_value(render_tables, 'vrf-name')
    if present == False :
        ospf_debug_print("show_router_ospf_area_vlink_config: vrf_name not present")
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_router_ospf_area_vlink_config: vrf_name {} present".format(vrf_name))

    tbl_path = 'sonic-ospfv2:sonic-ospfv2/OSPFV2_ROUTER_AREA_VIRTUAL_LINK/OSPFV2_ROUTER_AREA_VIRTUAL_LINK_LIST'
    present, tbl_path, tbl_rec_list = ospf_get_key_value(render_tables, tbl_path)
    if present == False :
        ospf_debug_print("show_router_ospf_area_vlink_config: AREA_VIRTUAL_LINK not present")
        status, sub_cmd_str = show_router_ospf_area_vlmd_auth_config(render_tables)
        if status == 'CB_SUCCESS' :
            cmd_str += sub_cmd_str
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_router_ospf_area_vlink_config: AREA_VIRTUAL_LINK {}".format(tbl_rec_list))

    if not isinstance(tbl_rec_list, list) :
        tbl_rec_list = [ tbl_rec_list ]

    for tbl_rec in tbl_rec_list :
        vrf_p, _, vrf_v = ospf_get_key_value(tbl_rec, 'vrf_name')
        if vrf_p == False :
            ospf_debug_print("show_router_ospf_area_vlink_config: vrf field not present")
            continue

        if vrf_v != vrf_name :
            ospf_debug_print("show_router_ospf_area_vlink_config: vrf names {} != {}".format(vrf_v, vrf_name))
            continue

        area_p, _, area_v = ospf_get_key_value(tbl_rec, 'area-id')
        if area_p == False :
            continue

        rmtid_p, _, rmtid_v = ospf_get_key_value(tbl_rec, 'remote-router-id')
        if rmtid_p == False :
            continue

        sub_cmd_p = False
        cmd_vlink_str = 'area {} virtual-link {}'.format(area_v, rmtid_v)
        temp_cmd = ''

        ospf_debug_print("show_router_ospf_area_vlink_config: {}".format(cmd_vlink_str))
        cmd_str += cmd_vlink_str + cmd_end

        auth_p, _, auth_v = ospf_get_key_value(tbl_rec, 'authentication-type')
        if auth_p :
            if auth_v == 'TEXT' :
                temp_cmd = cmd_vlink_str + ' authentication'
                cmd_str += temp_cmd + cmd_end
                sub_cmd_p = True
            elif auth_v == 'MD5HMAC' :
                temp_cmd = cmd_vlink_str + ' authentication message-digest'  
                cmd_str += temp_cmd + cmd_end
                sub_cmd_p = True
            elif auth_v == 'NONE' :
                temp_cmd = cmd_vlink_str + ' authentication null'
                cmd_str += temp_cmd + cmd_end
                sub_cmd_p = True

        akey_p, _, akey_v = ospf_get_key_value(tbl_rec, 'authentication-key')
        if akey_p :
            temp_cmd = cmd_vlink_str + ' authentication-key {} encrypted'.format(akey_v)
            cmd_str += temp_cmd + cmd_end
            sub_cmd_p = True

        akey_p, _, akey_v = ospf_get_key_value(tbl_rec, 'authentication-md5-key')
        akeyid_p, _, akeyid_v = ospf_get_key_value(tbl_rec, 'authentication-key-id')
        if akey_p and akeyid_p :
            temp_cmd = cmd_vlink_str + ' authentication message-digest'
            temp_cmd += ' message-digest-key {} md5 {} encrypted'.format(akeyid_v, akey_v)
            cmd_str += temp_cmd + cmd_end
            sub_cmd_p = True

        tmr_p, _, tmr_v = ospf_get_key_value(tbl_rec, 'dead-interval')
        if tmr_p :
            cmd_str += cmd_vlink_str + ' dead-interval {}'.format(tmr_v) + cmd_end
            sub_cmd_p = True

        tmr_p, _, tmr_v = ospf_get_key_value(tbl_rec, 'hello-interval')
        if tmr_p :
            cmd_str += cmd_vlink_str + ' hello-interval {}'.format(tmr_v) + cmd_end
            sub_cmd_p = True

        tmr_p, _, tmr_v = ospf_get_key_value(tbl_rec, 'retransmission-interval')
        if tmr_p :
            cmd_str += cmd_vlink_str + ' retransmit-interval {}'.format(tmr_v) + cmd_end
            sub_cmd_p = True

        tmr_p, _, tmr_v = ospf_get_key_value(tbl_rec, 'transmit-delay')
        if tmr_p :
            cmd_str += cmd_vlink_str + ' transmit-delay {}'.format(tmr_v) + cmd_end
            sub_cmd_p = True

    status, sub_cmd_str = show_router_ospf_area_vlmd_auth_config(render_tables)
    if status == 'CB_SUCCESS' :
        cmd_str += sub_cmd_str

    ospf_debug_print("show_router_ospf_area_vlink_config: cmd_str {}".format(cmd_str))
    return 'CB_SUCCESS', cmd_str


def show_router_ospf_area_vlmd_auth_config(render_tables):
    cmd_str = ''
    cmd_end = ' ;'

    #ospf_debug_log_enable()
    #ospf_debug_log_disable()

    ospf_debug_print("show_router_ospf_area_vlmd_auth_config: render_tables {}".format(render_tables))

    present, name, vrf_name = ospf_get_key_value(render_tables, 'vrf-name')
    if present == False :
        ospf_debug_print("show_router_ospf_area_vlmd_auth_config: vrf_name not present")
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_router_ospf_area_vlmd_auth_config: vrf_name {} present".format(vrf_name))

    tbl_path = 'sonic-ospfv2:sonic-ospfv2/OSPFV2_ROUTER_AREA_VLMD_AUTHENTICATION/OSPFV2_ROUTER_AREA_VLMD_AUTHENTICATION_LIST'
    present, tbl_path, tbl_rec_list = ospf_get_key_value(render_tables, tbl_path)
    if present == False :
        ospf_debug_print("show_router_ospf_area_vlmd_auth_config: AREA_VIRTUAL_LINK not present")
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_router_ospf_area_vlmd_auth_config: AREA_VLMD_AUTH {}".format(tbl_rec_list))

    if not isinstance(tbl_rec_list, list) :
        tbl_rec_list = [ tbl_rec_list ]

    for tbl_rec in tbl_rec_list :
        vrf_p, _, vrf_v = ospf_get_key_value(tbl_rec, 'vrf_name')
        if vrf_p == False :
            ospf_debug_print("show_router_ospf_area_vlmd_auth_config: vrf field not present")
            continue

        if vrf_v != vrf_name :
            ospf_debug_print("show_router_ospf_area_vlmd_auth_config: vrf names {} != {}".format(vrf_v, vrf_name))
            continue

        area_p, _, area_v = ospf_get_key_value(tbl_rec, 'area-id')
        if area_p == False :
            continue

        rmtid_p, _, rmtid_v = ospf_get_key_value(tbl_rec, 'remote-router-id')
        if rmtid_p == False :
            continue

        akeyid_p, _, akeyid_v = ospf_get_key_value(tbl_rec, 'authentication-key-id')
        if akeyid_p == False :
            continue

        sub_cmd_p = False
        cmd_vlink_str = 'area {} virtual-link {}'.format(area_v, rmtid_v)
        temp_cmd = ''

        ospf_debug_print("show_router_ospf_area_vlmd_auth_config: {}".format(cmd_vlink_str))

        akey_p, _, akey_v = ospf_get_key_value(tbl_rec, 'authentication-md5-key')
        if akey_p and akeyid_p :
            temp_cmd = cmd_vlink_str #+ ' authentication message-digest'
            temp_cmd += ' message-digest-key {} md5 {} encrypted'.format(akeyid_v, akey_v)

        if temp_cmd != '' :
            cmd_str += temp_cmd + cmd_end

    ospf_debug_print("show_router_ospf_area_vlmd_auth_config: cmd_str {}".format(cmd_str))
    return 'CB_SUCCESS', cmd_str


def show_router_ospf_area_addr_range_config(render_tables):
    cmd_str = ''
    cmd_end = ' ;'

    #ospf_debug_log_enable()
    #ospf_debug_log_disable()
    ospf_debug_print("show_router_ospf_area_addr_range_config: render_tables {}".format(render_tables))

    present, name, vrf_name = ospf_get_key_value(render_tables, 'vrf-name')
    if present == False :
        ospf_debug_print("show_router_ospf_area_addr_range_config: vrf_name not present")
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_router_ospf_area_addr_range_config: vrf_name {} present".format(vrf_name))

    tbl_path = 'sonic-ospfv2:sonic-ospfv2/OSPFV2_ROUTER_AREA_POLICY_ADDRESS_RANGE/OSPFV2_ROUTER_AREA_POLICY_ADDRESS_RANGE_LIST'
    present, tbl_path, tbl_rec_list = ospf_get_key_value(render_tables, tbl_path)
    if present == False :
        ospf_debug_print("show_router_ospf_area_addr_range_config: ADDRESS_RANGE not present")
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_router_ospf_area_addr_range_config: ADDRESS_RANGE {}".format(tbl_rec_list))

    if not isinstance(tbl_rec_list, list) :
        tbl_rec_list = [ tbl_rec_list ]

    for tbl_rec in tbl_rec_list :
        vrf_p, _, vrf_v = ospf_get_key_value(tbl_rec, 'vrf_name')
        if vrf_p == False :
            ospf_debug_print("show_router_ospf_area_addr_range_config: vrf field not present")
            continue

        if vrf_v != vrf_name :
            ospf_debug_print("show_router_ospf_area_addr_range_config: vrf names {} != {}".format(vrf_v, vrf_name))
            continue

        area_p, _, area_v = ospf_get_key_value(tbl_rec, 'area-id')
        if area_p == False :
            continue

        prefix_p, _, prefix_v = ospf_get_key_value(tbl_rec, 'prefix')
        if prefix_p == False :
            continue

        sub_cmd_p = False
        cmd_range_str = 'area {} range {}'.format(area_v, prefix_v)

        advt_p, _, advt_v = ospf_get_key_value(tbl_rec, 'advertise')

        if advt_p and advt_v == False :
            cmd_str += cmd_range_str + ' not-advertise' + cmd_end
            sub_cmd_p = True
        else :
            cost_p, _, cost_v = ospf_get_key_value(tbl_rec, 'metric')
            subt_p, _, subt_v = ospf_get_key_value(tbl_rec, 'substitue-prefix')

            if advt_p and advt_v == True:
                temp_cmd = cmd_range_str + ' advertise'
                if cost_p :
                    temp_cmd += ' cost {}'.format(cost_v)
                cmd_str += temp_cmd + cmd_end
                sub_cmd_p = True

            if cost_p and sub_cmd_p == False :
                temp_cmd = cmd_range_str + ' cost {}'.format(cost_v)
                cmd_str += temp_cmd + cmd_end
                sub_cmd_p = True

            if subt_p :
                temp_cmd = cmd_range_str + ' substitute {}'.format(subt_v)
                cmd_str += temp_cmd + cmd_end
                sub_cmd_p = True

        if sub_cmd_p == False :
             cmd_str += cmd_range_str + cmd_end

    ospf_debug_print("show_router_ospf_area_addr_range_config: cmd_str {}".format(cmd_str))
    return 'CB_SUCCESS', cmd_str


def show_router_ospf_distribute_route_config(render_tables):
    cmd_str = ''
    cmd_end = ' ;'

    #ospf_debug_log_enable()
    #ospf_debug_log_disable()
    ospf_debug_print("show_router_ospf_distribute_route_config: render_tables {}".format(render_tables))

    present, name, vrf_name = ospf_get_key_value(render_tables, 'vrf-name')
    if present == False :
        ospf_debug_print("show_router_ospf_distribute_route_config: vrf_name not present")
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_router_ospf_distribute_route_config: vrf_name {} present".format(vrf_name))

    tbl_path = 'sonic-ospfv2:sonic-ospfv2/OSPFV2_ROUTER_DISTRIBUTE_ROUTE/OSPFV2_ROUTER_DISTRIBUTE_ROUTE_LIST'
    present, tbl_path, tbl_rec_list = ospf_get_key_value(render_tables, tbl_path)
    if present == False :
        ospf_debug_print("show_router_ospf_distribute_route_config: DISTRIBUTE_ROUTE not present")
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_router_ospf_distribute_route_config: DISTRIBUTE_ROUTE {}".format(tbl_rec_list))

    protocol_map = { 'BGP' : ['redistribute', 'bgp'],
                     'KERNEL': ['redistribute', 'kernel'],
                     'STATIC' : ['redistribute', 'static'],
                     'DIRECTLY_CONNECTED' : ['redistribute', 'connected'] ,
                     'DEFAULT_ROUTE' : ['default-information originate', ''] }

    metric_type_map = { 'TYPE_1' : 1, 'TYPE_2': 2 }

    if not isinstance(tbl_rec_list, list) :
        tbl_rec_list = [ tbl_rec_list ]

    for tbl_rec in tbl_rec_list :
        vrf_p, _, vrf_v = ospf_get_key_value(tbl_rec, 'vrf_name')
        if vrf_p == False :
            ospf_debug_print("show_router_ospf_distribute_route_config: vrf field not present")
            continue

        if vrf_v != vrf_name :
            ospf_debug_print("show_router_ospf_distribute_route_config: vrf names {} != {}".format(vrf_v, vrf_name))
            continue

        protocol_p, _, protocol_v = ospf_get_key_value(tbl_rec, 'protocol')
        if protocol_p == False :
            continue

        if protocol_v not in list(protocol_map.keys()) :
            continue

        direction_p, _, direction_v = ospf_get_key_value(tbl_rec, 'direction')
        if direction_p == False :
            continue

        if direction_v == 'IMPORT' :
            temp_cmd = '{}'.format(protocol_map[protocol_v][0])
            if protocol_map[protocol_v][1] != '' :
                temp_cmd += ' {}'.format(protocol_map[protocol_v][1])

            if protocol_v == 'DEFAULT_ROUTE' :
                always_p, _, always_v = ospf_get_key_value(tbl_rec, 'always')
                if always_p :
                    temp_cmd += ' always'

            metric_p, _, metric_v = ospf_get_key_value(tbl_rec, 'metric')
            if metric_p :
                temp_cmd += ' metric {}'.format(metric_v)

            mtype_p, _, mtype_v = ospf_get_key_value(tbl_rec, 'metric-type')
            if mtype_p and mtype_v in list(metric_type_map.keys()) :
                temp_cmd += ' metric-type {}'.format(metric_type_map[mtype_v])

            rmap_p, _, rmap_v = ospf_get_key_value(tbl_rec, 'route-map')
            if rmap_p :
                temp_cmd += ' route-map {}'.format(rmap_v)

            cmd_str += ' ' + temp_cmd + cmd_end

    ospf_debug_print("show_router_ospf_distribute_route_config: cmd_str {}".format(cmd_str))
    return 'CB_SUCCESS', cmd_str


def show_interface_ip_ospf_config(render_tables):
    cmd_str = ''
    cmd_end = ' ;'

    #ospf_debug_log_enable()
    #ospf_debug_log_disable()
    ospf_debug_print("show_interface_ip_ospf_config: render_tables {}".format(render_tables))

    present, name, intf_name = ospf_get_key_value(render_tables, 'name')
    if present == False :
        ospf_debug_print("show_interface_ip_ospf_config: intf_name not present")
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_interface_ip_ospf_config: intf_name {} present".format(intf_name))

    tbl_path = 'sonic-ospfv2:sonic-ospfv2/OSPFV2_INTERFACE/OSPFV2_INTERFACE_LIST'
    present, tbl_path, tbl_rec_list = ospf_get_key_value(render_tables, tbl_path)
    if present == False :
        ospf_debug_print("show_interface_ip_ospf_config: OSPFV2_INTERFACE not present")
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_interface_ip_ospf_config: OSPFV2_INTERFACE {}".format(tbl_rec_list))

    if not isinstance(tbl_rec_list, list) :
        tbl_rec_list = [ tbl_rec_list ]

    for tbl_rec in tbl_rec_list :
        name_p, _, name_v = ospf_get_key_value(tbl_rec, 'name')
        if name_p == False :
            ospf_debug_print("show_interface_ip_ospf_config: name field not present")
            continue

        if name_v != intf_name :
            ospf_debug_print("show_interface_ip_ospf_config: if names {} != {}".format(name_v, intf_name))
            continue

        addr_p, _, addr_v = ospf_get_key_value(tbl_rec, 'address')
        if addr_p == False :
            continue

        cmd_prefix = 'ip ospf'

        if addr_v == '' or addr_v == '0.0.0.0' :
            cmd_suffix = cmd_end
        else :
            cmd_suffix = '{}'.format(addr_v) + cmd_end

        cmd_prefix = 'ip ospf area'
        cmd_str += ospf_generate_command(tbl_rec, 'area-id', cmd_prefix, cmd_suffix=cmd_suffix)

        cmd_prefix = 'ip ospf authentication'
        match_value = { 'TEXT' : '', 'MD5HMAC' : 'message-digest', 'NONE': 'null' }
        cmd_str += ospf_generate_command(tbl_rec, 'authentication-type', cmd_prefix, match_value=match_value, cmd_suffix=cmd_suffix)

        cmd_prefix = 'ip ospf authentication-key'
        cmd_str += ospf_generate_command(tbl_rec, 'authentication-key', cmd_prefix, cmd_suffix='encrypted ;')    

        if addr_v == '0.0.0.0' :
            cmd_prefix = 'ip ospf'
            match_value = { True : 'bfd' }
            cmd_str += ospf_generate_command(tbl_rec, 'bfd-enable', cmd_prefix, match_value=match_value, cmd_suffix=cmd_end)

        cmd_prefix = 'ip ospf cost'
        cmd_str += ospf_generate_command(tbl_rec, 'metric', cmd_prefix, cmd_suffix=cmd_suffix)

        tmr_p, _, tmr_v = ospf_get_key_value(tbl_rec, 'hello-multiplier')
        if tmr_p :
             cmd_prefix = 'ip ospf dead-interval minimal hello-multiplier'
             cmd_str += ospf_generate_command(tbl_rec, 'hello-multiplier', cmd_prefix, cmd_suffix=cmd_suffix)
        else :
             cmd_prefix = 'ip ospf dead-interval'
             cmd_str += ospf_generate_command(tbl_rec, 'dead-interval', cmd_prefix, cmd_suffix=cmd_suffix)

        cmd_prefix = 'ip ospf hello-interval'
        cmd_str += ospf_generate_command(tbl_rec, 'hello-interval', cmd_prefix, cmd_suffix=cmd_suffix)

        #mdkeyid_p, _, mdkeyid_v = ospf_get_key_value(tbl_rec, 'authentication-key-id')
        #mdkey_p, _, mdkey_v = ospf_get_key_value(tbl_rec, 'authentication-md5-key')
        #if mdkeyid_p and mdkey_p :
        #    temp_cmd = 'ip ospf message-digest-key {} md5 {} encrypted'.format(mdkeyid_v, mdkey_v)
        #    cmd_str +=  temp_cmd + cmd_suffix

        cmd_prefix = 'ip ospf'
        match_value = { True : 'mtu-ignore' }
        cmd_str += ospf_generate_command(tbl_rec, 'mtu-ignore', cmd_prefix, match_value=match_value, cmd_suffix=cmd_suffix)

        if addr_v == '0.0.0.0' :
            cmd_prefix = 'ip ospf network'
            match_value = { 'POINT_TO_POINT_NETWORK' : 'point-to-point', 'BROADCAST_NETWORK' : 'broadcast'}
            cmd_str += ospf_generate_command(tbl_rec, 'network-type', cmd_prefix, match_value=match_value, cmd_suffix=cmd_end)

        cmd_prefix = 'ip ospf priority'
        cmd_str += ospf_generate_command(tbl_rec, 'priority', cmd_prefix, cmd_suffix=cmd_suffix)

        cmd_prefix = 'ip ospf retransmit-interval'
        cmd_str += ospf_generate_command(tbl_rec, 'retransmission-interval', cmd_prefix, cmd_suffix=cmd_suffix)

        cmd_prefix = 'ip ospf transmit-delay'
        cmd_str += ospf_generate_command(tbl_rec, 'transmit-delay', cmd_prefix, cmd_suffix=cmd_suffix)

    ospf_debug_print("show_interface_ip_ospf_config: cmd_str {}".format(cmd_str))
    return 'CB_SUCCESS', cmd_str


def show_interface_ip_ospf_md_auth_config(render_tables):
    cmd_str = ''
    cmd_end = ' ;'

    #ospf_debug_log_enable()
    #ospf_debug_log_disable()
    ospf_debug_print("show_interface_ip_ospf_md_auth_config: render_tables {}".format(render_tables))

    present, name, intf_name = ospf_get_key_value(render_tables, 'name')
    if present == False :
        ospf_debug_print("show_interface_ip_ospf_md_auth_config: intf_name not present")
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_interface_ip_ospf_md_auth_config: intf_name {} present".format(intf_name))

    tbl_path = 'sonic-ospfv2:sonic-ospfv2/OSPFV2_INTERFACE_MD_AUTHENTICATION/OSPFV2_INTERFACE_MD_AUTHENTICATION_LIST'
    present, tbl_path, tbl_rec_list = ospf_get_key_value(render_tables, tbl_path)
    if present == False :
        ospf_debug_print("show_interface_ip_ospf_md_auth_config: OSPFV2_INTERFACE MD AUTH not present")
        return 'CB_SUCCESS', cmd_str

    ospf_debug_print("show_interface_ip_ospf_md_auth_config: OSPFV2_INTERFACE {}".format(tbl_rec_list))

    if not isinstance(tbl_rec_list, list) :
        tbl_rec_list = [ tbl_rec_list ]

    for tbl_rec in tbl_rec_list :
        name_p, _, name_v = ospf_get_key_value(tbl_rec, 'name')
        if name_p == False :
            ospf_debug_print("show_interface_ip_ospf_md_auth_config: name field not present")
            continue

        if name_v != intf_name :
            ospf_debug_print("show_interface_ip_ospf_md_auth_config: if names {} != {}".format(name_v, intf_name))
            continue

        addr_p, _, addr_v = ospf_get_key_value(tbl_rec, 'address')
        if addr_p == False :
            continue

        mdkeyid_p, _, mdkeyid_v = ospf_get_key_value(tbl_rec, 'authentication-key-id')
        if mdkeyid_p == False :
            continue

        if addr_v == '' or addr_v == '0.0.0.0' :
            cmd_suffix = cmd_end
        else :
            cmd_suffix = '{}'.format(addr_v) + cmd_end

        mdkey_p, _, mdkey_v = ospf_get_key_value(tbl_rec, 'authentication-md5-key')
        if mdkeyid_p and mdkey_p :
            temp_cmd = 'ip ospf message-digest-key {} md5 {} encrypted '.format(mdkeyid_v, mdkey_v)
            cmd_str +=  temp_cmd + cmd_suffix

    ospf_debug_print("show_interface_ip_ospf_md_auth_config: cmd_str {}".format(cmd_str))
    return 'CB_SUCCESS', cmd_str
