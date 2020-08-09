###########################################################################
#
# Copyright 2020 Broadcom. The term Broadcom refers to Broadcom Inc. and/or
# its subsidiaries.
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

import json

def show_snmp_contact(render_tables):
    resp = []

    tbl = 'sonic-snmp:sonic-snmp/SNMP_SERVER'
    lst = 'SNMP_SERVER_LIST'
    if (tbl in render_tables) and (lst in render_tables[tbl]):
        for ent in render_tables[tbl][lst]:
            name = ent.get('sysContact')
            if (name is None) or (name in ['None', 'NONE', 'none']):
                continue

            resp.append('snmp-server contact "{0}"'.format(name))
            break

    return 'CB_SUCCESS', "\n".join(resp)

def show_snmp_location(render_tables):
    resp = []

    tbl = 'sonic-snmp:sonic-snmp/SNMP_SERVER'
    lst = 'SNMP_SERVER_LIST'
    if (tbl in render_tables) and (lst in render_tables[tbl]):
        for ent in render_tables[tbl][lst]:
            name = ent.get('sysLocation')
            if (name is None) or (name in ['None', 'NONE', 'none']):
                continue

            resp.append('snmp-server location "{0}"'.format(name))
            break

    return 'CB_SUCCESS', "\n".join(resp)

def show_snmp_traps(render_tables):
    resp = []

    tbl = 'sonic-snmp:sonic-snmp/SNMP_SERVER'
    lst = 'SNMP_SERVER_LIST'
    if (tbl in render_tables) and (lst in render_tables[tbl]):
        for ent in render_tables[tbl][lst]:
            flag = ent.get('traps')
            if (flag is None) or (flag != 'enable'):
                continue

            resp.append('snmp-server enable trap')
            break

    return 'CB_SUCCESS', "\n".join(resp)

def show_snmp_community(render_tables):
    resp = []

    tbl = 'sonic-snmp:sonic-snmp/SNMP_SERVER_COMMUNITY'
    lst = 'SNMP_SERVER_COMMUNITY_LIST'
    if (tbl in render_tables) and (lst in render_tables[tbl]):
        for ent in render_tables[tbl][lst]:
            usr = ent.get('index')
            if (usr is None) or (usr in ['None', 'NONE', 'none']):
                continue

            grp = ent.get('securityName')
            if (grp is not None) and (grp not in ['None', 'NONE', 'none']):
                resp.append('snmp-server community {0} group {1}'.format(usr, grp))
            else:
                resp.append('snmp-server community {0}'.format(usr))

    return 'CB_SUCCESS', "\n".join(resp)

def show_snmp_engine(render_tables):
    resp = []

    tbl = 'sonic-snmp:sonic-snmp/SNMP_SERVER_ENGINE'
    lst = 'SNMP_SERVER_ENGINE_LIST'
    if (tbl in render_tables) and (lst in render_tables[tbl]):
        for ent in render_tables[tbl][lst]:
            id = ent.get('engine-id')
            if id is not None:
                resp.append('snmp-server engine {0}'.format(id.replace(':', '')))

    return 'CB_SUCCESS', "\n".join(resp)

def is_null_key(key_string):
    for tok in key_string.split(':'):
        if int(tok, 16) > 0:
            return False
    return True

def show_snmp_user(render_tables):
    resp = []

    tbl = 'sonic-snmp:sonic-snmp/SNMP_SERVER_USER'
    lst = 'SNMP_SERVER_USER_LIST'
    gtbl = 'sonic-snmp:sonic-snmp/SNMP_SERVER_GROUP_MEMBER'
    glst = 'SNMP_SERVER_GROUP_MEMBER_LIST'
    if (tbl in render_tables) and (lst in render_tables[tbl]):
        for ent in render_tables[tbl][lst]:
            user = ent['name']
            comm = 'snmp-server user {0}'.format(user)

            # group <group-name>
            group = 'None'
            for gent in render_tables[gtbl][glst]:
                if gent['securityName'] != user:
                    continue
                group = gent['groupName']
                if group is None:
                    group = 'None'
                break
            if group not in ['None', 'none', 'NONE']:
                comm += ' group {0}'.format(group)

            # encrypted auth <md5/sha> auth-password <hex>
            if ('md5Key' in ent) and (not is_null_key(ent['md5Key'])):
                str = ent['md5Key']
                comm += ' encrypted auth md5 auth-password {0}'.format(str.replace(':', ''))
            if ('shaKey' in ent) and (not is_null_key(ent['shaKey'])):
                str = ent['shaKey']
                comm += ' encrypted auth sha auth-password {0}'.format(str.replace(':', ''))

            # priv <des/aes-128> priv-password <hex>
            if ('desKey' in ent) and (not is_null_key(ent['desKey'])):
                str = ent['desKey']
                comm += ' priv des priv-password {0}'.format(str.replace(':', ''))
            if ('aesKey' in ent) and (not is_null_key(ent['aesKey'])):
                str = ent['aesKey']
                comm += ' priv aes-128 priv-password {0}'.format(str.replace(':', ''))
            resp.append(comm)

    return 'CB_SUCCESS', "\n".join(resp)

def show_snmp_view(render_tables):
    resp = []

    tbl = 'sonic-snmp:sonic-snmp/SNMP_SERVER_VIEW'
    lst = 'SNMP_SERVER_VIEW_LIST'
    if (tbl in render_tables) and (lst in render_tables[tbl]):
        for ent in render_tables[tbl][lst]:
            name = ent.get('name')
            if (name is None) or (name in ['None', 'NONE', 'none']):
                continue
            if 'exclude' in ent:
                for oid in ent['exclude']:
                    resp.append('snmp-server view {0} {1} excluded'.format(name, oid))
            if 'include' in ent:
                for oid in ent['include']:
                    resp.append('snmp-server view {0} {1} included'.format(name, oid))

    return 'CB_SUCCESS', "\n".join(resp)

def show_snmp_group(render_tables):
    resp = []

    tbl = 'sonic-snmp:sonic-snmp/SNMP_SERVER_GROUP_ACCESS'
    lst = 'SNMP_SERVER_GROUP_ACCESS_LIST'
    if (tbl in render_tables) and (lst in render_tables[tbl]):
        for ent in render_tables[tbl][lst]:
            name = ent.get('groupName')
            if (name is None) or (name in ['None', 'NONE', 'none']):
                continue

            model = ent['securityModel']
            if model in ['any', 'v2c']:
                mesg = 'snmp-server group {0} {1}'.format(name, model)
                view = ent['readView']
                if view not in ['None', 'NONE', 'none']:
                    mesg += ' read {0}'.format(view)
                view = ent['writeView']
                if view not in ['None', 'NONE', 'none']:
                    mesg += ' write {0}'.format(view)
                view = ent['notifyView']
                if view not in ['None', 'NONE', 'none']:
                    mesg += ' notify {0}'.format(view)
                resp.append(mesg)

            if model in ['usm', 'v3']:
                mesg = 'snmp-server group {0} v3'.format(name)

                level = ent['securityLevel']
                if level == 'no-auth-no-priv':
                    mesg += ' noauth'
                elif level == 'auth-no-priv':
                    mesg += ' auth'
                elif level == 'auth-priv':
                    mesg += ' priv'

                view = ent['readView']
                if view not in ['None', 'NONE', 'none']:
                    mesg += ' read {0}'.format(view)
                view = ent['writeView']
                if view not in ['None', 'NONE', 'none']:
                    mesg += ' write {0}'.format(view)
                view = ent['notifyView']
                if view not in ['None', 'NONE', 'none']:
                    mesg += ' notify {0}'.format(view)

                resp.append(mesg)

    return 'CB_SUCCESS', "\n".join(resp)

def show_snmp_host(render_tables):
    resp = []

    tbl = 'sonic-snmp:sonic-snmp/SNMP_SERVER_TARGET'
    lst = 'SNMP_SERVER_TARGET_LIST'
    ptbl = 'sonic-snmp:sonic-snmp/SNMP_SERVER_PARAMS'
    plst = 'SNMP_SERVER_PARAMS_LIST'
    if (tbl in render_tables) and (lst in render_tables[tbl]):
        for ent in render_tables[tbl][lst]:
            addr = ent['ip']
            port = ent['port']
            targ = ent['targetParams']
            mesg = None
            auth = None
            for param in render_tables[ptbl][plst]:
                if param['name'] != targ:
                    continue

                mesg = 'snmp-server host {0}'.format(addr)
                if 'securityNameV2' in param:
                    mesg += ' community {0}'.format(param['securityNameV2'])
                elif 'user' in param:
                    mesg += ' user {0}'.format(param['user'])

                # traps/informs
                mode = ent['tag'][0]
                if mode == 'informNotify':
                    mesg += ' informs'
                elif 'user' in param:
                    mesg += ' traps'

                # noauth/auth/priv
                if 'user' in param:
                    auth = param['security-level']
                    if auth == 'no-auth-no-priv':
                        mesg += ' noauth'
                    elif auth == 'auth-no-priv':
                        mesg += ' auth'
                    elif auth == 'auth-priv':
                        mesg += ' priv'

                # retries (informs only)
                if (mode == 'informNotify') and (ent['retries'] != 3):
                    mesg += ' retries {0}'.format(ent['retries'])

                # timeout (informs only)
                if (mode == 'informNotify') and (ent['timeout'] != 1500):
                    mesg += ' timeout {0}'.format(ent['timeout'] / 100)

                # port
                if port != 162:
                    mesg += ' port {0}'.format(port)

                # interface
                if len(ent['tag']) > 1:
                    mesg += ' interface {0}'.format(ent['tag'][1])

                break

            if mesg is None:
                continue;

            resp.append(mesg)

    return 'CB_SUCCESS', "\n".join(resp)