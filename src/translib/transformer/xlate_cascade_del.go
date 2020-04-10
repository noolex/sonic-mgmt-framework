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
    log "github.com/golang/glog"
    //"errors"
    "strings"
    //"translib/tlerr"
    "translib/db"
    "cvl"
    "fmt"
)

func getDbTblCbkName(tableName string) string {
    return tableName + "_cascade_cfg_hdl"
}

func xfmrDbTblCbkHandler (inParams XfmrDbTblCbkParams, tableName string)  error {
    xfmrLogInfoAll("Received inParams %v xfmrDbTblCbkHandler function name %v", inParams, tableName)

    ret, err := XlateFuncCall(getDbTblCbkName(tableName), inParams)
    if err != nil {
        xfmrLogInfo("xfmrDbTblCbkHandler: %v failed.", getDbTblCbkName(tableName))
        return err
    }
    if ((ret != nil) && (len(ret)>0)) {
        if ret[0].Interface() != nil {
            err =  ret[0].Interface().(error)
            if err != nil {
                log.Warningf("Table callback method i(%v) returned error - %v.", getDbTblCbkName(tableName), err)
            }
        }
    }

    return err
}



func handleCascadeDelete(d *db.DB, dbDataMap map[int]map[db.DBNum]map[string]map[string]db.Value,  cascadeDelTbl [] string) error {
    xfmrLogInfo("handleCascadeDelete : %v, cascadeDelTbl : %v.", dbDataMap, cascadeDelTbl)

    var err error
    cvlSess, cvlRetSess := cvl.ValidationSessOpen()
    if cvlRetSess != cvl.CVL_SUCCESS {
        xfmrLogInfo("handleCascadeDelete : cvl.ValidationSessOpen failed.")
        err = fmt.Errorf("%v", "cvl.ValidationSessOpen failed")
        return err
    }
    defer cvl.ValidationSessClose(cvlSess)

    for operIndex, redisMap := range dbDataMap {
        if operIndex != DELETE {
            continue
        }
        for dbIndex, dbMap := range redisMap {
            if dbIndex != db.ConfigDB {
                continue
            }
            for tblIndex, tblMap := range dbMap {
                if !contains(cascadeDelTbl, tblIndex) {
                    continue
                } else {
                    for key, entry := range tblMap {
                        // need to generate key based on the db type as of now just considering configdb
                        // and using "|" as tablename and key seperator
                        depKey := tblIndex + "|" + key
                        depList := cvlSess.GetDepDataForDelete(depKey)
                        xfmrLogInfo("handleCascadeDelete : depKey : %v, depList- %v, entry : %v", depKey, depList, entry)
                        for depIndex, depEntry := range depList {
                            for depEntkey, depEntkeyInst := range depEntry.Entry {
                                depEntkeyList := strings.SplitN(depEntkey, "|", 2)
                                cbkHdlName := depEntkeyList[0] + "_cascade_cfg_hdl"
                                if IsXlateFuncBinded(cbkHdlName) == true {
                                    //handle callback for table call Table Call back method and consolidate the data
                                    inParams := formXfmrDbTblCbkParams(d, DELETE, depEntry.RefKey, depEntkeyList[0], depEntkeyList[1], depEntkeyInst, dbDataMap[DELETE])
                                    xfmrLogInfo("handleCascadeDelete CBKHDL present depIndex %v, inParams : %v ", depIndex, inParams)
                                    err = xfmrDbTblCbkHandler(inParams, depEntkeyList[0])
                                    if err == nil {
                                        for operIdx, operMap := range inParams.delDepDataMap {
                                            if _, ok := dbDataMap[operIdx]; !ok {
                                                dbDataMap[operIdx] = make(map[db.DBNum]map[string]map[string]db.Value)
                                            }
                                            for dbIndx, dbMap := range *operMap {
                                                if _, ok := dbDataMap[operIdx][dbIndx]; !ok {
                                                    dbDataMap[operIdx][dbIndx] = make(map[string]map[string]db.Value)
                                                }
                                                mapMerge(dbDataMap[operIdx][dbIndx], dbMap)
                                            }
                                        }
                                    } else {
                                        xfmrLogInfo("handleCascadeDelete - xfmrDbTblCbkHandler failed.")
                                    }
                                } else {
                                    if _, ok := dbDataMap[DELETE][db.ConfigDB][depEntkeyList[0]]; !ok {
                                        dbDataMap[DELETE][db.ConfigDB][depEntkeyList[0]] = make(map[string]db.Value)
                                    }
                                    if _, ok := dbDataMap[DELETE][db.ConfigDB][depEntkeyList[0]][depEntkeyList[1]]; !ok {
                                        dbDataMap[DELETE][db.ConfigDB][depEntkeyList[0]][depEntkeyList[1]] = db.Value{Field: make(map[string]string)}
                                    }

                                    if len(depEntkeyInst) > 0 {
                                        for depEntAttr, depEntAttrInst := range depEntkeyInst {
                                            if _, ok := dbDataMap[DELETE][db.ConfigDB][depEntkeyList[0]][depEntkeyList[1]].Field[depEntAttr]; !ok {
                                                dbDataMap[DELETE][db.ConfigDB][depEntkeyList[0]][depEntkeyList[1]].Field[depEntAttr] = ""
                                            }

                                            if len(depEntAttrInst) > 0 {
                                                val := dbDataMap[DELETE][db.ConfigDB][depEntkeyList[0]][depEntkeyList[1]]
                                                if strings.HasSuffix(depEntAttr, "@") {
                                                    valList := val.GetList(depEntAttr)
                                                    if !contains(valList, depEntAttrInst) {
                                                        valList = append(valList, depEntAttrInst)
                                                        val.SetList(depEntAttr, valList)
                                                    }
                                                } else {
                                                    val.Set(depEntAttr, depEntAttrInst)
                                                }

                                                dbDataMap[DELETE][db.ConfigDB][depEntkeyList[0]][depEntkeyList[1]] = val
                                            } else {
                                                var data db.Value
                                                data.Field[depEntAttr] = ""
                                                dbDataMap[DELETE][db.ConfigDB][depEntkeyList[0]][depEntkeyList[1]] = data
                                            }
                                        }
                                    } else {
                                        var data db.Value
                                        dbDataMap[DELETE][db.ConfigDB][depEntkeyList[0]][depEntkeyList[1]] = data
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    return nil
}

/*****
Test code once cvl api is ready we can drop it.


type CVLDepDataForDelete struct {
    RefKey string //Ref Key which is getting deleted
    Entry  map[string]map[string]string //Entry or key which should be deleted as a result
    //map["BGP_NEIGHBOR|Vrf1|Ethernet0"]: []
    //map["BGP_NEIGHBOR_AF|Vrf1|Ethernet0|Unicast"]:[]
    //map["MIRROR_SESSION|sess1"]:[] ---> delete entire entry
    //map["ACL_RULE|Acl1|Rule1"]:map[MIRROR_ACTION]: "" ---> delete field
    //map["ACL_TABLE|Acl1"]:map["ports@"]:"Ethernet0" ---> delete a particular value in leaf-list
}

func TestGetDepDataForDelete(redisKey string) ([]CVLDepDataForDelete)  { //Returns array of entries which should be deleted

    var depList [] CVLDepDataForDelete

    var lentry CVLDepDataForDelete
    lentry.RefKey = redisKey
    lentry.Entry = make( map[string]map[string]string)
    lentry.Entry["INTERFACE|Ethernet0"] = make(map[string]string)
    depList= append(depList, lentry)
    return depList
}
*****/

