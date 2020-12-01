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

import cli_client as cc
from show_config_if_cmd import show_render_if_cmd

# show_aaa_config renders running config for 'aaa'
def show_aaa_config(render_tables):

    cmd = ''

    api = cc.ApiClient()
    path = cc.Path('/restconf/data/openconfig-system:system/aaa')
    response = api.get(path)

    if response.ok() is False:
        return 'CB_SUCCESS', cmd, False

    content = response.content
    if ( content is None ) or not ( 'openconfig-system:aaa' in content ):
        return 'CB_SUCCESS', cmd, False
    aaa = content['openconfig-system:aaa']

    # aaa authentication
    if 'authentication' in aaa:
        authentication = aaa['authentication']
        if 'config' in authentication:
            config = authentication['config']
            if 'authentication-method' in config:
                login = config['authentication-method']
                cmd += "aaa authentication login default"
                for method in login:
                    if method != 'local':
                        cmd += " group"
                    cmd += ' ' + method
                cmd += ";"
            if 'openconfig-system-ext:failthrough' in config:
                failthrough = config['openconfig-system-ext:failthrough']
                if failthrough == "True":
                    cmd += "aaa authentication failthrough enable;"

    # aaa authorization
    if 'authorization' in aaa:
        authorization = aaa['authorization']
        if 'openconfig-aaa-ext:login' in authorization:
            login = authorization['openconfig-aaa-ext:login']
            if 'config' in login:
                config = login['config']
                if 'authorization-method' in config:
                    authorization_method = config['authorization-method']
                    cmd += "aaa authorization login default"
                    for method in authorization_method:
                        if method != 'local':
                            cmd += " group"
                        cmd += ' ' + method
                    cmd += ";"
    
    # aaa name-service
    if 'openconfig-aaa-ext:name-service' in aaa:
        name_service = aaa['openconfig-aaa-ext:name-service']
        if 'config' in name_service:
            config = name_service['config']
            for (db,methodlist) in config.items():
                cmd += "aaa name-service " + db.replace("-method", "")
                for method in methodlist:
                    if method != 'local' and method != 'login':
                        cmd += " group"
                    cmd += ' ' + method
                cmd += ";"

    return 'CB_SUCCESS', cmd, False


def show_username_config(render_tables):
    cmd_prfx = 'username '
    table_name = 'sonic-system-aaa:sonic-system-aaa/USER/USER_LIST'
    cmd_str = ''
    if table_name in render_tables:
        for inst in render_tables[table_name]:
            temp_cmd_prfx = cmd_prfx + inst['username'] + ' password ' + inst['password'] + ' role '
            role_str = ' '.join(map(str, (elem for elem in inst['role'])))
            temp_cmd_prfx = temp_cmd_prfx + role_str
            cmd_str = cmd_str+';'+temp_cmd_prfx
    return 'CB_SUCCESS', cmd_str

