
def show_router_bgp_neighbor_cmd(render_tables):
    cmd_str = ''

    if 'sonic-bgp-neighbor:sonic-bgp-neighbor/BGP_NEIGHBOR' in render_tables:
        neighbor_inst = render_tables['sonic-bgp-neighbor:sonic-bgp-neighbor/BGP_NEIGHBOR']
        if 'neighbor' in neighbor_inst:
            neighbor = neighbor_inst['neighbor']
            if neighbor.startswith('Ethernet'):
               nbr_split = neighbor.split('Ethernet')
               cmd_str = 'neighbor interface Ethernet ' + nbr_split[1]
            elif neighbor.startswith('Vlan'):
               nbr_split = neighbor.split('Vlan')
               cmd_str = 'neighbor interface Vlan ' + nbr_split[1]
            elif neighbor.startswith('PortChannel'):
               nbr_split = neighbor.split('PortChannel')
               cmd_str = 'neighbor interface PortChannel ' + nbr_split[1]
            else:
               cmd_str = 'neighbor ' + neighbor

    return 'CB_SUCCESS', cmd_str
