################################################################################
#                                                                              #
#  Copyright 2020 Broadcom. The term Broadcom refers to Broadcom Inc. and/or   #
#  its subsidiaries.                                                           #
#                                                                              #
#  Licensed under the Apache License, Version 2.0 (the "License");             #
#  you may not use this file except in compliance with the License.            #
#  You may obtain a copy of the License at                                     #
#                                                                              #
#     http://www.apache.org/licenses/LICENSE-2.0                               #
#                                                                              #
#  Unless required by applicable law or agreed to in writing, software         #
#  distributed under the License is distributed on an "AS IS" BASIS,           #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    #
#  See the License for the specific language governing permissions and         #
#  limitations under the License.                                              #
#                                                                              #
################################################################################

from show_config_if_cmd import format_intf_name

def show_logging_server_cmd(render_tables):
    serevrs = render_tables.get('sonic-system-logging:sonic-system-logging/SYSLOG_SERVER/SYSLOG_SERVER_LIST')
    if serevrs is None:
        return 'CB_SUCCESS', ''

    commands = []
    for server in serevrs:
        cmd = 'logging server ' + server['ipaddress']
        if 'remote-port' in server:
            cmd += (' remote-port ' + str(server['remote-port']))
        if 'src_intf' in server:
            cmd += (' source-interface ' + format_intf_name(server['src_intf']))
        if 'vrf_name' in server:
            cmd += (' vrf ' + server['vrf_name'])
        commands.append(cmd)

    return 'CB_SUCCESS', ';'.join(commands)

