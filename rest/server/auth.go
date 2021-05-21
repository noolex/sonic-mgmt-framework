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
	"bytes"
	"fmt"
	"net/http"
	"os/user"
	"strings"
	"sync"

	"github.com/Azure/sonic-mgmt-common/translib"
	"github.com/golang/glog"
	"golang.org/x/crypto/ssh"
)

type UserAuth map[string]bool

var AuthLock sync.Mutex

var ErrUnauthorized = httpError(http.StatusUnauthorized, "Authentication not provided")

func (i UserAuth) String() string {
	if i["none"] {
		return ""
	}
	b := new(bytes.Buffer)
	for key, value := range i {
		if value {
			fmt.Fprintf(b, "%s ", key)
		}
	}
	return b.String()
}

func (i UserAuth) Any() bool {
	if i["none"] {
		return false
	}
	for _, value := range i {
		if value {
			return true
		}
	}
	return false
}

func (i UserAuth) Enabled(mode string) bool {
	if i["none"] {
		return false
	}
	if value, exist := i[mode]; exist && value {
		return true
	}
	return false
}

func (i UserAuth) Set(mode string) error {
	modes := strings.Split(mode, ",")
	for _, m := range modes {
		m = strings.Trim(m, " ")
		if m == "none" || m == "" {
			i["none"] = true
			return nil
		}

		if _, exist := i[m]; !exist {
			return fmt.Errorf("Expecting one or more of 'cert', 'password' or 'jwt'")
		}
		i[m] = true
	}
	return nil
}

func (i UserAuth) Unset(mode string) error {
	modes := strings.Split(mode, ",")
	for _, m := range modes {
		m = strings.Trim(m, " ")
		if _, exist := i[m]; !exist {
			return fmt.Errorf("Expecting one or more of 'cert', 'password' or 'jwt'")
		}
		i[m] = false
	}
	return nil
}

// NewUserAuth creates an UserAuth object with specified modes enabled.
func NewUserAuth(enabledModes ...string) UserAuth {
	auth := UserAuth{"password": false, "user": false, "cert": false, "jwt": false}
	for _, mode := range enabledModes {
		auth.Set(mode)
	}

	return auth
}

func GetUserRoles(usr *user.User) ([]string, error) {
	// Get user roles from DB
	tlUser, errDb := translib.GetUser(usr.Username)
	if errDb == nil {
		// We have a match, use the DB contents
		glog.Infof("DB info user=%v roles=%#v", tlUser.Name, tlUser.Roles)
		return tlUser.Roles, nil
	}
	// No match, fallback to using group membership

	// Lookup Roles
	gids, err := usr.GroupIds()
	if err != nil {
		return nil, err
	}
	roles := make([]string, len(gids))
	for idx, gid := range gids {
		group, err := user.LookupGroupId(gid)
		if err != nil {
			return nil, err
		}
		roles[idx] = group.Name
	}
	return roles, nil
}
func PopulateAuthStruct(username string, auth *AuthInfo) error {
	AuthLock.Lock()
	defer AuthLock.Unlock()
	usr, err := user.Lookup(username)
	if err != nil {
		return err
	}

	auth.User = username
	roles, err := GetUserRoles(usr)
	if err != nil {
		return err
	}
	auth.Roles = roles

	return nil
}

func UserPwAuth(username string, passwd string) (bool, error) {
	/*
	 * mgmt-framework container does not have access to /etc/passwd, /etc/group,
	 * /etc/shadow and /etc/tacplus_conf files of host. One option is to share
	 * /etc of host with /etc of container. For now disable this and use ssh
	 * for authentication.
	 */

	//Use ssh for authentication.
	config := &ssh.ClientConfig{
		User: username,
		Auth: []ssh.AuthMethod{
			ssh.Password(passwd),
		},
		HostKeyCallback: ssh.InsecureIgnoreHostKey(),
	}
	c, err := ssh.Dial("tcp", "127.0.0.1:22", config)
	if err != nil {
		glog.Infof("Authentication failed. user=%s, error:%s", username, err.Error())
		return false, err
	}
	defer c.Conn.Close()

	return true, nil
}
