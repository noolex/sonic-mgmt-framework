//////////////////////////////////////////////////////////////////////////
//
// Copyright 2020 Broadcom.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
//////////////////////////////////////////////////////////////////////////

package transformer

import (
    "os"
    "errors"
    "strings"
    "strconv"
    "syscall"
    "io/ioutil"
    "encoding/json"
    "translib/db"
    "translib/tlerr"
    log "github.com/golang/glog"
    "github.com/openconfig/ygot/ygot"
    "translib/ocbinds"
)

//Sub structure required based on the counters file in the DUT
type CounterObj  struct {
    Value         string    `json: "value"`
    Description   string    `json:"description"`
    }

// Counters structure for DHCP
type JSONDhcpCounters  struct {
    BootrequestSent        CounterObj  `json:"bootrequest-sent, omitempty"`
    BootreplySent          CounterObj  `json:"bootreply-sent, omitempty"`
    TotalDropped           CounterObj  `json:"total-dropped, omitempty"`
    InvalidOpcode          CounterObj  `json:"invalid-opcode, omitempty"`
    InvalidOptions         CounterObj  `json:"invalid-options, omitempty"`
    BootrequestReceived    CounterObj  `json:"bootrequest-received, omitempty"`
    DhcpDeclineReceived    CounterObj  `json:"dhcp-decline-received, omitempty"`
    DhcpDiscoverReceived   CounterObj  `json:"dhcp-discover-received, omitempty"`
    DhcpInformReceived     CounterObj  `json:"dhcp-inform-received, omitempty"`
    DhcpRequestReceived    CounterObj  `json:"dhcp-request-received, omitempty"`
    DhcpOfferSent          CounterObj  `json:"dhcp-offer-sent, omitempty"`
    DhcpAckSent            CounterObj  `json:"dhcp-ack-sent, omitempty"`
    DhcpNackSent           CounterObj  `json:"dhcp-nack-sent, omitempty"`
}

// Counters structure for DHCPv6
type JSONDhcpv6Counters  struct {
    TotalDropped                CounterObj  `json:"total-dropped, omitempty"`
    InvalidOpcode               CounterObj  `json:"invalid-opcode, omitempty"`
    InvalidOptions              CounterObj  `json:"invalid-options, omitempty"`
    Dhcpv6SolicitReceived       CounterObj  `json:"dhcpv6-solicit-received, omitempty"`
    Dhcpv6DeclineReceived       CounterObj  `json:"dhcpv6-decline-received, omitempty"`
    Dhcpv6RequestReceived       CounterObj  `json:"dhcpv6-request-received, omitempty"`
    Dhcpv6ReleaseReceived       CounterObj  `json:"dhcpv6-release-received, omitempty"`
    Dhcpv6ConfirmReceived       CounterObj  `json:"dhcpv6-confirm-received, omitempty"`
    Dhcpv6RebindReceived        CounterObj  `json:"dhcpv6-rebind-received, omitempty"`
    Dhcpv6InfoRequestReceived   CounterObj  `json:"dhcpv6-Info-request-received, omitempty"`
    Dhcpv6RelayReplyReceived    CounterObj  `json:"dhcpv6-relay-reply-received, omitempty"`
    Dhcpv6AdvertiseSent         CounterObj  `json:"dhcpv6-advertise-sent, omitempty"`
    Dhcpv6ReplySent             CounterObj  `json:"dhcpv6-reply-sent, omitempty"`
    Dhcpv6ReconfigureSent       CounterObj  `json:"dhcpv6-reconfigure-sent, omitempty"`
    Dhcpv6RelayForwSent         CounterObj  `json:"dhcpv6-relay-forw-sent, omitempty"`
}

//globals
const PATH_PREFIX = "/mnt/tmp/"

func init () {
    XlateFuncBind("relay_agent_table_xfmr", relay_agent_table_xfmr)
    XlateFuncBind("YangToDb_relay_agent_intf_tbl_key_xfmr", YangToDb_relay_agent_intf_tbl_key_xfmr)
    XlateFuncBind("DbToYang_relay_agent_intf_tbl_key_xfmr", DbToYang_relay_agent_intf_tbl_key_xfmr)
    XlateFuncBind("DbToYang_relay_agent_counters_xfmr", DbToYang_relay_agent_counters_xfmr)
    XlateFuncBind("DbToYang_relay_agent_v6_counters_xfmr", DbToYang_relay_agent_v6_counters_xfmr)
}

// Transformer function to loop over multiple interfaces
var relay_agent_table_xfmr TableXfmrFunc = func (inParams XfmrParams) ([]string, error) {
    var tblList []string
    var err error

    log.Info("RATableXfmrFunc - Uri: ", inParams.uri);
    pathInfo := NewPathInfo(inParams.uri)

    targetUriPath, err := getYangPathFromUri(pathInfo.Path)

    ifName := pathInfo.Var("id");
    log.Info(ifName)

    if ifName == "" {
        log.Info("TableXfmrFunc - intf_table_xfmr Intf key is not present")

        if _, ok := dbIdToTblMap[inParams.curDb]; !ok {
            log.Info("TableXfmrFunc - intf_table_xfmr db id entry not present")
            return tblList, errors.New("Key not present")
        } else {
            return dbIdToTblMap[inParams.curDb], nil
        }
    }

    intfType, _, ierr := getIntfTypeByName(ifName)
    if intfType == IntfTypeUnset || ierr != nil {
        log.Info("TableXfmrFunc - Invalid interface type IntfTypeUnset");
        return tblList, errors.New("Invalid interface type IntfTypeUnset");
    }
                      
    log.Info(intfType)

    intTbl := IntfTypeTblMap[intfType]
    log.Info("TableXfmrFunc - targetUriPath : ", targetUriPath)
    log.Info(intTbl)


    if (intfType == IntfTypeEthernet)  || intfType == IntfTypeVlan || 
       intfType == IntfTypePortChannel {
            tblList = append(tblList, intTbl.cfgDb.intfTN)
            log.Info(tblList)
    }
    return tblList, err

}

// Function to read the interface name from the interface table (interface, vlan, portchannel
var YangToDb_relay_agent_intf_tbl_key_xfmr KeyXfmrYangToDb = func(inParams XfmrParams) (string, error) {
    var err error

    pathInfo := NewPathInfo(inParams.uri)
    ifName := pathInfo.Var("id")


    return ifName, err
}
//Function to fetch the helper address from the appropriate interface table
var DbToYang_relay_agent_intf_tbl_key_xfmr KeyXfmrDbToYang = func(inParams XfmrParams) (map[string]interface{}, error) {
    var err error
    res_map := make(map[string]interface{})
    log.Info("DbToYang_relay_agent_intf_tbl_key_xfmr: ", inParams.key)

    if (inParams.key != "") {
        var configDb, _ = db.NewDB(getDBOptions(db.ConfigDB))

        intfType, _, _ := getIntfTypeByName(inParams.key)

        intTbl := IntfTypeTblMap[intfType]

        //tblList, intTbl.cfgDb.intfTN
        entry, dbErr := configDb.GetEntry(&db.TableSpec{Name:intTbl.cfgDb.intfTN}, db.Key{Comp: []string{inParams.key}})
        configDb.DeleteDB()
        if dbErr != nil {
            log.Info("Failed to read mgmt port status from config DB, " + intTbl.cfgDb.intfTN + " " + inParams.key)
            return res_map, dbErr
        }

        if (strings.HasPrefix(inParams.uri, "/openconfig-relay-agent:relay-agent/dhcp/")) && (entry.Get("dhcp_servers@") != "")  {

        //Check if config exist in table for the interface
            res_map["id"] = inParams.key
        }

        if (strings.HasPrefix(inParams.uri, "/openconfig-relay-agent:relay-agent/dhcpv6/")) && (entry.Get("dhcpv6_servers@") != "")  {
        //Check if config exist in table for the interface
            res_map["id"] = inParams.key
        }
    }

    return res_map, err
}

// Helper function to read the DHCP counters from the file mounted in /mnt/tmp folder
func getRelayCountersFromFile (fileName string, counterObj interface{}) error {
   
    if log.V(7) {
    //If verbose logging is enabled, log info 
    log.Infof("getRelayCountersFromFile Enter")
    }

    tmpFileName := PATH_PREFIX + fileName
    log.Info(tmpFileName) 

    jsonFile, err := os.Open(tmpFileName)
    if err != nil {
        log.Warningf("opening of dhcp counters json file failed")
        errStr := "Information not available"
        terr := tlerr.NotFoundError{Format: errStr}
        return terr
    }
    syscall.Flock(int(jsonFile.Fd()),syscall.LOCK_EX)
    log.Infof("syscall.Flock done")

    defer jsonFile.Close()
    defer log.Infof("jsonFile.Close called")
    defer syscall.Flock(int(jsonFile.Fd()), syscall.LOCK_UN);
    defer log.Infof("syscall.Flock unlock  called")

    byteValue, _ := ioutil.ReadAll(jsonFile)
    err = json.Unmarshal(byteValue, counterObj)
    if err != nil {
        log.Warningf("unmarshal of the json counters failed")
        errStr := "json.Unmarshal failed"
        terr := tlerr.InternalError{Format: errStr}
        return terr
    }
    return nil
}

// Helper function to get the root object
func getRelayAgentRoot(s *ygot.GoStruct) *ocbinds.OpenconfigRelayAgent_RelayAgent {
    deviceObj := (*s).(*ocbinds.Device)
    return deviceObj.RelayAgent
}

// Helper function to convert Value from string to uint64
func getCounterValue(valStr string) *uint64 {
    if val, err := strconv.ParseUint(valStr, 10, 64); err == nil {
        return &val
    }
   return nil
}

//sub tree transformer - that will read the appropriate file and populate the DHCP counters
var DbToYang_relay_agent_counters_xfmr SubTreeXfmrDbToYang = func(inParams XfmrParams) error {
    var err error
    var raObj *ocbinds.OpenconfigRelayAgent_RelayAgent_Dhcp_Interfaces_Interface 
    var jsonRelayAgentCounter JSONDhcpCounters

    log.Info("In DbToYang_relay_agent_counters_xfmr")
    if log.V(7) {
      log.Info(inParams)
    }
    relayAgentObj := getRelayAgentRoot(inParams.ygRoot)
    log.Info(relayAgentObj)

    pathInfo := NewPathInfo(inParams.uri)
    ifName := pathInfo.Var("id")

    if ifName == "" { 
       return err 
    }

    targetUriPath, err := getYangPathFromUri(pathInfo.Path)
    
    fileName := "dhcp-relay-ipv4-stats-"+ ifName + ".json"
 
    err = getRelayCountersFromFile(fileName, &jsonRelayAgentCounter)
    log.Info(jsonRelayAgentCounter)
    if err != nil {
        log.Infof("getRelayCountersFromFile failed")
        return err
    }

    
    if strings.HasPrefix(targetUriPath, "/openconfig-relay-agent:relay-agent/dhcp/interfaces/interface/state/counters") {
        if relayAgentObj != nil && relayAgentObj.Dhcp != nil {
            var ok bool = false
            ygot.BuildEmptyTree(relayAgentObj.Dhcp)
            ygot.BuildEmptyTree(relayAgentObj.Dhcp.Interfaces)
         if raObj, ok = relayAgentObj.Dhcp.Interfaces.Interface[ifName]; !ok {
                raObj, _ = relayAgentObj.Dhcp.Interfaces.NewInterface(ifName)
            }
            ygot.BuildEmptyTree(raObj)
        } else if relayAgentObj != nil {
            ygot.BuildEmptyTree(relayAgentObj)
            ygot.BuildEmptyTree(relayAgentObj.Dhcp)
            ygot.BuildEmptyTree(relayAgentObj.Dhcp.Interfaces)
            raObj, _ = relayAgentObj.Dhcp.Interfaces.NewInterface(ifName)
            ygot.BuildEmptyTree(raObj)
        }
        ygot.BuildEmptyTree(raObj.State)
        ygot.BuildEmptyTree(raObj.State.Counters)
    } else {
        err = errors.New("Invalid URI : " + targetUriPath)

    }

    counterObj := relayAgentObj.Dhcp.Interfaces.Interface[ifName].State.Counters

    counterObj.TotalDropped = getCounterValue(jsonRelayAgentCounter.TotalDropped.Value)
    
    counterObj.InvalidOpcode = getCounterValue(jsonRelayAgentCounter.InvalidOpcode.Value)

    counterObj.InvalidOptions = getCounterValue(jsonRelayAgentCounter.InvalidOptions.Value)

    counterObj.BootrequestReceived = getCounterValue(jsonRelayAgentCounter.BootrequestReceived.Value)

    counterObj.DhcpDeclineReceived = getCounterValue(jsonRelayAgentCounter.DhcpDeclineReceived.Value)

    counterObj.DhcpDiscoverReceived = getCounterValue(jsonRelayAgentCounter.DhcpDiscoverReceived.Value)

    counterObj.DhcpInformReceived = getCounterValue(jsonRelayAgentCounter.DhcpInformReceived.Value)

    counterObj.DhcpRequestReceived = getCounterValue(jsonRelayAgentCounter.DhcpRequestReceived.Value)

    counterObj.BootrequestSent = getCounterValue(jsonRelayAgentCounter.BootrequestSent.Value)

    counterObj.BootreplySent = getCounterValue(jsonRelayAgentCounter.BootreplySent.Value)

    counterObj.DhcpOfferSent = getCounterValue(jsonRelayAgentCounter.DhcpOfferSent.Value)

    counterObj.DhcpAckSent = getCounterValue(jsonRelayAgentCounter.DhcpAckSent.Value)

    counterObj.DhcpNackSent = getCounterValue(jsonRelayAgentCounter.DhcpNackSent.Value)

    return err
}


//sub tree transformer - that will read the appropriate file and populate the DHCPv6 counters
var DbToYang_relay_agent_v6_counters_xfmr SubTreeXfmrDbToYang = func(inParams XfmrParams) error {
    var err error
    var raObj *ocbinds.OpenconfigRelayAgent_RelayAgent_Dhcpv6_Interfaces_Interface 
    var jsonV6RelayAgentCounter JSONDhcpv6Counters

    log.Info("In DbToYang_relay_agent_v6_counters_xfmr")
    if log.V(7) {
       log.Info(inParams)
    }
    relayAgentObj := getRelayAgentRoot(inParams.ygRoot)
    log.Info(relayAgentObj)

    pathInfo := NewPathInfo(inParams.uri)
    ifName := pathInfo.Var("id")
    
    if ifName == "" { 
    return err 
    }

    targetUriPath, err := getYangPathFromUri(pathInfo.Path)

    fileName := "dhcp-relay-ipv6-stats-"+ ifName + ".json"
 
    err = getRelayCountersFromFile(fileName, &jsonV6RelayAgentCounter)
    log.Info(jsonV6RelayAgentCounter)
    if err != nil {
        log.Infof("getRelayCountersFromFile failed")
        return err
    }

    if strings.HasPrefix(targetUriPath, "/openconfig-relay-agent:relay-agent/dhcpv6/interfaces/interface/state/counters") {
        if relayAgentObj != nil && relayAgentObj.Dhcpv6 != nil {
            var ok bool = false
            ygot.BuildEmptyTree(relayAgentObj.Dhcpv6)
            ygot.BuildEmptyTree(relayAgentObj.Dhcpv6.Interfaces)
         if raObj, ok = relayAgentObj.Dhcpv6.Interfaces.Interface[ifName]; !ok {
                raObj, _ = relayAgentObj.Dhcpv6.Interfaces.NewInterface(ifName)
            }
            ygot.BuildEmptyTree(raObj)
        } else if relayAgentObj != nil {
            ygot.BuildEmptyTree(relayAgentObj)
            ygot.BuildEmptyTree(relayAgentObj.Dhcpv6)
            ygot.BuildEmptyTree(relayAgentObj.Dhcpv6.Interfaces)
            raObj, _ = relayAgentObj.Dhcpv6.Interfaces.NewInterface(ifName)
            ygot.BuildEmptyTree(raObj)
        }
        ygot.BuildEmptyTree(raObj.State)
        ygot.BuildEmptyTree(raObj.State.Counters)
    } else {
        err = errors.New("Invalid URI : " + targetUriPath)

    }

    counterObj := relayAgentObj.Dhcpv6.Interfaces.Interface[ifName].State.Counters

    counterObj.TotalDropped = getCounterValue(jsonV6RelayAgentCounter.TotalDropped.Value)    

    counterObj.InvalidOpcode = getCounterValue(jsonV6RelayAgentCounter.InvalidOpcode.Value)

    counterObj.InvalidOptions = getCounterValue(jsonV6RelayAgentCounter.InvalidOptions.Value)
          
    counterObj.Dhcpv6SolicitReceived = getCounterValue(jsonV6RelayAgentCounter.Dhcpv6SolicitReceived.Value)
              
    counterObj.Dhcpv6DeclineReceived = getCounterValue(jsonV6RelayAgentCounter.Dhcpv6DeclineReceived.Value)

    counterObj.Dhcpv6RequestReceived = getCounterValue(jsonV6RelayAgentCounter.Dhcpv6RequestReceived.Value)

    counterObj.Dhcpv6ReleaseReceived = getCounterValue(jsonV6RelayAgentCounter.Dhcpv6ReleaseReceived.Value)

    counterObj.Dhcpv6ConfirmReceived = getCounterValue(jsonV6RelayAgentCounter.Dhcpv6ConfirmReceived.Value)

    counterObj.Dhcpv6RebindReceived = getCounterValue(jsonV6RelayAgentCounter.Dhcpv6RebindReceived.Value)

    counterObj.Dhcpv6InfoRequestReceived = getCounterValue(jsonV6RelayAgentCounter.Dhcpv6InfoRequestReceived.Value)

    counterObj.Dhcpv6RelayReplyReceived = getCounterValue(jsonV6RelayAgentCounter.Dhcpv6RelayReplyReceived.Value)

    counterObj.Dhcpv6AdverstiseSent = getCounterValue(jsonV6RelayAgentCounter.Dhcpv6AdvertiseSent.Value)

    counterObj.Dhcpv6ReplySent = getCounterValue(jsonV6RelayAgentCounter.Dhcpv6ReplySent.Value)

    counterObj.Dhcpv6ReconfigureSent = getCounterValue(jsonV6RelayAgentCounter.Dhcpv6ReconfigureSent.Value)

    counterObj.Dhcpv6RelayForwSent = getCounterValue(jsonV6RelayAgentCounter.Dhcpv6RelayForwSent.Value)

    return err
}
