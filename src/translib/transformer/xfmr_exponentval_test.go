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

func Test_FieldExpntVal_OCYang(t *testing.T) {
        fmt.Println("\n\n+++++++++++++ Performing Field Exponent value OC Yang Cases ++++++++++++")
        var prereq_map map[string]interface{}
        var expected_map map[string]interface{}
        var url, url_body_json string

        /** Field Exponent value processing Create**/
        prereq_map_bgp_globals := map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                                  "NULL": "NULL"}}}
        prereq_map_vrf :=  map[string]interface{}{"VRF":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                               "NULL": "NULL"}}}

        expected_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "confed_id": "4294967292",
                                                                                                  "confed_peers@": "4294967291"}}}
        unloadConfigDB(rclient, prereq_map_bgp_globals)
        loadConfigDB(rclient, prereq_map_vrf)
        url = "/openconfig-network-instance:network-instances/network-instance[name=Vrf_test1]/protocols/protocol[identifier=BGP][name=bgp]/bgp/global/confederation/config"
        url_body_json = "{\"openconfig-network-instance:identifier\":4294967292,\"openconfig-network-instance:member-as\":[4294967291]}"
        t.Run("Field Exponent value create.", processSetRequest(url, url_body_json, "POST", false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Verify Field Exponent value create.", verifyDbResult(rclient, "BGP_GLOBALS|Vrf_test1", expected_map, false))
        unloadConfigDB(rclient, prereq_map)
        /*********************/

	/** Field Exponent value processing update**/
        prereq_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "confed_id": "4294967292",
                                                                                                  "confed_peers@": "4294967294"}},
					     "VRF":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        expected_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "confed_id": "4294967293",
                                                                                                  "confed_peers@": "4294967294,1,4294967295"}}}
        loadConfigDB(rclient, prereq_map)
        url = "/openconfig-network-instance:network-instances/network-instance[name=Vrf_test1]/protocols/protocol[identifier=BGP][name=bgp]/bgp/global/confederation/config"
        url_body_json = "{\"openconfig-network-instance:config\":{\"identifier\":4294967293,\"member-as\":[4294967294,1,4294967295]}}"
        t.Run("Field Exponent value update.", processSetRequest(url, url_body_json, "PATCH", false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Verify Field Exponent value update.", verifyDbResult(rclient, "BGP_GLOBALS|Vrf_test1", expected_map, false))
        unloadConfigDB(rclient, prereq_map)
        /*********************/


	/** Field Exponent value processing replace**/
        prereq_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "confed_id": "4294967292",
                                                                                                  "confed_peers@": "4294967294"}},
					     "VRF":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        expected_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "confed_id": "4294967293",
                                                                                                  "confed_peers@": "4294967294,1,4294967295"}}}
        loadConfigDB(rclient, prereq_map)
        url = "/openconfig-network-instance:network-instances/network-instance[name=Vrf_test1]/protocols/protocol[identifier=BGP][name=bgp]/bgp/global/confederation/config"
        url_body_json = "{\"openconfig-network-instance:config\":{\"identifier\":4294967293,\"member-as\":[4294967294,1,4294967295]}}"
        t.Run("Field Exponent value replace.", processSetRequest(url, url_body_json, "PUT", false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Verify Field Exponent value replace.", verifyDbResult(rclient, "BGP_GLOBALS|Vrf_test1", expected_map, false))
        unloadConfigDB(rclient, prereq_map)
        /*********************/

	/** Field Exponent value processing get**/
        prereq_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                 "confed_peers@": "4294967294"}},
					     "VRF":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        loadConfigDB(rclient, prereq_map)
        expected_get_json := "{\"openconfig-network-instance:member-as\":[4294967294]}"
        url = "/openconfig-network-instance:network-instances/network-instance[name=Vrf_test1]/protocols/protocol[identifier=BGP][name=bgp]/bgp/global/confederation/config/member-as"
        t.Run("Field Exponent value get.", processGetRequest(url, expected_get_json, false))
        time.Sleep(1 * time.Second)
        unloadConfigDB(rclient, prereq_map)

        fmt.Println("\n\n+++++++++++++ Done Performing Field Exponent Value OC Yang Cases ++++++++++++")
}

func Test_FieldExpntVal_SonicYang(t *testing.T) {
        fmt.Println("\n\n+++++++++++++ Performing Field Exponent value Sonic Yang Cases ++++++++++++")
        var prereq_map map[string]interface{}
        var expected_map map[string]interface{}
        var url, url_body_json string

        /** Field Exponent value processing Create**/
        prereq_map_bgp_globals := map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        prereq_map_vrf :=  map[string]interface{}{"VRF":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        expected_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "keepalive": "123",
                                                                                                  "local_asn": "4294967295",
                                                                                                  "always_compare_med": "true",
                                                                                                  "confed_peers@": "4294967294,1,4294967295"}}}
        unloadConfigDB(rclient, prereq_map_bgp_globals)
        loadConfigDB(rclient, prereq_map_vrf)
	url = "/sonic-bgp-global:sonic-bgp-global"
        url_body_json = "{\"sonic-bgp-global:BGP_GLOBALS\":{\"BGP_GLOBALS_LIST\":[{\"vrf_name\":\"Vrf_test1\",\"local_asn\": 4294967295,\"always_compare_med\":true,\"confed_peers\":[4294967294,1,4294967295],\"keepalive\":123}]}}"
        t.Run("Field Exponent value create.", processSetRequest(url, url_body_json, "POST", false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Verify Field Exponent value create.", verifyDbResult(rclient, "BGP_GLOBALS|Vrf_test1", expected_map, false))
        unloadConfigDB(rclient, prereq_map)
	/***********************/

	/** Field Exponent value processing update**/
        prereq_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "keepalive": "123",
                                                                                                  "local_asn": "4294967295",
                                                                                                  "always_compare_med": "true",
                                                                                                  "confed_peers@": "4294967294,1,4294967295"}},
					     "VRF":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        expected_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "keepalive": "123",
                                                                                                  "local_asn": "4294967293",
                                                                                                  "always_compare_med": "false",
                                                                                                  "confed_peers@": "4294967294,1,4294967295,6,4294967293"}}}
        loadConfigDB(rclient, prereq_map)
	url = "/sonic-bgp-global:sonic-bgp-global/BGP_GLOBALS/BGP_GLOBALS_LIST"
        url_body_json = "{\"sonic-bgp-global:BGP_GLOBALS_LIST\":[{\"vrf_name\":\"Vrf_test1\",\"local_asn\":4294967293,\"always_compare_med\":false,\"confed_peers\":[6,4294967293]}]}"
        t.Run("Field Exponent value update.", processSetRequest(url, url_body_json, "PATCH", false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Verify Field Exponent value update.", verifyDbResult(rclient, "BGP_GLOBALS|Vrf_test1", expected_map, false))
        unloadConfigDB(rclient, prereq_map)
        /*********************/


	/** Field Exponent value processing replace**/
        prereq_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "keepalive": "123",
                                                                                                  "local_asn": "4294967293",
                                                                                                  "always_compare_med": "true",
                                                                                                  "confed_peers@": "4294967294,1,4294967295"}},
					     "VRF":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        expected_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "local_asn": "4294967291",
                                                                                                  "always_compare_med": "false",
                                                                                                  "confed_peers@": "6,4294967293"}}}
        loadConfigDB(rclient, prereq_map)
	url = "/sonic-bgp-global:sonic-bgp-global/BGP_GLOBALS/BGP_GLOBALS_LIST"
        url_body_json = "{\"sonic-bgp-global:BGP_GLOBALS_LIST\":[{\"vrf_name\":\"Vrf_test1\",\"local_asn\":4294967291,\"always_compare_med\":false,\"confed_peers\":[6,4294967293]}]}"
        t.Run("Field Exponent value replace.", processSetRequest(url, url_body_json, "PUT", false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Verify Field Exponent value replace.", verifyDbResult(rclient, "BGP_GLOBALS|Vrf_test1", expected_map, false))
        unloadConfigDB(rclient, prereq_map)
        /*********************/


        /** Field Exponent value processing get**/
        prereq_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "keepalive": "123",
                                                                                                  "local_asn": "4294967293",
                                                                                                  "always_compare_med": "false",
                                                                                                  "confed_peers@": "4294967294"}},
					     "VRF":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        loadConfigDB(rclient, prereq_map)
        expected_get_json := "{\"sonic-bgp-global:BGP_GLOBALS_LIST\":[{\"always_compare_med\":false,\"confed_peers\":[4294967294],\"keepalive\":123,\"local_asn\":4294967293,\"vrf_name\":\"Vrf_test1\"}]}"
        t.Run("Field Exponent value get.", processGetRequest(url, expected_get_json, false))
        time.Sleep(1 * time.Second)
        unloadConfigDB(rclient, prereq_map)
        /*********************/

        fmt.Println("\n\n+++++++++++++ Done Performing Field ExponentValue Sonic Yang Cases ++++++++++++")
}

func Test_KeyExpntVal_OCYang(t *testing.T) {
        fmt.Println("\n\n+++++++++++++ Performing Key Exponent value OC Yang Cases ++++++++++++")
        var url, url_body_json string

        /** Key Exponent value processing Create**/
        bgp_globals_map := map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "local_asn": "4294"}},
					     "VRF":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        bgp_globals_af_map := map[string]interface{}{"BGP_GLOBALS_AF":map[string]interface{}{"Vrf_test1|l2vpn_evpn":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        bgp_globals_evpnvni_map := map[string]interface{}{"BGP_GLOBALS_EVPN_VNI":map[string]interface{}{"Vrf_test1|L2VPN_EVPN|14628525":map[string]interface{}{
                                                                                                  "advertise-default-gw": "true",
											          "route-distinguisher": "trd1"}}}
        unloadConfigDB(rclient, bgp_globals_af_map)
        unloadConfigDB(rclient, bgp_globals_evpnvni_map)
        loadConfigDB(rclient, bgp_globals_map)
	url = "/openconfig-network-instance:network-instances/network-instance[name=Vrf_test1]/protocols/protocol[identifier=BGP][name=bgp]/bgp/global/afi-safis/afi-safi[afi-safi-name=L2VPN_EVPN]/l2vpn-evpn/openconfig-bgp-evpn-ext:vnis/vni[vni-number=14628525]"
        url_body_json = "{\"openconfig-bgp-evpn-ext:config\":{\"vni-number\":14628525},\"openconfig-bgp-evpn-ext:advertise-default-gw\":true,\"openconfig-bgp-evpn-ext:route-distinguisher\":\"trd1\"}"
        t.Run("Key Exponent value create.", processSetRequest(url, url_body_json, "POST", false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Verify Key Exponent value create - BGP_GLOBALS_AF.", verifyDbResult(rclient, "BGP_GLOBALS_AF|Vrf_test1|l2vpn_evpn", bgp_globals_af_map, false))
        t.Run("Verify Key Exponent value create - BGP_GLOBALS_EVPN_VNI.", verifyDbResult(rclient, "BGP_GLOBALS_EVPN_VNI|Vrf_test1|L2VPN_EVPN|14628525", bgp_globals_evpnvni_map, false))
        unloadConfigDB(rclient, bgp_globals_map)
        unloadConfigDB(rclient, bgp_globals_af_map)
        unloadConfigDB(rclient, bgp_globals_evpnvni_map)
        /*********************/

        /** Key Exponent value processing update**/
        bgp_globals_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "local_asn": "4294"}},
					     "VRF":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        bgp_globals_af_map = map[string]interface{}{"BGP_GLOBALS_AF":map[string]interface{}{"Vrf_test1|l2vpn_evpn":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        bgp_globals_evpnvni_map = map[string]interface{}{"BGP_GLOBALS_EVPN_VNI":map[string]interface{}{"Vrf_test1|L2VPN_EVPN|14628525":map[string]interface{}{
                                                                                                  "advertise-default-gw": "false"}}}
        exp_bgp_globals_evpnvni_map := map[string]interface{}{"BGP_GLOBALS_EVPN_VNI":map[string]interface{}{"Vrf_test1|L2VPN_EVPN|14628525":map[string]interface{}{
                                                                                                  "advertise-default-gw": "true"}}}
        loadConfigDB(rclient, bgp_globals_map)
        loadConfigDB(rclient, bgp_globals_af_map)
        loadConfigDB(rclient, bgp_globals_evpnvni_map)
	url = "/openconfig-network-instance:network-instances/network-instance[name=Vrf_test1]/protocols/protocol[identifier=BGP][name=bgp]/bgp/global/afi-safis/afi-safi[afi-safi-name=L2VPN_EVPN]/l2vpn-evpn/openconfig-bgp-evpn-ext:vnis/vni[vni-number=14628525]/advertise-default-gw"
        url_body_json = "{\"openconfig-bgp-evpn-ext:advertise-default-gw\":true}"
        t.Run("Key Exponent value update.", processSetRequest(url, url_body_json, "PATCH", false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Verify Key Exponent value update - BGP_GLOBALS_EVPN_VNI.", verifyDbResult(rclient, "BGP_GLOBALS_EVPN_VNI|Vrf_test1|L2VPN_EVPN|14628525", exp_bgp_globals_evpnvni_map, false))
        unloadConfigDB(rclient, bgp_globals_map)
        unloadConfigDB(rclient, bgp_globals_af_map)
        unloadConfigDB(rclient, bgp_globals_evpnvni_map)
        /*********************/

	/** Key Exponent value processing replace**/
        bgp_globals_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                 "local_asn": "4294"}},
					     "VRF":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        bgp_globals_af_map = map[string]interface{}{"BGP_GLOBALS_AF":map[string]interface{}{"Vrf_test1|l2vpn_evpn":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        bgp_globals_evpnvni_map = map[string]interface{}{"BGP_GLOBALS_EVPN_VNI":map[string]interface{}{"Vrf_test1|L2VPN_EVPN|14628525":map[string]interface{}{
                                                                                                  "advertise-default-gw": "false"}}}
        exp_bgp_globals_evpnvni_map = map[string]interface{}{"BGP_GLOBALS_EVPN_VNI":map[string]interface{}{"Vrf_test1|L2VPN_EVPN|14628525":map[string]interface{}{
                                                                                                  "advertise-default-gw": "true"}}}
        loadConfigDB(rclient, bgp_globals_map)
        loadConfigDB(rclient, bgp_globals_af_map)
        loadConfigDB(rclient, bgp_globals_evpnvni_map)
        url = "/openconfig-network-instance:network-instances/network-instance[name=Vrf_test1]/protocols/protocol[identifier=BGP][name=bgp]/bgp/global/afi-safis/afi-safi[afi-safi-name=L2VPN_EVPN]/l2vpn-evpn/openconfig-bgp-evpn-ext:vnis/vni[vni-number=14628525]/advertise-default-gw"
        url_body_json = "{\"openconfig-bgp-evpn-ext:advertise-default-gw\":true}"
        t.Run("Key Exponent value replace.", processSetRequest(url, url_body_json, "PUT", false, nil))
        time.Sleep(1 * time.Second)
        t.Run("Verify Key Exponent value replace - BGP_GLOBALS_EVPN_VNI.", verifyDbResult(rclient, "BGP_GLOBALS_EVPN_VNI|Vrf_test1|L2VPN_EVPN|14628525", exp_bgp_globals_evpnvni_map, false))
        unloadConfigDB(rclient, bgp_globals_map)
        unloadConfigDB(rclient, bgp_globals_af_map)
        unloadConfigDB(rclient, bgp_globals_evpnvni_map)
        /*********************/

	/** Key Exponent value  processing delete**/
        bgp_globals_map = map[string]interface{}{"BGP_GLOBALS":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "local_asn": "4294"}},
					     "VRF":map[string]interface{}{"Vrf_test1":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        bgp_globals_af_map = map[string]interface{}{"BGP_GLOBALS_AF":map[string]interface{}{"Vrf_test1|l2vpn_evpn":map[string]interface{}{
                                                                                                  "NULL": "NULL"}}}
        bgp_globals_evpnvni_map = map[string]interface{}{"BGP_GLOBALS_EVPN_VNI":map[string]interface{}{"Vrf_test1|L2VPN_EVPN|14628525":map[string]interface{}{
                                                                                                  "advertise-default-gw": "false"}}}

        expected_map := make(map[string]interface{})
        loadConfigDB(rclient, bgp_globals_map)
        loadConfigDB(rclient, bgp_globals_af_map)
        loadConfigDB(rclient, bgp_globals_evpnvni_map)
        url = "/openconfig-network-instance:network-instances/network-instance[name=Vrf_test1]/protocols/protocol[identifier=BGP][name=bgp]/bgp/global/afi-safis/afi-safi[afi-safi-name=L2VPN_EVPN]/l2vpn-evpn/openconfig-bgp-evpn-ext:vnis/vni[vni-number=14628525]"
        t.Run("Key Exponent value delete.", processDeleteRequest(url, false))
        time.Sleep(1 * time.Second)
        t.Run("Verify  Key Exponent value delete.", verifyDbResult(rclient, "BGP_GLOBALS_EVPN_VNI|Vrf_test1|L2VPN_EVPN|14628525", expected_map, false))
        unloadConfigDB(rclient, bgp_globals_map)
        unloadConfigDB(rclient, bgp_globals_af_map)
        unloadConfigDB(rclient, bgp_globals_evpnvni_map)
        /*********************/
        fmt.Println("\n\n+++++++++++++ Done Performing Key Exponent value OC Yang Cases ++++++++++++")
}
