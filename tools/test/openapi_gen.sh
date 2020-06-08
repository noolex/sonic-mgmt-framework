#!/usr/bin/env bash

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

set -e

TOPDIR=$PWD
BUILD_DIR=$TOPDIR/build
MODELS_DIR=$TOPDIR/models
cd $MODELS_DIR
export OPENAPI_EXTENDED=True
make -f yang_to_openapi.mk clean
mkdir -p $BUILD_DIR/yaml
touch $BUILD_DIR/yaml/.openapi_gen_ut
make -f yang_to_openapi.mk all
echo "++++++++++ Please find OpenAPIs generated at $BUILD_DIR/yaml ++++++++"
