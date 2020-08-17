import sys
import json
import collections
import re
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
from natsort import natsorted

def get_print_all_port_config(type, th_type, renderer_template):

    # Get the list of interfaces on the system and create a base dictionary with interface name and all zero values
    api = cc.ApiClient()
    path = cc.Path('/restconf/operations/sonic-counters:interface_counters')
    body = {"sonic-counters:input":{}}
    response =  api.post(path, body)
    if not (response.ok() and response.content):
        print "%Error: REST API transaction failure on sonic-counters:interface_counters"
        return

    table = []
    output = {}
    for keys in natsorted(response.content["sonic-counters:output"]["interfaces"]["interface"]):
        output[keys] = {"q0":0,"q1":0,"q2":0,"q3":0,"q4":0,"q5":0,"q6":0,"q7":0}


    # Now get threshold table and update the earlier dictionary with values got from threshold table
    path = cc.Path('/restconf/data/sonic-threshold:sonic-threshold/THRESHOLD_TABLE')
    response = api.get(path)
    if not response.ok():
        print "%Error: REST API transaction failure for THRESHOLD_TABLE"
        return

    if response.content:
        for key in response.content['sonic-threshold:THRESHOLD_TABLE']['THRESHOLD_TABLE_LIST']:
            if key['buffer'] != type:
                continue
            if key['threshold_buffer_type'] != th_type:
                continue
            if key['interface_name'] == 'CPU':
                continue
            intf_name = key['interface_name']
            queue_num = key['buffer_index_per_port']
            thresh = key['threshold']
            queue_name = "q{}".format(queue_num)
            queue_list = {queue_name:thresh}
            output[intf_name].update(queue_list)

    # Populate the array to print using jinja2 template
    for key in natsorted(output):
        table.append((key, output[key]['q0'], output[key]['q1'], output[key]['q2'], output[key]['q3'],
                    output[key]['q4'], output[key]['q5'], output[key]['q6'], output[key]['q7']))
    show_cli_output(renderer_template, table)
    return

def get_print_cpu_port_config(type, th_type, renderer_template):

    # Create a base dictionary with CPU queue name and zero values
    table = []
    output = {}
    for i in range(48):
        queue_name = "CPU:{}".format(i)
        output[queue_name] = {'q':0}

    # Now get threshold table and update the earlier dictionary with values got from threshold table
    path = cc.Path('/restconf/data/sonic-threshold:sonic-threshold/THRESHOLD_TABLE')
    api = cc.ApiClient()
    response = api.get(path)
    if not response.ok():
        print "%Error: REST API transaction failure for THRESHOLD_TABLE"
        return

    if response.content:
        for key in response.content['sonic-threshold:THRESHOLD_TABLE']['THRESHOLD_TABLE_LIST']:
            if key['interface_name'] != 'CPU':
                continue
            queue_num = key['buffer_index_per_port']
            intf_name = "CPU:{}".format(queue_num)
            thresh = key['threshold']
            queue_list = {'q':thresh}
            output[intf_name].update(queue_list)

    # Populate the array to print using jinja2 template
    for key in natsorted(output):
        table.append((key, output[key]['q']))
    show_cli_output(renderer_template, table)
    return


def invoke_api(func, args):
    body = None
    api = cc.ApiClient()

    # Set/Get the rules of all THRESHOLD_TABLE entries.
    if func == 'patch_sonic_threshold_sonic_threshold_threshold_table_threshold_table_list_threshold':
	path = cc.Path('/restconf/data/sonic-threshold:sonic-threshold/THRESHOLD_TABLE/THRESHOLD_TABLE_LIST')
        body = { "sonic-threshold:THRESHOLD_TABLE_LIST": [{ "buffer": args[1], "threshold_buffer_type": args[3], "interface_name": args[5], "buffer_index_per_port": int(args[2]), "threshold":  int(args[4]) }] }
        return api.patch(path, body)

    elif func == 'delete_sonic_threshold_sonic_threshold_threshold_table_threshold_table_list_threshold':
	path = cc.Path('/restconf/data/sonic-threshold:sonic-threshold/THRESHOLD_TABLE/THRESHOLD_TABLE_LIST={buffer},{threshold_buffer_type},{interface_name},{buffer_index_per_port}', buffer = args[2], threshold_buffer_type = args[4], interface_name = args[5], buffer_index_per_port = args[3] )
	return api.delete(path)

    elif func == 'delete_list_sonic_threshold_sonic_threshold_threshold_bufferpool_table_threshold_bufferpool_table_list':
	path = cc.Path('/restconf/data/sonic-threshold:sonic-threshold/THRESHOLD_BUFFERPOOL_TABLE/THRESHOLD_BUFFERPOOL_TABLE_LIST')
	return api.delete(path)

    elif func == 'patch_sonic_threshold_sonic_threshold_threshold_bufferpool_table_threshold_bufferpool_table_list_threshold':
        pool_name = args[0]
        pool_list = []
        path = cc.Path('/restconf/data/sonic-buffer-pool:sonic-buffer-pool/BUFFER_POOL')
        response = api.get(path)
        if not response.ok():
            print "%Error: REST API transaction failure for BUFFER_POOL"
            return False

        if not response.content:
            print "Buffer pool configuration missing on the system! Please configure buffer pools"
            return False

        for key in response.content['sonic-buffer-pool:BUFFER_POOL']['BUFFER_POOL_LIST']:
            pool_list.append(key['name'])

        if pool_name not in pool_list:
            print "Invalid pool {}, please configure a valid pool name from {}".format(pool_name, pool_list)
            return False

	path = cc.Path('/restconf/data/sonic-threshold:sonic-threshold/THRESHOLD_BUFFERPOOL_TABLE/THRESHOLD_BUFFERPOOL_TABLE_LIST')
        body = { "sonic-threshold:THRESHOLD_BUFFERPOOL_TABLE_LIST": [{ "pool_name": args[0], "threshold":  int(args[1]) }] }
        return api.patch(path, body)

    elif func == 'rpc_sonic_threshold_clear_threshold_breach':
	path = cc.Path('/restconf/operations/sonic-threshold:clear-threshold-breach')
	body = { "sonic-threshold:input":  {"breach_event_id":args[3] }}
	return api.post(path, body)

    elif func == 'rpc_sonic_buffer_pool_clear_buffer_pool_wm_stats':
	path = cc.Path('/restconf/operations/sonic-buffer-pool:clear-buffer-pool-wm-stats')
        body = { "sonic-buffer-pool:input":  {"watermark-type":args[0] }}
        return api.post(path, body)

    else:
       body = {}
    return api.cli_not_implemented(func)

def run(func, args):
    if func == 'get_threshold_breach_event_reports':
	get_threshold_breach_event_reports(args)
	return
    elif func == 'get_list_sonic_threshold_sonic_threshold_threshold_bufferpool_table_threshold_bufferpool_table_list':
        get_list_sonic_threshold_sonic_threshold_threshold_bufferpool_table_threshold_bufferpool_table_list(args)
	return
    elif func == 'get_list_sonic_threshold_sonic_threshold_threshold_table_threshold_table_list':
        get_list_sonic_threshold_sonic_threshold_threshold_table_threshold_table_list(args)
	return
    elif func == 'rpc_sonic_buffer_pool_get_buffer_pool_wm_stats':
	rpc_sonic_buffer_pool_get_buffer_pool_wm_stats(args)
	return
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
    else:
	print "%Error: REST API transaction failure"
    show_cli_output("show_threshold_breach_event_reports.j2", api_response)


def get_list_sonic_threshold_sonic_threshold_threshold_bufferpool_table_threshold_bufferpool_table_list(args):
    api_response = {}
    api = cc.ApiClient()
    path = cc.Path('/restconf/data/sonic-threshold:sonic-threshold/THRESHOLD_BUFFERPOOL_TABLE/THRESHOLD_BUFFERPOOL_TABLE_LIST')
    response = api.get(path)

    if response.ok():
        if response.content:
            api_response = response.content['sonic-threshold:THRESHOLD_BUFFERPOOL_TABLE_LIST']
            for i in range(len(api_response)):
                if 'pool_name' not in api_response[i] and 'threshold' not in api_response[i]:
                   print("Failed : Required mandatory parameters are not found")
                   return
        else:
            print("No buffer pool threshold entries found in DB")
    else:
        print "%Error: REST API transaction failure"
    show_cli_output("show_buffer_pool_threshold_config.j2", api_response)


def get_list_sonic_threshold_sonic_threshold_threshold_table_threshold_table_list(args):

    if args[0] == 'do':
        args[2] = args[3]
        args[3] = args[4]

    if args[2] == 'queue' and args[3] == 'unicast':
        renderer_template = "show_threshold_queue_unicast_config.j2"
    if args[2] == 'queue' and args[3] == 'multicast':
        renderer_template = "show_threshold_queue_multicast_config.j2"
    elif args[2] == 'priority-group' and args[3] == 'shared':
        renderer_template = "show_threshold_priority_group_config.j2"
    elif args[2] == 'priority-group' and args[3] == 'headroom':
        renderer_template = "show_threshold_priority_group_config.j2"
    elif args[2] == 'queue' and args[3] == 'CPU':
        renderer_template = "show_threshold_cpu_queue.j2"

    if args[2] == 'queue' and args[3] == 'CPU':
        get_print_cpu_port_config(args[2], args[3], renderer_template)
    else:
        get_print_all_port_config(args[2], args[3], renderer_template)


def rpc_sonic_buffer_pool_get_buffer_pool_wm_stats(args):

	watermark_stats_type = ''
        if (len(args) == 2):
            watermark_stats_type = args[1]
            renderer_template = "show_buffer_pool_stats_percentage.j2"
        else:
            watermark_stats_type = 'bytes'
            renderer_template = "show_buffer_pool_stats_bytes.j2"

	api_response = {}
	api = cc.ApiClient()
	path = cc.Path('/restconf/operations/sonic-buffer-pool:get-buffer-pool-wm-stats')
	body = { "sonic-buffer-pool:input":  {"watermark-stats-type":watermark_stats_type, "watermark-type":args[0]} }
	response = api.post(path, body)

	if response.ok():
		if response.content:
		    api_response = response.content['sonic-buffer-pool:output']['Buffer_pool_list']
		    if api_response:
			for i in range(len(api_response)):
			  if 'Poolname' not in api_response[i] and 'StatsValue' not in api_response[i]:
				print("Required parameters are not found in buffer pool stats payload")
				return
		else:
			print("Buffer pool configuration missing on the system! Please configure buffer pools ")
	else:
		print "%Error: REST API transaction failure for buffer pool stats"
	show_cli_output(renderer_template, api_response)


if __name__ == '__main__':
     pipestr().write(sys.argv)

     run(sys.argv[1], sys.argv[2:])
