////////////////////////////////////////////////////////////////////////////////
//                                                                            //
//  Copyright 2019 Broadcom. The term Broadcom refers to Broadcom Inc. and/or //
//  its subsidiaries.                                                         //
//                                                                            //
//  Licensed under the Apache License, Version 2.0 (the "License");           //
//  you may not use this file except in compliance with the License.          //
//  You may obtain a copy of the License at                                   //
//                                                                            //
//     http://www.apache.org/licenses/LICENSE-2.0                             //
//                                                                            //
//  Unless required by applicable law or agreed to in writing, software       //
//  distributed under the License is distributed on an "AS IS" BASIS,         //
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  //
//  See the License for the specific language governing permissions and       //
//  limitations under the License.                                            //
//                                                                            //
////////////////////////////////////////////////////////////////////////////////

package custom_validation

import (
	"github.com/go-redis/redis"
	"strings"
	"fmt"
	util "cvl/internal/util"
	)

type VxlanMap struct {
	vlanMap map[string]bool
	vniMap map[string]bool
	vniVrfMap map[string]string //vni->vrf map
}

func fetchVNIVrfMappingFromRedis(vc *CustValidationCtxt) {
	pVxlanMap := &VxlanMap{}
	pVxlanMap.vniVrfMap = make(map[string]string)
	vc.SessCache.Data = pVxlanMap

	//Get all VXLAN keys
	tableKeys, err:= vc.RClient.Keys("VRF|*").Result()

	if (err != nil) || (vc.SessCache == nil) {
		util.TRACE_LEVEL_LOG(util.TRACE_SEMANTIC, "VRF is empty or invalid argument")
		return
	}

	mCmd := map[string]*redis.SliceCmd{}
	//Get VNI data and store
	pipe := vc.RClient.Pipeline()
	for _, dbKey := range tableKeys {
		mCmd[dbKey] = pipe.HMGet(dbKey, "vni")
	}

	_, err = pipe.Exec()
	pipe.Close()

	for dbKey, val := range mCmd {
		res, err := val.Result()
		if (err != nil) || (len(res) != 1) || (res[0] == nil) || (res[0] == "") {
			continue
		}

		keyComp := strings.Split(dbKey, "|") //VRF|vrfname
		//Store data vniVrfMap from Redis
		if (len(keyComp) == 2) {
			pVxlanMap.vniVrfMap[res[0].(string)] = keyComp[1] //Store Vrf name only
		}
	}

}

func fetchVlanVNIMappingFromRedis(vc *CustValidationCtxt) {
	//Store map in the session
	pVxlanMap := &VxlanMap{}
	pVxlanMap.vlanMap = make(map[string]bool)
	pVxlanMap.vniMap = make(map[string]bool)
	vc.SessCache.Data = pVxlanMap

	//Get all VXLAN keys
	tableKeys, err:= vc.RClient.Keys("VXLAN_TUNNEL_MAP|*").Result()

	if (err != nil) || (vc.SessCache == nil) {
		util.TRACE_LEVEL_LOG(util.TRACE_SEMANTIC, "VXLAN_TUNNEL_MAP is empty or invalid argument")
		return
	}

	mCmd := map[string]*redis.SliceCmd{}
	//Get VLAN and VNI data, store
	pipe := vc.RClient.Pipeline()
	for _, dbKey := range tableKeys {
		mCmd[dbKey] = pipe.HMGet(dbKey, "vlan", "vni")
	}

	_, err = pipe.Exec()
	pipe.Close()

	for _, val := range mCmd {
		res, err := val.Result()
		if (err != nil || len(res) != 2) {
			continue
		}

		//Store data vlan-vni from Redis
		pVxlanMap.vlanMap[res[0].(string)] = true
		pVxlanMap.vniMap[res[1].(string)] = true
	}
}

//Validate unique vlan across all vlan-vni mappings
func (t *CustomValidation) ValidateUniqueVlan(vc *CustValidationCtxt) CVLErrorInfo {

	if (vc.CurCfg.VOp == OP_DELETE) {
		 return CVLErrorInfo{ErrCode: CVL_SUCCESS}
	}

	vlan, hasVlan := vc.CurCfg.Data["vlan"]
	if hasVlan == false {
		return CVLErrorInfo{ErrCode: CVL_SUCCESS}
	}

	if (vc.SessCache.Data == nil) {
		fetchVlanVNIMappingFromRedis(vc)
	}

	vxlanMap := (vc.SessCache.Data).(*VxlanMap)

	//Loop up in session cache, if the vlan is already used
	if _, exists := vxlanMap.vlanMap[vlan]; exists {
		return CVLErrorInfo{
			ErrCode: CVL_SEMANTIC_ERROR,
			TableName: "VXLAN_TUNNEL_MAP",
			Keys: strings.Split(vc.CurCfg.Key, "|"),
			ErrAppTag:  "not-unique-vlanid",
		}
	}

	//Mark that Vlan is already used
	vxlanMap.vlanMap[vlan] = true

	return CVLErrorInfo{ErrCode: CVL_SUCCESS}
}

//Validate unique vni across all vlan-vni mappings
func (t *CustomValidation) ValidateUniqueVNI(vc *CustValidationCtxt) CVLErrorInfo {
	if (vc.CurCfg.VOp == OP_DELETE) {
		 return CVLErrorInfo{ErrCode: CVL_SUCCESS}
	}

	vni, hasVni := vc.CurCfg.Data["vni"]
	if hasVni == false {
		return CVLErrorInfo{ErrCode: CVL_SUCCESS}
	}

	if (vc.SessCache.Data == nil) {
		fetchVlanVNIMappingFromRedis(vc)
	}

	vxlanMap := (vc.SessCache.Data).(*VxlanMap)

	//Loop up in session cache, if the VNI is already used
	if _, exists := vxlanMap.vniMap[vni]; exists {
		return CVLErrorInfo{
			ErrCode: CVL_SEMANTIC_ERROR,
			TableName: "VXLAN_TUNNEL_MAP",
			Keys: strings.Split(vc.CurCfg.Key, "|"),
			ErrAppTag:  "not-unique-vni",
		}
	}

	//Mark that VNI is already used
	vxlanMap.vniMap[vni] = true

	return CVLErrorInfo{ErrCode: CVL_SUCCESS}
}


func getVniFromVxlanMapEntry(vc *CustValidationCtxt) string {

	if (vc.YCur == nil) || (vc.YCur.FirstChild == nil) {
		return ""
	}

	for node := vc.YCur.FirstChild; node != nil; node = node.NextSibling {
		if (node.Data == "vni") && (node.FirstChild != nil) {
			return node.FirstChild.Data
		}
	}

	return ""
}

//Validate Vxlan Map entry delete
func (t *CustomValidation) ValidateVxlanMapDelete(vc *CustValidationCtxt) CVLErrorInfo {
	if (vc.CurCfg.VOp != OP_DELETE) {
		 return CVLErrorInfo{ErrCode: CVL_SUCCESS}
	}

	vni := ""
	if vni = getVniFromVxlanMapEntry(vc) ; vni == "" {
		return CVLErrorInfo{ErrCode: CVL_SUCCESS}
	}

	if (vc.SessCache.Data == nil) {
		fetchVNIVrfMappingFromRedis(vc)
	}

	pVxlanMap := (vc.SessCache.Data).(*VxlanMap)

	if vrf, exists := pVxlanMap.vniVrfMap[vni]; exists == true {
		return CVLErrorInfo{
			ErrCode: CVL_SEMANTIC_ERROR,
			TableName: "VXLAN_TUNNEL_MAP",
			Keys: strings.Split(vc.CurCfg.Key, "|"),
			ErrAppTag:  "vni-used-in-vrf",
			ConstraintErrMsg:  fmt.Sprintf("VXLAN tunnel map delete is not allowed as VNI is in use in VRF %s", vrf),
		}
	}

	return CVLErrorInfo{ErrCode: CVL_SUCCESS}
}

//Validate Vrf VNI mappings
//
func (t *CustomValidation) ValidateVrfVNI(vc *CustValidationCtxt) CVLErrorInfo {
	if (vc.CurCfg.VOp == OP_DELETE) {
		 return CVLErrorInfo{ErrCode: CVL_SUCCESS}
	}

	//Allow vni 0 for Update or create
	vni, hasVni := vc.CurCfg.Data["vni"]
	if (hasVni == false) || (vni == "0") {
		return CVLErrorInfo{ErrCode: CVL_SUCCESS}
	}

	keyArr := strings.Split(vc.CurCfg.Key, "|")
	if (len(keyArr) > 1) {
		keyArr = keyArr[1:]
	}

	if (vc.SessCache.Data == nil) {
		fetchVNIVrfMappingFromRedis(vc)
		pTmpVxlanMap := (vc.SessCache.Data).(*VxlanMap)

		fetchVlanVNIMappingFromRedis(vc)
		//merge VNIVrf mapping details
		pVxlanMap := (vc.SessCache.Data).(*VxlanMap)
		pVxlanMap.vniVrfMap = pTmpVxlanMap.vniVrfMap
		vc.SessCache.Data = pVxlanMap
	}

	pVxlanMap := (vc.SessCache.Data).(*VxlanMap)

	//Check if VNI is already configured in VRF
	for vni, vrf := range pVxlanMap.vniVrfMap {
		if (vrf == keyArr[0]) && (vni != "0") { // if vrf matches  and if vni is non-default
			return CVLErrorInfo{
				ErrCode: CVL_SEMANTIC_ERROR,
				TableName: "VRF",
				Keys: keyArr,
				ErrAppTag:  "vni-already-configured",
				ConstraintErrMsg:  fmt.Sprintf("VNI is already configured for VRF %s", vrf),
			}
		}
	}

	//Check if VNI is configured in VXLAN_TUNNEL_MAP
	if _, exists := pVxlanMap.vniMap[vni]; exists == false {
		return CVLErrorInfo{
			ErrCode: CVL_SEMANTIC_ERROR,
			TableName: "VRF",
			Keys: keyArr,
			ErrAppTag:  "vni-not-configured",
			ConstraintErrMsg:  fmt.Sprintf("VNI %s is not configured in VXLAN_TUNNEL_MAP table", vni),
		}
	}

	//Check if VNI is already used in other VRF
	if  vrf, exists := pVxlanMap.vniVrfMap[vni]; exists == true {
	    if (keyArr[0] != pVxlanMap.vniVrfMap[vni]) {
		return CVLErrorInfo{
			ErrCode: CVL_SEMANTIC_ERROR,
			TableName: "VRF",
			Keys: keyArr,
			ErrAppTag:  "vni-already-used-in-other-vrf",
			ConstraintErrMsg:  fmt.Sprintf("VNI is already used in VRF %s", vrf),
		}
	    }
	}

	return CVLErrorInfo{ErrCode: CVL_SUCCESS}
}
