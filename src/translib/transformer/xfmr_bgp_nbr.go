package transformer

import (
    "errors"
    "strings"
    "translib/ocbinds"
    "translib/db"
    "strconv"
    "github.com/openconfig/ygot/ygot"
    log "github.com/golang/glog"
    "net"
)

func init () {
    XlateFuncBind("bgp_nbr_tbl_xfmr", bgp_nbr_tbl_xfmr)
    XlateFuncBind("YangToDb_bgp_nbr_tbl_key_xfmr", YangToDb_bgp_nbr_tbl_key_xfmr)
    XlateFuncBind("DbToYang_bgp_nbr_tbl_key_xfmr", DbToYang_bgp_nbr_tbl_key_xfmr)
    XlateFuncBind("YangToDb_bgp_nbr_address_fld_xfmr", YangToDb_bgp_nbr_address_fld_xfmr)
    XlateFuncBind("DbToYang_bgp_nbr_address_fld_xfmr", DbToYang_bgp_nbr_address_fld_xfmr)
    XlateFuncBind("YangToDb_bgp_nbr_peer_type_fld_xfmr", YangToDb_bgp_nbr_peer_type_fld_xfmr)
    XlateFuncBind("DbToYang_bgp_nbr_peer_type_fld_xfmr", DbToYang_bgp_nbr_peer_type_fld_xfmr)
    XlateFuncBind("YangToDb_bgp_af_nbr_tbl_key_xfmr", YangToDb_bgp_af_nbr_tbl_key_xfmr)
    XlateFuncBind("DbToYang_bgp_af_nbr_tbl_key_xfmr", DbToYang_bgp_af_nbr_tbl_key_xfmr)
    XlateFuncBind("YangToDb_bgp_nbr_afi_safi_name_fld_xfmr", YangToDb_bgp_nbr_afi_safi_name_fld_xfmr)
    XlateFuncBind("DbToYang_bgp_nbr_afi_safi_name_fld_xfmr", DbToYang_bgp_nbr_afi_safi_name_fld_xfmr)
    XlateFuncBind("YangToDb_bgp_af_nbr_proto_tbl_key_xfmr", YangToDb_bgp_af_nbr_proto_tbl_key_xfmr)
    XlateFuncBind("DbToYang_bgp_af_nbr_proto_tbl_key_xfmr", DbToYang_bgp_af_nbr_proto_tbl_key_xfmr)
    XlateFuncBind("DbToYang_bgp_nbrs_nbr_state_xfmr", DbToYang_bgp_nbrs_nbr_state_xfmr)
    XlateFuncBind("DbToYang_bgp_nbrs_nbr_af_state_xfmr", DbToYang_bgp_nbrs_nbr_af_state_xfmr)
    XlateFuncBind("YangToDb_bgp_nbr_community_type_fld_xfmr", YangToDb_bgp_nbr_community_type_fld_xfmr)
    XlateFuncBind("DbToYang_bgp_nbr_community_type_fld_xfmr", DbToYang_bgp_nbr_community_type_fld_xfmr)
    XlateFuncBind("YangToDb_bgp_nbr_orf_type_fld_xfmr", YangToDb_bgp_nbr_orf_type_fld_xfmr)
    XlateFuncBind("DbToYang_bgp_nbr_orf_type_fld_xfmr", DbToYang_bgp_nbr_orf_type_fld_xfmr)
    XlateFuncBind("YangToDb_bgp_nbr_tx_add_paths_fld_xfmr", YangToDb_bgp_nbr_tx_add_paths_fld_xfmr)
    XlateFuncBind("DbToYang_bgp_nbr_tx_add_paths_fld_xfmr", DbToYang_bgp_nbr_tx_add_paths_fld_xfmr)
    XlateFuncBind("YangToDb_bgp_nbrs_nbr_auth_password_xfmr", YangToDb_bgp_nbrs_nbr_auth_password_xfmr)
    XlateFuncBind("DbToYang_bgp_nbrs_nbr_auth_password_xfmr", DbToYang_bgp_nbrs_nbr_auth_password_xfmr)
}

var bgp_nbr_tbl_xfmr TableXfmrFunc = func (inParams XfmrParams)  ([]string, error) {
    var tblList []string
    var err error
    var vrf string
    var key string

    log.Info("bgp_nbr_tbl_xfmr: ", inParams.uri)
    pathInfo := NewPathInfo(inParams.uri)

    vrf = pathInfo.Var("name")
    bgpId      := pathInfo.Var("identifier")
    protoName  := pathInfo.Var("name#2")
    pNbrAddr   := pathInfo.Var("neighbor-address")

    if len(pathInfo.Vars) <  3 {
        err = errors.New("Invalid Key length");
        log.Info("Invalid Key length", len(pathInfo.Vars))
        return tblList, err
    }

    if len(vrf) == 0 {
        err = errors.New("vrf name is missing");
        log.Info("VRF Name is Missing")
        return tblList, err
    }
    if strings.Contains(bgpId,"BGP") == false {
        err = errors.New("BGP ID is missing");
        log.Info("BGP ID is missing")
        return tblList, err
    }
    if len(protoName) == 0 {
        err = errors.New("Protocol Name is missing");
        log.Info("Protocol Name is Missing")
        return tblList, err
    }

    if (inParams.oper != GET) {
        tblList = append(tblList, "BGP_NEIGHBOR")
        return tblList, nil
    }

    tblList = append(tblList, "BGP_NEIGHBOR")
    if len(pNbrAddr) != 0 {
        key = vrf + "|" + pNbrAddr
        log.Info("bgp_nbr_tbl_xfmr: key - ", key)
        if (inParams.dbDataMap != nil) {
            if _, ok := (*inParams.dbDataMap)[db.ConfigDB]["BGP_NEIGHBOR"]; !ok {
                (*inParams.dbDataMap)[db.ConfigDB]["BGP_NEIGHBOR"] = make(map[string]db.Value)
            }

            nbrCfgTblTs := &db.TableSpec{Name: "BGP_NEIGHBOR"}
            nbrEntryKey := db.Key{Comp: []string{vrf, pNbrAddr}}

            if _, ok := (*inParams.dbDataMap)[db.ConfigDB]["BGP_NEIGHBOR"][key]; !ok {
                var entryValue db.Value
                if entryValue, err = inParams.d.GetEntry(nbrCfgTblTs, nbrEntryKey) ; err == nil {
                    (*inParams.dbDataMap)[db.ConfigDB]["BGP_NEIGHBOR"][key] = entryValue
                }
            }
        }
    } else {
        if(inParams.dbDataMap != nil) {
            err = errors.New("Opertational error")
            nbrKeys, _ := inParams.d.GetKeys(&db.TableSpec{Name:"BGP_NEIGHBOR"})
            if len(nbrKeys) > 0 {
                if _, ok := (*inParams.dbDataMap)[db.ConfigDB]["BGP_NEIGHBOR"]; !ok {
                    (*inParams.dbDataMap)[db.ConfigDB]["BGP_NEIGHBOR"] = make(map[string]db.Value)
                }
                for _, nkey := range nbrKeys {
                    if nkey.Get(0) != vrf {
                        continue
                    }

                    key = nkey.Get(0) + "|" + nkey.Get(1)
                    log.Info("bgp_nbr_tbl_xfmr: Static Neighbor key - ", key)
                    nbrCfgTblTs := &db.TableSpec{Name: "BGP_NEIGHBOR"}
                    nbrEntryKey := db.Key{Comp: []string{nkey.Get(0), nkey.Get(1)}}

                    if _, ok := (*inParams.dbDataMap)[db.ConfigDB]["BGP_NEIGHBOR"][key]; !ok {
                        var entryValue db.Value
                        if entryValue, err = inParams.d.GetEntry(nbrCfgTblTs, nbrEntryKey) ; err == nil {
                            (*inParams.dbDataMap)[db.ConfigDB]["BGP_NEIGHBOR"][key] = entryValue
                        }
                    }
                }
            }

            cmd := "show ip bgp vrf" + " " + vrf + " " + "ipv4 summary json"
            bgpNeighOutputJson, _:= exec_vtysh_cmd (cmd)

            if _, ok := bgpNeighOutputJson["warning"] ; !ok {
                ipv4Unicast, ok := bgpNeighOutputJson["ipv4Unicast"].(map[string]interface{})
                if ok {
                    peers, ok := ipv4Unicast["peers"].(map[string]interface{})
                    if ok {
                        if _, ok := (*inParams.dbDataMap)[db.ConfigDB]["BGP_NEIGHBOR"]; !ok {
                            (*inParams.dbDataMap)[db.ConfigDB]["BGP_NEIGHBOR"] = make(map[string]db.Value)
                        }

                        for peer, _peerData := range peers {
                            peerData := _peerData.(map[string]interface {})
                            if value, ok := peerData["dynamicPeer"].(bool) ; ok {
                                if (value == false) {
                                    continue
                                }
                            } else {
                                continue;
                            }

                            key = vrf + "|" + peer
                            log.Info("bgp_nbr_tbl_xfmr: Dynamic ipv4 neighbor key - ", key)
                            if _, ok := (*inParams.dbDataMap)[db.ConfigDB]["BGP_NEIGHBOR"][key]; !ok {
                                (*inParams.dbDataMap)[db.ConfigDB]["BGP_NEIGHBOR"][key] = db.Value{Field: make(map[string]string)}
                            }
                        }
                    }
                }
            }
            cmd = "show ip bgp vrf" + " " + vrf + " " + "ipv6 summary json"
            bgpNeighOutputJson, _= exec_vtysh_cmd (cmd)

            if _, ok := bgpNeighOutputJson["warning"] ; !ok {
                ipv6Unicast, ok := bgpNeighOutputJson["ipv6Unicast"].(map[string]interface{})
                if ok {
                    peers, ok := ipv6Unicast["peers"].(map[string]interface{})
                    if ok {
                        if _, ok := (*inParams.dbDataMap)[db.ConfigDB]["BGP_NEIGHBOR"]; !ok {
                            (*inParams.dbDataMap)[db.ConfigDB]["BGP_NEIGHBOR"] = make(map[string]db.Value)
                        }

                        for peer, _peerData := range peers {
                            peerData := _peerData.(map[string]interface {})
                            if value, ok := peerData["dynamicPeer"].(bool) ; ok {
                                if (value == false) {
                                   continue
                                }
                            } else {
                               continue;
                            }

                            key = vrf + "|" + peer
                            log.Info("bgp_nbr_tbl_xfmr: Dynamic ipv6 neighbor key - ", key)
                            if _, ok := (*inParams.dbDataMap)[db.ConfigDB]["BGP_NEIGHBOR"][key]; !ok {
                                (*inParams.dbDataMap)[db.ConfigDB]["BGP_NEIGHBOR"][key] = db.Value{Field: make(map[string]string)}
                            }
                        }
                    }
                }
            }
        }
    }
    return tblList, nil
}

var YangToDb_bgp_nbr_tbl_key_xfmr KeyXfmrYangToDb = func(inParams XfmrParams) (string, error) {
    var err error
    var vrfName string

    log.Info("YangToDb_bgp_nbr_tbl_key_xfmr: ", inParams.uri)
    pathInfo := NewPathInfo(inParams.uri)

    /* Key should contain, <vrf name, protocol name, neighbor name> */

    vrfName    =  pathInfo.Var("name")
    bgpId      := pathInfo.Var("identifier")
    protoName  := pathInfo.Var("name#2")
    pNbrAddr   := pathInfo.Var("neighbor-address")

    if len(pathInfo.Vars) <  3 {
        err = errors.New("Invalid Key length");
        log.Info("Invalid Key length", len(pathInfo.Vars))
        return vrfName, err
    }

    if len(vrfName) == 0 {
        err = errors.New("vrf name is missing");
        log.Info("VRF Name is Missing")
        return "", err
    }
    if strings.Contains(bgpId,"BGP") == false {
        err = errors.New("BGP ID is missing");
        log.Info("BGP ID is missing")
        return "", err
    }
    if len(protoName) == 0 {
        err = errors.New("Protocol Name is missing");
        log.Info("Protocol Name is Missing")
        return "", err
    }
    if len(pNbrAddr) == 0 {
        err = errors.New("Neighbor address is missing")
        log.Info("Neighbor address is Missing")
        return "", nil
    }

    log.Info("URI VRF", vrfName)
    log.Info("URI Neighbor address", pNbrAddr)

    var pNbrKey string

    pNbrKey = vrfName + "|" + pNbrAddr

    log.Info("YangToDb_bgp_nbr_tbl_key_xfmr: pNbrKey:", pNbrKey)
    return pNbrKey, nil
}

var DbToYang_bgp_nbr_tbl_key_xfmr KeyXfmrDbToYang = func(inParams XfmrParams) (map[string]interface{}, error) {
    rmap := make(map[string]interface{})
    entry_key := inParams.key
    log.Info("DbToYang_bgp_nbr_tbl_key: ", entry_key)

    nbrKey := strings.Split(entry_key, "|")
    if len(nbrKey) < 2 {return rmap, nil}

    nbrName:= nbrKey[1]

    rmap["neighbor-address"] = nbrName

    return rmap, nil
}

var YangToDb_bgp_nbr_peer_type_fld_xfmr FieldXfmrYangToDb = func(inParams XfmrParams) (map[string]string, error) {
    res_map := make(map[string]string)

    var err error
    if inParams.param == nil {
        err = errors.New("No Params");
        return res_map, err
    }

    if inParams.oper == DELETE {
        res_map["peer_type"] = ""
        return res_map, nil
    }

    peer_type, _ := inParams.param.(ocbinds.E_OpenconfigBgp_PeerType)
    log.Info("YangToDb_bgp_nbr_peer_type_fld_xfmr: ", inParams.ygRoot, " Xpath: ", inParams.uri, " peer-type: ", peer_type)

    if (peer_type == ocbinds.OpenconfigBgp_PeerType_INTERNAL) {
        res_map["peer_type"] = "internal"
    }  else if (peer_type == ocbinds.OpenconfigBgp_PeerType_EXTERNAL) {
        res_map["peer_type"] = "external"
    } else {
        err = errors.New("Peer Type Missing");
        return res_map, err
    }

    return res_map, nil

}

var DbToYang_bgp_nbr_peer_type_fld_xfmr FieldXfmrDbtoYang = func(inParams XfmrParams) (map[string]interface{}, error) {
    result := make(map[string]interface{})

    data := (*inParams.dbDataMap)[inParams.curDb]
    log.Info("DbToYang_bgp_nbr_peer_type_fld_xfmr : ", data, "inParams : ", inParams)

    pTbl := data["BGP_NEIGHBOR"]
    if _, ok := pTbl[inParams.key]; !ok {
        log.Info("DbToYang_bgp_nbr_peer_type_fld_xfmr BGP neighbor not found : ", inParams.key)
        return result, errors.New("BGP neighbor not found : " + inParams.key)
    }
    pGrpKey := pTbl[inParams.key]
    peer_type, ok := pGrpKey.Field["peer_type"]

    if ok {
        if (peer_type == "internal") {
            result["peer-type"] = "INTERNAL"
        } else if (peer_type == "external") {
            result["peer-type"] = "EXTERNAL"
        }
    } else {
        log.Info("peer_type field not found in DB")
    }
    return result, nil
}

var YangToDb_bgp_nbr_tx_add_paths_fld_xfmr FieldXfmrYangToDb = func(inParams XfmrParams) (map[string]string, error) {
    res_map := make(map[string]string)

    var err error
    if inParams.param == nil {
        err = errors.New("No Params");
        return res_map, err
    }

    if inParams.oper == DELETE {
        res_map["tx_add_paths"] = ""
        return res_map, nil
    }

    tx_add_paths_type, _ := inParams.param.(ocbinds.E_OpenconfigBgpExt_TxAddPathsType)
    log.Info("YangToDb_bgp_nbr_tx_add_paths_fld_xfmr: ", inParams.ygRoot, " Xpath: ", inParams.uri, " add-paths-type: ", tx_add_paths_type)

    if (tx_add_paths_type == ocbinds.OpenconfigBgpExt_TxAddPathsType_TX_ALL_PATHS) {
        res_map["tx_add_paths"] = "tx_all_paths"
    }  else if (tx_add_paths_type == ocbinds.OpenconfigBgpExt_TxAddPathsType_TX_BEST_PATH_PER_AS) {
        res_map["tx_add_paths"] = "tx_best_path_per_as"
    } else {
        err = errors.New("Invalid add Paths type Missing");
        return res_map, err
    }

    return res_map, err

}

var DbToYang_bgp_nbr_tx_add_paths_fld_xfmr FieldXfmrDbtoYang = func(inParams XfmrParams) (map[string]interface{}, error) {

    var err error
    result := make(map[string]interface{})

    data := (*inParams.dbDataMap)[inParams.curDb]
    log.Info("DbToYang_bgp_nbr_tx_add_paths_fld_xfmr: ", data, "inParams : ", inParams)

    pTbl := data["BGP_NEIGHBOR_AF"]
    if _, ok := pTbl[inParams.key]; !ok {
        log.Info("DbToYang_bgp_nbr_tx_add_paths_fld_xfmr BGP neighbor not found : ", inParams.key)
        return result, errors.New("BGP neighbor not found : " + inParams.key)
    }
    pNbrKey := pTbl[inParams.key]
    tx_add_paths_type, ok := pNbrKey.Field["tx_add_paths"]

    if ok {
        if (tx_add_paths_type == "tx_all_paths") {
            result["tx-add-paths"] = "TX_ALL_PATHS"
        } else if (tx_add_paths_type == "tx_best_path_per_as") {
            result["tx-add-paths"] = "TX_BEST_PATH_PER_AS"
        }
    } else {
        log.Info("Tx add Paths field not found in DB")
    }
    return result, err
}

var YangToDb_bgp_nbr_address_fld_xfmr FieldXfmrYangToDb = func(inParams XfmrParams) (map[string]string, error) {
    res_map := make(map[string]string)

    res_map["NULL"] = "NULL"
    return res_map, nil
}

var DbToYang_bgp_nbr_address_fld_xfmr FieldXfmrDbtoYang = func(inParams XfmrParams) (map[string]interface{}, error) {

    var err error
    result := make(map[string]interface{})

    entry_key := inParams.key
    nbrAddrKey := strings.Split(entry_key, "|")
    if len(nbrAddrKey) < 2 {return result, nil}

    nbrAddr:= nbrAddrKey[1]

    result["neighbor-address"] = nbrAddr

    return result, err
}

var YangToDb_bgp_nbr_afi_safi_name_fld_xfmr FieldXfmrYangToDb = func(inParams XfmrParams) (map[string]string, error) {
    res_map := make(map[string]string)

    res_map["NULL"] = "NULL"
    return res_map, nil
}

var DbToYang_bgp_nbr_afi_safi_name_fld_xfmr FieldXfmrDbtoYang = func(inParams XfmrParams) (map[string]interface{}, error) {

    var err error
    var nbrAfName string
    result := make(map[string]interface{})

    entry_key := inParams.key
    nbrAfKey := strings.Split(entry_key, "|")
    if len(nbrAfKey) < 3 {return result, nil}

    switch nbrAfKey[2] {
        case "ipv4_unicast":
            nbrAfName = "IPV4_UNICAST"
        case "ipv6_unicast":
            nbrAfName = "IPV6_UNICAST"
        case "l2vpn_evpn":
            nbrAfName = "L2VPN_EVPN"
       default:
            return result, nil
    }
    result["afi-safi-name"] = nbrAfName

    return result, err
}


var YangToDb_bgp_af_nbr_tbl_key_xfmr KeyXfmrYangToDb = func(inParams XfmrParams) (string, error) {
    var err error
    var vrfName string

    log.Info("YangToDb_bgp_af_nbr_tbl_key_xfmr ***", inParams.uri)
    pathInfo := NewPathInfo(inParams.uri)

    /* Key should contain, <vrf name, protocol name, neighbor name> */

    vrfName    =  pathInfo.Var("name")
    bgpId      := pathInfo.Var("identifier")
    protoName  := pathInfo.Var("name#2")
    pNbr   := pathInfo.Var("neighbor-address")
    afName     := pathInfo.Var("afi-safi-name")

    if len(pathInfo.Vars) <  4 {
        err = errors.New("Invalid Key length");
        log.Info("Invalid Key length", len(pathInfo.Vars))
        return vrfName, err
    }

    if len(vrfName) == 0 {
        err = errors.New("vrf name is missing");
        log.Info("VRF Name is Missing")
        return vrfName, err
    }
    if strings.Contains(bgpId,"BGP") == false {
        err = errors.New("BGP ID is missing");
        log.Info("BGP ID is missing")
        return bgpId, err
    }
    if len(protoName) == 0 {
        err = errors.New("Protocol Name is missing");
        log.Info("Protocol Name is Missing")
        return protoName, err
    }
    if len(pNbr) == 0 {
        err = errors.New("Neighbor is missing")
        log.Info("Neighbor is Missing")
        return pNbr, err
    }

    if len(afName) == 0 {
        err = errors.New("AFI SAFI is missing")
        log.Info("AFI SAFI is Missing")
        return afName, err
    }

    if strings.Contains(afName, "IPV4_UNICAST") {
        afName = "ipv4_unicast"
    } else if strings.Contains(afName, "IPV6_UNICAST") {
        afName = "ipv6_unicast"
    } else if strings.Contains(afName, "L2VPN_EVPN") {
        afName = "l2vpn_evpn"
    } else  {
	err = errors.New("Unsupported AFI SAFI")
	log.Info("Unsupported AFI SAFI ", afName);
	return afName, err
    }

    log.Info("URI VRF ", vrfName)
    log.Info("URI Nbr ", pNbr)
    log.Info("URI AFI SAFI ", afName)

    var nbrAfKey string

    nbrAfKey = vrfName + "|" + pNbr + "|" + afName

    log.Info("YangToDb_bgp_af_nbr_tbl_key_xfmr: afPgrpKey:", nbrAfKey)
    return nbrAfKey, nil
}

var DbToYang_bgp_af_nbr_tbl_key_xfmr KeyXfmrDbToYang = func(inParams XfmrParams) (map[string]interface{}, error) {
    var afName string
    rmap := make(map[string]interface{})
    entry_key := inParams.key
    log.Info("DbToYang_bgp_af_nbr_tbl_key: ", entry_key)

    nbrAfKey := strings.Split(entry_key, "|")
    if len(nbrAfKey) < 3 {return rmap, nil}

    switch nbrAfKey[2] {
        case "ipv4_unicast":
            afName = "IPV4_UNICAST"
        case "ipv6_unicast":
            afName = "IPV6_UNICAST"
        case "l2vpn_evpn":
            afName = "L2VPN_EVPN"
       default:
            return rmap, nil
    }

    rmap["afi-safi-name"]   = afName

    return rmap, nil
}

var YangToDb_bgp_af_nbr_proto_tbl_key_xfmr KeyXfmrYangToDb = func(inParams XfmrParams) (string, error) {
    var err error
    var vrfName string

    log.Info("YangToDb_bgp_af_nbr_proto_tbl_key_xfmr***", inParams.uri)
    pathInfo := NewPathInfo(inParams.uri)

    vrfName    =  pathInfo.Var("name")
    bgpId      := pathInfo.Var("identifier")
    protoName  := pathInfo.Var("name#2")
    pNbr   := pathInfo.Var("neighbor-address")
    afName     := pathInfo.Var("afi-safi-name")

    if len(pathInfo.Vars) <  4 {
        err = errors.New("Invalid Key length");
        log.Info("Invalid Key length", len(pathInfo.Vars))
        return vrfName, err
    }

    if len(vrfName) == 0 {
        err = errors.New("vrf name is missing");
        log.Info("VRF Name is Missing")
        return vrfName, err
    }
    if strings.Contains(bgpId,"BGP") == false {
        err = errors.New("BGP ID is missing");
        log.Info("BGP ID is missing")
        return bgpId, err
    }
    if len(protoName) == 0 {
        err = errors.New("Protocol Name is missing");
        log.Info("Protocol Name is Missing")
        return protoName, err
    }
    if len(pNbr) == 0 {
        err = errors.New("Neighbor missing")
        log.Info("Neighbo Missing")
        return pNbr, err
    }

    if len(afName) == 0 {
        err = errors.New("AFI SAFI is missing")
        log.Info("AFI SAFI is Missing")
        return afName, err
    }

    if strings.Contains(afName, "IPV4_UNICAST") {
        afName = "ipv4_unicast"
        if strings.Contains(inParams.uri, "ipv6-unicast") ||
           strings.Contains(inParams.uri, "l2vpn-evpn") {
		err = errors.New("IPV4_UNICAST supported only on ipv4-config container")
		log.Info("IPV4_UNICAST supported only on ipv4-config container: ", afName);
		return afName, err
        }
    } else if strings.Contains(afName, "IPV6_UNICAST") {
        afName = "ipv6_unicast"
        if strings.Contains(inParams.uri, "ipv4-unicast") ||
           strings.Contains(inParams.uri, "l2vpn-evpn") {
		err = errors.New("IPV6_UNICAST supported only on ipv6-config container")
		log.Info("IPV6_UNICAST supported only on ipv6-config container: ", afName);
		return afName, err
        }
    } else if strings.Contains(afName, "L2VPN_EVPN") {
        afName = "l2vpn_evpn"
        if strings.Contains(inParams.uri, "ipv6-unicast") ||
           strings.Contains(inParams.uri, "ipv4-unicast") {
		err = errors.New("L2VPN_EVPN supported only on l2vpn-evpn container")
		log.Info("L2VPN_EVPN supported only on l2vpn-evpn container: ", afName);
		return afName, err
        }
    } else  {
	err = errors.New("Unsupported AFI SAFI")
	log.Info("Unsupported AFI SAFI ", afName);
	return afName, err
    }

    log.Info("URI VRF ", vrfName)
    log.Info("URI Nbr ", pNbr)
    log.Info("URI AFI SAFI ", afName)

    var nbrAfKey string

  nbrAfKey = vrfName + "|" + pNbr + "|" + afName

    log.Info("YangToDb_bgp_af_nbr_proto_tbl_key_xfmr: nbrAfKey:", nbrAfKey)
    return nbrAfKey, nil
}

var DbToYang_bgp_af_nbr_proto_tbl_key_xfmr KeyXfmrDbToYang = func(inParams XfmrParams) (map[string]interface{}, error) {
   var afName string
    rmap := make(map[string]interface{})
    entry_key := inParams.key
    log.Info("DbToYang_bgp_af_nbr_proto_tbl_key_xfmr: ", entry_key)

    nbrAfKey := strings.Split(entry_key, "|")
    if len(nbrAfKey) < 3 {return rmap, nil}

    switch nbrAfKey[2] {
        case "ipv4_unicast":
            afName = "IPV4_UNICAST"
        case "ipv6_unicast":
            afName = "IPV6_UNICAST"
        case "l2vpn_evpn":
            afName = "L2VPN_EVPN"
       default:
            return rmap, nil
    }

    rmap["afi-safi-name"]   = afName

    return rmap, nil
}

type _xfmr_bgp_nbr_state_key struct {
    niName string
    nbrAddr string
}

func get_spec_nbr_cfg_tbl_entry (cfgDb *db.DB, nbr_key *_xfmr_bgp_nbr_state_key) (map[string]string, error) {
    var err error

    nbrCfgTblTs := &db.TableSpec{Name: "BGP_NEIGHBOR"}
    nbrEntryKey := db.Key{Comp: []string{nbr_key.niName, nbr_key.nbrAddr}}

    var entryValue db.Value
    if entryValue, err = cfgDb.GetEntry(nbrCfgTblTs, nbrEntryKey) ; err != nil {
        return nil, err
    }

    return entryValue.Field, err
}

func fill_nbr_state_cmn_info (nbr_key *_xfmr_bgp_nbr_state_key, frrNbrDataValue interface{}, cfgDb *db.DB,
                              nbr_obj *ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Bgp_Neighbors_Neighbor) error {
    var err error
    nbrState := nbr_obj.State
    nbrState.NeighborAddress = &nbr_key.nbrAddr

    if frrNbrDataValue != nil {
        frrNbrDataJson := frrNbrDataValue.(map[string]interface{})

        if value, ok := frrNbrDataJson["bgpState"] ; ok {
            switch value {
            case "Idle":
                nbrState.SessionState = ocbinds.OpenconfigBgp_Bgp_Neighbors_Neighbor_State_SessionState_IDLE
            case "Connect":
                nbrState.SessionState = ocbinds.OpenconfigBgp_Bgp_Neighbors_Neighbor_State_SessionState_CONNECT
            case "Active":
                nbrState.SessionState = ocbinds.OpenconfigBgp_Bgp_Neighbors_Neighbor_State_SessionState_ACTIVE
            case "OpenSent":
                nbrState.SessionState = ocbinds.OpenconfigBgp_Bgp_Neighbors_Neighbor_State_SessionState_OPENSENT
            case "OpenConfirm":
                nbrState.SessionState = ocbinds.OpenconfigBgp_Bgp_Neighbors_Neighbor_State_SessionState_OPENCONFIRM
            case "Established":
                nbrState.SessionState = ocbinds.OpenconfigBgp_Bgp_Neighbors_Neighbor_State_SessionState_ESTABLISHED
            }
        }

        if value, ok := frrNbrDataJson["adminShutDown"] ; (ok && (value == true)) {
            _enabled, _ := strconv.ParseBool("false")
            nbrState.Enabled = &_enabled
        } else {
            _enabled, _ := strconv.ParseBool("true")
            nbrState.Enabled = &_enabled
        }

        if value, ok := frrNbrDataJson["localAs"] ; ok {
            _localAs := uint32(value.(float64))
            nbrState.LocalAs = &_localAs
        }

        if value, ok := frrNbrDataJson["remoteAs"] ; ok {
            _peerAs := uint32(value.(float64))
            nbrState.PeerAs = &_peerAs
        }

        if value, ok := frrNbrDataJson["portForeign"] ; ok {
            _peerPort := uint16(value.(float64))
            nbrState.PeerPort = &_peerPort
        }

        if value, ok := frrNbrDataJson["bgpTimerUpEstablishedEpoch"] ; ok {
            _lastEstablished := uint64(value.(float64))
            nbrState.LastEstablished = &_lastEstablished
        }

        if routerId, ok := frrNbrDataJson["remoteRouterId"] ; ok {
            _routerId := routerId.(string)
            nbrState.RemoteRouterId = &_routerId
        }

        if value, ok := frrNbrDataJson["connectionsEstablished"] ; ok {
            _establishedTransitions := uint64(value.(float64))
            nbrState.EstablishedTransitions = &_establishedTransitions
        }

        if value, ok := frrNbrDataJson["connectionsDropped"] ; ok {
            _connectionsDropped := uint64(value.(float64))
            nbrState.ConnectionsDropped = &_connectionsDropped
        }

        if value, ok := frrNbrDataJson["lastResetTimerMsecs"] ; ok {
            _lastResetTimerSec := uint64(value.(float64))/1000
            nbrState.LastResetTime = &_lastResetTimerSec
        }

        if resetReason, ok := frrNbrDataJson["lastResetDueTo"] ; ok {
            _resetReason := resetReason.(string)
            nbrState.LastResetReason = &_resetReason
        }

        if value, ok := frrNbrDataJson["bgpTimerLastRead"] ; ok {
            _lastRead := uint64(value.(float64))/1000
            nbrState.LastRead = &_lastRead
        }

        if value, ok := frrNbrDataJson["bgpTimerLastWrite"] ; ok {
            _lastWrite := uint64(value.(float64))/1000
            nbrState.LastWrite = &_lastWrite
        }

        if statsMap, ok := frrNbrDataJson["messageStats"].(map[string]interface{}) ; ok {
            var _rcvd_msgs ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Bgp_Neighbors_Neighbor_State_Messages_Received
            var _sent_msgs ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Bgp_Neighbors_Neighbor_State_Messages_Sent
            var _msgs ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Bgp_Neighbors_Neighbor_State_Messages
            var _queues ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Bgp_Neighbors_Neighbor_State_Queues
            _msgs.Received = &_rcvd_msgs
            _msgs.Sent = &_sent_msgs
            nbrState.Messages = &_msgs
            nbrState.Queues = &_queues

            if value, ok := statsMap["capabilityRecv"] ; ok {
                _capability_rcvd := uint64(value.(float64))
                _rcvd_msgs.CAPABILITY = &_capability_rcvd
            }
            if value, ok := statsMap["keepalivesRecv"] ; ok {
                _keepalive_rcvd := uint64(value.(float64))
                _rcvd_msgs.KEEPALIVE = &_keepalive_rcvd
            }
            if value, ok := statsMap["notificationsRecv"] ; ok {
                _notification_rcvd := uint64(value.(float64))
                _rcvd_msgs.NOTIFICATION = &_notification_rcvd
            }
            if value, ok := statsMap["opensRecv"] ; ok {
                _open_rcvd := uint64(value.(float64))
                _rcvd_msgs.OPEN = &_open_rcvd
            }
            if value, ok := statsMap["routeRefreshRecv"] ; ok {
                _routeRefresh_rcvd := uint64(value.(float64))
                _rcvd_msgs.ROUTE_REFRESH = &_routeRefresh_rcvd
            }
            if value, ok := statsMap["updatesRecv"] ; ok {
                _update_rcvd := uint64(value.(float64))
                _rcvd_msgs.UPDATE = &_update_rcvd
            }

            if value, ok := statsMap["capabilitySent"] ; ok {
                _capability_sent := uint64(value.(float64))
                _sent_msgs.CAPABILITY = &_capability_sent
            }
            if value, ok := statsMap["keepalivesSent"] ; ok {
                _keepalive_sent := uint64(value.(float64))
                _sent_msgs.KEEPALIVE = &_keepalive_sent
            }
            if value, ok := statsMap["notificationsSent"] ; ok {
                _notification_sent := uint64(value.(float64))
                _sent_msgs.NOTIFICATION = &_notification_sent
            }
            if value, ok := statsMap["opensSent"] ; ok {
                _open_sent := uint64(value.(float64))
                _sent_msgs.OPEN = &_open_sent
            }
            if value, ok := statsMap["routeRefreshSent"] ; ok {
                _routeRefresh_sent := uint64(value.(float64))
                _sent_msgs.ROUTE_REFRESH = &_routeRefresh_sent
            }
            if value, ok := statsMap["updatesSent"] ; ok {
                _update_sent := uint64(value.(float64))
                _sent_msgs.UPDATE = &_update_sent
            }

            if value, ok := statsMap["depthOutq"] ; ok {
                _output := uint32(value.(float64))
                _queues.Output = &_output
            }
            if value, ok := statsMap["depthInq"] ; ok {
                _input := uint32(value.(float64))
                _queues.Input = &_input
            }
        }
        nbrState.SupportedCapabilities = nil
        if capabMap, ok := frrNbrDataJson["neighborCapabilities"].(map[string]interface{}) ; ok {

            if value, ok := capabMap["4byteAs"].(string) ; ok {
                switch value {
                case "advertisedAndReceived":
                    nbrState.SupportedCapabilities = append(nbrState.SupportedCapabilities, ocbinds.OpenconfigBgpTypes_BGP_CAPABILITY_ASN32)
                case "advertised":
                    nbrState.SupportedCapabilities = append(nbrState.SupportedCapabilities, ocbinds.OpenconfigBgpTypes_BGP_CAPABILITY_ASN32_ADVERTISED_ONLY)
                case "received":
                    nbrState.SupportedCapabilities = append(nbrState.SupportedCapabilities, ocbinds.OpenconfigBgpTypes_BGP_CAPABILITY_ASN32_RECEIVED_ONLY)
                }
            }

            if addPath, ok := capabMap["addPath"].(map[string]interface{}) ; ok {
                if ipv4UCast, ok := addPath["ipv4Unicast"].(map[string]interface{}) ; ok {
                    if value, ok := ipv4UCast["rxAdvertised"].(bool) ; (ok && value == true) {
                        nbrState.SupportedCapabilities = append(nbrState.SupportedCapabilities, ocbinds.OpenconfigBgpTypes_BGP_CAPABILITY_ADD_PATHS_ADVERTISED_ONLY)
                    }
                    if value, ok := ipv4UCast["rxReceived"].(bool) ; (ok && value == true) {
                        nbrState.SupportedCapabilities = append(nbrState.SupportedCapabilities, ocbinds.OpenconfigBgpTypes_BGP_CAPABILITY_ADD_PATHS_RECEIVED_ONLY)
                    }
                    if value, ok := ipv4UCast["rxAdvertisedAndReceived"].(bool) ; (ok && value == true) {
                        nbrState.SupportedCapabilities = append(nbrState.SupportedCapabilities, ocbinds.OpenconfigBgpTypes_BGP_CAPABILITY_ADD_PATHS)
                    }
                }
            }

            if value, ok := capabMap["routeRefresh"].(string) ; ok {
                switch value {
                case "advertisedAndReceivedOldNew":
                    fallthrough
                case "advertisedAndReceivedOld":
                    fallthrough
                case "advertisedAndReceivedNew":
                    nbrState.SupportedCapabilities = append(nbrState.SupportedCapabilities, ocbinds.OpenconfigBgpTypes_BGP_CAPABILITY_ROUTE_REFRESH)
                case "advertised":
                    nbrState.SupportedCapabilities = append(nbrState.SupportedCapabilities, ocbinds.OpenconfigBgpTypes_BGP_CAPABILITY_ROUTE_REFRESH_ADVERTISED_ONLY)
                case "received":
                    nbrState.SupportedCapabilities = append(nbrState.SupportedCapabilities, ocbinds.OpenconfigBgpTypes_BGP_CAPABILITY_ROUTE_REFRESH_RECEIVED_ONLY)
                }
            }

            if multi, ok := capabMap["multiprotocolExtensions"].(map[string]interface{}) ; ok {
                if ipv4UCast, ok := multi["ipv4Unicast"].(map[string]interface{}) ; ok {
                    if value, ok := ipv4UCast["advertised"].(bool) ; (ok && value == true) {
                        nbrState.SupportedCapabilities = append(nbrState.SupportedCapabilities, ocbinds.OpenconfigBgpTypes_BGP_CAPABILITY_MPBGP_ADVERTISED_ONLY)
                    }
                    if value, ok := ipv4UCast["received"].(bool) ; (ok && value == true) {
                        nbrState.SupportedCapabilities = append(nbrState.SupportedCapabilities, ocbinds.OpenconfigBgpTypes_BGP_CAPABILITY_MPBGP_RECEIVED_ONLY)
                    }
                    if value, ok := ipv4UCast["advertisedAndReceived"].(bool) ; (ok && value == true) {
                        nbrState.SupportedCapabilities = append(nbrState.SupportedCapabilities, ocbinds.OpenconfigBgpTypes_BGP_CAPABILITY_MPBGP)
                    }
                }
            }

            if value, ok := capabMap["gracefulRestartCapability"].(string) ; ok {
                switch value {
                case "advertisedAndReceived":
                    nbrState.SupportedCapabilities = append(nbrState.SupportedCapabilities, ocbinds.OpenconfigBgpTypes_BGP_CAPABILITY_GRACEFUL_RESTART)
                case "advertised":
                    nbrState.SupportedCapabilities = append(nbrState.SupportedCapabilities, ocbinds.OpenconfigBgpTypes_BGP_CAPABILITY_GRACEFUL_RESTART_ADVERTISED_ONLY)
                case "received":
                    nbrState.SupportedCapabilities = append(nbrState.SupportedCapabilities, ocbinds.OpenconfigBgpTypes_BGP_CAPABILITY_GRACEFUL_RESTART_RECEIVED_ONLY)
                }
            }
        }
    }
    _dynamically_cfred := true

    if cfgDbEntry, cfgdb_get_err := get_spec_nbr_cfg_tbl_entry (cfgDb, nbr_key) ; cfgdb_get_err == nil {
        if value, ok := cfgDbEntry["peer_group_name"] ; ok {
            nbrState.PeerGroup = &value
        }

        if value, ok := cfgDbEntry["admin_status"] ; ok {
            _enabled, _ := strconv.ParseBool(value)
            nbrState.Enabled = &_enabled
        }

        if value, ok := cfgDbEntry["shutdown_message"] ; ok {
            nbrState.ShutdownMessage = &value
        }

        if value, ok := cfgDbEntry["name"] ; ok {
            nbrState.Description = &value
        }

        if value, ok := cfgDbEntry["peer_type"] ; ok {
            switch value {
                case "internal":
                    nbrState.PeerType = ocbinds.OpenconfigBgp_PeerType_INTERNAL
                case "external":
                    nbrState.PeerType = ocbinds.OpenconfigBgp_PeerType_EXTERNAL
            }
        }

        if value, ok := cfgDbEntry["disable_ebgp_connected_route_check"] ; ok {
            _disableEbgpConnectedRouteCheck, _ := strconv.ParseBool(value)
            nbrState.DisableEbgpConnectedRouteCheck = &_disableEbgpConnectedRouteCheck
        }

        if value, ok := cfgDbEntry["enforce_first_as"] ; ok {
            _enforceFirstAs, _ := strconv.ParseBool(value)
            nbrState.EnforceFirstAs = &_enforceFirstAs
        }

        if value, ok := cfgDbEntry["enforce_multihop"] ; ok {
            _enforceMultihop, _ := strconv.ParseBool(value)
            nbrState.EnforceMultihop = &_enforceMultihop
        }

        if value, ok := cfgDbEntry["solo_peer"] ; ok {
            _soloPeer, _ := strconv.ParseBool(value)
            nbrState.SoloPeer = &_soloPeer
        }

        if value, ok := cfgDbEntry["ttl_security_hops"] ; ok {
            if _ttlSecurityHops_u64, err := strconv.ParseUint(value, 10, 8) ; err == nil {
                _ttlSecurityHops_u8 := uint8(_ttlSecurityHops_u64)
                nbrState.TtlSecurityHops = &_ttlSecurityHops_u8
            }
        }

        if value, ok := cfgDbEntry["capability_ext_nexthop"] ; ok {
            _capabilityExtendedNexthop, _ := strconv.ParseBool(value)
            nbrState.CapabilityExtendedNexthop = &_capabilityExtendedNexthop
        }

        if value, ok := cfgDbEntry["capability_dynamic"] ; ok {
            _capabilityDynamic, _ := strconv.ParseBool(value)
            nbrState.CapabilityDynamic = &_capabilityDynamic
        }

        if value, ok := cfgDbEntry["dont_negotiate_capability"] ; ok {
            _dontNegotiateCapability, _ := strconv.ParseBool(value)
            nbrState.DontNegotiateCapability = &_dontNegotiateCapability
        }

        if value, ok := cfgDbEntry["override_capability"] ; ok {
            _overrideCapability, _ := strconv.ParseBool(value)
            nbrState.OverrideCapability = &_overrideCapability
        }

        if value, ok := cfgDbEntry["strict_capability_match"] ; ok {
            _strictCapabilityMatch, _ := strconv.ParseBool(value)
            nbrState.StrictCapabilityMatch = &_strictCapabilityMatch
        }

        if value, ok := cfgDbEntry["local_as_no_prepend"] ; ok {
            _localAsNoPrepend, _ := strconv.ParseBool(value)
            nbrState.LocalAsNoPrepend = &_localAsNoPrepend
        }

        if value, ok := cfgDbEntry["local_as_replace_as"] ; ok {
            _localAsReplaceAs, _ := strconv.ParseBool(value)
            nbrState.LocalAsReplaceAs = &_localAsReplaceAs
        }

        _dynamically_cfred = false
        nbrState.DynamicallyConfigured = &_dynamically_cfred
    } else {
        nbrState.DynamicallyConfigured = &_dynamically_cfred
    }

    return err
}

func fill_nbr_state_timers_info (nbr_key *_xfmr_bgp_nbr_state_key, frrNbrDataValue interface{}, cfgDb *db.DB,
                                 nbr_obj *ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Bgp_Neighbors_Neighbor) error {
    var err error
    nbrTimersState := nbr_obj.Timers.State
    if (frrNbrDataValue != nil) {
        frrNbrDataJson := frrNbrDataValue.(map[string]interface{})

        if value, ok := frrNbrDataJson["bgpTimerHoldTimeMsecs"] ; ok {
            _neg_hold_time := (value.(float64))/1000
            nbrTimersState.NegotiatedHoldTime = &_neg_hold_time
        }

        if value, ok := frrNbrDataJson["bgpTimerKeepAliveIntervalMsecs"] ; ok {
            _keepaliveInterval := (value.(float64))/1000
            nbrTimersState.KeepaliveInterval = &_keepaliveInterval
        }
    }
    if cfgDbEntry, cfgdb_get_err := get_spec_nbr_cfg_tbl_entry (cfgDb, nbr_key) ; cfgdb_get_err == nil {
        if value, ok := cfgDbEntry["conn_retry"] ; ok {
            _connectRetry, _ := strconv.ParseFloat(value, 64)
            nbrTimersState.ConnectRetry = &_connectRetry
        }
        if value, ok := cfgDbEntry["holdtime"] ; ok {
            _holdTime, _ := strconv.ParseFloat(value, 64)
            nbrTimersState.HoldTime = &_holdTime
        }
        if value, ok := cfgDbEntry["min_adv_interval"] ; ok {
            _minimumAdvertisementInterval, _ := strconv.ParseFloat(value, 64)
            nbrTimersState.MinimumAdvertisementInterval = &_minimumAdvertisementInterval
        }
    }

    return err
}

func fill_nbr_state_transport_info (nbr_key *_xfmr_bgp_nbr_state_key, frrNbrDataValue interface{}, cfgDb *db.DB,
                                    nbr_obj *ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Bgp_Neighbors_Neighbor) error {
    var err error
    ygot.BuildEmptyTree(nbr_obj.Transport)
    nbrTransportState := nbr_obj.Transport.State
    if (frrNbrDataValue != nil) {
        frrNbrDataJson := frrNbrDataValue.(map[string]interface{})

        if value, ok := frrNbrDataJson["hostLocal"] ; ok {
            _localAddress := string(value.(string))
            nbrTransportState.LocalAddress = &_localAddress
        }
        if value, ok := frrNbrDataJson["portLocal"] ; ok {
            _localPort := uint16(value.(float64))
            nbrTransportState.LocalPort = &_localPort
        }
        if value, ok := frrNbrDataJson["hostForeign"] ; ok {
            _remoteAddress := string(value.(string))
            nbrTransportState.RemoteAddress = &_remoteAddress
        }
        if value, ok := frrNbrDataJson["portForeign"] ; ok {
            _remotePort := uint16(value.(float64))
            nbrTransportState.RemotePort = &_remotePort
        }
    }
    if cfgDbEntry, cfgdb_get_err := get_spec_nbr_cfg_tbl_entry (cfgDb, nbr_key) ; cfgdb_get_err == nil {
        if value, ok := cfgDbEntry["passive_mode"] ; ok {
            _passiveMode, _ := strconv.ParseBool(value)
            nbrTransportState.PassiveMode = &_passiveMode
        }
    }

    return err
}

func fill_nbr_state_info (get_req_uri_type E_bgp_nbr_state_get_req_uri_t, nbr_key *_xfmr_bgp_nbr_state_key, frrNbrDataValue interface{}, cfgDb *db.DB,
                          nbr_obj *ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Bgp_Neighbors_Neighbor) error {
    switch get_req_uri_type {
        case E_bgp_nbr_state_get_req_uri_nbr_state:
            return fill_nbr_state_cmn_info (nbr_key, frrNbrDataValue, cfgDb, nbr_obj)
        case E_bgp_nbr_state_get_req_uri_nbr_timers_state:
            return fill_nbr_state_timers_info (nbr_key, frrNbrDataValue, cfgDb, nbr_obj)
        case E_bgp_nbr_state_get_req_uri_nbr_transport_state:
            return fill_nbr_state_transport_info (nbr_key, frrNbrDataValue, cfgDb, nbr_obj)
    }

    return errors.New("Opertational error")
}

func get_specific_nbr_state (get_req_uri_type E_bgp_nbr_state_get_req_uri_t,
                             nbr_obj *ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Bgp_Neighbors_Neighbor,
                             cfgDb *db.DB, nbr_key *_xfmr_bgp_nbr_state_key) error {
    var err error
    var nbrKey string
    vtysh_cmd := "show ip bgp vrf " + nbr_key.niName + " neighbors " + nbr_key.nbrAddr + " json"
    nbrMapJson, cmd_err := exec_vtysh_cmd (vtysh_cmd)
    if cmd_err != nil {
        log.Errorf("Failed to fetch bgp neighbors state info for niName:%s nbrAddr:%s. Err: %s vtysh_cmd %s \n", nbr_key.niName, nbr_key.nbrAddr, cmd_err, vtysh_cmd)
    }

    if net.ParseIP(nbr_key.nbrAddr) == nil {
        nbrKey = nbr_key.nbrAddr
    } else {
        nbrKey = net.ParseIP(nbr_key.nbrAddr).String()
    }

    if frrNbrDataJson, ok := nbrMapJson[nbrKey].(map[string]interface{}) ; ok {
        err = fill_nbr_state_info (get_req_uri_type, nbr_key, frrNbrDataJson, cfgDb, nbr_obj)
    } else {
        err = fill_nbr_state_info (get_req_uri_type, nbr_key, nil, cfgDb, nbr_obj)
    }

    return err
}

func validate_nbr_state_get (inParams XfmrParams, dbg_log string) (*ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Bgp_Neighbors_Neighbor, _xfmr_bgp_nbr_state_key, error) {
    var err error
    oper_err := errors.New("Opertational error")
    var nbr_key _xfmr_bgp_nbr_state_key
    var bgp_obj *ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Bgp

    bgp_obj, nbr_key.niName, err = getBgpRoot (inParams)
    if err != nil {
        log.Errorf ("%s failed !! Error:%s", dbg_log , err);
        return nil, nbr_key, err
    }

    pathInfo := NewPathInfo(inParams.uri)
    targetUriPath, _ := getYangPathFromUri(pathInfo.Path)
    nbr_key.nbrAddr = pathInfo.Var("neighbor-address")
    log.Infof("%s : path:%s; template:%s targetUriPath:%s niName:%s nbrAddr:%s",
              dbg_log, pathInfo.Path, pathInfo.Template, targetUriPath, nbr_key.niName, nbr_key.nbrAddr)

    nbrs_obj := bgp_obj.Neighbors
    if nbrs_obj == nil {
        log.Errorf("%s failed !! Error: Neighbors container missing", dbg_log)
        return nil, nbr_key, oper_err
    }

    nbr_obj, ok := nbrs_obj.Neighbor[nbr_key.nbrAddr]
    if !ok {
        log.Infof("%s Neighbor object missing, add new", dbg_log)
        nbr_obj,_ = nbrs_obj.NewNeighbor(nbr_key.nbrAddr)
    }
    ygot.BuildEmptyTree(nbr_obj)
    return nbr_obj, nbr_key, err
}

type E_bgp_nbr_state_get_req_uri_t string
const (
    E_bgp_nbr_state_get_req_uri_nbr_state E_bgp_nbr_state_get_req_uri_t = "GET_REQ_URI_BGP_NBR_STATE"
    E_bgp_nbr_state_get_req_uri_nbr_timers_state E_bgp_nbr_state_get_req_uri_t = "GET_REQ_URI_BGP_NBR_TIMERS_STATE"
    E_bgp_nbr_state_get_req_uri_nbr_transport_state E_bgp_nbr_state_get_req_uri_t = "GET_REQ_URI_BGP_NBR_TRANSPORT_STATE"
)

var DbToYang_bgp_nbrs_nbr_state_xfmr SubTreeXfmrDbToYang = func(inParams XfmrParams) error {
    var err error
    cmn_log := "GET: xfmr for BGP-nbrs state"
    get_req_uri_type := E_bgp_nbr_state_get_req_uri_nbr_state

    pathInfo := NewPathInfo(inParams.uri)
    targetUriPath, err := getYangPathFromUri(pathInfo.Path)
    switch targetUriPath {
        case "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/timers/state":
            cmn_log = "GET: xfmr for BGP-nbrs timers state"
            get_req_uri_type = E_bgp_nbr_state_get_req_uri_nbr_timers_state
        case "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/transport/state":
            cmn_log = "GET: xfmr for BGP-nbrs transport state"
            get_req_uri_type = E_bgp_nbr_state_get_req_uri_nbr_transport_state
    }

    nbr_obj, nbr_key, get_err := validate_nbr_state_get (inParams, cmn_log);
    if get_err != nil {
        log.Info("Neighbor state get subtree error: ", get_err)
        return get_err
    }

    err = get_specific_nbr_state (get_req_uri_type, nbr_obj, inParams.dbs[db.ConfigDB], &nbr_key)
    return err;
}

type _xfmr_bgp_nbr_af_state_key struct {
    niName string
    nbrAddr string
    afiSafiNameStr string
    afiSafiNameDbStr string
    afiSafiNameEnum ocbinds.E_OpenconfigBgpTypes_AFI_SAFI_TYPE
}

func get_afi_safi_name_enum_dbstr_for_ocstr (afiSafiNameStr string) (ocbinds.E_OpenconfigBgpTypes_AFI_SAFI_TYPE, string, bool) {
    switch afiSafiNameStr {
        case "IPV4_UNICAST":
            return ocbinds.OpenconfigBgpTypes_AFI_SAFI_TYPE_IPV4_UNICAST, "ipv4_unicast", true
        case "IPV6_UNICAST":
            return ocbinds.OpenconfigBgpTypes_AFI_SAFI_TYPE_IPV6_UNICAST, "ipv6_unicast", true
        case "L2VPN_EVPN":
            return ocbinds.OpenconfigBgpTypes_AFI_SAFI_TYPE_L2VPN_EVPN, "l2vpn_evpn", true
        default:
            return ocbinds.OpenconfigBgpTypes_AFI_SAFI_TYPE_UNSET, "", false
    }
}

func validate_nbr_af_state_get (inParams XfmrParams, dbg_log string) (*ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Bgp_Neighbors_Neighbor_AfiSafis_AfiSafi_State,
                                                                      _xfmr_bgp_nbr_af_state_key, error) {
    var err error
    var ok bool
    oper_err := errors.New("Opertational error")
    var nbr_af_key _xfmr_bgp_nbr_af_state_key
    var bgp_obj *ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Bgp

    bgp_obj, nbr_af_key.niName, err = getBgpRoot (inParams)
    if err != nil {
        log.Errorf ("%s failed !! Error:%s", dbg_log , err);
        return nil, nbr_af_key, err
    }

    pathInfo := NewPathInfo(inParams.uri)
    targetUriPath, err := getYangPathFromUri(pathInfo.Path)
    nbr_af_key.nbrAddr = pathInfo.Var("neighbor-address")
    nbr_af_key.afiSafiNameStr = pathInfo.Var("afi-safi-name")
    nbr_af_key.afiSafiNameEnum, nbr_af_key.afiSafiNameDbStr, ok = get_afi_safi_name_enum_dbstr_for_ocstr (nbr_af_key.afiSafiNameStr)
    if !ok {
        log.Errorf("%s failed !! Error: AFI-SAFI ==> %s not supported", dbg_log, nbr_af_key.afiSafiNameStr)
        return nil, nbr_af_key, oper_err
    }

    log.Infof("%s : path:%s; template:%s targetUriPath:%s niName:%s nbrAddr:%s afiSafiNameStr:%s afiSafiNameEnum:%d afiSafiNameDbStr:%s",
              dbg_log, pathInfo.Path, pathInfo.Template, targetUriPath, nbr_af_key.niName, nbr_af_key.nbrAddr, nbr_af_key.afiSafiNameStr, nbr_af_key.afiSafiNameEnum, nbr_af_key.afiSafiNameDbStr)

    nbrs_obj := bgp_obj.Neighbors
    if nbrs_obj == nil {
        log.Errorf("%s failed !! Error: Neighbors container missing", dbg_log)
        return nil, nbr_af_key, oper_err
    }

    nbr_obj, ok := nbrs_obj.Neighbor[nbr_af_key.nbrAddr]
    if !ok {
        log.Errorf("%s Neighbor object missing, add new", dbg_log)
        nbr_obj,_ = nbrs_obj.NewNeighbor(nbr_af_key.nbrAddr)
    }
    ygot.BuildEmptyTree(nbr_obj)

    afiSafis_obj := nbr_obj.AfiSafis
    if afiSafis_obj == nil {
        log.Errorf("%s failed !! Error: Neighbors AfiSafis container missing", dbg_log)
        return nil, nbr_af_key, oper_err
    }
    ygot.BuildEmptyTree(afiSafis_obj)

    afiSafi_obj, ok := afiSafis_obj.AfiSafi[nbr_af_key.afiSafiNameEnum]
    if !ok {
        log.Errorf("%s Neighbor AfiSafi object missing, allocate new", dbg_log)
        afiSafi_obj, _ = afiSafis_obj.NewAfiSafi(nbr_af_key.afiSafiNameEnum)
    }

    ygot.BuildEmptyTree(afiSafi_obj)

    afiSafiState_obj := afiSafi_obj.State
    if afiSafiState_obj == nil {
        log.Errorf("%s failed !! Error: Neighbor AfiSafi State object missing", dbg_log)
        return nil, nbr_af_key, oper_err
    }
    ygot.BuildEmptyTree(afiSafiState_obj)

    return afiSafiState_obj, nbr_af_key, err
}

func get_spec_nbr_af_cfg_tbl_entry (cfgDb *db.DB, key *_xfmr_bgp_nbr_af_state_key) (map[string]string, error) {
    var err error

    nbrAfCfgTblTs := &db.TableSpec{Name: "BGP_NEIGHBOR_AF"}
    nbrAfEntryKey := db.Key{Comp: []string{key.niName, key.nbrAddr, key.afiSafiNameDbStr}}

    var entryValue db.Value
    if entryValue, err = cfgDb.GetEntry(nbrAfCfgTblTs, nbrAfEntryKey) ; err != nil {
        return nil, err
    }

    return entryValue.Field, err
}

var DbToYang_bgp_nbrs_nbr_af_state_xfmr SubTreeXfmrDbToYang = func(inParams XfmrParams) error {
    var err error
    var nbrKey string
    cmn_log := "GET: xfmr for BGP-nbrs-nbr-af state"

    nbrs_af_state_obj, nbr_af_key, get_err := validate_nbr_af_state_get (inParams, cmn_log);
    if get_err != nil {
        return get_err
    }

    var afiSafi_cmd string
    switch (nbr_af_key.afiSafiNameEnum) {
        case ocbinds.OpenconfigBgpTypes_AFI_SAFI_TYPE_IPV4_UNICAST:
            afiSafi_cmd = "ipv4"
        case ocbinds.OpenconfigBgpTypes_AFI_SAFI_TYPE_IPV6_UNICAST:
            afiSafi_cmd = "ipv6"
    }

    if cfgDbEntry, cfgdb_get_err := get_spec_nbr_af_cfg_tbl_entry (inParams.dbs[db.ConfigDB], &nbr_af_key) ; cfgdb_get_err == nil {
        nbrs_af_state_obj.AfiSafiName = nbr_af_key.afiSafiNameEnum
        if value, ok := cfgDbEntry["admin_status"] ; ok {
            _enabled, _ := strconv.ParseBool(value)
            nbrs_af_state_obj.Enabled = &_enabled
        }

        if value, ok := cfgDbEntry["soft_reconfiguration_in"] ; ok {
            _softReconfigurationIn, _ := strconv.ParseBool(value)
            nbrs_af_state_obj.SoftReconfigurationIn = &_softReconfigurationIn
        }

        if value, ok := cfgDbEntry["unsuppress_map_name"] ; ok {
            nbrs_af_state_obj.UnsuppressMapName = &value
        }

        if value, ok := cfgDbEntry["weight"] ; ok {
            if _weight_u64, err := strconv.ParseUint(value, 10, 32) ; err == nil {
                _weight_u32 := uint32(_weight_u64)
                nbrs_af_state_obj.Weight = &_weight_u32
            }
        }

        if value, ok := cfgDbEntry["as_override"] ; ok {
            _asOverride, _ := strconv.ParseBool(value)
            nbrs_af_state_obj.AsOverride = &_asOverride
        }

        if value, ok := cfgDbEntry["send_community"] ; ok {
            switch value {
                case "standard":
                    nbrs_af_state_obj.SendCommunity = ocbinds.OpenconfigBgpExt_BgpExtCommunityType_STANDARD
                case "extended":
                    nbrs_af_state_obj.SendCommunity = ocbinds.OpenconfigBgpExt_BgpExtCommunityType_EXTENDED
                case "both":
                    nbrs_af_state_obj.SendCommunity = ocbinds.OpenconfigBgpExt_BgpExtCommunityType_BOTH
                case "none":
                    nbrs_af_state_obj.SendCommunity = ocbinds.OpenconfigBgpExt_BgpExtCommunityType_NONE
                case "large":
                    nbrs_af_state_obj.SendCommunity = ocbinds.OpenconfigBgpExt_BgpExtCommunityType_LARGE
                case "all":
                    nbrs_af_state_obj.SendCommunity = ocbinds.OpenconfigBgpExt_BgpExtCommunityType_ALL
            }
        }

        if value, ok := cfgDbEntry["rrclient"] ; ok {
            _routeReflectorClient, _ := strconv.ParseBool(value)
            nbrs_af_state_obj.RouteReflectorClient = &_routeReflectorClient
        }
    }

    vtysh_cmd := "show ip bgp vrf " + nbr_af_key.niName + " " + afiSafi_cmd + " neighbors " + nbr_af_key.nbrAddr + " json"
    nbrMapJson, nbr_cmd_err := exec_vtysh_cmd (vtysh_cmd)
    if nbr_cmd_err != nil {
        log.Errorf("Failed to fetch bgp neighbors state info for niName:%s nbrAddr:%s afi-safi-name:%s. Err: %s, Cmd: %s\n",
                   nbr_af_key.niName, nbr_af_key.nbrAddr, afiSafi_cmd, nbr_cmd_err, vtysh_cmd)
        return nil
    }
    if net.ParseIP(nbr_af_key.nbrAddr) == nil {
        nbrKey = nbr_af_key.nbrAddr
    } else {
        nbrKey = net.ParseIP(nbr_af_key.nbrAddr).String()
    }

    frrNbrDataJson, ok := nbrMapJson[nbrKey].(map[string]interface{}); if !ok {
        log.Errorf("Failed data from bgp neighbors state info for niName:%s nbrAddr:%s afi-safi-name:%s. Err: %s vtysh_cmd: %s \n",
                   nbr_af_key.niName, nbr_af_key.nbrAddr, afiSafi_cmd, nbr_cmd_err, vtysh_cmd)
        return nil
    }

    _active := false
    var _prefixes ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Bgp_Neighbors_Neighbor_AfiSafis_AfiSafi_State_Prefixes

    var _activeRcvdPrefixes, _activeSentPrefixes uint32
    nbrs_af_state_obj.AfiSafiName = nbr_af_key.afiSafiNameEnum
    if AddrFamilyMap, ok := frrNbrDataJson["addressFamilyInfo"].(map[string]interface{}) ; ok {
        log.Info("Family dump: %v %d", AddrFamilyMap, nbrs_af_state_obj.AfiSafiName)
        if nbrs_af_state_obj.AfiSafiName == ocbinds.OpenconfigBgpTypes_AFI_SAFI_TYPE_IPV4_UNICAST {
            if ipv4UnicastMap, ok := AddrFamilyMap["ipv4Unicast"].(map[string]interface{}) ; ok {
                log.Info("IPv4 dump: %v", AddrFamilyMap)
                _active = true
                if value, ok := ipv4UnicastMap["acceptedPrefixCounter"] ; ok {
                    _activeRcvdPrefixes = uint32(value.(float64))
                    log.Info("IPv4 dump recd: %d", _activeRcvdPrefixes)
                    _prefixes.Received = &_activeRcvdPrefixes
                }
                if value, ok := ipv4UnicastMap["sentPrefixCounter"] ; ok {
                    _activeSentPrefixes = uint32(value.(float64))
                    _prefixes.Sent = &_activeSentPrefixes
                    log.Info("IPv4 dump set: %d", _activeSentPrefixes)
                }
            }
        } else if nbrs_af_state_obj.AfiSafiName == ocbinds.OpenconfigBgpTypes_AFI_SAFI_TYPE_IPV6_UNICAST {
            if ipv6UnicastMap, ok := AddrFamilyMap["ipv6Unicast"].(map[string]interface{}) ; ok {
                _active = true
                if value, ok := ipv6UnicastMap["acceptedPrefixCounter"] ; ok {
                    _activeRcvdPrefixes = uint32(value.(float64))
                    _prefixes.Received = &_activeRcvdPrefixes
                }
                if value, ok := ipv6UnicastMap["sentPrefixCounter"] ; ok {
                    _activeSentPrefixes = uint32(value.(float64))
                    _prefixes.Sent = &_activeSentPrefixes
                }
           }
        }
    }
 
    vtysh_cmd = "show ip bgp vrf " + nbr_af_key.niName + " " + afiSafi_cmd + " neighbors " + nbr_af_key.nbrAddr + " received-routes json"
    rcvdRoutesJson, rcvd_cmd_err := exec_vtysh_cmd (vtysh_cmd)
    if rcvd_cmd_err != nil {
        log.Errorf("Failed check to fetch bgp neighbors received-routes state info for niName:%s nbrAddr:%s afi-safi-name:%s. Err: %s\n",
                   nbr_af_key.niName, nbr_af_key.nbrAddr, afiSafi_cmd, rcvd_cmd_err)
    }

    if rcvd_cmd_err == nil {
        var _receivedPrePolicy uint32
        if value, ok := rcvdRoutesJson["totalPrefixCounter"] ; ok {
            _active = true
            _receivedPrePolicy = uint32(value.(float64))
            _prefixes.ReceivedPrePolicy = &_receivedPrePolicy
        }
    }
    nbrs_af_state_obj.Active = &_active
    nbrs_af_state_obj.Prefixes = &_prefixes

    return err;
}

var YangToDb_bgp_nbr_community_type_fld_xfmr FieldXfmrYangToDb = func(inParams XfmrParams) (map[string]string, error) {
    res_map := make(map[string]string)

    var err error
    if inParams.param == nil {
        err = errors.New("No Params");
        return res_map, err
    }

    if inParams.oper == DELETE {
        subOpMap := make(map[db.DBNum]map[string]map[string]db.Value)

        if _, ok := subOpMap[db.ConfigDB]; !ok {
            subOpMap[db.ConfigDB] = make(map[string]map[string]db.Value)
        }
        if _, ok := subOpMap[db.ConfigDB]["BGP_NEIGHBOR_AF"]; !ok {
            subOpMap[db.ConfigDB]["BGP_NEIGHBOR_AF"] = make(map[string]db.Value)
        }
        subOpMap[db.ConfigDB]["BGP_NEIGHBOR_AF"][inParams.key] = db.Value{Field: make(map[string]string)}
        subOpMap[db.ConfigDB]["BGP_NEIGHBOR_AF"][inParams.key].Field["send_community"] = "both"

        inParams.subOpDataMap[UPDATE] = &subOpMap
        return res_map, nil
    }

    community_type, _ := inParams.param.(ocbinds.E_OpenconfigBgpExt_BgpExtCommunityType)
    log.Info("YangToDb_bgp_nbr_community_type_fld_xfmr: ", inParams.ygRoot, " Xpath: ", inParams.uri, " community_type: ", community_type)

    if (community_type == ocbinds.OpenconfigBgpExt_BgpExtCommunityType_STANDARD) {
        res_map["send_community"] = "standard"
    }  else if (community_type == ocbinds.OpenconfigBgpExt_BgpExtCommunityType_EXTENDED) {
        res_map["send_community"] = "extended"
    }  else if (community_type == ocbinds.OpenconfigBgpExt_BgpExtCommunityType_BOTH) {
        res_map["send_community"] = "both"
    }  else if (community_type == ocbinds.OpenconfigBgpExt_BgpExtCommunityType_NONE) {
        res_map["send_community"] = "none"
    }  else if (community_type == ocbinds.OpenconfigBgpExt_BgpExtCommunityType_LARGE) {
        res_map["send_community"] = "large"
    }  else if (community_type == ocbinds.OpenconfigBgpExt_BgpExtCommunityType_ALL) {
        res_map["send_community"] = "all"
    } else {
        err = errors.New("send_community  Missing");
        return res_map, err
    }

    return res_map, nil

}

var DbToYang_bgp_nbr_community_type_fld_xfmr FieldXfmrDbtoYang = func(inParams XfmrParams) (map[string]interface{}, error) {

    var err error
    result := make(map[string]interface{})

    data := (*inParams.dbDataMap)[inParams.curDb]
    log.Info("DbToYang_bgp_nbr_community_type_fld_xfmr : ", data, "inParams : ", inParams)

    pTbl := data["BGP_NEIGHBOR_AF"]
    if _, ok := pTbl[inParams.key]; !ok {
        log.Info("DbToYang_bgp_nbr_community_type_fld_xfmr BGP Peer group not found : ", inParams.key)
        return result, errors.New("BGP neighbor not found : " + inParams.key)
    }
    pGrpKey := pTbl[inParams.key]
    community_type, ok := pGrpKey.Field["send_community"]

    if ok {
        if (community_type == "standard") {
            result["send-community"] = "STANDARD"
        } else if (community_type == "extended") {
            result["send-community"] = "EXTENDED"
        } else if (community_type == "both") {
            result["send-community"] = "BOTH"
        } else if (community_type == "none") {
            result["send-community"] = "NONE"
        }
    } else {
        log.Info("send_community not found in DB")
    }
    return result, err
}

var YangToDb_bgp_nbr_orf_type_fld_xfmr FieldXfmrYangToDb = func(inParams XfmrParams) (map[string]string, error) {
    res_map := make(map[string]string)

    var err error
    if inParams.param == nil {
        err = errors.New("No Params");
        return res_map, err
    }

    if inParams.oper == DELETE {
        res_map["cap_orf"] = ""
        return res_map, nil
    }

    orf_type, _ := inParams.param.(ocbinds.E_OpenconfigBgpExt_BgpOrfType)
    log.Info("YangToDb_bgp_nbr_orf_type_fld_xfmr: ", inParams.ygRoot, " Xpath: ", inParams.uri, " orf_type: ", orf_type)

    if (orf_type == ocbinds.OpenconfigBgpExt_BgpOrfType_SEND) {
        res_map["cap_orf"] = "send"
    }  else if (orf_type == ocbinds.OpenconfigBgpExt_BgpOrfType_RECEIVE) {
        res_map["cap_orf"] = "receive"
    }  else if (orf_type == ocbinds.OpenconfigBgpExt_BgpOrfType_BOTH) {
        res_map["cap_orf"] = "both"
    } else {
        err = errors.New("ORF type Missing");
        return res_map, err
    }

    return res_map, nil

}

var DbToYang_bgp_nbr_orf_type_fld_xfmr FieldXfmrDbtoYang = func(inParams XfmrParams) (map[string]interface{}, error) {

    var err error
    result := make(map[string]interface{})

    data := (*inParams.dbDataMap)[inParams.curDb]
    log.Info("DbToYang_bgp_nbr_orf_type_fld_xfmr : ", data, "inParams : ", inParams)

    pTbl := data["BGP_NEIGHBOR_AF"]
    if _, ok := pTbl[inParams.key]; !ok {
        log.Info("DbToYang_bgp_nbr_orf_type_fld_xfmr BGP neighbor not found : ", inParams.key)
        return result, errors.New("BGP neighbor not found : " + inParams.key)
    }
    pNbrKey := pTbl[inParams.key]
    orf_type, ok := pNbrKey.Field["cap_orf"]

    if ok {
        if (orf_type == "send") {
            result["orf-type"] = "SEND"
        } else if (orf_type == "receive") {
            result["orf-type"] = "RECEIVE"
        } else if (orf_type == "both") {
            result["orf-type"] = "BOTH"
        }
    } else {
        log.Info("cap_orf_direction field not found in DB")
    }
    return result, err
}

var YangToDb_bgp_nbrs_nbr_auth_password_xfmr SubTreeXfmrYangToDb = func(inParams XfmrParams) (map[string]map[string]db.Value, error) {
    var err error
    res_map := make(map[string]map[string]db.Value)
    authmap := make(map[string]db.Value)

    var bgp_obj *ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Bgp

    bgp_obj, niName, err := getBgpRoot (inParams)
    if err != nil {
        log.Errorf ("BGP root get failed!");
        return res_map, err
    }

    pathInfo := NewPathInfo(inParams.uri)
    targetUriPath, _ := getYangPathFromUri(pathInfo.Path)
    nbrAddr := pathInfo.Var("neighbor-address")
    log.Infof("YangToDb_bgp_nbrs_nbr_auth_password_xfmr VRF:%s nbrAddr:%s URI:%s", niName, nbrAddr, targetUriPath)

    nbrs_obj := bgp_obj.Neighbors
    if nbrs_obj == nil {
        log.Errorf("Error: Neighbors container missing")
        return res_map, err
    }

    nbr_obj, ok := nbrs_obj.Neighbor[nbrAddr]
    if !ok {
        log.Infof("%s Neighbor object missing, add new", nbrAddr)
        return res_map, err
    }
    entry_key := niName + "|" + nbrAddr
    if nbr_obj.AuthPassword.Config != nil && nbr_obj.AuthPassword.Config.Password != nil && (inParams.oper != DELETE){
        auth_password := nbr_obj.AuthPassword.Config.Password
        encrypted := nbr_obj.AuthPassword.Config.Encrypted
        log.Infof("Neighbor password:%d encrypted:%s", *auth_password, *encrypted)

        encrypted_password := *auth_password
        if encrypted == nil || (encrypted != nil && *encrypted == false) {
            cmd := "show bgp encrypt " + *auth_password + " json"
            bgpNeighPasswordJson, cmd_err := exec_vtysh_cmd (cmd)
            if (cmd_err != nil) {
                log.Errorf ("Failed !! Error:%s", cmd_err);
                return res_map, err
            }
            encrypted_password, ok = bgpNeighPasswordJson["Encrypted_string"].(string); if !ok {
                return res_map, err
            }
            log.Infof("Neighbor password:%s encrypted:%s", *auth_password, encrypted_password)
        }

        authmap[entry_key] = db.Value{Field: make(map[string]string)}
        authmap[entry_key].Field["auth_password"] = encrypted_password
    } else if (inParams.oper == DELETE) {
        authmap[entry_key] = db.Value{Field: make(map[string]string)}
        authmap[entry_key].Field["auth_password"] = ""
    }
    res_map["BGP_NEIGHBOR"] = authmap
    return res_map, err
}

var DbToYang_bgp_nbrs_nbr_auth_password_xfmr SubTreeXfmrDbToYang = func (inParams XfmrParams) (error) {
    var err error
    var bgp_obj *ocbinds.OpenconfigNetworkInstance_NetworkInstances_NetworkInstance_Protocols_Protocol_Bgp

    bgp_obj, niName, err := getBgpRoot (inParams)
    if err != nil {
        log.Errorf ("BGP root get failed!");
        return err
    }

    pathInfo := NewPathInfo(inParams.uri)
    targetUriPath, _ := getYangPathFromUri(pathInfo.Path)
    nbrAddr := pathInfo.Var("neighbor-address")
    log.Infof("DbToYang_bgp_nbrs_nbr_auth_password_xfmr VRF:%s nbrAddr:%s URI:%s", niName, nbrAddr, targetUriPath)

    nbrs_obj := bgp_obj.Neighbors
    if nbrs_obj == nil {
        log.Errorf("Error: Neighbors container missing")
        return err
    }

    nbr_obj, ok := nbrs_obj.Neighbor[nbrAddr]
    if !ok {
        log.Infof("%s Neighbor object missing, add new", nbrAddr)
        nbr_obj,_ = nbrs_obj.NewNeighbor(nbrAddr)
    }
    ygot.BuildEmptyTree(nbr_obj)
    var nbr_key _xfmr_bgp_nbr_state_key
    nbr_key.niName = niName
    nbr_key.nbrAddr = nbrAddr
    if cfgDbEntry, cfgdb_get_err := get_spec_nbr_cfg_tbl_entry (inParams.dbs[db.ConfigDB], &nbr_key) ; cfgdb_get_err == nil {
        if value, ok := cfgDbEntry["auth_password"] ; ok {
            nbr_obj.AuthPassword.Config.Password = &value
            nbr_obj.AuthPassword.State.Password = &value
            encrypted := true
            nbr_obj.AuthPassword.Config.Encrypted = &encrypted
            nbr_obj.AuthPassword.State.Encrypted = &encrypted
        }
    }

    return err
}


