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
)


func Test_Leaf_Field_Name_UINT8_Update(t *testing.T) {

        cleanuptbl := map[string]interface{}{"RADIUS":map[string]interface{}{"global":""}}
        url := "/openconfig-system:system/aaa/server-groups/server-group[name=RADIUS]/config/openconfig-system-ext:retransmit-attempts"

        fmt.Println("++++++++++++++  UPDATE Test_Leaf_Field_Name_UINT8  +++++++++++++")

        patch_payload := "{ \"openconfig-system-ext:retransmit-attempts\": 5}"
        patch_expected := map[string]interface{}{"RADIUS":map[string]interface{}{"global":map[string]interface{}{"retransmit":"5"}}}

        t.Run("UPDATE on Leaf Field Name UINT8", processSetRequest(url, patch_payload, "PATCH", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify update on Leaf Field Name UINT8", verifyDbResult(rclient, "RADIUS|global", patch_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Field_Name_UINT8_Replace(t *testing.T) {

        cleanuptbl := map[string]interface{}{"RADIUS":map[string]interface{}{"global":""}}
        prereq := map[string]interface{}{"RADIUS":map[string]interface{}{"global":map[string]interface{}{"retransmit":"5"}}}
        url := "/openconfig-system:system/aaa/server-groups/server-group[name=RADIUS]/config/openconfig-system-ext:retransmit-attempts"

        fmt.Println("++++++++++++++  Replace Test_Leaf_Field_Name_UINT8  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        put_payload := "{ \"openconfig-system-ext:retransmit-attempts\": 6}"
        put_expected := map[string]interface{}{"RADIUS":map[string]interface{}{"global":map[string]interface{}{"retransmit":"6"}}}

        t.Run("Replace on Leaf Field Name UINT8", processSetRequest(url, put_payload, "PUT", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify replace on Leaf Field Name UINT8", verifyDbResult(rclient, "RADIUS|global", put_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Field_Name_UINT8_Delete(t *testing.T) {

        cleanuptbl := map[string]interface{}{"RADIUS":map[string]interface{}{"global":""}}
        prereq := map[string]interface{}{"RADIUS":map[string]interface{}{"global":map[string]interface{}{"retransmit":"5"}}}
        url := "/openconfig-system:system/aaa/server-groups/server-group[name=RADIUS]/config/openconfig-system-ext:retransmit-attempts"

        fmt.Println("++++++++++++++  DELETE Test_Leaf_Field_Name_UINT8  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        delete_expected_map := make(map[string]interface{})

        t.Run("DELETE on Leaf Field Name UINT8", processDeleteRequest(url, false))
        time.Sleep(1 * time.Second)
        t.Run("Verify delete on Leaf Field Name UINT8", verifyDbResult(rclient, "RADIUS|global", delete_expected_map, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Field_Name_UINT8_Get(t *testing.T) {

        cleanuptbl := map[string]interface{}{"RADIUS":map[string]interface{}{"global":""}}
        prereq := map[string]interface{}{"RADIUS":map[string]interface{}{"global":map[string]interface{}{"retransmit":"5"}}}
        url := "/openconfig-system:system/aaa/server-groups/server-group[name=RADIUS]/config/openconfig-system-ext:retransmit-attempts"

        fmt.Println("++++++++++++++  Get Test_Leaf_Field_Name_UINT8  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        get_expected := "{\"openconfig-system-ext:retransmit-attempts\":5}"

        t.Run("GET on Leaf Field Name UINT8", processGetRequest(url, get_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Field_Name_UINT16_Update(t *testing.T) {

        cleanuptbl := map[string]interface{}{"RADIUS":map[string]interface{}{"global":""}}
        url := "/openconfig-system:system/aaa/server-groups/server-group[name=RADIUS]/config/openconfig-system-ext:timeout"

        fmt.Println("++++++++++++++  UPDATE Test_Leaf_Field_Name_UINT16  +++++++++++++")

        patch_payload := "{ \"openconfig-system-ext:timeout\": 8}"
        patch_expected := map[string]interface{}{"RADIUS":map[string]interface{}{"global":map[string]interface{}{"timeout":"8"}}}

        t.Run("UPDATE on Leaf Field Name UINT16", processSetRequest(url, patch_payload, "PATCH", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify update on Leaf Field Name UINT16", verifyDbResult(rclient, "RADIUS|global", patch_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Field_Name_UINT16_Replace(t *testing.T) {

        cleanuptbl := map[string]interface{}{"RADIUS":map[string]interface{}{"global":""}}
        prereq := map[string]interface{}{"RADIUS":map[string]interface{}{"global":map[string]interface{}{"timeout":"8"}}}
        url := "/openconfig-system:system/aaa/server-groups/server-group[name=RADIUS]/config/openconfig-system-ext:timeout"

        fmt.Println("++++++++++++++  Replace Test_Leaf_Field_Name_UINT16  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        put_payload := "{ \"openconfig-system-ext:timeout\": 4}"
        put_expected := map[string]interface{}{"RADIUS":map[string]interface{}{"global":map[string]interface{}{"timeout":"4"}}}

        t.Run("Replace on Leaf Field Name UINT16", processSetRequest(url, put_payload, "PUT", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify replace on Leaf Field Name UINT16", verifyDbResult(rclient, "RADIUS|global", put_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Field_Name_UINT16_Delete(t *testing.T) {

        cleanuptbl := map[string]interface{}{"RADIUS":map[string]interface{}{"global":""}}
        prereq := map[string]interface{}{"RADIUS":map[string]interface{}{"global":map[string]interface{}{"timeout":"4"}}}
        url := "/openconfig-system:system/aaa/server-groups/server-group[name=RADIUS]/config/openconfig-system-ext:timeout"

        fmt.Println("++++++++++++++  DELETE Test_Leaf_Field_Name_UINT16  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        delete_expected_map := make(map[string]interface{})

        t.Run("DELETE on Leaf Field Name UINT16", processDeleteRequest(url, false))
        time.Sleep(1 * time.Second)
        t.Run("Verify delete on Leaf Field Name UINT16", verifyDbResult(rclient, "RADIUS|global", delete_expected_map, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Field_Name_UINT16_Get(t *testing.T) {

        cleanuptbl := map[string]interface{}{"RADIUS":map[string]interface{}{"global":""}}
        prereq := map[string]interface{}{"RADIUS":map[string]interface{}{"global":map[string]interface{}{"timeout":"4"}}}
        url := "/openconfig-system:system/aaa/server-groups/server-group[name=RADIUS]/config/openconfig-system-ext:timeout"

        fmt.Println("++++++++++++++  Get Test_Leaf_Field_Name_UINT16  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        get_expected := "{\"openconfig-system-ext:timeout\":4}"

        t.Run("GET on Leaf Field Name UINT16", processGetRequest(url, get_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Field_Name_UINT32_Update(t *testing.T) {

        cleanuptbl := map[string]interface{}{"ROUTE_MAP":map[string]interface{}{"MAP1|1":""}}
        url := "/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition[name=MAP1]/statements/statement[name=1]/actions/openconfig-bgp-policy:bgp-actions/config/set-local-pref"

        fmt.Println("++++++++++++++  UPDATE Test_Leaf_Field_Name_UINT32  +++++++++++++")

        patch_payload := "{ \"openconfig-bgp-policy:set-local-pref\": 7}"
        patch_expected := map[string]interface{}{"ROUTE_MAP":map[string]interface{}{"MAP1|1":map[string]interface{}{"set_local_pref":"7"}}}

        t.Run("UPDATE on Leaf Field Name UINT32", processSetRequest(url, patch_payload, "PATCH", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify update on Leaf Field Name UINT32", verifyDbResult(rclient, "ROUTE_MAP|MAP1|1", patch_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Field_Name_UINT32_Replace(t *testing.T) {

        cleanuptbl := map[string]interface{}{"ROUTE_MAP":map[string]interface{}{"MAP1|1":""}}
        prereq := map[string]interface{}{"ROUTE_MAP":map[string]interface{}{"MAP1|1":map[string]interface{}{"set_local_pref":"7"}}}
        url := "/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition[name=MAP1]/statements/statement[name=1]/actions/openconfig-bgp-policy:bgp-actions/config/set-local-pref"

        fmt.Println("++++++++++++++  Replace Test_Leaf_Field_Name_UINT32  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        put_payload := "{ \"openconfig-bgp-policy:set-local-pref\": 9}"
        put_expected := map[string]interface{}{"ROUTE_MAP":map[string]interface{}{"MAP1|1":map[string]interface{}{"set_local_pref":"9"}}}
        t.Run("Replace on Leaf Field Name UINT32", processSetRequest(url, put_payload, "PUT", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify replace on Leaf Field Name UINT32", verifyDbResult(rclient, "ROUTE_MAP|MAP1|1", put_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Field_Name_UINT32_Delete(t *testing.T) {

        cleanuptbl := map[string]interface{}{"ROUTE_MAP":map[string]interface{}{"MAP1|1":""}}
        prereq := map[string]interface{}{"ROUTE_MAP":map[string]interface{}{"MAP1|1":map[string]interface{}{"set_local_pref":"9"}}}
        url := "/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition[name=MAP1]/statements/statement[name=1]/actions/openconfig-bgp-policy:bgp-actions/config/set-local-pref"

        fmt.Println("++++++++++++++  DELETE Test_Leaf_Field_Name_UINT32  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        delete_expected_map := make(map[string]interface{})

        t.Run("DELETE on Leaf Field Name UINT32", processDeleteRequest(url, false))
        time.Sleep(1 * time.Second)
        t.Run("Verify delete on Leaf Field Name UINT32", verifyDbResult(rclient, "ROUTE_MAP|MAP1|1", delete_expected_map, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Field_Name_UINT32_Get(t *testing.T) {

        cleanuptbl := map[string]interface{}{"ROUTE_MAP":map[string]interface{}{"MAP1":map[string]interface{}{"1":""}}}
        prereq := map[string]interface{}{"ROUTE_MAP":map[string]interface{}{"MAP1|1":map[string]interface{}{"set_local_pref":"9"}}}
        url := "/openconfig-routing-policy:routing-policy/policy-definitions/policy-definition[name=MAP1]/statements/statement[name=1]/actions/openconfig-bgp-policy:bgp-actions/config/set-local-pref"

        fmt.Println("++++++++++++++  Get Test_Leaf_Field_Name_UINT32  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        get_expected := "{\"openconfig-bgp-policy:set-local-pref\": 9}"

        t.Run("GET on Leaf Field Name UINT32", processGetRequest(url, get_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

/* Test_Leaf_Field_Name_Boolean also covers leaf field name default value and data type conversion cases */
func Test_Leaf_Field_Name_Boolean_Update(t *testing.T) {

        cleanuptbl := map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"default":""}}
        url := "/openconfig-network-instance:network-instances/network-instance[name=default]/protocols/protocol[identifier=BGP][name=bgp]/bgp/global/route-selection-options/config/always-compare-med"

        fmt.Println("++++++++++++++  UPDATE Test_Leaf_Field_Name_Boolean  +++++++++++++")

        patch_payload := "{ \"openconfig-network-instance:always-compare-med\": true}"
        patch_expected := map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"default":map[string]interface{}{"always_compare_med":"true"}}}

        t.Run("UPDATE on Leaf Field Name Boolean", processSetRequest(url, patch_payload, "PATCH", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify update on Leaf Field Name Boolean", verifyDbResult(rclient, "BGP_GLOBALS|default", patch_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Field_Name_Boolean_Replace(t *testing.T) {

        cleanuptbl := map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"default":""}}
        prereq := map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"default":map[string]interface{}{"always_compare_med":"true"}}}
        url := "/openconfig-network-instance:network-instances/network-instance[name=default]/protocols/protocol[identifier=BGP][name=bgp]/bgp/global/route-selection-options/config/always-compare-med"

        fmt.Println("++++++++++++++  Replace Test_Leaf_Field_Name_Boolean  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        put_payload := "{ \"openconfig-network-instance:always-compare-med\": false}"
        put_expected := map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"default":map[string]interface{}{"always_compare_med":"false"}}}

        t.Run("Replace on Leaf Field Name Boolean", processSetRequest(url, put_payload, "PUT", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify replace on Leaf Field Name Boolean", verifyDbResult(rclient, "BGP_GLOBALS|default", put_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Field_Name_Boolean_Delete(t *testing.T) {

        cleanuptbl := map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"default":""}}
        prereq := map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"default":map[string]interface{}{"always_compare_med":"true"}}}
        url := "/openconfig-network-instance:network-instances/network-instance[name=default]/protocols/protocol[identifier=BGP][name=bgp]/bgp/global/route-selection-options/config/always-compare-med"

        fmt.Println("++++++++++++++  DELETE Test_Leaf_Field_Name_Boolean  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        delete_expected_map := map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"default":map[string]interface{}{"always_compare_med":"false"}}}

        t.Run("DELETE on Leaf Field Name Boolean", processDeleteRequest(url, false))
        time.Sleep(1 * time.Second)
        t.Run("Verify delete on Leaf Field Name Boolean", verifyDbResult(rclient, "BGP_GLOBALS|default", delete_expected_map, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Field_Name_Boolean_Get(t *testing.T) {

        cleanuptbl := map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"default":""}}
        prereq := map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"default":map[string]interface{}{"always_compare_med":"false"}}}
        url := "/openconfig-network-instance:network-instances/network-instance[name=default]/protocols/protocol[identifier=BGP][name=bgp]/bgp/global/route-selection-options/config/always-compare-med"

        fmt.Println("++++++++++++++  Get Test_Leaf_Field_Name_Boolean  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        get_expected := "{\"openconfig-network-instance:always-compare-med\": false}"

        t.Run("GET on Leaf Field Name Boolean", processGetRequest(url, get_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

/* Test_Leaf_Field_Xfmr also covers leaf table transformer case */
func Test_Leaf_Field_Xfmr_Update(t *testing.T) {

        cleanuptbl := map[string]interface{}{"PORTCHANNEL":map[string]interface{}{"PortChannel1":""}}
        url := "/openconfig-interfaces:interfaces/interface[name=PortChannel1]/openconfig-if-aggregate:aggregation/config/openconfig-interfaces-ext:fallback"

        fmt.Println("++++++++++++++  UPDATE Test_Leaf_Field_Xfmr  +++++++++++++")

        patch_payload := "{ \"openconfig-interfaces-ext:fallback\": true}"
        patch_expected := map[string]interface{}{"PORTCHANNEL":map[string]interface{}{"PortChannel1":map[string]interface{}{"fallback":"true"}}}

        t.Run("UPDATE on Leaf Field Xfmr", processSetRequest(url, patch_payload, "PATCH", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify update on Leaf Field Xfmr", verifyDbResult(rclient, "PORTCHANNEL|PortChannel1", patch_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Field_Xfmr_Replace(t *testing.T) {

        cleanuptbl := map[string]interface{}{"PORTCHANNEL":map[string]interface{}{"PortChannel1":""}}
        prereq := map[string]interface{}{"PORTCHANNEL":map[string]interface{}{"PortChannel1":map[string]interface{}{"fallback":"true"}}}
        url := "/openconfig-interfaces:interfaces/interface[name=PortChannel1]/openconfig-if-aggregate:aggregation/config/openconfig-interfaces-ext:fallback"

        fmt.Println("++++++++++++++  Replace Test_Leaf_Field_Xfmr  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        put_payload := "{ \"openconfig-interfaces-ext:fallback\": false}"
        put_expected := map[string]interface{}{"PORTCHANNEL":map[string]interface{}{"PortChannel1":map[string]interface{}{"fallback":"false"}}}

        t.Run("Replace on Leaf Field Xfmr", processSetRequest(url, put_payload, "PUT", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify replace on Leaf Field Xfmr", verifyDbResult(rclient, "PORTCHANNEL|PortChannel1", put_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Field_Xfmr_Delete(t *testing.T) {

        cleanuptbl := map[string]interface{}{"PORTCHANNEL":map[string]interface{}{"PortChannel1":""}}
        prereq := map[string]interface{}{"PORTCHANNEL":map[string]interface{}{"PortChannel1":map[string]interface{}{"fallback":"true"}}}
        url := "/openconfig-interfaces:interfaces/interface[name=PortChannel1]/openconfig-if-aggregate:aggregation/config/openconfig-interfaces-ext:fallback"

        fmt.Println("++++++++++++++  DELETE Test_Leaf_Field_Xfmr  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        delete_expected_map := make(map[string]interface{})

        t.Run("DELETE on Leaf Field Xfmr", processDeleteRequest(url, false))
        time.Sleep(1 * time.Second)
        t.Run("Verify delete on Leaf Field Xfmr", verifyDbResult(rclient, "PORTCHANNEL|PortChannel1", delete_expected_map, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Field_Xfmr_Get(t *testing.T) {

        cleanuptbl := map[string]interface{}{"PORTCHANNEL":map[string]interface{}{"PortChannel1":""}}
        prereq := map[string]interface{}{"PORTCHANNEL":map[string]interface{}{"PortChannel1":map[string]interface{}{"fallback":"true"}}}
        url := "/openconfig-interfaces:interfaces/interface[name=PortChannel1]/openconfig-if-aggregate:aggregation/config/openconfig-interfaces-ext:fallback" 

        fmt.Println("++++++++++++++  Get Test_Leaf_Field_Xfmr  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        get_expected := "{\"openconfig-interfaces-ext:fallback\": true}"

        t.Run("GET on Leaf Field Xfmr", processGetRequest(url, get_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Subtree_Xfmr_Update(t *testing.T) {

        cleanuptbl1 := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan1":""}}
        cleanuptbl2 := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":""}}
        prereq := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan1":map[string]interface{}{"vlanid":"1"}}}
        url := "/openconfig-interfaces:interfaces/interface[name=Vlan1]/subinterfaces/subinterface[index=0]/openconfig-if-ip:ipv4/openconfig-interfaces-ext:sag-ipv4/config/static-anycast-gateway"

        fmt.Println("++++++++++++++  UPDATE Test_Leaf_Subtree_Xfmr  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        patch_payload := "{ \"openconfig-interfaces-ext:static-anycast-gateway\": [ \"1.1.1.1/1\" ]}"
        patch_expected := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":map[string]interface{}{"gwip@":"1.1.1.1/1"}}}

        t.Run("UPDATE on Leaf Subtree Xfmr", processSetRequest(url, patch_payload, "PATCH", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify update on Leaf Subtree Xfmr", verifyDbResult(rclient, "SAG|Vlan1|IPv4", patch_expected, false))

        unloadConfigDB(rclient, cleanuptbl1)
        unloadConfigDB(rclient, cleanuptbl2)
}

func Test_Leaf_Subtree_Xfmr_Replace(t *testing.T) {

        cleanuptbl1 := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan1":""}}
        cleanuptbl2 := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":""}}
        prereq1 := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan1":map[string]interface{}{"vlanid":"1"}}}
        prereq2 := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":map[string]interface{}{"gwip@":"1.1.1.1/1"}}}
        url := "/openconfig-interfaces:interfaces/interface[name=Vlan1]/subinterfaces/subinterface[index=0]/openconfig-if-ip:ipv4/openconfig-interfaces-ext:sag-ipv4/config/static-anycast-gateway"

        fmt.Println("++++++++++++++  Replace Test_Leaf_Subtree_Xfmr  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq1)
        loadConfigDB(rclient, prereq2)

        put_payload := "{ \"openconfig-interfaces-ext:static-anycast-gateway\": [ \"2.2.2.2/2\" ]}"
        put_expected := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":map[string]interface{}{"gwip@":"1.1.1.1/1,2.2.2.2/2"}}}

        t.Run("Replace on Leaf Subtree Xfmr", processSetRequest(url, put_payload, "PUT", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify replace on Leaf Subtree Xfmr", verifyDbResult(rclient, "SAG|Vlan1|IPv4", put_expected, false))

        unloadConfigDB(rclient, cleanuptbl1)
        unloadConfigDB(rclient, cleanuptbl2)
}

func Test_Leaf_Subtree_Xfmr_Delete(t *testing.T) {

        cleanuptbl1 := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan1":""}}
        cleanuptbl2 := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":""}}
        prereq1 := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan1":map[string]interface{}{"vlanid":"1"}}}
        prereq2 := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":map[string]interface{}{"gwip@":"2.2.2.2/2"}}}
        url := "/openconfig-interfaces:interfaces/interface[name=Vlan1]/subinterfaces/subinterface[index=0]/openconfig-if-ip:ipv4/openconfig-interfaces-ext:sag-ipv4/config/static-anycast-gateway[static-anycast-gateway=2.2.2.2/2]"

        fmt.Println("++++++++++++++  DELETE Test_Leaf_Subtree_Xfmr  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq1)
        loadConfigDB(rclient, prereq2)

        delete_expected_map := make(map[string]interface{})

        t.Run("DELETE on Leaf Subtree Xfmr", processDeleteRequest(url, false))
        time.Sleep(1 * time.Second)
        t.Run("Verify delete on Leaf Subtree Xfmr", verifyDbResult(rclient, "SAG|Vlan1|IPv4", delete_expected_map, false))

        unloadConfigDB(rclient, cleanuptbl1)
        unloadConfigDB(rclient, cleanuptbl2)
}

func Test_Leaf_Subtree_Xfmr_Get(t *testing.T) {

        cleanuptbl1 := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan1":""}}
        cleanuptbl2 := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":""}}
        prereq1 := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan1":map[string]interface{}{"vlanid":"1"}}}
        prereq2 := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":map[string]interface{}{"gwip@":"2.2.2.2/2"}}}
        url := "/openconfig-interfaces:interfaces/interface[name=Vlan1]/subinterfaces/subinterface[index=0]/openconfig-if-ip:ipv4/openconfig-interfaces-ext:sag-ipv4/config/static-anycast-gateway"

        fmt.Println("++++++++++++++  Get Test_Leaf_Subtree_Xfmr  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq1)
        loadConfigDB(rclient, prereq2)

        get_expected := "{\"openconfig-interfaces-ext:static-anycast-gateway\": [\"2.2.2.2/2\"]}"

        t.Run("GET on Leaf Subtree Xfmr", processGetRequest(url, get_expected, false))

        unloadConfigDB(rclient, cleanuptbl1)
        unloadConfigDB(rclient, cleanuptbl2)
}

func Test_Leaf_Sonic_Yang_UINT32_Update(t *testing.T) {

        cleanuptbl := map[string]interface{}{"SFLOW_SESSION":map[string]interface{}{"Ethernet0":""}}
        url := "/sonic-sflow:sonic-sflow/SFLOW_SESSION/SFLOW_SESSION_LIST[ifname=Ethernet0]/sample_rate"

        fmt.Println("++++++++++++++  UPDATE Test_Leaf_Sonic_Yang_UINT32  +++++++++++++")

        patch_payload := "{ \"sonic-sflow:sample_rate\": 512}"
        patch_expected := map[string]interface{}{"SFLOW_SESSION":map[string]interface{}{"Ethernet0":map[string]interface{}{"sample_rate":"512"}}}

        t.Run("UPDATE on Leaf Sonic Yang UINT32", processSetRequest(url, patch_payload, "PATCH", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify update on Leaf Sonic Yang UINT32", verifyDbResult(rclient, "SFLOW_SESSION|Ethernet0", patch_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Sonic_Yang_UINT32_Replace(t *testing.T) {

        cleanuptbl := map[string]interface{}{"SFLOW_SESSION":map[string]interface{}{"Ethernet0":""}}
        prereq := map[string]interface{}{"SFLOW_SESSION":map[string]interface{}{"Ethernet0":map[string]interface{}{"sample_rate":"512"}}}
        url := "/sonic-sflow:sonic-sflow/SFLOW_SESSION/SFLOW_SESSION_LIST[ifname=Ethernet0]/sample_rate"

        fmt.Println("++++++++++++++  Replace Test_Leaf_Sonic_Yang_UINT32  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        put_payload := "{ \"sonic-sflow:sample_rate\": 256}"
        put_expected := map[string]interface{}{"SFLOW_SESSION":map[string]interface{}{"Ethernet0":map[string]interface{}{"sample_rate":"256"}}}

        t.Run("Replace on Leaf Sonic Yang UINT32", processSetRequest(url, put_payload, "PUT", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify replace on Leaf Sonic Yang UINT32", verifyDbResult(rclient, "SFLOW_SESSION|Ethernet0", put_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Sonic_Yang_UINT32_Delete(t *testing.T) {

        cleanuptbl := map[string]interface{}{"SFLOW_SESSION":map[string]interface{}{"Ethernet0":""}}
        prereq := map[string]interface{}{"SFLOW_SESSION":map[string]interface{}{"Ethernet0":map[string]interface{}{"sample_rate":"256"}}}
        url := "/sonic-sflow:sonic-sflow/SFLOW_SESSION/SFLOW_SESSION_LIST[ifname=Ethernet0]/sample_rate"

        fmt.Println("++++++++++++++  DELETE Test_Leaf_Sonic_Yang_UINT32  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        delete_expected_map := make(map[string]interface{})

        t.Run("DELETE on Leaf Sonic Yang UINT32", processDeleteRequest(url, false))
        time.Sleep(1 * time.Second)
        t.Run("Verify delete on Leaf Sonic Yang UINT32", verifyDbResult(rclient, "SFLOW_SESSION|Ethernet0", delete_expected_map, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Sonic_Yang_UINT32_Get(t *testing.T) {

        cleanuptbl := map[string]interface{}{"SFLOW_SESSION":map[string]interface{}{"Ethernet0":""}}
        prereq := map[string]interface{}{"SFLOW_SESSION":map[string]interface{}{"Ethernet0":map[string]interface{}{"sample_rate":"256"}}}
        url := "/sonic-sflow:sonic-sflow/SFLOW_SESSION/SFLOW_SESSION_LIST[ifname=Ethernet0]/sample_rate"

        fmt.Println("++++++++++++++  Get Test_Leaf_Sonic_Yang_UINT32  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        get_expected := "{\"sonic-sflow:sample_rate\": 256}"

        t.Run("GET on Leaf Sonic Yang UINT32", processGetRequest(url, get_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Ref_Sonic_Yang_Create(t *testing.T) {

        cleanuptbl1 := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan1":""}}
        cleanuptbl2 := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":""}}
        prereq := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan1":map[string]interface{}{"vlanid":"1"}}}
        url := "/sonic-sag:sonic-sag/SAG/SAG_LIST[ifname=Vlan1][table_distinguisher=IPv4]"

        fmt.Println("++++++++++++++  CREATE Test_Leaf_Ref_Sonic_Yang  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        post_payload := "{ \"sonic-sag:gwip\": [ \"2.2.2.2/2\" ]}"
        post_expected := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":map[string]interface{}{"gwip@":"2.2.2.2/2"}}}

        t.Run("CREATE on Leaf Ref Sonic Yang", processSetRequest(url, post_payload, "POST", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify create on Leaf Ref Sonic Yang", verifyDbResult(rclient, "SAG|Vlan1|IPv4", post_expected, false))

        unloadConfigDB(rclient, cleanuptbl1)
        unloadConfigDB(rclient, cleanuptbl2)
}

func Test_Leaf_Ref_Sonic_Yang_Update(t *testing.T) {

        cleanuptbl1 := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan1":""}}
        cleanuptbl2 := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":""}}
        prereq := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan1":map[string]interface{}{"vlanid":"1"}}}
        url := "/sonic-sag:sonic-sag/SAG/SAG_LIST[ifname=Vlan1][table_distinguisher=IPv4]/gwip"

        fmt.Println("++++++++++++++  UPDATE Test_Leaf_Ref_Sonic_Yang  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        patch_payload := "{ \"sonic-sag:gwip\": [ \"2.2.2.2/2\" ]}"
        patch_expected := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":map[string]interface{}{"gwip@":"2.2.2.2/2"}}}

        t.Run("UPDATE on Leaf Ref Sonic Yang", processSetRequest(url, patch_payload, "PATCH", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify update on Leaf Ref Sonic Yang", verifyDbResult(rclient, "SAG|Vlan1|IPv4", patch_expected, false))

        unloadConfigDB(rclient, cleanuptbl1)
        unloadConfigDB(rclient, cleanuptbl2)
}

func Test_Leaf_Ref_Sonic_Yang_Replace(t *testing.T) {

        cleanuptbl1 := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan1":""}}
        cleanuptbl2 := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":""}}
        prereq1 := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan1":map[string]interface{}{"vlanid":"1"}}}
        prereq2 := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":map[string]interface{}{"gwip@":"1.1.1.1/1"}}}
        url := "/sonic-sag:sonic-sag/SAG/SAG_LIST[ifname=Vlan1][table_distinguisher=IPv4]/gwip"

        fmt.Println("++++++++++++++  Replace Test_Leaf_Ref_Sonic_Yang  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq1)
        loadConfigDB(rclient, prereq2)

        put_payload := "{ \"sonic-sag:gwip\": [ \"2.2.2.2/2\" ]}"
        put_expected := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":map[string]interface{}{"gwip@":"2.2.2.2/2"}}}

        t.Run("Replace on Leaf Ref Sonic Yang", processSetRequest(url, put_payload, "PUT", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify replace on Leaf Ref Sonic Yang", verifyDbResult(rclient, "SAG|Vlan1|IPv4", put_expected, false))

        unloadConfigDB(rclient, cleanuptbl1)
        unloadConfigDB(rclient, cleanuptbl2)
}

func Test_Leaf_Ref_Sonic_Yang_Delete(t *testing.T) {

        cleanuptbl1 := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan1":""}}
        cleanuptbl2 := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":""}}
        prereq1 := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan1":map[string]interface{}{"vlanid":"1"}}}
        prereq2 := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":map[string]interface{}{"gwip@":"1.1.1.1/1"}}}
        url := "/sonic-sag:sonic-sag/SAG/SAG_LIST[ifname=Vlan1][table_distinguisher=IPv4]/gwip"

        fmt.Println("++++++++++++++  DELETE Test_Leaf_Ref_Sonic_Yang  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq1)
        loadConfigDB(rclient, prereq2)

        delete_expected_map := make(map[string]interface{})

        t.Run("DELETE on Leaf Ref Sonic Yang", processDeleteRequest(url, false))
        time.Sleep(1 * time.Second)
        t.Run("Verify delete on Leaf Ref Sonic Yang", verifyDbResult(rclient, "SAG|Vlan1|IPv4", delete_expected_map, false))

        unloadConfigDB(rclient, cleanuptbl1)
        unloadConfigDB(rclient, cleanuptbl2)
}

func Test_Leaf_Ref_Sonic_Yang_Get(t *testing.T) {

        cleanuptbl1 := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan1":""}}
        cleanuptbl2 := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":""}}
        prereq1 := map[string]interface{}{"VLAN":map[string]interface{}{"Vlan1":map[string]interface{}{"vlanid":"1"}}}
        prereq2 := map[string]interface{}{"SAG":map[string]interface{}{"Vlan1|IPv4":map[string]interface{}{"gwip@":"1.1.1.1/1"}}}
        url := "/sonic-sag:sonic-sag/SAG/SAG_LIST[ifname=Vlan1][table_distinguisher=IPv4]/gwip"

        fmt.Println("++++++++++++++  Get Test_Leaf_Ref_Sonic_Yang  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq1)
        loadConfigDB(rclient, prereq2)

        get_expected := "{\"sonic-sag:gwip\": [\"1.1.1.1/1\"]}"

        t.Run("GET on Leaf Ref Sonic Yang", processGetRequest(url, get_expected, false))

        unloadConfigDB(rclient, cleanuptbl1)
        unloadConfigDB(rclient, cleanuptbl2)
}

func Test_Leaf_OC_Yang_Choice_Case_Update(t *testing.T) {

        cleanuptbl := map[string]interface{}{"NAT_POOL":map[string]interface{}{"pool1":""}}
        url := "/openconfig-nat:nat/instances/instance[id=0]/nat-pool/nat-pool-entry[pool-name=pool1]/config/IP-ADDRESS"

        fmt.Println("++++++++++++++  UPDATE Test_Leaf_OC_Yang_Choice_Case  +++++++++++++")

        patch_payload := "{ \"openconfig-nat:IP-ADDRESS\": \"1.1.1.1\"}"
        patch_expected := map[string]interface{}{"NAT_POOL":map[string]interface{}{"pool1":map[string]interface{}{"nat_ip":"1.1.1.1"}}}

        t.Run("UPDATE on Leaf OC Yang Choice Case", processSetRequest(url, patch_payload, "PATCH", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify update on Leaf OC Yang Choice Case", verifyDbResult(rclient, "NAT_POOL|pool1", patch_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_OC_Yang_Choice_Case_Replace(t *testing.T) {

        cleanuptbl := map[string]interface{}{"NAT_POOL":map[string]interface{}{"pool1":""}}
        prereq := map[string]interface{}{"NAT_POOL":map[string]interface{}{"pool1":map[string]interface{}{"nat_ip":"1.1.1.1"}}}
        url := "/openconfig-nat:nat/instances/instance[id=0]/nat-pool/nat-pool-entry[pool-name=pool1]/config/IP-ADDRESS"

        fmt.Println("++++++++++++++  Replace Test_Leaf_OC_Yang_Choice_Case  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        put_payload := "{ \"openconfig-nat:IP-ADDRESS\": \"2.2.2.2\"}"
        put_expected := map[string]interface{}{"NAT_POOL":map[string]interface{}{"pool1":map[string]interface{}{"nat_ip":"2.2.2.2"}}}

        t.Run("Replace on Leaf OC Yang Choice Case", processSetRequest(url, put_payload, "PUT", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify replace on Leaf OC Yang Choice Case", verifyDbResult(rclient, "NAT_POOL|pool1", put_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_OC_Yang_Choice_Case_Delete(t *testing.T) {

        cleanuptbl := map[string]interface{}{"NAT_POOL":map[string]interface{}{"pool1":""}}
        prereq := map[string]interface{}{"NAT_POOL":map[string]interface{}{"pool1":map[string]interface{}{"nat_ip":"1.1.1.1"}}}
        url := "/openconfig-nat:nat/instances/instance[id=0]/nat-pool/nat-pool-entry[pool-name=pool1]/config/IP-ADDRESS"

        fmt.Println("++++++++++++++  DELETE Test_Leaf_OC_Yang_Choice_Case  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        delete_expected_map := make(map[string]interface{})

        t.Run("DELETE on Leaf OC Yang Choice Case", processDeleteRequest(url, false))
        time.Sleep(1 * time.Second)
        t.Run("Verify delete on Leaf OC Yang Choice Case", verifyDbResult(rclient, "NAT_POOL|pool1", delete_expected_map, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_OC_Yang_Choice_Case_Get(t *testing.T) {

        cleanuptbl := map[string]interface{}{"NAT_POOL":map[string]interface{}{"pool1":""}}
        prereq := map[string]interface{}{"NAT_POOL":map[string]interface{}{"pool1":map[string]interface{}{"nat_ip":"1.1.1.1"}}}
        url := "/openconfig-nat:nat/instances/instance[id=0]/nat-pool/nat-pool-entry[pool-name=pool1]/config/IP-ADDRESS"

        fmt.Println("++++++++++++++  Get Test_Leaf_OC_Yang_Choice_Case  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        get_expected := "{\"openconfig-nat:IP-ADDRESS\": \"1.1.1.1\"}"

        t.Run("GET on Leaf OC Yang Choice Case", processGetRequest(url, get_expected, false))

        unloadConfigDB(rclient, cleanuptbl)
}

func Test_Leaf_Sonic_Yang_Choice_Case_Update(t *testing.T) {

        cleanuptbl1 := map[string]interface{}{"ACL_TABLE":map[string]interface{}{"acl1":""}}
        cleanuptbl2 := map[string]interface{}{"ACL_RULE":map[string]interface{}{"acl1|rule1":""}}
        prereq := map[string]interface{}{"ACL_TABLE":map[string]interface{}{"acl1":map[string]interface{}{"ports@":"Ethernet0","stage":"INGRESS","type":"MIRROR","policy_desc":"descr"}}}
        url := "/sonic-acl:sonic-acl/ACL_RULE/ACL_RULE_LIST[aclname=acl1][rulename=rule1]/SRC_IP"

        fmt.Println("++++++++++++++  UPDATE Test_Leaf_Sonic_Yang_Choice_Case  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq)

        patch_payload := "{ \"sonic-acl:SRC_IP\": \"1.1.1.1/1\", \"sonic-acl:DST_IP\": \"2.2.2.2/2\"}"
        patch_expected := map[string]interface{}{"ACL_RULE":map[string]interface{}{"acl1|rule1":map[string]interface{}{"DST_IP":"2.2.2.2/2","SRC_IP":"1.1.1.1/1"}}}

        t.Run("UPDATE on Leaf Sonic Yang Choice Case", processSetRequest(url, patch_payload, "PATCH", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify update on Leaf Sonic Yang Choice Case", verifyDbResult(rclient, "ACL_RULE|acl1|rule1", patch_expected, false))

        unloadConfigDB(rclient, cleanuptbl1)
        unloadConfigDB(rclient, cleanuptbl2)
}

func Test_Leaf_Sonic_Yang_Choice_Case_Replace(t *testing.T) {

        cleanuptbl1 := map[string]interface{}{"ACL_TABLE":map[string]interface{}{"acl1":""}}
        cleanuptbl2 := map[string]interface{}{"ACL_RULE":map[string]interface{}{"acl1|rule1":""}}
        prereq1 := map[string]interface{}{"ACL_TABLE":map[string]interface{}{"acl1":map[string]interface{}{"ports@":"Ethernet0","stage":"INGRESS","type":"MIRROR","policy_desc":"descr"}}}
        prereq2 := map[string]interface{}{"ACL_RULE":map[string]interface{}{"acl1|rule1":map[string]interface{}{"DST_IP":"2.2.2.2/2","SRC_IP":"1.1.1.1/1"}}}
        url := "/sonic-acl:sonic-acl/ACL_RULE/ACL_RULE_LIST[aclname=acl1][rulename=rule1]/SRC_IP"

        fmt.Println("++++++++++++++  Replace Test_Leaf_Sonic_Yang_Choice_Case  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq1)
        loadConfigDB(rclient, prereq2)

        put_payload := "{ \"sonic-acl:SRC_IP\": \"3.3.3.3/3\"}"
        put_expected := map[string]interface{}{"ACL_RULE":map[string]interface{}{"acl1|rule1":map[string]interface{}{"SRC_IP":"3.3.3.3/3"}}}

        t.Run("Replace on Leaf Sonic Yang Choice Case", processSetRequest(url, put_payload, "PUT", false))
        time.Sleep(1 * time.Second)
        t.Run("Verify replace on Leaf Sonic Yang Choice Case", verifyDbResult(rclient, "ACL_RULE|acl1|rule1", put_expected, false))

        unloadConfigDB(rclient, cleanuptbl1)
        unloadConfigDB(rclient, cleanuptbl2)
}

func Test_Leaf_Sonic_Yang_Choice_Case_Delete(t *testing.T) {

        cleanuptbl1 := map[string]interface{}{"ACL_TABLE":map[string]interface{}{"acl1":""}}
        cleanuptbl2 := map[string]interface{}{"ACL_RULE":map[string]interface{}{"acl1|rule1":""}}
        prereq1 := map[string]interface{}{"ACL_TABLE":map[string]interface{}{"acl1":map[string]interface{}{"ports@":"Ethernet0","stage":"INGRESS","type":"MIRROR","policy_desc":"descr"}}}
        prereq2 := map[string]interface{}{"ACL_RULE":map[string]interface{}{"acl1|rule1":map[string]interface{}{"DST_IP":"2.2.2.2/2","SRC_IP":"1.1.1.1/1"}}}
        url := "/sonic-acl:sonic-acl/ACL_RULE/ACL_RULE_LIST[aclname=acl1][rulename=rule1]/SRC_IP"

        fmt.Println("++++++++++++++  DELETE Test_Leaf_Sonic_Yang_Choice_Case  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq1)
        loadConfigDB(rclient, prereq2)

        delete_expected_map := map[string]interface{}{"ACL_RULE":map[string]interface{}{"acl1|rule1":map[string]interface{}{"DST_IP":"2.2.2.2/2"}}}

        t.Run("DELETE on Leaf Sonic Yang Choice Case", processDeleteRequest(url, false))
        time.Sleep(1 * time.Second)
        t.Run("Verify delete on Leaf Sonic Yang Choice Case", verifyDbResult(rclient, "ACL_RULE|acl1|rule1", delete_expected_map, false))

        unloadConfigDB(rclient, cleanuptbl1)
        unloadConfigDB(rclient, cleanuptbl2)
}

func Test_Leaf_Sonic_Yang_Choice_Case_Get(t *testing.T) {

        cleanuptbl1 := map[string]interface{}{"ACL_TABLE":map[string]interface{}{"acl1":""}}
        cleanuptbl2 := map[string]interface{}{"ACL_RULE":map[string]interface{}{"acl1|rule1":""}}
        prereq1 := map[string]interface{}{"ACL_TABLE":map[string]interface{}{"acl1":map[string]interface{}{"ports@":"Ethernet0","stage":"INGRESS","type":"MIRROR","policy_desc":"descr"}}}
        prereq2 := map[string]interface{}{"ACL_RULE":map[string]interface{}{"acl1|rule1":map[string]interface{}{"DST_IP":"2.2.2.2/2","SRC_IP":"1.1.1.1/1"}}}
        url := "/sonic-acl:sonic-acl/ACL_RULE/ACL_RULE_LIST[aclname=acl1][rulename=rule1]/SRC_IP"

        fmt.Println("++++++++++++++  Get Test_Leaf_Sonic_Yang_Choice_Case  +++++++++++++")

        // Setup - Prerequisite
        loadConfigDB(rclient, prereq1)
        loadConfigDB(rclient, prereq2)

        get_expected := "{\"sonic-acl:SRC_IP\": \"1.1.1.1/1\"}"

        t.Run("GET on Leaf Sonic Yang Choice Case", processGetRequest(url, get_expected, false))

        unloadConfigDB(rclient, cleanuptbl1)
        unloadConfigDB(rclient, cleanuptbl2)
}
