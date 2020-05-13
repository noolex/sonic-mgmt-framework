#!/usr/bin/python
###########################################################################
#
# Copyright 2019 Broadcom, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###########################################################################

import sys
import time
import json
import ast
from rpipe_utils import pipestr
import cli_client as cc
from scripts.render_cli import show_cli_output

def apply_vrf_filter(response, inputvrf):
    if "null" != inputvrf:
        new_list_shop = []
        new_list_mhop = []
        if 'openconfig-bfd-ext:bfd-state' in response:
            if 'single-hop-state' in response['openconfig-bfd-ext:bfd-state']:
                for i in range(len(response['openconfig-bfd-ext:bfd-state']['single-hop-state'])):
                    shopsession = response['openconfig-bfd-ext:bfd-state']['single-hop-state'][i]
                    if inputvrf == shopsession['vrf']:
                        new_list_shop.append(shopsession)
                response['openconfig-bfd-ext:bfd-state']['single-hop-state'] = new_list_shop
        if 'openconfig-bfd-ext:bfd-state' in response:
            if 'multi-hop-state' in response['openconfig-bfd-ext:bfd-state']:
                for i in range(len(response['openconfig-bfd-ext:bfd-state']['multi-hop-state'])):
                    mhopsession = response['openconfig-bfd-ext:bfd-state']['multi-hop-state'][i]
                    if inputvrf == mhopsession['vrf']:
                        new_list_mhop.append(mhopsession)
                response['openconfig-bfd-ext:bfd-state']['multi-hop-state'] = new_list_mhop

def invoke_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None

    #Patch cases
    if func == 'patch_openconfig_bfd_ext_bfd_sessions_single_hop':
	if len(args) == 3:
	    print("%Error: Interface must be configured for single-hop peer")
	    exit(1)

        if args[2] != "default" and args[1] == "null":
            print("%Error: Interface must be configured for non-default vrf")
            exit(1)

        keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:sessions/single-hop={address},{interfacename},{vrfname},{localaddress}/enabled', address=args[0], interfacename=args[1], vrfname=args[2],localaddress=args[3])
        body = {"openconfig-bfd-ext:enabled": True}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_multi_hop':
	if args[3] == "null":
            print("%Error: Local Address must be configured for multi-hop peer")
            exit(1)

        keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:sessions/multi-hop={address},{interfacename},{vrfname},{localaddress}/enabled', address=args[0], interfacename=args[1], vrfname=args[2], localaddress=args[3])
        body = {"openconfig-bfd-ext:enabled": True}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_single_hop_enabled':
        keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:sessions/single-hop={address},{interfacename},{vrfname},{localaddress}/enabled', address=args[0], interfacename=args[1], vrfname=args[2],localaddress=args[3])
        body = {"openconfig-bfd-ext:enabled": True}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_single_hop_disable':
        keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:sessions/single-hop={address},{interfacename},{vrfname},{localaddress}/enabled', address=args[0], interfacename=args[1], vrfname=args[2],localaddress=args[3])
        body = {"openconfig-bfd-ext:enabled": False}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_single_hop_desired_minimum_tx_interval':
        keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:sessions/single-hop={address},{interfacename},{vrfname},{localaddress}/desired-minimum-tx-interval', address=args[0], interfacename=args[1], vrfname=args[2],localaddress=args[3])
        body = {"openconfig-bfd-ext:desired-minimum-tx-interval": int(args[4])}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_single_hop_required_minimum_receive':
        keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:sessions/single-hop={address},{interfacename},{vrfname},{localaddress}/required-minimum-receive', address=args[0], interfacename=args[1], vrfname=args[2],localaddress=args[3])
        body = {"openconfig-bfd-ext:required-minimum-receive": int(args[4])}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_single_hop_detection_multiplier':
        keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:sessions/single-hop={address},{interfacename},{vrfname},{localaddress}/detection-multiplier', address=args[0], interfacename=args[1], vrfname=args[2],localaddress=args[3])
        body = {"openconfig-bfd-ext:detection-multiplier": int(args[4])}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_single_hop_desired_minimum_echo_receive':
        keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:sessions/single-hop={address},{interfacename},{vrfname},{localaddress}/desired-minimum-echo-receive', address=args[0], interfacename=args[1], vrfname=args[2],localaddress=args[3])
        body = {"openconfig-bfd-ext:desired-minimum-echo-receive": int(args[4])}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_single_hop_echo_active':
        keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:sessions/single-hop={address},{interfacename},{vrfname},{localaddress}/echo-active', address=args[0], interfacename=args[1], vrfname=args[2], localaddress=args[3])
        body = {"openconfig-bfd-ext:echo-active": True}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_single_hop_echo_active_disable':
        keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:sessions/single-hop={address},{interfacename},{vrfname},{localaddress}/echo-active', address=args[0], interfacename=args[1], vrfname=args[2], localaddress=args[3])
        body = {"openconfig-bfd-ext:echo-active": False}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_multi_hop_enabled':
        keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:sessions/multi-hop={address},{interfacename},{vrfname},{localaddress}/enabled', address=args[0], interfacename=args[1], vrfname=args[2],localaddress=args[3])        
	body = {"openconfig-bfd-ext:enabled": True}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_multi_hop_disable':
        keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:sessions/multi-hop={address},{interfacename},{vrfname},{localaddress}/enabled', address=args[0], interfacename=args[1], vrfname=args[2],localaddress=args[3])
        body = {"openconfig-bfd-ext:enabled": False}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_multi_hop_desired_minimum_tx_interval':
        keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:sessions/multi-hop={address},{interfacename},{vrfname},{localaddress}/desired-minimum-tx-interval', address=args[0], interfacename=args[1], vrfname=args[2],localaddress=args[3])
	body = {"openconfig-bfd-ext:desired-minimum-tx-interval": int(args[4])}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_multi_hop_required_minimum_receive':
        keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:sessions/multi-hop={address},{interfacename},{vrfname},{localaddress}/required-minimum-receive', interfacename=args[1], address=args[0], vrfname=args[2],localaddress=args[3])       
	body = {"openconfig-bfd-ext:required-minimum-receive": int(args[4])}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_multi_hop_detection_multiplier':
        keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:sessions/multi-hop={address},{interfacename},{vrfname},{localaddress}/detection-multiplier', address=args[0], interfacename=args[1], vrfname=args[2],localaddress=args[3])       
	body = {"openconfig-bfd-ext:detection-multiplier": int(args[4])}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_multi_hop_desired_minimum_echo_receive':
	print("%Error: Echo-mode is not supported for multihop peer")
        exit(1)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_multi_hop_echo_active':
        print("%Error: Echo-mode is not supported for multihop peer")
        exit(1)
    elif func == 'delete_openconfig_bfd_ext_bfd_sessions_single_hop':
        if len(args) == 3:
            print("%Error: Interface must be configured for single-hop peer")
            exit(1)

        keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:sessions/single-hop={address},{interfacename},{vrfname},{localaddress}', address=args[0], interfacename=args[1], vrfname=args[2], localaddress=args[3])
        return api.delete(keypath)
    elif func == 'delete_openconfig_bfd_ext_bfd_sessions_multi_hop':

        if args[2] == "null":
            print("%Error: Local Address must be configured for multi-hop peer")
            exit(1)

        keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:sessions/multi-hop={address},{interfacename},{vrfname},{localaddress}', address=args[0], interfacename=args[1], vrfname=args[2],localaddress=args[3])
        return api.delete(keypath)

    return api.cli_not_implemented(func)


def invoke_show_api(func, args=[]):
	api = cc.ApiClient()
	keypath = []
	body = None

	if func == 'get_bfd_peers':
		keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-state')
		response = api.get(keypath)
		vrfname = args[1]
		if (vrfname != "all"):
			apply_vrf_filter(response.content, vrfname)
		return response;
	elif func == 'get_openconfig_bfd_ext_bfd_sessions_single_hop':
		keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-state/single-hop-state={address},{interfacename},{vrfname},{localaddress}', address=args[1], interfacename=args[2], vrfname=args[3], localaddress=args[4])
		return api.get(keypath)
	elif func == 'get_openconfig_bfd_ext_bfd_sessions_multi_hop':
		keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-state/multi-hop-state={address},{interfacename},{vrfname},{localaddress}', address=args[1], interfacename=args[2], vrfname=args[3], localaddress=args[4])
                return api.get(keypath)
	else:
		return api.cli_not_implemented(func)


def run(func, args):
	if func == 'get_bfd_peers' or func == 'get_openconfig_bfd_ext_bfd_sessions_single_hop' or func == 'get_openconfig_bfd_ext_bfd_sessions_multi_hop':
		response = invoke_show_api(func, args)
		if response.ok():
			if response.content is not None:
				# Get Command Output
				api_response = response.content
				if api_response is None:
					print("Failed")
					return
				show_cli_output(args[0], api_response)
	else:
		response = invoke_api(func, args)

		if response.ok():
			if response.content is not None:
				print("Failed")
		else:
			print(response.error_message())

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])
