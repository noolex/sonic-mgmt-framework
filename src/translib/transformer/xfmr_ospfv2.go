
package transformer

import (
    "errors"
    "strconv"
    "math"
    "strings"
    "encoding/json"
    "translib/ocbinds"
//    "translib/tlerr"
//    "translib/db"
    "os/exec"
//  "io"
//  "bytes"
//  "net"
//  "encoding/binary"
    "github.com/openconfig/ygot/ygot"
    log "github.com/golang/glog"
)

//const sock_addr = "/etc/sonic/frr/bgpd_client_sock"


func getOspfv2Root (inParams XfmrParams) (*ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Ospfv2, string, error) {
    pathInfo := NewPathInfo(inParams.uri)
    ospfv2VrfName := pathInfo.Var("name")
    ospfv2Identifier := pathInfo.Var("identifier")
    ospfv2InstanceNumber := pathInfo.Var("name#2")
    var err error

    if len(pathInfo.Vars) <  3 {
        return nil, "", errors.New("Invalid Key length")
    }

    if len(ospfv2VrfName) == 0 {
        return nil, "", errors.New("vrf name is missing")
    }

    if strings.Contains(ospfv2Identifier, "OSPF") == false {
        return nil, "", errors.New("Protocol ID OSPF is missing")
    }
 
    if len(ospfv2InstanceNumber) == 0 {
        return nil, "", errors.New("Protocol Insatnce Id is missing")
    }

    deviceObj := (*inParams.ygRoot).(*ocbinds.Device)
    netInstsObj := deviceObj.NetworkInstances

    if netInstsObj.NetworkInstance == nil {
        return nil, "", errors.New("Network-instances container missing")
    }

    netInstObj := netInstsObj.NetworkInstance[ospfv2VrfName]
    if netInstObj == nil {
        return nil, "", errors.New("Network-instance obj for OSPFv2 missing")
    }

    if netInstObj.Protocols == nil || len(netInstObj.Protocols.Protocol) == 0 {
        return nil, "", errors.New("Network-instance protocols-container for OSPFv2 missing or protocol-list empty")
    }

    var protoKey ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Key
    protoKey.Identifier = ocbinds.OpenconfigPolicyTypes_INSTALL_PROTOCOL_TYPE_OSPF
    protoKey.Name = ospfv2InstanceNumber
    protoInstObj := netInstObj.Protocols.Protocol[protoKey]
    if protoInstObj == nil {
        return nil, "", errors.New("Network-instance OSPFv2-Protocol obj missing")
    }

    if protoInstObj.Ospfv2 == nil {
        var _Ospfv2_obj ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Ospfv2
        protoInstObj.Ospfv2 = &_Ospfv2_obj
    }

    ygot.BuildEmptyTree (protoInstObj.Ospfv2)
    return protoInstObj.Ospfv2, ospfv2VrfName, err
}


var YangToDb_ospfv2_router_tbl_key_xfmr KeyXfmrYangToDb = func(inParams XfmrParams) (string, error) {
    var err error

    log.Info("YangToDb_ospfv2_router_tbl_key_xfmr - URI: ", inParams.uri)

    pathInfo := NewPathInfo(inParams.uri)

    ospfv2VrfName := pathInfo.Var("name")
    ospfv2Identifier := pathInfo.Var("identifier")
    ospfv2InstanceNumber := pathInfo.Var("name#2")

    if len(pathInfo.Vars) <  3 {
        return "", errors.New("Invalid Key length")
    }

    if len(ospfv2VrfName) == 0 {
        return "", errors.New("vrf name is missing")
    }

    if strings.Contains(ospfv2Identifier,"OSPF") == false {
        return "", errors.New("OSPF ID is missing")
    }

    if len(ospfv2InstanceNumber) == 0 {
        return "", errors.New("Protocol instance number Name is missing")
    }

    log.Info("URI VRF ", ospfv2VrfName)

    log.Info("YangToDb_ospfv2_router_tbl_key_xfmr returned Key: ", ospfv2VrfName)
    return ospfv2VrfName, err
}

var DbToYang_ospfv2_router_tbl_key_xfmr KeyXfmrDbToYang = func(inParams XfmrParams) (map[string]interface{}, error) {
    res_map := make(map[string]interface{})
    var err error

    ospfv2RouterTableKey := inParams.key
    log.Info("DbToYang_ospfv2_router_tbl_key: ", ospfv2RouterTableKey)

    res_map["name"] = ospfv2RouterTableKey

    log.Info("DbToYang_ospfv2_router_tbl_key_xfmr key: ", res_map)
    return res_map, err
}


var YangToDb_ospfv2_router_enable_fld_xfmr FieldXfmrYangToDb = func(inParams XfmrParams) (map[string]string, error) {

    res_map := make(map[string]string)

    res_map["NULL"] = "NULL"
    return res_map, nil
}

var DbToYang_ospfv2_router_enable_fld_xfmr FieldXfmrDbtoYang = func(inParams XfmrParams) (map[string]interface{}, error) {

    var err error
    res_map := make(map[string]interface{})

    ospfv2RouterTableKey := inParams.key
    log.Info("DbToYang_ospfv2_router_enable_fld_xfmr: ", ospfv2RouterTableKey)

    res_map["name"] = ospfv2RouterTableKey
    return res_map, err
}


func getAreaDotted(areaString string) string {
    if len(areaString) == 0 {
       log.Info("getAreaDotted: Null area id received")
       return ""
    }

    areaInt, err := strconv.ParseInt(areaString, 10, 64)
    if err == nil {
        b0 := strconv.FormatInt((areaInt >> 24) & 0xff, 10)
        b1 := strconv.FormatInt((areaInt >> 16) & 0xff, 10)
        b2 := strconv.FormatInt((areaInt >> 8) & 0xff, 10)
        b3 := strconv.FormatInt((areaInt & 0xff), 10)
         
        areaDotted :=  b0 + "." + b1 + "." + b2 + "." + b3
        log.Info("getAreaDotted: ", areaDotted)
        return areaDotted
     }

     log.Info("getAreaDotted: ", areaString) 
     return areaString
}


var YangToDb_ospfv2_router_area_tbl_key_xfmr KeyXfmrYangToDb = func(inParams XfmrParams) (string, error) {
    var err error
    var ospfv2VrfName string

    log.Info("YangToDb_ospfv2_router_area_tbl_key_xfmr: ", inParams.uri)
    pathInfo := NewPathInfo(inParams.uri)

    ospfv2VrfName    =  pathInfo.Var("name")
    ospfv2Identifier      := pathInfo.Var("identifier")
    ospfv2InstanceNumber  := pathInfo.Var("name#2")
    ospfv2AreaId   := pathInfo.Var("identifier#2")

    if len(pathInfo.Vars) <  4 {
        err = errors.New("Invalid Key length");
        log.Info("Invalid Key length", len(pathInfo.Vars))
        return ospfv2VrfName, err
    }

    if len(ospfv2VrfName) == 0 {
        err = errors.New("vrf name is missing");
        log.Info("VRF Name is Missing")
        return "", err
    }
    if strings.Contains(ospfv2Identifier,"OSPF") == false {
        err = errors.New("OSPF ID is missing");
        log.Info("OSPF ID is missing")
        return "", err
    }
    if len(ospfv2InstanceNumber) == 0 {
        err = errors.New("OSPF intance number/name is missing");
        log.Info("Protocol Name is Missing")
        return "", err
    }
    if len(ospfv2AreaId) == 0 {
        err = errors.New("OSPF area Id is missing")
        log.Info("OSPF area Id is Missing")
        return "", nil
    }

    ospfv2AreaId = getAreaDotted(ospfv2AreaId)

    log.Info("URI VRF", ospfv2VrfName)
    log.Info("URI Area Id", ospfv2AreaId)

    var pAreaTableKey string

    pAreaTableKey = ospfv2VrfName + "|" + ospfv2AreaId

    log.Info("YangToDb_ospfv2_router_area_tbl_key_xfmr: pAreaTableKey - ", pAreaTableKey)
    return pAreaTableKey, nil
}


var DbToYang_ospfv2_router_area_tbl_key_xfmr KeyXfmrDbToYang = func(inParams XfmrParams) (map[string]interface{}, error) {
    res_map := make(map[string]interface{})
    entry_key := inParams.key
    log.Info("DbToYang_ospfv2_router_area_tbl_key: entry key - ", entry_key)

    areaTableKeys := strings.Split(entry_key, "|")
    ospfv2AreaId:= areaTableKeys[1]

    res_map["identifier"] = ospfv2AreaId

    log.Info("DbToYang_ospfv2_router_area_tbl_key: res_map - ", res_map)
    return res_map, nil
}

var YangToDb_ospfv2_router_area_area_id_fld_xfmr FieldXfmrYangToDb = func(inParams XfmrParams) (map[string]string, error) {

    res_map := make(map[string]string)

    res_map["NULL"] = "NULL"
    return res_map, nil
}

var DbToYang_ospfv2_router_area_area_id_fld_xfmr FieldXfmrDbtoYang = func(inParams XfmrParams) (map[string]interface{}, error) {

    var err error
    res_map := make(map[string]interface{})

    entry_key := inParams.key
    areaTableKeys := strings.Split(entry_key, "|")
    ospfv2AreaId:= areaTableKeys[1]

    res_map["identifier"] = ospfv2AreaId
    return res_map, err
}


var YangToDb_ospfv2_router_area_policy_tbl_key_xfmr KeyXfmrYangToDb = func(inParams XfmrParams) (string, error) {
    var err error
    var ospfv2VrfName string

    log.Info("YangToDb_ospfv2_router_area_policy_tbl_key_xfmr: ", inParams.uri)
    pathInfo := NewPathInfo(inParams.uri)

    ospfv2VrfName    =  pathInfo.Var("name")
    ospfv2Identifier      := pathInfo.Var("identifier")
    ospfv2InstanceNumber  := pathInfo.Var("name#2")
    ospfv2AreaId   := pathInfo.Var("src-area")

    if len(pathInfo.Vars) <  4 {
        err = errors.New("Invalid Key length");
        log.Info("Invalid Key length", len(pathInfo.Vars))
        return ospfv2VrfName, err
    }

    if len(ospfv2VrfName) == 0 {
        err = errors.New("vrf name is missing");
        log.Info("VRF Name is Missing")
        return "", err
    }
    if strings.Contains(ospfv2Identifier,"OSPF") == false {
        err = errors.New("OSPF ID is missing");
        log.Info("OSPF ID is missing")
        return "", err
    }
    if len(ospfv2InstanceNumber) == 0 {
        err = errors.New("OSPF intance number/name is missing");
        log.Info("Protocol Name is Missing")
        return "", err
    }
    if len(ospfv2AreaId) == 0 {
        err = errors.New("OSPF area Id is missing")
        log.Info("OSPF area Id is Missing")
        return "", nil
    }

    ospfv2AreaId = getAreaDotted(ospfv2AreaId)

    log.Info("URI VRF", ospfv2VrfName)
    log.Info("URI Area Id", ospfv2AreaId)

    var pAreaTableKey string

    pAreaTableKey = ospfv2VrfName + "|" + ospfv2AreaId

    log.Info("YangToDb_ospfv2_router_area_policy_tbl_key_xfmr: pAreaTableKey - ", pAreaTableKey)
    return pAreaTableKey, nil
}


var DbToYang_ospfv2_router_area_policy_tbl_key_xfmr KeyXfmrDbToYang = func(inParams XfmrParams) (map[string]interface{}, error) {
    res_map := make(map[string]interface{})
    entry_key := inParams.key
    log.Info("DbToYang_ospfv2_router_area_policy_tbl_key: entry key - ", entry_key)

    areaTableKeys := strings.Split(entry_key, "|")
    ospfv2AreaId:= areaTableKeys[1]

    res_map["src-area"] = ospfv2AreaId

    log.Info("DbToYang_ospfv2_router_area_policy_tbl_key: res_map - ", res_map)
    return res_map, nil
}


var YangToDb_ospfv2_router_area_policy_src_area_fld_xfmr FieldXfmrYangToDb = func(inParams XfmrParams) (map[string]string, error) {

    res_map := make(map[string]string)

    res_map["NULL"] = "NULL"
    return res_map, nil
}

var DbToYang_ospfv2_router_area_policy_src_area_fld_xfmr FieldXfmrDbtoYang = func(inParams XfmrParams) (map[string]interface{}, error) {

    var err error
    res_map := make(map[string]interface{})

    entry_key := inParams.key
    areaTableKeys := strings.Split(entry_key, "|")
    ospfv2AreaId:= areaTableKeys[1]

    res_map["src-area"] = ospfv2AreaId
    return res_map, err
}

var YangToDb_ospfv2_router_area_network_tbl_key_xfmr KeyXfmrYangToDb = func(inParams XfmrParams) (string, error) {
    var err error
    var ospfv2VrfName string

    log.Info("YangToDb_ospfv2_router_area_network_tbl_key_xfmr: ", inParams.uri)
    pathInfo := NewPathInfo(inParams.uri)

    ospfv2VrfName    =  pathInfo.Var("name")
    ospfv2Identifier      := pathInfo.Var("identifier")
    ospfv2InstanceNumber  := pathInfo.Var("name#2")
    ospfv2AreaId   := pathInfo.Var("identifier#2")
    ospfv2NetworkPrefix   := pathInfo.Var("address-prefix")

    if len(pathInfo.Vars) <  5 {
        err = errors.New("Invalid Key length");
        log.Info("Invalid Key length", len(pathInfo.Vars))
        return ospfv2VrfName, err
    }

    if len(ospfv2VrfName) == 0 {
        err = errors.New("vrf name is missing");
        log.Info("VRF Name is Missing")
        return "", err
    }
    if strings.Contains(ospfv2Identifier,"OSPF") == false {
        err = errors.New("OSPF ID is missing");
        log.Info("OSPF ID is missing")
        return "", err
    }
    if len(ospfv2InstanceNumber) == 0 {
        err = errors.New("OSPF intance number/name is missing");
        log.Info("Protocol Name is Missing")
        return "", err
    }

    if len(ospfv2AreaId) == 0 {
        err = errors.New("OSPF area Id is missing")
        log.Info("OSPF area Id is Missing")
        return "", nil
    }

    ospfv2AreaId = getAreaDotted(ospfv2AreaId)

    if len(ospfv2NetworkPrefix) == 0 {
        err = errors.New("OSPF area Network prefix is missing")
        log.Info("OSPF area Network prefix is Missing")
        return "", nil
    }

    log.Info("URI VRF ", ospfv2VrfName)
    log.Info("URI Area Id ", ospfv2AreaId)
    log.Info("URI Network ", ospfv2NetworkPrefix)

    var pNetworkTableKey string

    pNetworkTableKey = ospfv2VrfName + "|" + ospfv2AreaId + "|" + ospfv2NetworkPrefix

    log.Info("YangToDb_ospfv2_router_area_network_tbl_key_xfmr: pNetworkTableKey - ", pNetworkTableKey)
    return pNetworkTableKey, nil
}


var DbToYang_ospfv2_router_area_network_tbl_key_xfmr KeyXfmrDbToYang = func(inParams XfmrParams) (map[string]interface{}, error) {
    res_map := make(map[string]interface{})
    entry_key := inParams.key
    log.Info("DbToYang_ospfv2_router_area_network_tbl_key: entry key - ", entry_key)

    netowrkTableKeys := strings.Split(entry_key, "|")
    //ospfv2AreaId:= netowrkTableKeys[1]
    ospfv2NetworkPrefix:= netowrkTableKeys[2]

    res_map["address-prefix"] = ospfv2NetworkPrefix

    log.Info("DbToYang_ospfv2_router_area_network_tbl_key: res_map - ", res_map)
    return res_map, nil
}

var YangToDb_ospfv2_router_network_prefix_fld_xfmr FieldXfmrYangToDb = func(inParams XfmrParams) (map[string]string, error) {

    res_map := make(map[string]string)

    res_map["NULL"] = "NULL"
    return res_map, nil
}


var DbToYang_ospfv2_router_network_prefix_fld_xfmr FieldXfmrDbtoYang = func(inParams XfmrParams) (map[string]interface{}, error) {

    var err error
    res_map := make(map[string]interface{})

    entry_key := inParams.key
    netowrkTableKeys := strings.Split(entry_key, "|")
    ospfv2NetworkPrefix:= netowrkTableKeys[2]

    res_map["address-prefix"] = ospfv2NetworkPrefix
    return res_map, err
}


var YangToDb_ospfv2_router_area_virtual_link_tbl_key_xfmr KeyXfmrYangToDb = func(inParams XfmrParams) (string, error) {
    var err error
    var ospfv2VrfName string

    log.Info("YangToDb_ospfv2_router_area_virtual_link_tbl_key_xfmr: ", inParams.uri)
    pathInfo := NewPathInfo(inParams.uri)

    ospfv2VrfName    =  pathInfo.Var("name")
    ospfv2Identifier      := pathInfo.Var("identifier")
    ospfv2InstanceNumber  := pathInfo.Var("name#2")
    ospfv2AreaId   := pathInfo.Var("identifier#2")
    ospfv2RemoteRouterId   := pathInfo.Var("remote-router-id")

    if len(pathInfo.Vars) <  5 {
        err = errors.New("Invalid Key length");
        log.Info("Invalid Key length", len(pathInfo.Vars))
        return ospfv2VrfName, err
    }

    if len(ospfv2VrfName) == 0 {
        err = errors.New("vrf name is missing");
        log.Info("VRF Name is Missing")
        return "", err
    }

    if strings.Contains(ospfv2Identifier,"OSPF") == false {
        err = errors.New("OSPF ID is missing");
        log.Info("OSPF ID is missing")
        return "", err
    }

    if len(ospfv2InstanceNumber) == 0 {
        err = errors.New("OSPF intance number/name is missing");
        log.Info("Protocol Name is Missing")
        return "", err
    }

    if len(ospfv2AreaId) == 0 {
        err = errors.New("OSPF area Id is missing")
        log.Info("OSPF area Id is Missing")
        return "", nil
    }

    ospfv2AreaId = getAreaDotted(ospfv2AreaId)

    if len(ospfv2RemoteRouterId) == 0 {
        err = errors.New("OSPF area VL remote router Id is missing")
        log.Info("OSPF area VL remote router Id is Missing")
        return "", nil
    }

    log.Info("URI VRF ", ospfv2VrfName)
    log.Info("URI Area Id ", ospfv2AreaId)
    log.Info("URI Virtual link remote router Id ", ospfv2RemoteRouterId)

    var pVirtualLinkTableKey string

    pVirtualLinkTableKey = ospfv2VrfName + "|" + ospfv2AreaId + "|" + ospfv2RemoteRouterId

    log.Info("YangToDb_ospfv2_router_area_virtual_link_tbl_key_xfmr: pVirtualLinkTableKey - ", pVirtualLinkTableKey)
    return pVirtualLinkTableKey, nil
}


var DbToYang_ospfv2_router_area_virtual_link_tbl_key_xfmr KeyXfmrDbToYang = func(inParams XfmrParams) (map[string]interface{}, error) {
    res_map := make(map[string]interface{})
    entry_key := inParams.key
    log.Info("DbToYang_ospfv2_router_area_virtual_link_tbl_key: entry key - ", entry_key)

    virtualLinkTableKey := strings.Split(entry_key, "|")
    //ospfv2AreaId:= virtualLinkTableKey[1]
    ospfv2RemoteRouterId:= virtualLinkTableKey[2]

    res_map["remote-router-id"] = ospfv2RemoteRouterId

    log.Info("DbToYang_ospfv2_router_area_virtual_link_tbl_key: res_map - ", res_map)
    return res_map, nil
}

var YangToDb_ospfv2_router_area_vl_remote_router_id_fld_xfmr FieldXfmrYangToDb = func(inParams XfmrParams) (map[string]string, error) {

    res_map := make(map[string]string)

    res_map["NULL"] = "NULL"
    return res_map, nil
}

var DbToYang_ospfv2_router_area_vl_remote_router_id_fld_xfmr FieldXfmrDbtoYang = func(inParams XfmrParams) (map[string]interface{}, error) {

    var err error
    res_map := make(map[string]interface{})

    entry_key := inParams.key
    virtualLinkTableKey := strings.Split(entry_key, "|")
    //ospfv2AreaId:= virtualLinkTableKey[1]
    ospfv2RemoteRouterId:= virtualLinkTableKey[2]

    res_map["remote-router-id"] = ospfv2RemoteRouterId
    return res_map, err
}

var YangToDb_ospfv2_router_area_policy_address_range_tbl_key_xfmr KeyXfmrYangToDb = func(inParams XfmrParams) (string, error) {
    var err error
    var ospfv2VrfName string

    log.Info("YangToDb_ospfv2_router_area_policy_address_range_tbl_key_xfmr: ", inParams.uri)
    pathInfo := NewPathInfo(inParams.uri)

    ospfv2VrfName           = pathInfo.Var("name")
    ospfv2Identifier       := pathInfo.Var("identifier")
    ospfv2InstanceNumber   := pathInfo.Var("name#2")
    ospfv2policySourceArea := pathInfo.Var("src-area")
    ospfv2AddressRange     := pathInfo.Var("address-prefix")

    if len(pathInfo.Vars) <  5 {
        err = errors.New("Invalid Key length");
        log.Info("Invalid Key length", len(pathInfo.Vars))
        return ospfv2VrfName, err
    }

    if len(ospfv2VrfName) == 0 {
        err = errors.New("vrf name is missing");
        log.Info("VRF Name is Missing")
        return "", err
    }

    if strings.Contains(ospfv2Identifier,"OSPF") == false {
        err = errors.New("OSPF ID is missing");
        log.Info("OSPF ID is missing")
        return "", err
    }

    if len(ospfv2InstanceNumber) == 0 {
        err = errors.New("OSPF intance number/name is missing");
        log.Info("Protocol Name is Missing")
        return "", err
    }

    if len(ospfv2policySourceArea) == 0 {
        err = errors.New("OSPF area Id is missing")
        log.Info("OSPF area Id is Missing")
        return "", nil
    }

    ospfv2policySourceArea = getAreaDotted(ospfv2policySourceArea)

    if len(ospfv2AddressRange) == 0 {
        err = errors.New("OSPF area Address Range prefix is missing")
        log.Info("OSPF area Address Range prefix is Missing")
        return "", nil
    }

    log.Info("URI VRF ", ospfv2VrfName)
    log.Info("URI Area Id ", ospfv2policySourceArea)
    log.Info("URI Address Range ", ospfv2AddressRange)

    var pAddressRangeTableKey string

    pAddressRangeTableKey = ospfv2VrfName + "|" + ospfv2policySourceArea + "|" + ospfv2AddressRange

    log.Info("YangToDb_ospfv2_router_area_policy_address_range_tbl_key_xfmr: pAddressRangeTableKey - ", pAddressRangeTableKey)
    return pAddressRangeTableKey, nil
}


var DbToYang_ospfv2_router_area_policy_address_range_tbl_key_xfmr KeyXfmrDbToYang = func(inParams XfmrParams) (map[string]interface{}, error) {
    res_map := make(map[string]interface{})
    entry_key := inParams.key
    log.Info("DbToYang_ospfv2_router_area_policy_address_range_tbl_key: entry key - ", entry_key)

    addressRAngeTableKey := strings.Split(entry_key, "|")
    //ospfv2policySourceArea:= addressRAngeTableKey[1]
    ospfv2AddressRange:= addressRAngeTableKey[2]

    res_map["address-prefix"] = ospfv2AddressRange

    log.Info("DbToYang_ospfv2_router_area_policy_address_range_tbl_key: res_map - ", res_map)
    return res_map, nil
}


var YangToDb_ospfv2_router_area_policy_address_range_prefix_fld_xfmr FieldXfmrYangToDb = func(inParams XfmrParams) (map[string]string, error) {

    res_map := make(map[string]string)

    res_map["NULL"] = "NULL"
    return res_map, nil
}

var DbToYang_ospfv2_router_area_policy_address_range_prefix_fld_xfmr FieldXfmrDbtoYang = func(inParams XfmrParams) (map[string]interface{}, error) {

    var err error
    res_map := make(map[string]interface{})

    entry_key := inParams.key
    addressRAngeTableKey := strings.Split(entry_key, "|")
    //ospfv2policySourceArea:= addressRAngeTableKey[1]
    ospfv2AddressRange:= addressRAngeTableKey[2]

    res_map["address-prefix"] = ospfv2AddressRange
    return res_map, err
}


var YangToDb_ospfv2_router_distribute_route_tbl_key_xfmr KeyXfmrYangToDb = func(inParams XfmrParams) (string, error) {
    var err error
    var ospfv2VrfName string

    log.Info("YangToDb_ospfv2_router_distribute_route_tbl_key_xfmr: ", inParams.uri)
    pathInfo := NewPathInfo(inParams.uri)

    ospfv2VrfName    =  pathInfo.Var("name")
    ospfv2Identifier      := pathInfo.Var("identifier")
    ospfv2InstanceNumber  := pathInfo.Var("name#2")
    distributionProtocol  := pathInfo.Var("protocol")
    distributionDirection := pathInfo.Var("direction")

    if len(pathInfo.Vars) <  5 {
        err = errors.New("Invalid Key length");
        log.Info("Invalid Key length", len(pathInfo.Vars))
        return ospfv2VrfName, err
    }

    if len(ospfv2VrfName) == 0 {
        err = errors.New("vrf name is missing");
        log.Info("VRF Name is Missing")
        return "", err
    }
    if strings.Contains(ospfv2Identifier,"OSPF") == false {
        err = errors.New("OSPF ID is missing");
        log.Info("OSPF ID is missing")
        return "", err
    }
    if len(ospfv2InstanceNumber) == 0 {
        err = errors.New("OSPF intance number/name is missing");
        log.Info("Protocol Name is Missing")
        return "", err
    }

    if len(distributionProtocol) == 0 {
        err = errors.New("OSPF Route Distriburion protocol name is missing")
        log.Info("OSPF Route Distriburion protocol name Missing")
        return "", nil
    }

    if len(distributionDirection) == 0 {
        err = errors.New("OSPF Route Distriburion direction is missing")
        log.Info("OSPF Route Distriburion direction is Missing")
        return "", nil
    }

    log.Info("URI VRF ", ospfv2VrfName)
    log.Info("URI route distribution protocol ", distributionProtocol)
    log.Info("URI route distribution direction ", distributionDirection)

    tempkey1 := strings.Split(distributionProtocol, ":")
    if len(tempkey1) > 1 {
        distributionProtocol = tempkey1[1]
    }

    tempkey2 := strings.Split(distributionDirection, ":")
    if len(tempkey2) > 1 {
        distributionDirection = tempkey2[1]
    }
   
    var pdistributionTableKey string

    pdistributionTableKey = ospfv2VrfName + "|" + distributionProtocol + "|" + distributionDirection

    log.Info("YangToDb_ospfv2_router_distribute_route_tbl_key_xfmr: pdistributionTableKey - ", pdistributionTableKey)
    return pdistributionTableKey, nil
}


var DbToYang_ospfv2_router_distribute_route_tbl_key_xfmr KeyXfmrDbToYang = func(inParams XfmrParams) (map[string]interface{}, error) {
    res_map := make(map[string]interface{})
    entry_key := inParams.key
    log.Info("DbToYang_ospfv2_router_distribute_route_tbl_key: entry key - ", entry_key)

    distributionTableKeys := strings.Split(entry_key, "|")
    distributionProtocol:= distributionTableKeys[1]
    distributionDirection:= distributionTableKeys[2]

    res_map["protocol"] = distributionProtocol
    res_map["direction"] = distributionDirection

    log.Info("DbToYang_ospfv2_router_distribute_route_tbl_key: res_map - ", res_map)
    return res_map, nil
}

var YangToDb_ospfv2_router_distribute_route_protocol_fld_xfmr FieldXfmrYangToDb = func(inParams XfmrParams) (map[string]string, error) {

    res_map := make(map[string]string)

    res_map["NULL"] = "NULL"
    return res_map, nil
}

var DbToYang_ospfv2_router_distribute_route_protocol_fld_xfmr FieldXfmrDbtoYang = func(inParams XfmrParams) (map[string]interface{}, error) {

    var err error
    res_map := make(map[string]interface{})

    entry_key := inParams.key
    distributionTableKeys := strings.Split(entry_key, "|")
    distributionProtocol:= distributionTableKeys[1]

    res_map["protocol"] = distributionProtocol
    return res_map, err
}

var YangToDb_ospfv2_router_distribute_route_direction_fld_xfmr FieldXfmrYangToDb = func(inParams XfmrParams) (map[string]string, error) {

    res_map := make(map[string]string)

    res_map["NULL"] = "NULL"
    return res_map, nil
}

var DbToYang_ospfv2_router_distribute_route_direction_fld_xfmr FieldXfmrDbtoYang = func(inParams XfmrParams) (map[string]interface{}, error) {

    var err error
    res_map := make(map[string]interface{})

    entry_key := inParams.key
    distributionTableKeys := strings.Split(entry_key, "|")
    distributionDirection:= distributionTableKeys[2]

    res_map["direction"] = distributionDirection
    return res_map, err
}

var YangToDb_ospfv2_interface_tbl_key_xfmr KeyXfmrYangToDb = func(inParams XfmrParams) (string, error) {
    var err error
    var interfaceVrfName string

    log.Info("YangToDb_ospfv2_interface_tbl_key_xfmr: ", inParams.uri)
    pathInfo := NewPathInfo(inParams.uri)

    interfaceVrfName         = "default" //pathInfo.Var("name")
    ospfv2InterfaceName  := pathInfo.Var("name")
    ospfv2InterfaceId    := pathInfo.Var("index")

    if len(pathInfo.Vars) <  2 {
        err = errors.New("Invalid Key length");
        log.Info("Invalid Key length", len(pathInfo.Vars))
        return interfaceVrfName, err
    }

    if len(interfaceVrfName) == 0 {
        err = errors.New("vrf name is missing");
        log.Info("VRF Name is Missing")
        return "", err
    }

    if len(ospfv2InterfaceName) == 0 {
        err = errors.New("OSPF interface name is missing");
        log.Info("OSPF interface name is Missing")
        return "", err
    }

    if len(ospfv2InterfaceId) == 0 {
        err = errors.New("OSPF interface identifier missing");
        log.Info("OSPF sub-interface identifier is Missing")
        return "", err
    }

    log.Info("URI VRF ", interfaceVrfName)
    log.Info("URI interface name ", ospfv2InterfaceName)
    log.Info("URI Sub interface Id ", ospfv2InterfaceId)

    var pInterfaceTableKey string

    //pInterfaceTableKey = interfaceVrfName + "|" + ospfv2InterfaceName 
    pInterfaceTableKey = ospfv2InterfaceName

    log.Info("YangToDb_ospfv2_interface_tbl_key_xfmr: pInterfaceTableKey - ", pInterfaceTableKey)
    return pInterfaceTableKey, nil
}


var DbToYang_ospfv2_interface_tbl_key_xfmr KeyXfmrDbToYang = func(inParams XfmrParams) (map[string]interface{}, error) {
    res_map := make(map[string]interface{})
    entry_key := inParams.key
    log.Info("DbToYang_ospfv2_interface_tbl_key: entry key - ", entry_key)

    interfaceTableKeys := strings.Split(entry_key, "|")
    ospfv2InterfaceName := interfaceTableKeys[1]
    //ospfv2InterfaceId:= interfaceTableKeys[2]

    res_map["name"] = ospfv2InterfaceName
    //res_map["index"] = ospfv2InterfaceId

    log.Info("DbToYang_ospfv2_interface_tbl_key: res_map - ", res_map)
    return res_map, nil
}


func exec_vtysh_ospf_cmd (vtysh_cmd string) ([]interface{}, error) {
    var err error
    oper_err := errors.New("Operational error")

    log.Infof("Going to execute vtysh cmd ==> \"%s\"", vtysh_cmd)

    cmd := exec.Command("/usr/bin/docker", "exec", "bgp", "vtysh", "-c", vtysh_cmd)
    out_stream, err := cmd.StdoutPipe()
    if err != nil {
        log.Errorf("Can't get stdout pipe: %s\n", err)
        return nil, oper_err
    }

    err = cmd.Start()
    if err != nil {
        log.Errorf("cmd.Start() failed with %s\n", err)
        return nil, oper_err
    }

    var outputJson []interface{}
    err = json.NewDecoder(out_stream).Decode(&outputJson)
    if err != nil {
        log.Errorf("Not able to decode vtysh json output as array of objects: %s\n", err)
        return nil, oper_err
    }

    err = cmd.Wait()
    if err != nil {
        log.Errorf("Command execution completion failed with %s\n", err)
        return nil, oper_err
    }

    log.Infof("Successfully executed vtysh-cmd ==> \"%s\"", vtysh_cmd)

    if outputJson == nil {
        log.Errorf("VTYSH output empty !!!")
        return nil, oper_err
    }

    return outputJson, err
}

func ospfv2_fill_global_state (output_state map[string]interface{}, 
        ospfv2_obj *ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Ospfv2) error {
    var err error
    var ospfv2Gbl_obj *ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Ospfv2_Global
    var ospfv2GblState_obj *ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Ospfv2_Global_State
    var ospfv2GblTimersSpfState_obj *ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Ospfv2_Global_Timers_Spf_State 
    var ospfv2GblTimersLsaGenState_obj *ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Ospfv2_Global_Timers_LsaGeneration_State
    oper_err := errors.New("Operational error")
    cmn_log := "GET: xfmr for OSPF-Global State"

    ospfv2Gbl_obj = ospfv2_obj.Global
    if ospfv2Gbl_obj == nil {
        log.Errorf("%s failed !! Error: OSPFv2-Global container missing", cmn_log)
        return  oper_err
    }
    ygot.BuildEmptyTree (ospfv2Gbl_obj)

    ospfv2GblState_obj = ospfv2Gbl_obj.State
    if ospfv2GblState_obj == nil {
        log.Errorf("%s failed !! Error: Ospfv2-Global-State container missing", cmn_log)
        return oper_err
    }
    ygot.BuildEmptyTree (ospfv2GblState_obj)

    ospfv2GblTimersSpfState_obj = ospfv2Gbl_obj.Timers.Spf.State
    if ospfv2GblTimersSpfState_obj == nil {
        log.Errorf("%s failed !! Error: Ospfv2-Global-State container missing", cmn_log)
        return  oper_err
    }
    ygot.BuildEmptyTree (ospfv2GblTimersSpfState_obj)

    ospfv2GblTimersLsaGenState_obj = ospfv2Gbl_obj.Timers.LsaGeneration.State
    if ospfv2GblTimersLsaGenState_obj == nil {
        log.Errorf("%s failed !! Error: Ospfv2-Global-Timers Lsa generation State container missing", cmn_log)
        return  oper_err
    }
    ygot.BuildEmptyTree (ospfv2GblTimersLsaGenState_obj)


    if _routerId,ok := output_state["routerId"].(string); ok {
        ospfv2GblState_obj.RouterId = &_routerId
    }

    if _rfc1583Compatibility,ok := output_state["rfc1583Compatibility"].(bool); ok {
        ospfv2GblState_obj.OspfRfc1583Compatible = &_rfc1583Compatibility
    }

    if _opaqueCapable,ok := output_state["opaqueCapable"].(bool); ok {
        ospfv2GblState_obj.OpaqueLsaCapability = &_opaqueCapable
    }

    if value,ok := output_state["spfScheduleDelayMsecs"]; ok {
        _throttle_delay := uint32(value.(float64))
        ospfv2GblTimersSpfState_obj.ThrottleDelay = &_throttle_delay
    }

    if value,ok := output_state["holdtimeMinMsecs"] ; ok {
        _holdtime_minMsec := uint32(value.(float64))
        ospfv2GblTimersSpfState_obj.InitialDelay = &_holdtime_minMsec
    }
    
    if value,ok := output_state["holdtimeMaxMsecs"] ; ok {
        _holdtime_maxMsec := uint32(value.(float64))
        ospfv2GblTimersSpfState_obj.MaximumDelay = &_holdtime_maxMsec
    }

    var _spfTimerDueInMsecs uint32 = 0
    ospfv2GblTimersSpfState_obj.SpfTimerDue = &_spfTimerDueInMsecs
    if value,ok := output_state["spfTimerDueInMsecs"] ; ok {
        _spfTimerDueInMsecs = uint32(value.(float64))
        ospfv2GblTimersSpfState_obj.SpfTimerDue = &_spfTimerDueInMsecs
    }

    if value,ok := output_state["holdtimeMultplier"] ; ok {
        _holdtime_multiplier := uint32(value.(float64))
        ospfv2GblState_obj.HoldTimeMultiplier = &_holdtime_multiplier
    }

    if value,ok := output_state["spfLastExecutedMsecs"]; ok {
        _spfLastExecutedMsecs  := uint64(value.(float64))
        ospfv2GblState_obj.LastSpfExecutionTime = &_spfLastExecutedMsecs
    }

    if value,ok := output_state["spfLastDurationMsecs"] ; ok {
        _spfLastDurationMsecs   := uint32(value.(float64))
        ospfv2GblState_obj.LastSpfDuration = &_spfLastDurationMsecs
    }
    if value,ok := output_state["lsaMinIntervalMsecs"] ; ok {
        _lsaMinIntervalMsecs := uint32(value.(float64))
        ospfv2GblTimersLsaGenState_obj.LsaMinIntervalTimer = &_lsaMinIntervalMsecs
    }
    if value,ok := output_state["lsaMinArrivalMsecs"] ; ok {
        _lsaMinArrivalMsecs  := uint32(value.(float64))
        ospfv2GblTimersLsaGenState_obj.LsaMinArrivalTimer = &_lsaMinArrivalMsecs
    }
    if value,ok := output_state["refreshTimerMsecs"] ; ok {
        _refreshTimerMsecs     := uint32(value.(float64))
        ospfv2GblTimersLsaGenState_obj.RefreshTimer = &_refreshTimerMsecs
    }
    if value,ok := output_state["writeMultiplier"] ; ok {
        _write_multiplier := uint8(value.(float64))
        ospfv2GblState_obj.WriteMultiplier = &_write_multiplier
    }
    if value,ok := output_state["lsaExternalCounter"] ; ok {
        _lsaExternalCounter := uint32(value.(float64))
        ospfv2GblState_obj.ExternalLsaCount = &_lsaExternalCounter
    }
    if value,ok := output_state["lsaAsopaqueCounter"] ; ok {
        _lsaAsopaqueCounter := uint32(value.(float64))
        ospfv2GblState_obj.OpaqueLsaCount = &_lsaAsopaqueCounter
    }
    if value,ok := output_state["lsaExternalChecksum"]; ok {
        _lsaExternalChecksum := math.Float64bits(value.(float64))
        s16 := strconv.FormatUint(_lsaExternalChecksum, 16)
        ospfv2GblState_obj.ExternalLsaChecksum = &s16
    }
    if value,ok := output_state["lsaAsOpaqueChecksum"]; ok {
        _lsaAsOpaqueChecksum := math.Float64bits(value.(float64))
        s16 := strconv.FormatUint(_lsaAsOpaqueChecksum, 16)
        ospfv2GblState_obj.OpaqueLsaChecksum = &s16
    }
    if value,ok := output_state["attachedAreaCounter"] ; ok {
        _attachedAreaCounter  := uint32(value.(float64))
        ospfv2GblState_obj.AreaCount = &_attachedAreaCounter
    }
    
    return err
}


func ospfv2_fill_area_state (output_state map[string]interface{}, 
        ospfv2_obj *ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Ospfv2) error {
    var err error
    var ospfv2Areas_obj *ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Ospfv2_Areas
    var ospfv2Area_obj *ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Ospfv2_Areas_Area
    var ospfv2AreaKey ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Ospfv2_Areas_Area_Config_Identifier_Union
    var ospfv2AreaInfo_obj *ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Ospfv2_Areas_Area_State
    oper_err := errors.New("Operational error")
    cmn_log := "GET: xfmr for OSPF-Areas-Area State"

    ospfv2Areas_obj = ospfv2_obj.Areas
    if ospfv2Areas_obj == nil {
        log.Errorf("%s failed !! Error: Ospfv2 areas list missing", cmn_log)
        return  oper_err
    }
    ygot.BuildEmptyTree (ospfv2Areas_obj)

    if value, ok := output_state["areas"]; ok {
        areas_map := value.(map[string]interface {})
        for key, area := range areas_map {
            area_info := area.(map[string]interface{})
            log.Info(key)
            log.Info(area_info)
            ospfv2AreaKey, err = 
                    ospfv2Area_obj.To_OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Ospfv2_Areas_Area_Config_Identifier_Union(key) 
            if (err != nil) {
                log.Info("Failed to convert the area key")
                return  oper_err
            }
            ospfv2Area_obj, err = ospfv2Areas_obj.NewArea(ospfv2AreaKey)
            if (err != nil) {
                log.Info("Failed to create a new area")
                return  oper_err
            }
                ospfv2AreaInfo_obj = new(ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Ospfv2_Areas_Area_State)
                if ospfv2AreaInfo_obj == nil {
                    log.Errorf("%s failed !! Error: Area information missing", cmn_log)
                    return  oper_err
                }
                ospfv2Area_obj.State = ospfv2AreaInfo_obj
                ygot.BuildEmptyTree (ospfv2AreaInfo_obj)
                if _authtype,ok := area_info["authentication"].(string); ok {
                    if _authtype == "authenticationNone" {
                        ospfv2AreaInfo_obj.AuthenticationType = ocbinds.OpenconfigOspfv2Ext_OSPF_AUTHENTICATION_TYPE_AUTH_NONE
                    }
                    //TBD: To add other authentication later
                }
                
                if value,ok := area_info["areaIfTotalCounter"] ; ok {
                    _areaIfTotalCounter  := uint32(value.(float64))
                    ospfv2AreaInfo_obj.InterfaceCount = &_areaIfTotalCounter
                }
                if value,ok := area_info["areaIfActiveCounter"] ; ok {
                    _areaIfActiveCounter  := uint32(value.(float64))
                    ospfv2AreaInfo_obj.ActiveInterfaceCount = &_areaIfActiveCounter
                }
                if value,ok := area_info["nbrFullAdjacentCounter"] ; ok {
                    _nbrFullAdjacentCounter  := uint32(value.(float64))
                    ospfv2AreaInfo_obj.AdjacencyCount = &_nbrFullAdjacentCounter
                }
                
                if value,ok := area_info["spfExecutedCounter"] ; ok {
                    _spfExecutedCounter := uint32(value.(float64))
                    ospfv2AreaInfo_obj.SpfExecutionCount = &_spfExecutedCounter
                }
                
                if value,ok := area_info["lsaNumber"] ; ok {
                    _lsaNumber  := uint32(value.(float64))
                    ospfv2AreaInfo_obj.LsaCount = &_lsaNumber
                }
                if value,ok := area_info["lsaRouterNumber"]; ok {
                    _lsaRouterNumber := uint32(value.(float64))
                    ospfv2AreaInfo_obj.RouterLsaCount = &_lsaRouterNumber
                }
                if value,ok := area_info["lsaRouterChecksum"]; ok {
                    _lsaRouterChecksum  := math.Float64bits(value.(float64))
                    s16 := strconv.FormatUint(_lsaRouterChecksum, 16)
                    ospfv2AreaInfo_obj.RouterLsaChecksum = &s16
                }
                if value,ok := area_info["lsaNetworkNumber"]; ok {
                    _lsaNetworkNumber := uint32(value.(float64))
                    ospfv2AreaInfo_obj.NetworkLsaCount = &_lsaNetworkNumber
                }
                if value,ok := area_info["lsaNetworkChecksum"]; ok {
                    _lsaNetworkChecksum   := math.Float64bits(value.(float64))
                    s16 := strconv.FormatUint(_lsaNetworkChecksum, 16)
                    ospfv2AreaInfo_obj.NetworkLsaChecksum = &s16
                }
                if value,ok := area_info["lsaSummaryNumber"]; ok {
                    _lsaSummaryNumber := uint32(value.(float64))
                    ospfv2AreaInfo_obj.SummaryLsaCount = &_lsaSummaryNumber
                }
                if value,ok := area_info["lsaSummaryChecksum"]; ok {
                    _lsaSummaryChecksum  := math.Float64bits(value.(float64))
                    s16 := strconv.FormatUint(_lsaSummaryChecksum, 16)
                    ospfv2AreaInfo_obj.SummaryLsaChecksum = &s16
                }
                if value,ok := area_info["lsaAsbrNumber"]; ok {
                    _lsaAsbrNumber := uint32(value.(float64))
                    ospfv2AreaInfo_obj.AsbrSummaryLsaCount = &_lsaAsbrNumber
                }
                if value,ok := area_info["lsaAsbrChecksum"]; ok {
                    _lsaAsbrChecksum   := math.Float64bits(value.(float64))
                    s16 := strconv.FormatUint(_lsaAsbrChecksum, 16)
                    ospfv2AreaInfo_obj.AsbrSummaryLsaChecksum = &s16
                }
                if value,ok := area_info["lsaNssaNumber"]; ok {
                    _lsaNssaNumber := uint32(value.(float64))
                    ospfv2AreaInfo_obj.NssaLsaCount = &_lsaNssaNumber
                }
                if value,ok := area_info["lsaNssaChecksum"]; ok {
                    _lsaNssaChecksum  := math.Float64bits(value.(float64))
                    s16 := strconv.FormatUint(_lsaNssaChecksum, 16)
                    ospfv2AreaInfo_obj.NssaLsaChecksum = &s16
                }
                if value,ok := area_info["lsaOpaqueLinkNumber"]; ok {
                    _lsaOpaqueAreaNumber := uint32(value.(float64))
                    ospfv2AreaInfo_obj.OpaqueAreaLsaCount = &_lsaOpaqueAreaNumber
                }
                if value,ok := area_info["lsaOpaqueAreaChecksum"]; ok {
                    _lsaOpaqueAreaChecksum := math.Float64bits(value.(float64))
                    s16 := strconv.FormatUint(_lsaOpaqueAreaChecksum, 16)
                    ospfv2AreaInfo_obj.OpaqueAreaLsaChecksum = &s16
                }
            
        }
    }    
    return err
}

var DbToYang_ospfv2_state_xfmr SubTreeXfmrDbToYang = func(inParams XfmrParams) error {
    var err error
    var cmd_err error
    oper_err := errors.New("Operational error")
    cmn_log := "GET: xfmr for OSPF-Global State"
    var vtysh_cmd string

    log.Info("DbToYang_ospfv2_state_xfmr ***", inParams.uri)
    var ospfv2_obj *ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Ospfv2
    ospfv2_obj, vrfName, err := getOspfv2Root (inParams)
    if err != nil {
        log.Errorf ("%s failed !! Error:%s", cmn_log , err);
        return  oper_err
    }
    log.Info(vrfName)

    // get the values from the backend
    pathInfo := NewPathInfo(inParams.uri)

    targetUriPath, err := getYangPathFromUri(pathInfo.Path)
    log.Info(targetUriPath)
    vtysh_cmd = "show ip ospf vrf " + vrfName + " json"
    output_state, cmd_err := exec_vtysh_cmd (vtysh_cmd)
    if cmd_err != nil {
      log.Errorf("Failed to fetch ospf global state:, err=%s", cmd_err)
      return  cmd_err
    }
    
    log.Info(output_state)
    log.Info(vrfName)
    
    for key,value := range output_state {
        ospf_info := value.(map[string]interface{})
        log.Info(key)
        log.Info(ospf_info)
        err = ospfv2_fill_global_state (ospf_info, ospfv2_obj)
        err = ospfv2_fill_area_state (ospf_info, ospfv2_obj)
    }
    
    return  err;
}

func init () {

    XlateFuncBind("YangToDb_ospfv2_router_tbl_key_xfmr", YangToDb_ospfv2_router_tbl_key_xfmr)
    XlateFuncBind("DbToYang_ospfv2_router_tbl_key_xfmr", DbToYang_ospfv2_router_tbl_key_xfmr)
    XlateFuncBind("YangToDb_ospfv2_router_enable_fld_xfmr", YangToDb_ospfv2_router_enable_fld_xfmr)
    XlateFuncBind("DbToYang_ospfv2_router_enable_fld_xfmr", DbToYang_ospfv2_router_enable_fld_xfmr)

    XlateFuncBind("YangToDb_ospfv2_router_area_tbl_key_xfmr", YangToDb_ospfv2_router_area_tbl_key_xfmr)
    XlateFuncBind("DbToYang_ospfv2_router_area_tbl_key_xfmr", DbToYang_ospfv2_router_area_tbl_key_xfmr)
    XlateFuncBind("YangToDb_ospfv2_router_area_area_id_fld_xfmr", YangToDb_ospfv2_router_area_area_id_fld_xfmr)
    XlateFuncBind("DbToYang_ospfv2_router_area_area_id_fld_xfmr", DbToYang_ospfv2_router_area_area_id_fld_xfmr)

    XlateFuncBind("YangToDb_ospfv2_router_area_policy_tbl_key_xfmr", YangToDb_ospfv2_router_area_policy_tbl_key_xfmr)
    XlateFuncBind("DbToYang_ospfv2_router_area_policy_tbl_key_xfmr", DbToYang_ospfv2_router_area_policy_tbl_key_xfmr)
    XlateFuncBind("YangToDb_ospfv2_router_area_policy_src_area_fld_xfmr", YangToDb_ospfv2_router_area_policy_src_area_fld_xfmr)
    XlateFuncBind("DbToYang_ospfv2_router_area_policy_src_area_fld_xfmr", DbToYang_ospfv2_router_area_policy_src_area_fld_xfmr)

    XlateFuncBind("YangToDb_ospfv2_router_area_network_tbl_key_xfmr", YangToDb_ospfv2_router_area_network_tbl_key_xfmr)
    XlateFuncBind("DbToYang_ospfv2_router_area_network_tbl_key_xfmr", DbToYang_ospfv2_router_area_network_tbl_key_xfmr)
    XlateFuncBind("YangToDb_ospfv2_router_network_prefix_fld_xfmr", YangToDb_ospfv2_router_network_prefix_fld_xfmr)
    XlateFuncBind("DbToYang_ospfv2_router_network_prefix_fld_xfmr", DbToYang_ospfv2_router_network_prefix_fld_xfmr)

    XlateFuncBind("YangToDb_ospfv2_router_area_virtual_link_tbl_key_xfmr", YangToDb_ospfv2_router_area_virtual_link_tbl_key_xfmr)
    XlateFuncBind("DbToYang_ospfv2_router_area_virtual_link_tbl_key_xfmr", DbToYang_ospfv2_router_area_virtual_link_tbl_key_xfmr)
    XlateFuncBind("YangToDb_ospfv2_router_area_vl_remote_router_id_fld_xfmr", YangToDb_ospfv2_router_area_vl_remote_router_id_fld_xfmr)
    XlateFuncBind("DbToYang_ospfv2_router_area_vl_remote_router_id_fld_xfmr", DbToYang_ospfv2_router_area_vl_remote_router_id_fld_xfmr)

    XlateFuncBind("YangToDb_ospfv2_router_area_policy_address_range_tbl_key_xfmr", YangToDb_ospfv2_router_area_policy_address_range_tbl_key_xfmr)
    XlateFuncBind("DbToYang_ospfv2_router_area_policy_address_range_tbl_key_xfmr", DbToYang_ospfv2_router_area_policy_address_range_tbl_key_xfmr)
    XlateFuncBind("YangToDb_ospfv2_router_area_policy_address_range_prefix_fld_xfmr", YangToDb_ospfv2_router_area_policy_address_range_prefix_fld_xfmr)
    XlateFuncBind("DbToYang_ospfv2_router_area_policy_address_range_prefix_fld_xfmr", DbToYang_ospfv2_router_area_policy_address_range_prefix_fld_xfmr)

    XlateFuncBind("YangToDb_ospfv2_router_distribute_route_tbl_key_xfmr", YangToDb_ospfv2_router_distribute_route_tbl_key_xfmr)
    XlateFuncBind("DbToYang_ospfv2_router_distribute_route_tbl_key_xfmr", DbToYang_ospfv2_router_distribute_route_tbl_key_xfmr)
    XlateFuncBind("YangToDb_ospfv2_router_distribute_route_protocol_fld_xfmr", YangToDb_ospfv2_router_distribute_route_protocol_fld_xfmr)
    XlateFuncBind("DbToYang_ospfv2_router_distribute_route_protocol_fld_xfmr", DbToYang_ospfv2_router_distribute_route_protocol_fld_xfmr)

    XlateFuncBind("YangToDb_ospfv2_interface_tbl_key_xfmr", YangToDb_ospfv2_interface_tbl_key_xfmr)
    XlateFuncBind("DbToYang_ospfv2_interface_tbl_key_xfmr", DbToYang_ospfv2_interface_tbl_key_xfmr)
    XlateFuncBind("DbToYang_ospfv2_state_xfmr", DbToYang_ospfv2_state_xfmr)
}




