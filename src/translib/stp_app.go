///////////////////////////////////////////////////////////////////////
//
// Copyright 2019 Broadcom. All rights reserved.
// The term "Broadcom" refers to Broadcom Inc. and/or its subsidiaries.
//
///////////////////////////////////////////////////////////////////////

package translib

import (
	"errors"
	"reflect"
	"strconv"
	"strings"
	"translib/db"
	"translib/ocbinds"
	"translib/tlerr"

	"github.com/facette/natsort"
	log "github.com/golang/glog"
	"github.com/openconfig/ygot/util"
	"github.com/openconfig/ygot/ygot"
)

const (
	GLOBAL_TABLE            = "STP"
	VLAN_TABLE              = "STP_VLAN"
	VLAN_INTF_TABLE         = "STP_VLAN_INTF"
	INTF_TABLE              = "STP_INTF"
	VLAN_OPER_TABLE         = "_STP_VLAN_TABLE"
	VLAN_INTF_OPER_TABLE    = "_STP_VLAN_INTF_TABLE"
	INTF_OPER_TABLE         = "_STP_INTF_TABLE"
	STP_MODE                = "mode"
	OC_STP_APP_MODULE_NAME  = "/openconfig-spanning-tree:stp"
	OC_STP_YANG_PATH_PREFIX = "/device/stp"
	PVST_MAX_INSTANCES      = 255
)

type StpApp struct {
	pathInfo   *PathInfo
	ygotRoot   *ygot.GoStruct
	ygotTarget *interface{}

	globalTable    *db.TableSpec
	vlanTable      *db.TableSpec
	vlanIntfTable  *db.TableSpec
	interfaceTable *db.TableSpec

	vlanOperTable     *db.TableSpec
	vlanIntfOperTable *db.TableSpec
	intfOperTable     *db.TableSpec

	globalInfo       db.Value
	vlanTableMap     map[string]db.Value
	vlanIntfTableMap map[string]map[string]db.Value
	intfTableMap     map[string]db.Value

	vlanOperTableMap     map[string]db.Value
	vlanIntfOperTableMap map[string]map[string]db.Value
	intfOperTableMap     map[string]db.Value

	appDB *db.DB
}

func init() {
	err := register("/openconfig-spanning-tree:stp",
		&appInfo{appType: reflect.TypeOf(StpApp{}),
			ygotRootType:  reflect.TypeOf(ocbinds.OpenconfigSpanningTree_Stp{}),
			isNative:      false,
			tablesToWatch: []*db.TableSpec{&db.TableSpec{Name: GLOBAL_TABLE}, &db.TableSpec{Name: VLAN_TABLE}, &db.TableSpec{Name: VLAN_INTF_TABLE}, &db.TableSpec{Name: INTF_TABLE}}})

	if err != nil {
		log.Fatal("Register STP app module with App Interface failed with error=", err)
	}

	err = addModel(&ModelData{Name: "openconfig-spanning-tree", Org: "OpenConfig working group", Ver: "0.3.0"})
	if err != nil {
		log.Fatal("Adding model data to appinterface failed with error=", err)
	}
}

func (app *StpApp) initialize(data appData) {
	log.Info("initialize:stp:path =", data.path)
	app.pathInfo = NewPathInfo(data.path)
	app.ygotRoot = data.ygotRoot
	app.ygotTarget = data.ygotTarget

	app.globalTable = &db.TableSpec{Name: GLOBAL_TABLE}
	app.vlanTable = &db.TableSpec{Name: VLAN_TABLE}
	app.vlanIntfTable = &db.TableSpec{Name: VLAN_INTF_TABLE}
	app.interfaceTable = &db.TableSpec{Name: INTF_TABLE}

	app.vlanOperTable = &db.TableSpec{Name: VLAN_OPER_TABLE}
	app.vlanIntfOperTable = &db.TableSpec{Name: VLAN_INTF_OPER_TABLE}
	app.intfOperTable = &db.TableSpec{Name: INTF_OPER_TABLE}

	app.globalInfo = db.Value{Field: map[string]string{}}
	app.vlanTableMap = make(map[string]db.Value)
	app.intfTableMap = make(map[string]db.Value)
	app.vlanIntfTableMap = make(map[string]map[string]db.Value)

	app.vlanOperTableMap = make(map[string]db.Value)
	app.vlanIntfOperTableMap = make(map[string]map[string]db.Value)
	app.intfOperTableMap = make(map[string]db.Value)
}

func (app *StpApp) getAppRootObject() *ocbinds.OpenconfigSpanningTree_Stp {
	deviceObj := (*app.ygotRoot).(*ocbinds.Device)
	return deviceObj.Stp
}

func (app *StpApp) translateCreate(d *db.DB) ([]db.WatchKeys, error) {
	var err error
	var keys []db.WatchKeys
	log.Info("translateCreate:stp:path =", app.pathInfo.Template)

	keys, err = app.translateCRUCommon(d, CREATE)
	return keys, err
}

func (app *StpApp) translateUpdate(d *db.DB) ([]db.WatchKeys, error) {
	var err error
	var keys []db.WatchKeys
	log.Info("translateUpdate:stp:path =", app.pathInfo.Template)

	return keys, err
}

func (app *StpApp) translateReplace(d *db.DB) ([]db.WatchKeys, error) {
	var err error
	var keys []db.WatchKeys
	log.Info("translateReplace:stp:path =", app.pathInfo.Template)

	return keys, err
}

func (app *StpApp) translateDelete(d *db.DB) ([]db.WatchKeys, error) {
	var err error
	var keys []db.WatchKeys
	log.Info("translateDelete:stp:path =", app.pathInfo.Template)

	return keys, err
}

func (app *StpApp) translateGet(dbs [db.MaxDB]*db.DB) error {
	var err error
	log.Info("translateGet:stp:path =", app.pathInfo.Template)
	return err
}

func (app *StpApp) translateAction(dbs [db.MaxDB]*db.DB) error {
	err := errors.New("Not supported")
	return err
}

func (app *StpApp) translateSubscribe(dbs [db.MaxDB]*db.DB, path string) (*notificationOpts, *notificationInfo, error) {
	var err error
	return nil, nil, err
}

func (app *StpApp) processCreate(d *db.DB) (SetResponse, error) {
	var err error
	var resp SetResponse

	if err = app.processCommon(d, CREATE); err != nil {
		log.Error(err)
		resp = SetResponse{ErrSrc: AppErr}
	}
	return resp, err
}

func (app *StpApp) processUpdate(d *db.DB) (SetResponse, error) {
	var err error
	var resp SetResponse

	err = errors.New("Not Implemented")
	return resp, err
}

func (app *StpApp) processReplace(d *db.DB) (SetResponse, error) {
	var err error
	var resp SetResponse

	err = errors.New("Not Implemented")
	return resp, err
}

func (app *StpApp) processDelete(d *db.DB) (SetResponse, error) {
	var err error
	var resp SetResponse

	if err = app.processCommon(d, DELETE); err != nil {
		log.Error(err)
		resp = SetResponse{ErrSrc: AppErr}
	}
	return resp, err
}

func (app *StpApp) processGet(dbs [db.MaxDB]*db.DB) (GetResponse, error) {
	var err error
	var payload []byte

	app.appDB = dbs[db.ApplDB]

	configDb := dbs[db.ConfigDB]
	err = app.processCommon(configDb, GET)
	if err != nil {
		return GetResponse{Payload: payload, ErrSrc: AppErr}, err
	}

	payload, err = generateGetResponsePayload(app.pathInfo.Path, (*app.ygotRoot).(*ocbinds.Device), app.ygotTarget)
	if err != nil {
		return GetResponse{Payload: payload, ErrSrc: AppErr}, err
	}

	return GetResponse{Payload: payload}, err
}

func (app *StpApp) processAction(dbs [db.MaxDB]*db.DB) (ActionResponse, error) {
	var resp ActionResponse
	err := errors.New("Not implemented")

	return resp, err
}

func (app *StpApp) translateCRUCommon(d *db.DB, opcode int) ([]db.WatchKeys, error) {
	var err error
	var keys []db.WatchKeys
	log.Info("translateCRUCommon:STP:path =", app.pathInfo.Template)

	app.convertOCStpGlobalConfToInternal()
	app.convertOCPvstToInternal()
	app.convertOCRpvstConfToInternal()
	app.convertOCStpInterfacesToInternal()

	return keys, err
}

func (app *StpApp) processCommon(d *db.DB, opcode int) error {
	var err error
	var topmostPath bool = false
	stp := app.getAppRootObject()

	log.Infof("processCommon--Path Received: %s", app.pathInfo.Template)
	targetType := reflect.TypeOf(*app.ygotTarget)
	if !util.IsValueScalar(reflect.ValueOf(*app.ygotTarget)) && util.IsValuePtr(reflect.ValueOf(*app.ygotTarget)) {
		log.Infof("processCommon: Target object is a <%s> of Type: %s", targetType.Kind().String(), targetType.Elem().Name())
		if targetType.Elem().Name() == "OpenconfigSpanningTree_Stp" {
			topmostPath = true
		}
	}

	targetUriPath, _ := getYangPathFromUri(app.pathInfo.Path)
	log.Infof("processCommon -- isTopmostPath: %t and Uri: %s", topmostPath, targetUriPath)
	if isSubtreeRequest(app.pathInfo.Template, "/openconfig-spanning-tree:stp/global") {
		switch opcode {
		case CREATE:
			err = app.setStpGlobalConfigInDB(d)
			if err != nil {
				return err
			}
			err = app.enableStpForInterfaces(d)
			if err != nil {
				return err
			}
			err = app.enableStpForVlans(d)
		case REPLACE:
		case UPDATE:
		case DELETE:
		case GET:
			err = app.convertDBStpGlobalConfigToInternal(d)
			if err != nil {
				return err
			}
			ygot.BuildEmptyTree(stp)
			app.convertInternalToOCStpGlobalConfig(stp.Global)
		}
	} else if isSubtreeRequest(app.pathInfo.Template, "/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst") {
		mode, _ := app.getStpModeFromConfigDB(d)
		if mode != "pvst" {
			return tlerr.InvalidArgs("STP mode is configured as %s", mode)
		}
		if isSubtreeRequest(app.pathInfo.Template, "/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan{}") {
			for vlanId, _ := range stp.Pvst.Vlan {
				pvstVlan := stp.Pvst.Vlan[vlanId]
				vlanName := "Vlan" + strconv.Itoa(int(vlanId))
				if isSubtreeRequest(app.pathInfo.Template, "/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan{}/interfaces/interface{}") {
					// Subtree of one interface under a vlan
					for intfId, _ := range pvstVlan.Interfaces.Interface {
						pvstVlanIntf := pvstVlan.Interfaces.Interface[intfId]
						switch opcode {
						case CREATE:
							if *app.ygotTarget == pvstVlanIntf {
								err = app.setRpvstVlanInterfaceDataInDB(d, true)
							} else {
								err = app.setRpvstVlanInterfaceDataInDB(d, false)
							}
						case REPLACE:
						case UPDATE:
						case DELETE:
							if *app.ygotTarget == pvstVlanIntf {
								err = d.DeleteEntry(app.vlanIntfTable, asKey(vlanName, intfId))
							} else {
								//err = app.handleVlanInterfaceFieldsDeletion(d, vlanName, intfId)
							}
						case GET:
							err = app.convertDBRpvstVlanInterfaceToInternal(d, vlanName, intfId, asKey(vlanName, intfId))
							if err != nil {
								return err
							}
							ygot.BuildEmptyTree(pvstVlanIntf)
							app.convertInternalToOCPvstVlanInterface(vlanName, intfId, pvstVlan, pvstVlanIntf)
						}
					}
				} else {
					isInterfacesSubtree := isSubtreeRequest(app.pathInfo.Template, "/openconfig-spanning-tree:stp/openconfig-spanning-tree-ext:pvst/vlan{}/interfaces")
					switch opcode {
					case CREATE:
						if *app.ygotTarget == pvstVlan {
							log.Info("ygotTarget is pvstVlan")
							err = app.setRpvstVlanDataInDB(d, true)
							if err != nil {
								return err
							}
							err = app.setRpvstVlanInterfaceDataInDB(d, true)
						} else if isInterfacesSubtree {
							err = app.setRpvstVlanInterfaceDataInDB(d, true)
						} else {
							err = d.SetEntry(app.vlanTable, asKey(vlanName), app.vlanTableMap[vlanName])
						}
					case REPLACE:
					case UPDATE:
					case DELETE:
						if *app.ygotTarget == pvstVlan {
							err = d.DeleteKeys(app.vlanIntfTable, asKey(vlanName+TABLE_SEPARATOR+"*"))
							if err != nil {
								return err
							}
							err = d.DeleteEntry(app.vlanTable, asKey(vlanName))
						} else if isInterfacesSubtree {
							err = d.DeleteKeys(app.vlanIntfTable, asKey(vlanName+TABLE_SEPARATOR+"*"))
						} else {
							// handle deletion of individual fields
						}
					case GET:
						err = app.convertDBRpvstVlanConfigToInternal(d, asKey(vlanName))
						if err != nil {
							return err
						}
						ygot.BuildEmptyTree(pvstVlan)
						app.convertInternalToOCPvstVlan(vlanName, stp.Pvst, pvstVlan)
					}
				}
			}
		} else {
			// Handle top PVST
		}
	} else if isSubtreeRequest(app.pathInfo.Template, "/openconfig-spanning-tree:stp/rapid-pvst") {
		mode, _ := app.getStpModeFromConfigDB(d)
		if mode != "rpvst" {
			return tlerr.InvalidArgs("STP mode is configured as %s", mode)
		}
		if isSubtreeRequest(app.pathInfo.Template, "/openconfig-spanning-tree:stp/rapid-pvst/vlan{}") {
			for vlanId, _ := range stp.RapidPvst.Vlan {
				rpvstVlanConf := stp.RapidPvst.Vlan[vlanId]
				vlanName := "Vlan" + strconv.Itoa(int(vlanId))
				if isSubtreeRequest(app.pathInfo.Template, "/openconfig-spanning-tree:stp/rapid-pvst/vlan{}/interfaces/interface{}") {
					// Subtree of one interface under a vlan
					for intfId, _ := range rpvstVlanConf.Interfaces.Interface {
						rpvstVlanIntfConf := rpvstVlanConf.Interfaces.Interface[intfId]
						switch opcode {
						case CREATE:
							if *app.ygotTarget == rpvstVlanIntfConf {
								err = app.setRpvstVlanInterfaceDataInDB(d, true)
							} else {
								err = app.setRpvstVlanInterfaceDataInDB(d, false)
							}
						case REPLACE:
						case UPDATE:
						case DELETE:
							if *app.ygotTarget == rpvstVlanIntfConf {
								err = d.DeleteEntry(app.vlanIntfTable, asKey(vlanName, intfId))
							} else {
								//err = app.handleVlanInterfaceFieldsDeletion(d, vlanName, intfId)
							}
						case GET:
							err = app.convertDBRpvstVlanInterfaceToInternal(d, vlanName, intfId, asKey(vlanName, intfId))
							if err != nil {
								return err
							}
							ygot.BuildEmptyTree(rpvstVlanIntfConf)
							app.convertInternalToOCRpvstVlanInterface(vlanName, intfId, rpvstVlanConf, rpvstVlanIntfConf)
						}
					}
				} else {
					isInterfacesSubtree := isSubtreeRequest(app.pathInfo.Template, "/openconfig-spanning-tree:stp/rapid-pvst/vlan{}/interfaces")
					switch opcode {
					case CREATE:
						if *app.ygotTarget == rpvstVlanConf {
							err = app.setRpvstVlanDataInDB(d, true)
							if err != nil {
								return err
							}
							err = app.setRpvstVlanInterfaceDataInDB(d, true)
						} else if isInterfacesSubtree {
							err = app.setRpvstVlanInterfaceDataInDB(d, true)
						} else {
							err = d.SetEntry(app.vlanTable, asKey(vlanName), app.vlanTableMap[vlanName])
						}
					case REPLACE:
					case UPDATE:
					case DELETE:
						if *app.ygotTarget == rpvstVlanConf {
							err = d.DeleteKeys(app.vlanIntfTable, asKey(vlanName+TABLE_SEPARATOR+"*"))
							if err != nil {
								return err
							}
							err = d.DeleteEntry(app.vlanTable, asKey(vlanName))
						} else if isInterfacesSubtree {
							err = d.DeleteKeys(app.vlanIntfTable, asKey(vlanName+TABLE_SEPARATOR+"*"))
						} else {
							// handle deletion of individual fields
						}
					case GET:
						err = app.convertDBRpvstVlanConfigToInternal(d, asKey(vlanName))
						if err != nil {
							return err
						}
						ygot.BuildEmptyTree(rpvstVlanConf)
						app.convertInternalToOCRpvstVlanConfig(vlanName, stp.RapidPvst, rpvstVlanConf)
					}
				}
			}
		} else {
			// Handle both rapid-pvst and rapid-pvst/vlan
			err = app.processCommonRpvstVlanToplevelPath(d, stp, opcode)
		}
	} else if isSubtreeRequest(app.pathInfo.Template, "/openconfig-spanning-tree:stp/mstp") {
		mode, _ := app.getStpModeFromConfigDB(d)
		if mode != "mstp" {
			return tlerr.InvalidArgs("STP mode is configured as %s", mode)
		}
	} else if isSubtreeRequest(app.pathInfo.Template, "/openconfig-spanning-tree:stp/interfaces") {
		if isSubtreeRequest(app.pathInfo.Template, "/openconfig-spanning-tree:stp/interfaces/interface{}") {
			for intfId, _ := range stp.Interfaces.Interface {
				intfData := stp.Interfaces.Interface[intfId]
				switch opcode {
				case CREATE:
					if *app.ygotTarget == intfData {
						err = app.setStpInterfacesDataInDB(d, true)
					} else {
						err = app.setStpInterfacesDataInDB(d, false)
					}
				case REPLACE:
				case UPDATE:
				case DELETE:
					if *app.ygotTarget == intfData {
						err = d.DeleteEntry(app.interfaceTable, asKey(intfId))
					} else {
						//err = app.handleVlanInterfaceFieldsDeletion(d, vlanName, intfId)
					}
				case GET:
					err = app.convertDBStpInterfacesToInternal(d, asKey(intfId))
					if err != nil {
						return err
					}
					ygot.BuildEmptyTree(intfData)
					app.convertInternalToOCStpInterfaces(intfId, stp.Interfaces, intfData)
				}
			}
		} else {
		}
	} else if topmostPath {
		switch opcode {
		case CREATE:
		case DELETE:
			err = d.DeleteTable(app.vlanIntfTable)
			if err != nil {
				return err
			}
			err = d.DeleteTable(app.vlanTable)
			if err != nil {
				return err
			}
			err = d.DeleteTable(app.interfaceTable)
			if err != nil {
				return err
			}
			err = d.DeleteTable(app.globalTable)
		case GET:
			ygot.BuildEmptyTree(stp)
			//////////////////////
			ygot.BuildEmptyTree(stp.Global)
			err = app.convertDBStpGlobalConfigToInternal(d)
			if err != nil {
				return err
			}
			app.convertInternalToOCStpGlobalConfig(stp.Global)

			stpMode := (&app.globalInfo).Get(STP_MODE)
			switch stpMode {
			case "pvst":
				ygot.BuildEmptyTree(stp.Pvst)
				err = app.convertDBRpvstVlanConfigToInternal(d, db.Key{})
				if err != nil {
					return err
				}
				app.convertInternalToOCPvstVlan("", stp.Pvst, nil)
			case "rpvst":
				ygot.BuildEmptyTree(stp.RapidPvst)
				err = app.convertDBRpvstVlanConfigToInternal(d, db.Key{})
				if err != nil {
					return err
				}
				app.convertInternalToOCRpvstVlanConfig("", stp.RapidPvst, nil)
			case "mstp":
			}
			//////////////////////
			ygot.BuildEmptyTree(stp.Interfaces)
			err = app.convertDBStpInterfacesToInternal(d, db.Key{})
			if err != nil {
				return err
			}
			app.convertInternalToOCStpInterfaces("", stp.Interfaces, nil)
		}
	}

	return err
}

func (app *StpApp) processCommonRpvstVlanToplevelPath(d *db.DB, stp *ocbinds.OpenconfigSpanningTree_Stp, opcode int) error {
	var err error

	switch opcode {
	case CREATE:
	case REPLACE:
	case UPDATE:
	case DELETE:
	case GET:
	}

	return err
}

/////////////////    STP GLOBAL   //////////////////////
func (app *StpApp) setStpGlobalConfigInDB(d *db.DB) error {
	var err error

	err = d.CreateEntry(app.globalTable, asKey("GLOBAL"), app.globalInfo)

	return err
}

func (app *StpApp) convertOCStpGlobalConfToInternal() {
	stp := app.getAppRootObject()
	if stp != nil {
		if stp.Global != nil && stp.Global.Config != nil {
			if stp.Global.Config.BridgePriority != nil {
				(&app.globalInfo).Set("priority", strconv.Itoa(int(*stp.Global.Config.BridgePriority)))
			} else {
				(&app.globalInfo).Set("priority", "32768")
			}
			if stp.Global.Config.ForwardingDelay != nil {
				(&app.globalInfo).Set("forward_delay", strconv.Itoa(int(*stp.Global.Config.ForwardingDelay)))
			} else {
				(&app.globalInfo).Set("forward_delay", "15")
			}
			if stp.Global.Config.HelloTime != nil {
				(&app.globalInfo).Set("hello_time", strconv.Itoa(int(*stp.Global.Config.HelloTime)))
			} else {
				(&app.globalInfo).Set("hello_time", "2")
			}
			if stp.Global.Config.MaxAge != nil {
				(&app.globalInfo).Set("max_age", strconv.Itoa(int(*stp.Global.Config.MaxAge)))
			} else {
				(&app.globalInfo).Set("max_age", "20")
			}
			if stp.Global.Config.RootguardTimeout != nil {
				(&app.globalInfo).Set("rootguard_timeout", strconv.Itoa(int(*stp.Global.Config.RootguardTimeout)))
			} else {
				(&app.globalInfo).Set("rootguard_timeout", "30")
			}

			mode := app.convertOCStpModeToInternal(stp.Global.Config)
			if len(mode) > 0 {
				(&app.globalInfo).Set(STP_MODE, mode)
			}

			log.Infof("convertOCStpGlobalConfToInternal -- Internal Stp global config: %v", app.globalInfo)
		}
	}
}

func (app *StpApp) convertDBStpGlobalConfigToInternal(d *db.DB) error {
	var err error

	app.globalInfo, err = d.GetEntry(app.globalTable, asKey("GLOBAL"))
	if err != nil {
		return err
	}
	return err
}

func (app *StpApp) convertInternalToOCStpGlobalConfig(stpGlobal *ocbinds.OpenconfigSpanningTree_Stp_Global) {
	if stpGlobal != nil {
		var priority uint32
		var forDelay, helloTime, maxAge uint8
		var rootGTimeout uint16
		if stpGlobal.Config != nil {
			stpGlobal.Config.EnabledProtocol = app.convertInternalStpModeToOC((&app.globalInfo).Get(STP_MODE))

			var num uint64
			num, _ = strconv.ParseUint((&app.globalInfo).Get("priority"), 10, 32)
			priority = uint32(num)
			stpGlobal.Config.BridgePriority = &priority

			num, _ = strconv.ParseUint((&app.globalInfo).Get("forward_delay"), 10, 8)
			forDelay = uint8(num)
			stpGlobal.Config.ForwardingDelay = &forDelay

			num, _ = strconv.ParseUint((&app.globalInfo).Get("hello_time"), 10, 8)
			helloTime = uint8(num)
			stpGlobal.Config.HelloTime = &helloTime

			num, _ = strconv.ParseUint((&app.globalInfo).Get("max_age"), 10, 8)
			maxAge = uint8(num)
			stpGlobal.Config.MaxAge = &maxAge

			num, _ = strconv.ParseUint((&app.globalInfo).Get("rootguard_timeout"), 10, 16)
			rootGTimeout = uint16(num)
			stpGlobal.Config.RootguardTimeout = &rootGTimeout
		}
		if stpGlobal.State != nil {
			stpGlobal.State.EnabledProtocol = app.convertInternalStpModeToOC((&app.globalInfo).Get(STP_MODE))
			stpGlobal.State.BridgePriority = &priority
			stpGlobal.State.ForwardingDelay = &forDelay
			stpGlobal.State.HelloTime = &helloTime
			stpGlobal.State.MaxAge = &maxAge
			stpGlobal.State.RootguardTimeout = &rootGTimeout
		}
	}
}

/////////////////    RPVST //////////////////////
func (app *StpApp) convertOCRpvstConfToInternal() {
	stp := app.getAppRootObject()
	if stp != nil && stp.RapidPvst != nil && len(stp.RapidPvst.Vlan) > 0 {
		for vlanId, _ := range stp.RapidPvst.Vlan {
			vlanName := "Vlan" + strconv.Itoa(int(vlanId))
			app.vlanTableMap[vlanName] = db.Value{Field: map[string]string{}}
			rpvstVlanConf := stp.RapidPvst.Vlan[vlanId]
			if rpvstVlanConf.Config != nil {
				dbVal := app.vlanTableMap[vlanName]
				(&dbVal).Set("vlanid", strconv.Itoa(int(vlanId)))
				if rpvstVlanConf.Config.BridgePriority != nil {
					(&dbVal).Set("priority", strconv.Itoa(int(*rpvstVlanConf.Config.BridgePriority)))
				} else {
					(&dbVal).Set("priority", "32768")
				}
				if rpvstVlanConf.Config.ForwardingDelay != nil {
					(&dbVal).Set("forward_delay", strconv.Itoa(int(*rpvstVlanConf.Config.ForwardingDelay)))
				} else {
					(&dbVal).Set("forward_delay", "15")
				}
				if rpvstVlanConf.Config.HelloTime != nil {
					(&dbVal).Set("hello_time", strconv.Itoa(int(*rpvstVlanConf.Config.HelloTime)))
				} else {
					(&dbVal).Set("hello_time", "2")
				}
				if rpvstVlanConf.Config.MaxAge != nil {
					(&dbVal).Set("max_age", strconv.Itoa(int(*rpvstVlanConf.Config.MaxAge)))
				} else {
					(&dbVal).Set("max_age", "20")
				}
				if rpvstVlanConf.Config.SpanningTreeEnable != nil {
					if *rpvstVlanConf.Config.SpanningTreeEnable {
						(&dbVal).Set("enabled", "true")
					} else {
						(&dbVal).Set("enabled", "false")
					}
				} else {
					(&dbVal).Set("enabled", "false")
				}
			}
			if rpvstVlanConf.Interfaces != nil && len(rpvstVlanConf.Interfaces.Interface) > 0 {
				app.vlanIntfTableMap[vlanName] = make(map[string]db.Value)
				for intfId, _ := range rpvstVlanConf.Interfaces.Interface {
					rpvstVlanIntfConf := rpvstVlanConf.Interfaces.Interface[intfId]
					app.vlanIntfTableMap[vlanName][intfId] = db.Value{Field: map[string]string{}}
					if rpvstVlanIntfConf.Config != nil {
						dbVal := app.vlanIntfTableMap[vlanName][intfId]
						(&dbVal).Set("vlan-name", vlanName)
						(&dbVal).Set("ifname", intfId)
						if rpvstVlanIntfConf.Config.Cost != nil {
							(&dbVal).Set("path_cost", strconv.Itoa(int(*rpvstVlanIntfConf.Config.Cost)))
						} else {
							(&dbVal).Set("path_cost", "200")
						}
						if rpvstVlanIntfConf.Config.PortPriority != nil {
							(&dbVal).Set("priority", strconv.Itoa(int(*rpvstVlanIntfConf.Config.PortPriority)))
						} else {
							(&dbVal).Set("priority", "128")
						}
					}
				}
			}
		}
	}
}

func (app *StpApp) setRpvstVlanDataInDB(d *db.DB, createFlag bool) error {
	var err error
	for vlanName := range app.vlanTableMap {
		existingEntry, err := d.GetEntry(app.vlanTable, asKey(vlanName))
		if createFlag && existingEntry.IsPopulated() {
			return tlerr.AlreadyExists("Vlan %s already configured", vlanName)
		}
		if createFlag || (!createFlag && err != nil && !existingEntry.IsPopulated()) {
			err = d.CreateEntry(app.vlanTable, asKey(vlanName), app.vlanTableMap[vlanName])
		} else {
			if existingEntry.IsPopulated() {
				err = d.ModEntry(app.vlanTable, asKey(vlanName), app.vlanTableMap[vlanName])
			}
		}
	}
	return err
}

func (app *StpApp) setRpvstVlanInterfaceDataInDB(d *db.DB, createFlag bool) error {
	var err error
	for vlanName := range app.vlanIntfTableMap {
		for intfId := range app.vlanIntfTableMap[vlanName] {
			existingEntry, err := d.GetEntry(app.vlanIntfTable, asKey(vlanName, intfId))
			if createFlag && existingEntry.IsPopulated() {
				return tlerr.AlreadyExists("Interface %s already configured", intfId)
			}
			if createFlag || (!createFlag && err != nil && !existingEntry.IsPopulated()) {
				err = d.CreateEntry(app.vlanIntfTable, asKey(vlanName, intfId), app.vlanIntfTableMap[vlanName][intfId])
				log.Error(err)
			} else {
				if existingEntry.IsPopulated() {
					err = d.ModEntry(app.vlanIntfTable, asKey(vlanName, intfId), app.vlanIntfTableMap[vlanName][intfId])
				}
			}
		}
	}
	return err
}

func (app *StpApp) convertDBRpvstVlanConfigToInternal(d *db.DB, vlanKey db.Key) error {
	var err error
	if vlanKey.Len() > 0 {
		entry, err := d.GetEntry(app.vlanTable, vlanKey)
		if err != nil {
			return err
		}
		vlanName := vlanKey.Get(0)
		if entry.IsPopulated() {
			app.vlanTableMap[vlanName] = entry
			app.vlanIntfTableMap[vlanName] = make(map[string]db.Value)
			err = app.convertDBRpvstVlanInterfaceToInternal(d, vlanName, "", db.Key{})
			if err != nil {
				return err
			}
			// Collect operational info from application DB
			err = app.convertApplDBRpvstVlanToInternal(vlanName)
		} else {
			return tlerr.NotFound("Vlan %s is not configured", vlanName)
		}
	} else {
		tbl, err := d.GetTable(app.vlanTable)
		if err != nil {
			return err
		}
		keys, err := tbl.GetKeys()
		if err != nil {
			return err
		}
		for i, _ := range keys {
			app.convertDBRpvstVlanConfigToInternal(d, keys[i])
		}
	}

	return err
}

func (app *StpApp) convertInternalToOCRpvstVlanConfig(vlanName string, rpvst *ocbinds.OpenconfigSpanningTree_Stp_RapidPvst, rpvstVlanConf *ocbinds.OpenconfigSpanningTree_Stp_RapidPvst_Vlan) {
	if len(vlanName) > 0 {
		var num uint64
		if rpvstVlanData, ok := app.vlanTableMap[vlanName]; ok {
			if rpvstVlanConf != nil {
				vlanId, _ := strconv.Atoi(strings.Replace(vlanName, "Vlan", "", 1))
				vlan := uint16(vlanId)
				rpvstVlanConf.VlanId = &vlan
				rpvstVlanConf.Config.VlanId = &vlan
				rpvstVlanConf.State.VlanId = &vlan

				stpEnabled, _ := strconv.ParseBool((&rpvstVlanData).Get("enabled"))
				rpvstVlanConf.Config.SpanningTreeEnable = &stpEnabled
				//rpvstVlanConf.State.SpanningTreeEnable = &stpEnabled

				num, _ = strconv.ParseUint((&rpvstVlanData).Get("priority"), 10, 32)
				priority := uint32(num)
				rpvstVlanConf.Config.BridgePriority = &priority
				rpvstVlanConf.State.BridgePriority = &priority

				num, _ = strconv.ParseUint((&rpvstVlanData).Get("forward_delay"), 10, 8)
				forDelay := uint8(num)
				rpvstVlanConf.Config.ForwardingDelay = &forDelay

				num, _ = strconv.ParseUint((&rpvstVlanData).Get("hello_time"), 10, 8)
				helloTime := uint8(num)
				rpvstVlanConf.Config.HelloTime = &helloTime

				num, _ = strconv.ParseUint((&rpvstVlanData).Get("max_age"), 10, 8)
				maxAge := uint8(num)
				rpvstVlanConf.Config.MaxAge = &maxAge

				app.convertInternalToOCRpvstVlanInterface(vlanName, "", rpvstVlanConf, nil)
			}
		}

		// populate operational information
		//ygot.BuildEmptyTree(rpvstVlanConf.State)
		operDbVal := app.vlanOperTableMap[vlanName]
		if operDbVal.IsPopulated() && rpvstVlanConf != nil {
			num, _ = strconv.ParseUint((&operDbVal).Get("max_age"), 10, 8)
			opMaxAge := uint8(num)
			rpvstVlanConf.State.MaxAge = &opMaxAge

			num, _ = strconv.ParseUint((&operDbVal).Get("hello_time"), 10, 8)
			opHelloTime := uint8(num)
			rpvstVlanConf.State.HelloTime = &opHelloTime

			num, _ = strconv.ParseUint((&operDbVal).Get("forward_delay"), 10, 8)
			opForwardDelay := uint8(num)
			rpvstVlanConf.State.ForwardingDelay = &opForwardDelay

			num, _ = strconv.ParseUint((&operDbVal).Get("hold_time"), 10, 8)
			opHoldTime := uint8(num)
			rpvstVlanConf.State.HoldTime = &opHoldTime

			/*num, _ = strconv.ParseUint((&operDbVal).Get("root_max_age"), 10, 8)
			opRootMaxAge := uint8(num)
			rpvstVlanConf.State.RootMaxAge = &opRootMaxAge

			num, _ = strconv.ParseUint((&operDbVal).Get("root_hello_time"), 10, 8)
			opRootHelloTime := uint8(num)
			rpvstVlanConf.State.RootHelloTime = &opRootHelloTime

			num, _ = strconv.ParseUint((&operDbVal).Get("root_forward_delay"), 10, 8)
			opRootForwardDelay := uint8(num)
			rpvstVlanConf.State.RootForwardingDelay = &opRootForwardDelay  */

			num, _ = strconv.ParseUint((&operDbVal).Get("stp_instance"), 10, 16)
			opStpInstance := uint16(num)
			rpvstVlanConf.State.StpInstance = &opStpInstance

			num, _ = strconv.ParseUint((&operDbVal).Get("root_path_cost"), 10, 32)
			opRootCost := uint32(num)
			rpvstVlanConf.State.RootCost = &opRootCost

			num, _ = strconv.ParseUint((&operDbVal).Get("last_topology_change"), 10, 64)
			opLastTopologyChange := num
			rpvstVlanConf.State.LastTopologyChange = &opLastTopologyChange

			num, _ = strconv.ParseUint((&operDbVal).Get("topology_change_count"), 10, 64)
			opTopologyChanges := num
			rpvstVlanConf.State.TopologyChanges = &opTopologyChanges

			bridgeId := (&operDbVal).Get("bridge_id")
			rpvstVlanConf.State.BridgeAddress = &bridgeId

			desigRootAddr := (&operDbVal).Get("desig_bridge_id")
			rpvstVlanConf.State.DesignatedRootAddress = &desigRootAddr

			//rootPortStr := (&operDbVal).Get("root_port")
			//rpvstVlanConf.State.RootPort = &rootPortStr
		}
	} else {
		for vlanName := range app.vlanTableMap {
			vlanId, _ := strconv.Atoi(strings.Replace(vlanName, "Vlan", "", 1))
			vlan := uint16(vlanId)

			rpvstVlanConfPtr, _ := rpvst.NewVlan(vlan)
			ygot.BuildEmptyTree(rpvstVlanConfPtr)
			app.convertInternalToOCRpvstVlanConfig(vlanName, rpvst, rpvstVlanConfPtr)
		}
	}
}

func (app *StpApp) convertDBRpvstVlanInterfaceToInternal(d *db.DB, vlanName string, intfId string, vlanInterfaceKey db.Key) error {
	var err error
	if vlanInterfaceKey.Len() > 1 {
		rpvstVlanIntfConf, err := d.GetEntry(app.vlanIntfTable, asKey(vlanName, intfId))
		if err != nil {
			return err
		}
		if app.vlanIntfTableMap[vlanName] == nil {
			app.vlanIntfTableMap[vlanName] = make(map[string]db.Value)
		}
		app.vlanIntfTableMap[vlanName][intfId] = rpvstVlanIntfConf
		// Collect operational info from application DB
		err = app.convertApplDBRpvstVlanInterfaceToInternal(vlanName, intfId)
	} else {
		keys, err := d.GetKeys(app.vlanIntfTable)
		if err != nil {
			return err
		}
		for i, _ := range keys {
			if vlanName == keys[i].Get(0) {
				err = app.convertDBRpvstVlanInterfaceToInternal(d, vlanName, keys[i].Get(1), keys[i])
			}
		}
	}
	return err
}

func (app *StpApp) convertInternalToOCRpvstVlanInterface(vlanName string, intfId string, rpvstVlanConf *ocbinds.OpenconfigSpanningTree_Stp_RapidPvst_Vlan, rpvstVlanIntfConf *ocbinds.OpenconfigSpanningTree_Stp_RapidPvst_Vlan_Interfaces_Interface) {
	var num uint64

	if len(intfId) == 0 {
		for intf, _ := range app.vlanIntfTableMap[vlanName] {
			app.convertInternalToOCRpvstVlanInterface(vlanName, intf, rpvstVlanConf, rpvstVlanIntfConf)
		}
	} else {
		dbVal := app.vlanIntfTableMap[vlanName][intfId]

		if rpvstVlanIntfConf == nil {
			if rpvstVlanConf != nil {
				rpvstVlanIntfConf_, _ := rpvstVlanConf.Interfaces.NewInterface(intfId)
				rpvstVlanIntfConf = rpvstVlanIntfConf_
				ygot.BuildEmptyTree(rpvstVlanIntfConf)
			}
		}

		num, _ = strconv.ParseUint((&dbVal).Get("path_cost"), 10, 32)
		cost := uint32(num)
		rpvstVlanIntfConf.Config.Cost = &cost

		num, _ = strconv.ParseUint((&dbVal).Get("priority"), 10, 8)
		portPriority := uint8(num)
		rpvstVlanIntfConf.Config.PortPriority = &portPriority

		rpvstVlanIntfConf.Config.Name = &intfId

		// populate operational information
		ygot.BuildEmptyTree(rpvstVlanIntfConf.State)

		rpvstVlanIntfConf.State.Name = &intfId
		operDbVal := app.vlanIntfOperTableMap[vlanName][intfId]

		if operDbVal.IsPopulated() {
			num, _ = strconv.ParseUint((&operDbVal).Get("port_num"), 10, 16)
			opPortNum := uint16(num)
			rpvstVlanIntfConf.State.PortNum = &opPortNum

			num, _ = strconv.ParseUint((&operDbVal).Get("path_cost"), 10, 32)
			opcost := uint32(num)
			rpvstVlanIntfConf.State.Cost = &opcost

			num, _ = strconv.ParseUint((&operDbVal).Get("priority"), 10, 8)
			opPortPriority := uint8(num)
			rpvstVlanIntfConf.State.PortPriority = &opPortPriority

			num, _ = strconv.ParseUint((&operDbVal).Get("desig_cost"), 10, 32)
			opDesigCost := uint32(num)
			rpvstVlanIntfConf.State.DesignatedCost = &opDesigCost

			num, _ = strconv.ParseUint((&operDbVal).Get("desig_port"), 10, 16)
			opDesigPortNum := uint16(num)
			rpvstVlanIntfConf.State.DesignatedPortNum = &opDesigPortNum

			num, _ = strconv.ParseUint((&operDbVal).Get("root_guard_timer"), 10, 16)
			opRootGuardTimer := uint16(num)
			rpvstVlanIntfConf.State.RootGuardTimer = &opRootGuardTimer

			num, _ = strconv.ParseUint((&operDbVal).Get("fwd_transitions"), 10, 64)
			opFwtrans := num
			rpvstVlanIntfConf.State.ForwardTransisitions = &opFwtrans

			desigRootAddr := (&operDbVal).Get("desig_root")
			rpvstVlanIntfConf.State.DesignatedRootAddress = &desigRootAddr

			desigBridgeAddr := (&operDbVal).Get("desig_bridge")
			rpvstVlanIntfConf.State.DesignatedBridgeAddress = &desigBridgeAddr

			switch (&operDbVal).Get("port_state") {
			case "disabled":
				rpvstVlanIntfConf.State.PortState = ocbinds.OpenconfigSpanningTreeTypes_STP_PORT_STATE_DISABLED
			case "block":
				rpvstVlanIntfConf.State.PortState = ocbinds.OpenconfigSpanningTreeTypes_STP_PORT_STATE_BLOCKING
			case "listen":
				rpvstVlanIntfConf.State.PortState = ocbinds.OpenconfigSpanningTreeTypes_STP_PORT_STATE_LISTENING
			case "learn":
				rpvstVlanIntfConf.State.PortState = ocbinds.OpenconfigSpanningTreeTypes_STP_PORT_STATE_LEARNING
			case "forward":
				rpvstVlanIntfConf.State.PortState = ocbinds.OpenconfigSpanningTreeTypes_STP_PORT_STATE_FORWARDING
			}

			//Counters
			if rpvstVlanIntfConf.State.Counters != nil {
				num, _ = strconv.ParseUint((&operDbVal).Get("bpdu_sent"), 10, 64)
				opBpduSent := num
				rpvstVlanIntfConf.State.Counters.BpduSent = &opBpduSent

				num, _ = strconv.ParseUint((&operDbVal).Get("bpdu_received"), 10, 64)
				opBpduReceived := num
				rpvstVlanIntfConf.State.Counters.BpduReceived = &opBpduReceived

				num, _ = strconv.ParseUint((&operDbVal).Get("tcn_sent"), 10, 64)
				opTcnSent := num
				rpvstVlanIntfConf.State.Counters.TcnSent = &opTcnSent

				num, _ = strconv.ParseUint((&operDbVal).Get("tcn_received"), 10, 64)
				opTcnReceived := num
				rpvstVlanIntfConf.State.Counters.TcnReceived = &opTcnReceived
			}
		}
	}
}

///////////   PVST   //////////////////////
func (app *StpApp) convertOCPvstToInternal() {
	stp := app.getAppRootObject()
	if stp != nil && stp.Pvst != nil && len(stp.Pvst.Vlan) > 0 {
		for vlanId, _ := range stp.Pvst.Vlan {
			vlanName := "Vlan" + strconv.Itoa(int(vlanId))
			app.vlanTableMap[vlanName] = db.Value{Field: map[string]string{}}
			pvstVlan := stp.Pvst.Vlan[vlanId]
			if pvstVlan.Config != nil {
				dbVal := app.vlanTableMap[vlanName]
				(&dbVal).Set("vlanid", strconv.Itoa(int(vlanId)))
				if pvstVlan.Config.BridgePriority != nil {
					(&dbVal).Set("priority", strconv.Itoa(int(*pvstVlan.Config.BridgePriority)))
				} else {
					(&dbVal).Set("priority", "32768")
				}
				if pvstVlan.Config.ForwardingDelay != nil {
					(&dbVal).Set("forward_delay", strconv.Itoa(int(*pvstVlan.Config.ForwardingDelay)))
				} else {
					(&dbVal).Set("forward_delay", "15")
				}
				if pvstVlan.Config.HelloTime != nil {
					(&dbVal).Set("hello_time", strconv.Itoa(int(*pvstVlan.Config.HelloTime)))
				} else {
					(&dbVal).Set("hello_time", "2")
				}
				if pvstVlan.Config.MaxAge != nil {
					(&dbVal).Set("max_age", strconv.Itoa(int(*pvstVlan.Config.MaxAge)))
				} else {
					(&dbVal).Set("max_age", "20")
				}
				if pvstVlan.Config.SpanningTreeEnable != nil {
					if *pvstVlan.Config.SpanningTreeEnable {
						(&dbVal).Set("enabled", "true")
					} else {
						(&dbVal).Set("enabled", "false")
					}
				} else {
					(&dbVal).Set("enabled", "false")
				}
			}
			if pvstVlan.Interfaces != nil && len(pvstVlan.Interfaces.Interface) > 0 {
				app.vlanIntfTableMap[vlanName] = make(map[string]db.Value)
				for intfId, _ := range pvstVlan.Interfaces.Interface {
					pvstVlanIntf := pvstVlan.Interfaces.Interface[intfId]
					app.vlanIntfTableMap[vlanName][intfId] = db.Value{Field: map[string]string{}}
					if pvstVlanIntf.Config != nil {
						dbVal := app.vlanIntfTableMap[vlanName][intfId]
						(&dbVal).Set("vlan-name", vlanName)
						(&dbVal).Set("ifname", intfId)
						if pvstVlanIntf.Config.Cost != nil {
							(&dbVal).Set("path_cost", strconv.Itoa(int(*pvstVlanIntf.Config.Cost)))
						} else {
							(&dbVal).Set("path_cost", "200")
						}
						if pvstVlanIntf.Config.PortPriority != nil {
							(&dbVal).Set("priority", strconv.Itoa(int(*pvstVlanIntf.Config.PortPriority)))
						} else {
							(&dbVal).Set("priority", "128")
						}
					}
				}
			}
		}
	}
}

func (app *StpApp) convertInternalToOCPvstVlan(vlanName string, pvst *ocbinds.OpenconfigSpanningTree_Stp_Pvst, pvstVlan *ocbinds.OpenconfigSpanningTree_Stp_Pvst_Vlan) {
	if len(vlanName) > 0 {
		var num uint64
		if pvstVlanData, ok := app.vlanTableMap[vlanName]; ok {
			if pvstVlan != nil {
				vlanId, _ := strconv.Atoi(strings.Replace(vlanName, "Vlan", "", 1))
				vlan := uint16(vlanId)
				pvstVlan.VlanId = &vlan
				pvstVlan.Config.VlanId = &vlan
				pvstVlan.State.VlanId = &vlan

				stpEnabled, _ := strconv.ParseBool((&pvstVlanData).Get("enabled"))
				pvstVlan.Config.SpanningTreeEnable = &stpEnabled
				//pvstVlan.State.SpanningTreeEnable = &stpEnabled

				num, _ = strconv.ParseUint((&pvstVlanData).Get("priority"), 10, 32)
				priority := uint32(num)
				pvstVlan.Config.BridgePriority = &priority
				pvstVlan.State.BridgePriority = &priority

				num, _ = strconv.ParseUint((&pvstVlanData).Get("forward_delay"), 10, 8)
				forDelay := uint8(num)
				pvstVlan.Config.ForwardingDelay = &forDelay

				num, _ = strconv.ParseUint((&pvstVlanData).Get("hello_time"), 10, 8)
				helloTime := uint8(num)
				pvstVlan.Config.HelloTime = &helloTime

				num, _ = strconv.ParseUint((&pvstVlanData).Get("max_age"), 10, 8)
				maxAge := uint8(num)
				pvstVlan.Config.MaxAge = &maxAge

				app.convertInternalToOCPvstVlanInterface(vlanName, "", pvstVlan, nil)
			}
		}

		// populate operational information
		//ygot.BuildEmptyTree(pvstVlan.State)
		operDbVal := app.vlanOperTableMap[vlanName]
		if operDbVal.IsPopulated() && pvstVlan != nil {
			num, _ = strconv.ParseUint((&operDbVal).Get("max_age"), 10, 8)
			opMaxAge := uint8(num)
			pvstVlan.State.MaxAge = &opMaxAge

			num, _ = strconv.ParseUint((&operDbVal).Get("hello_time"), 10, 8)
			opHelloTime := uint8(num)
			pvstVlan.State.HelloTime = &opHelloTime

			num, _ = strconv.ParseUint((&operDbVal).Get("forward_delay"), 10, 8)
			opForwardDelay := uint8(num)
			pvstVlan.State.ForwardingDelay = &opForwardDelay

			num, _ = strconv.ParseUint((&operDbVal).Get("hold_time"), 10, 8)
			opHoldTime := uint8(num)
			pvstVlan.State.HoldTime = &opHoldTime

			/*num, _ = strconv.ParseUint((&operDbVal).Get("root_max_age"), 10, 8)
			opRootMaxAge := uint8(num)
			pvstVlan.State.RootMaxAge = &opRootMaxAge

			num, _ = strconv.ParseUint((&operDbVal).Get("root_hello_time"), 10, 8)
			opRootHelloTime := uint8(num)
			pvstVlan.State.RootHelloTime = &opRootHelloTime

			num, _ = strconv.ParseUint((&operDbVal).Get("root_forward_delay"), 10, 8)
			opRootForwardDelay := uint8(num)
			pvstVlan.State.RootForwardingDelay = &opRootForwardDelay  */

			num, _ = strconv.ParseUint((&operDbVal).Get("stp_instance"), 10, 16)
			opStpInstance := uint16(num)
			pvstVlan.State.StpInstance = &opStpInstance

			num, _ = strconv.ParseUint((&operDbVal).Get("root_path_cost"), 10, 32)
			opRootCost := uint32(num)
			pvstVlan.State.RootCost = &opRootCost

			num, _ = strconv.ParseUint((&operDbVal).Get("last_topology_change"), 10, 64)
			opLastTopologyChange := num
			pvstVlan.State.LastTopologyChange = &opLastTopologyChange

			num, _ = strconv.ParseUint((&operDbVal).Get("topology_change_count"), 10, 64)
			opTopologyChanges := num
			pvstVlan.State.TopologyChanges = &opTopologyChanges

			bridgeId := (&operDbVal).Get("bridge_id")
			pvstVlan.State.BridgeAddress = &bridgeId

			desigRootAddr := (&operDbVal).Get("desig_bridge_id")
			pvstVlan.State.DesignatedRootAddress = &desigRootAddr

			//rootPortStr := (&operDbVal).Get("root_port")
			//pvstVlan.State.RootPort = &rootPortStr
		}
	} else {
		for vlanName := range app.vlanTableMap {
			vlanId, _ := strconv.Atoi(strings.Replace(vlanName, "Vlan", "", 1))
			vlan := uint16(vlanId)

			pvstVlanPtr, _ := pvst.NewVlan(vlan)
			ygot.BuildEmptyTree(pvstVlanPtr)
			app.convertInternalToOCPvstVlan(vlanName, pvst, pvstVlanPtr)
		}
	}
}

func (app *StpApp) convertInternalToOCPvstVlanInterface(vlanName string, intfId string, pvstVlan *ocbinds.OpenconfigSpanningTree_Stp_Pvst_Vlan, pvstVlanIntf *ocbinds.OpenconfigSpanningTree_Stp_Pvst_Vlan_Interfaces_Interface) {
	var num uint64

	if len(intfId) == 0 {
		for intf, _ := range app.vlanIntfTableMap[vlanName] {
			app.convertInternalToOCPvstVlanInterface(vlanName, intf, pvstVlan, pvstVlanIntf)
		}
	} else {
		dbVal := app.vlanIntfTableMap[vlanName][intfId]

		if pvstVlanIntf == nil {
			if pvstVlan != nil {
				pvstVlanIntf_, _ := pvstVlan.Interfaces.NewInterface(intfId)
				pvstVlanIntf = pvstVlanIntf_
				ygot.BuildEmptyTree(pvstVlanIntf)
			}
		}

		num, _ = strconv.ParseUint((&dbVal).Get("path_cost"), 10, 32)
		cost := uint32(num)
		pvstVlanIntf.Config.Cost = &cost

		num, _ = strconv.ParseUint((&dbVal).Get("priority"), 10, 8)
		portPriority := uint8(num)
		pvstVlanIntf.Config.PortPriority = &portPriority

		pvstVlanIntf.Config.Name = &intfId

		// populate operational information
		ygot.BuildEmptyTree(pvstVlanIntf.State)

		pvstVlanIntf.State.Name = &intfId
		operDbVal := app.vlanIntfOperTableMap[vlanName][intfId]

		if operDbVal.IsPopulated() {
			num, _ = strconv.ParseUint((&operDbVal).Get("port_num"), 10, 16)
			opPortNum := uint16(num)
			pvstVlanIntf.State.PortNum = &opPortNum

			num, _ = strconv.ParseUint((&operDbVal).Get("path_cost"), 10, 32)
			opcost := uint32(num)
			pvstVlanIntf.State.Cost = &opcost

			num, _ = strconv.ParseUint((&operDbVal).Get("priority"), 10, 8)
			opPortPriority := uint8(num)
			pvstVlanIntf.State.PortPriority = &opPortPriority

			num, _ = strconv.ParseUint((&operDbVal).Get("desig_cost"), 10, 32)
			opDesigCost := uint32(num)
			pvstVlanIntf.State.DesignatedCost = &opDesigCost

			num, _ = strconv.ParseUint((&operDbVal).Get("desig_port"), 10, 16)
			opDesigPortNum := uint16(num)
			pvstVlanIntf.State.DesignatedPortNum = &opDesigPortNum

			num, _ = strconv.ParseUint((&operDbVal).Get("root_guard_timer"), 10, 16)
			opRootGuardTimer := uint16(num)
			pvstVlanIntf.State.RootGuardTimer = &opRootGuardTimer

			num, _ = strconv.ParseUint((&operDbVal).Get("fwd_transitions"), 10, 64)
			opFwtrans := num
			pvstVlanIntf.State.ForwardTransisitions = &opFwtrans

			desigRootAddr := (&operDbVal).Get("desig_root")
			pvstVlanIntf.State.DesignatedRootAddress = &desigRootAddr

			desigBridgeAddr := (&operDbVal).Get("desig_bridge")
			pvstVlanIntf.State.DesignatedBridgeAddress = &desigBridgeAddr

			switch (&operDbVal).Get("port_state") {
			case "disabled":
				pvstVlanIntf.State.PortState = ocbinds.OpenconfigSpanningTreeTypes_STP_PORT_STATE_DISABLED
			case "block":
				pvstVlanIntf.State.PortState = ocbinds.OpenconfigSpanningTreeTypes_STP_PORT_STATE_BLOCKING
			case "listen":
				pvstVlanIntf.State.PortState = ocbinds.OpenconfigSpanningTreeTypes_STP_PORT_STATE_LISTENING
			case "learn":
				pvstVlanIntf.State.PortState = ocbinds.OpenconfigSpanningTreeTypes_STP_PORT_STATE_LEARNING
			case "forward":
				pvstVlanIntf.State.PortState = ocbinds.OpenconfigSpanningTreeTypes_STP_PORT_STATE_FORWARDING
			}

			//Counters
			if pvstVlanIntf.State.Counters != nil {
				num, _ = strconv.ParseUint((&operDbVal).Get("bpdu_sent"), 10, 64)
				opBpduSent := num
				pvstVlanIntf.State.Counters.BpduSent = &opBpduSent

				num, _ = strconv.ParseUint((&operDbVal).Get("bpdu_received"), 10, 64)
				opBpduReceived := num
				pvstVlanIntf.State.Counters.BpduReceived = &opBpduReceived

				num, _ = strconv.ParseUint((&operDbVal).Get("tcn_sent"), 10, 64)
				opTcnSent := num
				pvstVlanIntf.State.Counters.TcnSent = &opTcnSent

				num, _ = strconv.ParseUint((&operDbVal).Get("tcn_received"), 10, 64)
				opTcnReceived := num
				pvstVlanIntf.State.Counters.TcnReceived = &opTcnReceived
			}
		}
	}
}

///////////  Interfaces   //////////
func (app *StpApp) convertOCStpInterfacesToInternal() {
	stp := app.getAppRootObject()
	if stp != nil && stp.Interfaces != nil && len(stp.Interfaces.Interface) > 0 {
		for intfId, _ := range stp.Interfaces.Interface {
			app.intfTableMap[intfId] = db.Value{Field: map[string]string{}}

			stpIntfConf := stp.Interfaces.Interface[intfId]
			if stpIntfConf.Config != nil {
				dbVal := app.intfTableMap[intfId]
				(&dbVal).Set("ifname", intfId)

				if stpIntfConf.Config.BpduGuard != nil {
					if *stpIntfConf.Config.BpduGuard == true {
						(&dbVal).Set("bpdu_guard", "true")
					} else {
						(&dbVal).Set("bpdu_guard", "false")
					}
				}

				if stpIntfConf.Config.BpduGuardPortShutdown != nil {
					if *stpIntfConf.Config.BpduGuardPortShutdown == true {
						(&dbVal).Set("bpdu_guard_do_disable", "true")
					} else {
						(&dbVal).Set("bpdu_guard_do_disable", "false")
					}
				}

				if stpIntfConf.Config.Portfast != nil {
					if *stpIntfConf.Config.Portfast == true {
						(&dbVal).Set("portfast", "true")
					} else {
						(&dbVal).Set("portfast", "false")
					}
				}

				if stpIntfConf.Config.UplinkFast != nil {
					if *stpIntfConf.Config.UplinkFast == true {
						(&dbVal).Set("uplink_fast", "true")
					} else {
						(&dbVal).Set("uplink_fast", "false")
					}
				}

				if stpIntfConf.Config.SpanningTreeEnable != nil {
					if *stpIntfConf.Config.SpanningTreeEnable == true {
						(&dbVal).Set("enabled", "true")
					} else {
						(&dbVal).Set("enabled", "false")
					}
				}

				if stpIntfConf.Config.Cost != nil {
					(&dbVal).Set("path_cost", strconv.Itoa(int(*stpIntfConf.Config.Cost)))
				} else {
					//(&dbVal).Set("path_cost", "200")
				}
				if stpIntfConf.Config.PortPriority != nil {
					(&dbVal).Set("priority", strconv.Itoa(int(*stpIntfConf.Config.PortPriority)))
				} else {
					//(&dbVal).Set("priority", "128")
				}

				if stpIntfConf.Config.Guard == ocbinds.OpenconfigSpanningTree_StpGuardType_ROOT {
					(&dbVal).Set("root_guard", "true")
				} else {
					//(&dbVal).Set("root_guard", "false")
				}
				////   For RPVST+   /////
				if stpIntfConf.Config.EdgePort == ocbinds.OpenconfigSpanningTreeTypes_STP_EDGE_PORT_EDGE_ENABLE {
					(&dbVal).Set("edge_port", "true")
				} else if stpIntfConf.Config.EdgePort == ocbinds.OpenconfigSpanningTreeTypes_STP_EDGE_PORT_EDGE_DISABLE {
					(&dbVal).Set("edge_port", "false")
				}

				if stpIntfConf.Config.LinkType == ocbinds.OpenconfigSpanningTree_StpLinkType_P2P {
					(&dbVal).Set("pt2pt_mac", "true")
				} else if stpIntfConf.Config.LinkType == ocbinds.OpenconfigSpanningTree_StpLinkType_SHARED {
					(&dbVal).Set("pt2pt_mac", "false")
				}
			}
		}
	}
}

func (app *StpApp) setStpInterfacesDataInDB(d *db.DB, createFlag bool) error {
	var err error
	for intfName := range app.intfTableMap {
		existingEntry, err := d.GetEntry(app.interfaceTable, asKey(intfName))
		if createFlag && existingEntry.IsPopulated() {
			return tlerr.AlreadyExists("Stp Interface %s already configured", intfName)
		}
		if createFlag || (!createFlag && err != nil && !existingEntry.IsPopulated()) {
			err = d.CreateEntry(app.interfaceTable, asKey(intfName), app.intfTableMap[intfName])
		} else {
			if existingEntry.IsPopulated() {
				err = d.ModEntry(app.interfaceTable, asKey(intfName), app.intfTableMap[intfName])
			}
		}
	}
	return err
}

func (app *StpApp) convertDBStpInterfacesToInternal(d *db.DB, intfKey db.Key) error {
	var err error
	if intfKey.Len() > 0 {
		entry, err := d.GetEntry(app.interfaceTable, intfKey)
		if err != nil {
			return err
		}
		intfName := intfKey.Get(0)
		if entry.IsPopulated() {
			app.intfTableMap[intfName] = entry
		} else {
			return tlerr.NotFound("STP interface %s is not configured", intfName)
		}
		err = app.convertApplDBStpInterfacesToInternal(intfName)
	} else {
		tbl, err := d.GetTable(app.interfaceTable)
		if err != nil {
			return err
		}
		keys, err := tbl.GetKeys()
		if err != nil {
			return err
		}
		for i, _ := range keys {
			app.convertDBStpInterfacesToInternal(d, keys[i])
		}
	}

	return err
}

func (app *StpApp) convertInternalToOCStpInterfaces(intfName string, interfaces *ocbinds.OpenconfigSpanningTree_Stp_Interfaces, intf *ocbinds.OpenconfigSpanningTree_Stp_Interfaces_Interface) {
	var err error
	if len(intfName) > 0 {
		if stpIntfData, ok := app.intfTableMap[intfName]; ok {
			if intf != nil {
				intf.Config.Name = &intfName
				intf.State.Name = &intfName

				stpEnabled, _ := strconv.ParseBool((&stpIntfData).Get("enabled"))
				intf.Config.SpanningTreeEnable = &stpEnabled
				intf.State.SpanningTreeEnable = &stpEnabled

				bpduGuardEnabled, _ := strconv.ParseBool((&stpIntfData).Get("bpdu_guard"))
				intf.Config.BpduGuard = &bpduGuardEnabled
				intf.State.BpduGuard = &bpduGuardEnabled

				bpduGuardPortShut, _ := strconv.ParseBool((&stpIntfData).Get("bpdu_guard_do_disable"))
				intf.Config.BpduGuardPortShutdown = &bpduGuardPortShut
				intf.State.BpduGuardPortShutdown = &bpduGuardPortShut

				uplinkFast, _ := strconv.ParseBool((&stpIntfData).Get("uplink_fast"))
				intf.Config.UplinkFast = &uplinkFast
				intf.State.UplinkFast = &uplinkFast

				portFast, _ := strconv.ParseBool((&stpIntfData).Get("portfast"))
				intf.Config.Portfast = &portFast

				rootGuardEnabled, _ := strconv.ParseBool((&stpIntfData).Get("root_guard"))
				if rootGuardEnabled {
					intf.Config.Guard = ocbinds.OpenconfigSpanningTree_StpGuardType_ROOT
					intf.State.Guard = ocbinds.OpenconfigSpanningTree_StpGuardType_ROOT
				} else {
					intf.Config.Guard = ocbinds.OpenconfigSpanningTree_StpGuardType_NONE
					intf.State.Guard = ocbinds.OpenconfigSpanningTree_StpGuardType_NONE
				}

				if edgePortEnabled, err := strconv.ParseBool((&stpIntfData).Get("edge_port")); err == nil {
					if edgePortEnabled {
						intf.Config.EdgePort = ocbinds.OpenconfigSpanningTreeTypes_STP_EDGE_PORT_EDGE_ENABLE
						intf.State.EdgePort = ocbinds.OpenconfigSpanningTreeTypes_STP_EDGE_PORT_EDGE_ENABLE
					} else {
						intf.Config.EdgePort = ocbinds.OpenconfigSpanningTreeTypes_STP_EDGE_PORT_EDGE_DISABLE
						intf.State.EdgePort = ocbinds.OpenconfigSpanningTreeTypes_STP_EDGE_PORT_EDGE_DISABLE
					}
				}

				if linkTypeEnabled, err := strconv.ParseBool((&stpIntfData).Get("pt2pt_mac")); err == nil {
					if linkTypeEnabled {
						intf.Config.LinkType = ocbinds.OpenconfigSpanningTree_StpLinkType_P2P
						intf.State.LinkType = ocbinds.OpenconfigSpanningTree_StpLinkType_P2P
					} else {
						intf.Config.LinkType = ocbinds.OpenconfigSpanningTree_StpLinkType_SHARED
						intf.State.LinkType = ocbinds.OpenconfigSpanningTree_StpLinkType_SHARED
					}
				}

				var num uint64
				if num, err = strconv.ParseUint((&stpIntfData).Get("priority"), 10, 8); err == nil {
					priority := uint8(num)
					intf.Config.PortPriority = &priority
					intf.State.PortPriority = &priority
				}

				if num, err = strconv.ParseUint((&stpIntfData).Get("path_cost"), 10, 32); err == nil {
					cost := uint32(num)
					intf.Config.Cost = &cost
					intf.State.Cost = &cost
				}
			}
		}

		operDbVal := app.intfOperTableMap[intfName]
		if operDbVal.IsPopulated() && intf != nil {
			var boolVal bool

			bpduGuardShut := (&operDbVal).Get("bpdu_guard_shutdown")
			if bpduGuardShut == "yes" {
				boolVal = true
			} else if bpduGuardShut == "no" {
				boolVal = false
			}
			intf.State.BpduGuardShutdown = &boolVal

			opPortfast := (&operDbVal).Get("port_fast")
			if opPortfast == "yes" {
				boolVal = true
			} else if opPortfast == "no" {
				boolVal = false
			}
			intf.State.Portfast = &boolVal
		}
	} else {
		for intfName := range app.intfTableMap {
			intfPtr, _ := interfaces.NewInterface(intfName)
			ygot.BuildEmptyTree(intfPtr)
			app.convertInternalToOCStpInterfaces(intfName, interfaces, intfPtr)
		}
	}
}

func (app *StpApp) convertApplDBRpvstVlanToInternal(vlanName string) error {
	var err error

	rpvstVlanOperState, err := app.appDB.GetEntry(app.vlanOperTable, asKey(vlanName))
	if err != nil {
		return err
	}
	app.vlanOperTableMap[vlanName] = rpvstVlanOperState

	return err
}

func (app *StpApp) convertApplDBRpvstVlanInterfaceToInternal(vlanName string, intfId string) error {
	var err error

	rpvstVlanIntfOperState, err := app.appDB.GetEntry(app.vlanIntfOperTable, asKey(vlanName, intfId))
	if err != nil {
		return err
	}
	if app.vlanIntfOperTableMap[vlanName] == nil {
		app.vlanIntfOperTableMap[vlanName] = make(map[string]db.Value)
	}
	app.vlanIntfOperTableMap[vlanName][intfId] = rpvstVlanIntfOperState

	return err
}

func (app *StpApp) convertApplDBStpInterfacesToInternal(intfId string) error {
	var err error

	intfOperState, err := app.appDB.GetEntry(app.intfOperTable, asKey(intfId))
	if err != nil {
		return err
	}
	app.intfOperTableMap[intfId] = intfOperState

	return err
}

func (app *StpApp) convertOCStpModeToInternal(config *ocbinds.OpenconfigSpanningTree_Stp_Global_Config) string {
	switch config.EnabledProtocol[0] {
	case ocbinds.OpenconfigSpanningTreeTypes_STP_PROTOCOL_MSTP:
		return "mstp"
	case ocbinds.OpenconfigSpanningTreeTypes_STP_PROTOCOL_PVST:
		return "pvst"
	case ocbinds.OpenconfigSpanningTreeTypes_STP_PROTOCOL_RAPID_PVST:
		return "rpvst"
	case ocbinds.OpenconfigSpanningTreeTypes_STP_PROTOCOL_RSTP:
		return "rstp"
	default:
		return ""
	}
}

func (app *StpApp) convertInternalStpModeToOC(mode string) []ocbinds.E_OpenconfigSpanningTreeTypes_STP_PROTOCOL {
	var stpModes []ocbinds.E_OpenconfigSpanningTreeTypes_STP_PROTOCOL
	if len(mode) > 0 {
		switch mode {
		case "pvst":
			stpModes = append(stpModes, ocbinds.OpenconfigSpanningTreeTypes_STP_PROTOCOL_PVST)
		case "rpvst":
			stpModes = append(stpModes, ocbinds.OpenconfigSpanningTreeTypes_STP_PROTOCOL_RAPID_PVST)
		case "mstp":
			stpModes = append(stpModes, ocbinds.OpenconfigSpanningTreeTypes_STP_PROTOCOL_MSTP)
		case "rstp":
			stpModes = append(stpModes, ocbinds.OpenconfigSpanningTreeTypes_STP_PROTOCOL_RSTP)
		}
	}
	return stpModes
}

func (app *StpApp) getStpModeFromConfigDB(d *db.DB) (string, error) {
	stpGlobalDbEntry, err := d.GetEntry(app.globalTable, asKey("GLOBAL"))
	if err != nil {
		return "", err
	}
	return (&stpGlobalDbEntry).Get(STP_MODE), nil
}

func (app *StpApp) getAllInterfacesFromVlanMemberTable(d *db.DB) ([]string, error) {
	var intfList []string

	keys, err := d.GetKeys(&db.TableSpec{Name: "VLAN_MEMBER"})
	if err != nil {
		return intfList, err
	}
	for i, _ := range keys {
		key := keys[i]
		if !contains(intfList, (&key).Get(1)) {
			intfList = append(intfList, (&key).Get(1))
		}
	}
	return intfList, err
}

func (app *StpApp) enableStpForInterfaces(d *db.DB) error {
	defaultDBValues := db.Value{Field: map[string]string{}}
	(&defaultDBValues).Set("enabled", "true")
	(&defaultDBValues).Set("root_guard", "false")
	(&defaultDBValues).Set("bpdu_guard", "false")
	(&defaultDBValues).Set("bpdu_guard_do_disable", "false")
	(&defaultDBValues).Set("portfast", "true")
	(&defaultDBValues).Set("uplink_fast", "false")

	intfList, err := app.getAllInterfacesFromVlanMemberTable(d)
	if err != nil {
		return err
	}

	portKeys, err := d.GetKeys(&db.TableSpec{Name: "PORT"})
	if err != nil {
		return err
	}
	for i, _ := range portKeys {
		portKey := portKeys[i]
		if contains(intfList, (&portKey).Get(0)) {
			d.CreateEntry(app.interfaceTable, portKey, defaultDBValues)
		}
	}

	// For portchannels
	portchKeys, err := d.GetKeys(&db.TableSpec{Name: "PORTCHANNEL"})
	if err != nil {
		return err
	}
	for i, _ := range portchKeys {
		portchKey := portchKeys[i]
		if contains(intfList, (&portchKey).Get(0)) {
			d.CreateEntry(app.interfaceTable, portchKey, defaultDBValues)
		}
	}
	return err
}

func (app *StpApp) enableStpForVlans(d *db.DB) error {
	stpGlobalVal := app.globalInfo
	fDelay := (&stpGlobalVal).Get("forward_delay")
	helloTime := (&stpGlobalVal).Get("hello_time")
	maxAge := (&stpGlobalVal).Get("max_age")
	priority := (&stpGlobalVal).Get("priority")

	vlanKeys, err := d.GetKeys(&db.TableSpec{Name: "VLAN"})
	if err != nil {
		return err
	}

	var vlanList []string
	for i, _ := range vlanKeys {
		vlanKey := vlanKeys[i]
		vlanList = append(vlanList, (&vlanKey).Get(0))
	}

	// Sort vlanList in natural order such that 'Vlan2' < 'Vlan10'
	natsort.Sort(vlanList)

	for i, _ := range vlanList {
		if i < PVST_MAX_INSTANCES {
			defaultDBValues := db.Value{Field: map[string]string{}}
			(&defaultDBValues).Set("enabled", "true")
			(&defaultDBValues).Set("forward_delay", fDelay)
			(&defaultDBValues).Set("hello_time", helloTime)
			(&defaultDBValues).Set("max_age", maxAge)
			(&defaultDBValues).Set("priority", priority)

			vlanId := strings.Replace(vlanList[i], "Vlan", "", 1)
			(&defaultDBValues).Set("vlanid", vlanId)
			d.CreateEntry(app.vlanTable, asKey(vlanList[i]), defaultDBValues)
		}
	}
	return err
}
