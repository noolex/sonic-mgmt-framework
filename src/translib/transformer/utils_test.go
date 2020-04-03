////////////////////////////////////////////////////////////////////////////////
//                                                                            //
//  Copyright 2019 Broadcom. The term Broadcom refers to Broadcom Inc. and/or //
//  its subsidiaries.                                                         //
//                                                                            //
//  Licensed under the Apache License, Version 2.0 (the "License");           //
//  you may not use this file except in compliance with the License.          //
//  You may obtain a copy of the License at                                   //
//                                                                            //
//     http://www.apache.org/licenses/LICENSE-2.0                             //
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
	"github.com/go-redis/redis"
	"io/ioutil"
	"fmt"
	"testing"
	"reflect"
	"strings"
	db "translib/db"
	. "translib"
)

func processGetRequest(url string, expectedRespJson string, errorCase bool) func(*testing.T) {
	return func(t *testing.T) {
		response, err := Get(GetRequest{Path: url, User: UserRoles{Name: "admin", Roles: []string{"admin"}}})
		if err != nil && !errorCase {
			t.Errorf("Error %v received for Url: %s", err, url)
		}

		respJson := response.Payload
		if string(respJson) != expectedRespJson {
			t.Errorf("Response for Url: %s received is not expected:\n Received: %s\n Expected: %s", url, string(respJson), expectedRespJson)
		}
	}
}

func processSetRequest(url string, jsonPayload string, oper string, errorCase bool) func(*testing.T) {
	return func(t *testing.T) {
		var err error
		switch oper {
		case "POST":
			_, err = Create(SetRequest{Path: url, Payload: []byte(jsonPayload)})
		case "PATCH":
			_, err = Update(SetRequest{Path: url, Payload: []byte(jsonPayload)})
		case "PUT":
			_, err = Replace(SetRequest{Path: url, Payload: []byte(jsonPayload)})
		default:
			t.Errorf("Operation not supported")
		}
		if err != nil && !errorCase {
			t.Errorf("Error %v received for Url: %s", err, url)
		}
	}
}

func processSetRequestFromFile(url string, jsonFile string, oper string, errorCase bool) func(*testing.T) {
	return func(t *testing.T) {
		jsonPayload, err := ioutil.ReadFile(jsonFile)
		if err != nil {
			t.Errorf("read file %v err: %v", jsonFile, err)
		}
		switch oper {
		case "POST":
			_, err = Create(SetRequest{Path: url, Payload: []byte(jsonPayload)})
		case "PATCH":
			_, err = Update(SetRequest{Path: url, Payload: []byte(jsonPayload)})
		case "PUT":
			_, err = Replace(SetRequest{Path: url, Payload: []byte(jsonPayload)})
		default:
			t.Errorf("Operation not supported")
		}
		if err != nil && !errorCase {
			t.Errorf("Error %v received for Url: %s", err, url)
		}
	}
}

func processDeleteRequest(url string) func(*testing.T) {
	return func(t *testing.T) {
		_, err := Delete(SetRequest{Path: url})
		if err != nil {
			t.Errorf("Error %v received for Url: %s", err, url)
		}
	}
}

func getConfigDb() *db.DB {
	configDb, _ := db.NewDB(db.Options{
		DBNo:               db.ConfigDB,
		InitIndicator:      "CONFIG_DB_INITIALIZED",
		TableNameSeparator: "|",
		KeySeparator:       "|",
	})

	return configDb
}

func verifyDbResult(client *redis.Client, key string, expectedResult map[string]interface{}, errorCase bool) func(*testing.T) {
	return func(t *testing.T) {
		result, err := client.HGetAll(key).Result()
		if err != nil {
			t.Errorf("Error %v hgetall for key: %s", err, key)
		}

		expect := make(map[string]string)
		for ts := range expectedResult {
			for _,k := range expectedResult[ts].(map[string]interface{}) {
				for f,v := range k.(map[string]interface{}) {
					strKey := fmt.Sprintf("%v", f)
					var strVal string
					if strings.Contains(strKey, "@") == true {
						elems := make([]string, len(v.([]interface{})))
						for i, e := range v.([]interface{}) {
							elems[i] = e.(string)
						}
						if len(elems) > 1 {
							strVal = strings.Join(elems, ",")
						} else {
							strVal = fmt.Sprintf("%v", v)
						}
					} else {
						strVal = fmt.Sprintf("%v", v)
					}
					expect[strKey] = strVal
				}
			}
		}

		if reflect.DeepEqual(result, expect) != true {
			t.Errorf("Response for Key: %v received is not expected: Received %v Expected %v\n", key, result, expect)
		}
	}
}

var emptyJson string = "{}"
