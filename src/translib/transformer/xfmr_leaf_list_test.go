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

