//////////////////////////////////////////////////////////////////////////
//
// Copyright 2020 Dell, Inc.
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

package transformer_test

import (
	"fmt"
	"testing"
	"time"
    "errors"
	"translib/tlerr"
)

func Test_SubtreeXfmr_CRUDErr_OCYang(t *testing.T) {
	fmt.Println("\n\n+++++++++++++ Performing Subtree Xfmr Error handling CRUD OC Yang Cases ++++++++++++")
	var url, url_body_json string
    var exp_err error

	/** SubtreeXfmr Error handling Create**/
	prereq_cfg_exist_map := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan5":map[string]interface{}{
                                                                                      "vlanid": "5",
                                                                                      "members@": "Ethernet32"}},
				                       "VLAN_MEMBER":map[string]interface{}{"Vlan5|Ethernet32":map[string]interface{}{
					                                                             "tagging_mode": "tagged"}}}
        prereq_cfg_not_exist_map := map[string]interface{}{"INTERFACE":map[string]interface{}{"Ethernet32":map[string]interface{}{
                                                                                      "NULL": "NULL"}}}
        expected_map_vlan := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan5":map[string]interface{}{
		                                                                      "vlanid": "5",
                                                                                      "members@": "Ethernet32"}}}
        expected_map_vlanmember := map[string]interface{}{"VLAN_MEMBER":map[string]interface{}{"Vlan5|Ethernet32":map[string]interface{}{					                                                             "tagging_mode": "tagged"}}}

	loadConfigDB(rclient, prereq_cfg_exist_map)
	unloadConfigDB(rclient, prereq_cfg_not_exist_map)
	url = "/openconfig-interfaces:interfaces/interface[name=Ethernet32]/openconfig-if-ethernet:ethernet/openconfig-vlan:switched-vlan/config"
	url_body_json = "{\"openconfig-vlan:interface-mode\":\"ACCESS\",\"openconfig-vlan:trunk-vlans\":[5]}"
	exp_err = tlerr.AlreadyExists("Entry Vlan5 already exists")
	t.Run("SubtreeXfmr Error handling create.", processSetRequest(url, url_body_json, "POST", true, exp_err))
	time.Sleep(1 * time.Second)


	/** SubtreeXfmr Error handling Update**/
	prereq_cfg_not_exist_map = map[string]interface{}{"VLAN":map[string]interface{}{"Vlan25":map[string]interface{}{
                                                                                      "vlanid": "25",
                                                                                      "members@": "Ethernet32"}},
				                           "VLAN_MEMBER":map[string]interface{}{"Vlan25|Ethernet32":map[string]interface{}{
					                                                             "tagging_mode": "tagged"}},
							   "INTERFACE":map[string]interface{}{"Ethernet32":map[string]interface{}{
                                                                                      "NULL": "NULL"}}}
        expected_map_vlan = map[string]interface{}{}
        expected_map_vlanmember = map[string]interface{}{}


	unloadConfigDB(rclient, prereq_cfg_not_exist_map)
	url = "/openconfig-interfaces:interfaces/interface[name=Ethernet32]"
	url_body_json = "{\"openconfig-interfaces:interface\":[{\"name\":\"Ethernet32\",\"openconfig-if-ethernet:ethernet\":{\"openconfig-vlan:switched-vlan\":{\"config\":{\"interface-mode\":\"ACCESS\",\"trunk-vlans\":[25]}}}}]}"
	exp_err = tlerr.InvalidArgsError{Format:"Invalid VLAN: 25"}
	t.Run("SubtreeXfmr Error handling update.", processSetRequest(url, url_body_json, "PATCH", true, exp_err))
	time.Sleep(1 * time.Second)
	t.Run("Verify SubtreeXfmr error handling update - VLAN table.", verifyDbResult(rclient, "VLAN|Vlan25", expected_map_vlan, false))
	t.Run("Verify SubtreeXfmr error handling update - VLAN_MEMBER table.", verifyDbResult(rclient, "VLAN_MEMBER|Vlan25|Ethernet32", expected_map_vlanmember, false))
	unloadConfigDB(rclient, prereq_cfg_not_exist_map)
	/*********************/

	/** SubtreeXfmr Error handling Replace**/
	prereq_cfg_exist_map = map[string]interface{}{"VLAN":map[string]interface{}{"Vlan5":map[string]interface{}{
                                                                                      "vlanid": "5",
                                                                                      "members@": "Ethernet32"}},
				                           "VLAN_MEMBER":map[string]interface{}{"Vlan5|Ethernet32":map[string]interface{}{
					                                                             "tagging_mode": "tagged"}}}
        expected_map_vlan = map[string]interface{}{"VLAN":map[string]interface{}{"Vlan5":map[string]interface{}{
		                                                                      "vlanid": "5",
                                                                                      "members@": "Ethernet32"}}}
        expected_map_vlanmember = map[string]interface{}{"VLAN_MEMBER":map[string]interface{}{"Vlan5|Ethernet32":map[string]interface{}{					                                                             "tagging_mode": "tagged"}}}

	loadConfigDB(rclient, prereq_cfg_exist_map)
	url = "/openconfig-interfaces:interfaces/interface[name=Ethernet32]/openconfig-if-ethernet:ethernet/openconfig-vlan:switched-vlan/config/trunk-vlans"
	url_body_json = "{\"openconfig-vlan:trunk-vlans\":[10]}"
	exp_err = tlerr.NotSupported("REPLACE of Vlan members is currently not supported.")
	t.Run("SubtreeXfmr Error handling replace.", processSetRequest(url, url_body_json, "PUT", true, exp_err))
	time.Sleep(1 * time.Second)
	t.Run("Verify SubtreeXfmr error handling replace - VLAN table.", verifyDbResult(rclient, "VLAN|Vlan5", expected_map_vlan, false))
	t.Run("Verify SubtreeXfmr error handling replace - VLAN_MEMBER table.", verifyDbResult(rclient, "VLAN_MEMBER|Vlan5|Ethernet32", expected_map_vlanmember, false))
	unloadConfigDB(rclient, prereq_cfg_not_exist_map)
	/*********************/

	/** SubtreeXfmr Error handling Delete**/
	prereq_cfg_exist_map = map[string]interface{}{"VLAN":map[string]interface{}{"Vlan5":map[string]interface{}{
                                                                                      "vlanid": "5",
                                                                                      "members@": "Ethernet32"}},
				                           "VLAN_MEMBER":map[string]interface{}{"Vlan5|Ethernet32":map[string]interface{}{
					                                                             "tagging_mode": "tagged"}}}
        expected_map_vlan = map[string]interface{}{"VLAN":map[string]interface{}{"Vlan5":map[string]interface{}{
		                                                                      "vlanid": "5",
                                                                                      "members@": "Ethernet32"}}}
        expected_map_vlanmember = map[string]interface{}{"VLAN_MEMBER":map[string]interface{}{"Vlan5|Ethernet32":map[string]interface{}{					                                                             "tagging_mode": "tagged"}}}

	loadConfigDB(rclient, prereq_cfg_exist_map)
	url = "/openconfig-interfaces:interfaces/interface[name=Ethernet32]/openconfig-if-ethernet:ethernet/openconfig-vlan:switched-vlan/config/trunk-vlans[trunk-vlans=20]"
	exp_err = tlerr.InvalidArgsError{Format:"Invalid VLAN"}
	t.Run("SubtreeXfmr Error handling delete.", processDeleteRequest(url, true, exp_err))
	time.Sleep(1 * time.Second)
	t.Run("Verify SubtreeXfmr error handling delte - VLAN table.", verifyDbResult(rclient, "VLAN|Vlan5", expected_map_vlan, false))
	t.Run("Verify SubtreeXfmr error handling delete - VLAN_MEMBER table.", verifyDbResult(rclient, "VLAN_MEMBER|Vlan5|Ethernet32", expected_map_vlanmember, false))
	unloadConfigDB(rclient, prereq_cfg_not_exist_map)
	/*********************/
        fmt.Println("\n\n+++++++++++++ Done Performing Subtree Xfmr Error handling CRUD OC Yang Cases ++++++++++++")

}

func Test_FieldXfmr_CRUDErr_OCYang(t *testing.T) {
        fmt.Println("\n\n+++++++++++++ Performing Field Xfmr Error handling CRUD OC Yang Cases ++++++++++++")
        var prereq_map map[string]interface{}
        var url, url_body_json string
        var exp_err error

        /** FieldXfmr Error handling Create**/
        prereq_cfg_not_exist_map := map[string]interface{}{"INTERFACE":map[string]interface{}{"Ethernet1":map[string]interface{}{
                                                                                      "NULL": "NULL"}}}
        exp_map := make(map[string]interface{})
	unloadConfigDB(rclient, prereq_cfg_not_exist_map)
	url = "/openconfig-interfaces:interfaces"
	url_body_json = "{\"openconfig-interfaces:interface\":[{\"name\":\"Ethernet1\",\"config\":{\"name\": \"Ethernet1\",\"mtu\":1900}}]}"
	exp_err = tlerr.InvalidArgsError{Format: "Interface Ethernet1 cannot be configured."}
	t.Run("FieldXfmr Error handling create.", processSetRequest(url, url_body_json, "POST", true, exp_err))
	time.Sleep(1 * time.Second)
	t.Run("Verify .FieldXfmr Error handling create", verifyDbResult(rclient, "INTERFACE|Ethernet1", exp_map, false))
	unloadConfigDB(rclient, prereq_cfg_not_exist_map)
	/*********************/
	
	/** FieldXfmr Error handling Update**/
	prereq_map = map[string]interface{}{"COMMUNITY_SET":map[string]interface{}{"test1":map[string]interface{}{
		"match_action":"ANY",
		"community_member@":"1:1,no-peer,no-advertise",
		"set_type":"STANDARD"}}}
	loadConfigDB(rclient, prereq_map)
	url = "/openconfig-routing-policy:routing-policy/defined-sets/openconfig-bgp-policy:bgp-defined-sets/community-sets"
	url_body_json = "{\"openconfig-bgp-policy:community-sets\":{\"community-set\":[{\"community-set-name\":\"test1\",\"config\":{\"community-set-name\":\"test1\",\"community-member\":[\"NOPEER\",\"NO_ADVERTISE\",\"1:1\"],\"match-set-options\":\"ALL\"}}]}}"
	exp_err = errors.New("Match option difference")
	t.Run("FieldXfmr Error handling update.", processSetRequest(url, url_body_json, "PATCH", true, exp_err))
        time.Sleep(1 * time.Second)
        t.Run("Verify .FieldXfmr Error handling update", verifyDbResult(rclient, "COMMUNITY_SET|test1", prereq_map, false))
        unloadConfigDB(rclient, prereq_map)
	/*********************/

	/** FieldXfmr Error handling Replace**/
	prereq_map = map[string]interface{}{"COMMUNITY_SET":map[string]interface{}{"test1":map[string]interface{}{
                "match_action":"ANY",
                "community_member@":"1:1,no-peer,no-advertise",
                "set_type":"STANDARD"}}}
        loadConfigDB(rclient, prereq_map)
        url = "/openconfig-routing-policy:routing-policy/defined-sets/openconfig-bgp-policy:bgp-defined-sets/community-sets"
        url_body_json = "{\"openconfig-bgp-policy:community-sets\":{\"community-set\":[{\"community-set-name\":\"test1\",\"config\":{\"community-set-name\":\"test1\",\"community-member\":[\"NOPEER\",\"NO_ADVERTISE\",\"1:1\"],\"match-set-options\":\"ALL\"}}]}}"
        exp_err = errors.New("Match option difference")
        t.Run("FieldXfmr Error handling replace.", processSetRequest(url, url_body_json, "PUT", true, exp_err))
        time.Sleep(1 * time.Second)
        t.Run("Verify .FieldXfmr Error handling replace", verifyDbResult(rclient, "COMMUNITY_SET|test1", prereq_map, false))
        unloadConfigDB(rclient, prereq_map)
        /*********************/
        fmt.Println("\n\n+++++++++++++ Done Performing Field Xfmr Error handling CRUD OC Yang Cases ++++++++++++")

}

func Test_KeyXfmr_CRUDErr_OCYang(t *testing.T) {
        fmt.Println("\n\n+++++++++++++ Performing Key Xfmr Error handling CRUD OC Yang Cases ++++++++++++")
        var url, url_body_json string

        /** KeyXfmr Error handling Create**/
	url = "/openconfig-interfaces:interfaces/interface[name=defaultEth1]"
	url_body_json = "{\"openconfig-interfaces:config\":{\"name\":\"defaultEth\",\"type\":\"ds3\",\"mtu\":2300}}"
        experr := tlerr.InternalError{Format: "Interface name prefix not matched with supported types"}
        t.Run("KeyXfmr Error handling create.", processSetRequest(url, url_body_json, "POST", true, experr))
        time.Sleep(1 * time.Second)
        /*********************/


        /** KeyXfmr Error handling update**/
	url = "/openconfig-interfaces:interfaces/interface[name=defaultEth1]"
	url_body_json = "{\"openconfig-interfaces:interface\":[{\"name\":\"defaultEth1\",\"config\":{\"name\":\"defaultEth1\",\"type\":\"ds3\",\"mtu\": 2500}}]}"
        experr = tlerr.InternalError{Format: "Interface name prefix not matched with supported types"}
        t.Run("KeyXfmr Error handling update.", processSetRequest(url, url_body_json, "PATCH", true, experr))
        time.Sleep(1 * time.Second)
        /*********************/


	/** KeyXfmr Error handling replace **/
	url = "/openconfig-interfaces:interfaces/interface[name=defaultEth1]"
        url_body_json = "{\"openconfig-interfaces:interface\":[{\"name\":\"defaultEth1\",\"config\":{\"name\":\"defaultEth1\",\"type\":\"ds3\",\"mtu\": 2500}}]}"
        experr = tlerr.InternalError{Format: "Interface name prefix not matched with supported types"}
        t.Run("KeyXfmr Error handling update.", processSetRequest(url, url_body_json, "PUT", true, experr))
        time.Sleep(1 * time.Second)
        /*********************/


	/** KeyXfmr Error handling delete **/
        prereq_cfg_not_exist_map := map[string]interface{}{"INTERFACE":map[string]interface{}{"Ethernet1":map[string]interface{}{
                                                                                      "NULL": "NULL"}}}
	loadConfigDB(rclient, prereq_cfg_not_exist_map)
        url = "/openconfig-interfaces:interfaces/interface[name=Ethernet1]"
        exp_err := tlerr.InvalidArgsError{Format :"Physical Interface: Ethernet1 cannot be deleted"}
        t.Run("KeyXfmr Error handling delete.", processDeleteRequest(url, true, exp_err))
        time.Sleep(1 * time.Second)
        unloadConfigDB(rclient, prereq_cfg_not_exist_map)
        /*********************/

        fmt.Println("\n\n+++++++++++++ Done Performing Key Xfmr Error handling CRUD OC Yang Cases ++++++++++++")
}

func Test_TableXfmr_CRUDErr_OCYang(t *testing.T) {
        fmt.Println("\n\n+++++++++++++ Performing Table Xfmr Error handling CRUD OC Yang Cases ++++++++++++")
        var url, url_body_json string
        var exp_err error

        /** TableXfmr Error handling Create**/
	url = "/openconfig-network-instance:network-instances/network-instance[name=fVr]/protocols/protocol[identifier=BGP][name=bgp]/bgp/global/confederation/config"
        url_body_json = "{\"openconfig-network-instance:member-as\":[4294967294]}"
        exp_err = tlerr.InvalidArgsError{Format : "Invalid name fVr"}
        t.Run("TableXfmr Error handling create.", processSetRequest(url, url_body_json, "POST", true, exp_err))
        time.Sleep(1 * time.Second)
        /*********************/

	/** TableXfmr Error handling Update**/
        url = "/openconfig-network-instance:network-instances/network-instance[name=fVr]/protocols/protocol[identifier=BGP][name=bgp]/bgp/global/confederation/config/member-as"
        url_body_json = "{\"openconfig-network-instance:member-as\":[4294967294]}"
        exp_err = tlerr.InvalidArgsError{Format : "Invalid name fVr"}
        t.Run("TableXfmr Error handling Update.", processSetRequest(url, url_body_json, "PATCH", true, exp_err))
        time.Sleep(1 * time.Second)
        /*********************/

	/** TableXfmr Error handling Replace**/
        url = "/openconfig-network-instance:network-instances/network-instance[name=fVr]/protocols/protocol[identifier=BGP][name=bgp]/bgp/global/confederation/config/member-as"
        url_body_json = "{\"openconfig-network-instance:member-as\":[4294967294]}"
        exp_err = tlerr.InvalidArgsError{Format: "Invalid name fVr"}
        t.Run("TableXfmr Error handling Replace.", processSetRequest(url, url_body_json, "PUT", true, exp_err))
        time.Sleep(1 * time.Second)
        /*********************/

        /** TableXfmr Error handling delete **/
        url = "/openconfig-network-instance:network-instances/network-instance[name=fVr]"
        exp_err = tlerr.InvalidArgsError{Format:"Invalid name fVr"}
        t.Run("TableXfmr Error handling delete.", processDeleteRequest(url, true, exp_err))
        time.Sleep(1 * time.Second)
        /*********************/

        fmt.Println("\n\n+++++++++++++ Done Performing Table Xfmr Error handling CRUD OC Yang Cases ++++++++++++")

}

func Test_PostXfmr_Err_SetOCYang(t *testing.T) {
        fmt.Println("\n\n+++++++++++++ Performing Post Xfmr Error handling Set OC Yang Cases ++++++++++++")
        var url string
        var exp_err error

        /** PostXfmr Error handling **/
        prereq_map := map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"default":map[string]interface{}{
                                                                                                  "confed_id": "429496722",
                                                                                                  "confed_peers@": "4294967294"}},
                                             "VRF":map[string]interface{}{"default":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        expected_map := map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"default":map[string]interface{}{
                                                                                                  "confed_id": "429496722",
                                                                                                  "confed_peers@": "4294967294"}}}
        exp_err = tlerr.NotSupported("Delete not allowed at this container")
        loadConfigDB(rclient, prereq_map)
        url = "/openconfig-network-instance:network-instances/network-instance[name=default]/protocols/protocol[identifier=BGP][name=bgp]/bgp/global/confederation"
        t.Run("PostXfmr Error handling delete.", processDeleteRequest(url, true, exp_err))
        time.Sleep(1 * time.Second)
        t.Run("Verify PostXfmrError handling delete.", verifyDbResult(rclient, "BGP_GLOBALS|default", expected_map, false))
        unloadConfigDB(rclient, prereq_map)
        /*********************/
        fmt.Println("\n\n+++++++++++++ Done Performing Post Xfmr Error handling Set OC Yang Cases ++++++++++++")
}

