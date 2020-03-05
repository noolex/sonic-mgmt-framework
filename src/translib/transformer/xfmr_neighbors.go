//////////////////////////////////////////////////////////////////////////
//
// Copyright 2019 Dell, Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
//////////////////////////////////////////////////////////////////////////

package transformer

import (
    "strings"
    "github.com/openconfig/ygot/ygot"
    "translib/db"
    log "github.com/golang/glog"
    "translib/ocbinds"
    "encoding/json"
    "fmt"
    "os/exec"
    "bufio"
    "strconv"
)

func init () {
    XlateFuncBind("DbToYang_neigh_tbl_get_all_ipv4_xfmr", DbToYang_neigh_tbl_get_all_ipv4_xfmr)
    XlateFuncBind("DbToYang_neigh_tbl_get_all_ipv6_xfmr", DbToYang_neigh_tbl_get_all_ipv6_xfmr)
    XlateFuncBind("DbToYang_neigh_tbl_key_xfmr", DbToYang_neigh_tbl_key_xfmr)
    XlateFuncBind("YangToDb_neigh_tbl_key_xfmr", YangToDb_neigh_tbl_key_xfmr)
    XlateFuncBind("rpc_clear_neighbors", rpc_clear_neighbors)
}

const (
    NEIGH_IPv4_PREFIX = "/openconfig-interfaces:interfaces/interface/subinterfaces/subinterface/openconfig-if-ip:ipv4/neighbors"
    NEIGH_IPv4_PREFIX_IP = NEIGH_IPv4_PREFIX+"/neighbor"
    NEIGH_IPv4_PREFIX_STATE_IP = NEIGH_IPv4_PREFIX_IP+"/state/ip"
    NEIGH_IPv4_PREFIX_STATE_LL = NEIGH_IPv4_PREFIX_IP+"/state/link-layer-address"
    NEIGH_IPv6_PREFIX = "/openconfig-interfaces:interfaces/interface/subinterfaces/subinterface/openconfig-if-ip:ipv6/neighbors"
    NEIGH_IPv6_PREFIX_IP = NEIGH_IPv6_PREFIX+"/neighbor"
    NEIGH_IPv6_PREFIX_STATE_IP = NEIGH_IPv6_PREFIX_IP+"/state/ip"
    NEIGH_IPv6_PREFIX_STATE_LL = NEIGH_IPv6_PREFIX_IP+"/state/link-layer-address"
)

var YangToDb_neigh_tbl_key_xfmr KeyXfmrYangToDb = func(inParams XfmrParams) (string, error) {
    var neightbl_key string
    var err error

    log.Info("YangToDb_neigh_tbl_key_xfmr - inParams: ", inParams)
    pathInfo := NewPathInfo(inParams.uri)
    intfName := pathInfo.Var("name")
    ipAddr := pathInfo.Var("ip")

    neightbl_key = intfName + ":" +  ipAddr
    log.Info("YangToDb_neigh_tbl_key_xfmr - key returned: ", neightbl_key)

    return neightbl_key, err
}

var DbToYang_neigh_tbl_key_xfmr KeyXfmrDbToYang = func(inParams XfmrParams) (map[string]interface{}, error) {
    rmap := make(map[string]interface{})
    var err error

    log.Info("DbToYang_neigh_tbl_key_xfmr - inParams: ", inParams)
    mykey := strings.Split(inParams.key,":")

    rmap["ip"] =  inParams.key[(len(mykey[0])+1):]
    return rmap, err
}


var DbToYang_neigh_tbl_get_all_ipv4_xfmr SubTreeXfmrDbToYang = func (inParams XfmrParams) (error) {
    var err error
    var ok bool

    data := (*inParams.dbDataMap)[inParams.curDb]
    log.Info("DbToYang_neigh_tbl_get_all_ipv4_xfmr - data:", data)
    pathInfo := NewPathInfo(inParams.uri)
    targetUriPath, err := getYangPathFromUri(pathInfo.Path)
    log.Info("DbToYang_neigh_tbl_get_all_ipv4_xfmr - targetUriPath: ", targetUriPath)

    var intfObj *ocbinds.OpenconfigInterfaces_Interfaces_Interface
    var subIntfObj *ocbinds.OpenconfigInterfaces_Interfaces_Interface_Subinterfaces_Subinterface
    var neighObj *ocbinds.OpenconfigInterfaces_Interfaces_Interface_Subinterfaces_Subinterface_Ipv4_Neighbors_Neighbor

    intfsObj := getIntfsRoot(inParams.ygRoot)

    intfNameRcvd := pathInfo.Var("name")
    ipAddrRcvd := pathInfo.Var("ip")

    if intfObj, ok = intfsObj.Interface[intfNameRcvd]; !ok {
        intfObj, err = intfsObj.NewInterface(intfNameRcvd)
        if err != nil {
            log.Error("Creation of interface subtree failed!")
            return err
        }
    }
    ygot.BuildEmptyTree(intfObj)

    if subIntfObj, ok = intfObj.Subinterfaces.Subinterface[0]; !ok {
        subIntfObj, err = intfObj.Subinterfaces.NewSubinterface(0)
        if err != nil {
            log.Error("Creation of subinterface subtree failed!")
            return err
        }
    }
    ygot.BuildEmptyTree(subIntfObj)

    for key, entry := range data["NEIGH_TABLE"] {
        var ipAddr string

        /*separate ip and interface*/
        tokens := strings.Split(key, ":")
        intfName := tokens[0]
        ipAddr = key[len(intfName)+1:]

        linkAddr := data["NEIGH_TABLE"][key].Field["neigh"]
        if (linkAddr == "") {
            log.Info("No mac-address found for IP: ", ipAddr)
            continue;
        }

        addrFamily := data["NEIGH_TABLE"][key].Field["family"]
        if (addrFamily == "") {
            log.Info("No address family found for IP: ", ipAddr)
            continue;
        }

        /*The transformer returns complete table regardless of the interface.
          First check if the interface and IP of this redis entry matches one
          available in the received URI
        */
        if (strings.Contains(targetUriPath, "ipv4") && addrFamily != "IPv4") ||
            intfName != intfNameRcvd ||
            (ipAddrRcvd != "" && ipAddrRcvd != ipAddr) {
                log.Info("Skipping entry: ", entry, "for interface: ", intfName, " and IP:", ipAddr,
                         "interface received: ", intfNameRcvd, " IP received: ", ipAddrRcvd)
                continue
        } else if strings.HasPrefix(targetUriPath, NEIGH_IPv4_PREFIX_STATE_LL) {
            if neighObj, ok = subIntfObj.Ipv4.Neighbors.Neighbor[ipAddr]; !ok {
                neighObj, err = subIntfObj.Ipv4.Neighbors.NewNeighbor(ipAddr)
                if err != nil {
                    log.Error("Creation of neighbor subtree failed!")
                    return err
                }
            }
            ygot.BuildEmptyTree(neighObj)
            neighObj.State.LinkLayerAddress = &linkAddr
            break
        } else if strings.HasPrefix(targetUriPath, NEIGH_IPv4_PREFIX_STATE_IP) {
            if neighObj, ok = subIntfObj.Ipv4.Neighbors.Neighbor[ipAddr]; !ok {
                neighObj, err = subIntfObj.Ipv4.Neighbors.NewNeighbor(ipAddr)
                if err != nil {
                    log.Error("Creation of neighbor subtree failed!")
                    return err
                }
            }
            ygot.BuildEmptyTree(neighObj)
            neighObj.State.Ip = &ipAddr
            break
        } else if strings.HasPrefix(targetUriPath, NEIGH_IPv4_PREFIX_IP) {
            if neighObj, ok = subIntfObj.Ipv4.Neighbors.Neighbor[ipAddr]; !ok {
                neighObj, err = subIntfObj.Ipv4.Neighbors.NewNeighbor(ipAddr)
                if err != nil {
                    log.Error("Creation of neighbor subtree failed!")
                    return err
                }
            }
            ygot.BuildEmptyTree(neighObj)
            neighObj.State.Ip = &ipAddr
            neighObj.State.LinkLayerAddress = &linkAddr
            neighObj.State.Origin = 0
            break
        } else if strings.HasPrefix(targetUriPath, NEIGH_IPv4_PREFIX) {
            if neighObj, ok = subIntfObj.Ipv4.Neighbors.Neighbor[ipAddr]; !ok {
                neighObj, err = subIntfObj.Ipv4.Neighbors.NewNeighbor(ipAddr)
                if err != nil {
                    log.Error("Creation of neighbor subtree failed!")
                    return err
                }
            }
            ygot.BuildEmptyTree(neighObj)
            neighObj.State.Ip = &ipAddr
            neighObj.State.LinkLayerAddress = &linkAddr
            neighObj.State.Origin = 0
        }
    }
    return err
}

var DbToYang_neigh_tbl_get_all_ipv6_xfmr SubTreeXfmrDbToYang = func (inParams XfmrParams) (error) {
    var err error
    var ok bool

    data := (*inParams.dbDataMap)[inParams.curDb]
    log.Info("DbToYang_neigh_tbl_get_all_ipv6_xfmr - data: ", data)
    pathInfo := NewPathInfo(inParams.uri)
    targetUriPath, err := getYangPathFromUri(pathInfo.Path)
    log.Info("DbToYang_neigh_tbl_get_all_ipv6_xfmr - targetUriPath: ", targetUriPath)

    var intfObj *ocbinds.OpenconfigInterfaces_Interfaces_Interface
    var subIntfObj *ocbinds.OpenconfigInterfaces_Interfaces_Interface_Subinterfaces_Subinterface
    var neighObj *ocbinds.OpenconfigInterfaces_Interfaces_Interface_Subinterfaces_Subinterface_Ipv6_Neighbors_Neighbor

    intfsObj := getIntfsRoot(inParams.ygRoot)

    intfNameRcvd := pathInfo.Var("name")
    ipAddrRcvd := pathInfo.Var("ip")

    if intfObj, ok = intfsObj.Interface[intfNameRcvd]; !ok {
        intfObj, err = intfsObj.NewInterface(intfNameRcvd)
        if err != nil {
            log.Error("Creation of interface subtree failed!")
            return err
        }
    }
    ygot.BuildEmptyTree(intfObj)

    if subIntfObj, ok = intfObj.Subinterfaces.Subinterface[0]; !ok {
        subIntfObj, err = intfObj.Subinterfaces.NewSubinterface(0)
        if err != nil {
            log.Error("Creation of subinterface subtree failed!")
            return err
        }
    }
    ygot.BuildEmptyTree(subIntfObj)

    for key, entry := range data["NEIGH_TABLE"] {
        var ipAddr string

        /*separate ip and interface*/
        tokens := strings.Split(key, ":")
        intfName := tokens[0]
        ipAddr = key[len(intfName)+1:]

        linkAddr := data["NEIGH_TABLE"][key].Field["neigh"]
        if (linkAddr == "") {
            log.Info("No mac-address found for IP: ", ipAddr)
            continue;
        }

        addrFamily := data["NEIGH_TABLE"][key].Field["family"]
        if (addrFamily == "") {
            log.Info("No address family found for IP: ", ipAddr)
            continue;
        }

        if (strings.Contains(targetUriPath, "ipv6") && addrFamily != "IPv6") ||
            intfName != intfNameRcvd ||
            (ipAddrRcvd != "" && ipAddrRcvd != ipAddr) {
                log.Info("Skipping entry: ", entry, "for interface: ", intfName, " and IP:", ipAddr,
                         "interface received: ", intfNameRcvd, " IP received: ", ipAddrRcvd)
                continue
        }else if strings.HasPrefix(targetUriPath, NEIGH_IPv6_PREFIX_STATE_LL) {
            if neighObj, ok = subIntfObj.Ipv6.Neighbors.Neighbor[ipAddr]; !ok {
                neighObj, err = subIntfObj.Ipv6.Neighbors.NewNeighbor(ipAddr)
                if err != nil {
                    log.Error("Creation of neighbor subtree failed!")
                    return err
                }
            }
            ygot.BuildEmptyTree(neighObj)
            neighObj.State.LinkLayerAddress = &linkAddr
            break
        } else if strings.HasPrefix(targetUriPath, NEIGH_IPv6_PREFIX_STATE_IP) {
            if neighObj, ok = subIntfObj.Ipv6.Neighbors.Neighbor[ipAddr]; !ok {
                neighObj, err = subIntfObj.Ipv6.Neighbors.NewNeighbor(ipAddr)
                if err != nil {
                    log.Error("Creation of neighbor subtree failed!")
                    return err
                }
            }
            ygot.BuildEmptyTree(neighObj)
            neighObj.State.Ip = &ipAddr
            break
        } else if strings.HasPrefix(targetUriPath, NEIGH_IPv6_PREFIX_IP) {
            if neighObj, ok = subIntfObj.Ipv6.Neighbors.Neighbor[ipAddr]; !ok {
                neighObj, err = subIntfObj.Ipv6.Neighbors.NewNeighbor(ipAddr)
                if err != nil {
                    log.Error("Creation of neighbor subtree failed!")
                    return err
                }
            }
            ygot.BuildEmptyTree(neighObj)
            neighObj.State.Ip = &ipAddr
            neighObj.State.LinkLayerAddress = &linkAddr
            neighObj.State.IsRouter = true
            neighObj.State.NeighborState = 0
            neighObj.State.Origin = 0
            break
        } else if strings.HasPrefix(targetUriPath, NEIGH_IPv6_PREFIX) {
            if neighObj, ok = subIntfObj.Ipv6.Neighbors.Neighbor[ipAddr]; !ok {
                neighObj, err = subIntfObj.Ipv6.Neighbors.NewNeighbor(ipAddr)
                if err != nil {
                    log.Error("Creation of neighbor subtree failed!")
                    return err
                }
            }
            ygot.BuildEmptyTree(neighObj)
            neighObj.State.Ip = &ipAddr
            neighObj.State.LinkLayerAddress = &linkAddr
            neighObj.State.IsRouter = true
            neighObj.State.NeighborState = 0
            neighObj.State.Origin = 0
        }
    }
    return err
}

func getDefaultVrfInterfaces(d *db.DB)(map[string]string) {
    var defaultVrfIntfs map[string]string
    defaultVrfIntfs = make(map[string]string)

    tblList := []string{"INTERFACE", "VLAN_INTERFACE", "PORTCHANNEL_INTERFACE"}

    for _, tbl := range tblList {
        tblObj, err := d.GetTable(&db.TableSpec{Name:tbl})
        if err != nil {
           continue
        }

         keys, err := tblObj.GetKeys()
        for _, key := range keys {
            entry, err := d.GetEntry(&db.TableSpec{Name: tbl}, key)
            if(err != nil) {
                continue
            }

            log.Info("Key: ", key.Get(0))
            if _, ok := entry.Field["vrf_name"]; !ok {
                defaultVrfIntfs[key.Get(0)] = "default"
            }
        }
    }

    entry, _ := d.GetEntry(&db.TableSpec{Name: "MGMT_VRF_CONFIG"}, db.Key{Comp: []string{"vrf_global"}})
    if _, ok := entry.Field["mgmtVrfEnabled"]; !ok {
        defaultVrfIntfs["eth0"] = "default"
    }

    return defaultVrfIntfs
}

func getNonDefaultVrfInterfaces(d *db.DB)(map[string]string) {
    var nonDefaultVrfIntfs map[string]string
    nonDefaultVrfIntfs = make(map[string]string)

    tblList := []string{"INTERFACE", "VLAN_INTERFACE", "PORTCHANNEL_INTERFACE"}
    for _, tbl := range tblList {
        tblObj, err := d.GetTable(&db.TableSpec{Name:tbl})
        if err != nil {
           continue
        }

         keys, err := tblObj.GetKeys()
         for _, key := range keys {
            entry, err := d.GetEntry(&db.TableSpec{Name: tbl}, key)
            if(err != nil) {
                continue
            }

            log.Info("Key: ", key.Get(0))
            if input, ok := entry.Field["vrf_name"]; ok {
                input_str := fmt.Sprintf("%v", input)
                nonDefaultVrfIntfs[key.Get(0)] = input_str
                log.Info("VRF Found -- intf: ", key.Get(0), " input_str: ", input_str)
            } else {
                log.Info("VRF No Found -- intf: ", key.Get(0))
            }
        }
    }

    entry, _ := d.GetEntry(&db.TableSpec{Name: "MGMT_VRF_CONFIG"}, db.Key{Comp: []string{"vrf_global"}})
    if _, ok := entry.Field["mgmtVrfEnabled"]; ok {
        nonDefaultVrfIntfs["eth0"] = "mgmt"
    }

    return nonDefaultVrfIntfs
}


func clear_all(fam_switch string, force bool, d *db.DB)  string {
    var err error
    var isPerm bool = false
    var cmd *exec.Cmd

    vrfList := getNonDefaultVrfInterfaces(d)

    cmd = exec.Command("ip", fam_switch, "neigh", "show", "all")
    cmd.Dir = "/bin"

    out, err := cmd.StdoutPipe()
    if err != nil {
        log.Info("Can't get stdout pipe: ", err)
        return "%Error: Internal error"
    }

    err = cmd.Start()
    if err != nil {
        log.Info("cmd.Start() failed with: ", err)
        return "%Error: Internal error"
    }

    in := bufio.NewScanner(out)
    for in.Scan() {
        line := in.Text()

        if strings.Contains(line, "lladdr") {
            if strings.Contains(line, "PERMANENT") && force == false {
                isPerm = true
                continue
            }

            list := strings.Fields(line)
            ip := list[0]
            intf := list[2]

            if (vrfList[intf] != "") {
                continue
            }

            _, e := exec.Command("ip", fam_switch, "neigh", "del", ip, "dev", intf).Output()
            if e != nil {
               log.Info("Eror: ", e)
                if (strings.Contains(e.Error(), "255")) {
                    return "Unable to clear all entries, please try again"
                } else {
                    return "%Error: Internal error"
                }
            }
        }
    }

    if isPerm {
        return "Permanent entry found, use 'force' to delete permanent entries"
    }

    return "Success"
}


func clear_all_vrf(fam_switch string, force bool, vrf string) string {
    var err error
    var isPerm bool = false
    var cmd *exec.Cmd

    if (len(vrf) <= 0) {
        log.Info("Missing VRF name, returning")
        return "%Error: Internal error"
    }
    cmd = exec.Command("ip", fam_switch, "neigh", "show", "all", "vrf", vrf)
    cmd.Dir = "/bin"

    out, err := cmd.StdoutPipe()
    if err != nil {
        log.Info("Can't get stdout pipe: ", err)
        return err.Error()
    }

    err = cmd.Start()
    if err != nil {
        log.Info("cmd.Start() failed with: ", err)
        return err.Error()
    }

    in := bufio.NewScanner(out)
    for in.Scan() {
        line := in.Text()

        if strings.Contains(line, "PERMANENT") && force == false {
            isPerm = true
            break
        }
    }

    /* Now flush all entries */
    if (force == true) {
        log.Info("Executing: ip ", fam_switch, " -s ", "-s ", "neigh ", "flush ", "all ", "nud ", "all ", "vrf ", vrf)
        _, err = exec.Command("ip", fam_switch, "-s", "-s", "neigh", "flush", "all", "nud", "all", "vrf", vrf).Output()

    } else {
        log.Info("Executing: ip ", fam_switch, " -s ", "-s ", "neigh ", "flush ", "all ", "vrf ", vrf)
        _, err = exec.Command("ip", fam_switch, "-s", "-s", "neigh", "flush", "all", "vrf", vrf).Output()
    }

    if err != nil {
        log.Info(err)
        if (strings.Contains(err.Error(), "255")) {
            return "Unable to clear all entries, please try again"
        } else {
            return "%Error: Internal error"
        }
    }

    if isPerm {
        return "Permanent entry found, use 'force' to delete permanent entries"
    }

    return "Success"
}

func clear_ip(ip string, fam_switch string, force bool, vrf string) string {
    var cmd *exec.Cmd
    var isValidIp bool = false
    var isPerm bool = false

    //get interfaces first associated with this ip
    if (len(vrf) > 0) {
        cmd = exec.Command("ip", fam_switch, "neigh", "show", ip, "vrf", vrf)
    } else {
        cmd = exec.Command("ip", fam_switch, "neigh", "show", ip)
    }
    cmd.Dir = "/bin"

    out, err := cmd.StdoutPipe()
    if err != nil {
        log.Info("Can't get stdout pipe: ", err)
        return "%Error: Internal error"
    }

    err = cmd.Start()
    if err != nil {
        log.Info("cmd.Start() failed with: ", err)
        return "%Error: Internal error"
    }

    in := bufio.NewScanner(out)
    for in.Scan() {
        line := in.Text()

        if strings.Contains(line, "PERMANENT") && force == false {
            isValidIp = true
            isPerm = true
            continue
        }

        list := strings.Fields(line)
        intf := list[2]
        log.Info("Executing: ip ", fam_switch, " neigh ", "del ", ip, " dev ", intf)
        _, e := exec.Command("ip", fam_switch, "neigh", "del", ip, "dev", intf).Output()
        if e != nil {
            log.Info(e)
            if (strings.Contains(e.Error(), "255")) {
                return "Unable to clear all entries, please try again"
            } else {
                return "%Error: Internal error"
            }
        }
        isValidIp = true
    }

    if isValidIp == true && isPerm == false {
        return "Success"
    } else if isPerm == true {
        return "Permanent entry found, use 'force' to delete permanent entries"
    } else {
        return "Error: IP address " + ip + " not found"
    }
}

func clear_intf(intf string, fam_switch string, force bool) string {
    var isValidIntf bool = false
    var isPerm bool = false

    cmd := exec.Command("ip", fam_switch, "neigh", "show", "dev", intf)
    cmd.Dir = "/bin"

    out, err := cmd.StdoutPipe()
    if err != nil {
        log.Info("Can't get stdout pipe: ", err)
        return "%Error: Internal error"
    }

    err = cmd.Start()
    if err != nil {
        log.Info("cmd.Start() failed with: ", err)
        return "%Error: Internal error"
    }

    in := bufio.NewScanner(out)
    for in.Scan() {
        line := in.Text()

        if strings.Contains(line, "Cannot find device") {
            log.Info("Error: ", line)
            return line
        }

        if strings.Contains(line, "PERMANENT") && force == false {
            isValidIntf = true
            isPerm = true
            continue
        }

        list := strings.Fields(line)
        ip := list[0]
        log.Info("Executing: ip ", fam_switch, " neigh ", "del ", ip, " dev ", intf)
        _, e := exec.Command("ip", fam_switch, "neigh", "del", ip, "dev", intf).Output()
        if e != nil {
            log.Info(e)
            if (strings.Contains(e.Error(), "255")) {
                return "Unable to clear all entries, please try again"
            } else {
                return "%Error: Internal error"
            }
        }
        isValidIntf = true
    }

    if isValidIntf == true && isPerm == false {
        return "Success"
    } else if isPerm == true {
        return "Permanent entry found, use 'force' to delete permanent entries"
    } else {
        return "Error: Interface " + intf + " not found"
    }
}

var rpc_clear_neighbors RpcCallpoint = func(body []byte, dbs [db.MaxDB]*db.DB) ([]byte, error) {
    log.Info("In rpc_clear_neighbors")
    var err error
    var status string
    var fam_switch string = "-4"
    var force bool = false
    var intf string = ""
    var ip string = ""
    var vrf string = ""

    var mapData map[string]interface{}
    err = json.Unmarshal(body, &mapData)
    if err != nil {
        log.Info("Failed to unmarshall given input data")
        return nil, err
    }

    var result struct {
        Output struct {
              Status string `json:"response"`
        } `json:"sonic-neighbor:output"`
    }

    if input, ok := mapData["sonic-neighbor:input"]; ok {
        mapData = input.(map[string]interface{})
    } else {
        result.Output.Status = "Invalid input"
        return json.Marshal(&result)
    }

    if input, ok := mapData["family"]; ok {
        input_str := fmt.Sprintf("%v", input)
        family := input_str
        if strings.EqualFold(family, "IPv6") || family == "1" {
            fam_switch = "-6"
        }
    }

    if input, ok := mapData["force"]; ok {
        input_str := fmt.Sprintf("%v", input)
        force, err = strconv.ParseBool(input_str)
        if (err != nil) {
            result.Output.Status = "Invalid input"
            return json.Marshal(&result)
        }
    }

    if input, ok := mapData["ifname"]; ok {
        input_str := fmt.Sprintf("%v", input)
        intf = input_str
    }

    if input, ok := mapData["ip"]; ok {
        input_str := fmt.Sprintf("%v", input)
        ip = input_str
    }

    if input, ok := mapData["vrf"]; ok {
        input_str := fmt.Sprintf("%v", input)
        vrf = input_str
    }

    if len(intf) > 0 {
        status = clear_intf(intf, fam_switch, force)
    } else if len(ip) > 0 {
        status = clear_ip(ip, fam_switch, force, vrf)
    } else if len(vrf) > 0 {
        status = clear_all_vrf(fam_switch, force, vrf)
    } else {
        status = clear_all(fam_switch, force, dbs[db.ConfigDB])
    }

    result.Output.Status = status

    log.Info("result: ", result.Output.Status)
    return json.Marshal(&result)
}
