////////////////////////////////////////////////////////////////////////////////
//                                                                            //
//  Copyright 2020 Broadcom. The term Broadcom refers to Broadcom Inc. and/or //
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

package translib

import (
	"testing"
)

func ver(major, minor, patch uint32) Version {
	return Version{Major:major, Minor:minor, Patch:patch}
}

func TestVersionParseStr(t *testing.T) {
	t.Run("empty", testVerSet("", ver(0, 0, 0), true))
	t.Run("0.0.0", testVerSet("0.0.0", ver(0, 0, 0), true))
	t.Run("1.0.0", testVerSet("1.0.0", ver(1, 0, 0), true))
	t.Run("1.2.3", testVerSet("1.2.3", ver(1, 2, 3), true))
	t.Run("1.-.-", testVerSet("1", Version{}, false))
	t.Run("1.2.-", testVerSet("1.2", Version{}, false))
	t.Run("1.-.3", testVerSet("1..2", Version{}, false))
	t.Run("neg_majr", testVerSet("-1.0.0", Version{}, false))
	t.Run("bad_majr", testVerSet("A.2.3", Version{}, false))
	t.Run("neg_minr", testVerSet("1.-2.0", Version{}, false))
	t.Run("bad_minr", testVerSet("1.B.3", Version{}, false))
	t.Run("neg_pat", testVerSet("1.2.-3", Version{}, false))
	t.Run("bad_pat", testVerSet("1.2.C", Version{}, false))
	t.Run("invalid", testVerSet("invalid", Version{}, false))
}

func testVerSet(vStr string, exp Version, expSuccess bool) func(*testing.T) {
	return func(t *testing.T) {
		v, err := NewVersion(vStr)
		if err != nil {
			if expSuccess == true {
				t.Fatalf("Failed to parse \"%s\"; err=%v. Expected %v", vStr, err, exp)
			}
			return
		}

		if !expSuccess {
			t.Fatalf("Version string \"%s\" was expected to fail; but got %v", vStr, v)
		}

		if v != exp {
			t.Fatalf("Failed to parse \"%s\"; expected %v", vStr, v)
		}
	}
}
