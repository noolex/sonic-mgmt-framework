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

TEST_ARGS=()
REST_ARGS=()
PIPE=tee
GO=go

while [[ $# -gt 0 ]]; do
case "$1" in
    -h|-help|--help)
        echo "usage: $0 [-run NAME] [-auth] [-json] [-tparse] [ARGS...]"
        echo ""
        echo " -run NAME  Run specific test cases."
        echo " -auth      Run local password authentication test cases"
        echo "            Extra arguments may be needed as described in auth_test.go"
        echo " -sudo      Run as 'sudo -E go test ...'. Usually required for auth tests"
        echo " -json      Prints output in json format"
        echo " -tparse    Render output through tparse; implicitly enables -json"
        echo " -deps      Rebuild go dependencies"
        echo " ARGS...    Arguments to test program (log level, auth test arguments etc)"
        exit 0 ;;
    -auth)
        TEST_ARGS+=("-run" "Auth")
        REST_ARGS+=("-authtest" "local")
        shift ;;
    -run)
        TEST_ARGS+=("-run" "$2")
        shift 2 ;;
    -json)
        TEST_ARGS+=("-json")
        shift ;;
    -tparse)
        TEST_ARGS+=("-json")
        PIPE=tparse
        shift ;;
    -sudo)
        GO="sudo -E $(which go)"
        shift ;;
    -deps|-go-deps)
        REBUILD_DEPS=yes
        shift ;;
    *)
        REST_ARGS+=("$1")
        shift;;
esac
done

MGMT_COMMON_DIR=$(realpath $TOPDIR/../sonic-mgmt-common)

export GOPATH=/tmp/go

export CVL_SCHEMA_PATH=$MGMT_COMMON_DIR/build/cvl/schema

export DB_CONFIG_PATH=$MGMT_COMMON_DIR/tools/test/database_config.json

if [ "$REBUILD_DEPS" == "yes" ]; then
    NO_TEST_BINS=1 make -s -C $MGMT_COMMON_DIR
    make -s go-deps-clean
    make -s go-deps
fi

if [ -z $YANG_MODELS_PATH ]; then
    export YANG_MODELS_PATH=$TOPDIR/build/all_test_yangs
    mkdir -p $YANG_MODELS_PATH
    pushd $YANG_MODELS_PATH > /dev/null
    rm -f *
    find $MGMT_COMMON_DIR/models/yang -name "ietf-*.yang" -not -path "*/annotations/*" -exec ln -sf {} \;
    popd > /dev/null
fi

${GO} test -mod=vendor ./rest/server -v -cover "${TEST_ARGS[@]}" -args -logtostderr "${REST_ARGS[@]}" | ${PIPE}
