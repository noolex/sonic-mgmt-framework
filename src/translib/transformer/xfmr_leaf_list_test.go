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
	"io/ioutil"
	"testing"
	"time"
)

func Test_LeafList(t *testing.T) {

	preRequisite , err := ioutil.ReadFile("testdata/snmp_vacm_view_db.json")
	if err != nil {
		fmt.Printf("read file err: %v",  err)
	}
	snmp_vacm_view_map := loadConfig("", preRequisite)
	unloadConfigDB(rclient, snmp_vacm_view_map)

	url := "/ietf-snmp:snmp/vacm/view[name=TestVacmView1]"

	// usecase: Leaf-list one-to-one mapping
	t.Run("Leaf-list one-to-one mapping", processSetRequestFromFile(url, "testdata/snmp_vacm_view_body.json", "POST", false))
	time.Sleep(1 * time.Second)
	t.Run("Verify Leaf-list one-to-one mapping", verifyDbResult(rclient, "SNMP_SERVER_VIEW|TestVacmView1", snmp_vacm_view_map, false))

	// usecase: Leaf-list merge (OC-YANG)

	// usecase: Leaf-list create (SONiC-YANG)

	unloadConfigDB(rclient, snmp_vacm_view_map)
}


func Test_LeafList_DataTypeConversion_SonicYang(t *testing.T) {
        fmt.Println("\n\n+++++++++++++ Performing Leaf-list Data-Type Conversion getting called Sonic Yang Cases ++++++++++++")
        var prereq_map map[string]interface{}
        var expected_map map[string]interface{}
        var url, url_body_json, expected_get_json string

	/** Data-type conversion getting called on leaf-list create**/
        prereq_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "ports@": "Ethernet0",
                                                                                          "stage": "INGRESS",
                                                                                          "type": "L3"}}}
        expected_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "ports@": "Ethernet0",
                                                                                          "stage": "INGRESS",
                                                                                          "type": "L3"}}}
        unloadConfigDB(rclient, prereq_map)
        url = "/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST[aclname=MyACL1_ACL_IPV4]"
        url_body_json = "{\"sonic-acl:stage\":\"INGRESS\",\"sonic-acl:type\":\"L3\",\"sonic-acl:ports\":[\"Ethernet0\"]}"
        t.Run("Data-type conversion create.", processSetRequest(url, url_body_json, "POST", false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Verify Data-type conversion create.", verifyDbResult(rclient, "ACL_TABLE|MyACL1_ACL_IPV4", expected_map, false))
        unloadConfigDB(rclient, prereq_map)
        /*********************/


        /** Data-type conversion getting called on leaf-list Update**/
        prereq_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "ports@": "Ethernet0,Ethernet8",
										          "stage": "INGRESS",
										          "type": "L3"}}}
        expected_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "ports@": "Ethernet0,Ethernet8,Ethernet124",
                                                                                          "stage": "INGRESS",
                                                                                          "type": "L3"}}}
        loadConfigDB(rclient, prereq_map)
	url = "/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST[aclname=MyACL1_ACL_IPV4]/ports"
        url_body_json = "{\"sonic-acl:ports\":[\"Ethernet0\",\"Ethernet124\",\"Ethernet8\"]}"
        t.Run("Data-type conversion update.", processSetRequest(url, url_body_json, "PATCH", false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Verify Data-type conversion update.", verifyDbResult(rclient, "ACL_TABLE|MyACL1_ACL_IPV4", expected_map, false))
        unloadConfigDB(rclient, prereq_map)
        /*********************/

        /** Data-type conversion getting called on leaf-list delete **/
        prereq_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "ports@": "Ethernet0,Ethernet8,Ethernet124",
										          "stage": "INGRESS",
										          "type": "L3"}}}
        expected_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "ports@": "Ethernet0,Ethernet124",
                                                                                          "stage": "INGRESS",
                                                                                          "type": "L3"}}}
        loadConfigDB(rclient, prereq_map)
	url = "/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST[aclname=MyACL1_ACL_IPV4]/ports[ports=Ethernet8]"
        t.Run("Data-type conversion delete.", processDeleteRequest(url, false))
        time.Sleep(1 * time.Second)
        t.Run("Verify Data-type conversion delete.", verifyDbResult(rclient, "ACL_TABLE|MyACL1_ACL_IPV4", expected_map, false))
        unloadConfigDB(rclient, prereq_map)
        /*********************/

        /** Data-type conversion getting called on leaf-list get**/
        prereq_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "ports@": "Ethernet8,Ethernet16",
										          "stage": "INGRESS",
										          "type": "L3"}}}

	url = "/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST[aclname=MyACL1_ACL_IPV4]/ports"
        expected_get_json = "{\"sonic-acl:ports\":[\"Ethernet8\",\"Ethernet16\"]}"
        loadConfigDB(rclient, prereq_map)
        t.Run("FieldXfmr leaf-list get.", processGetRequest(url, expected_get_json, false))
        time.Sleep(1 * time.Second)
        unloadConfigDB(rclient, prereq_map)
        /*********************/

        fmt.Println("\n\n+++++++++++++ Done Performing Leaf-list Data-Type Conversion getting called Sonic Yang Cases ++++++++++++")
}

func Test_LeafList_CRU_SonicYang(t *testing.T) {
        fmt.Println("\n\n+++++++++++++ Performing Leaf-list CRU Sonic Yang Cases ++++++++++++")
        var prereq_map map[string]interface{}
        var expected_map map[string]interface{}
        var url, url_body_json string

        /** sonic yang leaf-list create**/
        expected_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "ports@": "Ethernet0",
                                                                                          "stage": "INGRESS",
                                                                                          "type": "L3"}}}
        unloadConfigDB(rclient, expected_map)
        url = "/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST[aclname=MyACL1_ACL_IPV4]"
        url_body_json = "{\"sonic-acl:stage\":\"INGRESS\",\"sonic-acl:type\":\"L3\",\"sonic-acl:ports\":[\"Ethernet0\"]}"
        t.Run("leaf-list create.", processSetRequest(url, url_body_json, "POST", false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Verify leaf-list create.", verifyDbResult(rclient, "ACL_TABLE|MyACL1_ACL_IPV4", expected_map, false))
        unloadConfigDB(rclient, expected_map)
        /*********************/


        /**  sonic yang leaf-list Update/merge**/
        prereq_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "ports@": "Ethernet0,Ethernet8",
                                                                                          "stage": "INGRESS",
                                                                                          "type": "L3"}}}
        expected_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "ports@": "Ethernet0,Ethernet8,Ethernet124",
                                                                                          "stage": "INGRESS",
                                                                                          "type": "L3"}}}
        loadConfigDB(rclient, prereq_map)
        url = "/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST[aclname=MyACL1_ACL_IPV4]/ports"
        url_body_json = "{\"sonic-acl:ports\":[\"Ethernet0\",\"Ethernet124\",\"Ethernet8\"]}"
        t.Run("leaf-list update/merge.", processSetRequest(url, url_body_json, "PATCH", false, nil))
        t.Run("Verify leaf-list update/merge.", verifyDbResult(rclient, "ACL_TABLE|MyACL1_ACL_IPV4", expected_map, false))
        unloadConfigDB(rclient, prereq_map)

        fmt.Println("\n\n+++++++++++++ Done Performing Leaf-list CRU Sonic Yang Cases ++++++++++++")
}

func Test_LeafList_Delete_SonicYang(t *testing.T) {
        fmt.Println("\n\n+++++++++++++ Performing Leaf-list Deletion Sonic Yang Cases ++++++++++++")
        var prereq_map map[string]interface{}
        var expected_map map[string]interface{}
        var url string

        /** delete specific item from leaf-list **/
        prereq_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "ports@": "Ethernet0,Ethernet8,Ethernet124",
                                                                                          "stage": "INGRESS",
                                                                                          "type": "L3"}}}
        expected_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "ports@": "Ethernet0,Ethernet124",
                                                                                          "stage": "INGRESS",
                                                                                          "type": "L3"}}}
        loadConfigDB(rclient, prereq_map)
        url = "/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST[aclname=MyACL1_ACL_IPV4]/ports[ports=Ethernet8]"
        t.Run("Delete an item in leaf-list.", processDeleteRequest(url, false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Delete an item in leaf-list.", verifyDbResult(rclient, "ACL_TABLE|MyACL1_ACL_IPV4", expected_map, false))
        unloadConfigDB(rclient, prereq_map)
	/***********************************/

	/** Delete specific item from leaf-list, when leaf-list does not exist in DB **/
	prereq_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "type": "L3"}}}
        expected_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "type": "L3"}}}
        loadConfigDB(rclient, prereq_map)
        url = "/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST[aclname=MyACL1_ACL_IPV4]/ports[ports=Ethernet8]"

        t.Run("Delete an item when leaf-list doesn't exist in DB.", processDeleteRequest(url, false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Verify Delete an item when leaf-list doesn't exist in DB.", verifyDbResult(rclient, "ACL_TABLE|MyACL1_ACL_IPV4", expected_map, false))
        unloadConfigDB(rclient, prereq_map)
        /*********************/

        /** delete an item from leaf-list which happens to be the only element in leaf-lis in DB. **/
	prereq_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "ports@": "Ethernet8",
                                                                                          "stage": "INGRESS",
                                                                                          "type": "L3"}}}
        expected_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "stage": "INGRESS",
                                                                                          "type": "L3"}}}
        loadConfigDB(rclient, prereq_map)
        url = "/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST[aclname=MyACL1_ACL_IPV4]/ports[ports=Ethernet8]"
        t.Run("Delete an item which is the only one in leaf-list.", processDeleteRequest(url, false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Verify Delete an item which is the only one in leaf-list.", verifyDbResult(rclient, "ACL_TABLE|MyACL1_ACL_IPV4", expected_map, false))
        unloadConfigDB(rclient, prereq_map)
        /*********************/

        /** delete entire leaf-list. **/
	prereq_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "ports@": "Ethernet8",
                                                                                          "stage": "INGRESS",
                                                                                          "type": "L3"}}}
        expected_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "stage": "INGRESS",
                                                                                          "type": "L3"}}}
        loadConfigDB(rclient, prereq_map)
        url = "/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST[aclname=MyACL1_ACL_IPV4]/ports"
        t.Run("Delete entire leaf-list.", processDeleteRequest(url, false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Delete entire leaf-list.", verifyDbResult(rclient, "ACL_TABLE|MyACL1_ACL_IPV4", expected_map, false))
        unloadConfigDB(rclient, prereq_map)
        /*********************/

        /** delete entire leaf-list, when leaf-list doesn't exist in DB. **/
	prereq_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "type": "L3"}}}
        expected_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "type": "L3"}}}
        loadConfigDB(rclient, prereq_map)
        url = "/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST[aclname=MyACL1_ACL_IPV4]/ports"
        t.Run("Delete leaf-list not there in DB.", processDeleteRequest(url, false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Delete leaf-list not there in DB.", verifyDbResult(rclient, "ACL_TABLE|MyACL1_ACL_IPV4", expected_map, false))
        unloadConfigDB(rclient, prereq_map)

        fmt.Println("+++++++++++++ Done!!! Performing Leaf-list Deletion Sonic Yang Cases ++++++++++++")
}

func Test_LeafList_Get_SonicYang(t *testing.T) {
        fmt.Println("\n\n+++++++++++++ Performing Leaf-list Get Sonic Yang Cases ++++++++++++")
        var prereq_map map[string]interface{}
        var url, expected_get_json string

        /** leaf-list get when leaf-list doesn't exist in DB(valid field in yang)**/
        prereq_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "stage": "INGRESS",
                                                                                          "type": "L3"}}}

        url = "/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST[aclname=MyACL1_ACL_IPV4]/ports"
        expected_get_json = "{}"
        loadConfigDB(rclient, prereq_map)
        t.Run("Get leaf-list not there in DB.", processGetRequest(url, expected_get_json, false))
        time.Sleep(1 * time.Second)
        unloadConfigDB(rclient, prereq_map)
        /*********************/

        /** empty-string leaf-list get**/
        prereq_map = map[string]interface{}{"ACL_TABLE":map[string]interface{}{"MyACL1_ACL_IPV4":map[string]interface{}{
                                                                                          "ports@": "",
                                                                                          "stage": "INGRESS",
                                                                                          "type": "L3"}}}
        url = "/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST[aclname=MyACL1_ACL_IPV4]/ports"
        expected_get_json = "{}"
        loadConfigDB(rclient, prereq_map)
        t.Run("Get leaf-list empty string in DB.", processGetRequest(url, expected_get_json, false))
        time.Sleep(1 * time.Second)
        unloadConfigDB(rclient, prereq_map)
        /*********************/

        fmt.Println("\n\n+++++++++++++ Done Performing Leaf-list Get Sonic Yang Cases ++++++++++++")
}

