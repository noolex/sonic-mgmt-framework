////////////////////////////////////////////////////////////////////////////////
//                                                                            //
//  Copyright 2019 Dell, Inc.                                                 //
//                                                                            //
//  Licensed under the Apache License, Version 2.0 (the "License");           //
//  you may not use this file except in compliance with the License.          //
//  You may obtain a copy of the License at                                   //
//                                                                            //
//  http://www.apache.org/licenses/LICENSE-2.0                                //
//                                                                            //
//  Unless required by applicable law or agreed to in writing, software       //
//  distributed under the License is distributed on an "AS IS" BASIS,         //
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  //
//  See the License for the specific language governing permissions and       //
//  limitations under the License.                                            //
//                                                                            //
////////////////////////////////////////////////////////////////////////////////

package transformer_test

import (
	"fmt"
	"time"
	"testing"
)

func Test_SetTABLE(t *testing.T) {

	fmt.Println("+++++  Start sonic-tests/TABLE_A testing  +++++")

	url := "/sonic-tests:sonic-tests/TABLE_A/TABLE_A_LIST[id=14628525]"

        //Add entry
	t.Run("Add entry", processSetRequest(url, addEntryJson, "PATCH", false))
	time.Sleep(1 * time.Second)

        // Verify entry
	t.Run("Verify entry", processGetRequest(url, addEntryJson, false))

}

/***************************************************************************/
///////////                  JSON Data for Tests              ///////////////
/***************************************************************************/

var addEntryJson string = "{\"sonic-tests:TABLE_A_LIST\":[{\"id\":14628525,\"ifname\":\"Ethernet0\",\"index\":14628526,\"indices\":[10,20,14628510,14628220],\"speed\":\"4444\"}]}"
var setSpeedJson string = "{\"sonic-tests:TABLE_A_LIST\": \"2.2.2.2\"}"
