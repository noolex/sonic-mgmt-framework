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

package main

import (
	"crypto/tls"
	"crypto/x509"
	"flag"
	"fmt"
	"io/ioutil"
	"net"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/Azure/sonic-mgmt-framework/rest/server"
	"github.com/Azure/sonic-mgmt-framework/build/rest_server/dist/openapi"

	"github.com/golang/glog"
	"github.com/pkg/profile"
)

// Command line parameters
var (
	port       int    // Server port
	certFile   string // Server certificate file path
	keyFile    string // Server private key file path
	caFile     string // Client CA certificate file path
	cliCAFile  string // CLI client CA certificate file path
	noSocket   bool   // Do not start unix domain socket lister
	clientAuth = server.NewUserAuth()
)

func init() {
	// Parse command line
	flag.IntVar(&port, "port", 443, "Listen port")
	flag.StringVar(&certFile, "cert", "", "Server certificate file path")
	flag.StringVar(&keyFile, "key", "", "Server private key file path")
	flag.StringVar(&caFile, "cacert", "", "CA certificate for client certificate validation")
	flag.StringVar(&cliCAFile, "clicacert", "", "CA certificate for CLI client validation")
	flag.Var(clientAuth, "client_auth", "Client auth mode(s) - <none,cert,jwt,password|user(deprecated)> default: password,jwt")
	flag.BoolVar(&noSocket, "no-sock", false, "Do not start unix domain socket listener")
	flag.Parse()

	//Below is for setting the default client_auth to password,jwt.
	//If you define the defaults in the above clientAuth, they will be merged together, which we don't want.
	clientAuthFound := false
	flag.Visit(func(f *flag.Flag) {
		if f.Name == "client_auth" {
			clientAuthFound = true
		}
	})
	if !clientAuthFound {
		clientAuth = server.UserAuth{"password": true, "cert": false, "jwt": true}
	}

}

var profRunning bool = true

// Start REST server
func main() {

	/* Enable profiling by default. Send SIGUSR1 signal to rest_server to
	 * stop profiling and save data to /tmp/profile<xxxxx>/cpu.pprof file.
	 * Copy over the cpu.pprof file and rest_server to a Linux host and run
	 * any of the following commands to generate a report in needed format.
	 * go tool pprof --txt ./rest_server ./cpu.pprof > report.txt
	 * go tool pprof --pdf ./rest_server ./cpu.pprof > report.pdf
	 * Note: install graphviz to generate the graph on a pdf format
	 */
	prof := profile.Start()
	defer prof.Stop()
	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGUSR1)
	go func() {
		for {
			<-sigs
			if profRunning {
				prof.Stop()
				profRunning = false
			} else {
				prof = profile.Start()
				//defer prof.Stop()
				profRunning = true
			}
		}
	}()

	if caFile == "" && clientAuth.Enabled("cert") {
		glog.Fatal("Must specify -cacert with -client_auth cert")
	}
	if clientAuth.Enabled("user") {
		glog.Warning("client_auth mode \"user\" is deprecated, use \"password\" instead.")
	}

	openapi.Load()

	server.GenerateJwtSecretKey()
	server.JwtRefreshInt = time.Duration(30 * time.Second)
	server.JwtValidInt = time.Duration(3600 * time.Second)

	rtrConfig := server.RouterConfig{Auth: clientAuth}
	router := server.NewRouter(&rtrConfig)

	address := fmt.Sprintf(":%d", port)

	// Prepare TLSConfig from the parameters
	tlsConfig := tls.Config{
		ClientAuth:               getTLSClientAuthType(),
		Certificates:             prepareServerCertificate(),
		ClientCAs:                prepareCACertificates(caFile),
		MinVersion:               tls.VersionTLS12,
		PreferServerCipherSuites: true,
		CipherSuites:             getPreferredCipherSuites(),
	}

	// Prepare HTTPS server
	restServer := &http.Server{
		Addr:      address,
		Handler:   router,
		TLSConfig: &tlsConfig,
	}

	if !noSocket {
		spawnUnixListener()
	}

	glog.Infof("**** Server started on %v", address)

	// Start HTTPS server
	glog.Fatal(restServer.ListenAndServeTLS("", ""))
}

// spawnUnixListener listens using certificate authentication on a local
// unix socket. This is used for authentication of the CLI client to the REST
// server, and will not be used for any other client.
func spawnUnixListener() {
	var CLIAuth = server.UserAuth{"clisock": true, "cert": true, "jwt": true}
	rtrConfig := server.RouterConfig{
		Auth: CLIAuth,
	}

	// Reuse the handler between the two listeners. This avoids creating an
	// extra identical handler for the TLS listener on TCP port 8443.
	handler := server.NewRouter(&rtrConfig)

	if cliCAFile != "" {
		// This block spawns an additional listener listening to localhost:8443
		// This is for use by the CLI, but only for those actioners using the
		// generated Swagger Python client, since they don't yet support
		// connections over the Unix domain sockets.
		cliListener, err := net.Listen("tcp", "127.0.0.1:8443")
		if err != nil {
			glog.Fatal(err)
		}

		// Prepare TLSConfig from the parameters
		tlsConfig := &tls.Config{
			ClientAuth:               tls.RequireAnyClientCert,
			Certificates:             prepareServerCertificate(),
			ClientCAs:                prepareCACertificates(cliCAFile),
			MinVersion:               tls.VersionTLS12,
			PreferServerCipherSuites: true,
			CipherSuites:             getPreferredCipherSuites(),
		}

		cliServer := &http.Server{
			Handler:   handler,
			TLSConfig: tlsConfig,
		}

		go func() {
			if err := cliServer.ServeTLS(cliListener, "", ""); err != nil && err != http.ErrServerClosed {
				glog.Fatal(err)
			}
		}()
	}

	const UDSock = "/var/run/rest-local.sock"
	os.Remove(UDSock)
	localListener, err := net.Listen("unix", UDSock)
	if err != nil {
		glog.Fatal(err)
	}

	// Allow all users to access the socket
	err = os.Chmod(UDSock, os.ModePerm)
	if err != nil {
		glog.Fatal(err)
	}

	localServer := &http.Server{
		Handler: handler,
		ConnContext: server.CLIConnectionContextFactory,
	}

	go func() {
		if err := localServer.Serve(localListener); err != nil && err != http.ErrServerClosed {
			glog.Fatal(err)
		}
	}()
}

// prepareServerCertificate function parses --cert and --key parameter
// values. Both cert and private key PEM files are loaded  into a
// tls.Certificate objects. Exits the process if files are not
// specified or not found or corrupted.
func prepareServerCertificate() []tls.Certificate {
	if certFile == "" {
		glog.Fatal("Server certificate file not specified")
	}

	if keyFile == "" {
		glog.Fatal("Server private key file not specified")
	}

	glog.Infof("Server certificate file: %s", certFile)
	glog.Infof("Server private key file: %s", keyFile)

	certificate, err := tls.LoadX509KeyPair(certFile, keyFile)
	if err != nil {
		glog.Fatal("Failed to load server cert/key -- ", err)
	}

	return []tls.Certificate{certificate}
}

// prepareCACertificates function parses --ca parameter, which is the
// path to CA certificate file. Loads file contents to a x509.CertPool
// object. Returns nil if file name is empty (not specified). Exists
// the process if file path is invalid or file is corrupted.
func prepareCACertificates(file string) *x509.CertPool {
	if file == "" { // no CA file..
		return nil
	}

	glog.Infof("Client CA certificate file: %s", file)

	caCert, err := ioutil.ReadFile(file)
	if err != nil {
		glog.Fatal("Failed to load CA certificate file -- ", err)
	}

	caPool := x509.NewCertPool()
	ok := caPool.AppendCertsFromPEM(caCert)
	if !ok {
		glog.Fatal("Invalid CA certificate")
	}

	return caPool
}

// getTLSClientAuthType function parses requires client cert
// if caFile is provided, otherwise we just request the client cert.
func getTLSClientAuthType() tls.ClientAuthType {
	if caFile != "" {
		return tls.RequireAndVerifyClientCert
	}
	return tls.RequestClientCert
}

func getPreferredCipherSuites() []uint16 {
	return []uint16{
		tls.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,
		tls.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
		tls.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305,
		tls.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305,
		tls.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,
		tls.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
	}
}
