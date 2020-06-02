package server

import (
	"crypto/rand"
	"encoding/json"
	jwt "github.com/dgrijalva/jwt-go"
	"github.com/golang/glog"
	"net/http"
	"os/user"
	"strings"
	"time"
)

var (
	JwtRefreshInt    time.Duration
	JwtValidInt      time.Duration
	hmacSampleSecret = make([]byte, 16)
)

type Credentials struct {
	Password string `json:"password"`
	Username string `json:"username"`
}

type Claims struct {
	Username string   `json:"username"`
	Roles    []string `json:"roles"`
	jwt.StandardClaims
}

type jwtToken struct {
	Token     string `json:"access_token"`
	TokenType string `json:"token_type"`
	ExpIn     int64  `json:"expires_in"`
}

func generateJWT(username string, roles []string, expire_dt time.Time) string {
	// Create a new token object, specifying signing method and the claims
	// you would like it to contain.
	claims := &Claims{
		Username: username,
		Roles:    roles,
		StandardClaims: jwt.StandardClaims{
			// In JWT, the expiry time is expressed as unix milliseconds
			ExpiresAt: expire_dt.Unix(),
		},
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)

	// Sign and get the complete encoded token as a string using the secret
	tokenString, _ := token.SignedString(hmacSampleSecret)

	return tokenString
}
func GenerateJwtSecretKey() {
	rand.Read(hmacSampleSecret)
}

func tokenResp(w http.ResponseWriter, r *http.Request, username string, roles []string) {
	exp_tm := time.Now().Add(JwtValidInt)
	token := jwtToken{Token: generateJWT(username, roles, exp_tm), TokenType: "Bearer", ExpIn: int64(JwtValidInt / time.Second)}
	resp, err := json.Marshal(token)
	if err != nil {
		glog.Errorf("Failed to marshal token: %v; err=%v", token, err)
		writeErrorResponse(w, r, err)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write(resp)
}

func Authenticate(w http.ResponseWriter, r *http.Request) {
	var creds Credentials
	rc, r := GetContext(r)
	auth_success := false
	if rc.ClientAuth.Enabled("clisock") {
		// Check if they are connected using the Unix socket
		if err := CliUserAuthenAndAuthor(r, rc); err == nil {
			auth_success = true
			tokenResp(w, r, rc.Auth.User, rc.Auth.Roles)
			return
		}
	}

	if !auth_success && rc.ClientAuth.Enabled("cert") && r.TLS != nil && len(r.TLS.PeerCertificates) > 0 {
		//Check if they are using certificate based auth
		username := strings.ToLower(r.TLS.PeerCertificates[0].Subject.CommonName)
		if len(username) > 0 {
			auth_success = true
			creds.Username = username
		}
	}

	if !auth_success {
		//Check if they are using user/password based auth
		err := json.NewDecoder(r.Body).Decode(&creds)
		if err != nil {
			w.WriteHeader(http.StatusBadRequest)
			return
		}

		auth_success, _ = UserPwAuth(creds.Username, creds.Password)
	}

	if auth_success {
		usr, err := user.Lookup(creds.Username)
		if err == nil {
			roles, err := GetUserRoles(usr)
			if err == nil {
				tokenResp(w, r, creds.Username, roles)
				return
			}
		}
	}

	// Authentication for JWT token failed!
	writeErrorResponse(w, r, httpError(http.StatusUnauthorized, ""))
}

func Refresh(w http.ResponseWriter, r *http.Request) {

	ctx, _ := GetContext(r)
	token, err := JwtAuthenAndAuthor(r, ctx)
	if err != nil {
		writeErrorResponse(w, r, err)
		return
	}

	claims := &Claims{}
	jwt.ParseWithClaims(token.Token, claims, func(token *jwt.Token) (interface{}, error) {
		return hmacSampleSecret, nil
	})

	if time.Until(time.Unix(claims.ExpiresAt, 0)) > JwtRefreshInt {
		writeErrorResponse(w, r, httpError(http.StatusBadRequest, "Refresh request too soon"))
		return
	}

	tokenResp(w, r, claims.Username, claims.Roles)

}

func JwtAuthenAndAuthor(r *http.Request, rc *RequestContext) (jwtToken, error) {
	var token jwtToken
	auth_hdr := r.Header.Get("Authorization")
	if len(auth_hdr) == 0 {
		glog.Errorf("[%s] JWT Token not present", rc.ID)
		return token, httpError(http.StatusUnauthorized, "JWT Token not present")
	}
	auth_parts := strings.Split(auth_hdr, " ")
	if len(auth_parts) != 2 || auth_parts[0] != "Bearer" {
		glog.Errorf("[%s] Failed to authenticate, Invalid JWT Token", rc.ID)
		return token, httpError(http.StatusUnauthorized, "Invalid JWT Token")
	}

	token.Token = auth_parts[1]

	claims := &Claims{}
	tkn, err := jwt.ParseWithClaims(token.Token, claims, func(token *jwt.Token) (interface{}, error) {
		return hmacSampleSecret, nil
	})
	if err != nil {
		if err == jwt.ErrSignatureInvalid {
			glog.Errorf("[%s] Failed to authenticate, Invalid JWT Signature", rc.ID)
			return token, httpError(http.StatusUnauthorized, "Invalid JWT Signature")

		}
		glog.Errorf("[%s] Failed to authenticate, Invalid JWT Token", rc.ID)
		return token, httpError(http.StatusUnauthorized, "Invalid JWT Token")
	}
	if !tkn.Valid {
		glog.Errorf("[%s] Failed to authenticate, Invalid JWT Token", rc.ID)
		return token, httpError(http.StatusUnauthorized, "Invalid JWT Token")
	}
	// if err := PopulateAuthStruct(claims.Username, &rc.Auth); err != nil {
	// 	glog.Infof("[%s] Failed to retrieve authentication information; %v", rc.ID, err)
	// 	return token, httpError(http.StatusUnauthorized, "")
	// }
	rc.Auth.User = claims.Username
	rc.Auth.Roles = claims.Roles
	return token, nil
}
