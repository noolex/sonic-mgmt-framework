
package transformer

import (
    "translib/ocbinds"
    "github.com/openconfig/ygot/ygot"
    "translib/db"
    //"strings"
    "strconv"
    log "github.com/golang/glog"
)


func init () {
     XlateFuncBind("YangToDb_fp_ports_sbt_xfmr", YangToDb_fp_ports_sbt_xfmr)
     XlateFuncBind("DbToYang_fp_ports_sbt_xfmr", DbToYang_fp_ports_sbt_xfmr)
}

func getCasDelRootObject (s *ygot.GoStruct) (*ocbinds.CascadeDelete_FpPorts) {
    deviceObj := (*s).(*ocbinds.Device)
    return deviceObj.FpPorts
}


var YangToDb_fp_ports_sbt_xfmr SubTreeXfmrYangToDb = func(inParams XfmrParams) (map[string]map[string]db.Value, error) {

    subOpMap := make(map[db.DBNum]map[string]map[string]db.Value)
    subOpMapCr := make(map[db.DBNum]map[string]map[string]db.Value)
    dbData :=  make(map[string]map[string]db.Value)
    dbDelMap := make(map[string]map[string]db.Value)
    dbCrMap := make(map[string]map[string]db.Value)
    var err error

    pathInfo := NewPathInfo(inParams.uri)
    log.Infof("YangToDb_fp_ports_sbt_xfmr CASCADE SubTreeXfmrYangToDb");
    log.Infof("YangToDb_fp_ports_sbt_xfmr : %v", inParams)

    fpIdStr := pathInfo.Var("fp-id")
    fpId, efp := strconv.Atoi(fpIdStr)
    log.Infof("YangToDb_fp_ports_sbt_xfmr fpIdStr %v, efp %v",fpIdStr, efp)

    log.Infof("YangToDb_fp_ports_sbt_xfmr fpId %v", fpId)
    fpPorts := getCasDelRootObject(inParams.ygRoot)
    brkmod := *fpPorts.FpPort[uint32(fpId)].BrkOut

    log.Infof("YangToDb_fp_ports_sbt_xfmr brkmod %v", brkmod)

    dbDelMap["PORT"] =  make(map[string]db.Value)
    dbCrMap["PORT"] = make(map[string]db.Value)
    //dbDelMap["INTERFACE"] = make(map[string]db.Value)
    dbCrMap["INTERFACE"] = make(map[string]db.Value)

    compName := "Ethernet" + strconv.Itoa(fpId)
    var subIntfList []string
    intfMap := make(map[string]db.Value)
    m := make(map[string]string)
    value := db.Value{Field: m}
    m["index"] = pathInfo.Var("fp-id")
    m["lanes"] = "25,26,27,28"
    //intfMap[compName] = value

    ln := 25
    for i:= 0; i < 4; i++ {
        sbIntf := "Ethernet20"  + strconv.Itoa(i)
        subIntfList = append(subIntfList,  sbIntf)
        n := make(map[string]string)
        v  := db.Value{Field:n}
        n["index"] =  pathInfo.Var("fp-id") +  "20" + strconv.Itoa(i)
        n["lanes"] = strconv.Itoa(ln + i)
        intfMap[sbIntf] = v
    }

    log.Infof("YangToDb_fp_ports_sbt_xfmr intfMap :%v,  subIntfList : %v", intfMap, subIntfList)

    if brkmod == true {
        mm := make(map[string]string)
        vv:= db.Value{Field: mm}
        dbDelMap["PORT"][compName] = vv
        for _, sub := range subIntfList {
            dbCrMap["PORT"][sub] = intfMap[sub]
            dbCrMap["INTERFACE"][sub] = db.Value{Field: make(map[string]string)}
            dbCrMap["INTERFACE"][sub].Field["NULL"] = "NULL"
        }
        log.Infof("YangToDb_fp_ports_sbt_xfmr  dbCrMap %v, dbDelMap %v", dbCrMap, dbDelMap)
    }else {
        for _, sub := range subIntfList {
            mm := make(map[string]string)
            vv:= db.Value{Field: mm}
            dbDelMap["PORT"][sub] = vv

        }
        //dbCrMap["PORT"][compName] = intfMap[compName]
        dbCrMap["PORT"][compName] = value
        dbCrMap["INTERFACE"][compName] = db.Value{Field: make(map[string]string)}
        dbCrMap["INTERFACE"][compName].Field["NULL"] = "NULL"
        log.Infof("YangToDb_fp_ports_sbt_xfmr  BRKMOD FALSE dbCrMap %v, dbDelMap %v", dbCrMap, dbDelMap)
    }

    subOpMap[db.ConfigDB] = dbDelMap
    inParams.subOpDataMap[DELETE] = &subOpMap
    subOpMapCr[db.ConfigDB] = dbCrMap
    inParams.subOpDataMap[CREATE] = &subOpMapCr
    *inParams.pCascadeDelTbl = append(*inParams.pCascadeDelTbl, "PORT")

    log.Infof("YangToDb_fp_ports_sbt_xfmr: CREATE : %v, DELETE %v", inParams.subOpDataMap[CREATE], inParams.subOpDataMap[DELETE])
    log.Infof("YangToDb_fp_ports_sbt_xfmr: inParams : %v", inParams)
    return dbData, err



}
var DbToYang_fp_ports_sbt_xfmr SubTreeXfmrDbToYang = func (inParams XfmrParams) (error) {
    pathInfo := NewPathInfo(inParams.uri)
    log.Infof("Received GET for  CASCADE SubTreeXfmrDbToYang Template: %s ,path: %s, vars: %v",
    pathInfo.Template, pathInfo.Path, pathInfo.Vars)
    return nil
}
