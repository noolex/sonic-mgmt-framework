package custom_validation

import (
    "net"
//    util "cvl/internal/util"
    "strings"
    log "github.com/golang/glog"

 )

//Purpose: Check correct for correct agent_id
//vc : Custom Validation Context
//Returns -  CVL Error object
func (t *CustomValidation) ValidateDpbConfigs(
       vc *CustValidationCtxt) CVLErrorInfo {

       log.Info("DpbValidateInterfaceConfigs operation: ", vc.CurCfg.VOp)
       if (vc.CurCfg.VOp == OP_DELETE) {
               return CVLErrorInfo{ErrCode: CVL_SUCCESS}
       }

       log.Info("DpbValidateInterfaceConfigs YNodeVal: ", vc.YNodeVal)

       /* check if input passed is found in ConfigDB PORT|* */
       tableKeys, err:= vc.RClient.Keys("PORT|*").Result()

       if (err != nil) || (vc.SessCache == nil) {
               log.Info("DpbValidateInterfaceConfigs PORT is empty or invalid argument")
               errStr := "ConfigDB PORT list is empty"
               return CVLErrorInfo{
                       ErrCode: CVL_SEMANTIC_ERROR,
                       TableName: "PORT",
                       CVLErrDetails : errStr,
                       ConstraintErrMsg : errStr,
               }
       }

       for _, dbKey := range tableKeys {
               tmp := strings.Replace(dbKey, "PORT|", "", 1)
               log.Info("DpbValidateInterfaceConfigs dbKey ", tmp)
               if (tmp == vc.YNodeVal) {
                       return CVLErrorInfo{ErrCode: CVL_SUCCESS}
                    /*errStr := "Invalid interface name"
                    return CVLErrorInfo{
                        ErrCode: CVL_SEMANTIC_ERROR,
                        TableName: "PORT",
                        CVLErrDetails : errStr,
                        ConstraintErrMsg : errStr,
                    }*/
               }
       }

       /* check if input passed is found in list of network interfaces (includes, network_if, mgmt_if, and loopback) */
       ifaces, err2 := net.Interfaces()
       if err2 != nil {
               log.Info("DpbValidateInterfaceConfigs Error getting network interfaces")
               errStr := "Error getting network interfaces"
               return CVLErrorInfo{
                       ErrCode: CVL_SEMANTIC_ERROR,
                       TableName: "PORT",
                       CVLErrDetails : errStr,
                       ConstraintErrMsg : errStr,
               }
       }
       for _, i := range ifaces {
               log.Info("DpbValidateInterfaceConfigs i.Name ", i.Name)
               if (i.Name == vc.YNodeVal) {
                       return CVLErrorInfo{ErrCode: CVL_SUCCESS}
               }
       }
       return CVLErrorInfo{ErrCode: CVL_SUCCESS}

}

