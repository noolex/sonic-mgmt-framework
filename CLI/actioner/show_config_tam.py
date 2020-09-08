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
COLLECTORS = 'sonic-tam-collectors:sonic-tam-collectors/TAM_COLLECTORS_TABLE/TAM_COLLECTORS_TABLE_LIST'
AGING_INTERVAL = 'sonic-tam-dropmonitor:sonic-tam-dropmonitor/TAM_DROPMONITOR_TABLE/TAM_DROPMONITOR_TABLE_LIST'
DROPMONITOR = 'sonic-tam-dropmonitor:sonic-tam-dropmonitor/TAM_DROPMONITOR_SESSIONS_TABLE/TAM_DROPMONITOR_SESSIONS_TABLE_LIST'
FEATURES = 'sonic-tam-features:sonic-tam-features/TAM_STATE_FEATURES_TABLE/TAM_STATE_FEATURES_TABLE_LIST'
FLOWGROUP = 'sonic-tam-flowgroups:sonic-tam-flowgroups/TAM_FLOWGROUP_TABLE/TAM_FLOWGROUP_TABLE_LIST'
IFA_SESSIONS = 'sonic-tam-ifa:sonic-tam-ifa/TAM_IFA_SESSIONS_TABLE/TAM_IFA_SESSIONS_TABLE_LIST'
SAMPLINGRATE = 'sonic-tam-samplers:sonic-tam-samplers/TAM_SAMPLINGRATE_TABLE/TAM_SAMPLINGRATE_TABLE_LIST'
SWITCH = 'sonic-tam-switch:sonic-tam-switch/TAM_SWITCH_TABLE/TAM_SWITCH_TABLE_LIST'
TAILSTAMPING_SESSIONS = 'sonic-tam-tailstamping:sonic-tam-tailstamping/TAM_TAILSTAMPING_SESSIONS_TABLE/TAM_TAILSTAMPING_SESSIONS_TABLE_LIST'
ACL_RULES = 'sonic-acl:sonic-acl/ACL_RULE'

def getAclRuleHash(aclRules):
    ruleHash = {}
    for r in aclRules:
        name = r['rulename']
        ruleHash[name] = {}
        if 'DST_IP' in r:
            ruleHash[name]['DST_IP'] = r['DST_IP']
        if 'SRC_IP' in r:
            ruleHash[name]['SRC_IP'] = r['SRC_IP']
        if 'SRC_MAC' in r:
            ruleHash[name]['SRC_MAC'] = r['SRC_MAC']
        if 'DST_MAC' in r:
            ruleHash[name]['DST_MAC'] = r['DST_MAC']
        if 'PACKET_ACTION' in r:
            ruleHash[name]['PACKET_ACTION'] = r['PACKET_ACTION']
        if 'IP_TYPE' in r:
            ruleHash[name]['IP_TYPE'] = r['IP_TYPE']
        if 'IP_PROTOCOL' in r:
            ruleHash[name]['IP_PROTOCOL'] = r['IP_PROTOCOL']
        if 'ETHER_TYPE' in r:
            ruleHash[name]['ETHER_TYPE'] = r['ETHER_TYPE']
        if 'SRC_IPV6' in r:
            ruleHash[name]['SRC_IPV6'] = r['SRC_IPV6']
        if 'DST_IPV6' in r:
            ruleHash[name]['DST_IPV6'] = r['DST_IPV6']
        if 'L4_SRC_PORT' in r:
            ruleHash[name]['L4_SRC_PORT'] = r['L4_SRC_PORT']
        if 'L4_DST_PORT' in r:
            ruleHash[name]['L4_DST_PORT'] = r['L4_DST_PORT']
        if 'IN_PORTS' in r:
            ruleHash[name]['IN_PORTS'] = r['IN_PORTS']
    return ruleHash

def getIpType(type):
   if type == "IPV6ANY":
       return "ipv6"
   else:
       return "ipv4"

def getProtocol(proto):
   if type == "6":
       return "TCP"
   else:
       return "UDP"

def get_tam_interface_config_cmds(intf, FlowgroupCfg, AclRules):
    CMDS_STRING = ''
    
    if (len(AclRules) != 0):
        aclRules = AclRules['ACL_RULE_LIST']
        aclRuleHash = getAclRuleHash(aclRules)
        flowGroupPerIntf = {}
        if (len(FlowgroupCfg) != 0):
            for f in FlowgroupCfg:
                rulename = f['name']
                aclCfg = aclRuleHash[rulename]                
                if 'IN_PORTS' in aclCfg:
                    inPorts = aclCfg['IN_PORTS']
                    for p in inPorts:
                        if p == intf:
                            CMDS_STRING += 'flow-group ' + str(rulename) + ";"

    return CMDS_STRING

def get_tam_config_cmds(SwitchCfg, CollectorsCfg, SamplingrateCfg, FlowgroupCfg, AclRules):
    CMDS_STRING = ''
    configured = False
    # Switch Configuration
    if (len(SwitchCfg) != 0):
        cfg = SwitchCfg[0]
        if 'switch-id' in cfg:
            configured = True
            CMDS_STRING += ' switch-id ' + str(cfg['switch-id']) + "\n"
        if 'enterprise-id' in cfg:
            configured = True
            CMDS_STRING += ' enterprise-id ' + str(cfg['enterprise-id']) + "\n"
    # Collector Configuration
    if (len(CollectorsCfg) != 0):
        for c in CollectorsCfg:
            configured = True
            CMDS_STRING += ' collector ' + c['name']
            CMDS_STRING += ' ip ' + c['ip']
            CMDS_STRING += ' port ' + str(c['port'])
            CMDS_STRING += ' protocol ' + c['protocol'] + '\n'
    # Sampler Configuration
    if (len(SamplingrateCfg) != 0):
        for s in SamplingrateCfg:
            configured = True
            CMDS_STRING += ' sampler ' + s['name']
            CMDS_STRING += ' rate ' + str(s['sampling-rate']) + '\n'
    # Flow Group Configuration
    if (len(AclRules) != 0):
        aclRules = AclRules['ACL_RULE_LIST']
        aclRuleHash = getAclRuleHash(aclRules)
        flowGroupPerIntf = {}
        intfExists = False
        if (len(FlowgroupCfg) != 0):
            for f in FlowgroupCfg:
                configured = True
                rulename = f['name']
                CMDS_STRING += ' flow-group ' + rulename
                aclCfg = aclRuleHash[rulename]
                if 'SRC_MAC' in aclCfg:
                    CMDS_STRING += ' src-mac ' + aclCfg['SRC_MAC']
                if 'DST_MAC' in aclCfg:
                    CMDS_STRING += ' dst-mac ' + aclCfg['DST_MAC']
                if 'ETHER_TYPE' in aclCfg:
                    CMDS_STRING += ' ethertype ' + aclCfg['ETHER_TYPE']
                if 'IP_TYPE' in aclCfg:
                #    CMDS_STRING += ' ip-type ' + getIpType(aclCfg['IP_TYPE'])
                    if aclCfg['IP_TYPE'] == "IPV6ANY":
                        if 'SRC_IPV6' in aclCfg:
                            CMDS_STRING += ' src-ip ' + (aclCfg['SRC_IPV6'])
                        if 'DST_IPV6' in aclCfg:
                            CMDS_STRING += ' dst-ip ' + (aclCfg['DST_IPV6'])
                    else:
                        if 'SRC_IP' in aclCfg:
                            if((aclCfg['SRC_IP']) != "0.0.0.0/0"):
                                CMDS_STRING += ' src-ip ' + (aclCfg['SRC_IP'])
                        if 'DST_IP' in aclCfg:
                            if((aclCfg['DST_IP']) != "0.0.0.0/0"):
                                CMDS_STRING += ' dst-ip ' + (aclCfg['DST_IP'])
                if 'IP_PROTOCOL' in aclCfg:
                    CMDS_STRING += ' protocol ' + getProtocol(aclCfg['IP_PROTOCOL'])
                if 'L4_SRC_PORT' in aclCfg:
                    CMDS_STRING += ' l4-src-port ' + str(aclCfg['L4_SRC_PORT'])
                if 'L4_DST_PORT' in aclCfg:
                    CMDS_STRING += ' l4-dst-port ' + str(aclCfg['L4_DST_PORT'])
                if 'PRIORITY' in aclCfg:
                    CMDS_STRING += ' priority ' + str(aclCfg['PRIORITY'])

                CMDS_STRING += "\n"

    #Interface Configuration
    CMDS_STRING = '!' + "\n" + 'tam' + "\n" + CMDS_STRING
    return CMDS_STRING

def show_tam_dropmonitor(DropmonitorCfg, AgingIntervalCfg):
    CMDS_STRING = ''
    if (len(AgingIntervalCfg) != 0):
        CMDS_STRING += '  aging-interval ' + str(AgingIntervalCfg[0]['aging-interval']) + "\n"

    if (len(DropmonitorCfg) != 0):
        for s in DropmonitorCfg:
            CMDS_STRING += '  session ' + s['name']
            if 'flowgroup' in s:
                CMDS_STRING += ' flowgroup ' + s['flowgroup']
            if 'collector' in s:
                CMDS_STRING += ' collector ' + s['collector']
            if 'sample-rate' in s:
                CMDS_STRING += ' sampler ' + s['sample-rate']
            CMDS_STRING += "\n"
    if (CMDS_STRING != ""):
        CMDS_STRING = " drop-monitor\n" + CMDS_STRING
    return CMDS_STRING

def show_tam_ifa(IfaCfg):
    CMDS_STRING = ''
    if (len(IfaCfg) != 0):
        for i in IfaCfg:
            CMDS_STRING += '  session ' + i['name']
            if 'flowgroup' in i:
                CMDS_STRING += ' flowgroup ' + i['flowgroup']
            if 'collector' in i:
                CMDS_STRING += ' collector ' + i['collector']
            if 'sample-rate' in i:
                CMDS_STRING += ' sampler ' + i['sample-rate']
            if 'node-type' in i:
                CMDS_STRING += ' node-type ' + i['node-type']
            CMDS_STRING += "\n"
    if (CMDS_STRING != ""):
        CMDS_STRING = " ifa\n" + CMDS_STRING
    return CMDS_STRING

def show_tam_tailstamping(TailstampingCfg):
    CMDS_STRING = ''
    if (len(TailstampingCfg) != 0):
        for t in TailstampingCfg:
            CMDS_STRING += '  session ' + t['name']
            if 'flowgroup' in t:
                CMDS_STRING += ' flowgroup ' + t['flowgroup']
            CMDS_STRING += "\n"
    if (CMDS_STRING != ""):
        CMDS_STRING = " tail-stamping\n" + CMDS_STRING
    return CMDS_STRING

def GetFeatureStatus(FeaturesCfg):
    result = {}
    if len(FeaturesCfg) != 0:
        for f in FeaturesCfg:
            result[f['feature-ref']] = f['op-status']
    return result

def show_tam_config(render_tables):
   CMDS_STRING_TAM = ''
   SwitchCfg = render_tables[SWITCH] if SWITCH in render_tables else []
   CollectorsCfg = render_tables[COLLECTORS] if COLLECTORS in render_tables else []
   FeaturesCfg = render_tables[FEATURES] if FEATURES in render_tables else []
   featuresCfg = GetFeatureStatus(FeaturesCfg)
   SamplingrateCfg = render_tables[SAMPLINGRATE] if SAMPLINGRATE in render_tables else []
   FlowgroupCfg = render_tables[FLOWGROUP] if FLOWGROUP in render_tables else []
   AclRules = render_tables[ACL_RULES] if ACL_RULES in render_tables else []

   AgingIntervalCfg = render_tables[AGING_INTERVAL] if AGING_INTERVAL in render_tables else []
   DropmonitorCfg = render_tables[DROPMONITOR] if DROPMONITOR in render_tables else []
   IfaCfg = render_tables[IFA_SESSIONS] if IFA_SESSIONS in render_tables else []
   TailstampingCfg = render_tables[TAILSTAMPING_SESSIONS] if TAILSTAMPING_SESSIONS in render_tables else []
   
   tamCfg = get_tam_config_cmds(SwitchCfg, CollectorsCfg, SamplingrateCfg, FlowgroupCfg, AclRules)
   CMDS_STRING_TAM += tamCfg

   dropMonitorCmds =  '!\n'
   ifaCmds =  '!\n'
   tailstampingCmds =  '!\n'
   if ((len(DropmonitorCfg) != 0) or (len(AgingIntervalCfg) != 0)):
       dropMonitorCmds += show_tam_dropmonitor(DropmonitorCfg, AgingIntervalCfg)
       if 'DROPMONITOR' in featuresCfg:
           if (featuresCfg['DROPMONITOR'] == "ACTIVE"):
               dropMonitorCmds += '  enable\n'
   if (len(IfaCfg) != 0):
       ifaCmds += show_tam_ifa(IfaCfg)
       if 'IFA' in featuresCfg:
           if (featuresCfg['IFA'] == "ACTIVE"):
               ifaCmds += '  enable\n'
   if (len(TailstampingCfg) != 0):
       tailstampingCmds += show_tam_tailstamping(TailstampingCfg)
       if 'TAILSTAMPING' in featuresCfg:
           if (featuresCfg['TAILSTAMPING'] == "ACTIVE"):
               tailstampingCmds += '  enable\n'

   if (dropMonitorCmds != "") or (ifaCmds != "") or (tailstampingCmds != ""):
       if (dropMonitorCmds != ""):
           CMDS_STRING_TAM += dropMonitorCmds
       if (ifaCmds != ""):
           CMDS_STRING_TAM += ifaCmds
       if (tailstampingCmds != ""):
           CMDS_STRING_TAM += tailstampingCmds
    

   return 'CB_SUCCESS', CMDS_STRING_TAM

def show_tam_interface_config(render_tables):

   intf = str(render_tables['name'])

   CMDS_STRING_TAM = ''   
   
   FlowgroupCfg = render_tables[FLOWGROUP] if FLOWGROUP in render_tables else []
   AclRules = render_tables[ACL_RULES] if ACL_RULES in render_tables else []
   
   tamIntfCfg = get_tam_interface_config_cmds(intf, FlowgroupCfg, AclRules)
   CMDS_STRING_TAM += tamIntfCfg


   return 'CB_SUCCESS', CMDS_STRING_TAM
