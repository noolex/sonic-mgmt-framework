def show_ntp_source_if(render_tables):

    cmd_str = ''
    cmd_prfx = 'ntp source-interface '
    if 'sonic-system-ntp:sonic-system-ntp/NTP' in render_tables:
        for ntp_inst in render_tables['sonic-system-ntp:sonic-system-ntp/NTP']:
          if 'source' in ntp_inst:
            intf = ntp_inst['source']
            if intf.startswith('Ethernet'):
               intf_split = intf.split('Ethernet')
               cmd_str = cmd_prfx + 'Ethernet ' + intf_split[1]
            elif intf.startswith('Vlan'):
               intf_split = intf.split('Vlan')
               cmd_str = cmd_prfx + 'Vlan ' + intf_split[1]
            elif intf.startswith('PortChannel'):
               intf_split = intf.split('PortChannel')
               cmd_str = cmd_prfx +  'PortChannel ' + intf_split[1]
            elif intf.startswith('Loopback'):
               intf_split = intf.split('Loopback')
               cmd_str = cmd_prfx +  'Loopback ' + intf_split[1]
            elif intf.startswith('eth0'):
               cmd_str = cmd_prfx +  'Management 0'
            else:
               pass

    return 'CB_SUCCESS', cmd_str
