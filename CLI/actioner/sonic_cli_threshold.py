import sys
import json
import collections
import re
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
from swsssdk import ConfigDBConnector
from swsssdk import SonicV2Connector
from natsort import natsorted

headerPg = ['Port', 'PG0', 'PG1', 'PG2', 'PG3', 'PG4', 'PG5', 'PG6', 'PG7']
headerUc = ['Port', 'UC0', 'UC1', 'UC2', 'UC3', 'UC4', 'UC5', 'UC6', 'UC7']
headerMc = ['Port', 'MC0', 'MC1', 'MC2', 'MC3', 'MC4', 'MC5', 'MC6', 'MC7']
headerCpu = ['Queue', 'Percent']

THRESHOLD_DEFAULT = 0

QUEUE_TYPE_MC = 'MC'
QUEUE_TYPE_UC = 'UC'
QUEUE_TYPE_ALL = 'ALL'
SAI_QUEUE_TYPE_MULTICAST = "SAI_QUEUE_TYPE_MULTICAST"
SAI_QUEUE_TYPE_UNICAST = "SAI_QUEUE_TYPE_UNICAST"
SAI_QUEUE_TYPE_ALL = "SAI_QUEUE_TYPE_ALL"

THRESHOLD_TABLE_PREFIX = "THRESHOLD_TABLE|"

COUNTERS_PORT_NAME_MAP = "COUNTERS_PORT_NAME_MAP"
COUNTERS_QUEUE_NAME_MAP = "COUNTERS_QUEUE_NAME_MAP"
COUNTERS_QUEUE_TYPE_MAP = "COUNTERS_QUEUE_TYPE_MAP"
COUNTERS_QUEUE_INDEX_MAP = "COUNTERS_QUEUE_INDEX_MAP"
COUNTERS_QUEUE_PORT_MAP = "COUNTERS_QUEUE_PORT_MAP"
COUNTERS_PG_NAME_MAP = "COUNTERS_PG_NAME_MAP"
COUNTERS_PG_PORT_MAP = "COUNTERS_PG_PORT_MAP"
COUNTERS_PG_INDEX_MAP = "COUNTERS_PG_INDEX_MAP"

class Thresholdcfg(object):

    def __init__(self):
        # connect COUNTER DB
        self.counters_db = SonicV2Connector(host='127.0.0.1')
        self.counters_db.connect(self.counters_db.COUNTERS_DB)

        # connect APP DB
        self.config_db = ConfigDBConnector()
        self.config_db.connect()

        self.num_uc_queues = 0

        def get_queue_type(table_id):
            queue_type = self.counters_db.get(self.counters_db.COUNTERS_DB, COUNTERS_QUEUE_TYPE_MAP, table_id)
            if queue_type is None:
                print "Queue Type is not available!", table_id
                sys.exit(1)
            elif queue_type == SAI_QUEUE_TYPE_MULTICAST:
                return QUEUE_TYPE_MC

            elif queue_type == SAI_QUEUE_TYPE_UNICAST:
                return QUEUE_TYPE_UC
            elif queue_type == SAI_QUEUE_TYPE_ALL:
                return QUEUE_TYPE_ALL
            else:
                print "Queue Type is invalid:", table_id, queue_type
                sys.exit(1)

        def get_queue_port(table_id):
            port_table_id = self.counters_db.get(self.counters_db.COUNTERS_DB, COUNTERS_QUEUE_PORT_MAP, table_id)
            if port_table_id is None:
                print "Port is not available!", table_id
                sys.exit(1)

            return port_table_id

        def get_pg_port(table_id):
            port_table_id = self.counters_db.get(self.counters_db.COUNTERS_DB, COUNTERS_PG_PORT_MAP, table_id)
            if port_table_id is None:
                print "Port is not available!", table_id
                sys.exit(1)

            return port_table_id

        # Get all ports
        self.counter_port_name_map = self.counters_db.get_all(self.counters_db.COUNTERS_DB, COUNTERS_PORT_NAME_MAP)
        if self.counter_port_name_map is None:
            print "COUNTERS_PORT_NAME_MAP is empty!"
            sys.exit(1)

        self.port_uc_queues_map = {}
        self.port_mc_queues_map = {}
        self.port_pg_map = {}
        self.port_name_map = {}

        for port in self.counter_port_name_map:
            self.port_uc_queues_map[port] = {}
            self.port_mc_queues_map[port] = {}
            self.port_pg_map[port] = {}
            self.port_name_map[self.counter_port_name_map[port]] = port

        # Get Queues for each port
        counter_queue_name_map = self.counters_db.get_all(self.counters_db.COUNTERS_DB, COUNTERS_QUEUE_NAME_MAP)
        if counter_queue_name_map is None:
            print "COUNTERS_QUEUE_NAME_MAP is empty!"
            sys.exit(1)

        for queue in counter_queue_name_map:
            port = self.port_name_map[get_queue_port(counter_queue_name_map[queue])]
            if get_queue_type(counter_queue_name_map[queue]) == QUEUE_TYPE_UC:
                self.port_uc_queues_map[port][queue] = counter_queue_name_map[queue]

            elif get_queue_type(counter_queue_name_map[queue]) == QUEUE_TYPE_MC:
                self.port_mc_queues_map[port][queue] = counter_queue_name_map[queue]

        # Get PGs for each port
        counter_pg_name_map = self.counters_db.get_all(self.counters_db.COUNTERS_DB, COUNTERS_PG_NAME_MAP)
        if counter_pg_name_map is None:
            print "COUNTERS_PG_NAME_MAP is empty!"
            sys.exit(1)

        for pg in counter_pg_name_map:
            port = self.port_name_map[get_pg_port(counter_pg_name_map[pg])]
            self.port_pg_map[port][pg] = counter_pg_name_map[pg]

        for queue in counter_queue_name_map:
            port = self.port_name_map[get_queue_port(counter_queue_name_map[queue])]
            if port == 'CPU':
                continue
            self.num_uc_queues = len(self.port_uc_queues_map[port])
            break

        self.threshold_types = {
            "pg_headroom": {"message": "Ingress headroom threshold per PG:",
                           "obj_map": self.port_pg_map,
                           "idx_func": self.get_pg_index,
                           "th_name": "threshold",
                           "header": headerPg},
            "pg_shared": {"message": "Ingress shared pool threshold per PG:",
                          "obj_map": self.port_pg_map,
                          "idx_func": self.get_pg_index,
                          "th_name": "threshold",
                          "header": headerPg},
            "q_shared_uni": {"message": "Egress shared pool threshold per unicast queue:",
                            "obj_map": self.port_uc_queues_map,
                            "idx_func": self.get_queue_index,
                            "th_name": "threshold",
                            "header": headerUc},
            "q_shared_multi": {"message": "Egress shared pool threshold per multicast queue:",
                            "obj_map": self.port_mc_queues_map,
                            "idx_func": self.get_queue_index,
                            "th_name": "threshold",
                            "header": headerMc},
            "q_shared_multi_cpu": {"message": "Egress shared pool threshold per CPU queue:",
                            "obj_map": self.port_mc_queues_map,
                            "idx_func": self.get_queue_index,
                            "th_name": "threshold",
                            "header": headerCpu}
        }

    def get_queue_index(self, table_id):
        queue_index = self.counters_db.get(self.counters_db.COUNTERS_DB, COUNTERS_QUEUE_INDEX_MAP, table_id)
        if queue_index is None:
            print "Queue index is not available!", table_id
            sys.exit(1)

        return queue_index

    def get_pg_index(self, table_id):
        pg_index = self.counters_db.get(self.counters_db.COUNTERS_DB, COUNTERS_PG_INDEX_MAP, table_id)
        if pg_index is None:
            print "Priority group index is not available!", table_id
            sys.exit(1)

        return pg_index

    def get_counters(self, table_prefix, port, port_obj, idx_func, threshold, th_type):
        """
            Get the threshold from specific table.
        """

        fields = ["0"]*8
        if th_type == "q_shared_uni" or th_type == "q_shared_multi":
            fields = ["0"]*self.num_uc_queues

        elif th_type == "q_shared_multi_cpu":
            fields = ["0"]*48

        for name, obj_id in port_obj.items():
            pos = int(idx_func(obj_id)) % len(fields)
            full_table_id = table_prefix + port + '|' + str(pos)
            threshold_data = self.config_db.get(self.config_db.CONFIG_DB, full_table_id, threshold)

            if threshold_data is None:
                fields[pos] = THRESHOLD_DEFAULT
            elif fields[pos] != THRESHOLD_DEFAULT:
                fields[pos] = str(int(threshold_data))

        cntr = tuple(fields)
        return cntr

    def get_print_cpu_queue_stat(self, table_prefix, type, th_type, renderer_template):
        table = []
        array_of_cpu = self.port_mc_queues_map["CPU"]
        for item in natsorted(array_of_cpu):
            queue = item.split(':')
            key = table_prefix + queue[1]
            data = self.config_db.get(self.config_db.CONFIG_DB, key, "threshold")
            if data is None:
               data = 0
            table.append((item, data))
        show_cli_output(renderer_template, table)
        return

    def get_print_all_stat(self, table_prefix, type, th_type, renderer_template):
        # Get stat for each port
        table = []
        for port in natsorted(self.counter_port_name_map):
            if port == 'CPU':
                continue
            data = self.get_counters(table_prefix, port,
                                     type["obj_map"][port], type["idx_func"], type["th_name"], th_type)
            table.append((port, data[0], data[1], data[2], data[3],
                        data[4], data[5], data[6], data[7]))
        show_cli_output(renderer_template, table)
        return

def invoke_api(func, args):
    body = None
    api = cc.ApiClient()

    # Set/Get the rules of all THRESHOLD_TABLE entries.
    if func == 'patch_sonic_threshold_sonic_threshold_threshold_table_threshold_table_list_threshold':
	path = cc.Path('/restconf/data/sonic-threshold:sonic-threshold/THRESHOLD_TABLE/THRESHOLD_TABLE_LIST={buffer},{threshold_buffer_type},{interface_name},{buffer_index_per_port}/threshold', buffer = args[1], threshold_buffer_type = args[3], interface_name = args[5], buffer_index_per_port = args[2] )
        body = { "sonic-threshold:threshold":  int(args[4]) }
        return api.patch(path, body)

    elif func == 'delete_sonic_threshold_sonic_threshold_threshold_table_threshold_table_list_threshold':
	path = cc.Path('/restconf/data/sonic-threshold:sonic-threshold/THRESHOLD_TABLE/THRESHOLD_TABLE_LIST={buffer},{threshold_buffer_type},{interface_name},{buffer_index_per_port}/threshold', buffer = args[2], threshold_buffer_type = args[4], interface_name = args[5], buffer_index_per_port = args[3] )
	return api.delete(path)

    elif func == 'patch_sonic_threshold_sonic_threshold_threshold_table_buffer_pool_list_threshold':
        pool_name = args[0]
	config_db = ConfigDBConnector()
	config_db.connect()
	counters_db = SonicV2Connector(host='127.0.0.1')
	counters_db.connect(counters_db.COUNTERS_DB)
	buffer_pool_name_to_oid_map = counters_db.get_all(counters_db.COUNTERS_DB, "COUNTERS_BUFFER_POOL_NAME_MAP")
	if pool_name not in buffer_pool_name_to_oid_map:
		print("Invalid pool name, please configure a valid pool name")
		return False
	path = cc.Path('/restconf/data/sonic-threshold:sonic-threshold/THRESHOLD_TABLE/BUFFER_POOL_LIST={bufferpoolprefix},{pool_name}/threshold', bufferpoolprefix = 'BUFFER_POOL', pool_name = args[0] )
        body = { "sonic-threshold:threshold":  int(args[1]) }
        return api.patch(path, body)
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
    else:
	print "%Error: REST API transaction failure"
    show_cli_output("show_threshold_breach_event_reports.j2", api_response)


def get_list_sonic_threshold_sonic_threshold_threshold_table_buffer_pool_list(args):
    api_response = {}
    api = cc.ApiClient()
    path = cc.Path('/restconf/data/sonic-threshold:sonic-threshold/THRESHOLD_TABLE/BUFFER_POOL_LIST')
    response = api.get(path)

    if response.ok():
        if response.content:
            api_response = response.content['sonic-threshold:BUFFER_POOL_LIST']
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

    if args[3] == 'queue' and args[0] == 'unicast':
        th_type = "q_shared_uni"
        renderer_template = "show_threshold_queue_unicast_config.j2"
    if args[3] == 'queue' and args[0] == 'multicast':
        th_type = "q_shared_multi"
        renderer_template = "show_threshold_queue_multicast_config.j2"
    elif args[3] == 'priority-group' and args[0] == 'shared':
        th_type = "pg_shared"
        renderer_template = "show_threshold_priority_group_config.j2"
    elif args[3] == 'priority-group' and args[0] == 'headroom':
        th_type = "pg_headroom"
        renderer_template = "show_threshold_priority_group_config.j2"
    elif args[3] == 'queue' and args[0] == 'CPU':
        th_type = "q_shared_multi_cpu"
        renderer_template = "show_threshold_cpu_queue.j2"

    thresholdcfg = Thresholdcfg()
    if th_type is not None:
        if th_type == "pg_shared":
            table_prefix = THRESHOLD_TABLE_PREFIX + "priority-group" + "|" + "shared" + "|"
        elif th_type == "pg_headroom":
            table_prefix = THRESHOLD_TABLE_PREFIX + "priority-group" + "|" + "headroom" + "|"
        elif th_type == "q_shared_uni":
            table_prefix = THRESHOLD_TABLE_PREFIX + "queue" + "|" + "unicast" + "|"
        elif th_type == "q_shared_multi":
            table_prefix = THRESHOLD_TABLE_PREFIX + "queue" + "|" + "multicast" + "|"
        elif th_type == "q_shared_multi_cpu":
            table_prefix = THRESHOLD_TABLE_PREFIX + "queue" + "|" + "multicast" + "|"+ "CPU" + "|"
            thresholdcfg.get_print_cpu_queue_stat(table_prefix, thresholdcfg.threshold_types[th_type], th_type, renderer_template)
            sys.exit(0)
        thresholdcfg.get_print_all_stat(table_prefix, thresholdcfg.threshold_types[th_type], th_type, renderer_template)
    sys.exit(0)

if __name__ == '__main__':
     pipestr().write(sys.argv)
     func = sys.argv[1]

     if func == 'get_threshold_breach_event_reports':
        get_threshold_breach_event_reports(sys.argv[2:])
     elif func == 'get_list_sonic_threshold_sonic_threshold_threshold_table_buffer_pool_list':
        get_list_sonic_threshold_sonic_threshold_threshold_table_buffer_pool_list(sys.argv[2:])
     elif func == 'get_list_sonic_threshold_sonic_threshold_threshold_table_threshold_table_list':
        get_list_sonic_threshold_sonic_threshold_threshold_table_threshold_table_list(sys.argv[2:])
     else:
        run(sys.argv[1], sys.argv[2:])
