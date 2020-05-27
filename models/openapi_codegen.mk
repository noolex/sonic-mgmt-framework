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

TOPDIR := ..
ABS_TOPDIR := $(abspath $(TOPDIR))

BUILD_DIR := $(TOPDIR)/build
CODEGEN_TOOLS_DIR := $(TOPDIR)/tools/swagger_codegen

CODEGEN_VER	:= 4.2.3
CODEGEN_JAR := $(CODEGEN_TOOLS_DIR)/openapi-generator-cli-$(CODEGEN_VER).jar

SERVER_BUILD_DIR	:= $(BUILD_DIR)/rest_server
SERVER_CODEGEN_DIR	:= $(SERVER_BUILD_DIR)/codegen
SERVER_DIST_DIR		:= $(SERVER_BUILD_DIR)/dist
SERVER_DIST_INIT	:= $(SERVER_DIST_DIR)/.init_done
SERVER_DIST_GO		:= $(SERVER_DIST_DIR)/openapi
SERVER_DIST_UI		:= $(SERVER_DIST_DIR)/ui
SERVER_DIST_UI_HOME	:= $(SERVER_DIST_UI)/index.html
RESTCONF_MD_INDEX	:= $(BUILD_DIR)/restconf_md/index.md

include codegen.config

YANGAPI_DIR     := $(TOPDIR)/build/yaml
YANGAPI_SPECS   := $(shell find $(YANGAPI_DIR) -name '*.yaml' 2> /dev/null)
YANGAPI_NAMES   := $(filter-out $(YANGAPI_EXCLUDES), $(basename $(notdir $(YANGAPI_SPECS))))
YANGAPI_SERVERS := $(addsuffix /.yangapi_done, $(addprefix $(SERVER_CODEGEN_DIR)/, $(YANGAPI_NAMES)))

OPENAPI_DIR     := openapi
OPENAPI_SPECS   := $(shell find $(OPENAPI_DIR) -name '*.yaml')
OPENAPI_NAMES   := $(filter-out $(OPENAPI_EXCLUDES), $(basename $(notdir $(OPENAPI_SPECS))))
OPENAPI_SERVERS := $(addsuffix /.openapi_done, $(addprefix $(SERVER_CODEGEN_DIR)/, $(OPENAPI_NAMES)))

PY_YANGAPI_NAMES       := $(filter $(YANGAPI_NAMES), $(PY_YANGAPI_CLIENTS))
PY_OPENAPI_NAMES       := $(filter $(OPENAPI_NAMES), $(PY_OPENAPI_CLIENTS))
PY_CLIENT_CODEGEN_DIR  := $(BUILD_DIR)/openapi_client_py
PY_CLIENT_TARGETS := $(addsuffix .yangapi_client, $(addprefix $(PY_CLIENT_CODEGEN_DIR)/, $(PY_YANGAPI_NAMES))) \
                     $(addsuffix .openapi_client, $(addprefix $(PY_CLIENT_CODEGEN_DIR)/, $(PY_OPENAPI_NAMES)))

UIGEN_DIR  = $(TOPDIR)/tools/ui_gen
UIGEN_SRCS = $(shell find $(UIGEN_DIR) -type f)

JAVA   ?= java

.PHONY: all clean cleanall go-server py-client

all: go-server py-client

go-server-init: $(SERVER_DIST_INIT)

go-server: $(YANGAPI_SERVERS) $(OPENAPI_SERVERS) $(SERVER_DIST_INIT) $(SERVER_DIST_UI_HOME) $(RESTCONF_MD_INDEX)

py-client: $(PY_CLIENT_CODEGEN_DIR)/. $(PY_CLIENT_TARGETS)

$(SERVER_DIST_UI_HOME): $(YANGAPI_SERVERS) $(OPENAPI_SERVERS) $(UIGEN_SRCS)
	@echo "+++ Generating  landing page for Swagger UI +++"
	$(UIGEN_DIR)/src/uigen.py

$(RESTCONF_MD_INDEX): $(YANGAPI_SERVERS) $(OPENAPI_SERVERS)
	@echo "+++ Generating index page for RESTCONF documents +++"
	$(TOPDIR)/tools/restconf_doc_tools/index.py --mdDir $(BUILD_DIR)/restconf_md


.SECONDEXPANSION:

#======================================================================
# Common rule for directories. Use "." suffix, like "xyz/."
#======================================================================
.PRECIOUS: %/. 
%/.:
	mkdir -p $@

#======================================================================
# Download openapi codegen jar from Maven.org repo. It will be saved as
# build/openapi-codegen-cli.jar file.
#======================================================================
$(CODEGEN_JAR): | $$(@D)/.
	cd $(@D) && \
	wget https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/$(CODEGEN_VER)/$(@F)

#======================================================================
# Generate openapi server in GO language for Yang generated OpenAPIs
# specs.
#======================================================================
%/.yangapi_done: $(YANGAPI_DIR)/$$(*F).yaml | $$(@D)/. $(CODEGEN_JAR) $(SERVER_DIST_INIT)
	@echo "+++ Generating GO server for Yang API $$(basename $(@D)).yaml +++"
	$(JAVA) -jar $(CODEGEN_JAR) generate \
		-g go-server \
		--input-spec $(YANGAPI_DIR)/$$(basename $(@D)).yaml \
		--template-dir $(CODEGEN_TOOLS_DIR)/go-server/templates-yang \
		--output $(@D)
	rm -rf  $(@D)/go/api_*service.go
	cp $(@D)/go/api_* $(SERVER_DIST_GO)/
	cp $(@D)/go/routers.go $(SERVER_DIST_GO)/routers_$$(basename $(@D)).go
	cp $(@D)/api/openapi.yaml $(SERVER_DIST_UI)/$$(basename $(@D)).yaml
	touch $@

#======================================================================
# Generate openapi server in GO language for handcoded OpenAPI specs
#======================================================================
%/.openapi_done: $(OPENAPI_DIR)/$$(*F).yaml | $$(@D)/. $(CODEGEN_JAR) $(SERVER_DIST_INIT)
	@echo "+++ Generating GO server for OpenAPI $$(basename $(@D)).yaml +++"
	$(JAVA) -jar $(CODEGEN_JAR) generate \
		-g go-server \
		--input-spec $(OPENAPI_DIR)/$$(basename $(@D)).yaml \
		--template-dir $(CODEGEN_TOOLS_DIR)/go-server/templates-nonyang \
		--output $(@D)
	rm -rf  $(@D)/go/api_*service.go
	cp $(@D)/go/api_* $(@D)/go/model_* $(SERVER_DIST_GO)/
	cp $(@D)/go/routers.go $(SERVER_DIST_GO)/routers_$$(basename $(@D)).go
	cp $(@D)/api/openapi.yaml $(SERVER_DIST_UI)/$$(basename $(@D)).yaml
	touch $@

#======================================================================
# Initialize dist directory for GO server code
#======================================================================
$(SERVER_DIST_INIT): | $$(@D)/.
	cp -r $(CODEGEN_TOOLS_DIR)/ui-dist $(@D)/ui
	cp -r $(CODEGEN_TOOLS_DIR)/go-server/src/* $(@D)/
	touch $@

#======================================================================
# Generate openapi client in Python for yang generated OpenAPI specs
#======================================================================
%.yangapi_client: $(YANGAPI_DIR)/$$(*F).yaml | $(CODEGEN_JAR) $$(@D)/.
	@echo "+++++ Generating Python client for $(*F).yaml +++++"
	$(JAVA) -jar $(CODEGEN_JAR) generate \
		--package-name $(subst -,_,$(*F))_client \
		-g python \
		--input-spec $(YANGAPI_DIR)/$(*F).yaml \
		--template-dir $(CODEGEN_TOOLS_DIR)/py-client/templates \
		--output $(@D)
	touch $@

#======================================================================
# Generate openapi client in Python for handcoded OpenAPI specs
#======================================================================
%.openapi_client: $(OPENAPI_DIR)/$$(*F).yaml | $(CODEGEN_JAR) $$(@D)/.
	@echo "+++++ Generating Python client for $(*F).yaml +++++"
	$(JAVA) -jar $(CODEGEN_JAR) generate \
		--package-name $(subst -,_,$(*F))_client \
		-g python \
		--input-spec $(OPENAPI_DIR)/$(*F).yaml \
		--template-dir $(CODEGEN_TOOLS_DIR)/py-client/templates \
		--output $(@D)
	touch $@

#======================================================================
# Cleanups
#======================================================================

clean-server:
	$(RM) -r $(SERVER_DIST_DIR)
	$(RM) -r $(SERVER_CODEGEN_DIR)
	$(RM) $(SERVER_DIST_UI_HOME)

clean-client:
	$(RM) -r $(PY_CLIENT_CODEGEN_DIR)

clean: clean-server clean-client

cleanall: clean
	$(RM) $(CODEGEN_JAR)

