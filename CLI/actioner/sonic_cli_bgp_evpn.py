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


def invoke_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None
     
    #Patch cases
    if func == 'patch_bgp_evpn_advertise_all_vni':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn/openconfig-bgp-evpn-ext:config'
            +'/advertise-all-vni',
                vrf=args[0], af_name=args[1])
        body = { "openconfig-bgp-evpn-ext:advertise-all-vni": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_bgp_evpn_advertise_default_gw':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn/openconfig-bgp-evpn-ext:config'
            +'/advertise-default-gw',
                vrf=args[0], af_name=args[1])
        body = { "openconfig-bgp-evpn-ext:advertise-default-gw": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_bgp_evpn_advertise_svi_ip':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn/openconfig-bgp-evpn-ext:config'
            +'/advertise-svi-ip',
                vrf=args[0], af_name=args[1])
        body = { "openconfig-bgp-evpn-ext:advertise-svi-ip": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_bgp_evpn_default_originate':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
            +'/openconfig-bgp-evpn-ext:default-originate/config/{originate_family}',
                vrf=args[0], af_name=args[1], originate_family=args[2])
        body = { "openconfig-bgp-evpn-ext:{}".format(args[2]): True }
        return api.patch(keypath, body)
    elif func == 'patch_bgp_evpn_rd':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn/openconfig-bgp-evpn-ext:config'
            +'/route-distinguisher',
                vrf=args[0], af_name=args[1])
        body = { "openconfig-bgp-evpn-ext:route-distinguisher": args[2] }
        return api.patch(keypath, body)
    elif func == 'patch_bgp_evpn_rt':
        rttype = args[3]
        if rttype == 'both' or rttype == 'import':
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
                +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn/openconfig-bgp-evpn-ext:config'
                +'/import-rts',
                    vrf=args[0], af_name=args[1])
            body = { "openconfig-bgp-evpn-ext:import-rts": [ args[2] ] }
            response = api.patch(keypath, body)
            if not response.ok():
                return response
        if rttype == 'both' or rttype == 'export':
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
                +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn/openconfig-bgp-evpn-ext:config'
                +'/export-rts',
                    vrf=args[0], af_name=args[1], route_target_type=args[3])
            body = { "openconfig-bgp-evpn-ext:export-rts": [ args[2] ] }
            response = api.patch(keypath, body)
        return response
    elif func == 'patch_bgp_evpn_advertise':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn/openconfig-bgp-evpn-ext:config'
            +'/advertise-list',
                vrf=args[0], af_name=args[1])
        body = { "openconfig-bgp-evpn-ext:advertise-list": [ args[2] ] }
        return api.patch(keypath, body)
    elif func == 'patch_bgp_evpn_autort':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn/openconfig-bgp-evpn-ext:config'
            +'/autort',
                vrf=args[0], af_name=args[1])
        body = { "openconfig-bgp-evpn-ext:autort": args[2].upper().replace('-','_') }
        return api.patch(keypath, body)
    elif func == 'patch_bgp_evpn_flooding':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
            +'/openconfig-bgp-evpn-ext:flooding',
                vrf=args[0], af_name=args[1])
        body = { "openconfig-bgp-evpn-ext:flooding": args[2] }
        return api.patch(keypath, body)
    elif func == 'patch_bgp_evpn_dad_enable_params':
        if len(args) < 3:
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
                +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
                +'/openconfig-bgp-evpn-ext:dup-addr-detection/config/enabled',
                    vrf=args[0], af_name=args[1])
            body = { "openconfig-bgp-evpn-ext:enabled": True }
            return api.patch(keypath, body)
        else:
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
                +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
                +'/openconfig-bgp-evpn-ext:dup-addr-detection/config',
                    vrf=args[0], af_name=args[1])
            body = { 
                        "openconfig-bgp-evpn-ext:config": {
                            "enabled": True,
                            "max-moves": int(args[2]),
                            "time": int(args[3])
                        }
                    }
            return api.patch(keypath, body)
    elif func == 'patch_bgp_evpn_dad_freeze':
        if args[2] == 'permanent':
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
                +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
                +'/openconfig-bgp-evpn-ext:dup-addr-detection/config/freeze',
                    vrf=args[0], af_name=args[1])
            body = { "openconfig-bgp-evpn-ext:freeze": "permanent" }
            return api.patch(keypath, body)
        else:
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
                +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
                +'/openconfig-bgp-evpn-ext:dup-addr-detection/config/freeze',
                    vrf=args[0], af_name=args[1])
            body = { "openconfig-bgp-evpn-ext:freeze": args[3] }
            return api.patch(keypath, body)

    #Patch EVPN VNI cases
    elif func == 'patch_bgp_evpn_vni':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
            +'/openconfig-bgp-evpn-ext:vnis/vni',
                vrf=args[0], af_name=args[1])
        body = { "openconfig-bgp-evpn-ext:vni": [ 
                    { "vni-number": int(args[2]), 
                        "config" : 
                            { "vni-number" : int(args[2]) } 
                    } ] 
                }
        return api.patch(keypath, body)
    elif func == 'patch_bgp_evpn_vni_rt':
        rttype = args[4]
        if rttype == 'both' or rttype == 'import':
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
                +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
                +'/openconfig-bgp-evpn-ext:vnis/vni={vni_number}/config/import-rts',
                    vrf=args[0], af_name=args[1], vni_number=args[2])
            body = { "openconfig-bgp-evpn-ext:import-rts": [ args[3] ] }
            response = api.patch(keypath, body)
            if not response.ok():
                return response
        if rttype == 'both' or rttype == 'export':
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
                +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
                +'/openconfig-bgp-evpn-ext:vnis/vni={vni_number}/config/export-rts',
                    vrf=args[0], af_name=args[1], vni_number=args[2])
            body = { "openconfig-bgp-evpn-ext:export-rts": [ args[3] ] }
            response = api.patch(keypath, body)
        return response
    elif func == 'patch_bgp_evpn_vni_advertise_default_gw':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
            +'/openconfig-bgp-evpn-ext:vnis/vni={vni_number}/config/advertise-default-gw',
                vrf=args[0], af_name=args[1], vni_number=args[2])
        body = { "openconfig-bgp-evpn-ext:advertise-default-gw": True }
        return api.patch(keypath, body)
    elif func == 'patch_bgp_evpn_vni_advertise_svi_ip':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
            +'/openconfig-bgp-evpn-ext:vnis/vni={vni_number}/config/advertise-svi-ip',
                vrf=args[0], af_name=args[1], vni_number=args[2])
        body = { "openconfig-bgp-evpn-ext:advertise-svi-ip": True }
        return api.patch(keypath, body)
    elif func == 'patch_bgp_evpn_vni_rd':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
            +'/openconfig-bgp-evpn-ext:vnis/vni={vni_number}/config/route-distinguisher',
                vrf=args[0], af_name=args[1], vni_number=args[2])
        body = { "openconfig-bgp-evpn-ext:route-distinguisher": args[3] }
        return api.patch(keypath, body)

    #PIP cases
    elif func == 'patch_bgp_evpn_advertise_pip':
        # fetch parameter values
        arg_map = {}
        for i in range(len(args)):
            arg_val = (args[i].split(":", 1))[-1]
            arg_name = (args[i].split(":", 1))[0]

            if arg_val :
                arg_map[arg_name] = arg_val
         
        if 'enable' not in arg_map.keys() :
            print("PIP comamnd option enable not present")
            return None
         
        if  arg_map["enable"] != 'True' :
            print("PIP comamnd option enable not true")
            return None

        pip_cfg_data = {}
        pip_cfg_data.update({ 'openconfig-bgp-evpn-ext:advertise-pip': True })

        if 'ip' in arg_map.keys() :
            pip_cfg_data.update({ 'openconfig-bgp-evpn-ext:advertise-pip-ip': arg_map['ip'] })

        if 'peer' in arg_map.keys() :
            pip_cfg_data.update({ 'openconfig-bgp-evpn-ext:advertise-pip-peer-ip': arg_map['peer'] })

        if 'mac' in arg_map.keys() :
            pip_cfg_data.update({ 'openconfig-bgp-evpn-ext:advertise-pip-mac': arg_map['mac'] })

        keypath_str =  '/restconf/data/openconfig-network-instance:network-instances/network-instance={}'.format(arg_map['vrf'])
        keypath_str += '/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={}/l2vpn-evpn'.format(arg_map['af'])
        keypath_str += '/openconfig-bgp-evpn-ext:config/'

        keypath = cc.Path(keypath_str)
        body = { 'openconfig-bgp-evpn-ext:config' : pip_cfg_data }
        #print("PIP cmd keypath {}", keypath_str)
        #print("PIP cmd body {}", body)

        return api.patch(keypath, body)

    #Delete cases
    elif func == 'delete_bgp_evpn_advertise_all_vni':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
            +'/openconfig-bgp-evpn-ext:config/advertise-all-vni',
                vrf=args[0], af_name=args[1])
        return api.delete(keypath)
    elif func == 'delete_bgp_evpn_advertise_default_gw':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
            +'/openconfig-bgp-evpn-ext:config/advertise-default-gw',
                vrf=args[0], af_name=args[1])
        return api.delete(keypath)
    elif func == 'delete_bgp_evpn_advertise_svi_ip':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
            +'/openconfig-bgp-evpn-ext:config/advertise-svi-ip',
                vrf=args[0], af_name=args[1])
        return api.delete(keypath)
    elif func == 'delete_bgp_evpn_default_originate':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
            +'/openconfig-bgp-evpn-ext:default-originate/config/{originate_family}',
                vrf=args[0], af_name=args[1], originate_family=args[2])
        return api.delete(keypath)
    elif func == 'delete_bgp_evpn_rd':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
            +'/openconfig-bgp-evpn-ext:config/route-distinguisher',
                vrf=args[0], af_name=args[1])
        return api.delete(keypath)
    elif func == 'delete_bgp_evpn_rt':
        rttype = args[3]
        if rttype == "both" or rttype == "import":
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
                +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
                +'/openconfig-bgp-evpn-ext:config/import-rts={route_target}',
                    vrf=args[0], af_name=args[1], route_target=args[2])
            response = api.delete(keypath)
            if not response.ok():
                return response
        if rttype == "both" or rttype == "export":
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
                +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
                +'/openconfig-bgp-evpn-ext:config/export-rts={route_target}',
                    vrf=args[0], af_name=args[1], route_target=args[2])
            response = api.delete(keypath)
        return response
    elif func == 'delete_bgp_evpn_advertise':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
            +'/openconfig-bgp-evpn-ext:config/advertise-list={afi_safi_name}',
                vrf=args[0], af_name=args[1], afi_safi_name=args[2])
        return api.delete(keypath)
    elif func == 'delete_bgp_evpn_autort':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
            +'/openconfig-bgp-evpn-ext:config/autort',
                vrf=args[0], af_name=args[1])
        return api.delete(keypath)
    elif func == 'delete_bgp_evpn_flooding':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
            +'/openconfig-bgp-evpn-ext:flooding',
                vrf=args[0], af_name=args[1])
        return api.delete(keypath)
    elif func == 'delete_bgp_evpn_dad_enable_params':
        if len(args) < 3:
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
                +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
                +'/openconfig-bgp-evpn-ext:dup-addr-detection/config/enabled',
                    vrf=args[0], af_name=args[1])
            return api.delete(keypath)
        else:
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
                +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
                +'/openconfig-bgp-evpn-ext:dup-addr-detection/config/max-moves',
                    vrf=args[0], af_name=args[1])
            api.delete(keypath)
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
                +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
                +'/openconfig-bgp-evpn-ext:dup-addr-detection/config/time',
                    vrf=args[0], af_name=args[1])
            return api.delete(keypath)
    elif func == 'delete_bgp_evpn_dad_freeze':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
            +'/openconfig-bgp-evpn-ext:dup-addr-detection/config/freeze',
                vrf=args[0], af_name=args[1])
        return api.delete(keypath)

    #Delete EVPN VNI cases
    elif func == 'delete_bgp_evpn_vni':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
            +'/openconfig-bgp-evpn-ext:vnis/vni={vni_number}',
                vrf=args[0], af_name=args[1], vni_number=args[2])
        return api.delete(keypath)
    elif func == 'delete_bgp_evpn_vni_rt':
        rttype = args[4]
        if rttype == "both" or rttype == "import":
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
                +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
                +'/openconfig-bgp-evpn-ext:vnis/vni={vni_number}/config/import-rts={route_target}',
                    vrf=args[0], af_name=args[1], vni_number=args[2], route_target=args[3])
            response = api.delete(keypath)
            if not response.ok():
                return response
        if rttype == "both" or rttype == "export":
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
                +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
                +'/openconfig-bgp-evpn-ext:vnis/vni={vni_number}/config/export-rts={route_target}',
                    vrf=args[0], af_name=args[1], vni_number=args[2], route_target=args[3])
            response = api.delete(keypath)
        return response
    elif func == 'delete_bgp_evpn_vni_advertise_default_gw':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
            +'/openconfig-bgp-evpn-ext:vnis/vni={vni_number}/config/advertise-default-gw',
                vrf=args[0], af_name=args[1], vni_number=args[2])
        return api.delete(keypath)
    elif func == 'delete_bgp_evpn_vni_advertise_svi_ip':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
            +'/openconfig-bgp-evpn-ext:vnis/vni={vni_number}/config/advertise-svi-ip',
                vrf=args[0], af_name=args[1], vni_number=args[2])
        return api.delete(keypath)
    elif func == 'delete_bgp_evpn_vni_rd':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={vrf}'
            +'/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={af_name}/l2vpn-evpn'
            +'/openconfig-bgp-evpn-ext:vnis/vni={vni_number}/config/route-distinguisher',
                vrf=args[0], af_name=args[1], vni_number=args[2])
        return api.delete(keypath)

    #Delete PIP cases
    elif func == 'delete_bgp_evpn_advertise_pip':
        # fetch parameter values
        #print("PIP cmd input args {}", args)
        arg_map = {}
        for i in range(len(args)):
            arg_val = (args[i].split(":", 1))[-1]
            arg_name = (args[i].split(":", 1))[0]
            if arg_val:
                arg_map[arg_name] = arg_val
        #print("PIP cmd arg map {}", arg_map)

        if 'enable' not in arg_map.keys() :
            print("PIP comamnd option enable not present")
            return None

        if  arg_map["enable"] != 'False' :
            print("PIP comamnd option enable not false")
            return None

        keypath_str =  '/restconf/data/openconfig-network-instance:network-instances/network-instance={}'.format(arg_map['vrf'])
        keypath_str += '/protocols/protocol=BGP,bgp/bgp/global/afi-safis/afi-safi={}/l2vpn-evpn'.format(arg_map['af'])
        keypath_str += '/openconfig-bgp-evpn-ext:config/'
        #print("PIP cmd keypath {}", keypath_str)

        response = None
        unconfig_pip_all = True

        if 'ip' in arg_map.keys() :
            unconfig_pip_all = False
            keypath = cc.Path(keypath_str + 'advertise-pip-ip')
            response = api.delete(keypath)
            if response.ok() == False : return response
            #keypath = cc.Path(keypath_str + 'advertise-pip-mac')
            #response = api.delete(keypath)
            return response

        if 'peer' in arg_map.keys() :
            unconfig_pip_all = False
            keypath = cc.Path(keypath_str + 'advertise-pip-peer-ip')
            response = api.delete(keypath)
            if response.ok() == False : return response

        if 'mac' in arg_map.keys() :
            unconfig_pip_all = False
            keypath = cc.Path(keypath_str + 'advertise-pip-mac')
            response = api.delete(keypath)
            if response.ok() == False : return response

        if unconfig_pip_all :
            keypath = cc.Path(keypath_str + 'advertise-pip')
            response = api.delete(keypath)
            if response.ok() == False : return response

        return response

    else:
        body = {}

    return api.cli_not_implemented(func)

def run(func, args):
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

