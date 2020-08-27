package server

import (
	"net/http"
	"strings"
	"github.com/golang/glog"
)

func ClientCertAuthenAndAuthor(r *http.Request, rc *RequestContext) error {

	var username string
	if r.TLS != nil && len(r.TLS.PeerCertificates) > 0 {
		username = strings.ToLower(r.TLS.PeerCertificates[0].Subject.CommonName)
	}

	if len(username) == 0 {
		glog.Errorf("[%s] User info not present", rc.ID)
		return ErrNotFound
	}

	if err := PopulateAuthStruct(username, &rc.Auth); err != nil {
		glog.Infof("[%s] Failed to retrieve authentication information; %v", rc.ID, err)
		return httpError(http.StatusUnauthorized, "")
	}
	glog.Infof("[%s] Received user=%s", rc.ID, username)

	glog.Infof("[%s] Authentication passed. user=%s ", rc.ID, username)

	glog.Infof("[%s] Authorization passed for user=%s, roles=%s", rc.ID, rc.Auth.User, rc.Auth.Roles)
	return nil
}
