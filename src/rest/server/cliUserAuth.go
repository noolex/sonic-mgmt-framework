package server

import (
	"fmt"
	"net"
	"net/http"
	"os/user"

	"golang.org/x/sys/unix"

	"github.com/golang/glog"
)

func CliUserAuthenAndAuthor(r *http.Request, rc *RequestContext) error {

	netConn := r.Context().Value("http-conn")

	unixConn, ok := netConn.(*net.UnixConn)
	if !ok {
		glog.Errorf("[%s] Unable to obtain network connection", rc.ID)
		return fmt.Errorf("Unable to obtain network connection")
	}

	var cred *unix.Ucred

	raw, err := unixConn.SyscallConn()
	if err != nil {
		glog.Errorf("[%s] Unable to get raw socket info (%v)", rc.ID, err)
		return err
	}

	err2 := raw.Control(func(fd uintptr) {
		cred, err = unix.GetsockoptUcred(int(fd),
			unix.SOL_SOCKET, unix.SO_PEERCRED)
	})

	if err != nil {
		glog.Errorf("[%s] Unable to get peer credentials (%v)", rc.ID, err)
		return err
	}
	if err2 != nil {
		glog.Errorf("[%s] Unable to send control to raw socket (%v)", rc.ID, err2)
		return err2
	}

	// PopulateAuthStruct will repeat the lookup by username, and we don't
	// need to do that again
	var usr *user.User
	// user.LookupId expects the UID as a string
	usr, err = user.LookupId(fmt.Sprint(cred.Uid))
	if err != nil {
		glog.Errorf("[%s] Unable to get user information (%v)", rc.ID, err)
		return err
	}

	rc.Auth.User = usr.Username
	rc.Auth.Roles, err = GetUserRoles(usr)
	if err != nil {
		glog.Errorf("[%s] Unable to get user roles (%v)", rc.ID, err)
		return err
	}

	glog.Infof("[%s] Authorization passed for user=%s, roles=%s", rc.ID, rc.Auth.User, rc.Auth.Roles)
	return nil
}
