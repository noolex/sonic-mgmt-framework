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
BUILD_DIR := $(TOPDIR)/build

YANGAPI_DIR                 := $(TOPDIR)/build/yaml
YANGAPI3_DIR                := $(TOPDIR)/build/openapi3
MD_DIR                      := $(TOPDIR)/build/restconf_md

YANGDIR                     := yangs
YANGDIR_COMMON              := $(YANGDIR)/common
YANGDIR_EXTENSIONS          := $(YANGDIR)/extensions
YANG_MOD_FILES              := $(shell find $(YANGDIR)/ -maxdepth 1 -name '*.yang')
YANG_MOD_EXTENSION_FILES    := $(shell find $(YANGDIR_EXTENSIONS) -maxdepth 1 -name '*.yang')
YANG_COMMON_FILES           := $(shell find $(YANGDIR_COMMON) -name '*.yang')

YANGDIR_SONIC               := $(YANGDIR)/sonic
YANGDIR_SONIC_COMMON        := $(YANGDIR_SONIC)/common
SONIC_YANG_MOD_FILES        := $(shell find $(YANGDIR_SONIC) -maxdepth 1 -name '*.yang')
SONIC_YANG_COMMON_FILES     := $(shell find $(YANGDIR_SONIC)/common -name '*.yang')

TOOLS_DIR        := $(TOPDIR)/tools
PYANG_PLUGIN_DIR := $(TOOLS_DIR)/pyang/pyang_plugins
PYANG  ?= pyang
RMDIR  ?= rm -rf

all: $(YANGAPI_DIR)/.done $(YANGAPI_DIR)/.sonic_done

.PRECIOUS: %/.
%/.:
	mkdir -p $@

#======================================================================
# Generate YAML files for Yang modules
#======================================================================
$(YANGAPI_DIR)/.done: $(YANG_MOD_FILES) $(YANG_COMMON_FILES) $(YANGAPI_DIR)/. $(MD_DIR)/.
	@echo "+++++ Generating YAML files for Yang modules +++++"
	$(PYANG) \
		-f swaggerapi \
		--with-md-doc \
		--outdir $(YANGAPI_DIR) \
		--md-outdir $(MD_DIR) \
		--plugindir $(PYANG_PLUGIN_DIR) \
		-p $(YANGDIR_COMMON):$(YANGDIR):$(YANGDIR_EXTENSIONS) \
		$(YANG_MOD_FILES) $(YANG_MOD_EXTENSION_FILES)
	@echo "+++++ Generation of  YAML files for Yang modules completed +++++"
	touch $@

#======================================================================
# Generate YAML files for SONiC YANG modules
#======================================================================
$(YANGAPI_DIR)/.sonic_done: $(SONIC_YANG_MOD_FILES) $(SONIC_YANG_COMMON_FILES) $(YANGAPI_DIR)/. $(MD_DIR)/.
	@echo "+++++ Generating YAML files for Sonic Yang modules +++++"
	$(PYANG) \
		-f swaggerapi \
		--with-md-doc \
		--outdir $(YANGAPI_DIR) \
		--md-outdir $(MD_DIR) \
		--plugindir $(PYANG_PLUGIN_DIR) \
		-p $(YANGDIR_SONIC_COMMON):$(YANGDIR_SONIC) \
		$(SONIC_YANG_MOD_FILES)
	@echo "+++++ Generation of  YAML files for Sonic Yang modules completed +++++"
	touch $@

#======================================================================
# TODO: Temporary remove this when V3 plugin is enabled
#======================================================================
openapi3:  $(YANG_MOD_FILES) $(YANG_COMMON_FILES) $(YANGAPI3_DIR)/.
	@echo "+++++ Generating OpenAPI specs for Yang modules +++++"
	$(PYANG) \
		-f openapiv3 \
		--outputdir $(YANGAPI3_DIR) \
		--plugindir $(PYANG_PLUGIN_DIR) \
		-p $(YANGDIR_COMMON):$(YANGDIR):$(YANGDIR_EXTENSIONS):$(YANGDIR_SONIC_COMMON):$(YANGDIR_SONIC) \
		$(YANG_MOD_FILES) $(YANG_MOD_EXTENSION_FILES) $(SONIC_YANG_MOD_FILES)
	@echo "+++++ Generation of  OpenAPI V3 specs for Yang modules completed +++++"
	
#======================================================================
# Cleanups
#======================================================================

clean:
	$(RMDIR) $(YANGAPI_DIR)
	$(RMDIR) $(MD_DIR)

cleanall: clean

