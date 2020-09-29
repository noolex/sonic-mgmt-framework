def show_ptp_mode(render_tables):

    cmd_str = ''
    cmd_prfx = 'ptp mode '
    if 'sonic-ptp:sonic-ptp/PTP_CLOCK/PTP_CLOCK_LIST' in render_tables:
        for ptp_inst in render_tables['sonic-ptp:sonic-ptp/PTP_CLOCK/PTP_CLOCK_LIST']:
          if 'clock-type' in ptp_inst:
            clock_type = ptp_inst['clock-type']
            if clock_type == "BC":
                cmd_str = cmd_prfx + "boundary-clock"
            elif clock_type == "P2P_TC":
                cmd_str = cmd_prfx + "peer-to-peer-transparent-clock"
            elif clock_type == "E2E_TC":
                cmd_str = cmd_prfx + "end-to-end-transparent-clock"
            elif clock_type == "disable":
                cmd_str = cmd_prfx + "disable"

    return 'CB_SUCCESS', cmd_str

def show_ptp_domain_profile(render_tables):

    cmd_str = ''
    cmd_prfx = 'ptp domain-profile '
    if 'sonic-ptp:sonic-ptp/PTP_CLOCK/PTP_CLOCK_LIST' in render_tables:
        for ptp_inst in render_tables['sonic-ptp:sonic-ptp/PTP_CLOCK/PTP_CLOCK_LIST']:
          if 'domain-profile' in ptp_inst:
            domain_profile = ptp_inst['domain-profile']
            if domain_profile == "ieee1588":
                cmd_str = cmd_prfx + "default"
            elif domain_profile == "G.8275.1":
                cmd_str = cmd_prfx + "g8275.1"
            elif domain_profile == "G.8275.2":
                cmd_str = cmd_prfx + "g8275.2"

    return 'CB_SUCCESS', cmd_str

def show_ptp_two_step(render_tables):

    cmd_str = ''
    cmd_prfx = 'ptp two-step '
    if 'sonic-ptp:sonic-ptp/PTP_CLOCK/PTP_CLOCK_LIST' in render_tables:
        for ptp_inst in render_tables['sonic-ptp:sonic-ptp/PTP_CLOCK/PTP_CLOCK_LIST']:
          if 'two-step-flag' in ptp_inst:
            two_step = ptp_inst['two-step-flag']
            if two_step == 1:
                cmd_str = cmd_prfx + "enable"
            elif two_step == 0:
                cmd_str = cmd_prfx + "disable"

    return 'CB_SUCCESS', cmd_str

def show_ptp_network_transport(render_tables):

    cmd_str = ''
    cmd_prfx = 'ptp network-transport '
    if 'sonic-ptp:sonic-ptp/PTP_CLOCK/PTP_CLOCK_LIST' in render_tables:
        for ptp_inst in render_tables['sonic-ptp:sonic-ptp/PTP_CLOCK/PTP_CLOCK_LIST']:
          if 'network-transport' in ptp_inst:
            network_transport = ptp_inst['network-transport']
            if network_transport == "L2":
                cmd_str = cmd_prfx + "l2 "
            elif network_transport == "UDPv4":
                cmd_str = cmd_prfx + "ipv4 "
            elif network_transport == "UDPv6":
                cmd_str = cmd_prfx + "ipv6 "
          if 'unicast-multicast' in ptp_inst:
            unicast_multicast = ptp_inst['unicast-multicast']
            cmd_str = cmd_str + unicast_multicast

    return 'CB_SUCCESS', cmd_str

def show_ptp_master_table(render_tables):

    underlying_interface = None
    cmd_str = ''
    cmd_prfx = 'ptp port master-table '
    if 'sonic-ptp:sonic-ptp/PTP_PORT/PTP_PORT_LIST' in render_tables:
        for ptp_inst in render_tables['sonic-ptp:sonic-ptp/PTP_PORT/PTP_PORT_LIST']:
            if 'unicast-table' in ptp_inst:
                if 'underlying-interface' in ptp_inst:
                    underlying_interface = ptp_inst['underlying-interface']
                unicast_table = ptp_inst['unicast-table'].split(",")
                if len(unicast_table) == 1 and unicast_table[0] == '':
                    unicast_table = []
                if (underlying_interface is not None):
                    for i, address in enumerate(unicast_table):
                        cmd_str += cmd_prfx + underlying_interface + " add "+ address + ";"

    return 'CB_SUCCESS', cmd_str
