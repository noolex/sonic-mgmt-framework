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
	//"errors"
	"testing"
	"time"
	"translib/tlerr"
)

func Test_verifyError(t *testing.T) {

	var col1Json string = "{\"sonic-sflow:SFLOW_COLLECTOR_LIST\":[{\"collector_ip\":\"1.1.1.1\",\"collector_name\":\"col1\",\"collector_port\":4444}]}"

        //Delete collector
	url := "/sonic-sflow:sonic-sflow/SFLOW_COLLECTOR"
	list_url := "/sonic-sflow:sonic-sflow/SFLOW_COLLECTOR/SFLOW_COLLECTOR_LIST[collector_name=col1]"
	t.Run("Delete sFlow collector col1", processDeleteRequest(list_url, false))

        //Add collector
	t.Run("Add sFlow collector col1", processSetRequest(url, col1Json, "POST", false))
	time.Sleep(1 * time.Second)

        // Verify collector configurations
	t.Run("Verify sFlow collector col1", processGetRequest(list_url, col1Json, false))
	time.Sleep(1 * time.Second)

        // Verify error
	err := tlerr.AlreadyExists("Entry col1 already exists")
	t.Run("check error", processSetRequest(url, col1Json, "POST", true, err))
	time.Sleep(1 * time.Second)
}

