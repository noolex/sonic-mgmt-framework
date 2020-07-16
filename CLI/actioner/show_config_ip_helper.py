default_protocol_string = {
    69: "tftp",
    53: "dns",
    37: "ntp",
    137: "netbios-name-server",
    138: "netbios-datagram-server",
    49: "tacacs"
}

def show_ip_helper_address(render_tables):
    cmd_str = ''
    cmd_prfx = 'ip helper-address '
    if 'sonic-interface:sonic-interface/INTERFACE/INTERFACE_LIST' in render_tables:
        intfdata = render_tables['sonic-interface:sonic-interface/INTERFACE/INTERFACE_LIST']
        key = 'portname'
    if 'sonic-vlan-interface:sonic-vlan-interface/VLAN_INTERFACE/VLAN_INTERFACE_LIST' in render_tables:
        intfdata = render_tables['sonic-vlan-interface:sonic-vlan-interface/VLAN_INTERFACE/VLAN_INTERFACE_LIST']
        key = 'vlanName'
    if 'sonic-portchannel-interface:sonic-portchannel-interface/PORTCHANNEL_INTERFACE/PORTCHANNEL_INTERFACE_LIST' in render_tables:
        intfdata = render_tables['sonic-portchannel-interface:sonic-portchannel-interface/PORTCHANNEL_INTERFACE/PORTCHANNEL_INTERFACE_LIST']
        key = 'pch_name'
    for item in intfdata:
        if render_tables['name'] == item[key]:
            if 'helper_addresses' in item:
                for addr in item['helper_addresses']:
                    arglist = addr.split("|")
                    if len(arglist) > 1:
                        cmd_str = cmd_str + cmd_prfx + 'vrf ' + arglist[0] + ' ' + arglist[1] + ';'
                    else:
                        cmd_str = cmd_str + cmd_prfx + arglist[0] + ';'
    return 'CB_SUCCESS', cmd_str

def show_ip_helper_include_ports(render_tables):
    cmd_str = ''
    cmd_prfx = 'ip forward-protocol udp include '
    if 'sonic-ip-helper:sonic-ip-helper/UDP_BROADCAST_FORWARDING/UDP_BROADCAST_FORWARDING_LIST' in render_tables:
        data = render_tables['sonic-ip-helper:sonic-ip-helper/UDP_BROADCAST_FORWARDING/UDP_BROADCAST_FORWARDING_LIST']
        if 'include_ports' in data[0]:
            ports = data[0]['include_ports']
            for port in ports:
                if port not in default_protocol_string:
                    cmd_str = cmd_str + cmd_prfx + str(port) + ';'
    return 'CB_SUCCESS', cmd_str

def show_ip_helper_exclude_ports(render_tables):
    cmd_str = ''
    cmd_prfx = 'ip forward-protocol udp exclude '
    if 'sonic-ip-helper:sonic-ip-helper/UDP_BROADCAST_FORWARDING/UDP_BROADCAST_FORWARDING_LIST' in render_tables:
        data = render_tables['sonic-ip-helper:sonic-ip-helper/UDP_BROADCAST_FORWARDING/UDP_BROADCAST_FORWARDING_LIST']
        if 'exclude_default_ports' in data[0]:
            ports = data[0]['exclude_default_ports']
            for port in ports:
                if port in default_protocol_string:
                    cmd_str = cmd_str + cmd_prfx + default_protocol_string[port] + ';'
                else:
                    cmd_str = cmd_str + cmd_prfx + str(port) + ';'
    return 'CB_SUCCESS', cmd_str
