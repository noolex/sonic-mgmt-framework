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

package server

import (
	"net/http"
	"strconv"
	"strings"

	"github.com/golang/glog"
)

// parseQueryParams parses the http request's query parameters
// into a translibArgs args.
func parseQueryParams(args *translibArgs, r *http.Request) error {
	if strings.HasPrefix(r.URL.Path, restconfPathPrefix) {
		return parseRestconfQueryParams(args, r)
	}

	return nil
}

// parseRestconfQueryParams parses query parameters of a request 'r' to
// fill translibArgs object 'args'. Returns httpError with status 400
// if any parameter is unsupported or has invalid value.
func parseRestconfQueryParams(args *translibArgs, r *http.Request) error {
	var err error
	qParams := r.URL.Query()

	for name, vals := range qParams {
		switch name {
		case "depth":
			args.depth, err = parseDepthParam(vals, r)
		case "deleteEmptyEntry":
			args.deleteEmpty, err = parseDeleteEmptyEntryParam(vals, r)
		default:
			err = newUnsupportedParamError(name, r)
		}
		if err != nil {
			return err
		}
	}

	return nil
}

func newUnsupportedParamError(name string, r *http.Request) error {
	return httpError(http.StatusBadRequest, "query parameter '%s' not supported", name)
}

func newInvalidParamError(name string, r *http.Request) error {
	return httpError(http.StatusBadRequest, "invalid '%s' query parameter", name)
}

// parseDepthParam parses query parameter value for "depth" parameter.
// See https://tools.ietf.org/html/rfc8040#section-4.8.2
func parseDepthParam(v []string, r *http.Request) (uint, error) {
	if !restconfCapabilities.depth {
		glog.V(1).Infof("'depth' support disabled")
		return 0, newUnsupportedParamError("depth", r)
	}

	if r.Method != "GET" && r.Method != "HEAD" {
		glog.V(1).Infof("'depth' not supported for %s", r.Method)
		return 0, newUnsupportedParamError("depth", r)
	}

	if len(v) != 1 {
		glog.V(1).Infof("Expecting only 1 depth param; found %d", len(v))
		return 0, newInvalidParamError("depth", r)
	}

	if v[0] == "unbounded" {
		return 0, nil
	}

	d, err := strconv.ParseUint(v[0], 10, 16)
	if err != nil || d == 0 {
		glog.V(1).Infof("Bad depth value '%s', err=%v", v[0], err)
		return 0, newInvalidParamError("depth", r)
	}

	return uint(d), nil
}

// parseDeleteEmptyEntryParam parses the custom "deleteEmptyEntry" query parameter.
// Allowed only on internal router (like CLI).
func parseDeleteEmptyEntryParam(v []string, r *http.Request) (bool, error) {
	if !getRouterConfig(r).Internal {
		glog.V(1).Infof("deleteEmptyEntry supported only on internal router")
		return false, newUnsupportedParamError("deleteEmptyEntry", r)
	}

	if r.Method != "DELETE" {
		glog.V(1).Infof("deleteEmptyEntry not supported for %s", r.Method)
		return false, newUnsupportedParamError("deleteEmptyEntry", r)
	}

	if len(v) != 1 {
		glog.V(1).Infof("expecting only 1 deleteEmptyEntry; found %d", len(v))
		return false, newInvalidParamError("deleteEmptyEntry", r)
	}

	return strings.EqualFold(v[0], "true"), nil
}
