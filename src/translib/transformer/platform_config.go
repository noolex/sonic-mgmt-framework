package transformer

import (
    "strconv"
    "time"
    "translib/db"
    "errors"
    "strings"
    "github.com/openconfig/ygot/ygot"
    log "github.com/golang/glog"
    "translib/ocbinds"
    "io/ioutil"
    "encoding/json"
)

const (
    PLATFORM_JSON = "/usr/share/sonic/hwsku/platform.json"
    //PLATFORM_JSON = "/projects/csg_sonic/pk409742/repos/3.x/sonic-buildimage/device/accton/x86_64-accton_as7816_64x-r0/Accton-AS7816-64X/platform-dpb.json"
    DPB_OP_TIMEOUT = 60
)


type portProp struct {
    name string
    index string
    lanes string
    alias string
    valid_speeds string
    speed string
    oid string
}

var platConfigStr map[string]map[string]string
var portOidMap  map[string]string

/* Functions */

func init () {
    parsePlatformJsonFile();
}


func getPlatRoot (s *ygot.GoStruct) *ocbinds.OpenconfigPlatform_Components {
    deviceObj := (*s).(*ocbinds.Device)
    return deviceObj.Components
}


func decodePortParams(port_i string, mode string, subport int, entry map[string]string) (portProp, error) {
    var port_config portProp
    var dpb_index string
    var dpb_lanes string

    // Check if mode is supported.
    supported_modes := strings.Split(entry["breakout_modes"], ",")
    for _, mode_iter := range supported_modes {
        if strings.Contains(mode_iter, mode[2:len(mode)]) {
            pos := strings.Index(mode_iter, "G")
            if pos != -1 {
                speed,_ := strconv.Atoi(mode_iter[2:pos])
                port_config.valid_speeds = strconv.Itoa(speed*1000)
            } else {
                log.Error("MODES: ", mode_iter)
            }
            pos = strings.Index(mode_iter, "[")
            epos := strings.Index(mode_iter, "]")
            if pos != -1 && epos != -1 {
                speed,_ := strconv.Atoi(mode_iter[pos+1:epos-1])
                port_config.valid_speeds = port_config.valid_speeds + ", " + strconv.Itoa(speed*1000)
            }
        }
    }

    if len(port_config.valid_speeds) < 1 {
        log.Error("Invalid or unsupported breakout mode")
        return port_config, errors.New("Invalid or unsupported breakout mode")
    }

    lane_speed_map := map[string][]int{"1x100G":{4, 100000}, "1x40G":{4, 40000},"1x400G":{8, 400000},
                        "2x50G":{2, 50000}, "4x25G":{1, 25000}, "4x10G":{1, 10000}}
    indeces := strings.Split(entry["index"], ",")
    lanes := strings.Split(entry["lanes"], ",")
    lane_speed, ok := lane_speed_map[mode]
    if !ok {
        log.Error("Invalid or unsupported breakout mode", mode)
        return port_config, errors.New("Invalid or unsupported breakout mode")
    }
    start_lane := subport*lane_speed[0]
    end_lane := start_lane + lane_speed[0]
    dpb_index = indeces[subport]
    dpb_lanes = lanes[start_lane]
    for i := start_lane + 1; i < end_lane; i++ {
        dpb_lanes = dpb_lanes + "," + lanes[i]
    }
    base_port,_ := strconv.Atoi(strings.TrimLeft(port_i, "Ethernet"))
    port_config.name = "Ethernet"+strconv.Itoa(base_port+subport)
    port_config.alias = strings.Split(entry["alias_at_lanes"], ",")[subport]
    port_config.index = dpb_index
    port_config.lanes = dpb_lanes
    port_config.speed = strconv.Itoa(lane_speed_map[mode][1])
    if strings.HasPrefix(mode, "1x") {
        pos := strings.Index(port_config.alias, ":")
        if pos != -1 {
           port_config.alias =  port_config.alias[0:pos]
        }
    }
    log.Info("port_config: ", port_config)
    return port_config, nil
}

func getPorts (port_i string, mode string) ([]portProp, error) {
    var err error
    var ports []portProp

    // This error will get updated in success case.
    err = errors.New("Invalid breakout mode")
    if entry, ok := platConfigStr[port_i]; ok {
        // Default mode. DELETE/"no breakout" case
        if len(mode) == 0 {
            //mode =  strings.Split(entry["default_brkout_mode"],"[")[0]
            mode =  entry["default_brkout_mode"]
            if len(mode) == 0 {
                err = errors.New("Invalid default breakout mode")
                return ports, err
            }
            if strings.Contains(mode, "[") {
                mode =  mode[0:strings.Index(mode, "[")]
            }
            log.Info("Default to ", mode)
        }
        count,_ := strconv.Atoi(string(mode[0]))
        ports = make([]portProp, count)
        for i := 0; i < count; i++ {
            ports[i], err = decodePortParams(port_i, mode, i, entry )
        }

    } else {
            log.Info("Invalid interface/master port - ", mode)
            err = errors.New("Invalid interface/master port.")
    }

    return ports, err
}


func parsePlatformJsonFile () (error) {

    file, err := ioutil.ReadFile(PLATFORM_JSON)

    if nil != err {
        log.Error("Dynamic port breakout not supported");
        return err
    }

    platConfigStr = make(map[string]map[string]string)
    err = json.Unmarshal([]byte(file), &platConfigStr)
    return err
}


func shutdownPorts (d *db.DB, ports_i []portProp) (error) {
    var dbErr error

    m := make(map[string]string)
    value := db.Value{Field: m}
    value.Set("admin_status", "down")
    for _,  port := range ports_i {
        err := d.SetEntry(&db.TableSpec{Name:"PORT"}, db.Key{Comp: []string{port.name}}, value)
        if nil != err {
            dbErr := err
            log.Error("DPB: port shutdown failed for ", port.name, " Error ", dbErr)
        } else {
            log.Info("DPB: port shutdown success for ", port.name)
        }
    }
    time.Sleep(1 * time.Second)
    return dbErr;
}


func isPortRemoveCompleted( ports_i []portProp) (error) {
    var dbErr error
    var portsDeleted bool
    if len(portOidMap) < 1 {
        portOidMap = make(map[string]string)
        /* Get the port - oid mapping from counters db */
        d, err := db.NewDB(getDBOptions(db.CountersDB))
        if err != nil {
             log.Infof("DPB unable to connect to Counters DB, error %v", err)
             return err
        }
        OidInfMap,_  := getOidToIntfNameMap(d)
        for oid, port := range OidInfMap {
            portOidMap[port] = oid
        }
        log.Info("PORT OID Map:", portOidMap)
        defer d.DeleteDB()
    }
    d, err := db.NewDB(getDBOptions(db.AsicDB))
    if err != nil {
         log.Infof("DPB unable to connect to ASIC DB, error %v", err)
         return err
    }

    for wait:=0;wait<DPB_OP_TIMEOUT;wait++ {
        portsDeleted = true
        for _, port := range ports_i {
            if oid, ok := portOidMap[port.name]; ok {
                _, dbErr := d.GetEntry(&db.TableSpec{Name:"ASIC_DB"},
                    db.Key{Comp: []string{"ASIC_STATE:SAI_OBJECT_TYPE_PORT:" + oid}})
                if nil == dbErr {
                    log.Info("DPB: ", port.name, "remove in progress. retry ", wait+1)
                    portsDeleted = false
                }
            } else {
                log.Error("DPB: OID not found for ", port.name)
                portsDeleted = false
                return  errors.New("Port name to OID mapping failed")
            }
        }
        if !portsDeleted {
            time.Sleep(1 * time.Second)
        } else {
            break
        }
    }

    defer d.DeleteDB()
    if portsDeleted {
     dbErr = nil
    } else {
        dbErr = errors.New("Port remove timed out")
    }

    return dbErr
}

func removePorts (d *db.DB, ports_i []portProp) (error) {
    var dbErr error
    // Delete in reverse order, so that master port gets deleted last.
    for i := len(ports_i)-1; i >= 0; i-- {
        err := d.DeleteEntry(&db.TableSpec{Name:"PORT"}, db.Key{Comp: []string{ports_i[i].name}})
        if nil != err {
            dbErr := err
            log.Error("DPB: port remove failed for ", ports_i[i].name, " Error ", dbErr)
        } else {
            log.Info("DPB: port remove success for ", ports_i[i].name)
        }
        time.Sleep(1 * time.Second)
    }

    return dbErr;
}

func addPorts (d *db.DB, ports []portProp) (error) {
    var dbErr error
    m := make(map[string]string)
    value := db.Value{Field: m}
    value.Set("admin_status", "down")
    value.Set("mtu", "9100")

    for i := 0; i < len(ports); i++ {
        value.Set("index",ports[i].index)
        value.Set("lanes", ports[i].lanes)
        value.Set("alias", ports[i].alias)
        value.Set("speed", ports[i].speed)
        value.Set("valid_speeds", ports[i].valid_speeds)
        err := d.SetEntry(&db.TableSpec{Name:"PORT"}, db.Key{Comp: []string{ports[i].name}}, value)
        if nil != err {
            dbErr = err
            log.Error("DPB: port add failed for ", ports[i], " Error ", dbErr)
        } else {
            log.Info("DPB: port add success for ", ports[i])
        }
    }
    return dbErr;
}


