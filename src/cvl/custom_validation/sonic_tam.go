////////////////////////////////////////////////////////////////////////////////
//                                                                            //
//  Copyright 2020 Broadcom. The term Broadcom refers to Broadcom Inc. and/or //
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
	"strings"
        "fmt"
	util "cvl/internal/util"
	)

//Validate if feature is enabled for Broadview features
func (t *CustomValidation) ValidateTAMFeature(vc *CustValidationCtxt) CVLErrorInfo {

        rclient := util.NewDbClient("APPL_DB")
	defer func() {
		if (rclient != nil) {
			rclient.Close()
		}
	}()

        if (rclient == nil) {
		return CVLErrorInfo{
			 ErrCode: CVL_SEMANTIC_ERROR,
			 TableName: "SWITCH_TABLE",
			 Keys: strings.Split(vc.CurCfg.Key, "|"),
			 ConstraintErrMsg: fmt.Sprintf("Failed to connect to APPL_DB"),
			 CVLErrDetails: "Config Validation Error",
			 ErrAppTag:  "capability-unsupported",
		}
        }

	switchData, err := rclient.HGetAll("SWITCH_TABLE:switch").Result()

	if (err != nil) {
		util.CVL_LEVEL_LOG(util.TRACE_SEMANTIC, "SWITCH_TABLE is empty or invalid argument")
		return CVLErrorInfo{
			 ErrCode: CVL_SEMANTIC_ERROR,
			 TableName: "SWITCH_TABLE",
			 Keys: strings.Split(vc.CurCfg.Key, "|"),
			 ConstraintErrMsg: fmt.Sprintf("Failed to get all fields of SWITCH_TABLE"),
			 CVLErrDetails: "Config Validation Error",
			 ErrAppTag:  "capability-unsupported",
		}
	}

	tsSupported, tsExists := switchData["tam_int_ifa_ts_supported"]
	ifaSupported, ifaExists := switchData["tam_int_ifa_supported"]
	modSupported, modExists := switchData["drop_monitor_supported"]

	switch  vc.YNodeName {
		case "TAM_INT_IFA_FEATURE_TABLE_LIST", "TAM_INT_IFA_FLOW_TABLE_LIST":
			if (ifaExists == false) || (ifaSupported == "False"){
				return CVLErrorInfo{
					 ErrCode: CVL_SEMANTIC_ERROR,
					 TableName: "SWITCH_TABLE",
					 Keys: strings.Split(vc.CurCfg.Key, "|"),
					 ConstraintErrMsg: fmt.Sprintf("IFA capability not supported"),
					 CVLErrDetails: "Config Validation Error",
					 ErrAppTag:  "ifa-capability-unsupported",
				}
			}
		case "TAM_INT_IFA_TS_FEATURE_TABLE_LIST" , "TAM_INT_IFA_TS_FLOW_TABLE_LIST":
			if (tsExists == false) || (tsSupported == "False") {
				return CVLErrorInfo{
					 ErrCode: CVL_SEMANTIC_ERROR,
					 TableName: "SWITCH_TABLE",
					 Keys: strings.Split(vc.CurCfg.Key, "|"),
					 ConstraintErrMsg: fmt.Sprintf("TailStamping capability not supported"),
					 CVLErrDetails: "Config Validation Error",
					 ErrAppTag:  "ts-capability-unsupported",
				}
			}
		case  "TAM_DROP_MONITOR_FEATURE_TABLE_LIST", "TAM_DROP_MONITOR_AGING_INTERVAL_TABLE_LIST" , "TAM_DROP_MONITOR_FLOW_TABLE_LIST": 
			if (modExists == false) || (modSupported == "False") {
				return CVLErrorInfo{
					 ErrCode: CVL_SEMANTIC_ERROR,
					 TableName: "SWITCH_TABLE",
					 Keys: strings.Split(vc.CurCfg.Key, "|"),
					 ConstraintErrMsg: fmt.Sprintf("Drop-Monitor capability not supported"),
					 CVLErrDetails: "Config Validation Error",
					 ErrAppTag:  "drop-monitor-capability-unsupported",
				}
			}
	}
 

	return CVLErrorInfo{ErrCode: CVL_SUCCESS}
}

