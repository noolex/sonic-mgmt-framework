import sys
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output

def invoke_api(func, args):
    body = None
    api = cc.ApiClient()

    # Set/Get/Delete WATERMARK_TABLE/SNAPSHOT_TABLE table entries.

    if func == 'patch_sonic_watermark_sonic_watermark_watermark_table_watermark_table_list_interval':
       path = cc.Path('/restconf/data/sonic-watermark:sonic-watermark/WATERMARK_TABLE/WATERMARK_TABLE_LIST={telemetryIntarvalPrefix}/interval', telemetryIntarvalPrefix = 'TELEMETRY_INTERVAL')
       body = { "sonic-watermark:interval": int(args[3]) }
       return api.patch(path, body)

    elif func == 'patch_sonic_watermark_sonic_watermark_snapshot_table_snapshot_table_list_interval':
       path = cc.Path('/restconf/data/sonic-watermark:sonic-watermark/SNAPSHOT_TABLE/SNAPSHOT_TABLE_LIST={snapshotIntarvalPrefix}/interval', snapshotIntarvalPrefix = 'SNAPSHOT_INTERVAL')
       body = { "sonic-watermark:interval": int(args[2]) }
       return api.patch(path, body)

    elif func == 'delete_list_sonic_watermark_sonic_watermark_snapshot_table_snapshot_table_list':
       path = cc.Path('/restconf/data/sonic-watermark:sonic-watermark/SNAPSHOT_TABLE/SNAPSHOT_TABLE_LIST')
       return api.delete(path)

    elif func == 'delete_list_sonic_watermark_sonic_watermark_watermark_table_watermark_table_list':
       path = cc.Path('/restconf/data/sonic-watermark:sonic-watermark/WATERMARK_TABLE/WATERMARK_TABLE_LIST')
       return api.delete(path)

def get_list_sonic_watermark_sonic_watermark_watermark_table_watermark_table_list(args):
   
    api_response = {}
    api = cc.ApiClient()
    path = cc.Path('/restconf/data/sonic-watermark:sonic-watermark/WATERMARK_TABLE/WATERMARK_TABLE_LIST')
    response = api.get(path)

    if response.ok():
        if response.content:
            api_response = response.content['sonic-watermark:WATERMARK_TABLE_LIST']
            for i in range(len(api_response)):
                if 'interval' not in api_response[i]:
                   print("Failed : Required mandatory parameters are not found")
                   return
        else:
	    api_response = [{"interval":120}] 
    else:
        print "%Error: REST API transaction failure"
    show_cli_output("show_watermark_telemetry_interval.j2", api_response)


def get_list_sonic_watermark_sonic_watermark_snapshot_table_snapshot_table_list(args):

    api_response = {}
    api = cc.ApiClient()
    path = cc.Path('/restconf/data/sonic-watermark:sonic-watermark/SNAPSHOT_TABLE/SNAPSHOT_TABLE_LIST')
    response = api.get(path)

    if response.ok():
        if response.content:
            api_response = response.content['sonic-watermark:SNAPSHOT_TABLE_LIST']
            for i in range(len(api_response)):
                if 'interval' not in api_response[i]:
                   print("Failed : Required mandatory parameters are not found")
                   return
        else:
	    api_response = [{"interval":10}] 
    else:
        print "%Error: REST API transaction failure"
    show_cli_output("show_watermark_snapshot_interval.j2", api_response)


def run(func, args):
    
    if func == 'get_list_sonic_watermark_sonic_watermark_watermark_table_watermark_table_list':
	get_list_sonic_watermark_sonic_watermark_watermark_table_watermark_table_list(args)
	return
    elif func == 'get_list_sonic_watermark_sonic_watermark_snapshot_table_snapshot_table_list':
	get_list_sonic_watermark_sonic_watermark_snapshot_table_snapshot_table_list(args)
	return

    response = invoke_api(func, args)
    if response.ok():
        if response.content is not None:
            # Get Command Output
            api_response = response.content

            if api_response is None:
                print("Failed")
    else:
            api_response = response.content
            if "ietf-restconf:errors" in api_response:
                 err = api_response["ietf-restconf:errors"]
                 if "error" in err:
                     errList = err["error"]

                     errDict = {}
                     for dict in errList:
                         for k, v in dict.iteritems():
                              errDict[k] = v

                     if "error-message" in errDict:
                         print "%Error: " + errDict["error-message"]
                         return
                     print "%Error: Transaction Failure"
                     return
            print response.error_message()
            print "%Error: Transaction Failure"

if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]
    print(func)
    if func == 'get_list_sonic_watermark_sonic_watermark_watermark_table_watermark_table_list':
        get_list_sonic_watermark_sonic_watermark_watermark_table_watermark_table_list(sys.argv[2:])

    elif func == 'get_list_sonic_watermark_sonic_watermark_snapshot_table_snapshot_table_list':
        get_list_sonic_watermark_sonic_watermark_snapshot_table_snapshot_table_list(sys.argv[2:])

    else :
    	run(func, sys.argv[2:])
