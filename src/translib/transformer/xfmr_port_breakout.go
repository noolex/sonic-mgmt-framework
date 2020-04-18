package transformer

import (
    "strconv"
    "cvl"
    "translib/db"
    "errors"
    "strings"
    "github.com/openconfig/ygot/ygot"
    log "github.com/golang/glog"
    "translib/ocbinds"
    "encoding/json"
    "fmt"
    "reflect"
)

var ocSpeedMap = map[ocbinds.E_OpenconfigIfEthernet_ETHERNET_SPEED] string {
    ocbinds.OpenconfigIfEthernet_ETHERNET_SPEED_SPEED_1GB: "1G",
    ocbinds.OpenconfigIfEthernet_ETHERNET_SPEED_SPEED_5GB: "5G",
    ocbinds.OpenconfigIfEthernet_ETHERNET_SPEED_SPEED_10GB: "10G",
    ocbinds.OpenconfigIfEthernet_ETHERNET_SPEED_SPEED_25GB: "25G",
    ocbinds.OpenconfigIfEthernet_ETHERNET_SPEED_SPEED_40GB: "40G",
    ocbinds.OpenconfigIfEthernet_ETHERNET_SPEED_SPEED_50GB: "50G",
    ocbinds.OpenconfigIfEthernet_ETHERNET_SPEED_SPEED_100GB: "100G",
}

/* Transformer specific functions */

func init () {
    XlateFuncBind("YangToDb_port_breakout_config_xfmr", YangToDb_port_breakout_config_xfmr)
    XlateFuncBind("DbToYang_port_breakout_config_xfmr", DbToYang_port_breakout_config_xfmr)
    XlateFuncBind("DbToYang_port_breakout_state_xfmr", DbToYang_port_breakout_state_xfmr)
    XlateFuncBind("rpc_breakout_dependencies", rpc_breakout_dependencies)
    parsePlatformJsonFile()
}


func getDpbRoot (s *ygot.GoStruct) (map[string]*ocbinds.OpenconfigPlatform_Components_Component) {
    deviceObj := (*s).(*ocbinds.Device)
    return deviceObj.Components.Component

}


var DbToYang_port_breakout_state_xfmr SubTreeXfmrDbToYang = func (inParams XfmrParams) (error) {

    pathInfo := NewPathInfo(inParams.uri)
    targetUriPath, err := getYangPathFromUri(pathInfo.Path)
    log.Info("TARGET URI PATH DPB:", targetUriPath)
    log.Warningf("===== DPB STATE %v =====", inParams)
    return err;
}

var DbToYang_port_breakout_config_xfmr SubTreeXfmrDbToYang = func (inParams XfmrParams) (error) {
    log.Info("TableXfmrFunc - Uri DPB-1: ", inParams.uri);
    pathInfo := NewPathInfo(inParams.uri)

    targetUriPath, err := getYangPathFromUri(pathInfo.Path)
    log.Info("TARGET URI PATH DPBO:", targetUriPath)
    log.Info("DPB PATH:", pathInfo.Path)
    log.Warningf("DPB  %v", inParams)
    platObj := getDpbRoot(inParams.ygRoot)
    if platObj == nil || len(platObj) < 1 {
        log.Info("DbToYang_port_breakout_config_xfmr: Empty component.")
        return errors.New("Interface is not specified")
    }
    ifName := pathInfo.Var("name")
    entry, dbErr := inParams.d.GetEntry(&db.TableSpec{Name:"BREAKOUT_CFG"}, db.Key{Comp: []string{ifName}})
    
    if dbErr != nil {
            log.Info("Failed to read DB entry, BREAKOUT_CFG|", ifName)
            return errors.New("No port breakout configured")
    }
    splitted_mode := strings.Split(entry.Get("brkout_mode"), "x")
    log.Info(" Splitted breakout mode: ", splitted_mode)
    channels, err := strconv.ParseUint(splitted_mode[0], 10, 8)
    if err != nil {
        return err
    }
    dpb_channels := uint8(channels)
    if _, ok := platObj[ifName]; !ok {
        return errors.New("Request not supported")
    }
    platObj[ifName].Port.BreakoutMode.Config.NumChannels = &dpb_channels

    for oc_speed, speed := range ocSpeedMap {
        if speed == splitted_mode[1] {
            platObj[ifName].Port.BreakoutMode.Config.ChannelSpeed = oc_speed
        }
    }

    log.Info("OUT param ", *platObj[ifName].Port.BreakoutMode.Config.NumChannels, "x", ocSpeedMap[platObj[ifName].Port.BreakoutMode.Config.ChannelSpeed])


    return err;

}
/* Breakout action, shutdown, remove dependent configs , remove ports, add ports */
func breakout_action (ifName string, from_mode string, to_mode string, inParams XfmrParams) error {
        var err error
        if to_mode == from_mode {
            log.Info("DPB no config change")
            err = errors.New("No change in port breakout mode")
        } else {

            curr_ports, err1 := getPorts(ifName, from_mode)
            err = err1
            if err == nil {
                ports, err2 := getPorts(ifName, to_mode)
                err = err2
                if err == nil {
                    isEqual := reflect.DeepEqual(curr_ports,ports)
                    if isEqual {
                         log.Info("No change in port breakout mode")
                         return nil
                    } else {
                        //1. shutdown ports.
                        err = shutdownPorts(inParams.d, curr_ports)
                    }
                }
                if err == nil {
                    //2. Clean-up dependent configurations. TODO, pending on API
                } 
                if err == nil {
                    //3. Remove ports
                    err = removePorts(inParams.d, curr_ports)
                } 

                if err == nil {
                     isPortRemoveCompleted(curr_ports)
                }
                if err == nil {
                    log.Info("PORTS DELETED: ", curr_ports)
                    //4. Add ports
                    err = addPorts(inParams.d, ports)
                }
            }
        }
        return err
}

var YangToDb_port_breakout_config_xfmr SubTreeXfmrYangToDb = func(inParams XfmrParams) (map[string]map[string]db.Value,error) {
    var err error
    dpbMap := make(map[string]map[string]db.Value)
    log.Info("TableXfmrFunc - inParams DPB: ", inParams);
    log.Warningf("DPB  %v", inParams)
    log.Info(" DPB URI: ", inParams.uri);
    log.Info(" DPB REQ URI: ", inParams.requestUri);
    log.Info(" DPB OPER: ", inParams.oper);
    log.Info(" DPB KEY: ", inParams.key);
    log.Info(" DPB PARAM: ", inParams.param);

    if len(inParams.key) > 0 {
        return dpbMap, nil
    }

    platObj := getDpbRoot(inParams.ygRoot)
    if platObj == nil || len(platObj) < 1 {
        log.Info("YangToDb_port_breakout_config_xfmr: Empty component.")
        return dpbMap, errors.New("Interface is not specified")
    }
    pathInfo := NewPathInfo(inParams.uri)
    ifName := pathInfo.Var("name")
    log.Warning("DPB  Path:", pathInfo)
    log.Warning("DPB  ifName : ", ifName)
    log.Warning("DPB  Platform Object : ", platObj[ifName])

    if ifName == "" {
        errStr := "Interface KEY not present"
        log.Info("YangToDb_port_breakout_config_xfmr : " + errStr)
        return dpbMap, errors.New(errStr)
    }

    tblName := "BREAKOUT_CFG"

    entry, dbErr := inParams.d.GetEntry(&db.TableSpec{Name:tblName}, db.Key{Comp: []string{ifName}})
    if dbErr != nil {
        log.Info("Failed to read DB entry, " + tblName + " " + ifName)
    } else {
        log.Info("Read DB entry, " + tblName + " " + ifName)
    }

    if inParams.oper == DELETE {
        log.Info("DEL breakout config " + tblName + " " + ifName)
        if entry.Has("brkout_mode") == false {
            log.Info("Port breakout config not present, " + tblName + " " + ifName)
        }
        if _, ok := dpbMap[tblName]; !ok {
            dpbMap[tblName] = make (map[string]db.Value)
        }
        m := make(map[string]string)
        data := db.Value{Field: m}
        data.Set("brkout_mode", "")
        dpbMap[tblName][ifName] = data
        dpb_entry, err := inParams.d.GetEntry(&db.TableSpec{Name:tblName}, db.Key{Comp: []string{ifName}})
        //Delete only when current config is non-default
        if err == nil {
            log.Info("CURRENT: ", dpb_entry)
            ports, err := getPorts(ifName, dpb_entry.Get("brkout_mode"))
            if err == nil {
                log.Info("PORTS TO BE DELETED: ", ports)
            }
            err = breakout_action(ifName, dpb_entry.Get("brkout_mode"), "", inParams)
        }   else    {
            log.Info("DPB no config change")
            err = errors.New("No change in port breakout mode")
        }

    } else {
        m := make(map[string]string)
        data := db.Value{Field: m}
        log.Info("IN param ", *platObj[ifName].Port.BreakoutMode.Config.NumChannels, "x", ocSpeedMap[platObj[ifName].Port.BreakoutMode.Config.ChannelSpeed])
        brkout_mode := fmt.Sprint(*platObj[ifName].Port.BreakoutMode.Config.NumChannels) +
                    "x" + ocSpeedMap[platObj[ifName].Port.BreakoutMode.Config.ChannelSpeed]
        log.Info("inParams.oper: ", inParams.oper)
        log.Info("inParams: ", inParams)
        data.Set("brkout_mode", brkout_mode)
        if _, ok := dpbMap[tblName]; !ok {
            dpbMap[tblName] = make (map[string]db.Value)
        } else {
            dpbMap[tblName] = make (map[string]db.Value)
        }
        
        dpb_entry, _ := inParams.d.GetEntry(&db.TableSpec{Name:tblName}, db.Key{Comp: []string{ifName}})
        log.Info("CURRENT: ", dpb_entry)
        err = breakout_action(ifName, dpb_entry.Get("brkout_mode"), brkout_mode, inParams)
        if err == nil {
            dpbMap[tblName][ifName] = data
            log.Info("Breakout success for  ", ifName)
        } else {
            log.Info("Breakout failed for  ", ifName)
        }
    }
    log.Info("DPB map ==>", dpbMap)
    return dpbMap, err
}
var rpc_breakout_dependencies RpcCallpoint = func(body []byte, dbs [db.MaxDB]*db.DB) ([]byte, error) {
    var err error
    var input map[string]interface{}
    err = json.Unmarshal(body, &input)
    if err != nil {
       log.Infof("UnMarshall Error %v\n", err)
       return nil, err
    }


    key := input["sonic-port-breakout:input"].(map[string]interface{})
    log.Info("KEY : ", key)

    var exec struct {
        Output struct {
            DepKeys []string `json:"keys"`
        } `json:"sonic-port-breakout:output"`
    }
    cvSess, _ := cvl.ValidationSessOpen()
    depConfigs := cvSess.GetDepDataForDelete(fmt.Sprintf("PORT|%v", key["ifname"]))
    for i, dep := range depConfigs {
        for key, depc := range dep.Entry {
            exec.Output.DepKeys = append(exec.Output.DepKeys , key)
            log.Info("Dep-",i," : ", dep.RefKey, "/", key, "entry: ", depc)
        }

    }

    result, err := json.Marshal(&exec)
    log.Info("RPC Result: ", result)
    cvl.ValidationSessClose(cvSess)
    return result, err

}
