def show_dns_source_if(render_tables):

    cmd_str = ''
    cmd_prfx = 'ip name-server source-interface '
    if 'sonic-system-dns:sonic-system-dns/DNS/DNS_LIST' in render_tables:
        for dns_inst in render_tables['sonic-system-dns:sonic-system-dns/DNS/DNS_LIST']:
          if 'src_intf' in dns_inst:
            intf = dns_inst['src_intf']
            if intf.startswith('Ethernet'):
               intf_split = intf.split('Ethernet')
               cmd_str = cmd_prfx + 'Ethernet' + intf_split[1]
            elif intf.startswith('Vlan'):
               intf_split = intf.split('Vlan')
               cmd_str = cmd_prfx + 'Vlan' + intf_split[1]
            elif intf.startswith('PortChannel'):
               intf_split = intf.split('PortChannel')
               cmd_str = cmd_prfx +  'PortChannel' + intf_split[1]
            elif intf.startswith('Loopback'):
               intf_split = intf.split('Loopback')
               cmd_str = cmd_prfx +  'Loopback' + intf_split[1]
            elif intf.startswith('eth0'):
               cmd_str = cmd_prfx +  'Management0'
            else:
               pass

    return 'CB_SUCCESS', cmd_str
