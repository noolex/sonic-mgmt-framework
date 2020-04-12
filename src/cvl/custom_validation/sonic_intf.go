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
	util "cvl/internal/util"
	"fmt"
	"strings"
)

//Custom validation for Unnumbered interface
func (t *CustomValidation) ValidateIpv4UnnumIntf(vc *CustValidationCtxt) CVLErrorInfo {

	if vc.CurCfg.VOp == OP_DELETE {
		return CVLErrorInfo{ErrCode: CVL_SUCCESS}
	}

	if vc.YNodeVal == "" {
		return CVLErrorInfo{ErrCode: CVL_SUCCESS} //Allow empty value
	}

	keys := "LOOPBACK_INTERFACE|" + vc.YNodeVal + "|*"
	util.CVL_LEVEL_LOG(util.INFO, "Keys: %s", keys)
	tableKeys, err := vc.RClient.Keys(keys).Result()

	if err != nil {
		util.TRACE_LEVEL_LOG(util.TRACE_SEMANTIC, "LOOPBACK_INTERFACE is empty or invalid argument")
		return CVLErrorInfo{ErrCode: CVL_SUCCESS}
	}

	count := 0
	for _, dbKey := range tableKeys {
		if strings.Contains(dbKey, ".") {
			count++
		}
	}

	util.CVL_LEVEL_LOG(util.INFO, "Donor intf IP count: %d", count)
	if count > 1 {
		util.TRACE_LEVEL_LOG(util.TRACE_SEMANTIC, "Donor interface has multiple IPv4 address")
		return CVLErrorInfo{
			ErrCode:          CVL_SEMANTIC_ERROR,
			TableName:        "LOOPBACK_INTERFACE",
			Keys:             strings.Split(vc.CurCfg.Key, "|"),
			ConstraintErrMsg: fmt.Sprintf("Multiple IPv4 address configured on Donor interface. Cannot configure IP Unnumbered"),
			CVLErrDetails:    "Config Validation Error",
			ErrAppTag:        "donor-multi-ipv4-addr",
		}
	}

	return CVLErrorInfo{ErrCode: CVL_SUCCESS}
}

//Custom validation for MTU configuration on PortChannel
func (t *CustomValidation) ValidateMtuForPOMemberCount(vc *CustValidationCtxt) CVLErrorInfo {
	if vc.CurCfg.VOp == OP_DELETE {
		return CVLErrorInfo{ErrCode: CVL_SUCCESS}
	}
	keys := strings.Split(vc.CurCfg.Key, "|")
	if len(keys) > 0 {
		if "PORTCHANNEL" == keys[0] {
			poName := keys[1]
			poMembersKeys, err := vc.RClient.Keys("PORTCHANNEL_MEMBER|" + poName + "|*").Result()
			if err != nil {
				return CVLErrorInfo{ErrCode: CVL_SEMANTIC_KEY_NOT_EXIST}
			}

			_, hasMtu := vc.CurCfg.Data["mtu"]
			if hasMtu && len(poMembersKeys) > 0 {
				util.TRACE_LEVEL_LOG(util.TRACE_SEMANTIC, "MTU not allowed when portchannel members are configured")
				return CVLErrorInfo{
					ErrCode:          CVL_SEMANTIC_ERROR,
					TableName:        "PORTCHANNEL",
					Keys:             strings.Split(vc.CurCfg.Key, "|"),
					ConstraintErrMsg: fmt.Sprintf("Configuration not allowed when members are configured"),
					ErrAppTag:        "mtu-invalid",
				}
			}
		} else if "PORTCHANNEL_MEMBER" == keys[0] {
			poName := keys[1]
			intfName := keys[2]

			if vc.CurCfg.VOp == OP_CREATE {
				poData, err := vc.RClient.HGetAll("PORTCHANNEL|" + poName).Result()
				if err != nil {
					return CVLErrorInfo{ErrCode: CVL_SEMANTIC_KEY_NOT_EXIST}
				}
				intfData, err1 := vc.RClient.HGetAll("PORT|" + intfName).Result()
				if err1 != nil {
					return CVLErrorInfo{ErrCode: CVL_SEMANTIC_KEY_NOT_EXIST}
				}

				poMtu, hasPoMtu := poData["mtu"]
				intfMtu, _ := intfData["mtu"]
				util.TRACE_LEVEL_LOG(util.TRACE_SEMANTIC, "ValidateMtuForPOMemberCount: PO MTU=%v and Intf MTU=%v", poMtu, intfMtu)

				if hasPoMtu && poMtu != intfMtu {
					util.TRACE_LEVEL_LOG(util.TRACE_SEMANTIC, "Members can't be added to portchannel when member MTU not same as portchannel MTU")
					return CVLErrorInfo{
						ErrCode:          CVL_SEMANTIC_ERROR,
						TableName:        "PORTCHANNEL_MEMBER",
						Keys:             strings.Split(vc.CurCfg.Key, "|"),
						ConstraintErrMsg: fmt.Sprintf("Configuration not allowed when port MTU not same as portchannel MTU"),
						ErrAppTag:        "mtu-invalid",
					}
				}
			}
		} else if "PORT" == keys[0] {
			intfName := keys[1]
			poMembersKeys, _ := vc.RClient.Keys("PORTCHANNEL_MEMBER|*|" + intfName).Result()

			_, hasMtu := vc.CurCfg.Data["mtu"]
			if hasMtu && len(poMembersKeys) > 0 {
				util.TRACE_LEVEL_LOG(util.TRACE_SEMANTIC, "MTU not allowed when portchannel members are configured")
				return CVLErrorInfo{
					ErrCode:          CVL_SEMANTIC_ERROR,
					TableName:        "PORT",
					Keys:             strings.Split(vc.CurCfg.Key, "|"),
					ConstraintErrMsg: fmt.Sprintf("Configuration not allowed when port is member of Portchannel"),
					ErrAppTag:        "mtu-invalid",
				}
			}
		}
	}

	return CVLErrorInfo{ErrCode: CVL_SUCCESS}
}
