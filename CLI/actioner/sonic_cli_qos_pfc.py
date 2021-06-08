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
import syslog as log

from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
from natsort import natsorted

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

counterBucketRxDict = {
    'SAI_PORT_STAT_PFC_0_RX_PKTS': 0,
    'SAI_PORT_STAT_PFC_1_RX_PKTS': 1,
    'SAI_PORT_STAT_PFC_2_RX_PKTS': 2,
    'SAI_PORT_STAT_PFC_3_RX_PKTS': 3,
    'SAI_PORT_STAT_PFC_4_RX_PKTS': 4,
    'SAI_PORT_STAT_PFC_5_RX_PKTS': 5,
    'SAI_PORT_STAT_PFC_6_RX_PKTS': 6,
    'SAI_PORT_STAT_PFC_7_RX_PKTS': 7
}

counterBucketTxDict = {
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

def getPfcQueueCounters(ifName, queue):
    """
        Get the counters from specific table.
    """
    err = None
    counters = []
    uriStat = interfacePfcUri
    keypath = cc.Path(uriStat +  '/pfc-queue/pfc-queue={queue}/statistics', intfName=ifName, queue=str(queue))
    response = aa.get(keypath, None, False)
    if (response is not None) and (response.ok()) and (response.content is not None):
        if 'openconfig-qos-ext:statistics' in response.content.keys():
            data = response.content['openconfig-qos-ext:statistics']
            for stat in STATS_DISPLAY_ORDER:
                counters.append(data[stat])

    if (response is not None) and (not response.ok()):
        counters = [0,0,0,0,0,0,0,0,0,0]
        err = response.error_message()

    return (err, counters)

def getPauseCounters(ifName, rx):
    """
        Get the counters from specific table.
    """
    err = None
    pause = []
    uriStat = interfacePfcUri
    for cos in range(0,8):
        keypath = cc.Path(uriStat +  '/pfc-priorities/pfc-priority={dot1p}/state/statistics', intfName=ifName, dot1p=str(cos))
        response = aa.get(keypath, None, False)
        if (response is not None) and (response.ok()) and (response.content is not None):
            if 'openconfig-qos-ext:statistics' in response.content.keys():
                data = response.content['openconfig-qos-ext:statistics']
                #key = 'pfc' + str(cos)
                if rx:
                    pause.append(int(data['pause-frames-rx'], 10))
                else:
                    pause.append(int(data['pause-frames-tx'], 10))

    if len(pause) < 8:
        err = '{0}: unable to fetch pause counters'.format(ifName)

    return (err, pause)

def getPortList():
    path = cc.Path('/restconf/data/sonic-port:sonic-port/PORT/PORT_LIST')
    response = aa.get(path, None, False)
    portList = []
    intfList = {}
    if response.ok() and (response.content is not None) and ('sonic-port:PORT_LIST' in response.content):
        intfList = response.content['sonic-port:PORT_LIST']
        for intf in intfList:
            intfName = intf.get('ifname')
            # ALIAS mode is not supported in the PFC WD transformers
            # And the transformers ought to be revised later to have
            # getPortList() totally removed/replaced
            if (intfName is None) or (not intfName.startswith('Eth')):
                continue
            portList.append(intfName)
    return natsorted(portList)

def getPfcStatistics(ifName):
    err = None
    response = aa.cli_not_implemented("")
    response.status_code = RESPONSE_NO_CONTENT
    response.set_error_message("No Content Found")
    response.content = collections.OrderedDict()

    # Build a dictionary of the stats
    pauseRx = collections.OrderedDict()
    pauseTx = collections.OrderedDict()
    err, pauseRx[ifName] = getPauseCounters(ifName, RX_COUNTERS)
    if err is not None:
        response.set_error_message(err)
        return response
    err, pauseTx[ifName] = getPauseCounters(ifName, TX_COUNTERS)
    if err is not None:
        response.set_error_message(err)
        return response

    ifFrames = {}
    fcFrames = {}
    ifFrames['rx'] = pauseRx[ifName]
    ifFrames['tx'] = pauseTx[ifName]
    fcFrames[ifName] = ifFrames
    response.status_code = RESPONSE_OK
    response.content = collections.OrderedDict(fcFrames)
    return response

def getPfcQueueStatistics(ifName):
    path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/output/queues', interface_id=ifName)
    response = aa.get(path, None, False)
    ques = []
    if response.ok() and (response.content is not None) and ('openconfig-qos:queues' in response.content):
        queues = response.content['openconfig-qos:queues']['queue']
        for queue in queues:
            _, q = queue['state']['name'].split(':', 1)
            ques.append((int(q)))
        ques = sorted(ques)
        err = None
        pfcQueueCounters = collections.OrderedDict()
        for q in ques:
            err, pfcQueueCounters[q] = getPfcQueueCounters(ifName, q)

        response = aa.cli_not_implemented("")      # Just to get the proper format to return data and status
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

def getQosIntfSummary(ifName):
    info = { ifName: {} }

    path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/output/scheduler-policy/config', interface_id=ifName)
    data = aa.get(path, None, False)
    if (not data.ok()) or (not data.content):
        data.content = {}
        data.content['openconfig-qos:config'] = {'name':''}
    info[ifName].update({'policy': data.content['openconfig-qos:config']['name']})

    path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/openconfig-qos-maps-ext:interface-maps/config', interface_id=ifName)
    data = aa.get(path, None, False)
    if (not data.ok()) or (not data.content):
        data.content = {}
        data.content['openconfig-qos-maps-ext:config'] = {
            'dscp-to-forwarding-group':'',
            'dot1p-to-forwarding-group':'',
            'forwarding-group-to-queue':'',
            'forwarding-group-to-priority-group':'',
            'forwarding-group-to-dscp':'',
            'forwarding-group-to-dot1p':'',
            'pfc-priority-to-queue':''
        }
    info[ifName].update({'interface-maps': data.content['openconfig-qos-maps-ext:config']})

    path = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/interface={interface_id}/openconfig-qos-ext:pfc', interface_id=ifName)
    data = aa.get(path, None, False)
    if (not data.ok()) or (not data.content):
        data.content = {}
        data.content['openconfig-qos-ext:pfc'] = {}
    info[ifName].update({'pfc': data.content['openconfig-qos-ext:pfc']})

    response = data
    response.status_code = RESPONSE_OK
    response.content = info
    return response

def invoke(func, args):
    body = None

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
        keypath = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/')
        interface = args[0]
        action = Actions[args[1]]
        body = {"openconfig-qos:interfaces": {"interface": [{"interface-id": interface, "config": {"interface-id": interface}, "openconfig-qos-ext:pfc": {"watchdog": {"config": {"action": action}}, }}]}}
        return aa.patch(keypath, body)

    elif func == 'pfcwd_if_no_action':
        keypath = cc.Path(interfacePfcWdUri + '/config/action', intfName=args[0])
        return aa.delete(keypath)

    elif func == 'pfcwd_if_detect':
        keypath = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/')
        interface = args[0]
        body = {"openconfig-qos:interfaces": {"interface": [{"interface-id": interface, "config": {"interface-id": interface}, "openconfig-qos-ext:pfc": {"watchdog": {"config": {"detection-time": int(args[1])}}, }}]}}
        return aa.patch(keypath, body)

    elif func == 'pfcwd_if_no_detect':
        keypath = cc.Path(interfacePfcWdUri + '/config/detection-time', intfName=args[0])
        return aa.delete(keypath)

    elif func == 'pfcwd_if_restore':
        keypath = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/')
        interface = args[0]
        body = {"openconfig-qos:interfaces": {"interface": [{"interface-id": interface, "config": {"interface-id": interface}, "openconfig-qos-ext:pfc": {"watchdog": {"config": {"restoration-time": int(args[1])}}, }}]}}
        return aa.patch(keypath, body)

    elif func == 'pfcwd_if_no_restore':
        keypath = cc.Path(interfacePfcWdUri + '/config/restoration-time', intfName=args[0])
        return aa.delete(keypath)

    if func == 'pfcwd_if_enable':
        if len(args) < 2:
            return None
        if args[1] == 'off':
            keypath = cc.Path(interfacePfcWdUri + '/config', intfName=args[0])
            response = aa.delete(keypath)

        elif args[1] == 'on':
            keypath = cc.Path(interfacePfcWdUri + '/state', intfName=args[0])
            response = aa.get(keypath, None, False)
            cfg = {}
            if response.ok() and (response.content is not None):
                if 'openconfig-qos-ext:state' in response.content.keys():
                    cfg = response.content['openconfig-qos-ext:state']

            if 'action' in cfg.keys():
                action = cfg['action']
            else:
                action = Actions[DEFAULT_ACTION]

            if 'detection-time' in cfg.keys():
                detectTime = cfg['detection-time']
            else:
                detectTime = DEFAULT_DETECTION_TIME

            if 'restoration-time' in cfg.keys():
                restoreTime = cfg['restoration-time']
            else:
                restoreTime = 2 * detectTime

            if restoreTime < (2 * detectTime):
                print "Warning: restoration time (" + str(restoreTime) + ") is less than twice detection time(" + str(detectTime) + ")."

            interface = args[0]

            keypath = cc.Path('/restconf/data/openconfig-qos:qos/interfaces/')
            body = {"openconfig-qos:interfaces": {"interface": [{"interface-id": interface, "config": {"interface-id": interface},
                    "openconfig-qos-ext:pfc": {"watchdog": {"config": {"action": action, "detection-time": detectTime, "restoration-time": restoreTime}},}}]}}
            response = aa.patch(keypath, body)
        return response

    elif func == 'show_pfc_watchdog':
        interval="Not Available"
        keypath = cc.Path(globalPfcWdUri + '/poll/config/poll-interval')
        response = aa.get(keypath, None, False)
        if response.ok() and (response.content is not None):
            if 'openconfig-qos-ext:poll-interval' in response.content.keys():
                interval = response.content['openconfig-qos-ext:poll-interval']
        keypath = cc.Path(globalPfcWdUri + '/flex/config/counter-poll')
        response = aa.get(keypath, None, False)
        poll="Not Available"
        if response.ok() and (response.content is not None):
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
        response = aa.get(keypath, None, False)
        if response.ok() and (response.content is not None):
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

        response=aa.cli_not_implemented("")      # Just to get the proper format to return data and status
        response.status_code = RESPONSE_OK
        response.content = collections.OrderedDict(tuples)
        return response

    elif func == 'show_port_pfc_statistics':
        response = None
        if args[0].lower() in [ 'ethernetall', 'ethall' ]:
            response = aa.cli_not_implemented("")
            response.status_code = RESPONSE_OK
            response.content = collections.OrderedDict()
            for port in getPortList():
                data = getPfcStatistics(port)
                if (data is None) or (not data.ok()) or (not data.content):
                    continue
                response.content.update(data.content)
        else:
            response = getPfcStatistics(args[0])
        return response

    elif func == 'show_port_pfc_queue_statistics':
        response = None
        if args[0].lower() in [ 'ethernetall', 'ethall' ]:
            response = aa.cli_not_implemented("")
            response.status_code = RESPONSE_OK
            response.content = collections.OrderedDict()
            for port in getPortList():
                data = getPfcQueueStatistics(port)
                if (data is None) or (not data.ok()) or (not data.content):
                    continue
                response.content.update(data.content)
        else:
            response = getPfcQueueStatistics(args[0])
        return response

    elif func == 'show_port_pfc_summary':
        response = None
        if args[0].lower() in [ 'ethernetall', 'ethall' ]:
            response = aa.cli_not_implemented("")
            response.status_code = RESPONSE_OK
            response.content = collections.OrderedDict()
            for port in getPortList():
                data = getQosIntfSummary(port)
                if (data is None) or (not data.ok()) or (not data.content):
                    continue
                response.content.update(data.content)
        else:
            response = getQosIntfSummary(args[0])
        return response

    elif func == 'get_openconfig_qos_qos_queues_queue':
        path = cc.Path('/restconf/data/openconfig-qos:qos/queues/queue={name}', name=args[0])
        tmpl = 'show_qos_queue_config.j2'
        if args[0].split(':')[0].lower() in [ 'ethernetall', 'ethall' ]:
            path = cc.Path('/restconf/data/openconfig-qos:qos/queues')
            tmpl = 'show_qos_queue_config_all.j2'
        data = aa.get(path, None, False)
        if data.ok() and (data.content is not None):
            od = collections.OrderedDict()
            for port in natsorted(data.content.keys()):
                od[port] = data.content[port]
            data.content = od
            show_cli_output(tmpl, data.content)
        return None

    else:
        print("%Error: not implemented")
        exit(1)

def run(func, args):
    if debug == True:
        print "(sonic-cli-qos-pfc) run = ", func, len(args), args
    try:
        apiResponse = invoke(func, args)
        if debug == True:
            print apiResponse.status_code
        if apiResponse is None:
            return
        elif apiResponse.ok():
            response = apiResponse.content
            if debug == True:
                print response
            if func.startswith('show_'):
                if apiResponse.status_code == RESPONSE_NO_CONTENT:
                    message = apiResponse.error_message()
                    print message[7:]
                elif func.startswith('show_port') and (response is not None):
                    show_cli_output(args[1], response)
                elif func.startswith('show_pfc') and (response is not None):
                    show_cli_output(args[0], response)
            elif response is None:
                return
            else:
                print "%Error: Invalid command"
        else:
            #error response
            print apiResponse.error_message()

    except Exception as e:
        log.syslog(log.LOG_ERR, str(e))
        print "%Error: Transaction Failure"

if __name__ == '__main__':
    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])
