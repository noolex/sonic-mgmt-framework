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
	"errors"
	"github.com/openconfig/ygot/ygot"
	"translib/db"
)

func tblKeyDataGet(d *db.DB, ygRoot *ygot.GoStruct, oper int, uri string, requestUri string, xpath string, tbl string, keyName string, dbDataMap *map[db.DBNum]map[string]map[string]db.Value, resultMap map[int]map[db.DBNum]map[string]map[string]db.Value, txCache interface{}, cdb db.DBNum) ([]string, error) {
	var err error
	var dbs [db.MaxDB]*db.DB
	var tblList []string
	dbs[cdb] = d

	xfmrLogInfoAll("Get table data for  (\"%v\")", uri)
	if (xYangSpecMap[xpath].tableName != nil) && (len(*xYangSpecMap[xpath].tableName) > 0) {
		tblList = append(tblList, *xYangSpecMap[xpath].tableName)
	} else if xYangSpecMap[xpath].xfmrTbl != nil {
		xfmrTblFunc := *xYangSpecMap[xpath].xfmrTbl
		if len(xfmrTblFunc) > 0 {
			inParams := formXfmrInputRequest(d, dbs, cdb, ygRoot, uri, requestUri, oper, keyName, dbDataMap, nil, nil, txCache)
			tblList, err = xfmrTblHandlerFunc(xfmrTblFunc, inParams)
			if err != nil {
				return tblList, err
			}
		}
	}
	if tbl != "" {
		if !contains(tblList, tbl) {
			tblList = append(tblList, tbl)
		}
	}
	return tblList, err
}

func subTreeXfmrDelDataGet(d *db.DB, ygRoot *ygot.GoStruct, oper int, uri string, requestUri string, dbDataMap *map[db.DBNum]map[string]map[string]db.Value, txCache interface{}, cdb db.DBNum, spec *yangXpathInfo, chldSpec *yangXpathInfo, subTreeResMap *map[string]map[string]db.Value)  error {
	var dbs [db.MaxDB]*db.DB
	dbs[cdb]   = d

	xfmrLogInfoAll("Handle subtree for  (\"%v\")", uri)
	if (len(chldSpec.xfmrFunc) > 0) {
		if ((len(spec.xfmrFunc) == 0) || ((len(spec.xfmrFunc) > 0) && 
		(spec.xfmrFunc != chldSpec.xfmrFunc))) {
			inParams := formXfmrInputRequest(d, dbs, cdb, ygRoot, uri, requestUri, oper, "",
			                                 dbDataMap, nil, nil, txCache)
			retMap, err := xfmrHandler(inParams, chldSpec.xfmrFunc)
			if err != nil {
				xfmrLogInfoAll("Error returned by %v: %v", chldSpec.xfmrFunc, err)
				return err
			}
			mapCopy(*subTreeResMap, retMap)
		}
	} 
	return nil
}

func yangListDelData(d *db.DB, ygRoot *ygot.GoStruct, oper int, uri string, requestUri string, xpath string, dbDataMap *map[db.DBNum]map[string]map[string]db.Value, resultMap map[int]map[db.DBNum]map[string]map[string]db.Value, subTreeResMap *map[string]map[string]db.Value, subOpDataMap map[int]*RedisDbMap, txCache interface{}) error {
	var err error
	var dbs [db.MaxDB]*db.DB

	spec, ok := xYangSpecMap[xpath]
	if ok && (spec.dbIndex == db.ConfigDB) {
		var tblList []string
		cdb       := spec.dbIndex
		dbs[cdb]   = d
		dbOpts    := getDBOptions(cdb)
		separator := dbOpts.KeySeparator

		_, keyName, tbl, err := xpathKeyExtract(d, ygRoot, oper, uri, requestUri, subOpDataMap, txCache)
		if err != nil {
			return err
		}

		tblList, err = tblKeyDataGet(d, ygRoot, oper, uri, requestUri, xpath, tbl, keyName, dbDataMap,
		resultMap, txCache, cdb)
		if err != nil {
			return err
		}

		xfmrLogInfoAll("tblList(%v), tbl(%v), key(%v)  for uri (\"%v\")", tblList, tbl,  keyName, uri)
		for _, tbl := range(tblList) {
			curDbDataMap, ferr := fillDbDataMapForTbl(uri, xpath, tbl, keyName, cdb, dbs)
			if ((ferr == nil) && len(curDbDataMap) > 0) {
				mapCopy((*dbDataMap)[cdb], curDbDataMap[cdb])
			}
		}

		for _, tbl := range(tblList) {
			tblData, ok := (*dbDataMap)[cdb][tbl]
			if ok {
				for dbKey, _ := range tblData {
					_, curUri, kerr := dbKeyToYangDataConvert(uri, requestUri, xpath, dbKey, separator, txCache)
					if kerr != nil {
						continue
					}
					for yangChldName := range spec.yangEntry.Dir {
						chldXpath    := xpath+"/"+yangChldName
						chldUri      := curUri+"/"+yangChldName
						chldSpec, ok := xYangSpecMap[chldXpath]
						if (ok && (chldSpec.dbIndex == db.ConfigDB) && chldSpec.hasChildSubTree && 
						(chldSpec.yangEntry != nil)) {
							chldYangType := chldSpec.yangDataType
							if ((chldYangType == YANG_CONTAINER || chldYangType == YANG_LIST) &&
							    (len(chldSpec.xfmrFunc) > 0)) {
								err = subTreeXfmrDelDataGet(d, ygRoot, oper, chldUri, requestUri, dbDataMap,
								txCache, cdb, spec, chldSpec, subTreeResMap)
								if err != nil {
									return err
								}
							}
							if chldSpec.hasChildSubTree == true {
								if chldYangType == YANG_CONTAINER {
									err = yangContainerDelData(d, ygRoot, oper, chldUri, requestUri, chldXpath, 
									dbDataMap, resultMap, subTreeResMap, subOpDataMap, txCache)
									if err != nil {
										return err
									}
								} else if chldYangType == YANG_LIST {
									err = yangListDelData(d, ygRoot, oper, chldUri, requestUri, chldXpath,
									dbDataMap, resultMap, subTreeResMap, subOpDataMap, txCache)
									if err != nil {
										return err
									}
								}
							}
						}
					}
				}
			}
        }

    }
	return err
}

func yangContainerDelData(d *db.DB, ygRoot *ygot.GoStruct, oper int, uri string, requestUri string, xpath string, dbDataMap *map[db.DBNum]map[string]map[string]db.Value, resultMap map[int]map[db.DBNum]map[string]map[string]db.Value, subTreeResMap *map[string]map[string]db.Value, subOpDataMap map[int]*RedisDbMap, txCache interface{}) error {
	var err error
	var dbs [db.MaxDB]*db.DB
	spec, _ := xYangSpecMap[xpath]
	cdb     := spec.dbIndex
	dbs[cdb] = d

	xfmrLogInfoAll("Parse container for subtree-xfmr(\"%v\")", uri)
	for yangChldName := range spec.yangEntry.Dir {
		chldXpath    := xpath+"/"+yangChldName
		chldUri      := uri+"/"+yangChldName
		chldSpec, ok := xYangSpecMap[chldXpath]
		if (ok && (chldSpec.dbIndex == db.ConfigDB) && (chldSpec.yangEntry != nil)) {
			chldYangType := chldSpec.yangDataType
			if ((chldYangType == YANG_CONTAINER || chldYangType == YANG_LIST) && (len(chldSpec.xfmrFunc) > 0)) {
				err = subTreeXfmrDelDataGet(d, ygRoot, oper, chldUri, requestUri, dbDataMap,
				txCache, cdb, spec, chldSpec, subTreeResMap)
				if err != nil {
					return err
				}
			} 
			if xYangSpecMap[chldXpath].hasChildSubTree == true {
				if chldYangType == YANG_CONTAINER {
					err = yangContainerDelData(d, ygRoot, oper, chldUri, requestUri, chldXpath, dbDataMap, resultMap, subTreeResMap, subOpDataMap, txCache)
					if err != nil {
						return err
					}
				} else if chldYangType == YANG_LIST {
					err = yangListDelData(d, ygRoot, oper, chldUri, requestUri, chldXpath, dbDataMap, resultMap,  subTreeResMap, subOpDataMap, txCache)
					if err != nil {
						return err
					}
				}
			}
		}
	}
	return err
}

func allChildTblGetToDelete(d *db.DB, ygRoot *ygot.GoStruct, oper int, requestUri string, resultMap map[int]map[db.DBNum]map[string]map[string]db.Value, subOpDataMap map[int]*RedisDbMap, txCache interface{}) (map[string]map[string]db.Value, error) {
	var err error
	subTreeResMap := make(map[string]map[string]db.Value)
	xpath, _ := XfmrRemoveXPATHPredicates(requestUri)
	spec, ok := xYangSpecMap[xpath]

	if !ok {
		errStr := "Xpath not found in spec-map:" + xpath
		return subTreeResMap, errors.New(errStr)
	}

	dbDataMap := make(RedisDbMap)
	for i := db.ApplDB; i < db.MaxDB; i++ {
		dbDataMap[i] = make(map[string]map[string]db.Value)
	}

	xfmrLogInfoAll("Req-uri (\"%v\") has subtree-xfmr", requestUri)
	if ok && spec.yangEntry != nil {
		if (spec.yangDataType == YANG_LIST) {
			err = yangListDelData(d, ygRoot, oper, requestUri, requestUri, xpath, &dbDataMap, resultMap, &subTreeResMap, subOpDataMap, txCache)
			return subTreeResMap, err
		} else if (spec.yangDataType == YANG_CONTAINER) {
			err = yangContainerDelData(d, ygRoot, oper, requestUri, requestUri, xpath, &dbDataMap, resultMap, &subTreeResMap, subOpDataMap, txCache)
		}
	}
	return subTreeResMap, err
  }

