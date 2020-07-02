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
        if 'openconfig-bfd:bfd' in response:
            if 'openconfig-bfd-ext:bfd-shop-sessions' in response['openconfig-bfd:bfd']:
                for i in range(len(response['openconfig-bfd:bfd']['openconfig-bfd-ext:bfd-shop-sessions']['single-hop'])):
                    shopsession = response['openconfig-bfd:bfd']['openconfig-bfd-ext:bfd-shop-sessions']['single-hop'][i]
                    if inputvrf == shopsession['vrf']:
                        new_list_shop.append(shopsession)
                response['openconfig-bfd:bfd']['openconfig-bfd-ext:bfd-shop-sessions']['single-hop'] = new_list_shop
        if 'openconfig-bfd:bfd' in response:
            if 'openconfig-bfd-ext:bfd-mhop-sessions' in response['openconfig-bfd:bfd']:
                for i in range(len(response['openconfig-bfd:bfd']['openconfig-bfd-ext:bfd-mhop-sessions']['multi-hop'])):
                    mhopsession = response['openconfig-bfd:bfd']['openconfig-bfd-ext:bfd-mhop-sessions']['multi-hop'][i]
                    if inputvrf == mhopsession['vrf']:
                        new_list_mhop.append(mhopsession)
                response['openconfig-bfd:bfd']['openconfig-bfd-ext:bfd-mhop-sessions']['multi-hop'] = new_list_mhop

def bfd_get_session_params (args=[]):

    peeraddr = ""
    intfname = ""
    vrf = ""
    localaddr = ""

    if (args[0] == "multihop"):
        if (args[1] == "peer_ipv4"):
            peeraddr  = args[2]
            intfname  = args[5]
            vrf       = args[6]
            localaddr = args[3]
        else:
            peeraddr  = args[2]
            intfname  = args[5]
            vrf       = args[6]
            localaddr = args[4]
    else:
        if (args[0] == "peer_ipv4"):
            peeraddr  = args[1]
            intfname  = args[4]
            vrf       = args[5]
            localaddr = args[2]
        else:
            peeraddr  = args[1]
            intfname  = args[4]
            vrf       = args[5]
            localaddr = args[3]

    return peeraddr, intfname, vrf, localaddr

def invoke_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None

    #Patch cases
    if func == 'patch_openconfig_bfd_ext_bfd_sessions':

        peeraddr, intfname, vrf, localaddr = bfd_get_session_params(args)

        if (args[0] == "multihop"):
            if localaddr == "null":
		return api._make_error_response('%Error: Local Address must be configured for multi-hop peer')

            keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-mhop-sessions/multi-hop={address},{interfacename},{vrfname},{localaddress}/config/enabled', address=peeraddr, interfacename=intfname, vrfname=vrf, localaddress=localaddr)
        else:
            if intfname == "null":
                return api._make_error_response('%Error: Interface must be configured for single-hop peer')

            keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-shop-sessions/single-hop={address},{interfacename},{vrfname},{localaddress}/config/enabled', address=peeraddr, interfacename=intfname, vrfname=vrf, localaddress=localaddr)

        body = {"openconfig-bfd-ext:enabled": True}
        return api.patch(keypath, body)

    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_enable':
        peeraddr, intfname, vrf, localaddr = bfd_get_session_params(args)

        if (args[0] == "multihop"):
            keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-mhop-sessions/multi-hop={address},{interfacename},{vrfname},{localaddress}/config/enabled', address=peeraddr, interfacename=intfname, vrfname=vrf,localaddress=localaddr)
        else:
            keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-shop-sessions/single-hop={address},{interfacename},{vrfname},{localaddress}/config/enabled', address=peeraddr, interfacename=intfname, vrfname=vrf,localaddress=localaddr)

        body = {"openconfig-bfd-ext:enabled": True}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_disable':
        peeraddr, intfname, vrf, localaddr = bfd_get_session_params(args)

        if (args[0] == "multihop"):
            keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-mhop-sessions/multi-hop={address},{interfacename},{vrfname},{localaddress}/config/enabled', address=peeraddr, interfacename=intfname, vrfname=vrf,localaddress=localaddr)
        else:
            keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-shop-sessions/single-hop={address},{interfacename},{vrfname},{localaddress}/config/enabled', address=peeraddr, interfacename=intfname, vrfname=vrf,localaddress=localaddr)

        body = {"openconfig-bfd-ext:enabled": False}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_desired_minimum_tx_interval':
        peeraddr, intfname, vrf, localaddr = bfd_get_session_params(args)

        if (args[0] == "multihop"):
            keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-mhop-sessions/multi-hop={address},{interfacename},{vrfname},{localaddress}/config/desired-minimum-tx-interval', address=peeraddr, interfacename=intfname, vrfname=vrf,localaddress=localaddr)
            body = {"openconfig-bfd-ext:desired-minimum-tx-interval": int(args[7])}
        else:
            keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-shop-sessions/single-hop={address},{interfacename},{vrfname},{localaddress}/config/desired-minimum-tx-interval', address=peeraddr, interfacename=intfname, vrfname=vrf,localaddress=localaddr)
            body = {"openconfig-bfd-ext:desired-minimum-tx-interval": int(args[6])}

        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_required_minimum_receive':
        peeraddr, intfname, vrf, localaddr = bfd_get_session_params(args)

        if (args[0] == "multihop"):
            keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-mhop-sessions/multi-hop={address},{interfacename},{vrfname},{localaddress}/config/required-minimum-receive', address=peeraddr, interfacename=intfname, vrfname=vrf,localaddress=localaddr)
            body = {"openconfig-bfd-ext:required-minimum-receive": int(args[7])}
        else:
            keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-shop-sessions/single-hop={address},{interfacename},{vrfname},{localaddress}/config/required-minimum-receive', address=peeraddr, interfacename=intfname, vrfname=vrf,localaddress=localaddr)
            body = {"openconfig-bfd-ext:required-minimum-receive": int(args[6])}

        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_detection_multiplier':
        peeraddr, intfname, vrf, localaddr = bfd_get_session_params(args)

        if (args[0] == "multihop"):
            keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-mhop-sessions/multi-hop={address},{interfacename},{vrfname},{localaddress}/config/detection-multiplier', address=peeraddr, interfacename=intfname, vrfname=vrf,localaddress=localaddr)
            body = {"openconfig-bfd-ext:detection-multiplier": int(args[7])}
        else:
            keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-shop-sessions/single-hop={address},{interfacename},{vrfname},{localaddress}/config/detection-multiplier', address=peeraddr, interfacename=intfname, vrfname=vrf,localaddress=localaddr)
            body = {"openconfig-bfd-ext:detection-multiplier": int(args[6])}

        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_desired_minimum_echo_receive':
        peeraddr, intfname, vrf, localaddr = bfd_get_session_params(args)

        if (args[0] == "multihop"):
	    return api._make_error_response('%Error: Echo-mode is not supported for multihop peer')
        else:
            keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-shop-sessions/single-hop={address},{interfacename},{vrfname},{localaddress}/config/desired-minimum-echo-receive', address=peeraddr, interfacename=intfname, vrfname=vrf,localaddress=localaddr)

            body = {"openconfig-bfd-ext:desired-minimum-echo-receive": int(args[6])}
            return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_echo_active':
        peeraddr, intfname, vrf, localaddr = bfd_get_session_params(args)

        if (args[0] == "multihop"):
            return api._make_error_response('%Error: Echo-mode is not supported for multihop peer')
        else:
            keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-shop-sessions/single-hop={address},{interfacename},{vrfname},{localaddress}/config/echo-active', address=peeraddr, interfacename=intfname, vrfname=vrf,localaddress=localaddr)
            body = {"openconfig-bfd-ext:echo-active": True}
            return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_ext_bfd_sessions_echo_active_disable':
        peeraddr, intfname, vrf, localaddr = bfd_get_session_params(args)

        if (args[0] == "multihop"):
            return api._make_error_response('%Error: Echo-mode is not supported for multihop peer')
        else:
            keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-shop-sessions/single-hop={address},{interfacename},{vrfname},{localaddress}/config/echo-active', address=peeraddr, interfacename=intfname, vrfname=vrf,localaddress=localaddr)
            body = {"openconfig-bfd-ext:echo-active": False}
            return api.patch(keypath, body)
    elif func == 'delete_openconfig_bfd_ext_bfd_sessions':
        peeraddr, intfname, vrf, localaddr = bfd_get_session_params(args)
        if (args[0] == "multihop"):
            if localaddr == "null":
            	return api._make_error_response('%Error: Local Address must be configured for multi-hop peer')
            
            keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-mhop-sessions/multi-hop={address},{interfacename},{vrfname},{localaddress}',address=peeraddr, interfacename=intfname, vrfname=vrf,localaddress=localaddr)
        else:
            if intfname == "null":
                return api._make_error_response('%Error: Interface must be configured for single-hop peer')

            keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-shop-sessions/single-hop={address},{interfacename},{vrfname},{localaddress}',address=peeraddr, interfacename=intfname, vrfname=vrf,localaddress=localaddr)

        return api.delete(keypath)

    return api.cli_not_implemented(func)


def invoke_show_api(func, args=[]):
	api = cc.ApiClient()
	keypath = []
	body = None

	if func == 'get_bfd_peers':
		keypath = cc.Path('/restconf/data/openconfig-bfd:bfd')
		response = api.get(keypath)

                if (len(args) == 3):
                	if (args[1] == "counters"):
                        	args[0] = "show_bfd_counters.j2"
			vrfname = args[2]
		else:
			args[0] = "show_bfd_peers.j2"
			vrfname = args[1]
		if (vrfname != "all"):
			apply_vrf_filter(response.content, vrfname)
		return response;
	elif func == 'get_openconfig_bfd_ext_bfd_sessions':
                peeraddr, intfname, vrf, localaddr = bfd_get_session_params(args[1:])

		if (args[1] == "multihop"):
                    if localaddr == "null":
                        return api._make_error_response('%Error: Local Address must be configured for multi-hop peer')

                    keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-mhop-sessions/multi-hop={address},{interfacename},{vrfname},{localaddress}', address=peeraddr, interfacename=intfname, vrfname=vrf, localaddress=localaddr)
		else:
                    if intfname == "null":
                        return api._make_error_response('%Error: Interface must be configured for single-hop peer')

                    keypath = cc.Path('/restconf/data/openconfig-bfd:bfd/openconfig-bfd-ext:bfd-shop-sessions/single-hop={address},{interfacename},{vrfname},{localaddress}', address=peeraddr, interfacename=intfname, vrfname=vrf, localaddress=localaddr)

                return api.get(keypath)
	else:
		return api.cli_not_implemented(func)


def run(func, args):
	if func == 'get_bfd_peers' or func == 'get_openconfig_bfd_ext_bfd_sessions':
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
                        print(response.error_message())
                        return 1

	else:
		response = invoke_api(func, args)

		if response.ok():
			if response.content is not None:
				print("Failed")
		else:
			print(response.error_message())
			return 1

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])
