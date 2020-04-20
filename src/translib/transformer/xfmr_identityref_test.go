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

func Test_IdentityRef(t *testing.T) {
        fmt.Println("\n\n+++++++++++++ Performing Yang IdentityRef Cases ++++++++++++")
        var prereq_map map[string]interface{}
        var expected_map map[string]interface{}
        var url, url_body_json string

        /** IdentityRef processing Create**/
        prereq_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"default":map[string]interface{}{
                                                                                                  "NULL": "NULL"}},
                                            "VRF":map[string]interface{}{"default":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        expected_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"default":map[string]interface{}{
                                                                                                  "confed_id": "4294",
                                                                                                  "confed_peers@": "4294"}}}
        unloadConfigDB(rclient, prereq_map)
        url = "/openconfig-network-instance:network-instances/network-instance[name=default]/protocols/protocol[identifier=BGP][name=bgp]/bgp/global/confederation/config"
        url_body_json = "{\"openconfig-network-instance:identifier\":4294,\"openconfig-network-instance:member-as\":[4294]}"
        t.Run("IdentityRef create.", processSetRequest(url, url_body_json, "POST", false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Verify IdentityRef create.", verifyDbResult(rclient, "BGP_GLOBALS|default", expected_map, false))
        unloadConfigDB(rclient, prereq_map)
        /*********************/

	/** IdentityRef processing update**/
        prereq_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"default":map[string]interface{}{
                                                                                                  "confed_id": "4292",
                                                                                                  "confed_peers@": "4294"}},
                                            "VRF":map[string]interface{}{"default":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        expected_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"default":map[string]interface{}{
                                                                                                  "confed_id": "4293",
                                                                                                  "confed_peers@": "4294,1,4295"}}}
        loadConfigDB(rclient, prereq_map)
        url = "/openconfig-network-instance:network-instances/network-instance[name=default]/protocols/protocol[identifier=BGP][name=bgp]/bgp/global/confederation/config"
        url_body_json = "{\"openconfig-network-instance:config\":{\"identifier\":4293,\"member-as\":[4294,1,4295]}}"
        t.Run("IdentityRef update.", processSetRequest(url, url_body_json, "PATCH", false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Verify IdentityRef update.", verifyDbResult(rclient, "BGP_GLOBALS|default", expected_map, false))
        unloadConfigDB(rclient, prereq_map)
        /*********************/


	/** IdentityRef processing replace**/
        prereq_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"default":map[string]interface{}{
                                                                                                  "confed_id": "4292",
                                                                                                  "confed_peers@": "4294"}},
                                            "VRF":map[string]interface{}{"default":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        expected_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"default":map[string]interface{}{
                                                                                                  "confed_id": "4293",
                                                                                                  "confed_peers@": "4294,1,4295"}}}
        loadConfigDB(rclient, prereq_map)
        url = "/openconfig-network-instance:network-instances/network-instance[name=default]/protocols/protocol[identifier=BGP][name=bgp]/bgp/global/confederation/config"
        url_body_json = "{\"openconfig-network-instance:config\":{\"identifier\":4293,\"member-as\":[4294,1,4295]}}"
        t.Run("IdentityRef replace.", processSetRequest(url, url_body_json, "PUT", false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Verify IdentityRef replace.", verifyDbResult(rclient, "BGP_GLOBALS|default", expected_map, false))
        unloadConfigDB(rclient, prereq_map)
        /*********************/


        fmt.Println("\n\n+++++++++++++ Done Performing Yang IdentityRef Cases ++++++++++++")
}

