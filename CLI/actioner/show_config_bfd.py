###########################################################################
#
# Copyright 2020 Broadcom. The term Broadcom refers to Broadcom Inc. and/or
# its subsidiaries.
#
###########################################################################

'''
def bfd_get_key_value(in_map, key_name) :
    if key_name == None or key_name == '' :
        return False, 'Key name empty'
    if in_map == None :
        return False, 'Record map null'
    if key_name not in in_map :
        return False, 'Key not found'
    return True, in_map[key_name]
'''

def bfd_get_key_values(in_map) :
    if in_map == None :
        return False
    return True, in_map["remote-address"], in_map["interface"], in_map["vrf"], in_map["local-address"]

def bfd_generate_command(in_map, key_name, cmd_prefix, match_value={}, cmd_suffix=' ;', default='') :
    cmd_str = ''

    if in_map == None :
        return ''
    if key_name == None or key_name == '' :
        return ''

    if key_name in in_map :
        if len(match_value) :
            for key, value in match_value.items() :
                if in_map[key_name] == key :
                    if value != '' :
                        cmd_str = '{} {} {}'.format(cmd_prefix, value, cmd_suffix)
                    else :
                        cmd_str = '{} {}'.format(cmd_prefix, cmd_suffix)
        else :
            value = in_map[key_name]
            if ((default != '') and (value != default)):
                cmd_str = '{} {} {}'.format(cmd_prefix, value, cmd_suffix)

    return cmd_str

def bfd_generate_peer_view_cmd(rec, cmd_prefix):
    cmd_str = ''

    default_value = 3
    cmd_str += bfd_generate_command(rec, 'detection-multiplier', cmd_prefix + 'detect-multiplier', default=default_value)

    default_value = 50
    cmd_str += bfd_generate_command(rec, 'desired-minimum-echo-receive', cmd_prefix + 'echo-interval', default=default_value)

    match_value = { True : '' }
    cmd_str += bfd_generate_command(rec, 'echo-active', cmd_prefix + 'echo-mode', match_value=match_value)

    default_value = 300
    cmd_str += bfd_generate_command(rec, 'required-minimum-receive', cmd_prefix + 'receive-interval', default=default_value)

    match_value = { False : '' }
    cmd_str += bfd_generate_command(rec, 'enabled', cmd_prefix + 'shutdown', match_value=match_value)

    default_value = 300
    cmd_str += bfd_generate_command(rec, 'desired-minimum-tx-interval', cmd_prefix + 'transmit-interval', default=default_value)

    return cmd_str

def bfd_generate_shop_config(shop_rec):
    cmd_str = ""
    cmd_end = ' ;'

    present, remoteaddr, intfname, vrfname, localaddr = bfd_get_key_values(shop_rec)

    cmd_str += ' peer ' + remoteaddr

    if (localaddr != "null"):
        cmd_str += " local-address " + localaddr

    if (vrfname != 'default'):
            cmd_str += ' vrf ' + vrfname

    if (intfname != "null"):
        cmd_str += ' interface ' + intfname

    cmd_str += cmd_end
    cmd_str += bfd_generate_peer_view_cmd(shop_rec, '  ')

    return cmd_str

def bfd_generate_mhop_config(mhop_rec):
    cmd_str = ""
    cmd_end = ' ;'

    present, remoteaddr, intfname, vrfname, localaddr = bfd_get_key_values(mhop_rec)
    cmd_str += ' peer ' + remoteaddr + ' multihop'

    if (localaddr != "null"):
        cmd_str += " local-address " + localaddr

    if (vrfname != 'default'):
        cmd_str += ' vrf ' + vrfname

    if (intfname != "null"):
        cmd_str += ' interface ' + intfname

    cmd_str += cmd_end
    cmd_str += bfd_generate_peer_view_cmd(mhop_rec, '  ')

    return cmd_str

'''
def show_bfd_config(render_tables):
    cmd_str = ''
    cmd_end = ' ;'
    addr_family = "ipv4"
    mhopflag = False
    shop_record_list = {}
    mhop_record_list = {}

    print(show_bfd_config)
    print(render_tables)

    present, vrf_name = bfd_get_key_value(render_tables, "vrfname")
    present, peerip = bfd_get_key_value(render_tables, "peer_ip")
    present, localip = bfd_get_key_value(render_tables, "local_ip")
    present, interface = bfd_get_key_value(render_tables, "interfacename")

    print(vrf_name)
    print(peerip)
    print(interface)
    print(localip)

    shop_tbl_path = 'sonic-bfd:sonic-bfd/BFD_PEER_SINGLE_HOP/BFD_PEER_SINGLE_HOP_LIST'
    mhop_tbl_path = 'sonic-bfd:sonic-bfd/BFD_PEER_MULTI_HOP/BFD_PEER_MULTI_HOP_LIST'

    if (shop_tbl_path in render_tables):
        shop_record = True
        shop_record_list = render_tables[shop_tbl_path]
        if not isinstance(shop_record_list, list):
            shop_record_list = [shop_record_list]

    if (mhop_tbl_path in render_tables):
        mhop_record = True
        mhop_record_list = render_tables[mhop_tbl_path]
        if not isinstance(mhop_record_list, list) :
            mhop_record_list = [mhop_record_list]

    if (shop_record == False and mhop_record == False):
        return 'CB_SUCCESS', cmd_str

    cmd_str += "bfd" + cmd_end

    for shop_rec in shop_record_list:
        present, remoteaddr, intfname, vrfname, localaddr = bfd_get_key_values(shop_rec)
        if (vrf_name == vrfname and peerip == remoteaddr and interface == intfname and localip == localaddr):
            #cmd_str += bfd_generate_peer_view_cmd(shop_rec, '')
            cmd_str += bfd_generate_shop_config(shop_rec)

    for mhop_rec in mhop_record_list:
        present, remoteaddr, intfname, vrfname, localaddr = bfd_get_key_values(mhop_rec)
        if (vrf_name == vrfname and peerip == remoteaddr and interface == intfname and localip == localaddr):
            #cmd_str += bfd_generate_peer_view_cmd(mhop_rec, '')
            cmd_str += bfd_generate_mhop_config(mhop_rec)

    return 'CB_SUCCESS', cmd_str
'''

def show_bfd_config(render_tables):
    cmd_str = ''
    cmd_end = ' ;'
    shop_record = False
    mhop_record = False
    shop_record_list = {}
    mhop_record_list = {}

    shop_tbl_path = 'sonic-bfd:sonic-bfd/BFD_PEER_SINGLE_HOP/BFD_PEER_SINGLE_HOP_LIST'
    mhop_tbl_path = 'sonic-bfd:sonic-bfd/BFD_PEER_MULTI_HOP/BFD_PEER_MULTI_HOP_LIST'

    if (shop_tbl_path in render_tables):
        shop_record = True
        shop_record_list = render_tables[shop_tbl_path]
        if not isinstance(shop_record_list, list):
            shop_record_list = [shop_record_list]

    if (mhop_tbl_path in render_tables):
        mhop_record = True
        mhop_record_list = render_tables[mhop_tbl_path]
        if not isinstance(mhop_record_list, list) :
            mhop_record_list = [mhop_record_list]

    if (shop_record == False and mhop_record == False):
        return 'CB_SUCCESS', cmd_str

    cmd_str += "bfd" + cmd_end

    for shop_rec in shop_record_list:
        cmd_str += bfd_generate_shop_config(shop_rec)
        cmd_str += ' !'
        cmd_str += cmd_end

    for mhop_rec in mhop_record_list:
        cmd_str += bfd_generate_mhop_config(mhop_rec)
        cmd_str += ' !'
        cmd_str += cmd_end

    #cmd_str += cmd_end

    return 'CB_SUCCESS', cmd_str
