################################################################################
#                                                                              #
#  Copyright 2019 Broadcom. The term Broadcom refers to Broadcom Inc. and/or   #
#  its subsidiaries.                                                           #
#                                                                              #
#  Licensed under the Apache License, Version 2.0 (the "License");             #
#  you may not use this file except in compliance with the License.            #
#  You may obtain a copy of the License at                                     #
#                                                                              #
#     http://www.apache.org/licenses/LICENSE-2.0                               #
#                                                                              #
#  Unless required by applicable law or agreed to in writing, software         #
#  distributed under the License is distributed on an "AS IS" BASIS,           #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    #
#  See the License for the specific language governing permissions and         #
#  limitations under the License.                                              #
#                                                                              #
################################################################################

.PHONY: all clean cleanall codegen rest-server rest-clean yamlGen cli clitree ham clidocgen clidocgen-clean

TOPDIR := $(abspath .)
BUILD_DIR := $(TOPDIR)/build
export TOPDIR

ifeq ($(BUILD_GOPATH),)
export BUILD_GOPATH=$(TOPDIR)/build/gopkgs
endif

export GOPATH=$(BUILD_GOPATH):$(TOPDIR)

ifeq ($(GO),)
GO := /usr/local/go/bin/go 
export GO
endif

INSTALL := /usr/bin/install

MAIN_TARGET = sonic-mgmt-framework_1.0-01_amd64.deb

# list of go dependencies in "<PACKAGE_NAME>@<REMOTE_URL>@<COMMIT_ID>" format.
GO_DEPS_LIST = golang.org/x/crypto@https\://go.googlesource.com/crypto@be400aefbc4c83e9aab51e82b8d4b12760653b47 \
               golang.org/x/sys@https\://go.googlesource.com/sys@ed752295db8857b3a7f36c3f57e38509cadff471 \
               golang.org/x/text@https\://go.googlesource.com/text@c27b9fd57aec08b1104313fb190f0ecc6d23095f \
               golang.org/x/net@https\://go.googlesource.com/net@c7110b5ffcbb9f2ac4de9fbd2600e37d42473a9a \
               gopkg.in/go-playground/validator.v9@https\://gopkg.in/go-playground/validator.v9@21c910fc6d9c3556c28252b04beb17de0c2d40ec \
               gopkg.in/godbus/dbus.v5@https\://gopkg.in/godbus/dbus.v5@37bf87eef99d69c4f1d3528bd66e3a87dc201472 \
               google.golang.org/grpc@https\://github.com/grpc/grpc-go@0d6a24f68a5f9a38c64be00364587becb0e40518 \
               google.golang.org/genproto@https\://github.com/google/go-genproto@06b3db80844671cc7ff39f70718ddc6f943bac08 \
               google.golang.org/protobuf@https\://go.googlesource.com/protobuf@81d297c66c9b1e0606eee19a9ee718dcf149276d \
               github.com/golang/protobuf@https\://github.com/golang/protobuf@4846b58453b3708320bdb524f25cc5a1d9cda4d4 \
               github.com/golang/groupcache@https\://github.com/golang/groupcache@8c9f03a8e57eb486e42badaed3fb287da51807ba \
               github.com/golang/glog@https\://github.com/golang/glog@23def4e6c14b4da8ac2ed8007337bc5eb5007998 \
               github.com/go-redis/redis@https\://github.com/go-redis/redis@d19aba07b47683ef19378c4a4d43959672b7cec8 \
               github.com/openconfig/gnmi@https\://github.com/openconfig/gnmi@e7106f7f5493a9fa152d28ab314f2cc734244ed8 \
               github.com/openconfig/ygot@https\://github.com/openconfig/ygot@724a6b18a9224343ef04fe49199dfb6020ce132a \
               github.com/openconfig/goyang@https\://github.com/openconfig/goyang@064f9690516f4f72db189f4690b84622c13b7296 \
               github.com/pkg/profile@https\://github.com/pkg/profile@3704c8d23324a3fc0771ad2c1cef0aa4e9459f6f \
               github.com/go-playground/locales@https\://github.com/go-playground/locales@ac5643571b2e4508ec50f9a132b5a683412b5bbe \
               github.com/go-playground/universal-translator@https\://github.com/go-playground/universal-translator@f87b1403479a348651dbf5f07f5cc6e5fcf07008 \
               github.com/leodido/go-urn@https\://github.com/leodido/go-urn@a0f5013415294bb94553821ace21a1a74c0298cc \
               github.com/Workiva/go-datastructures@https\://github.com/Workiva/go-datastructures@0819bcaf26091e7c33585441f8961854c2400faa \
               github.com/facette/natsort@https\://github.com/facette/natsort@2cd4dd1e2dcba4d85d6d3ead4adf4cfd2b70caf2 \
               github.com/kylelemons/godebug@https\://github.com/kylelemons/godebug@e693023230a4a8be4e28c9bd02f467b0534ac08b \
               github.com/google/go-cmp@https\://github.com/google/go-cmp@ec71d6d790538ad88c95a192fd059e11afb45b6f \
               github.com/antchfx/xpath@https\://github.com/antchfx/xpath@d9ad276609987dd73ce5cd7d6265fe82189b10b6 \
               github.com/antchfx/jsonquery@https\://github.com/antchfx/jsonquery@3b69d31134d889b501e166a035a4d5ecb8c6c367 \
               github.com/antchfx/xmlquery@https\://github.com/antchfx/xmlquery@fe009d4cc63c3011f05e1dfa75a27899acccdf11 \
               github.com/pborman/getopt@https\://github.com/pborman/getopt@dcd73336fd9c322469cb3248fcfcd883aaa65e19 \
               github.com/gorilla/mux@https\://github.com/gorilla/mux@d07530f46e1eec4e40346e24af34dcc6750ad39f \
               github.com/msteinert/pam@https\://github.com/msteinert/pam@e61372126161db56aa15734b7575714920c274ac \
               github.com/dgrijalva/jwt-go@https\://github.com/dgrijalva/jwt-go@dc14462fd58732591c7fa58cc8496d6824316a82 \
               github.com/philopon/go-toposort@https\://github.com/philopon/go-toposort@9be86dbd762f98b5b9a4eca110a3f40ef31d0375

REST_BIN = $(BUILD_DIR)/rest_server/main
CERTGEN_BIN = $(BUILD_DIR)/rest_server/generate_cert

go-deps = $(BUILD_DIR)/gopkgs/.done
go-patch = $(BUILD_DIR)/gopkgs/.patch_done

all: build-deps $(go-deps) $(go-patch) translib rest-server cli ham

build-deps:
	mkdir -p $(BUILD_DIR)/gopkgs

cli: 
	$(MAKE) -C src/CLI

clish:
	SONIC_CLI_ROOT=$(BUILD_DIR) $(MAKE) -C src/CLI/klish

clitree:
	 TGT_DIR=$(BUILD_DIR)/cli $(MAKE) -C src/CLI/clitree

clidocgen:
	 TGT_DIR=$(BUILD_DIR)/cli $(MAKE) -C src/CLI/clitree doc_gen

clidocgen-clean:
	TGT_DIR=$(BUILD_DIR)/cli $(MAKE) -C src/CLI/clitree doc_gen_clean

cvl: $(go-deps) $(go-patch)
	$(MAKE) -C src/cvl

cvl-test:
	$(MAKE) -C src/cvl gotest

rest-server: build-deps translib
	$(MAKE) -C src/rest

rest-clean:
	$(MAKE) -C src/rest clean

translib: cvl
	$(MAKE) -C src/translib

codegen:
	$(MAKE) -C models

yamlGen:
	$(MAKE) -C models/yang
	$(MAKE) -C models/yang/sonic

ham:
	(cd src/ham; ./build.sh)

.PHONY: go-deps-list
go-deps-list: $(GO_DEPS_LIST)

$(GO_DEPS_LIST):
	TODIR=$(BUILD_GOPATH)/src/$(word 1,$(subst @, , $@)) && \
		  $(RM) -r $${TODIR} && mkdir -p $${TODIR} && \
		  git clone $(word 2,$(subst @, , $@)) $${TODIR} && \
		  git -C $${TODIR} reset --hard $(word 3,$(subst @, , $@))

$(go-deps): $(MAKEFILE_LIST)
	$(MAKE) go-deps-list
	touch $@

$(go-patch): $(go-deps)
	cd $(BUILD_GOPATH)/src/github.com/openconfig/goyang && \
		patch -p1 < $(TOPDIR)/goyang-modified-files/goyang.patch
	$(GO) install -v -gcflags "-N -l" $(BUILD_GOPATH)/src/github.com/openconfig/goyang
	cd $(BUILD_GOPATH)/src/github.com/openconfig && \
		patch -p1 < $(TOPDIR)/ygot-modified-files/ygot.patch
	cd $(BUILD_GOPATH)/src/github.com/antchfx/xpath && \
		git apply $(TOPDIR)/patches/xpath.patch
	cd $(BUILD_GOPATH)/src/github.com/antchfx/jsonquery && \
		git apply $(TOPDIR)/patches/jsonquery.patch
	cd $(BUILD_GOPATH)/src/github.com/antchfx/xmlquery && \
		git apply $(TOPDIR)/patches/xmlquery.patch
	touch  $@

install:
	$(INSTALL) -D $(REST_BIN) $(DESTDIR)/usr/sbin/rest_server
	$(INSTALL) -D $(CERTGEN_BIN) $(DESTDIR)/usr/sbin/generate_cert
	$(INSTALL) -d $(DESTDIR)/usr/sbin/schema/
	$(INSTALL) -d $(DESTDIR)/usr/sbin/lib/
	$(INSTALL) -d $(DESTDIR)/usr/bin/
	$(INSTALL) -d $(DESTDIR)/usr/models/yang/
	$(INSTALL) -D $(TOPDIR)/models/yang/sonic/*.yang $(DESTDIR)/usr/models/yang/
	$(INSTALL) -D $(TOPDIR)/models/yang/sonic/common/*.yang $(DESTDIR)/usr/models/yang/
	$(INSTALL) -D $(TOPDIR)/models/yang/*.yang $(DESTDIR)/usr/models/yang/
	$(INSTALL) -D $(TOPDIR)/config/transformer/models_list $(DESTDIR)/usr/models/yang/
	$(INSTALL) -D $(TOPDIR)/config/transformer/sonic_table_info.json $(DESTDIR)/usr/models/yang/
	$(INSTALL) -D $(TOPDIR)/models/yang/common/*.yang $(DESTDIR)/usr/models/yang/
	$(INSTALL) -D $(TOPDIR)/models/yang/annotations/*.yang $(DESTDIR)/usr/models/yang/
	$(INSTALL) -D $(TOPDIR)/models/yang/extensions/*.yang $(DESTDIR)/usr/models/yang/
	$(INSTALL) -D $(TOPDIR)/models/yang/version.xml $(DESTDIR)/usr/models/yang/
	$(INSTALL) -D $(TOPDIR)/build/yaml/api_ignore $(DESTDIR)/usr/models/yang/
	cp -rf $(TOPDIR)/build/rest_server/dist/ui/ $(DESTDIR)/rest_ui/
	cp -rf $(TOPDIR)/build/cli $(DESTDIR)/usr/sbin/
	rsync -a --exclude="test" --exclude="docs" build/swagger_client_py $(DESTDIR)/usr/sbin/lib/
	cp -rf $(TOPDIR)/src/cvl/conf/cvl_cfg.json $(DESTDIR)/usr/sbin/cvl_cfg.json

# Copy all CVL schema files
	cp -aT build/cvl/schema $(DESTDIR)/usr/sbin/schema

	# Scripts for host service
	$(INSTALL) -d $(DESTDIR)/usr/lib/sonic_host_service/host_modules
	$(INSTALL) -D $(TOPDIR)/scripts/sonic_host_server.py $(DESTDIR)/usr/lib/sonic_host_service
	$(INSTALL) -D $(TOPDIR)/scripts/host_modules/*.py $(DESTDIR)/usr/lib/sonic_host_service/host_modules
ifneq ($(ENABLE_ZTP),y)
	$(RM) -f $(DESTDIR)/usr/lib/sonic_host_service/host_modules/ztp_handler.py
endif
	$(INSTALL) -d $(DESTDIR)/etc/dbus-1/system.d
	$(INSTALL) -D $(TOPDIR)/scripts/org.sonic.hostservice.conf $(DESTDIR)/etc/dbus-1/system.d
	$(INSTALL) -d $(DESTDIR)/lib/systemd/system
	$(INSTALL) -D $(TOPDIR)/scripts/sonic-hostservice.service $(DESTDIR)/lib/systemd/system
	$(INSTALL) -d $(DESTDIR)/etc/sonic/
	$(INSTALL) -D $(TOPDIR)/config/cfg_mgmt.json $(DESTDIR)/etc/sonic/

	# Scripts for Host Account Management (HAM)
	$(INSTALL) -D $(TOPDIR)/src/ham/hamd/etc/dbus-1/system.d/* $(DESTDIR)/etc/dbus-1/system.d/
	$(INSTALL) -d $(DESTDIR)/etc/sonic/hamd/
	$(INSTALL) -D $(TOPDIR)/src/ham/hamd/etc/sonic/hamd/*      $(DESTDIR)/etc/sonic/hamd/
	$(INSTALL) -D $(TOPDIR)/src/ham/hamd/lib/systemd/system/*  $(DESTDIR)/lib/systemd/system/
	$(INSTALL) -D $(TOPDIR)/src/ham/hamd/usr/bin/*             $(DESTDIR)/usr/bin/
	$(INSTALL) -D $(TOPDIR)/src/ham/hamd/hamd     $(DESTDIR)/usr/sbin/.
	$(INSTALL) -D $(TOPDIR)/src/ham/hamctl/hamctl $(DESTDIR)/usr/bin/.
	$(INSTALL) -d $(DESTDIR)/lib/x86_64-linux-gnu/
	$(INSTALL) -D $(TOPDIR)/src/ham/libnss_ham/libnss_ham.so.2 $(DESTDIR)/lib/x86_64-linux-gnu/.

	# Scripts for the certificate fixer oneshot service
	$(INSTALL) -D $(TOPDIR)/src/certfix/usr/sbin/*             $(DESTDIR)/usr/sbin/
	$(INSTALL) -D $(TOPDIR)/src/certfix/lib/systemd/system/*   $(DESTDIR)/lib/systemd/system/

ifeq ($(SONIC_COVERAGE_ON),y)
	echo "" > $(DESTDIR)/usr/sbin/.test
endif

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	mv $* $(DEST)/

clean: rest-clean
	$(MAKE) -C src/translib clean
	$(MAKE) -C src/cvl clean
	(cd src/ham; ./build.sh clean)
	rm -rf debian/.debhelper
	(cd build && find .  -maxdepth 1 -name "gopkgs" -prune -o -not -name '.' -exec rm -rf {} +) || true

cleanall:
	$(MAKE) -C src/cvl cleanall
	rm -rf build/*

