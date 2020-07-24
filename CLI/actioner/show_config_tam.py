###########################################################################
#
# Copyright 2020 Broadcom, Inc.
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

def show_tam_view_table_entry_cmds(render_tables, view_type):

   CMDS_STRING = ''
   flag = 0
   if view_type == 'tam_view':
	CMDS_STRING += '!' + "\n" + 'tam' + "\n"
	if 'sonic-tam:sonic-tam/TAM_DEVICE_TABLE/TAM_DEVICE_TABLE_LIST' in render_tables:
	    cmd_prefix = ' device-id '
	    tam_device_table_list = render_tables['sonic-tam:sonic-tam/TAM_DEVICE_TABLE/TAM_DEVICE_TABLE_LIST']
	    for tam_device_entry in tam_device_table_list:
		if 'deviceid' in tam_device_entry:
		    flag = flag + 1
		    CMDS_STRING += cmd_prefix + str(tam_device_entry['deviceid']) + "\n"
	if 'sonic-tam:sonic-tam/TAM_COLLECTOR_TABLE/TAM_COLLECTOR_TABLE_LIST' in render_tables:
	    cmd_prefix = ' collector '
	    tam_collector_table_list = render_tables['sonic-tam:sonic-tam/TAM_COLLECTOR_TABLE/TAM_COLLECTOR_TABLE_LIST']
            for tam_collector_entry in tam_collector_table_list:
		if 'name' in tam_collector_entry and 'ipaddress' in tam_collector_entry and 'ipaddress-type' in \
								tam_collector_entry and 'port' in tam_collector_entry:
		     flag = flag + 1
		     CMDS_STRING += cmd_prefix + tam_collector_entry['name'] + ' type ' + tam_collector_entry['ipaddress-type'] + \
					' ip ' + tam_collector_entry['ipaddress'] + ' port ' + str(tam_collector_entry['port']) + "\n"
	if not flag:
	    CMDS_STRING = ''

   if view_type == 'tam_drop_monitor_view':
	CMDS_STRING += '!' + "\n" + 'tam drop-monitor' + "\n"
	if 'sonic-tam-drop-monitor:sonic-tam-drop-monitor/TAM_DROP_MONITOR_FEATURE_TABLE/TAM_DROP_MONITOR_FEATURE_TABLE_LIST' in render_tables:
	    cmd_prefix = ' feature '
	    tam_drop_monitor_table_list = render_tables['sonic-tam-drop-monitor:sonic-tam-drop-monitor/TAM_DROP_MONITOR_FEATURE_TABLE/TAM_DROP_MONITOR_FEATURE_TABLE_LIST']
	    for tam_drop_monitor_table_entry in tam_drop_monitor_table_list:
	        if tam_drop_monitor_table_entry['enable']:
		    flag = flag + 1
		    CMDS_STRING += cmd_prefix + "enable" + "\n"

        if 'sonic-tam-drop-monitor:sonic-tam-drop-monitor/TAM_DROP_MONITOR_FLOW_TABLE/TAM_DROP_MONITOR_FLOW_TABLE_LIST' in render_tables:
	    cmd_prefix = ' flow '
	    tam_drop_monitor_flow_table_list = render_tables['sonic-tam-drop-monitor:sonic-tam-drop-monitor/TAM_DROP_MONITOR_FLOW_TABLE/TAM_DROP_MONITOR_FLOW_TABLE_LIST']
	    for tam_drop_monitor_flow_table_entry in tam_drop_monitor_flow_table_list:
	        if 'name' in tam_drop_monitor_flow_table_entry and 'acl-table-name' in tam_drop_monitor_flow_table_entry and \
									'acl-rule-name' in tam_drop_monitor_flow_table_entry and \
		'collector-name' in tam_drop_monitor_flow_table_entry and 'sample' in tam_drop_monitor_flow_table_entry and \
									'flowgroup-id' in tam_drop_monitor_flow_table_entry:
		     flag = flag + 1
		     CMDS_STRING += cmd_prefix + tam_drop_monitor_flow_table_entry['name'] + ' acl-table ' + tam_drop_monitor_flow_table_entry['acl-table-name'] + ' acl-rule ' + tam_drop_monitor_flow_table_entry['acl-rule-name'] + ' collector ' + tam_drop_monitor_flow_table_entry['collector-name'] + ' sample ' + tam_drop_monitor_flow_table_entry['sample'] + ' flowgroup-id ' + str(tam_drop_monitor_flow_table_entry['flowgroup-id']) + "\n"

        if 'sonic-tam-drop-monitor:sonic-tam-drop-monitor/TAM_DROP_MONITOR_AGING_INTERVAL_TABLE/TAM_DROP_MONITOR_AGING_INTERVAL_TABLE_LIST' in render_tables:
            cmd_prefix = ' aging-interval '
	    tam_drop_monitor_aging_inter_table_list = render_tables['sonic-tam-drop-monitor:sonic-tam-drop-monitor/TAM_DROP_MONITOR_AGING_INTERVAL_TABLE/TAM_DROP_MONITOR_AGING_INTERVAL_TABLE_LIST']
            for tam_dm_aging_inter_table_entry in tam_drop_monitor_aging_inter_table_list:
	        if 'aging-interval' in tam_dm_aging_inter_table_entry:
		     CMDS_STRING += cmd_prefix + str(tam_dm_aging_inter_table_entry['aging-interval']) + "\n"

	if not flag:
	    CMDS_STRING = ''

   if view_type == 'tam_int_ifa_view':
	CMDS_STRING += '!' + "\n" + 'tam int-ifa' + "\n"
	if 'sonic-ifa:sonic-ifa/TAM_INT_IFA_FEATURE_TABLE/TAM_INT_IFA_FEATURE_TABLE_LIST' in render_tables:
            cmd_prefix = ' feature '
            tam_int_ifa_feature_table_list = render_tables['sonic-ifa:sonic-ifa/TAM_INT_IFA_FEATURE_TABLE/TAM_INT_IFA_FEATURE_TABLE_LIST']
            for tam_int_ifa_feature_table_entry in tam_int_ifa_feature_table_list:
                if tam_int_ifa_feature_table_entry['enable']:
		   flag = flag + 1
                   CMDS_STRING += cmd_prefix + "enable" + "\n"

        if 'sonic-ifa:sonic-ifa/TAM_INT_IFA_FLOW_TABLE/TAM_INT_IFA_FLOW_TABLE_LIST' in render_tables:
            cmd_prefix = ' flow '
            tam_int_ifa_flow_table_list = render_tables['sonic-ifa:sonic-ifa/TAM_INT_IFA_FLOW_TABLE/TAM_INT_IFA_FLOW_TABLE_LIST']
            for tam_int_ifa_flow_table_entry in tam_int_ifa_flow_table_list:
		if 'name' in tam_int_ifa_flow_table_entry and 'acl-table-name' in tam_int_ifa_flow_table_entry and \
                                                                'acl-rule-name' in tam_int_ifa_flow_table_entry:
		     flag = flag + 1
                     CMDS_STRING += cmd_prefix + tam_int_ifa_flow_table_entry['name'] + ' acl-table ' + tam_int_ifa_flow_table_entry['acl-table-name'] + ' acl-rule ' + tam_int_ifa_flow_table_entry['acl-rule-name']
                if 'collector-name' in tam_int_ifa_flow_table_entry:
		     CMDS_STRING += ' collector ' + tam_int_ifa_flow_table_entry['collector-name']
		if 'sampling-rate' in tam_int_ifa_flow_table_entry:
		     CMDS_STRING += ' sampling-rate ' + str(tam_int_ifa_flow_table_entry['sampling-rate'])
		CMDS_STRING += "\n"

	if not flag:
	     CMDS_STRING = ''

   if view_type == 'tam_int_ifa_ts_view':
	CMDS_STRING += '!' + "\n" + 'tam int-ifa-ts' + "\n"
	if 'sonic-tam-int-ifa-ts:sonic-tam-int-ifa-ts/TAM_INT_IFA_TS_FEATURE_TABLE/TAM_INT_IFA_TS_FEATURE_TABLE_LIST' in render_tables:
           cmd_prefix = ' feature '
           tam_int_ifa_ts_feature_table_list = render_tables['sonic-tam-int-ifa-ts:sonic-tam-int-ifa-ts/TAM_INT_IFA_TS_FEATURE_TABLE/TAM_INT_IFA_TS_FEATURE_TABLE_LIST']
           for tam_int_ifa_ts_feature_table_entry in tam_int_ifa_ts_feature_table_list:
              if tam_int_ifa_ts_feature_table_entry['enable']:
		  flag = flag + 1
                  CMDS_STRING += cmd_prefix + "enable" + "\n"

        if 'sonic-tam-int-ifa-ts:sonic-tam-int-ifa-ts/TAM_INT_IFA_TS_FLOW_TABLE/TAM_INT_IFA_TS_FLOW_TABLE_LIST' in render_tables:
           cmd_prefix = ' flow '
           tam_int_ifa_ts_flow_table_list = render_tables['sonic-tam-int-ifa-ts:sonic-tam-int-ifa-ts/TAM_INT_IFA_TS_FLOW_TABLE/TAM_INT_IFA_TS_FLOW_TABLE_LIST']
           for tam_int_ifa_ts_flow_table_entry in tam_int_ifa_ts_flow_table_list:
               if 'name' in tam_int_ifa_ts_flow_table_entry and 'acl-table-name' in tam_int_ifa_ts_flow_table_entry and \
                                                                'acl-rule-name' in tam_int_ifa_ts_flow_table_entry:
		   flag = flag + 1
                   CMDS_STRING += cmd_prefix + tam_int_ifa_ts_flow_table_entry['name'] + ' acl-table ' + tam_int_ifa_ts_flow_table_entry['acl-table-name'] + ' acl-rule ' + tam_int_ifa_ts_flow_table_entry['acl-rule-name'] + "\n"

	if not flag:
	    CMDS_STRING = ''

   # return command string of all tam views i,e tam, int-ifa, int-ifa-ts, drop-monitor
   return CMDS_STRING

def show_tam_config(render_tables):

   CMDS_STRING_TAM = ''

   if 'sonic-tam:sonic-tam/TAM_DEVICE_TABLE/TAM_DEVICE_TABLE_LIST' in render_tables or 'sonic-tam:sonic-tam/TAM_COLLECTOR_TABLE/TAM_COLLECTOR_TABLE_LIST in render_tables':
	CMDS_STRING_TAM += show_tam_view_table_entry_cmds(render_tables, 'tam_view')

   if 'sonic-tam-drop-monitor:sonic-tam-drop-monitor/TAM_DROP_MONITOR_FEATURE_TABLE/TAM_DROP_MONITOR_FEATURE_TABLE_LIST' in render_tables or 'sonic-tam-drop-monitor:sonic-tam-drop-monitor/TAM_DROP_MONITOR_FLOW_TABLE/TAM_DROP_MONITOR_FLOW_TABLE_LIST' in render_tables or 'sonic-tam-drop-monitor:sonic-tam-drop-monitor/TAM_DROP_MONITOR_AGING_INTERVAL_TABLE/TAM_DROP_MONITOR_AGING_INTERVAL_TABLE_LIST' in render_tables:
	CMDS_STRING_TAM += show_tam_view_table_entry_cmds(render_tables, 'tam_drop_monitor_view')

   if 'sonic-ifa:sonic-ifa/TAM_INT_IFA_FEATURE_TABLE/TAM_INT_IFA_FEATURE_TABLE_LIST' in render_tables or 'sonic-ifa:sonic-ifa/TAM_INT_IFA_FLOW_TABLE/TAM_INT_IFA_FLOW_TABLE_LIST' in render_tables:
	CMDS_STRING_TAM += show_tam_view_table_entry_cmds(render_tables, 'tam_int_ifa_view')

   if 'sonic-tam-int-ifa-ts:sonic-tam-int-ifa-ts/TAM_INT_IFA_TS_FEATURE_TABLE/TAM_INT_IFA_TS_FEATURE_TABLE_LIST' in render_tables or 'sonic-ifa:sonic-ifa/TAM_INT_IFA_TS_FLOW_TABLE/TAM_INT_IFA_TS_FLOW_TABLE_LIST' in render_tables:
	CMDS_STRING_TAM += show_tam_view_table_entry_cmds(render_tables, 'tam_int_ifa_ts_view')

   return 'CB_SUCCESS', CMDS_STRING_TAM
