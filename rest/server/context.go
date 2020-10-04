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

package server

import (
	"context"
	"fmt"
	"mime"
	"net/http"
	"regexp"
	"sync/atomic"
)

// AuthInfo holds data about the authenticated user
type AuthInfo struct {
	// Username
	User string

	// Roles
	Roles []string
}

// RequestContext holds metadata about REST request.
type RequestContext struct {

	// Unique reqiest id
	ID string

	// Name represents the operationId from OpenAPI spec
	Name string

	// "consumes" and "produces" data from OpenAPI spec
	Consumes MediaTypes
	Produces MediaTypes

	// Model holds pointer to the OpenAPI data model object for
	// the body. When set, the request handler can validate the
	// request payload by loading the body into this model object.
	Model interface{}

	// PMap is the mapping of URI parameter names to actual yang
	// leaf names. Yang xpaths can have duplicate parameter names,
	// which is not supported by swagger and mux libraries. We
	// work around it by assigning different parameter names in
	// swagger and map them back to yang names while converting
	// REST paths to TransLib paths.
	PMap NameMap

	// stats is the apiStats object from the context
	stats *apiStats

	// Auth contains the authorized user information
	Auth AuthInfo

	ClientAuth UserAuth
}

type contextkey int

const (
	requestContextKey contextkey = iota + 1
	statsContextKey
	routerConfigContextKey
	routeMatchContextKey
	cliConnectionContextKey
)

// Request Id generator
var requestCounter uint64

// GetContext function returns the RequestContext object for a
// HTTP request. RequestContext is maintained as a context value of
// the request. Creates a new RequestContext object is not already
// available; in which case this function also creates a copy of
// the HTTP request object with new context.
func GetContext(r *http.Request) (*RequestContext, *http.Request) {
	cv := getContextValue(r, requestContextKey)
	if cv != nil {
		return cv.(*RequestContext), r
	}

	rc := new(RequestContext)
	rc.ID = fmt.Sprintf("REST-%v", atomic.AddUint64(&requestCounter, 1))
	rc.stats = getApiStats(r)

	r = setContextValue(r, requestContextKey, rc)
	return rc, r
}

// setContextValue sets a new value into http request's context.
// Returns the new http.Request object containing the new context.
func setContextValue(r *http.Request, k contextkey, v interface{}) *http.Request {
	return r.WithContext(context.WithValue(r.Context(), k, v))
}

// getContextValue looks up a value in a http request's context.
// Returns nil if the value was not found.
func getContextValue(r *http.Request, k contextkey) interface{} {
	return r.Context().Value(k)
}

///////////

// MediaType represents the parsed media type value. Includes
// a MIME type string and optional parameters.
type MediaType struct {
	Type   string
	Params map[string]string

	TypePrefix string
	TypeSuffix string
	TypeMiddle string
}

// mediaTypeExpr is the regex to extract parts from media type string.
var mediaTypeExpr = regexp.MustCompile(`([^/]+)(?:/(?:([^+]+)\+)?(.+))?`)

// Parse function parses a full media type value with parameters
// into this MediaType object.
func parseMediaType(value string) (*MediaType, error) {
	if value == "" {
		return nil, nil
	}

	mtype, params, err := mime.ParseMediaType(value)
	if err != nil {
		return nil, err
	}

	// Extract parts from the mime type
	parts := mediaTypeExpr.FindStringSubmatch(mtype)
	if parts[3] == "*" && parts[2] == "" { // for patterns like "text/*"
		parts[2] = "*"
	}

	return &MediaType{Type: mtype, Params: params,
		TypePrefix: parts[1], TypeMiddle: parts[2], TypeSuffix: parts[3]}, nil
}

// Format function returns the full media type string - including
// MIME type and parameters.
func (m *MediaType) Format() string {
	return mime.FormatMediaType(m.Type, m.Params)
}

// Matches verifies if this Mediatype matches the another MediaType.
func (m *MediaType) Matches(other *MediaType) bool {
	return m.Type == other.Type ||
		(matchPart(m.TypePrefix, other.TypePrefix) &&
			matchPart(m.TypeMiddle, other.TypeMiddle) &&
			matchPart(m.TypeSuffix, other.TypeSuffix))
}

// isJSON function checks if this media type represents a json
// content. Uses the suffix part of media type string.
func (m *MediaType) isJSON() bool {
	return m.TypeSuffix == "json"
}

func matchPart(x, y string) bool {
	return x == y || x == "*" || y == "*"
}

//////////

// MediaTypes is a collection of parsed media type values
type MediaTypes []MediaType

// Add function parses and adds a media type to the MediaTypes
// object. Any parameters in the media type value are ignored.
func (m *MediaTypes) Add(mimeType string) error {
	mtype, err := parseMediaType(mimeType)
	if err == nil {
		*m = append(*m, *mtype)
	}

	return err
}

// Contains function checks if a given media type value is
// present in the ContentTypes. Ignores the media type parameters.
func (m *MediaTypes) Contains(mimeType string) bool {
	t, _, _ := mime.ParseMediaType(mimeType)
	for _, entry := range *m {
		if entry.Type == t {
			return true
		}
	}

	return false
}

// GetMatching returns registered full content type value
// matching a given hint.
func (m *MediaTypes) GetMatching(mimeType string) MediaTypes {
	mtype, err := parseMediaType(mimeType)
	if err != nil {
		return nil // TODO return error
	}

	var matchList MediaTypes
	for _, entry := range *m {
		if entry.Matches(mtype) {
			matchList = append(matchList, entry)
		}
	}

	return matchList
}

func (m MediaTypes) String() string {
	types := make([]string, 0, len(m))
	for _, entry := range m {
		types = append(types, entry.Type)
	}
	return fmt.Sprintf("%v", types)
}

//////////

// NameMap is a simple mapping of names (string to string)
type NameMap map[string]string

// Get function returns the mapped name for a given name.
// Returns given name itself if no mapping exists.
func (m *NameMap) Get(name string) string {
	if mappedName, ok := (*m)[name]; ok {
		return mappedName
	}
	return name
}
