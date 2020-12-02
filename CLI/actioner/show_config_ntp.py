###########################################################################
#
# Copyright 2020 Dell, Inc.
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

from show_config_if_cmd import format_intf_name
from show_config_if_cmd import show_get_if_cmd

def show_ntp_source_if(render_tables):

    cmd_str = ''
    cmd_prfx = 'ntp source-interface '
    if 'sonic-system-ntp:sonic-system-ntp/NTP/NTP_LIST' in render_tables:
        for ntp_inst in render_tables['sonic-system-ntp:sonic-system-ntp/NTP/NTP_LIST']:
            if 'src_intf' in ntp_inst:
                if type(ntp_inst['src_intf']) == list:
                    for intf_inst in ntp_inst['src_intf']:
                        intf_name = format_intf_name(intf_inst)
                        cmd_str = cmd_str+';'+cmd_prfx+intf_name
                else:
                    return show_get_if_cmd(render_tables,
                                           'sonic-system-ntp:sonic-system-ntp/NTP/NTP_LIST',
                                           'src_intf',
                                           cmd_prfx)
    return 'CB_SUCCESS', cmd_str

def show_ntp_trusted_key(render_tables):

    cmd_str = ''
    cmd_prfx = 'ntp trusted-key '
    if 'sonic-system-ntp:sonic-system-ntp/NTP/NTP_LIST' in render_tables:
        for ntp_inst in render_tables['sonic-system-ntp:sonic-system-ntp/NTP/NTP_LIST']:
            if 'trusted_key' in ntp_inst:
                if type(ntp_inst['trusted_key']) == list:
                    for key_id in ntp_inst['trusted_key']:
                        cmd_str = cmd_str+';'+cmd_prfx+str(key_id)

    return 'CB_SUCCESS', cmd_str

def show_ntp_authentication_key(render_tables):

    cmd_str = ''
    cmd_prfx = 'ntp authentication-key '
    if 'sonic-system-ntp:sonic-system-ntp/NTP_AUTHENTICATION_KEY/NTP_AUTHENTICATION_KEY_LIST' in render_tables:
        for ntp_key in render_tables['sonic-system-ntp:sonic-system-ntp/NTP_AUTHENTICATION_KEY/NTP_AUTHENTICATION_KEY_LIST']:
            encrypted = ""
            if ntp_key['encrypted'] == True:
                encrypted = " encrypted"

            if ntp_key['type'] == 'SHA2_256':
                cmd_str = cmd_str+';'+cmd_prfx+str(ntp_key['id'])+" SHA2-256 "+ntp_key['value']+encrypted
            else:
                cmd_str = cmd_str+';'+cmd_prfx+str(ntp_key['id'])+" "+ntp_key['type']+" "+ntp_key['value']+encrypted

    return 'CB_SUCCESS', cmd_str
