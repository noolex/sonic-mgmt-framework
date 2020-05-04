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

.ONESHELL:
.SHELLFLAGS += -e

TOPDIR := $(abspath .)
BUILD_DIR := $(TOPDIR)/build
MGMT_COMMON_DIR := $(abspath ../sonic-mgmt-common)

GO      ?= /usr/local/go/bin/go
GOPATH  ?= /tmp/go
RMDIR   ?= rm -rf
INSTALL := /usr/bin/install

MAIN_TARGET = sonic-mgmt-framework_1.0-01_amd64.deb

GO_MOD   = go.mod
GO_DEPS  = vendor/.done

export TOPDIR MGMT_COMMON_DIR GO GOPATH RMDIR

.PHONY: all
all: rest cli ham

$(GO_MOD):
	$(GO) mod init github.com/Azure/sonic-mgmt-framework

$(GO_DEPS): $(GO_MOD)
	$(MAKE) -C models -f openapi_codegen.mk go-server-init
	$(GO) mod vendor
	$(MGMT_COMMON_DIR)/patches/apply.sh vendor
	touch  $@

go-deps-clean:
	$(RMDIR) vendor

cli: 
	$(MAKE) -C CLI

clish:
	SONIC_CLI_ROOT=$(BUILD_DIR) $(MAKE) -C CLI/klish

clitree:
	TGT_DIR=$(BUILD_DIR)/cli $(MAKE) -C CLI/clitree

clidocgen:
	TGT_DIR=$(BUILD_DIR)/cli $(MAKE) -C CLI/clitree doc_gen

clidocgen-clean:
	TGT_DIR=$(BUILD_DIR)/cli $(MAKE) -C CLI/clitree doc_gen_clean

.PHONY: rest
rest: $(GO_DEPS) models
	$(MAKE) -C rest

# Special target for local compilation of REST server binary.
# Compiles models, translib and cvl schema from sonic-mgmt-common
rest-server: rest-clean
	$(MAKE) -C $(MGMT_COMMON_DIR)/models
	TOPDIR=$(MGMT_COMMON_DIR) $(MAKE) -C $(MGMT_COMMON_DIR)/cvl/schema
	$(MAKE) -C $(MGMT_COMMON_DIR)/translib ocbinds/ocbinds.go
	$(MAKE) rest

rest-clean: go-deps-clean
	$(MAKE) -C rest clean

.PHONY: models
models:
	$(MAKE) -C models

models-clean:
	$(MAKE) -C models clean

.PHONY: ham
ham:
	(cd ham; ./build.sh)


install:
	$(INSTALL) -D $(BUILD_DIR)/rest_server/main $(DESTDIR)/usr/sbin/rest_server
	$(INSTALL) -D $(BUILD_DIR)/rest_server/generate_cert $(DESTDIR)/usr/sbin/generate_cert
	$(INSTALL) -d $(DESTDIR)/usr/sbin/lib/
	$(INSTALL) -d $(DESTDIR)/usr/bin/
	cp -rf $(TOPDIR)/build/rest_server/dist/ui/ $(DESTDIR)/rest_ui/
	cp -rf $(TOPDIR)/build/cli $(DESTDIR)/usr/sbin/
	rsync -a --exclude="test" --exclude="docs" build/swagger_client_py $(DESTDIR)/usr/sbin/lib/
	
	$(INSTALL) -d $(DESTDIR)/etc/dbus-1/system.d
	$(INSTALL) -d $(DESTDIR)/lib/systemd/system
	
	# Scripts for Host Account Management (HAM)
	$(INSTALL) -D $(TOPDIR)/ham/hamd/etc/dbus-1/system.d/* $(DESTDIR)/etc/dbus-1/system.d/
	$(INSTALL) -d $(DESTDIR)/etc/sonic/hamd/
	$(INSTALL) -D $(TOPDIR)/ham/hamd/etc/sonic/hamd/*      $(DESTDIR)/etc/sonic/hamd/
	$(INSTALL) -D $(TOPDIR)/ham/hamd/lib/systemd/system/*  $(DESTDIR)/lib/systemd/system/
	$(INSTALL) -D $(TOPDIR)/ham/hamd/usr/bin/*             $(DESTDIR)/usr/bin/
	$(INSTALL) -D $(TOPDIR)/ham/hamd/hamd     $(DESTDIR)/usr/sbin/.
	$(INSTALL) -D $(TOPDIR)/ham/hamctl/hamctl $(DESTDIR)/usr/bin/.
	$(INSTALL) -d $(DESTDIR)/lib/x86_64-linux-gnu/
	$(INSTALL) -D $(TOPDIR)/ham/libnss_ham/libnss_ham.so.2 $(DESTDIR)/lib/x86_64-linux-gnu/.
	
	# Scripts for the certificate fixer oneshot service
	$(INSTALL) -D $(TOPDIR)/certfix/usr/sbin/*             $(DESTDIR)/usr/sbin/
	$(INSTALL) -D $(TOPDIR)/certfix/lib/systemd/system/*   $(DESTDIR)/lib/systemd/system/
	
ifeq ($(SONIC_COVERAGE_ON),y)
	echo "" > $(DESTDIR)/usr/sbin/.test
endif

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	mv $* $(DEST)/

clean: rest-clean models-clean
	(cd ham; ./build.sh clean)
	$(RMDIR) debian/.debhelper

cleanall: clean
	$(RMDIR) $(BUILD_DIR)

