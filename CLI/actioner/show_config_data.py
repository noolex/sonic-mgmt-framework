###########################################################################
#
# Copyright 2019 Dell, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###########################################################################

from show_config_bgp import *
from show_config_interface import *
from show_config_authentication import *
from show_config_ptp import *
from show_config_dns import *

view_dependency= \
{'configure-router-bgp':['configure-router-bgp-ipv4', 'configure-router-bgp-ipv6', 'configure-router-bgp-l2vpn',
                         'configure-router-bgp-nbr'],
'configure-router-bgp-nbr':['configure-router-bgp-nbr-ipv4', 'configure-router-bgp-nbr-ipv6', 'configure-router-bgp-nbr-l2vpn']}

config_view_hierarchy= \
['configure', 'configure-vlan', 'configure-lo', 'configure-if-mgmt',  'configure-if', 'configure-lag', 'configure-router-bgp']


render_filelst  = {}

render_cb_dict  = {'router_bgp_neighbor'    : show_router_bgp_neighbor_cmd,
                  'if_channel_group'        : show_if_channel_group_cmd,
                  'if_switchport_access'    : show_if_switchport_access,
                  'if_switchport_trunk'     : show_if_switchport_trunk,
                  'interface_loopback'      : show_if_loopback,
                  'interface_portchannel'   : show_interface_portchannel,
                  'if_lag_mclag'            : show_if_lag_mclag,
                  'interface_management'    : show_interface_management,
                  'if_management_autoneg'   : show_if_management_autoneg,
                  'tacacs_server_source_if' : show_tacacs_source_if,
                  'ptp_mode'                : show_ptp_mode,
                  'ptp_domain_profile'      : show_ptp_domain_profile,
                  'ptp_two_step'            : show_ptp_two_step,
                  'ptp_network_transport'   : show_ptp_network_transport,
                  'ptp_master_table'        : show_ptp_master_table,
                  'dns_server_source_if'    : show_dns_source_if
 }

