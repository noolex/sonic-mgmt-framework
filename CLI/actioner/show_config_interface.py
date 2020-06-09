
def show_if_channel_group_cmd(render_tables):
    cmd_str = ''

    if 'name' in render_tables:
       ifname_key = render_tables['name']
       if 'sonic-portchannel:sonic-portchannel/PORTCHANNEL_MEMBER' in render_tables:
           for channel_member in render_tables['sonic-portchannel:sonic-portchannel/PORTCHANNEL_MEMBER']:
              if 'ifname' in channel_member:
	         if ifname_key == channel_member['ifname']:
                   lag_id = channel_member['name'].lstrip('PortChannel')
                   cmd_str = 'channel-group ' + lag_id
                  
    return 'CB_SUCCESS', cmd_str


def show_if_switchport_access(render_tables):
    cmd_str = ''

    if 'name' in render_tables:
       ifname_key = render_tables['name']
       if 'sonic-vlan:sonic-vlan/VLAN_MEMBER' in render_tables:
           for vlan_member in render_tables['sonic-vlan:sonic-vlan/VLAN_MEMBER']:
              if 'ifname' in vlan_member:
	         if ifname_key == vlan_member['ifname'] and vlan_member['tagging_mode']=='untagged':
                   vlan_id = vlan_member['name'].lstrip('Vlan')
                   cmd_str = 'switchport access Vlan ' + vlan_id

    return 'CB_SUCCESS', cmd_str



def show_if_switchport_trunk(render_tables):
    cmd_str = ''
    vlan_lst = ''
    if 'name' in render_tables:
       ifname_key = render_tables['name']
       if 'sonic-vlan:sonic-vlan/VLAN_MEMBER' in render_tables:
           for vlan_member in render_tables['sonic-vlan:sonic-vlan/VLAN_MEMBER']:
              if 'ifname' in vlan_member:
	         if ifname_key == vlan_member['ifname'] and vlan_member['tagging_mode']=='tagged':
                   vlan_id = vlan_member['name'].lstrip('Vlan')
                   if vlan_lst: 
                       vlan_lst += ","
                   vlan_lst += vlan_id   
    if vlan_lst:
       cmd_str = 'switchport trunk allowed Vlan ' + vlan_lst

    return 'CB_SUCCESS', cmd_str

def show_interface_portchannel(render_tables):
    cmd_str = ''

    if 'name' in render_tables:
        ifname_key = render_tables['name']
        if 'sonic-portchannel:sonic-portchannel/PORTCHANNEL' in render_tables:
              portchannel = render_tables['sonic-portchannel:sonic-portchannel/PORTCHANNEL']
              if 'name' in portchannel:
	         if ifname_key == portchannel['name']:
                   cmd_str = 'interface PortChannel ' + ifname_key.lstrip('PortChannel')
                 if 'min_links' in portchannel:
                   cmd_str += " min-links "
                   cmd_str += str(portchannel['min_links'])
                 if 'static' in portchannel:
                   if portchannel['static'] == 'false':
                      cmd_str += " mode active"
                   else:
                      cmd_str += " mode on"
                 if 'fallback' in portchannel:
                    if portchannel['fallback'] == 'true':
                      cmd_str += ' fallback'
    return 'CB_SUCCESS', cmd_str

def show_if_lag_mclag(render_tables):
   cmd_str = ''

   if 'name' in render_tables:
       ifname_key = render_tables['name']
       if 'sonic-mclag:sonic-mclag/MCLAG_INTERFACE' in render_tables:
             for mclag_if in render_tables['sonic-mclag:sonic-mclag/MCLAG_INTERFACE']:
                 if 'if_name' in mclag_if:
		    if ifname_key == mclag_if['if_name']:
                       if 'domain_id' in mclag_if:
                           cmd_str = 'mclag ' + mclag_if['domain_id']
   return 'CB_SUCCESS', cmd_str    
        

def show_interface_management(render_tables):
    return 'CB_SUCCESS','interface Management 0'


def show_if_management_autoneg(render_tables):
    cmd_str = ''

    if 'name' in render_tables:
        ifname_key = render_tables['name']
        if 'sonic-mgmt-port:sonic-mgmt-port/MGMT_PORT' in render_tables:
              port = render_tables['sonic-mgmt-port:sonic-mgmt-port/MGMT_PORT']
              if 'name' in port:
	         if ifname_key == port['name']:
                    if 'autoneg' in port:
                       if port['autoneg'] == 'true':
                           cmd_str = "autoneg on"
                       else:
                           cmd_str = "autoneg off"

    return 'CB_SUCCESS', cmd_str

def show_if_loopback(render_tables):
  cmd_str = ''

  if 'name' in render_tables:
      ifname = render_tables['name']
      cmd_str = "interface Loopback " + ifname.lstrip('Loopback')
  return 'CB_SUCCESS', cmd_str
