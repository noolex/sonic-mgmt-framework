#!/usr/bin/python
###########################################################################
#
# Copyright 2020 Broadcom. The term Broadcom refers to Broadcom Inc. and/or
# its subsidiaries.
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
from rpipe_utils import pipestr
import cli_client as cc
from scripts.render_cli import show_cli_output
import random
from natsort import natsorted
from collections import OrderedDict

api = cc.ApiClient()

tam_rest = '/restconf/data/openconfig-tam:tam'
collectors_url = tam_rest+'/collectors'
samplers_url = tam_rest+'/samplers'
switch_url = tam_rest+'/switch'
switch_id_config_url = switch_url+'/config/switch-id'
enterprise_id_config_url = switch_url+'/config/enterprise-id'
ifa_sessions_url = tam_rest+'/ifa-sessions'
tailstamping_sessions_url = tam_rest+'/tailstamping-sessions'
dropmonitor_sessions_url = tam_rest+'/dropmonitor/dropmonitor-sessions'
dropmonitor_aginginterval_url = tam_rest+'/dropmonitor/global'
features_status_url = tam_rest+'/features-state'
feature_config_url = tam_rest+'/features'
flowgroups_url = tam_rest+'/flowgroups'
flowgroup_ids_url = '/restconf/data/sonic-tam-flowgroups:sonic-tam-flowgroups/TAM_FLOWGROUP_TABLE/TAM_FLOWGROUP_TABLE_LIST'
detach_flowgroup_url = '/restconf/data/openconfig-tam:tam/flowgroups/flowgroup={name}/config/interfaces={interfaces}'
intf_naming_mode_url = '/restconf/data/sonic-device-metadata:sonic-device-metadata/DEVICE_METADATA/DEVICE_METADATA_LIST={name}/intf_naming_mode'
intf_alias_url = '/restconf/data/sonic-port:sonic-port/PORT_TABLE/PORT_TABLE_LIST'
clear_flowgroup_counters_url = '/restconf/operations/openconfig-tam:clear-flowgroup-counters'

def get_intf_alias():
    intfList = {}
    path = cc.Path(intf_naming_mode_url, name="localhost")
    tmp_response = api.get(path)
    if tmp_response.ok():
        response = tmp_response.content
        if response and 'sonic-device-metadata:intf_naming_mode' in response and response['sonic-device-metadata:intf_naming_mode'] == 'standard':
            path = cc.Path(intf_alias_url)
            tmp_response = api.get(path)
            if tmp_response.ok():
                response = tmp_response.content
                if response is None:
                    return intfList
                if 'sonic-port:PORT_TABLE_LIST' in response:
                    for entry in response['sonic-port:PORT_TABLE_LIST']:
                        if 'alias' in entry:
                            intfList[entry['alias']] = {}
                            intfList[entry['alias']] = entry['ifname']
    return intfList


def do_get(url):
    result = {}
    response = api.get(url)
    result['ok'] = response.ok()
    result['content'] = response.content
    return result

def getFeatureDescription(feature):
    features = {
        'openconfig-tam:DROPMONITOR': 'drop-monitor',
        'openconfig-tam:IFA': 'ifa',
        'openconfig-tam:TAILSTAMPING': 'tail-stamping',
        'openconfig-tam:THRESHOLDS': 'thresholds'
    }
    return features[feature]

def getFeatureIdentification(feature):
    feature_id = 'ANY'
    if 'ifa' in feature:
        feature_id = 'IFA'
    elif 'tail-stamping' in feature:
        feature_id = 'TAILSTAMPING'
    elif 'drop-monitor' in feature:
        feature_id = 'DROPMONITOR'
    elif 'thresholds' in feature:
        feature_id = 'THRESHOLDS'
    return feature_id

def getStatusDescription(status):
    descriptions = {
        'ACTIVE': 'Active',
        'INACTIVE': 'Inactive',
        'UNSUPPORTED': 'Unsupported',
        'INSUFFICIENT_RESOURCES': 'Insufficient Resources'
    }
    return descriptions[status]

def getCollectorsCount(data):
    counter = set()
    for x in data:
        state_data = x['state']
        if (state_data['collector'] != ""):
            counter.add(state_data['collector'])
    return len(counter)

def printFeatureDetails(data):
    feature = data['feature']
    feature_status = data['feature_status']
    sessions = data['sessions']
    switch_status = data['switch_status']
    response = []

    status = "-"
    switch_id = "-"
    enterprise_id = "-"
    try:
        status = getStatusDescription(feature_status['openconfig-tam:op-status'])
        switch_id = switch_status['openconfig-tam:switch']['state']['op-switch-id']
        enterprise_id = switch_status['openconfig-tam:switch']['state']['op-enterprise-id']
    except KeyError:
        pass
    response.append({'title': 'Status               : ', 'value': status})
    response.append({'title': 'Switch ID            : ', 'value': switch_id})
    if 'ifa' in feature:
        response.append({'title': 'Enterprise ID        : ', 'value': enterprise_id})
        response.append({'title': 'Version              : ', 'value': "2.0"})
        sessions_count = 0
        collectors_count = 0
        try:
            sessions_count = len(sessions['openconfig-tam:ifa-sessions']['ifa-session'])
            collectors_count = getCollectorsCount(sessions['openconfig-tam:ifa-sessions']['ifa-session'])
        except KeyError:
            pass
        response.append({'title': 'Number of sessions   : ', 'value': sessions_count})
        response.append({'title': 'Number of collectors : ', 'value': collectors_count})
    elif 'tailstamping' in feature:
        sessions_count = 0
        try:
            sessions_count = len(sessions['openconfig-tam:tailstamping-sessions']['tailstamping-session'])
        except KeyError:
            pass
        response.append({'title': 'Number of sessions   : ', 'value': sessions_count})
    elif 'dropmonitoring' in feature:
        sessions_count = 0
        collectors_count = 0
        try:
            sessions_count = len(sessions['openconfig-tam:dropmonitor-sessions']['dropmonitor-session'])
            collectors_count = getCollectorsCount(sessions['openconfig-tam:dropmonitor-sessions']['dropmonitor-session'])
        except KeyError:
            pass
        response.append({'title': 'Number of sessions   : ', 'value': sessions_count})
        response.append({'title': 'Number of collectors : ', 'value': collectors_count})
        aging_interval = "Not Configured"
        try:
            aging_interval = data['aginginterval']['openconfig-tam:aging-interval']
        except KeyError:
            pass
        response.append({'title': 'Aging Interval       : ', 'value': aging_interval})
    return response

def getEthertype(ethertype):
    ethertypes = {
        'openconfig-packet-match-types:ETHERTYPE_IPV4': "0x0800",
        'openconfig-packet-match-types:ETHERTYPE_IPV6': "0x86DD",
        'openconfig-packet-match-types:ETHERTYPE_LLDP': "0x88CC",
        'openconfig-packet-match-types:ETHERTYPE_VLAN': "0x8100",
        'openconfig-packet-match-types:ETHERTYPE_ROCE': "0x8915",
        'openconfig-packet-match-types:ETHERTYPE_ARP':  "0x0806",
        'openconfig-packet-match-types:ETHERTYPE_MPLS': "0x8847"
    }
    if ethertype in ethertypes:
        return ethertypes[ethertype]
    else:
        return str(hex(ethertype))

def getProtocol(protocol):
    protocols = {
        'openconfig-packet-match-types:IP_UDP': "UDP",
        'openconfig-packet-match-types:IP_TCP': "TCP",
    }
    return protocols[protocol]

def getFlowGroups(flowgroups):
    response = {}
    for flowgroup in flowgroups:
        data = flowgroup['state']
        name = data['name']
        response[name] = {}
        response[name]['id'] = data['id']
        response[name]['priority'] = data['priority']
        if 'l2' in flowgroup:
            l2 = flowgroup['l2']['state']
            if 'source-mac' in l2: response[name]['src_mac'] = l2['source-mac']
            if 'destination-mac' in l2: response[name]['dst_mac'] = l2['destination-mac']
            if 'ethertype' in l2: response[name]['ethertype'] = getEthertype(l2['ethertype'])
        if 'ipv4' in flowgroup:
            ipv4 = flowgroup['ipv4']['state']
            if 'source-address' in ipv4: response[name]['src_ip'] = ipv4['source-address']
            if 'destination-address' in ipv4: response[name]['dst_ip'] = ipv4['destination-address']
            if 'protocol' in ipv4: response[name]['protocol'] = getProtocol(ipv4['protocol'])
        if 'ipv6' in flowgroup:
            ipv6 = flowgroup['ipv6']['state']
            if 'source-address' in ipv6: response[name]['src_ip'] = ipv6['source-address']
            if 'destination-address' in ipv6: response[name]['dst_ip'] = ipv6['destination-address']
            if 'protocol' in ipv6: response[name]['protocol'] = getProtocol(ipv6['protocol'])
        if 'transport' in flowgroup:
            transport = flowgroup['transport']['state']
            if 'source-port' in transport: response[name]['src_port'] = transport['source-port']
            if 'destination-port' in transport: response[name]['dst_port'] = transport['destination-port']
        # inports
        if 'interfaces' in data:
            interfaces = data['interfaces']
            t = {}
            getIntfList = get_intf_alias()
            for i in interfaces:
                n = i.split('Ethernet')[1]
                if (len(getIntfList) > 0):
                    t[int(n)] = getIntfList[i]
                else:
                    t[int(n)] = i
            response[name]['ports'] = ','.join(str(t[x]) for x in sorted(t))
        response[name]['packets'] = data['statistics']['packets']
    return OrderedDict(natsorted(response.items()))

helper_functions = {
    'getFeatureDescription': getFeatureDescription,
    'getStatusDescription': getStatusDescription,
    'printFeatureDetails': printFeatureDetails,
    'getFlowGroups': getFlowGroups,
}

def getBody(fn):
    body = {
        'patch_collector': """{"openconfig-tam:collectors":{"collector":[{"name":"%s","config":{"name":"%s","ip":"%s","port":%d,"protocol":"%s"}}]}}""",
        'patch_sampler': """{"openconfig-tam:samplers":{"sampler":[{"name":"%s","config":{"name":"%s","sampling-rate":%d}}]}}""",
        'patch_switch_id': """{"openconfig-tam:switch-id":%d}""",
        'patch_enterprise_id': """{"openconfig-tam:enterprise-id":%d}""",
        'patch_ifa_session': """{"openconfig-tam:ifa-sessions":{"ifa-session":[{"name":"%s","config":{"name":"%s","flowgroup":"%s","collector":"%s","sample-rate":"%s","node-type":"%s"}}]}}""",
        'patch_ts_session': """{"openconfig-tam:tailstamping-sessions":{"tailstamping-session":[{"name":"%s","config":{"name":"%s","flowgroup":"%s"}}]}}""",
        'patch_dm_session': """{"openconfig-tam:dropmonitor-sessions":{"dropmonitor-session":[{"name":"%s","config":{"name":"%s","flowgroup":"%s","collector":"%s","sample-rate":"%s"}}]}}""",
        'patch_aginginterval': """{"openconfig-tam:global":{"config":{"aging-interval":%d}}}""",
        'patch_feature': """{"openconfig-tam:features":{"feature":[{"feature-ref":"%s","config":{"feature-ref":"%s","status":"%s"}}]}}""",
        'associate_flowgroup': """{"openconfig-tam:flowgroups":{"flowgroup":[{"name":"%s","config":{"name":"%s","id":%d,"interfaces":["%s"]}}]}}""",
        'clear_flowgroup_counters': """{"openconfig-tam:input":{}}"""
    }
    return body[fn]

def getFlowGroupDate(data, currentid):
    flowGroupData = {}
    flowGroupData["openconfig-tam:flowgroups"] = {}
    flowGroupData["openconfig-tam:flowgroups"]["flowgroup"] = []
    flowData = {}
    flowData["name"] = data["name"]
    flowData["config"] = {}
    flowData["config"]["name"] = data["name"]
    flowData["config"]["id"] = int(currentid)
    if (data['priority'] != ""):
        flowData["config"]["priority"] = int(data['priority'])
    if ((data['sip'] != "") or (data['dip'] != "") or (data['protocol'] != "")):
        if (("." in data['sip']) or ("." in data['dip']) or (data['protocol'] != "")):
            flowData["ipv4"] = {}
            flowData["ipv4"]["config"] = {}
            if ("." in data['sip']):
                flowData["ipv4"]["config"]["source-address"] = data['sip']
            if ("." in data['dip']):
                flowData["ipv4"]["config"]["destination-address"] = data['dip']
            if (data['protocol'] != ""):
                flowData["ipv4"]["config"]["protocol"] = data['protocol']
        if ((":" in data['sip']) or (":" in data['dip'])):
            flowData["ipv6"] = {}
            flowData["ipv6"]["config"] = {}
            if (":" in data['sip']):
                flowData["ipv6"]["config"]["source-address"] = data['sip']
            if (":" in data['dip']):
                flowData["ipv6"]["config"]["destination-address"] = data['dip']
            if (data['protocol'] != ""):
                flowData["ipv6"]["config"]["protocol"] = data['protocol']
    if ((data['sport'] != "") or (data['dport'] != "")):
        flowData["transport"] = {}
        flowData["transport"]["config"] = {}
        if (data['sport'] != ""):
            flowData["transport"]["config"]["source-port"] = int(data['sport'])
        if (data['dport'] != ""):
            flowData["transport"]["config"]["destination-port"] = int(data['dport'])
    flowGroupData["openconfig-tam:flowgroups"]["flowgroup"].append(flowData)
    return flowGroupData

def getDetails(fn, args):
    data = json.loads(args[0])
    details = {}
    details['method'] = data['method']
    details['feature'] = data['feature']
    details['do_request'] = True
    if fn == "show_collectors":
        if (data['name'] == 'all'):
            details['url'] = collectors_url
            details['template'] = data['template']+"_all.j2"
        else:
            details['url'] = collectors_url+'/collector={}'.format(data['name'])
            details['template'] = data['template']+".j2"
            details['description'] = "Collector"
            details['name'] = data['name']
    elif fn == "patch_collector":
        details['url'] = collectors_url
        body = getBody(fn)%(data['name'],data['name'],data['ip'],data['port'],data['protocol'])
        details['body'] = json.loads(body)
    elif fn == "delete_collector":
        details['url'] = collectors_url+'/collector={}'.format(data['name'])
        details['description'] = "Collector"
        details['name'] = data['name']
    elif fn == "show_samplers":
        if (data['name'] == 'all'):
            details['url'] = samplers_url
            details['template'] = data['template']+"_all.j2"
        else:
            details['url'] = samplers_url+'/sampler={}'.format(data['name'])
            details['template'] = data['template']+".j2"
            details['description'] = "Sampler"
            details['name'] = data['name']
    elif fn == "patch_sampler":
        details['url'] = samplers_url
        body = getBody(fn)%(data['name'],data['name'],data['rate'])
        details['body'] = json.loads(body)
    elif fn == "delete_sampler":
        details['url'] = samplers_url+'/sampler={}'.format(data['name'])
        details['description'] = "Sampler"
        details['name'] = data['name']
    elif fn == "show_switch":
        details['url'] = switch_url
        details['template'] = data['template']
    elif fn == "patch_switch_id":
        details['url'] = switch_id_config_url
        body = getBody(fn)%(data['id'])
        details['body'] = json.loads(body)
        details['description'] = "%Info: Any changes to the switch-wide global attributes are not immediately effective, if any of the TAM features are currently active."
        details['name'] = ""
    elif fn == "delete_switch_id":
        details['url'] = switch_id_config_url
        #details['description'] = "Switch Id"
        #details['name'] = 'switch_id'
    elif fn == "patch_enterprise_id":
        details['url'] = enterprise_id_config_url
        body = getBody(fn)%(data['id'])
        details['body'] = json.loads(body)
        details['description'] = "%Info: Any changes to the switch-wide global attributes are not immediately effective, if any of the TAM features are currently active."
        details['name'] = ""
    elif fn == "delete_enterprise_id":
        details['url'] = enterprise_id_config_url
        #details['description'] = "Enterprise Id"
        #details['name'] = 'enterprise_id'
    elif fn == "show_ifa":
        details['template'] = data['template']
        url = features_status_url+'/feature={}/state/op-status'.format("IFA")
        feature_status = do_get(url)
        url = switch_url
        switch_status = do_get(url)
        url = ifa_sessions_url
        sessions = do_get(url)
        if (feature_status['ok'] and switch_status['ok'] and sessions['ok']):
            if ((feature_status['content'] is not None) and (switch_status['content'] is not None)
                 and (sessions['content'] is not None)):
                details['response'] = {'feature': 'ifa', 'feature_status': feature_status['content'],
                        'switch_status': switch_status['content'], 'sessions': sessions['content']}
        details['do_request'] = False
        details['ok'] = True
    elif fn == "show_ifa_sessions":
        if (data['name'] == 'all'):
            details['url'] = ifa_sessions_url
            details['template'] = data['template']+"_all.j2"
        else:
            details['url'] = ifa_sessions_url+'/ifa-session={}'.format(data['name'])
            details['template'] = data['template']+".j2"
            details['description'] = "Session"
            details['name'] = data['name']
    elif fn == "patch_ifa_session":
        details['url'] = ifa_sessions_url
        body = getBody(fn)%(data['session'],data['session'],data['flowgroup'],data['collector'],data['sampler'],data['node_type'])
        details['body'] = json.loads(body)
        if data['collector'] == "":
            del details['body']["openconfig-tam:ifa-sessions"]["ifa-session"][0]["config"]["collector"]
        if data['sampler'] == "":
            del details['body']["openconfig-tam:ifa-sessions"]["ifa-session"][0]["config"]["sample-rate"]
    elif fn == "delete_ifa_session":
        details['url'] = ifa_sessions_url+'/ifa-session={}'.format(data['session'])
        details['description'] = "Session"
        details['name'] = data['session']
    elif fn == "show_tailstamping":
        details['template'] = data['template']
        url = features_status_url+'/feature={}/state/op-status'.format("TAILSTAMPING")
        feature_status = do_get(url)
        url = switch_url
        switch_status = do_get(url)
        url = tailstamping_sessions_url
        sessions = do_get(url)
        if (feature_status['ok'] and switch_status['ok'] and sessions['ok']):
            if ((feature_status['content'] is not None) and (switch_status['content'] is not None)
                and (sessions['content'] is not None)):
                details['response'] = {'feature': 'tailstamping', 'feature_status': feature_status['content'],
                        'switch_status': switch_status['content'], 'sessions': sessions['content']}
        details['do_request'] = False
        details['ok'] = True
    elif fn == "show_tailstamping_sessions":
        if (data['name'] == 'all'):
            details['url'] = tailstamping_sessions_url
            details['template'] = data['template']+"_all.j2"
        else:
            details['url'] = tailstamping_sessions_url+'/tailstamping-session={}'.format(data['name'])
            details['template'] = data['template']+".j2"
            details['description'] = "Session"
            details['name'] = data['name']
    elif fn == "patch_ts_session":
        details['url'] = tailstamping_sessions_url
        body = getBody(fn)%(data['session'],data['session'],data['flowgroup'])
        details['body'] = json.loads(body)
    elif fn == "delete_ts_session":
        details['url'] = tailstamping_sessions_url+'/tailstamping-session={}'.format(data['session'])
        details['description'] = "Session"
        details['name'] = data['session']
    elif fn == "show_dropmonitor":
        details['template'] = data['template']
        url = features_status_url+'/feature={}/state/op-status'.format("DROPMONITOR")
        feature_status = do_get(url)
        url = switch_url
        switch_status = do_get(url)
        url = dropmonitor_sessions_url
        sessions = do_get(url)
        url = dropmonitor_aginginterval_url+'/state/aging-interval'
        aginginterval = do_get(url)
        if (feature_status['ok'] and switch_status['ok'] and sessions['ok'] and aginginterval['ok']):
            if ((feature_status['content'] is not None) and (switch_status['content'] is not None)
                and (sessions['content'] is not None)):
                interval = {}
                if aginginterval['content'] is not None:
                    interval = aginginterval['content']
                details['response'] = {'feature': 'dropmonitoring', 'feature_status': feature_status['content'],
                        'switch_status': switch_status['content'], 'sessions': sessions['content'], 'aginginterval': interval}
        details['do_request'] = False
        details['ok'] = True
    elif fn == "show_dropmonitor_sessions":
        if (data['name'] == 'all'):
            details['url'] = dropmonitor_sessions_url
            details['template'] = data['template']+"_all.j2"
        else:
            details['url'] = dropmonitor_sessions_url+'/dropmonitor-session={}'.format(data['name'])
            details['template'] = data['template']+".j2"
            details['description'] = "Session"
            details['name'] = data['name']
    elif fn == "patch_dm_session":
        details['url'] = dropmonitor_sessions_url
        body = getBody(fn)%(data['session'],data['session'],data['flowgroup'],data['collector'],data['sampler'])
        details['body'] = json.loads(body)
    elif fn == "delete_dm_session":
        details['url'] = dropmonitor_sessions_url+'/dropmonitor-session={}'.format(data['session'])
        details['description'] = "Session"
        details['name'] = data['session']
    elif fn == "patch_aginginterval":
        details['url'] = dropmonitor_aginginterval_url
        body = getBody(fn)%(data['aging-interval'])
        details['body'] = json.loads(body)
        details['description'] = "%Info: Any changes to aging-interval are effective for newly created sessions only."
        details['name'] = ""
    elif fn == "delete_aginginterval":
        details['url'] = dropmonitor_aginginterval_url+'/config/aging-interval'
        details['description'] = "Aging Interval"
        details['name'] = 'aging_interval'
    elif fn == "show_features":
        if (data['name'] == 'all'):
            details['url'] = features_status_url
            details['template'] = data['template']+"_all.j2"
        else:
            details['url'] = features_status_url+'/feature={}'.format(getFeatureIdentification(data['name']))
            details['template'] = data['template']+".j2"
            details['description'] = "Feature"
            details['name'] = data['name']
    elif fn == "patch_feature":
        details['url'] = feature_config_url
        body = getBody(fn)%(data['feature'],data['feature'],(data['status']).upper())
        details['body'] = json.loads(body)
    elif fn == "show_flowgroups":
        if (data['name'] == 'all'):
            details['url'] = flowgroups_url
            details['template'] = data['template']+"_all.j2"
        else:
            details['url'] = flowgroups_url+'/flowgroup={}'.format(data['name'])
            details['template'] = data['template']+".j2"
            details['description'] = "Flowgroup"
            details['name'] = data['name']
    elif fn == "patch_flowgroup":
        details['url'] = flowgroups_url
        flowGroupsIds = do_get(flowgroup_ids_url)
        idsSet = set()
        maxSet = set(range(2, 255, 1))
        flowGroupsMap = {}
        currentid = 2
        if (flowGroupsIds['ok']):
            if (flowGroupsIds['content'] is not None):
                if 'sonic-tam-flowgroups:TAM_FLOWGROUP_TABLE_LIST' in flowGroupsIds['content']:
                    ids = flowGroupsIds['content']['sonic-tam-flowgroups:TAM_FLOWGROUP_TABLE_LIST']
                    for i in ids:
                        idsSet.add(i['id'])
                        flowGroupsMap[i['name']] = i['id']
        if data['name'] in flowGroupsMap:
            currentid = flowGroupsMap[data['name']]
        elif (len(idsSet) != 0):
            diff = maxSet.difference(idsSet)
            currentid = list(random.sample(diff, 1))[0]
        details['body'] = getFlowGroupDate(data, currentid)
    elif fn == "delete_flowgroup":
        details['url'] = flowgroups_url+'/flowgroup={}'.format(data['name'])
        details['description'] = "Flowgroup"
        details['name'] = data['name']
    elif fn == "associate_flowgroup":
        flowGroupsIds = do_get(flowgroup_ids_url)
        flowGroupsMap = {}
        if (flowGroupsIds['ok']):
            if (flowGroupsIds['content'] is not None):
                if 'sonic-tam-flowgroups:TAM_FLOWGROUP_TABLE_LIST' in flowGroupsIds['content']:
                    ids = flowGroupsIds['content']['sonic-tam-flowgroups:TAM_FLOWGROUP_TABLE_LIST']
                    for i in ids:
                        flowGroupsMap[i['name']] = i['id']
        if data['name'] in flowGroupsMap:
            currentid = flowGroupsMap[data['name']]
            details['url'] = flowgroups_url
            body = getBody(fn)%(data['name'],data['name'],currentid,data['interface'])
            details['body'] = json.loads(body)
        else:
            details['do_request'] = False
            details['ok'] = True
            details['description'] = "Flowgroup"
            details['name'] = data['name']
            details['status_code'] = 404
    elif fn == "disassociate_flowgroup":
        flowGroupsIds = do_get(flowgroup_ids_url)
        flowGroupsMap = {}
        if (flowGroupsIds['ok']):
            if (flowGroupsIds['content'] is not None):
                if 'sonic-tam-flowgroups:TAM_FLOWGROUP_TABLE_LIST' in flowGroupsIds['content']:
                    ids = flowGroupsIds['content']['sonic-tam-flowgroups:TAM_FLOWGROUP_TABLE_LIST']
                    for i in ids:
                        flowGroupsMap[i['name']] = i['id']
        if data['name'] in flowGroupsMap:
            details['url'] = detach_flowgroup_url.format(name=data['name'], interfaces=data['interface'])
        else:
            details['do_request'] = False
            details['ok'] = True
            details['description'] = "Flowgroup"
            details['name'] = data['name']
            details['status_code'] = 404
    elif fn == "clear_flowgroup_counters":
        details['url'] = clear_flowgroup_counters_url
        body = getBody(fn)
        if (data['name'] == ""):
            details['body'] = json.loads(body)
        else:
            details['body'] = json.loads(body)
            details['body']['openconfig-tam:input']['name'] = {}
            details['body']['openconfig-tam:input']['name'] = data['name']
    else:
        details = None
    return details

def getResponse(details):
    if details['method'] == 'GET':
        return api.get(details['url'])
    elif details['method'] == 'PATCH':
        return api.patch(details['url'], details['body'])
    elif details['method'] == 'PUT':
        return api.put(details['url'], details['body'])
    elif details['method'] == 'POST':
        return api.post(details['url'], details['body'])
    else:
        return api.delete(details['url'])

def invoke_api(fn, args):
    details = getDetails(fn, args)
    if details is None:
        return api.cli_not_implemented(fn)
    else:
        if details['do_request']:
            response = getResponse(details)
            details['status_code'] = response.response.status_code
            details['ok'] = response.ok()
            details['response'] = response.content
            details['error_message'] = response.error_message()
    return details

def run(fn, args):
    result = invoke_api(fn, args)
    if (not(result is None)) and result['ok']:
        if ('response' in result) and (result['response'] is not None):
            if result['method'] == 'GET':
                show_cli_output(result['template'], result['response'], **(helper_functions))
        else:
            if (result['status_code'] == 404):
                if 'description' in result:
                    description = result['description']
                    if ("%Error:" not in description):
                        description = "%Error: " + description
                    message = "{} '{}' not found.".format(description, result['name'])
                    print message
            elif (result['status_code'] == 204):
                if 'description' in result:
                    if '%Info' in result['description']:
                        print result['description']
    else:
        if 'error_message' in result:
            message = result['error_message']
            if ("%Error:" not in message):
                message = "%Error: " + message
            if "does not match" in message:
                message = "%Error: Invalid input in the command."
            print message
    return 0

if __name__ == '__main__':
    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])

