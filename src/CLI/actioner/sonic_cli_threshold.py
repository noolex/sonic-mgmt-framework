import sys
import json
import collections
import re
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
from swsssdk import ConfigDBConnector

THRESHOLD_BREACH_TABLE_PREFIX = "THRESHOLD_BREACH_TABLE"

def invoke_api(func, args):
    body = None
    api = cc.ApiClient()

    # Set/Get the rules of all THRESHOLD_TABLE entries.
    if func == 'patch_sonic_threshold_sonic_threshold_threshold_table_threshold_table_list_threshold':
	path = cc.Path('/restconf/data/sonic-threshold:sonic-threshold/THRESHOLD_TABLE/THRESHOLD_TABLE_LIST={buffer},{threshold_buffer_type},{interface_name},{buffer_index_per_port}/threshold', buffer = args[1], threshold_buffer_type = args[3], interface_name = args[5], buffer_index_per_port = args[2] )
        body = { "sonic-threshold:threshold":  int(args[4]) }
        return api.patch(path, body)

    if func == 'delete_sonic_threshold_sonic_threshold_threshold_table_threshold_table_list_threshold':
	path = cc.Path('/restconf/data/sonic-threshold:sonic-threshold/THRESHOLD_TABLE/THRESHOLD_TABLE_LIST={buffer},{threshold_buffer_type},{interface_name},{buffer_index_per_port}/threshold', buffer = args[2], threshold_buffer_type = args[4], interface_name = args[5], buffer_index_per_port = args[3] )
	return api.delete(path)
    else:
       body = {}
    return api.cli_not_implemented(func)

def run(func, args):
    try:
         api_response = invoke_api(func, args)

         if api_response.ok():
             response = api_response.content
             if response is None:
                 pass
         else:
             #error response
             print(api_response.error_message())

    except:
             # system/network error
             raise

def get_threshold_breach_event_reports(args):
    api_response = {}
    api = cc.ApiClient()
    # connect to COUNTERS_DB to get THRESHOLD_BREACH_TABLE entries
    counters_db = ConfigDBConnector()
    counters_db.db_connect('COUNTERS_DB')
    path = cc.Path('/restconf/data/sonic-threshold:sonic-threshold/THRESHOLD_BREACH_TABLE/THRESHOLD_BREACH_TABLE_LIST')
    response = api.get(path)

    if response.ok():
        if response.content:
            api_response = response.content['sonic-threshold:THRESHOLD_BREACH_TABLE_LIST']
            for i in range(len(api_response)):
                if "breachreport" not in api_response[i] and "buffer" not in api_response[i] and "type" not in api_response[i] \
				and "port" not in api_response[i] and "index" not in api_response[i] and "breach_value" not in \
				api_response[i] and "time-stamp" not in api_response[i]:
		    print("Failed : Required mandatory parameters are not found")
                    return

                breach_counter_key = THRESHOLD_BREACH_TABLE_PREFIX + ':' + str(api_response[i]['breachreport']) + ':' + str(api_response[i]['eventid'])
                breach_report_stats = counters_db.get_all(counters_db.COUNTERS_DB, breach_counter_key)

                if breach_report_stats is not None:
		   if api_response[i]['type'] == 'shared':
                        api_response[i]['counter'] = breach_report_stats['SAI_INGRESS_PRIORITY_GROUP_STAT_SHARED_WATERMARK_BYTES']
		   elif api_response[i]['type'] == 'headroom':
			api_response[i]['counter'] = breach_report_stats['SAI_INGRESS_PRIORITY_GROUP_STAT_XOFF_ROOM_WATERMARK_BYTES']
		   else :
			api_response[i]['counter'] = breach_report_stats['SAI_QUEUE_STAT_SHARED_WATERMARK_BYTES']
		else:
		   print("Failed : Unable to get the table entries from DB")
    else:
	print "%Error: REST API transaction failure"
    show_cli_output("show_threshold_breach_event_reports.j2", api_response)

if __name__ == '__main__':
     pipestr().write(sys.argv)
     func = sys.argv[1]

     if func == 'get_threshold_breach_event_reports':
        get_threshold_breach_event_reports(sys.argv[2:])
     else:
        run(sys.argv[1], sys.argv[2:])
