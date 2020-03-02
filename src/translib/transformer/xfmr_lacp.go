////////////////////////////////////////////////////////////////////////////////
//                                                                            //
//  Copyright 2019 Dell, Inc.                                                 //
//                                                                            //
//  Licensed under the Apache License, Version 2.0 (the "License");           //
//  you may not use this file except in compliance with the License.          //
//  You may obtain a copy of the License at                                   //
//                                                                            //
//  http://www.apache.org/licenses/LICENSE-2.0                                //
//                                                                            //
//  Unless required by applicable law or agreed to in writing, software       //
//  distributed under the License is distributed on an "AS IS" BASIS,         //
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  //
//  See the License for the specific language governing permissions and       //
//  limitations under the License.                                            //
//                                                                            //
////////////////////////////////////////////////////////////////////////////////

package transformer

import (
    "translib/tlerr"
    "errors"
    "encoding/json"
    "translib/ocbinds"
    "translib/db"
    "os/exec"

    log "github.com/golang/glog"
    "github.com/openconfig/ygot/ygot"
)

func init () {
    XlateFuncBind("DbToYang_lacp_get_xfmr", DbToYang_lacp_get_xfmr)
}

func getLacpRoot (s *ygot.GoStruct) *ocbinds.OpenconfigLacp_Lacp {
    deviceObj := (*s).(*ocbinds.Device)
    return deviceObj.Lacp
}

func getLacpData(ifKey string) (map[string]interface{}, error) {
    var TeamdJson map[string]interface{}
    var err error
    errStr := "Internal Error"

    cmd := exec.Command("docker", "exec", "teamd", "teamdctl", ifKey, "state", "dump")
    out_stream, e := cmd.StdoutPipe()
    if e != nil {
        log.Warningf("Can't get stdout pipe: %s\n", e.Error())
        return TeamdJson, tlerr.InternalError{Format:errStr}
    }
    err = cmd.Start()
    if err != nil {
        log.Warningf("cmd.Start() failed with %s\n", err.Error())
        return TeamdJson, tlerr.InternalError{Format:errStr}
    }

    err = json.NewDecoder(out_stream).Decode(&TeamdJson)
    if err != nil {
        log.Infof("Not able to decode teamd json output")
        return TeamdJson, tlerr.InternalError{Format:errStr}
    }

    err = cmd.Wait()
    if err != nil {
        log.Warningf("Command execution completion failed with %s\n", err.Error())
        return TeamdJson, tlerr.InternalError{Format:errStr}
    }

    return TeamdJson, nil
}

func fillLacpState(TeamdJson map[string]interface{}, state *ocbinds.OpenconfigLacp_Lacp_Interfaces_Interface_State) error {
    var runner_map map[string]interface{}
    var status bool
    if runner_map, status = TeamdJson["runner"].(map[string]interface{}); !status {
        errStr := "LAG not in LACP mode"
        log.Infof(errStr)
        return tlerr.InvalidArgsError{Format:errStr}
    }

    prio := runner_map["sys_prio"].(float64)
    sys_prio := uint16(prio)
    state.SystemPriority = &sys_prio

    fast_rate := runner_map["fast_rate"].(bool)
    if fast_rate {
    state.Interval = ocbinds.OpenconfigLacp_LacpPeriodType_FAST
    } else {
        state.Interval = ocbinds.OpenconfigLacp_LacpPeriodType_SLOW
    }

    active := runner_map["active"].(bool)
    if active {
        state.LacpMode = ocbinds.OpenconfigLacp_LacpActivityType_ACTIVE
    } else {
        state.LacpMode = ocbinds.OpenconfigLacp_LacpActivityType_PASSIVE
    }

    team_device := TeamdJson["team_device"].(map[string]interface{})
    team_device_ifinfo := team_device["ifinfo"].(map[string]interface{})
    SystemIdMac := team_device_ifinfo["dev_addr"].(string)
    state.SystemIdMac = &SystemIdMac

    return nil
}

func _fillLacpMemberHelper(ports_map map[string]interface{}, ifKey string, lacpMemberObj *ocbinds.OpenconfigLacp_Lacp_Interfaces_Interface_Members_Member) error {
    member_map := ports_map[ifKey].(map[string]interface{})
    if port_runner, ok := member_map["runner"].(map[string]interface{}); ok {

        selected := port_runner["selected"].(bool)
        lacpMemberObj.State.Selected = &selected

        actor := port_runner["actor_lacpdu_info"].(map[string]interface{})

        port_num := actor["port"].(float64)
        pport_num := uint16(port_num)
        lacpMemberObj.State.PortNum = &pport_num

        system_id := actor["system"].(string)
        lacpMemberObj.State.SystemId = &system_id

        oper_key := actor["key"].(float64)
        ooper_key := uint16(oper_key)
        lacpMemberObj.State.OperKey = &ooper_key

        partner := port_runner["partner_lacpdu_info"].(map[string]interface{})
        partner_port_num := partner["port"].(float64)
        ppartner_num := uint16(partner_port_num)
        lacpMemberObj.State.PartnerPortNum = &ppartner_num

        partner_system_id := partner["system"].(string)
        lacpMemberObj.State.PartnerId = &partner_system_id

        partner_oper_key := partner["key"].(float64)
        ppartner_key := uint16(partner_oper_key)
        lacpMemberObj.State.PartnerKey = &ppartner_key
        return nil
    }
    errStr := "LACP Member Information not available"
    return tlerr.InvalidArgsError{Format:errStr}
}

func fillLacpMember(TeamdJson map[string]interface{}, ifMemKey string, lacpMemberObj *ocbinds.OpenconfigLacp_Lacp_Interfaces_Interface_Members_Member) error {

    var err error

    if ports_map,ok := TeamdJson["ports"].(map[string]interface{}); ok {
        for ifKey := range ports_map {
            if ifKey == ifMemKey {
                err = _fillLacpMemberHelper(ports_map, ifKey, lacpMemberObj)
            }
        }
    }


    return err
}

func fillLacpMembers(TeamdJson map[string]interface{}, members *ocbinds.OpenconfigLacp_Lacp_Interfaces_Interface_Members) error {
    var lacpMemberObj *ocbinds.OpenconfigLacp_Lacp_Interfaces_Interface_Members_Member
    var err error

    if members == nil {
        ygot.BuildEmptyTree(members)
    }

    if ports_map,ok := TeamdJson["ports"].(map[string]interface{}); ok {
        for ifKey := range ports_map {
            if lacpMemberObj, ok = members.Member[ifKey]; !ok {
                lacpMemberObj, err = members.NewMember(ifKey)
                if err != nil {
                    log.Error("Creation of portchannel member subtree failed")
                    return err
                }
                ygot.BuildEmptyTree(lacpMemberObj)
            }
            err = _fillLacpMemberHelper(ports_map, ifKey, lacpMemberObj)
        }
    }

    return err
}

func populateLacpData(ifKey string, state *ocbinds.OpenconfigLacp_Lacp_Interfaces_Interface_State,
                                    members *ocbinds.OpenconfigLacp_Lacp_Interfaces_Interface_Members) error {
    TeamdJson, err := getLacpData(ifKey)
    if err != nil {
        log.Error("Failure in getting LACP data " )
        return err
    }

    e := fillLacpState(TeamdJson, state)
    if e != nil {
        log.Error("Failure in filling LACP state data ")
        return e
    }

    er := fillLacpMembers(TeamdJson, members)
    if er != nil {
        log.Error("Failure in filling LACP members data ")
        return er
    }

    return nil
}

func populateLacpMembers(ifKey string, members *ocbinds.OpenconfigLacp_Lacp_Interfaces_Interface_Members) error {

    TeamdJson, err := getLacpData(ifKey)
    if err != nil {
        log.Errorf("Failure in getting LACP data %s\n", err)
        return err
    }

    e := fillLacpMembers(TeamdJson, members)
    if e != nil {
        log.Errorf("Failure in filling LACP members data %s\n", e)
        return e
    }

    return nil
}

func populateLacpMember(ifPoKey string, ifMemKey string, lacpMemberObj *ocbinds.OpenconfigLacp_Lacp_Interfaces_Interface_Members_Member) error {

    TeamdJson, err := getLacpData(ifPoKey)
    if err != nil {
        log.Errorf("Failure in getting LACP data %s\n", err)
        return err
    }

    e := fillLacpMember(TeamdJson, ifMemKey, lacpMemberObj)
    if e != nil {
        log.Errorf("Failure in filling LACP member data %s\n", e)
        return e
    }

    return nil
}

var DbToYang_lacp_get_xfmr  SubTreeXfmrDbToYang = func(inParams XfmrParams) error {

    lacpIntfsObj := getLacpRoot(inParams.ygRoot)
    var members *ocbinds.OpenconfigLacp_Lacp_Interfaces_Interface_Members
    var member *ocbinds.OpenconfigLacp_Lacp_Interfaces_Interface_Members_Member
    var lacpintfObj *ocbinds.OpenconfigLacp_Lacp_Interfaces_Interface
    var ok bool

    pathInfo := NewPathInfo(inParams.uri)
    ifKey := pathInfo.Var("name")
    ifMemKey := pathInfo.Var("interface")

    targetUriPath, err := getYangPathFromUri(pathInfo.Path)
    if err != nil {
        log.Warningf("Get Yang Path from URI failed")
        return err
    }

    log.Infof("Received GET for path: %s; template: %s vars: %v targetUriPath: %s ifKey: %s", pathInfo.Path, pathInfo.Template, pathInfo.Vars, targetUriPath, ifKey)

    if isSubtreeRequest(targetUriPath, "/openconfig-lacp:lacp/interfaces/interface/members/member") {
        if lacpintfObj, ok = lacpIntfsObj.Interfaces.Interface[ifKey]; !ok {
            errStr := "PortChannel Instance doesn't exist"
            log.Info(errStr)
            return errors.New(errStr)
        }

        members = lacpintfObj.Members
        if members != nil && ifMemKey != "" {
            if member, ok = members.Member[ifMemKey]; !ok {
                errStr := "PortChannel Member Instance doesn't exist"
                log.Info(errStr)
                return errors.New(errStr)
            }
            ygot.BuildEmptyTree(member)
            return populateLacpMember(ifKey, ifMemKey, member)
        }
    } else if isSubtreeRequest(targetUriPath, "/openconfig-lacp:lacp/interfaces/interface/members") {
        if lacpintfObj, ok = lacpIntfsObj.Interfaces.Interface[ifKey]; !ok {
            errStr := "PortChannel Instance doesn't exist"
            log.Info(errStr)
            return errors.New(errStr)
        }

        members = lacpintfObj.Members
        if members != nil && ifKey != "" {
            return populateLacpMembers(ifKey, members)
        }
    } else if isSubtreeRequest(targetUriPath, "/openconfig-lacp:lacp/interfaces/interface") {

        /* Request for a specific portchannel */
        if lacpIntfsObj.Interfaces.Interface != nil && len(lacpIntfsObj.Interfaces.Interface) > 0 && ifKey != "" {
            lacpintfObj, ok = lacpIntfsObj.Interfaces.Interface[ifKey]
            if !ok {
                lacpintfObj, _ = lacpIntfsObj.Interfaces.NewInterface(ifKey)
            }
             ygot.BuildEmptyTree(lacpintfObj)

             return populateLacpData(ifKey, lacpintfObj.State, lacpintfObj.Members)
        }
    } else if isSubtreeRequest(targetUriPath, "/openconfig-lacp:lacp/interfaces") {

        ygot.BuildEmptyTree(lacpIntfsObj)

        var lagTblTs = &db.TableSpec{Name: "LAG_TABLE"}
        var appDb = inParams.dbs[db.ApplDB]
        tbl, err := appDb.GetTable(lagTblTs)

        if err != nil {
            log.Error("App-DB get for list of portchannels failed!")
            return err
        }
        keys, _ := tbl.GetKeys()
        for _, key := range keys {
           ifKey := key.Get(0)

           lacpintfObj, ok = lacpIntfsObj.Interfaces.Interface[ifKey]
           if !ok {
              lacpintfObj, _ = lacpIntfsObj.Interfaces.NewInterface(ifKey)
           }
           ygot.BuildEmptyTree(lacpintfObj)

           populateLacpData(ifKey, lacpintfObj.State, lacpintfObj.Members)
        }
    } else {
        log.Info("Unsupported Path");
    }

    return nil

}

