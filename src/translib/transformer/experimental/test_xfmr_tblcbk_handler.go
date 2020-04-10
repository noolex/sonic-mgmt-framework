////////////////////////////////////////////////////////////////////////////
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
    "errors"
    "translib/db"
)

func init() {
     XlateFuncBind("PORT_cascade_cfg_hdl", PORT_cascade_cfg_hdl)
     XlateFuncBind("INTERFACE_cascade_cfg_hdl", INTERFACE_cascade_cfg_hdl)
}


var PORT_cascade_cfg_hdl XfmrDbTblCbkMethod= func (inParams XfmrDbTblCbkParams) error {
    log.Infof("PORT_cascade_cfg_hdl call - Test *******")
    if inParams.tblName != "PORT" {
        errStr := "PORT_cascade_cfg_hdl Invalid Table : " + inParams.tblName
        log.Infof(errStr)
        return errors.New(errStr)
    }
    if _, ok := inParams.dbDataMap[db.ConfigDB]["PORT"][inParams.dbKey]; !ok {
        errStr := "PORT_cascade_cfg_hdl Invalid Table key: " + inParams.tblName + " " + inParams.dbKey
        log.Infof(errStr)
        return errors.New(errStr)
    }
    Entry  := inParams.dbDataMap[db.ConfigDB]["PORT"][inParams.dbKey]
    log.Infof("XfmrDbTblCbkMethod Received inParams %v , Entry - %v .", inParams, Entry)
    return nil
}


var INTERFACE_cascade_cfg_hdl XfmrDbTblCbkMethod = func (inParams XfmrDbTblCbkParams) error {
    log.Infof("INTERFACE_cascade_cfg_hdl call - Test *******")
    log.Infof("INTERFACE_cascade_cfg_hdl Received inParams %v ", inParams)
    if inParams.delDepDataMap != nil {
        dbMap := make(map[db.DBNum]map[string]map[string]db.Value)
        dbMap[db.ConfigDB] = make(map[string]map[string]db.Value)
        dbMap[db.ConfigDB]["INTERFACE"] = make(map[string]db.Value)
        m := make(map[string]string)
        value := db.Value{Field:m}
        dbMap[db.ConfigDB]["INTERFACE"][inParams.dbKey] = value

        inParams.delDepDataMap[DELETE] = &dbMap
    }
    return nil
}

