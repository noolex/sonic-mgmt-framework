#!/usr/bin/python
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
import sys
import json
import collections
import re
import datetime
import cli_client as cc

from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
from natsort import natsorted
from swsssdk import ConfigDBConnector

debug = False

RESPONSE_OK         = 200
RESPONSE_NO_CONTENT = 204
RESPONSE_SRV_ERROR  = 500

Actions = { 'forward' : 'FORWARD', 'drop': 'DROP', 'alert': 'ALERT' }
Ables =   { 'enable' : 'ENABLE', 'disable': 'DISABLE' }
SORTED_GLOBAL_ORDER = ['poll-interval', 'counter-poll']
SORTED_INTERFACE_ORDER = ['action', 'detection-time', 'restoration-time']
DEFAULT_DETECTION_TIME = 200
DEFAULT_ACTION = 'drop'

PStats = collections.namedtuple('PStats', 'pfc0, pfc1, pfc2, pfc3, pfc4, pfc5, pfc6, pfc7')

counter_bucket_rx_dict = {
    'SAI_PORT_STAT_PFC_0_RX_PKTS': 0,
    'SAI_PORT_STAT_PFC_1_RX_PKTS': 1,
    'SAI_PORT_STAT_PFC_2_RX_PKTS': 2,
    'SAI_PORT_STAT_PFC_3_RX_PKTS': 3,
    'SAI_PORT_STAT_PFC_4_RX_PKTS': 4,
    'SAI_PORT_STAT_PFC_5_RX_PKTS': 5,
    'SAI_PORT_STAT_PFC_6_RX_PKTS': 6,
    'SAI_PORT_STAT_PFC_7_RX_PKTS': 7
}

counter_bucket_tx_dict = {
    'SAI_PORT_STAT_PFC_0_TX_PKTS': 0,
    'SAI_PORT_STAT_PFC_1_TX_PKTS': 1,
    'SAI_PORT_STAT_PFC_2_TX_PKTS': 2,
    'SAI_PORT_STAT_PFC_3_TX_PKTS': 3,
    'SAI_PORT_STAT_PFC_4_TX_PKTS': 4,
    'SAI_PORT_STAT_PFC_5_TX_PKTS': 5,
    'SAI_PORT_STAT_PFC_6_TX_PKTS': 6,
    'SAI_PORT_STAT_PFC_7_TX_PKTS': 7
}

STATS_LIST = [
    'PFC_WD_QUEUE_STATS_DEADLOCK_DETECTED', 'PFC_WD_QUEUE_STATS_DEADLOCK_RESTORED',
    'PFC_WD_QUEUE_STATS_TX_PACKETS',        'PFC_WD_QUEUE_STATS_TX_DROPPED_PACKETS',
    'PFC_WD_QUEUE_STATS_RX_PACKETS',        'PFC_WD_QUEUE_STATS_RX_DROPPED_PACKETS',
    'PFC_WD_QUEUE_STATS_TX_PACKETS_LAST',   'PFC_WD_QUEUE_STATS_TX_DROPPED_PACKETS_LAST',
    'PFC_WD_QUEUE_STATS_RX_PACKETS_LAST',   'PFC_WD_QUEUE_STATS_RX_DROPPED_PACKETS_LAST']

STATS_DISPLAY_ORDER = ['storm-detected', 'storm-restored', 'tx-ok', 'tx-drop', 'rx-ok', 'rx-drop', 'tx-ok-last', 'tx-drop-last', 'rx-ok-last', 'rx-drop-last']

STATUS_NA = 'N/A'
COUNTER_TABLE_PREFIX = 'COUNTERS:'
COUNTERS_PORT_NAME_MAP = 'COUNTERS_PORT_NAME_MAP'
COUNTERS_QUEUE_NAME_MAP = 'COUNTERS_QUEUE_NAME_MAP'
RX_COUNTERS = True
TX_COUNTERS = False

modName           = 'openconfig-qos-pfc-ext:'
globalPfcWdUri    = '/restconf/data/openconfig-qos:qos/openconfig-qos-ext:pfc-watchdog'
interfacePfcUri   = '/restconf/data/openconfig-qos:qos/interfaces/interface={intfName}/openconfig-qos-ext:pfc'
interfacePfcWdUri = interfacePfcUri + '/watchdog'

aa = cc.ApiClient()

def getKeyFromDictData(diction, value):
    if isinstance(diction, dict):
        for key, data in diction.items():
            if data == value:
                return key
    return None

def getPfcQueueCounters(counters_db, ifName, queue, counterId):
    """
        Get the counters from specific table.
    """
    err = None
    counters = []
    uriStat = interfacePfcUri
    keypath = cc.Path(uriStat +  '/pfc-queue/pfc-queue={queue}/statistics', intfName=ifName, queue=str(queue))
    response = aa.get(keypath)
    if (response is not None) and (response.ok()):
        if 'openconfig-qos-ext:statistics' in response.content.keys():
            data = response.content['openconfig-qos-ext:statistics']
            for stat in STATS_DISPLAY_ORDER:
                counters.append(data[stat])

    if not response.ok():
        counters = [0,0,0,0,0,0,0,0,0,0]
        err = response.error_message()

    return (err, counters)

def getPauseCounters(counters_db, ifName, rx, counterId):
    """
        Get the counters from specific table.
    """
    err = None
    pause = [0,0,0,0,0,0,0,0]
    uriStat = interfacePfcUri
    pause = []
    for cos in range(0,8):
        keypath = cc.Path(uriStat +  '/pfc-priorities/pfc-priority={dot1p}/state/statistics', intfName=ifName, dot1p=str(cos))
        response = aa.get(keypath)
        if (response is not None) and (response.ok()):
            if 'openconfig-qos-ext:statistics' in response.content.keys():
                data = response.content['openconfig-qos-ext:statistics']
                #key = 'pfc' + str(cos)
                if rx:
                    pause.append(data['pause-frames-rx'])
                else:
                    pause.append(data['pause-frames-tx'])
    if not response.ok():
        err = response.error_message()

    return (err, pause)
    ########### This will be the equivalent of get_counters.

def invoke(func, args):
    body = None   
    field_val = None
    bodyParam = None
   
    if func == 'interval':
        if len(args) == 0:
            keypath = cc.Path(globalPfcWdUri + '/poll/config')
            return aa.delete(keypath)
        else:
            keypath = cc.Path(globalPfcWdUri + '/poll/config/poll-interval')
            body = {"openconfig-qos-ext:poll-interval" : int(args[0])}
            return aa.patch(keypath, body)

    elif func == 'counter-poll' :
        keypath = cc.Path(globalPfcWdUri + '/flex/config/counter-poll')
        body = {"openconfig-qos-ext:counter-poll" : Ables[args[0]]}
        return aa.patch(keypath, body)

    elif func == 'pfcwd_if_action':
        keypath = cc.Path(interfacePfcWdUri + '/config/action', intfName=args[0])
        action = Actions[args[1]]
        body = {"openconfig-qos-ext:action" : action}
        return aa.patch(keypath, body)
   
    elif func == 'pfcwd_if_no_action':
        keypath = cc.Path(interfacePfcWdUri + '/config/action', intfName=args[0])
        return aa.delete(keypath)
   
    elif func == 'pfcwd_if_detect':
        keypath = cc.Path(interfacePfcWdUri + '/config/detection-time', intfName=args[0])
        body = {"openconfig-qos-ext:detection-time" : int(args[1])}
        return aa.patch(keypath, body)
   
    elif func == 'pfcwd_if_no_detect':
        keypath = cc.Path(interfacePfcWdUri + '/config/detection-time', intfName=args[0])
        return aa.delete(keypath)

    elif func == 'pfcwd_if_restore':
        keypath = cc.Path(interfacePfcWdUri + '/config/restoration-time', intfName=args[0])
        body = {"openconfig-qos-ext:restoration-time" : int(args[1])}
        return aa.patch(keypath, body)
   
    elif func == 'pfcwd_if_no_restore':
        keypath = cc.Path(interfacePfcWdUri + '/config/restoration-time', intfName=args[0])
        return aa.delete(keypath)

    if func == 'pfcwd_if_enable':
      # (sonic-cli-qos-pfc) run =  pfcwd_if_enable 2 ['Ethernet16', 'off']
        if len(args) < 2:
            return None
        if args[1] == 'off':
            keypath = cc.Path(interfacePfcWdUri + '/config', intfName=args[0])
            response = aa.delete(keypath)

        elif args[1] == 'on':
            keypath = cc.Path(interfacePfcWdUri + '/state', intfName=args[0])
            response = aa.get(keypath, body)
            cfg = {}
            if response.ok():
                if 'openconfig-qos-ext:state' in response.content.keys():
                    cfg = response.content['openconfig-qos-ext:state']

            defaults = {}
            if 'action' in cfg.keys():
                action = cfg['action']
            else:
                action = Actions[DEFAULT_ACTION]
            defaults['action'] = action

            if 'detection-time' in cfg.keys():
                detectTime = cfg['detection-time']
            else:
                detectTime = DEFAULT_DETECTION_TIME
            defaults['detection-time'] = detectTime

            if 'restoration-time' in cfg.keys():
                restoreTime = cfg['restoration-time']
            else:
                restoreTime = 2 * detectTime
            defaults['restoration-time'] = restoreTime

            if restoreTime < (2 * detectTime):
                print "Warning: restoration time (" + str(restoreTime) + ") is less than twice detection time(" + str(detectTime) + ")."

            body = collections.defaultdict(dict)
            body['config'] = defaults

            keypath = cc.Path(interfacePfcWdUri + '/config', intfName=args[0])

            response = aa.patch(keypath, body)
        return response

    elif func == 'show_pfc_watchdog':
        # show_pfc_watchdog 1 ['show_pfc_watchdog.j2']
        interval="Not Available"
        keypath = cc.Path(globalPfcWdUri + '/poll/config/poll-interval')
        response = aa.get(keypath, body)
        if response.ok():
            if 'openconfig-qos-ext:poll-interval' in response.content.keys():
                interval = response.content['openconfig-qos-ext:poll-interval']
        keypath = cc.Path(globalPfcWdUri + '/flex/config/counter-poll')
        response = aa.get(keypath, body)
        poll="Not Available"
        if response.ok():
            if 'openconfig-qos-ext:counter-poll' in response.content.keys():
                poll = response.content['openconfig-qos-ext:counter-poll']
                # find key based on dictionary value
                for key, data in Ables.items():
                    if data == poll:
                        poll = key + 'd'
       
        datam = {}
        datam['poll-interval'] = interval
        datam['counter-poll'] = poll
        order = []
        for key in SORTED_GLOBAL_ORDER:
            if datam.has_key(key):
                order.append(key)
        tuples = [(key, datam[key]) for key in order]
        response=aa.cli_not_implemented("")      # Just to get the proper format to return data and status
        response.status_code = RESPONSE_OK
        response.content = collections.OrderedDict(tuples)
        return response
   
    elif func == 'show_port_pfc_watchdog':
        datam = {}

        datam['action'] =  "N/A"
        datam['detection-time'] =  "0"
        datam['restoration-time'] = "0"
        
        keypath = cc.Path(interfacePfcWdUri + '/state', intfName=args[0])
        response = aa.get(keypath, body)
        if response.ok():
            if 'openconfig-qos-ext:state' in response.content.keys():
                state = response.content['openconfig-qos-ext:state']
                if 'action' in state.keys():
                    action = state['action']
                    action = getKeyFromDictData(Actions, action)
                    if action != None:
                        datam['action'] = action
                if 'detection-time' in state.keys():
                    datam['detection-time'] =  state['detection-time']
                if 'restoration-time' in state.keys():
                    datam['restoration-time'] = state['restoration-time']
      
        order = []
        for key in SORTED_INTERFACE_ORDER:
            if datam.has_key(key):
                order.append(key)
        tuples = [(key, datam[key]) for key in order]
      
        response=aa.cli_not_implemented("interface")      # Just to get the proper format to return data and status
        response.status_code = RESPONSE_OK
        response.content = collections.OrderedDict(tuples)
        return response

    elif func == 'show_port_pfc_statistics':
        ifName=args[0]
        counters_db = ConfigDBConnector()
        counters_db.db_connect('COUNTERS_DB')
        counter_port_name_map = counters_db.get_all(counters_db.COUNTERS_DB, COUNTERS_PORT_NAME_MAP)
        # Build a dictionary of the stats
        # Time is only required when clearing the stats
        pauseRx = collections.OrderedDict()
#        pauseRx['time'] = datetime.datetime.now()
        pauseTx = collections.OrderedDict()
#        pauseTx['time'] = datetime.datetime.now()
        if counter_port_name_map is not None:
            for port in natsorted(counter_port_name_map):
                if port == ifName:
                    err, pauseRx[ifName] = getPauseCounters(counters_db, ifName, RX_COUNTERS, counter_port_name_map[port])
                    if not err == None:
                        break
                    err, pauseTx[ifName] = getPauseCounters(counters_db, ifName, TX_COUNTERS, counter_port_name_map[port])
                    if not err == None:
                        break

        response=aa.cli_not_implemented("")      # Just to get the proper format to return data and status
        if len(pauseRx[ifName]) == 0:
            response.status_code = RESPONSE_NO_CONTENT
            response.set_error_message("No Content Found")
            response.content = None
        elif err == None:
            ifFrames = {}
            fcFrames = {}
            ifFrames['rx'] = pauseRx[ifName]
            ifFrames['tx'] = pauseTx[ifName]
            fcFrames[ifName] = ifFrames
            response.status_code = RESPONSE_OK
            response.content = collections.OrderedDict(fcFrames)
        else: 
            response.status_code = RESPONSE_SRV_ERROR
            response.set_error_message(err)
            response.content = None
        return response

    elif func == 'show_port_pfc_queue_statistics':
        ifName=args[0]
        err = None
        counters_db = ConfigDBConnector()
        counters_db.db_connect('COUNTERS_DB')
        queue_names_map       = counters_db.get_all(counters_db.COUNTERS_DB, COUNTERS_QUEUE_NAME_MAP)
        pfcQueueCounters = collections.OrderedDict()
        for key in natsorted(queue_names_map.keys()):
            if key.startswith(ifName):
                _, queue = key.split(':', 1)
                err, pfcQueueCounters[queue] = getPfcQueueCounters(counters_db, ifName, queue, queue_names_map[key])

        response=aa.cli_not_implemented("")      # Just to get the proper format to return data and status
        if len(pfcQueueCounters) == 0:
            response.status_code = RESPONSE_NO_CONTENT
            response.set_error_message("No Content Found")
            response.content = None
        elif err == None:
            response.status_code = RESPONSE_OK
            data = {}
            data[ifName] = pfcQueueCounters
            response.content = collections.OrderedDict(data)
        else: 
            response.status_code = RESPONSE_SRV_ERROR
            response.set_error_message(err)
            response.content = None
        return response

    else:
        print("%Error: not implemented")
        exit(1)

def run(func, args):
    if debug == True:
        print "(sonic-cli-qos-pfc) run = ", func, len(args), args
    try:
        api_response = invoke(func, args)
        if debug == True:
            print api_response.status_code
        if api_response is None:
            return
        elif api_response.ok():
            response = api_response.content
            if debug == True:
                print response
            if func.startswith('show_'):
                if api_response.status_code == RESPONSE_NO_CONTENT:
                    message = api_response.error_message()
                    print message[7:]
                elif func.startswith('show_port'):
                    show_cli_output(args[1], response)
                elif func.startswith('show_pfc'):
                    show_cli_output(args[0], response)
            elif response is None:
                return
            else:
                print "%Error: Invalid command"
        else:
            #error response
            print api_response.error_message()
   
    except Exception as e:
        # system/network error
        print "%Error: Transaction Failure"
   
if __name__ == '__main__':
    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])
