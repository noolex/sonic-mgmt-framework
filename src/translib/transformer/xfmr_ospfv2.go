
package transformer

import (
    "errors"
//    "strconv"
    "strings"
//    "encoding/json"
    "translib/ocbinds"
    "translib/tlerr"
    "translib/db"
//    "io"
//    "bytes"
//    "net"
//   "encoding/binary"
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
        return nil, "", errors.New("OSPF ID is missing")
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

    if inParams.oper == DELETE && ospfv2VrfName == "default" {
        xpath, _ := XfmrRemoveXPATHPredicates(inParams.requestUri)
        switch xpath {
            case "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/ospfv2": fallthrough
            case "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/ospfv2/global": fallthrough
            case "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/ospfv2/global/config":
                 log.Info ("DELELE op for ospfv2VrfName: ", ospfv2VrfName, " XPATH: ", xpath)
                 ospfv2GblTblTs := &db.TableSpec{Name: "OSPFV2_ROUTER"}
                 if ospfv2GblTblKeys, err := inParams.d.GetKeys(ospfv2GblTblTs) ; err == nil {
                     for _, key := range ospfv2GblTblKeys {
                         /* If "default" VRF is present in keys-list & still list-len is greater than 1,
                          * then don't allow "default" VRF ospfv2-instance delete.
                          * "default" VRF ospfv2-instance should be deleted, only after all non-default VRF instances are deleted from the system */
                         if key.Get(0) == ospfv2VrfName && len(ospfv2GblTblKeys) > 1 {
                             return "", tlerr.NotSupported("Delete not allowed, since non-default-VRF ospfv2-instance present in system")
                         }
                     }
                 }
        }
    }

    log.Info("YangToDb_ospfv2_router_tbl_key_xfmr returned Key: ", ospfv2VrfName)
    return ospfv2VrfName, err
}

var DbToYang_ospfv2_router_tbl_key_xfmr KeyXfmrDbToYang = func(inParams XfmrParams) (map[string]interface{}, error) {
    rmap := make(map[string]interface{})
    var err error
    entry_key := inParams.key
    log.Info("DbToYang_bgp_gbl_tbl_key: ", entry_key)

    rmap["name"] = entry_key

    log.Info("DbToYang_ospfv2_router_tbl_key_xfmr key: ", rmap)
    return rmap, err
}

func init () {
    XlateFuncBind("YangToDb_ospfv2_router_tbl_key_xfmr", YangToDb_ospfv2_router_tbl_key_xfmr)
    XlateFuncBind("DbToYang_ospfv2_router_tbl_key_xfmr", DbToYang_ospfv2_router_tbl_key_xfmr)
}


