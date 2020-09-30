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
from datetime import datetime, timedelta
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output

import urllib3
urllib3.disable_warnings()

#Define globals
inputDict = {}
apiClient = cc.ApiClient()

def seconds_to_wdhm_str(seconds, upTime):
    d = None
    if upTime:
        d = datetime.now()
        d = d - timedelta(seconds=int(seconds))
    else:
        seconds = float(seconds) - time.time()
        if seconds < 0:
            seconds = 0
        d = datetime.fromtimestamp(seconds)
    weeks = 0
    days = d.day
    if days != 0:
       days = days - 1
       if days != 0:
          weeks = days // 7
          days = days % 7
    if weeks != 0:
        wdhm = '{}w{}d{:02}h'.format(int(weeks), int(days), int(d.hour))
    elif days != 0:
        wdhm = '{}d{:02}h{:02}m'.format(int(days), int(d.hour), int(d.minute))
    else:
        wdhm = '{:02}:{:02}:{:02}'.format(int(d.hour), int(d.minute), int(d.second))

    return wdhm

def get_keypath(func,args):
    keypath = None
    body = None
    path_prefix = '/restconf/data/openconfig-network-instance:network-instances/network-instance='
    intf = ""
    intf_uri = ""
    vrf = ""
    path = ""

    #patch and show config
    if ((func == 'patch_pim_global_config') or
        (func == 'show_pim_config') or
        (func.startswith('clear'))):

        #get vrf, needed for keypath
        vrf = inputDict.get('vrf')
        if vrf == None or vrf == "":
            vrf = "default"

    ##############################################################
    #patch global cmds
    ##############################################################
    if func == 'patch_pim_global_config':
        #generate keypath
        path = path_prefix + vrf + '/protocols/protocol=PIM,pim/pim/global'

        if inputDict.get('jpi') is not None:
            body = {"openconfig-network-instance:global": {"openconfig-pim-ext:config": {"join-prune-interval": float(inputDict.get('jpi'))}}}
        elif inputDict.get('kat') is not None:
            body = {"openconfig-network-instance:global": {"openconfig-pim-ext:config": {"keep-alive-timer": float(inputDict.get('kat'))}}}
        elif inputDict.get('pln') is not None:
            body = {"openconfig-network-instance:global": {"ssm": {"config": {"ssm-ranges": inputDict.get('pln')}}}}
        #as rebalance is a child of ecmp, check it first
        elif inputDict.get('rebalance') is not None:
            body = {"openconfig-network-instance:global": {"openconfig-pim-ext:config": {"ecmp-rebalance-enabled": True}}}
        elif inputDict.get('ecmp') is not None:
            body = {"openconfig-network-instance:global": {"openconfig-pim-ext:config": {"ecmp-enabled": True}}}

    ##############################################################
    #del global config
    ##############################################################
    if func == 'del_pim_global_config':
        #get vrf, needed for keypath
        vrf = inputDict.get('vrf')
        if vrf == None or vrf == "":
            vrf = "default"

        #generate keypath
        path = path_prefix + vrf + '/protocols/protocol=PIM,pim/pim/global'

        #generate del request based on the input
        if inputDict.get('jpi') is not None:
            path = path + "/openconfig-pim-ext:config/join-prune-interval"
        elif inputDict.get('kat') is not None:
            path = path + "/openconfig-pim-ext:config/keep-alive-timer"
        elif inputDict.get('pln') is not None:
            path = path + "/ssm/config/ssm-ranges"
        #as rebalance is a child of ecmp, check it first
        elif inputDict.get('rebalance') is not None:
            path = path + "/openconfig-pim-ext:config/ecmp-rebalance-enabled"
        elif inputDict.get('ecmp') is not None:
            path = path + "/openconfig-pim-ext:config/ecmp-enabled"

    ##############################################################
    #interface level config common code
    ##############################################################
    if 'pim_interface_config' in func:
        #get interface, needed for VRF lookup and keypath
        intf = inputDict.get('intf')
        if intf is None:
            return None, None

        intf_uri = inputDict.get('intf_uri')
        if intf_uri is None:
            return None, None

        #get vrf, needed for keypath
        vrf=get_vrf(intf_uri)
        if vrf is None:
            return None, None

    ##############################################################
    #patch/delete interface level config
    ##############################################################
    if func.endswith('config_mode'):
        if func.startswith('patch'):
            path = path_prefix + vrf + '/protocols/protocol=PIM,pim/pim/interfaces'
            body = {"openconfig-network-instance:interfaces": {"interface": [{"interface-id": intf, "config": {"interface-id": intf, "mode": "PIM_MODE_SPARSE"}}]}}
        elif func.startswith('del'):
            path = path_prefix + vrf + '/protocols/protocol=PIM,pim/pim/interfaces/interface=' + intf_uri + '/config/mode'

    if func.endswith('config_drprio'):
        if func.startswith('patch'):
            path = path_prefix + vrf + '/protocols/protocol=PIM,pim/pim/interfaces'
            body = {"openconfig-network-instance:interfaces": {"interface": [{"interface-id": intf, "config": {"interface-id": intf, "dr-priority": float(inputDict.get('drprio'))}}]}}
        elif func.startswith('del'):
            path = path_prefix + vrf + '/protocols/protocol=PIM,pim/pim/interfaces/interface=' + intf_uri + '/config/dr-priority'

    if func.endswith('config_hello'):
        if func.startswith('patch'):
            path = path_prefix + vrf + '/protocols/protocol=PIM,pim/pim/interfaces'
            body = {"openconfig-network-instance:interfaces": {"interface": [{"interface-id": intf, "config": {"interface-id": intf, "hello-interval": float(inputDict.get('hello'))}}]}}
        elif func.startswith('del'):
            path = path_prefix + vrf + '/protocols/protocol=PIM,pim/pim/interfaces/interface=' + intf_uri + '/config/hello-interval'

    if func.endswith('config_bfd'):
        if func.startswith('patch'):
            path = path_prefix + vrf + '/protocols/protocol=PIM,pim/pim/interfaces'
            body = {"openconfig-network-instance:interfaces": {"interface": [{"interface-id": intf, "config": {"interface-id": intf, "bfd-enabled": True}}]}}
        elif func.startswith('del'):
            path = path_prefix + vrf + '/protocols/protocol=PIM,pim/pim/interfaces/interface=' + intf_uri + '/config/openconfig-pim-ext:bfd-enabled'

    ##############################################################
    #show config
    ##############################################################
    if 'show_pim_config' in func:
        #generate keypath
        path = path_prefix + vrf + '/protocols/protocol=PIM,pim/pim'

        if ((inputDict.get('intf') is not None) or
            (inputDict.get('nbr') is not None)):
            path = path + "/interfaces"
            port = inputDict.get('port')
            if port is not None:
                if port.lower().startswith('e'):
                    path = path + "/interface=" + port
                else:
                    path = path + "/interface=" + inputDict.get('ifType') + port

        if (inputDict.get('ssm') is not None):
            path = path + "/global/ssm"
        if (inputDict.get('srcAddr') is not None):
            path = path + "/global/openconfig-pim-ext:tib/ipv4-entries/ipv4-entry=" + inputDict.get('grpAddr') + "/state/src-entries/src-entry=" + inputDict.get('srcAddr') + ",SG"
        elif (inputDict.get('grpAddr') is not None):
            path = path + "/global/openconfig-pim-ext:tib/ipv4-entries/ipv4-entry=" + inputDict.get('grpAddr')
        elif (inputDict.get('topology') is not None):
            path = path + "/global/openconfig-pim-ext:tib"
        elif (inputDict.get('rpf') is not None):
            path = "/restconf/operations/sonic-pim-show:show-pim"
            body = {"sonic-pim-show:input":{"vrf-name": vrf, "address-family": "IPV4_UNICAST", "query-type": "RPF", "rpf": True}}

    ##############################################################
    #clear config
    ##############################################################
    if 'clear_pim' in func:
        path = "/restconf/operations/sonic-pim-clear:clear-pim"
        if (inputDict.get('interfaces') is not None):
            body = {"sonic-pim-clear:input": {"vrf-name": vrf, "address-family":"IPV4_UNICAST", "config-type":"ALL-INTERFACES", "all-interfaces": True}}
        elif (inputDict.get('oil') is not None):
            body = {"sonic-pim-clear:input": {"vrf-name": vrf, "address-family":"IPV4_UNICAST", "config-type":"ALL-OIL", "all-oil": True}}

    keypath = cc.Path(path)
    return keypath, body

def get_vrf(intf):
    request = ''

    if intf.lower().startswith('e'):
        request = '/restconf/data/sonic-interface:sonic-interface/INTERFACE/INTERFACE_LIST=' + intf + '/vrf_name'
    elif intf.lower().startswith('vlan'):
        request = '/restconf/data/sonic-vlan-interface:sonic-vlan-interface/VLAN_INTERFACE/VLAN_INTERFACE_LIST=' + intf + '/vrf_name'
    elif intf.lower().startswith('p'):
        request =  '/restconf/data/sonic-portchannel-interface:sonic-portchannel-interface/PORTCHANNEL_INTERFACE/PORTCHANNEL_INTERFACE_LIST=' + intf + '/vrf_name'
    else:
        return 'default'

    keypath = cc.Path(request)

    try:
        response = apiClient.get(keypath)
        if response is  None:
            return 'default'

        response = response.content
        if response is  None:
            return 'default'

        if intf.lower().startswith('e'):
            vrf = response.get('sonic-interface:vrf_name')
        if intf.lower().startswith('vlan'):
            vrf = response.get('sonic-vlan-interface:vrf_name')
        if intf.lower().startswith('p'):
            vrf = response.get('sonic-portchannel-interface:vrf_name')

        if vrf is None or vrf == '':
            return 'default'
        return vrf

    except Exception as e:
        log.syslog(log.LOG_ERR, str(e))
        return None

def show_response(response):
    if (inputDict.get('intf') is not None):
        show_intf_info(response)
    elif (inputDict.get('nbr') is not None):
        show_nbr_info(response)
    elif (inputDict.get('ssm') is not None):
        show_ssm_info(response)
    elif (inputDict.get('srcAddr') is not None):
        show_topology_src_info(response)
    elif (inputDict.get('topology') is not None):
        show_topology_info(response)
    elif (inputDict.get('rpf') is not None):
        show_rpf_info(response)
    return

def show_intf_info(response):
    outputList = []
    outputList2 = []
    intfState = ""
    intfsContainer = None
    intfList = None

    if not response:
        return

    if inputDict.get('port') is not None:
        intfList = response.get('openconfig-network-instance:interface')
    else:
        intfsContainer = response.get('openconfig-network-instance:interfaces')
        if intfsContainer is None:
            return

        intfList = intfsContainer.get('interface')

    if intfList is None:
        return

    for intf in intfList:
        intfState = "down"

        intfId = intf.get('interface-id')
        if intfId is None:
            continue

        state = intf.get('state')
        if state is None:
           continue

        enabled = state.get('enabled')
        if enabled is None:
            intfState = ""
        elif enabled == True:
            intfState = "up"

        localAddr = state.get('openconfig-pim-ext:local-address')
        if localAddr is None:
            localAddr = ""

        nbrCount = state.get('openconfig-pim-ext:nbrs-count')
        if nbrCount is None:
            nbrCount = ""

        pimDrAddr = state.get('openconfig-pim-ext:dr-address')
        if pimDrAddr is None:
            pimDrAddr = ""

        helloInterval = state.get('hello-interval')
        if helloInterval is None:
            helloInterval = ""

        pimDrPrio = state.get('dr-priority')
        if pimDrPrio is None:
            pimDrPrio = ""

        intfEntry = {'intfId':intfId,
                    'intfState':intfState,
                    'localAddr':localAddr,
                    'nbrCount':nbrCount,
                    'pimDrAddr':pimDrAddr,
                    'helloInterval':helloInterval,
                    'pimDrPrio':pimDrPrio,
                    }
        outputList.append(intfEntry)

    if len(outputList) > 0:
        vrfName = inputDict.get('vrf')
        if vrfName is None:
            vrfName = 'default'

        outputList2.append('show_interface')
        outputList2.append(vrfName)
        outputList2.append(outputList)

        show_cli_output("show_pim.j2", outputList2)

def show_topology_src_info(response):
    outputList = []
    outputList2 = []
    oilList2 = None
    srcList2 = None
    ipList = None

    if not response:
        return

    grpAddr = inputDict.get('grpAddr')
    try:
        srcList = response.get('openconfig-pim-ext:src-entry')
        if srcList is None:
            return

        oilList2 = []
        srcAddr = srcList[0].get('source-address')
        if srcAddr is None:
            return

        srcState = srcList[0].get('state')
        if srcState is None:
            return

        srcFlags = srcState.get('flags')
        if srcFlags is None:
            srcFlags = ""

        tmp = srcExpiry = srcState.get('expiry')
        if srcExpiry is None:
            srcExpiry = "Never"
        else:
            srcExpiry = seconds_to_wdhm_str(srcExpiry, False)

        srcUpTime = srcState.get('uptime')
        if srcUpTime is None:
            srcUpTime = "--:--:--"
        else:
            srcUpTime = seconds_to_wdhm_str(srcUpTime, True)

        inIntf = srcState.get('incoming-interface')
        if inIntf is None:
            inIntf = ""

        rpfNbr = ""
        rpfState = srcState.get('rpf-info').get('state')
        if rpfState is not None:
            rpfNbr = rpfState.get('rpf-neighbor-address')
            if rpfNbr is None:
                rpfNbr = ""

        oilList = srcState.get('oil-info-entries').get('oil-info-entry')
        if oilList is not None:
            for oil in oilList:
                outIntf = oil.get('outgoing-interface')
                if  outIntf is None:
                    continue

                oilState = oil.get('state')
                if  oilState is None:
                    continue

                oilExpiry = oilState.get('expiry')
                if oilExpiry is None:
                    oilExpiry = "Never"
                else:
                    oilExpiry = seconds_to_wdhm_str(oilExpiry, False)

                oilUpTime = oilState.get('uptime')
                if oilUpTime is None:
                    oilUpTime = "--:--:--"
                else:
                    oilUpTime = seconds_to_wdhm_str(oilUpTime, True)

                oilEntry = {'outIntf': outIntf,
                            'oilExpiry': oilExpiry,
                            'oilUpTime': oilUpTime
                           }
                oilList2.append(oilEntry)

        srcEntry = {'grpAddr': grpAddr,
                    'srcAddr': srcAddr,
                    'srcFlags': srcFlags ,
                    'srcExpiry': srcExpiry,
                    'srcUpTime': srcUpTime,
                    'inIntf': inIntf,
                    'rpfNbr': rpfNbr,
                    'oilList': oilList2
                    }
        outputList.append(srcEntry)

        if len(outputList) > 0:
            vrfName = inputDict.get('vrf')
            if vrfName is None:
                vrfName = 'default'

            outputList2.append('show_topo')
            outputList2.append(vrfName)
            outputList2.append(outputList)

            show_cli_output("show_pim.j2", outputList2)

    except Exception as e:
        log.syslog(log.LOG_ERR, str(e))
        print "% Error: Internal error"

def show_topology_info(response):
    outputList = []
    outputList2 = []
    oilList2 = None
    srcList2 = None
    ipList = None

    if not response:
        return

    try:
        if inputDict.get('grpAddr') is not None:
            ipList = response.get('openconfig-pim-ext:ipv4-entry')
        else:
            tmpContainer = response.get('openconfig-pim-ext:tib')
            if tmpContainer is None:
                return
            tmpContainer = tmpContainer.get('ipv4-entries')
            if tmpContainer is None:
                return
            ipList = tmpContainer.get('ipv4-entry')

        if ipList is None:
            return

        for ip in ipList:
            srcList2 = []

            state = ip.get('state')
            if state is None:
                continue

            grpAddr = state.get('group-address')
            if grpAddr is None:
                continue

            srcList = state.get('src-entries').get('src-entry')
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

                srcFlags = srcState.get('flags')
                if srcFlags is None:
                    srcFlags = ""

                srcExpiry = srcState.get('expiry')
                if srcExpiry is None:
                    srcExpiry = "Never"
                else:
                    srcExpiry = seconds_to_wdhm_str(srcExpiry, False)

                srcUpTime = srcState.get('uptime')
                if srcUpTime is None:
                    srcUpTime = "--:--:--"
                else:
                    srcUpTime = seconds_to_wdhm_str(srcUpTime, True)

                inIntf = srcState.get('incoming-interface')
                if inIntf is None:
                    inIntf = ""

                rpfNbr = ""
                rpfState = srcState.get('rpf-info').get('state')
                if rpfState is not None:
                    rpfNbr = rpfState.get('rpf-neighbor-address')
                    if rpfNbr is None:
                        rpfNbr = ""

                oilList = srcState.get('oil-info-entries').get('oil-info-entry')
                if oilList is None:
                    continue

                for oil in oilList:
                    outIntf = oil.get('outgoing-interface')
                    if  outIntf is None:
                        continue

                    oilState = oil.get('state')
                    if  oilState is None:
                        continue

                    oilExpiry = oilState.get('expiry')
                    if oilExpiry is None:
                        oilExpiry = "Never"
                    else:
                        oilExpiry = seconds_to_wdhm_str(oilExpiry, False)

                    oilUpTime = oilState.get('uptime')
                    if oilUpTime is None:
                        oilUpTime = "--:--:--"
                    else:
                        oilUpTime = seconds_to_wdhm_str(oilUpTime, True)

                    oilEntry = {'outIntf': outIntf,
                                'oilExpiry': oilExpiry,
                                'oilUpTime': oilUpTime
                               }
                    oilList2.append(oilEntry)

                srcEntry = {'grpAddr': grpAddr,
                            'srcAddr': srcAddr,
                            'srcFlags': srcFlags ,
                            'srcExpiry': srcExpiry,
                            'srcUpTime': srcUpTime,
                            'inIntf': inIntf,
                            'rpfNbr': rpfNbr,
                            'oilList': oilList2
                            }
                outputList.append(srcEntry)

        if len(outputList) > 0:
            vrfName = inputDict.get('vrf')
            if vrfName is None:
                vrfName = 'default'

            outputList2.append('show_topo')
            outputList2.append(vrfName)
            outputList2.append(outputList)

            show_cli_output("show_pim.j2", outputList2)

    except Exception as e:
        log.syslog(log.LOG_ERR, str(e))
        print "% Error: Internal error"

def get_ssm_ranges(response):
    if not response:
        return '232.0.0.0/8'

    ssmContainer = response.get('openconfig-network-instance:ssm')
    if not ssmContainer:
        return '232.0.0.0/8'

    ssmState = ssmContainer.get('state')
    if not ssmState:
        return '232.0.0.0/8'

    ssmRanges = ssmState.get('ssm-ranges')
    if not ssmRanges:
        return '232.0.0.0/8'
    else:
        return ssmRanges

def show_ssm_info(response):
    outputList = []
    ssmRanges = get_ssm_ranges(response)

    vrfName = inputDict.get('vrf')
    if vrfName is None:
        vrfName = 'default'

    outputList.append('show_ssm')
    outputList.append(vrfName)
    outputList.append(ssmRanges)

    show_cli_output("show_pim.j2", outputList)

def show_rpf_info(response):
    outputList = []
    outputList2 = []
    rpfList = None

    if not response:
        return

    outputContainer = response.get('sonic-pim-show:output')
    if outputContainer is None:
        return

    tmp = outputContainer.get('response')
    if tmp is None:
        return

    responseContainer = json.loads(tmp)
    for key in responseContainer.keys():
        if key.startswith("rpf") or key.startswith("next"):
            continue

        rpfEntry = responseContainer.get(key)
        if rpfEntry is None:
            continue

        for subkey in rpfEntry.keys():
            rpfSubEntry = rpfEntry.get(subkey)
            if rpfSubEntry is not None:
                outputList.append(rpfSubEntry)

    if len(outputList) > 0:
        vrfName = inputDict.get('vrf')
        if vrfName is None:
            vrfName = 'default'

        outputList2.append('show_rpf')
        outputList2.append(vrfName)
        outputList2.append(outputList)

        show_cli_output("show_pim.j2", outputList2)

def show_nbr_info(response):
    outputList = []
    outputList2 = []
    intfsContainer = None
    intfList = None

    givenNbr = inputDict.get('nbrAddr')

    if not response:
        return

    intfsContainer = response.get('openconfig-network-instance:interfaces')
    if intfsContainer is None:
        return

    intfList = intfsContainer.get('interface')

    if intfList is None:
        return

    for intf in intfList:

        intfId = intf.get('interface-id')
        if intfId is None:
            continue

        nbrContainer = intf.get('neighbors')
        if nbrContainer is None:
           continue

        nbrList = nbrContainer.get('neighbor')
        if nbrList is None:
           continue

        for nbr in nbrList:
            rcvdNbr = nbr.get('neighbor-address')
            if rcvdNbr is None:
                continue

            if givenNbr is not None:
                if givenNbr != rcvdNbr:
                    continue

            nbrState = nbr.get('state')
            if nbrState is None:
                continue

            upTime  = nbrState.get('neighbor-established')
            if upTime is None:
                upTime = "--:--:--"
            else:
                upTime = seconds_to_wdhm_str(upTime, True)

            expiryTime = nbrState.get('neighbor-expires')
            if expiryTime is None:
                expiryTime = "Never"
            else:
                expiryTime = seconds_to_wdhm_str(expiryTime, False)

            pimDrPrio = nbrState.get('openconfig-pim-ext:dr-priority')
            if pimDrPrio is None:
                pimDrPrio = ""

            nbrEntry = {'intfId':intfId,
                        'rcvdNbr':rcvdNbr,
                        'upTime':upTime,
                        'expiryTime':expiryTime,
                        'pimDrPrio':pimDrPrio,
                        }
            outputList.append(nbrEntry)

    if len(outputList) > 0:
        vrfName = inputDict.get('vrf')
        if vrfName is None:
            vrfName = 'default'

        outputList2.append('show_neighbor')
        outputList2.append(vrfName)
        outputList2.append(outputList)

        show_cli_output("show_pim.j2", outputList2)

def get_vrf_list():
    # Use SONIC model to get all configued VRF names and set the keys in the dictionary
    vrfList =  []
    keypath = cc.Path('/restconf/data/sonic-vrf:sonic-vrf/VRF/VRF_LIST')
    response = apiClient.get(keypath)

    if not response:
        return None

    if response.ok():
        response = response.content
    else:
        return None

    if not response:
        return None

    if 'sonic-vrf:VRF_LIST' in response:
        vrf_list = response['sonic-vrf:VRF_LIST']
        for vrf in vrf_list:
            vrf_name = vrf['vrf_name']
            vrfList.append(vrf_name)
    return vrfList

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

def handle_patch(func, args):
    keypath, body = get_keypath(func, args)
    if keypath is None:
        print("% Error: Internal error")
        return -1
    response = apiClient.patch(keypath, body)
    if not response.ok():
        print(response.error_message())
        return -1
    return 0

def handle_del(func, args):
    keypath, body = get_keypath(func, args)
    if keypath is None:
        print("% Error: Internal error")
        return -1
    response = apiClient.delete(keypath, deleteEmptyEntry=True)
    if not response.ok():
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

def handle_show_all(func, args):
    global inputDict
    response = ""
    vrfList = get_vrf_list()
    if vrfList is None:
        return

    vrfCount = len(vrfList)
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

def run(func, args):
    global inputDict
    response = None
    status = 0
    count = process_args(args)
    if (count == 0):
        return -1

    if func.startswith("patch"):
        status =  handle_patch(func, args)
    elif func.startswith("del"):
        status = handle_del(func, args)
    elif func.startswith("show"):
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
