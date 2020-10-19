
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
###########################################################################

#!/usr/bin/python

import cli_client as cc

def qos_map_dscp_tc_cb(render_tables):

    #print ("render_tables: ", render_tables)

    map_name = ''
    if 'name' in render_tables:
        map_name = render_tables['name']

    api = cc.ApiClient()
  
    path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:dscp-maps')

    response = api.get(path)

    if response.ok() is False:
        return 'CB_SUCCESS', '', True

    content = response.content

    if content is None:
        return 'CB_SUCCESS', '', True
        
    #print ("Response Content: ", content)

    if 'openconfig-qos-maps-ext:dscp-maps' not in content:
        return 'CB_SUCCESS', '', True

    map_list = content['openconfig-qos-maps-ext:dscp-maps']["dscp-map"]

    #print ("map_list: ", map_list)

    cmd_str = ''
    for map in map_list:
        if map_name != '' and map['name'] != map_name:
            continue

        if 'dscp-map-entries' not in map:
            continue

        if map_name == '':
            if cmd_str != '':
                cmd_str += '!;'

            cmd_str += 'qos map dscp-tc ' + map['name'] + ';'

    
        entries = map['dscp-map-entries']['dscp-map-entry']
        entries = sorted(entries, key = lambda x: int(x['dscp']))
        for entry in entries:
            if entry['config']['fwd-group'] != 'NULL':
                cmd_str += ' dscp ' + str(entry['dscp']) + ' traffic-class ' + str(entry['config']['fwd-group']) + ';'


    #print ("cmd_str: ", cmd_str)

    return 'CB_SUCCESS', cmd_str, True

def qos_map_dot1p_tc_cb(render_tables):

    #print ("render_tables: ", render_tables)

    map_name = ''
    if 'name' in render_tables:
        map_name = render_tables['name']

    api = cc.ApiClient()
  
    path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:dot1p-maps')

    response = api.get(path)

    if response.ok() is False:
        return 'CB_SUCCESS', '', True

    content = response.content

    if content is None:
        return 'CB_SUCCESS', '', True
        
    #print ("Response Content: ", content)

    if 'openconfig-qos-maps-ext:dot1p-maps' not in content:
        return 'CB_SUCCESS', '', True

    map_list = content['openconfig-qos-maps-ext:dot1p-maps']["dot1p-map"]

    #print ("map_list: ", map_list)

    cmd_str = ''
    for map in map_list:
        if map_name != '' and map['name'] != map_name:
            continue

        if 'dot1p-map-entries' not in map:
            continue

        if map_name == '':
            if cmd_str != '':
                cmd_str += '!;'

            cmd_str += 'qos map dot1p-tc ' + map['name'] + ';'

    
        entries = map['dot1p-map-entries']['dot1p-map-entry']
        entries = sorted(entries, key = lambda x: int(x['dot1p']))
        for entry in entries:
            if entry['config']['fwd-group'] != 'NULL':
                cmd_str += ' dot1p ' + str(entry['dot1p']) + ' traffic-class ' + str(entry['config']['fwd-group']) + ';'


    #print ("cmd_str: ", cmd_str)

    return 'CB_SUCCESS', cmd_str, True

def qos_map_tc_queue_cb(render_tables):

    #print ("render_tables: ", render_tables)

    map_name = ''
    if 'name' in render_tables:
        map_name = render_tables['name']

    api = cc.ApiClient()
  
    path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-queue-maps')

    response = api.get(path)

    if response.ok() is False:
        return 'CB_SUCCESS', '', True

    content = response.content

    if content is None:
        return 'CB_SUCCESS', '', True
        
    if 'openconfig-qos-maps-ext:forwarding-group-queue-maps' not in content:
        return 'CB_SUCCESS', '', True

    map_list = content['openconfig-qos-maps-ext:forwarding-group-queue-maps']["forwarding-group-queue-map"]

    cmd_str = ''
    for map in map_list:
        if map_name != '' and map['name'] != map_name:
            continue

        if 'forwarding-group-queue-map-entries' not in map:
            continue

        if map_name == '':
            if cmd_str != '':
                cmd_str += '!;'

            cmd_str += 'qos map tc-queue ' + map['name'] + ';'

    
        entries = map['forwarding-group-queue-map-entries']['forwarding-group-queue-map-entry']
        entries = sorted(entries, key = lambda x: int(x['fwd-group']))
        for entry in entries:
            cmd_str += ' traffic-class ' + str(entry['fwd-group']) + ' queue ' + str(entry['config']['output-queue-index']) + ';'


    return 'CB_SUCCESS', cmd_str, True

def qos_map_tc_pg_cb(render_tables):

    #print ("render_tables: ", render_tables)

    map_name = ''
    if 'name' in render_tables:
        map_name = render_tables['name']

    api = cc.ApiClient()
  
    path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-priority-group-maps')

    response = api.get(path)

    if response.ok() is False:
        return 'CB_SUCCESS', '', True

    content = response.content

    if content is None:
        return 'CB_SUCCESS', '', True
        
    if 'openconfig-qos-maps-ext:forwarding-group-priority-group-maps' not in content:
        return 'CB_SUCCESS', '', True

    map_list = content['openconfig-qos-maps-ext:forwarding-group-priority-group-maps']["forwarding-group-priority-group-map"]

    cmd_str = ''
    for map in map_list:
        if map_name != '' and map['name'] != map_name:
            continue

        if 'forwarding-group-priority-group-map-entries' not in map:
            continue

        if map_name == '':
            if cmd_str != '':
                cmd_str += '!;'

            cmd_str += 'qos map tc-pg ' + map['name'] + ';'

    
        entries = map['forwarding-group-priority-group-map-entries']['forwarding-group-priority-group-map-entry']
        entries = sorted(entries, key = lambda x: int(x['fwd-group']))
        for entry in entries:
            cmd_str += ' traffic-class ' + str(entry['fwd-group']) + ' priority-group ' + str(entry['config']['priority-group-index']) + ';'


    return 'CB_SUCCESS', cmd_str, True

def qos_map_pfc_queue_cb(render_tables):

    #print ("render_tables: ", render_tables)

    map_name = ''
    if 'name' in render_tables:
        map_name = render_tables['name']

    api = cc.ApiClient()
  
    path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:pfc-priority-queue-maps')

    response = api.get(path)

    if response.ok() is False:
        return 'CB_SUCCESS', '', True

    content = response.content

    if content is None:
        return 'CB_SUCCESS', '', True
        
    if 'openconfig-qos-maps-ext:pfc-priority-queue-maps' not in content:
        return 'CB_SUCCESS', '', True

    map_list = content['openconfig-qos-maps-ext:pfc-priority-queue-maps']["pfc-priority-queue-map"]

    cmd_str = ''
    for map in map_list:
        if map_name != '' and map['name'] != map_name:
            continue

        if 'pfc-priority-queue-map-entries' not in map:
            continue

        if map_name == '':
            if cmd_str != '':
                cmd_str += '!;'

            cmd_str += 'qos map pfc-priority-queue ' + map['name'] + ';'

    
        entries = map['pfc-priority-queue-map-entries']['pfc-priority-queue-map-entry']
        entries = sorted(entries, key = lambda x: int(x['dot1p']))
        for entry in entries:
            cmd_str += ' pfc-priority ' + str(entry['dot1p']) + ' queue ' + str(entry['config']['output-queue-index']) + ';'


    return 'CB_SUCCESS', cmd_str, True

def qos_map_tc_dscp_cb(render_tables):

    #print ("render_tables: ", render_tables)

    map_name = ''
    if 'name' in render_tables:
        map_name = render_tables['name']

    api = cc.ApiClient()
  
    path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-dscp-maps')

    response = api.get(path)

    if response.ok() is False:
        return 'CB_SUCCESS', '', True

    content = response.content

    if content is None:
        return 'CB_SUCCESS', '', True
        
    if 'openconfig-qos-maps-ext:forwarding-group-dscp-maps' not in content:
        return 'CB_SUCCESS', '', True

    map_list = content['openconfig-qos-maps-ext:forwarding-group-dscp-maps']["forwarding-group-dscp-map"]

    cmd_str = ''
    for map in map_list:
        if map_name != '' and map['name'] != map_name:
            continue

        if 'forwarding-group-dscp-map-entries' not in map:
            continue

        if map_name == '':
            if cmd_str != '':
                cmd_str += '!;'

            cmd_str += 'qos map tc-dscp ' + map['name'] + ';'

    
        entries = map['forwarding-group-dscp-map-entries']['forwarding-group-dscp-map-entry']
        entries = sorted(entries, key = lambda x: int(x['fwd-group']))
        for entry in entries:
            if entry['fwd-group'] != 'NULL':
                cmd_str += ' traffic-class ' + str(entry['fwd-group']) + ' dscp ' + str(entry['config']['dscp']) + ';'


    return 'CB_SUCCESS', cmd_str, True

def qos_map_tc_dot1p_cb(render_tables):

    #print ("render_tables: ", render_tables)

    map_name = ''
    if 'name' in render_tables:
        map_name = render_tables['name']

    api = cc.ApiClient()
  
    path = cc.Path('/restconf/data/openconfig-qos:qos/openconfig-qos-maps-ext:forwarding-group-dot1p-maps')

    response = api.get(path)

    if response.ok() is False:
        return 'CB_SUCCESS', '', True

    content = response.content

    if content is None:
        return 'CB_SUCCESS', '', True
        
    if 'openconfig-qos-maps-ext:forwarding-group-dot1p-maps' not in content:
        return 'CB_SUCCESS', '', True

    map_list = content['openconfig-qos-maps-ext:forwarding-group-dot1p-maps']["forwarding-group-dot1p-map"]

    cmd_str = ''
    for map in map_list:
        if map_name != '' and map['name'] != map_name:
            continue

        if 'forwarding-group-dot1p-map-entries' not in map:
            continue

        if map_name == '':
            if cmd_str != '':
                cmd_str += '!;'

            cmd_str += 'qos map tc-dot1p ' + map['name'] + ';'

    
        entries = map['forwarding-group-dot1p-map-entries']['forwarding-group-dot1p-map-entry']
        entries = sorted(entries, key = lambda x: int(x['fwd-group']))
        for entry in entries:
            if entry['fwd-group'] != 'NULL':
                cmd_str += ' traffic-class ' + str(entry['fwd-group']) + ' dot1p ' + str(entry['config']['dot1p']) + ';'


    return 'CB_SUCCESS', cmd_str, True


