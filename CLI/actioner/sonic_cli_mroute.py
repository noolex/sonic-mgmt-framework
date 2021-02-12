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
#
###########################################################################

import syslog as log
import sys
import json
import string
import time
import cli_client as cc
from sonic_cli_pim import  get_vrf_list, seconds_to_wdhm_str
from datetime import datetime, timedelta
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output

import urllib3
urllib3.disable_warnings()

#Define globals
inputDict = {}
apiClient = cc.ApiClient()

def get_keypath(func,args):
    keypath = None
    body = None
    path_prefix = '/restconf/data/openconfig-network-instance:network-instances/network-instance='
    intf = ""
    vrf = ""
    path = ""

    #get vrf, needed for keypath
    vrf = inputDict.get('vrf')
    if vrf == None or vrf == "":
        vrf = "default"

    ##############################################################
    #show config
    ##############################################################
    if 'show_mroute' in func:
        if (inputDict.get('summary')):
            path = "/restconf/operations/sonic-ipmroute-show:show-ipmroute"
            body = {"sonic-ipmroute-show:input": {"vrf-name":vrf, "address-family":"IPV4_UNICAST", "query-type":"SUMMARY", "summary":True}}
        elif (inputDict.get('srcAddr') is not None):
            path = path_prefix + vrf + "/afts/openconfig-aft-ipv4-ext:ipv4-multicast/ipv4-entries/ipv4-entry=" + inputDict.get('grpAddr') + "/state/src-entries/src-entry=" + inputDict.get('srcAddr')
        elif (inputDict.get('grpAddr') is not None):
            path = path_prefix + vrf + "/afts/openconfig-aft-ipv4-ext:ipv4-multicast/ipv4-entries/ipv4-entry=" + inputDict.get('grpAddr')
        else:
            path = path_prefix + vrf + "/afts/openconfig-aft-ipv4-ext:ipv4-multicast/ipv4-entries"

    ##############################################################
    #clear config
    ##############################################################
    if 'clear_mroute' in func:
        path = "/restconf/operations/sonic-ipmroute-clear:clear-ipmroute"
        body = {"sonic-ipmroute-clear:input": {"vrf-name": vrf, "address-family":"IPV4_UNICAST", "config-type":"ALL-MROUTES", "all-mroutes": True}}

    keypath = cc.Path(path)
    return keypath, body

def process_args(args):
    global inputDict
    count = 0
    for arg in args:
        tmp = arg.split(":", 1)
        if not len(tmp) == 2:
            continue
        if tmp[1] == "":
            tmp[1] = None
        inputDict[tmp[0]] = tmp[1]
        if (tmp[1] != None) and (tmp[0] != 'vrf'):
            count = count + 1
    return count

def show_response(response):
    if (inputDict.get('summary') is not None):
        show_mroute_summary(response)
    elif (inputDict.get('srcAddr') is not None):
        show_mroute_src_info(response)
    else:
        show_mroute_info(response)
    return

def show_mroute_src_info(response):
    outputList = []
    outputList2 = []
    oilList2 = None
    srcList2 = None
    ipList = None

    grpAddr = inputDict.get('grpAddr')
    try:
        srcList = response.get('openconfig-aft-ipv4-ext:src-entry')
        if srcList is None:
            return

        oilList2 = []
        srcAddr = srcList[0].get('source-address')
        if srcAddr is None:
            srcAddr = ""

        srcState = srcList[0].get('state')
        if srcState is None:
            return

        inIntf = srcState.get('incoming-interface')
        if inIntf is None:
            inIntf = "-"

        installed = srcState.get('installed')
        if installed is None or installed == False:
            installed = ""
        else:
            installed = "*"

        oilContainer = srcState.get('oil-info-entries')
        if oilContainer is None:
            oilEntry = {'outIntf': "-", 'oilUpTime': "--:--:--"}
            oilList2.append(oilEntry)
        else:
            oilList = oilContainer.get('oif-info')
            if oilList is None:
                oilEntry = {'outIntf': "-", 'oilUpTime': "--:--:--"}
                oilList2.append(oilEntry)
            else:
                for oil in oilList:
                    outIntf = oil.get('outgoing-interface')
                    if  outIntf is None:
                        continue

                    oilState = oil.get('state')
                    if  oilState is None:
                        continue

                    oilUpTime = oilState.get('uptime')
                    if oilUpTime is None:
                        oilUpTime = "--:--:--"
                    else:
                        oilUpTime = seconds_to_wdhm_str(oilUpTime, True)

                    oilEntry = {'outIntf': outIntf,
                                'oilUpTime': oilUpTime
                               }
                    oilList2.append(oilEntry)

        srcEntry = {'grpAddr': grpAddr,
                    'srcAddr': srcAddr,
                    'installed': installed ,
                    'inIntf': inIntf,
                    'oilList': oilList2
                    }
        outputList.append(srcEntry)

        if len(outputList) > 0:
            vrfName = inputDict.get('vrf')
            if vrfName is None:
                vrfName = 'default'

            outputList2.append('show_mroute')
            outputList2.append(vrfName)
            outputList2.append(outputList)
            show_cli_output("show_mroute.j2", outputList2)

    except Exception as e:
        log.syslog(log.LOG_ERR, str(e))
        print "% Error: Internal error"

def show_mroute_info(response):
    outputList = []
    outputList2 = []
    oilList2 = None
    srcList2 = None
    ipList = None

    try:
        if inputDict.get('grpAddr') is not None:
            ipList = response.get('openconfig-aft-ipv4-ext:ipv4-entry')
        else:
            tmpContainer = response.get('openconfig-aft-ipv4-ext:ipv4-entries')
            if tmpContainer is None:
                return
            ipList = tmpContainer.get('ipv4-entry')

        if ipList is None:
            return

        for ip in ipList:
            srcList2 = []

            grpAddr = ip.get('group-address')
            if grpAddr is None:
                continue

            state = ip.get('state')
            if state is None:
                continue

            srcEntries = state.get('src-entries')
            if srcEntries is None:
                continue

            srcList = srcEntries.get('src-entry')
            if srcList is None:
                continue

            for src in srcList:
                oilList2 = []
                srcAddr = src.get('source-address')
                if srcAddr is None:
                    srcAddr = ""

                srcState = src.get('state')
                if srcState is None:
                    continue

                inIntf = srcState.get('incoming-interface')
                if inIntf is None:
                    inIntf = "-"

                installed = srcState.get('installed')
                if installed is None or installed == False:
                    installed = ""
                else:
                    installed = "*"

                oilContainer = srcState.get('oil-info-entries')
                if oilContainer is None:
                    oilEntry = {'outIntf': "-", 'oilUpTime': "--:--:--"}
                    oilList2.append(oilEntry)
                else:
                    oilList = oilContainer.get('oif-info')
                    if oilList is None:
                        oilEntry = {'outIntf': "-", 'oilUpTime': "--:--:--"}
                        oilList2.append(oilEntry)
                    else:
                        for oil in oilList:
                            outIntf = oil.get('outgoing-interface')
                            if  outIntf is None:
                                continue

                            oilState = oil.get('state')
                            if  oilState is None:
                                continue

                            oilUpTime = oilState.get('uptime')
                            if oilUpTime is None:
                                oilUpTime = "--:--:--"
                            else:
                                oilUpTime = seconds_to_wdhm_str(oilUpTime, True)

                            oilEntry = {'outIntf': outIntf,
                                        'oilUpTime': oilUpTime
                                       }
                            oilList2.append(oilEntry)

                srcEntry = {'grpAddr': grpAddr,
                            'srcAddr': srcAddr,
                            'installed': installed ,
                            'inIntf': inIntf,
                            'oilList': oilList2
                            }
                outputList.append(srcEntry)

        if len(outputList) > 0:
            vrfName = inputDict.get('vrf')
            if vrfName is None:
                vrfName = 'default'

            outputList2.append('show_mroute')
            outputList2.append(vrfName)
            outputList2.append(outputList)
            show_cli_output("show_mroute.j2", outputList2)
    except Exception as e:
        log.syslog(log.LOG_ERR, str(e))
        print "% Error: Internal error"

def show_mroute_summary(response):
    outputList = []

    outputContainer = response.get('sonic-ipmroute-show:output')
    if outputContainer is None:
        return

    tmp = outputContainer.get('response')
    if tmp is None:
        return

    resContainer = json.loads(tmp)
    srcGrp =  resContainer.get('sourceGroup')
    if srcGrp is None:
        return

    installed = srcGrp.get('installed')
    if installed is None:
        installed = 0

    total = srcGrp.get('total')
    if total is None:
        total = 0

    summaryEntry = {'installed': installed, 'total': total}

    vrfName = inputDict.get('vrf')
    if vrfName is None:
        vrfName = 'default'

    outputList.append('mroute_summary')
    outputList.append(vrfName)
    outputList.append(summaryEntry)
    show_cli_output("show_mroute.j2", outputList)

def handle_show_all(func, args):
    global inputDict
    response = ""
    vrfList = get_vrf_list()
    if vrfList is None:
        return

    vrfList.sort(key=string.lower)
    for vrf in vrfList:
        if vrf == "mgmt":
            continue

        inputDict['vrf'] = vrf
        keypath, body = get_keypath(func, args)
        if keypath is None:
            print("% Error: Internal error")
            return -1

        if "/operations/" in keypath.path:
            response = apiClient.post(keypath, body)
        else:
            response = apiClient.get(keypath)

        if response is None:
            return -1

        if response.ok():
            response = response.content
            show_response(response)
        else:
            print(response.error_message())
            return -1
    return 0

def handle_show(func, args):
    vrfList = []
    if inputDict.get('vrf') == "all":
        handle_show_all(func, args)
        return

    keypath, body = get_keypath(func, args)
    if keypath is None:
        print("% Error: Internal error")
        return -1
    if "/operations/" in keypath.path:
        response = apiClient.post(keypath, body)
    else:
        response = apiClient.get(keypath)

    if response is None:
        return -1

    if response.ok():
        response = response.content
        show_response(response)
    else:
        print(response.error_message())
        return -1
    return 0

def handle_clear(func, args):
    keypath, body = get_keypath(func, args)
    if keypath is None:
        print("% Error: Internal error")
        return -1
    response = apiClient.post(keypath, body)
    if not response.ok():
        print(response.error_message())
        return -1
    return 0

def run(func, args):
    global inputDict
    response = None
    status = 0
    process_args(args)

    if func.startswith("show"):
      status = handle_show(func, args)
    elif func.startswith("clear"):
      status = handle_clear(func, args)
    inputDict = {}
    return status

if __name__ == '__main__':
    pipestr().write(sys.argv)
    status = run(sys.argv[1], sys.argv[2:])
    if status != 0:
        sys.exit(0)
