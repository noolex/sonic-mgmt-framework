#!/usr/bin/python
###########################################################################
#
# Copyright 2019 Dell, Inc.
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

from collections import OrderedDict
import sys
import json
import netaddr
from rpipe_utils import pipestr
import cli_client as cc
from scripts.render_cli import show_cli_output
from bgp_openconfig_to_restconf_map import restconf_map
from datetime import datetime, timedelta

IDENTIFIER='BGP'
NAME1='bgp'

DELETE_OCPREFIX='delete_'
DELETE_OCPREFIX_LEN=len(DELETE_OCPREFIX)

GLOBAL_OCSTRG='openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp'
GLOBAL_OCSTRG_LEN=len(GLOBAL_OCSTRG)
DELETE_GLOBAL_OCPREFIX=DELETE_OCPREFIX+GLOBAL_OCSTRG
DELETE_GLOBAL_OCPREFIX_LEN=len(DELETE_GLOBAL_OCPREFIX)

NEIGHB_OCSTRG='openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor'
NEIGHB_OCSTRG_LEN=len(NEIGHB_OCSTRG)
DELETE_NEIGHB_OCPREFIX=DELETE_OCPREFIX+NEIGHB_OCSTRG
DELETE_NEIGHB_OCPREFIX_LEN=len(DELETE_NEIGHB_OCPREFIX)

PEERGP_OCSTRG='openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group'
PEERGP_OCSTRG_LEN=len(PEERGP_OCSTRG)
DELETE_PEERGP_OCPREFIX=DELETE_OCPREFIX+PEERGP_OCSTRG
DELETE_PEERGP_OCPREFIX_LEN=len(DELETE_PEERGP_OCPREFIX)

GLOBAF_OCSTRG='openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi'
GLOBAF_OCSTRG_LEN=len(GLOBAF_OCSTRG)
DELETE_GLOBAF_OCPREFIX=DELETE_OCPREFIX+GLOBAF_OCSTRG
DELETE_GLOBAF_OCPREFIX_LEN=len(DELETE_GLOBAF_OCPREFIX)

EXTGLOBAF_OCSTRG='openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi'
EXTGLOBAF_OCSTRG_LEN=len(EXTGLOBAF_OCSTRG)
DELETE_EXTGLOBAF_OCPREFIX=DELETE_OCPREFIX+EXTGLOBAF_OCSTRG
DELETE_EXTGLOBAF_OCPREFIX_LEN=len(DELETE_EXTGLOBAF_OCPREFIX)

NEIGAF_OCSTRG='openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi'
NEIGAF_OCSTRG_LEN=len(NEIGAF_OCSTRG)
DELETE_NEIGAF_OCPREFIX=DELETE_OCPREFIX+NEIGAF_OCSTRG
DELETE_NEIGAF_OCPREFIX_LEN=len(DELETE_NEIGAF_OCPREFIX)

EXTNGHAF_OCSTRG='openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi'
EXTNGHAF_OCSTRG_LEN=len(EXTNGHAF_OCSTRG)
DELETE_EXTNGHAF_OCPREFIX=DELETE_OCPREFIX+EXTNGHAF_OCSTRG
DELETE_EXTNGHAF_OCPREFIX_LEN=len(DELETE_EXTNGHAF_OCPREFIX)

EXTNGH_OCSTRG='openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor'
EXTNGH_OCSTRG_LEN=len(EXTNGH_OCSTRG)
DELETE_EXTNGH_OCPREFIX=DELETE_OCPREFIX+EXTNGH_OCSTRG
DELETE_EXTNGH_OCPREFIX_LEN=len(DELETE_EXTNGH_OCPREFIX)

PGAF_OCSTRG='openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi'
PGAF_OCSTRG_LEN=len(PGAF_OCSTRG)
DELETE_PGAF_OCPREFIX=DELETE_OCPREFIX+PGAF_OCSTRG
DELETE_PGAF_OCPREFIX_LEN=len(DELETE_PGAF_OCPREFIX)

EXTPGAF_OCSTRG='openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi'
EXTPGAF_OCSTRG_LEN=len(EXTPGAF_OCSTRG)
DELETE_EXTPGAF_OCPREFIX=DELETE_OCPREFIX+EXTPGAF_OCSTRG
DELETE_EXTPGAF_OCPREFIX_LEN=len(DELETE_EXTPGAF_OCPREFIX)

EXTPG_OCSTRG='openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group'
EXTPG_OCSTRG_LEN=len(EXTPG_OCSTRG)
DELETE_EXTPG_OCPREFIX=DELETE_OCPREFIX+EXTPG_OCSTRG
DELETE_EXTPG_OCPREFIX_LEN=len(DELETE_EXTPG_OCPREFIX)

EXTGLB_OCSTRG='openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global'
EXTGLB_OCSTRG_LEN=len(EXTGLB_OCSTRG)
DELETE_EXTGLB_OCPREFIX=DELETE_OCPREFIX+EXTGLB_OCSTRG
DELETE_EXTGLB_OCPREFIX_LEN=len(DELETE_EXTGLB_OCPREFIX)

OCEXTPREFIX_PATCH='PATCH'
OCEXTPREFIX_PATCH_LEN=len(OCEXTPREFIX_PATCH)
OCEXTPREFIX_DELETE='DELETE'
OCEXTPREFIX_DELETE_LEN=len(OCEXTPREFIX_DELETE)

def getPrefixAndLen(item):
    ip = netaddr.IPNetwork(item)
    return (ip.value, ip.prefixlen)

def getPrefix(item):
    ip = netaddr.IPNetwork(item['prefix'])
    return int(ip.ip)

def getNbr(item):
    ip = netaddr.IPNetwork(item['neighbor-address'])
    return int(ip.ip)

def getIntfId(item):

    ifName = item['neighbor-address']
    if ifName.startswith("Ethernet"):
        nums = ifName[len("Ethernet"):].split('.')
        ifId = int(nums[0]) * 2 ** 32
        if len(nums) > 1:
            ifId += int(nums[1])
    elif ifName.startswith("PortChannel"):
        nums = ifName[len("PortChannel"):].split('.')
        ifId = int(nums[0]) * 2 ** 32
        if len(nums) > 1:
            ifId += int(nums[1])
    elif ifName.startswith("Vlan"):
        ifId = int(ifName[len("Vlan"):])
    elif ifName.startswith("Loopback"):
        ifId = int(ifName[len("Loopback"):])
    else:
        return ifName
    return ifId


def generate_show_bgp_routes(args):
   api = cc.ApiClient()
   keypath = []
   body = None
   afisafi = "IPV4_UNICAST"
   rib_type = "ipv4-unicast"
   vrf = "default"
   neighbour_ip = ''
   route_option = 'loc-rib'
   querytype = None
   rfilter = None
   i = 0
   for arg in args:
        if "vrf" == arg:
           vrf = args[i+1]
        elif "ipv4" == arg:
           afisafi = "IPV4_UNICAST"
           rib_type = "ipv4-unicast"
        elif "ipv6" == arg:
           afisafi = "IPV6_UNICAST"
           rib_type = "ipv6-unicast"
        elif "neighbors" == arg:
           ni = i+2 if "interface" == args[i+1] else i+1
           neighbour_ip = args[ni]
           route_option = args[ni+1]
        elif "ip-addr" == arg:
           querytype = 'IP-ADDR'
        elif "community" == arg:
           querytype = 'COMMUNITY-STRING'
           aann = args[i+1]
        elif "local-as" == arg:
           querytype = 'COMMUNITY-LOCAL-AS'
        elif "no-advertise" == arg:
           querytype = 'COMMUNITY-NO-ADVERTISE'
        elif "no-export" == arg:
           querytype = 'COMMUNITY-NO-EXPORT'
        elif "no-peer" == arg:
           querytype = 'COMMUNITY-NO-PEER'
        elif "bestpath" == arg:
           rfilter = 'BEST_PATH'
        elif "multipath" == arg:
           rfilter = 'MULTI_PATH'
        elif "exact-match" == arg:
           rfilter = arg
        elif "route-map" == arg:
           querytype = 'ROUTE-MAP'
           rtmapname = args[i+1]
        else:
           if querytype == 'IP-ADDR':
               ipstr = arg
           else:
               pass
        i = i + 1
   d = {}
   method = "rpc"
   if route_option == "loc-rib":
      if method == 'rpc':
         keypath = cc.Path('/restconf/operations/sonic-bgp-show:show-bgp')
         inputs = {"vrf-name":vrf, "address-family":afisafi}
         if querytype:
             inputs['query-type'] = querytype
             if querytype == 'IP-ADDR':
                 inputs['ip-addr'] = ipstr
                 if rfilter:
                     inputs['path-type'] = rfilter
             elif querytype == 'COMMUNITY-STRING':
                 inputs['community-string'] = aann
                 if "exact-match" == rfilter:
                     inputs['community-str-exact-match'] = True
             elif querytype == 'COMMUNITY-LOCAL-AS':
                 if "exact-match" == rfilter:
                     inputs['community-local-as-exact-match'] = True
             elif querytype == 'COMMUNITY-NO-ADVERTISE':
                 if "exact-match" == rfilter:
                     inputs['community-no-advertise-exact-match'] = True
             elif querytype == 'COMMUNITY-NO-EXPORT':
                 if "exact-match" == rfilter:
                     inputs['community-no-export-exact-match'] = True
             elif querytype == 'COMMUNITY-NO-PEER':
                 if "exact-match" == rfilter:
                     inputs['community-no-peer-exact-match'] = True
             elif querytype == 'ROUTE-MAP':
                 inputs['route-map-name'] = rtmapname
         body = {"sonic-bgp-show:input": inputs}
         response = api.post(keypath, body)
         if not response:
             # unknown error (bad input?)
             return 1
         if(response.ok()):
            d = response.content['sonic-bgp-show:output']['response']
            if len(d) != 0 and "warning" not in d and "Unknown command:" not in d:
               try:
                  d = json.loads(d)
               except:
                  # unknown or missing output
                  return 1
               if querytype == 'IP-ADDR':
                  prf = d.get("prefix")
                  if not prf:
                     # no routes
                     return 0
                  show_cli_output("show_bgp_ipaddr_routes_rpc.j2", d)
               else:
                  routes = d.get("routes")
                  if not routes:
                      # no routes
                      return 0
                  keys = sorted(routes,key=getPrefixAndLen)
                  temp = OrderedDict()
                  for key in keys:
                      temp[key] = routes[key]

                  d["routes"] = temp

                  show_cli_output("show_ip_bgp_routes_rpc.j2", d)
         else:
            print response.error_message()
            return 1

      else:
         keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global', name=vrf, identifier=IDENTIFIER,name1=NAME1)
         response = api.get(keypath)
         if(response.ok() and response.content is not None):
            d.update(response.content)
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/rib/afi-safis/afi-safi={afi_safi_name}/{type_name}/loc-rib', name=vrf, identifier=IDENTIFIER, name1=NAME1, afi_safi_name=afisafi, type_name=rib_type)
            response1 = api.get(keypath)
            if(response1.ok() and response1.content is not None):
               if 'openconfig-network-instance:loc-rib' in response1.content:
                  route = response1.content['openconfig-network-instance:loc-rib']['routes']
                  tup = route['route']
                  route['route'] = sorted(tup, key=getPrefix)
                  response1.content['openconfig-network-instance:loc-rib']['routes'] = route
                  d.update(response1.content)
                  show_cli_output("show_ip_bgp_routes.j2", d)

   elif route_option == "routes":
      keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global', name=vrf, identifier=IDENTIFIER,name1=NAME1)
      response = api.get(keypath)
      if(response.ok() and response.content is not None):
         d.update(response.content)
         keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/rib/afi-safis/afi-safi={afi_safi_name}/{type_name}/neighbors/neighbor={nbr_address}/adj-rib-in-post', name=vrf, identifier=IDENTIFIER, name1=NAME1, afi_safi_name=afisafi, type_name=rib_type, nbr_address = neighbour_ip)
         response1 = api.get(keypath)
         if(response1.ok() and response1.content is not None):
            if 'openconfig-network-instance:adj-rib-in-post' in response1.content:
               route = response1.content['openconfig-network-instance:adj-rib-in-post']['routes']
               tup = route['route']
               route['route'] = sorted(tup, key=getPrefix)
               response1.content['openconfig-network-instance:adj-rib-in-post']['routes'] = route
               d.update(response1.content)
               show_cli_output("show_ip_bgp_routes.j2", d)
   elif route_option == "received-routes":
      keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global', name=vrf, identifier=IDENTIFIER,name1=NAME1)
      response = api.get(keypath)
      if(response.ok() and response.content is not None):
         d.update(response.content)
         keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/rib/afi-safis/afi-safi={afi_safi_name}/{type_name}/neighbors/neighbor={nbr_address}/adj-rib-in-pre', name=vrf, identifier=IDENTIFIER, name1=NAME1, afi_safi_name=afisafi, type_name=rib_type, nbr_address = neighbour_ip)
         response1 = api.get(keypath)
         if(response1.ok() and response1.content is not None):
            if 'openconfig-network-instance:adj-rib-in-pre' in response1.content:
               route = response1.content['openconfig-network-instance:adj-rib-in-pre']['routes']
               tup = route['route']
               route['route'] = sorted(tup, key=getPrefix)
               response1.content['openconfig-network-instance:adj-rib-in-pre']['routes'] = route
               d.update(response1.content)
               show_cli_output("show_ip_bgp_routes.j2", d)

   elif route_option == "advertised-routes":
      keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global', name=vrf, identifier=IDENTIFIER,name1=NAME1)
      response = api.get(keypath)
      if(response.ok() and response.content is not None):
         d.update(response.content)
         keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/rib/afi-safis/afi-safi={afi_safi_name}/{type_name}/neighbors/neighbor={nbr_address}/adj-rib-out-post', name=vrf, identifier=IDENTIFIER, name1=NAME1, afi_safi_name=afisafi, type_name=rib_type, nbr_address = neighbour_ip)
         response1 = api.get(keypath)
         if(response1.ok() and response1.content is not None):
            if 'openconfig-network-instance:adj-rib-out-post' in response1.content:
               route = response1.content['openconfig-network-instance:adj-rib-out-post']['routes']
               tup = route['route']
               route['route'] = sorted(tup, key=getPrefix)
               response1.content['openconfig-network-instance:adj-rib-out-post']['routes'] = route
               d.update(response1.content)
               show_cli_output("show_ip_bgp_routes.j2", d)
   else:
       pass

   return d

def generate_show_bgp_neighbors(args):
   api = cc.ApiClient()
   body = None
   afisafi = "IPV4_UNICAST"
   vrf = "default"
   querytype = None
   i = 0
   for arg in args:
        if "vrf" == arg:
           vrf = args[i+1]
        elif "ipv4" == arg:
           afisafi = "IPV4_UNICAST"
        elif "ipv6" == arg:
           afisafi = "IPV6_UNICAST"
        elif "l2vpn" == arg:
           afisafi = "L2VPN_EVPN"
        elif "summary" == arg:
           querytype = 'SUMMARY'
        i = i + 1
   d = {}
   # RPC to fetch the data
   keypath = cc.Path('/restconf/operations/sonic-bgp-show:show-bgp')
   inputs = {"vrf-name":vrf, "address-family":afisafi}
   if querytype:
      inputs['query-type'] = querytype

   body = {"sonic-bgp-show:input": inputs}
   response = api.post(keypath, body)
   if not response:
       # unknown error (bad input?)
       return 1
   if(response.ok()):
      d = response.content['sonic-bgp-show:output']['response']
      if len(d) != 0 and "warning" not in d and "Unknown command:" not in d:
         try:
            d = json.loads(d, object_pairs_hook=OrderedDict)
         except:
            # unknown or missing output
            return 1

         if querytype == "SUMMARY":
            if (not len(d)):
                print("% No BGP neighbors found")
                return 1
            d['max_nbr_col_len'] = len(max(d['peers'].keys(), key=len))
            d['addr_family'] = afisafi
            show_cli_output('show_ip_bgp_summary_rpc.j2', d)
            return 0
      else:
          d = json.loads(d)
          print(d['warning'])
   else:
      print response.error_message()
      return 1

def generate_show_bgp_vrf_all(args):
    api = cc.ApiClient()
    keypath = []
    body = None

    # Use SONIC model to get all configued VRF names
    keypath = cc.Path('/restconf/data/sonic-vrf:sonic-vrf/VRF/VRF_LIST')
    sonic_vrfs = api.get(keypath)
    if sonic_vrfs.ok() and sonic_vrfs.content is not None:
        args[5] = 'default'
        d = generate_show_bgp_routes(args)
        # then show bgp routes on remaining VRF
        if 'sonic-vrf:VRF_LIST' in sonic_vrfs.content:
            vrf_list = sonic_vrfs.content['sonic-vrf:VRF_LIST']
            for vrf in vrf_list:
               vrf_name = vrf['vrf_name']
               if vrf_name != 'default':
                   args[5] = vrf_name
                   d = generate_show_bgp_routes(args)

def generate_show_bgp_prefix_routes(args):
   api = cc.ApiClient()
   keypath = []
   body = None
   afisafi = "IPV4_UNICAST"
   rib_type = "ipv4-unicast"
   vrf = "default"
   rfilter = None
   i = 0
   for arg in args:
        if "vrf" == arg:
           vrf = args[i+1]
        elif "ipv4" == arg:
           afisafi = "IPV4_UNICAST"
           rib_type = "ipv4-unicast"
        elif "ipv6" == arg:
           afisafi = "IPV6_UNICAST"
           rib_type = "ipv6-unicast"
        elif "prefix" == arg:
           prefix_ip = args[i+1]
        elif "bestpath" == arg:
           rfilter = arg
        elif "multipath" == arg:
           rfilter = arg
        else:
           if i > 0 and args[0] == 'ip-prefix':
               prefix_ip = arg
           else:
               pass
        i = i + 1
   d = { 'vrf': vrf }
   keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/config', name=vrf, identifier=IDENTIFIER,name1=NAME1)
   response = api.get(keypath)
   if(response.ok() and response.content is not None):
       d.update(response.content)
       keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/rib/afi-safis/afi-safi={afi_safi_name}/{type_name}/openconfig-rib-bgp-ext:loc-rib-prefix/routes/route={prefix_name}', name=vrf, identifier=IDENTIFIER, name1=NAME1, afi_safi_name=afisafi, type_name=rib_type, prefix_name=prefix_ip)
       response1 = api.get(keypath)
       if(response1.ok() and response1.content is not None):
           if 'openconfig-rib-bgp-ext:route' in response1.content:
               if "bestpath" == rfilter:
                   rtList = response1.content['openconfig-rib-bgp-ext:route']
                   for rt in rtList:
                       prfpaths = rt.get('loc-rib-prefix-paths')
                       pathCnt = 0
                       if prfpaths:
                           paths = prfpaths.get('paths')
                           if paths:
                               pathList = paths.get('path')
                               pathCnt = len(pathList)
                               if pathList and pathCnt > 1:
                                   bestList = []
                                   for path in pathList:
                                       state = path.get('state')
                                       if state:
                                           if state.get('best-path') == True:
                                              bestList.append(path)
                                   if pathCnt > len(bestList):
                                       paths['path'] = bestList
                                       pathCnt = len(paths['path'])
                           if pathCnt == 0:
                               del rt['loc-rib-prefix-paths']

               d.update(response1.content)
               show_cli_output("show_ip_bgp_prefix_routes.j2", d)
   return d

def generate_show_bgp_peer_groups(args, show_all=False):
   api = cc.ApiClient()
   keypath = []
   body = None
   pg = None
   vrf = "default"
   i = 0
   for arg in args:
        if "vrf" == arg:
           vrf = args[i+1]
        elif "peer-group" == arg and show_all is False:
           pg = args[i+1]
        else:
           pass
        i = i + 1

   d = {}

   if pg is None:
      keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups', name=vrf, identifier=IDENTIFIER,name1=NAME1)
   else:
      keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={pgname}', name=vrf, identifier=IDENTIFIER,name1=NAME1,pgname=pg)
   response = api.get(keypath)
   if(response.ok() and response.content is not None):
       d.update(response.content)
       keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/dynamic-neighbor-prefixes', name=vrf, identifier=IDENTIFIER, name1=NAME1)
       response1 = api.get(keypath)
       if(response1.ok() and response1.content is not None):
          d.update(response1.content)
          show_cli_output("show_bgp_peer_group.j2", d)

   return d

def generate_show_bgp_stats(args):
   api = cc.ApiClient()
   keypath = []
   body = None
   afisafi = "IPV4_UNICAST"
   rib_type = "ipv4-unicast"
   vrf = "default"
   rfilter = None
   i = 0
   for arg in args:
       if "vrf" == arg:
          vrf = args[i+1]
       elif "ipv4" == arg:
          afisafi = "IPV4_UNICAST"
          rib_type = "ipv4-unicast"
       elif "ipv6" == arg:
          afisafi = "IPV6_UNICAST"
          rib_type = "ipv6-unicast"
       else:
          pass
       i = i + 1
   d = { 'vrf': vrf }
   keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/config', name=vrf, identifier=IDENTIFIER,name1=NAME1)
   response = api.get(keypath)
   if(response.ok() and response.content is not None):
       keypath = cc.Path('/restconf/operations/sonic-bgp-show:show-bgp-statistics')
       body = {"sonic-bgp-show:input": {"vrf-name":vrf, "address-family":afisafi}}
       response = api.post(keypath, body)
       if not response:
           # unknown error (bad input?)
           return 1
       if(response.ok()):
          d = response.content['sonic-bgp-show:output']['response']
          if len(d) != 0 and "warning" not in d:
             try:
                d = json.loads(d)
             except:
                # unknown or missing output
                return 1

             show_cli_output("show_bgp_stats_rpc.j2", d)


def invoke_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None

    op, attr = func.split('_', 1)

    if func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_config_as':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/config/as', 
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-network-instance:as": int(args[1]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_config_router_id':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/config/router-id',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-network-instance:router-id": args[1] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_graceful_restart_config_enabled':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/graceful-restart/config/enabled',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-network-instance:enabled": True if args[1] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_graceful_restart_config_restart_time':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/graceful-restart/config/restart-time',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-network-instance:restart-time": int(args[1]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_graceful_restart_config_stale_routes_time':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/graceful-restart/config/stale-routes-time',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-network-instance:stale-routes-time": args[1] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_use_multiple_paths_ebgp_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/use-multiple-paths/ebgp/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-network-instance:config" : { "allow-multiple-as" : True if args[1] == 'True' else False, "openconfig-bgp-ext:as-set" : True if 'as-set' in args[2:] else False } }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_route_selection_options_config_always_compare_med':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/route-selection-options/config/always-compare-med',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-network-instance:always-compare-med": True if args[1] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_route_selection_options_config_ignore_as_path_length':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/route-selection-options/config/ignore-as-path-length',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-network-instance:ignore-as-path-length": True if args[1] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_route_selection_options_config_external_compare_router_id':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/route-selection-options/config/external-compare-router-id',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-network-instance:external-compare-router-id": True if args[1] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_route_selection_options_config_compare_confed_as_path':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/route-selection-options/config/openconfig-bgp-ext:compare-confed-as-path',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:compare-confed-as-path": True if args[1] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_route_selection_options_config_med_missing_as_worst':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/route-selection-options/config/openconfig-bgp-ext:med-missing-as-worst',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:med-missing-as-worst": True if 'missing-as-worst' in args[1:] else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_route_selection_options_config_med_confed':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/route-selection-options/config/openconfig-bgp-ext:med-confed',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:med-confed": True if 'confed' in args[1:] else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_default_route_distance_config_external_route_distance':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/default-route-distance/config/external-route-distance',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-network-instance:external-route-distance": int(args[1]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_default_route_distance_config_internal_route_distance':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/default-route-distance/config/internal-route-distance',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-network-instance:internal-route-distance": int(args[1]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_bgp_ext_route_reflector_config_route_reflector_cluster_id':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/openconfig-bgp-ext:bgp-ext-route-reflector/config/route-reflector-cluster-id',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        cluster_id = args[1]
        if cluster_id.isdigit():
            cluster_id = int(cluster_id)
        body = { "openconfig-bgp-ext:route-reflector-cluster-id": cluster_id}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_logging_options_config_log_neighbor_state_changes':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/openconfig-bgp-ext:logging-options/config/log-neighbor-state-changes',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:log-neighbor-state-changes": True if args[1] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_config_disable_ebgp_connected_route_check':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/config/openconfig-bgp-ext:disable-ebgp-connected-route-check',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:disable-ebgp-connected-route-check": True if args[1] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_config_graceful_shutdown':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/config/openconfig-bgp-ext:graceful-shutdown',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = {"openconfig-bgp-ext:graceful-shutdown": True if args[1] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_config_fast_external_failover':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/config/openconfig-bgp-ext:fast-external-failover',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:fast-external-failover": True if args[1] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_config_network_import_check':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/config/openconfig-bgp-ext:network-import-check',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:network-import-check": True if args[1] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_bgp_ext_route_reflector_config_allow_outbound_policy':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/openconfig-bgp-ext:bgp-ext-route-reflector/config/allow-outbound-policy',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:allow-outbound-policy": True if args[1] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_graceful_restart_config_preserve_fw_state':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/graceful-restart/config/openconfig-bgp-ext:preserve-fw-state',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:preserve-fw-state" : True if args[1] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_config_coalesce_time':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/config/openconfig-bgp-ext:coalesce-time',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:coalesce-time" : int(args[1]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_config_read_quanta':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/config/openconfig-bgp-ext:read-quanta',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:read-quanta" : int(args[1]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_config_write_quanta':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/config/openconfig-bgp-ext:write-quanta',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:write-quanta" : int(args[1]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_config_clnt_to_clnt_reflection':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/config/openconfig-bgp-ext:clnt-to-clnt-reflection',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:clnt-to-clnt-reflection" : True if args[1] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_config_deterministic_med':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/config/openconfig-bgp-ext:deterministic-med',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:deterministic-med" : True if args[1] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_max_med_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/openconfig-bgp-ext:max-med/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        if args[1] == 'administrative':
            body = { "openconfig-bgp-ext:config" : { "administrative": True } }
            if len(args) > 2:
                body["openconfig-bgp-ext:config"]["admin-max-med-val"] = int(args[2])
        else:
            body = { "openconfig-bgp-ext:config" : { "time" : int(args[2]) } }
            if len(args) > 3:
                body["openconfig-bgp-ext:config"]["max-med-val"] = int(args[3])
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_global_defaults_config_ipv4_unicast':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/openconfig-bgp-ext:global-defaults/config/ipv4-unicast',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:ipv4-unicast" : True if args[1] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_global_defaults_config_local_preference':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/openconfig-bgp-ext:global-defaults/config/local-preference',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:local-preference" : int(args[1]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_global_defaults_config_show_hostname':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/openconfig-bgp-ext:global-defaults/config/show-hostname',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:show-hostname" : True if args[1] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_global_defaults_config_shutdown':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/openconfig-bgp-ext:global-defaults/config/shutdown',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:shutdown" : True if args[1] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_global_defaults_config_subgroup_pkt_queue_max':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/openconfig-bgp-ext:global-defaults/config/subgroup-pkt-queue-max',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:subgroup-pkt-queue-max" : int(args[1]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_config_route_map_process_delay':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/config/openconfig-bgp-ext:route-map-process-delay',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:route-map-process-delay" : int(args[1]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_update_delay_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/openconfig-bgp-ext:update-delay/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-bgp-ext:config" : { "max-delay": int(args[1]) } }
        if len(args) > 2:
            body["openconfig-bgp-ext:config"]["establish-wait"] = int(args[2])
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors', name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-network-instance:neighbors": { "neighbor": [{ "neighbor-address": args[1],
                                                                             "config" : { "neighbor-address": args[1]}}
                                                                            ]}}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups', name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-network-instance:peer-groups": { "peer-group": [{ "peer-group-name": args[1],
                                                                             "config" : { "peer-group-name": args[1]}}
                                                                            ]}}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis', name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1])
        body = { "openconfig-network-instance:afi-safis": {"afi-safi": [{ "afi-safi-name": args[1], "config": {"afi-safi-name":args[1]}}]}}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_network_config_network_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:network-config', name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1])
        body = { "openconfig-bgp-ext:network-config" : { "network": [{ "prefix": args[2], "config": { "prefix" : args[2] } }] }}
        if (args[1] == 'IPV4_UNICAST'):
           if (args[3] == 'backdoor'):
               body["openconfig-bgp-ext:network-config"]["network"][0]["config"]["backdoor"] = True
           if len(args) > 4:
               body["openconfig-bgp-ext:network-config"]["network"][0]["config"]["policy-name"] = args[4]
        elif (args[1] == 'IPV6_UNICAST'):
           if len(args) > 3:
               body["openconfig-bgp-ext:network-config"]["network"][0]["config"]["policy-name"] = args[3]
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_config_table_map_name':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/config/openconfig-bgp-ext:table-map-name',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1])
        body = { "openconfig-bgp-ext:table-map-name" : args[2] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_default_route_distance_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:default-route-distance/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1])
        body = { "oc-bgp-ext:config" : { "external-route-distance" : int(args[2]), "internal-route-distance" : int(args[3]), "local-route-distance" : int(args[4]) } }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_route_flap_damping_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:route-flap-damping/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1,  afi_safi_name=args[1])
        body = { "openconfig-bgp-ext:config" : { "enabled" : True if args[2] == 'True' else False } }
        if len(args) > 3:
            body["openconfig-bgp-ext:config"]["half-life"] = int(args[3])
            if len(args) > 4:
                body["openconfig-bgp-ext:config"]["reuse-threshold"] = int(args[4])
                if len(args) > 5:
                    body["openconfig-bgp-ext:config"]["suppress-threshold"] = int(args[5])
                    if len(args) > 6:
                        body["openconfig-bgp-ext:config"]["max-suppress"] = int(args[6])
        return api.patch(keypath, body)

    elif func == 'patch_openconfig_network_instance1348121867' or func == 'delete_openconfig_network_instance1348121867':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/use-multiple-paths/ebgp/config/maximum-paths',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1])
        if func[0:DELETE_OCPREFIX_LEN] == DELETE_OCPREFIX:
            return api.delete(keypath)
        body = { "openconfig-network-instance:maximum-paths": int(args[2]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance1543452951' or func == 'delete_openconfig_network_instance1543452951':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/use-multiple-paths/ibgp/config/maximum-paths',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1])
        if func[0:DELETE_OCPREFIX_LEN] == DELETE_OCPREFIX:
            return api.delete(keypath)
        body = { "openconfig-network-instance:maximum-paths": int(args[2]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext3691744053' or func == 'delete_openconfig_bgp_ext3691744053':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/use-multiple-paths/ibgp/config/openconfig-bgp-ext:equal-cluster-length',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1])
        if func[0:DELETE_OCPREFIX_LEN] == DELETE_OCPREFIX:
            return api.delete(keypath)
        body = { "openconfig-bgp-ext:equal-cluster-length": True if 'equal-cluster-length' in args[2:] else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance1717438887':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/dynamic-neighbor-prefixes', name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-network-instance:dynamic-neighbor-prefixes": { "dynamic-neighbor-prefix": [{ "prefix": args[1],
                                                                             "config": {"prefix": args[1], "peer-group": args[2]}}]} }
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_network_instance1717438887':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/dynamic-neighbor-prefixes/dynamic-neighbor-prefix={prefix}/config/peer-group', name=args[0], identifier=IDENTIFIER, name1=NAME1, prefix=args[1])
        if len(args) == 2:
            # if peer group is not given, delete the whole prefix, if given, just remove peer-group from prefix
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/dynamic-neighbor-prefixes/dynamic-neighbor-prefix={prefix}', name=args[0], identifier=IDENTIFIER, name1=NAME1, prefix=args[1])
        if func[0:DELETE_OCPREFIX_LEN] == DELETE_OCPREFIX:
            return api.delete(keypath)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_config_max_dynamic_neighbors':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/config/openconfig-bgp-ext:max-dynamic-neighbors',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-network-instance:max-dynamic-neighbors": int(args[1]) }
        return api.patch(keypath, body) 
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_confederation_config_identifier':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/confederation/config/identifier',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-network-instance:identifier": int(args[1]) }
        return api.patch(keypath, body)    
    elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_confederation_config_member_as':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/confederation/config/member-as',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        if op == 'patch':
            body = { "openconfig-network-instance:member-as": [ int(args[1]) ] }
            return api.patch(keypath, body)
        else:
            return api.delete(keypath)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_config_keepalive_interval':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/config/openconfig-bgp-ext:keepalive-interval',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-network-instance:keepalive-interval": args[1] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_config_hold_time':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/config/openconfig-bgp-ext:hold-time',
                name=args[0], identifier=IDENTIFIER, name1=NAME1)
        body = { "openconfig-network-instance:hold-time": args[1] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_enabled':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/enabled',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-network-instance:enabled": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_shutdown_message':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/openconfig-bgp-ext:shutdown-message',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-bgp-ext:shutdown-message": args[2] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_description':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/description',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-network-instance:description": args[2] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_ebgp_multihop_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/ebgp-multihop/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-network-instance:config" : { "enabled" : True if args[2] == 'True' else False, "multihop-ttl" : int(args[3]) } }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_peer_group':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/peer-group',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-network-instance:peer-group": args[2] }
        return api.patch(keypath, body)


    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_peer_as':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/peer-type',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        api.delete(keypath)
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/peer-as',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-network-instance:peer-as": int(args[2]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_peer_type':

        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/peer-as',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        api.delete(keypath)
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/peer-type',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-network-instance:peer-type": args[2].upper() }
        return api.patch(keypath, body)


    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_timers_config_connect_retry':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/timers/config/connect-retry',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-network-instance:connect-retry": args[2] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_timers_config_keepalive_interval':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/timers/config/keepalive-interval',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-network-instance:keepalive-interval": args[2] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_timers_config_hold_time':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/timers/config/hold-time',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-network-instance:hold-time": args[2] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_timers_config_connect_retry':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/timers/config/connect-retry',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-network-instance:connect-retry": args[2] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_transport_config_local_address':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/transport/config/local-address',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-network-instance:local-address": args[2] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_timers_config_minimum_advertisement_interval':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/timers/config/minimum-advertisement-interval',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-network-instance:minimum-advertisement-interval": args[2] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_capability_extended_nexthop':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/openconfig-bgp-ext:capability-extended-nexthop',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-bgp-ext:capability-extended-nexthop": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_capability_dynamic':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/openconfig-bgp-ext:capability-dynamic',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-bgp-ext:capability-dynamic": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_disable_ebgp_connected_route_check':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/openconfig-bgp-ext:disable-ebgp-connected-route-check',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-bgp-ext:disable-ebgp-connected-route-check": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_enforce_first_as':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/openconfig-bgp-ext:enforce-first-as',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-bgp-ext:enforce-first-as": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_local_as':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/local-as',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-network-instance:local-as": int(args[2]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_local_as_no_prepend':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/openconfig-bgp-ext:local-as-no-prepend',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-bgp-ext:local-as-no-prepend": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_local_as_replace_as':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/openconfig-bgp-ext:local-as-replace-as',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-bgp-ext:local-as-replace-as": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_transport_config_passive_mode':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/transport/config/passive-mode',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-network-instance:passive-mode": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_auth_password':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/openconfig-bgp-ext:auth-password/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "oc-bgp-ext:config": { "oc-bgp-ext:password": args[2],  "oc-bgp-ext:encrypted": True if "encrypted" in args[2:] else False }}
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_auth_password':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/openconfig-bgp-ext:auth-password',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        return api.delete(keypath)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_solo_peer':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/openconfig-bgp-ext:solo-peer',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-bgp-ext:solo-peer": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_ttl_security_hops':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/openconfig-bgp-ext:ttl-security-hops',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-bgp-ext:ttl-security-hops": int(args[2]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_enable_bfd_config_enabled':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/openconfig-bfd:enable-bfd/config/enabled',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-bfd:enabled" : True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_enable_bfd_config_bfd_check_control_plane_failure':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/openconfig-bfd:enable-bfd/config/openconfig-bgp-ext:bfd-check-control-plane-failure',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-bgp-ext:bfd-check-control-plane-failure" : True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_bfd_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_enable_bfd_config_enabled':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/openconfig-bfd:enable-bfd/config/enabled',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        return api.delete(keypath)
    elif func == 'delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_enable_bfd_config_bfd_check_control_plane_failure':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/openconfig-bfd:enable-bfd/config/openconfig-bgp-ext:bfd-check-control-plane-failure',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        return api.delete(keypath)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_dont_negotiate_capability':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/openconfig-bgp-ext:dont-negotiate-capability',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-bgp-ext:dont-negotiate-capability" : True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_enforce_multihop':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/openconfig-bgp-ext:enforce-multihop',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-bgp-ext:enforce-multihop" : True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_override_capability':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/openconfig-bgp-ext:override-capability',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-bgp-ext:override-capability" : True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_peer_port':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/openconfig-bgp-ext:peer-port',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-bgp-ext:peer-port" : int(args[2]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_strict_capability_match':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/config/openconfig-bgp-ext:strict-capability-match',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-bgp-ext:strict-capability-match" : True if args[2] == 'True' else False }
        return api.patch(keypath, body)

    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis', name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        body = { "openconfig-network-instance:afi-safis": {"afi-safi": [{ "afi-safi-name": args[2], "config": {"afi-safi-name": args[2] }}]}}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_config_enabled':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/config/enabled',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-network-instance:enabled": True if args[3] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_add_paths_config_tx_add_paths':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/add-paths/config/openconfig-bgp-ext:tx-add-paths',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:tx-add-paths" : args[3] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_config_as_override':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/config/openconfig-bgp-ext:as-override',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:as-override": True if args[3] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_attribute_unchanged_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:attribute-unchanged/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:config" : { "as-path" : True if 'as-path' in args[3:] else False, "med" : True if 'med' in args[3:] else False, "next-hop" : True if 'next-hop' in args[3:] else False } }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_filter_list_config_import_policy':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:filter-list/config/import-policy',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:import-policy" : args[3] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_filter_list_config_export_policy':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:filter-list/config/export-policy',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:export-policy" : args[3] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_next_hop_self_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:next-hop-self/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:config" : { "enabled" : True if args[3] == 'True' else False } }
        if 'force' in args[3:]: body["openconfig-bgp-ext:config"]["force"] = True
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_prefix_list_config_import_policy':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:prefix-list/config/import-policy',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:import-policy" : args[3] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_prefix_list_config_export_policy':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:prefix-list/config/export-policy',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:export-policy" : args[3] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_remove_private_as_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:remove-private-as/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:config" : { "enabled" : True if args[3] == 'True' else False } }
        if 'all' in args[3:]:
            body["openconfig-bgp-ext:config"]["all"] = True
        if 'replace-as' in args[3:]:
            body["openconfig-bgp-ext:config"]["replace-as"] = True
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_config_route_reflector_client':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/config/openconfig-bgp-ext:route-reflector-client',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:route-reflector-client" : True if args[3] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_config_send_community':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/config/openconfig-bgp-ext:send-community',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:send-community" : args[3].upper() }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_config_soft_reconfiguration_in':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/config/openconfig-bgp-ext:soft-reconfiguration-in',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:soft-reconfiguration-in" : True if args[3] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_config_unsuppress_map_name':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/config/openconfig-bgp-ext:unsuppress-map-name',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:unsuppress-map-name" : args[3] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_config_weight':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/config/openconfig-bgp-ext:weight',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:weight" : int(args[3]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_capability_orf_config_orf_type':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:capability-orf/config/orf-type',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:orf-type" : args[3].upper() }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_config_route_server_client':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/config/openconfig-bgp-ext:route-server-client',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:route-server-client" : True if args[3] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_as_count':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:allow-own-as/config/as-count',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-network-instance:as-count": int(args[3]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_enabled':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:allow-own-as/config/enabled',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-network-instance:enabled": True if args[3] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_origin':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:allow-own-as/config/origin',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:origin": True if "True" == args[3] else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_shutdown_message':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/openconfig-bgp-ext:shutdown-message',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-bgp-ext:shutdown-message": args[2] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_description':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/description',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-network-instance:description": args[2] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_ebgp_multihop_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/ebgp-multihop/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-network-instance:config" : { "enabled" : True if args[2] == 'True' else False, "multihop-ttl" : int(args[3]) } }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_peer_as':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/peer-as',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-network-instance:peer-as": int(args[2]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_peer_type':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/peer-type',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-network-instance:peer-type": args[2].upper() }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_timers_config_connect_retry':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/timers/config/connect-retry',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-network-instance:connect-retry": args[2] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_timers_config_keepalive_interval':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/timers/config/keepalive-interval',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-network-instance:keepalive-interval": args[2] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_timers_config_hold_time':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/timers/config/hold-time',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-network-instance:hold-time": args[2] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_timers_config_connect_retry':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/timers/config/connect-retry',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-network-instance:connect-retry": args[2] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_transport_config_local_address':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/transport/config/local-address',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-network-instance:local-address": args[2] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_capability_extended_nexthop':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/openconfig-bgp-ext:capability-extended-nexthop',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-bgp-ext:capability-extended-nexthop": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_capability_dynamic':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/openconfig-bgp-ext:capability-dynamic',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-bgp-ext:capability-dynamic": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_disable_ebgp_connected_route_check':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/openconfig-bgp-ext:disable-ebgp-connected-route-check',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-bgp-ext:disable-ebgp-connected-route-check": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_enforce_first_as':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/openconfig-bgp-ext:enforce-first-as',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-bgp-ext:enforce-first-as": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_local_as':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/local-as',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-network-instance:local-as": int(args[2]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_local_as_no_prepend':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/openconfig-bgp-ext:local-as-no-prepend',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-bgp-ext:local-as-no-prepend": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_local_as_replace_as':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/openconfig-bgp-ext:local-as-replace-as',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-bgp-ext:local-as-replace-as": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_transport_config_passive_mode':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/transport/config/passive-mode',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-network-instance:passive-mode": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_auth_password':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/openconfig-bgp-ext:auth-password/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "oc-bgp-ext:config": { "oc-bgp-ext:password": args[2],  "oc-bgp-ext:encrypted": True if "encrypted" in args[2:] else False }}
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_auth_password':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/openconfig-bgp-ext:auth-password/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        return api.delete(keypath)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_solo_peer':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/openconfig-bgp-ext:solo-peer',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-bgp-ext:solo-peer": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_ttl_security_hops':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/openconfig-bgp-ext:ttl-security-hops',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-bgp-ext:ttl-security-hops": int(args[2]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bfd_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_enable_bfd_config_enabled':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/openconfig-bfd:enable-bfd/config/enabled',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-bfd:enabled" : True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_enable_bfd_config_bfd_check_control_plane_failure':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/openconfig-bfd:enable-bfd/config/openconfig-bgp-ext:bfd-check-control-plane-failure',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-bgp-ext:bfd-check-control-plane-failure" : True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'delete_openconfig_bfd_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_enable_bfd_config_enabled':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/openconfig-bfd:enable-bfd/config/enabled',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        return api.delete(keypath, body)
    elif func == 'delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_enable_bfd_config_bfd_check_control_plane_failure':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/openconfig-bfd:enable-bfd/config/openconfig-bgp-ext:bfd-check-control-plane-failure',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        return api.delete(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_dont_negotiate_capability':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/openconfig-bgp-ext:dont-negotiate-capability',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-bgp-ext:dont-negotiate-capability" : True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_enforce_multihop':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/openconfig-bgp-ext:enforce-multihop',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-bgp-ext:enforce-multihop" : True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_override_capability':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/openconfig-bgp-ext:override-capability',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-bgp-ext:override-capability" : True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_peer_port':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/openconfig-bgp-ext:peer-port',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-bgp-ext:peer-port" : int(args[2]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_strict_capability_match':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/openconfig-bgp-ext:strict-capability-match',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-bgp-ext:strict-capability-match" : True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis', name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-network-instance:afi-safis": {"afi-safi": [{ "afi-safi-name": args[2], "config": {"afi-safi-name": args[2] }}]}}
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_config_enabled':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/config/enabled',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
        body = { "openconfig-network-instance:enabled": True if args[3] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_add_paths_config_tx_add_paths':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/add-paths/config/openconfig-bgp-ext:tx-add-paths',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:tx-add-paths" : args[3] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_config_as_override':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/config/openconfig-bgp-ext:as-override',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:as-override": True if args[3] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_attribute_unchanged_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:attribute-unchanged/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:config" : { "as-path" : True if 'as-path' in args[3:] else False, "med" : True if 'med' in args[3:] else False, "next-hop" : True if 'next-hop' in args[3:] else False } }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_next_hop_self_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:next-hop-self/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:config" : { "enabled" : True if args[3] == 'True' else False } }
        if 'force' in args[3:]: body["openconfig-bgp-ext:config"]["force"] = True
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_remove_private_as_config':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:remove-private-as/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:config" : { "enabled" : True if args[3] == 'True' else False } }
        if 'all' in args[3:]:
            body["openconfig-bgp-ext:config"]["all"] = True
        if 'replace-as' in args[3:]:
            body["openconfig-bgp-ext:config"]["replace-as"] = True
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_config_route_reflector_client':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/config/openconfig-bgp-ext:route-reflector-client',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:route-reflector-client" : True if args[3] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_config_send_community':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/config/openconfig-bgp-ext:send-community',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:send-community" : args[3].upper() }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_config_soft_reconfiguration_in':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/config/openconfig-bgp-ext:soft-reconfiguration-in',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:soft-reconfiguration-in" : True if args[3] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_config_unsuppress_map_name':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/config/openconfig-bgp-ext:unsuppress-map-name',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:unsuppress-map-name" : args[3] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_config_weight':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/config/openconfig-bgp-ext:weight',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:weight" : int(args[3]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_as_count':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:allow-own-as/config/as-count',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
        body = { "openconfig-network-instance:as-count" : int(args[3]) }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_enabled':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:allow-own-as/config/enabled',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
        body = { "openconfig-network-instance:enabled": True if args[3] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_capability_orf_config_orf_type':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:capability-orf/config/orf-type',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:orf-type" : args[3].upper() }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_config_route_server_client':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/config/openconfig-bgp-ext:route-server-client',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:route-server-client" : True if args[3] == 'True' else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_origin':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:allow-own-as/config/origin',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
        body = { "openconfig-bgp-ext:origin": True if 'True' == args[3] else False }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_shutdown_message':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/openconfig-bgp-ext:shutdown-message',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-bgp-ext:shutdown-message": args[2] }
        return api.patch(keypath, body)
    elif func == 'patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_enabled':
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/config/openconfig-bgp-ext:enabled',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        body = { "openconfig-bgp-ext:enabled": True if args[2] == 'True' else False }
        return api.patch(keypath, body)
    elif attr == 'openconfig_network_instance_network_instances_network_instance_table_connections_table_connection_config_import_policy':
        src_proto = "STATIC" if 'static' == args[2] else "DIRECTLY_CONNECTED" if 'connected' == args[2] else 'OSPF' if 'ospf' == args[2] else 'OSPF3'
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/table-connections/table-connection={src_protocol},{dst_protocol},{address_family}/config/import-policy',
                name=args[0], src_protocol= src_proto, dst_protocol=IDENTIFIER, address_family=args[1].split('_',1)[0])
        if op == 'patch':
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/table-connections', name=args[0])
            body = {"openconfig-network-instance:table-connections": {"table-connection": [{"src-protocol":src_proto, "dst-protocol":IDENTIFIER,
                                                                       "address-family": args[1].split('_',1)[0],
                                                                       "config":{"src-protocol":src_proto, "dst-protocol":IDENTIFIER,
                                                                       "address-family": args[1].split('_',1)[0],"import-policy":[args[3]] }} ] }}
            return api.patch(keypath, body)
        else:
            return api.delete(keypath)
    elif attr == 'openconfig_network_instance_ext_network_instances_network_instance_table_connections_table_connection_config_metric':
        src_proto = "STATIC" if 'static' == args[2] else "DIRECTLY_CONNECTED" if 'connected' == args[2] else 'OSPF' if 'ospf' == args[2] else 'OSPF3'
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/table-connections/table-connection={src_protocol},{dst_protocol},{address_family}/config/openconfig-network-instance-ext:metric',
                name=args[0], src_protocol=src_proto, dst_protocol=IDENTIFIER, address_family=args[1].split('_',1)[0])
        if op == 'patch':
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/table-connections', name=args[0])
            body = {"openconfig-network-instance:table-connections": {"table-connection": [{"src-protocol":src_proto, "dst-protocol":IDENTIFIER,
                                                                       "address-family": args[1].split('_',1)[0],
                                                                       "config":{"src-protocol":src_proto, "dst-protocol":IDENTIFIER,
                                                                       "address-family": args[1].split('_',1)[0],
                                                                       "openconfig-network-instance-ext:metric":int(args[3]) }} ] }}
            return api.patch(keypath, body)
        else:
            return api.delete(keypath)
    elif attr == 'openconfig_network_instance_network_instances_network_instance_table_connections_table_connection_config':
        src_proto = "STATIC" if 'static' == args[2] else "DIRECTLY_CONNECTED" if 'connected' == args[2] else 'OSPF' if 'ospf' == args[2] else 'OSPF3'
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/table-connections/table-connection={src_protocol},{dst_protocol},{address_family}/config',
                name=args[0], src_protocol= src_proto, dst_protocol=IDENTIFIER, address_family=args[1].split('_',1)[0])
        if op == 'patch':
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/table-connections', name=args[0])
            body = {"openconfig-network-instance:table-connections": {"table-connection": [{"src-protocol":src_proto, "dst-protocol":IDENTIFIER,
                                                                       "address-family": args[1].split('_',1)[0],
                                                                       "config":{"src-protocol":src_proto, "dst-protocol":IDENTIFIER,
                                                                       "address-family": args[1].split('_',1)[0] }} ] }}
            return api.patch(keypath, body)
        else:
            return api.delete(keypath)
    elif attr == 'openconfig_network_instance_network_instances_network_instance_table_connections_table_connection':
        src_proto = "STATIC" if 'static' == args[2] else "DIRECTLY_CONNECTED" if 'connected' == args[2] else 'OSPF' if 'ospf' == args[2] else 'OSPF3'
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/table-connections/table-connection={src_protocol},{dst_protocol},{address_family}',
                name=args[0], src_protocol= src_proto, dst_protocol=IDENTIFIER, address_family=args[1].split('_',1)[0])
        if op == 'patch':
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/table-connections', name=args[0])
            body = {"openconfig-network-instance:table-connections": {"table-connection": [{"src-protocol":src_proto, "dst-protocol":IDENTIFIER,
                                                                       "address-family": args[1].split('_',1)[0],
                                                                       "config":{"src-protocol":src_proto, "dst-protocol":IDENTIFIER,
                                                                       "address-family": args[1].split('_',1)[0] }} ] }}
            return api.patch(keypath, body)
        else:
            return api.delete(keypath)
    elif attr == 'openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_import_vrf':
        if args[2] == 'import-vrf-name':
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:import-network-instance/config/name',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:name": args[3] }
        elif args[2] == 'route-map':
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:import-network-instance/config/policy-name',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:policy-name": args[3] }
        
        if op == OCEXTPREFIX_PATCH:
            return api.patch(keypath, body)
        else:
            return api.delete(keypath)
    elif op == OCEXTPREFIX_DELETE or op == OCEXTPREFIX_PATCH:
        # PATCH_ and DELETE_ prefixes (all caps) means no swaggar-api string
        if attr == 'openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_aggregate_address_config_aggregate_address_config':
            # openconfig_bgp_ext1500978046
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:aggregate-address-config/aggregate-address={prefix}/config',
                    name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1], prefix=args[2])
            if op == OCEXTPREFIX_PATCH:
                keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:aggregate-address-config', name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1])
                body = { "openconfig-bgp-ext:aggregate-address-config": { "aggregate-address": [{ "prefix": args[2], "config": { "prefix" : args[2] }}] } }
                if 'as-set' in args[3:]:
                    body["openconfig-bgp-ext:aggregate-address-config"]["aggregate-address"][0]["config"]["as-set"] = True
                if 'summary-only' in args[3:]:
                    body["openconfig-bgp-ext:aggregate-address-config"]["aggregate-address"][0]["config"]["summary-only"] = True
        elif attr == 'openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_aggregate_address_config_aggregate_address_config_as_set':
            # openconfig_bgp_ext2155307832
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:aggregate-address-config/aggregate-address={prefix}/config/as-set',
                    name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1], prefix=args[2])
            if op == OCEXTPREFIX_PATCH:
                keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:aggregate-address-config', name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1])
                body = { "openconfig-bgp-ext:aggregate-address-config": { "aggregate-address": [{ "prefix": args[2], "config": { "prefix" : args[2], "as-set": True if 'True' == args[3] else False }}] } }
        elif attr == 'openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_aggregate_address_config_aggregate_address_config_summary_only':
            # patch_openconfig_bgp_ext1133616225
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:aggregate-address-config/aggregate-address={prefix}/config/summary-only',
                    name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1], prefix=args[2])
            if op == OCEXTPREFIX_PATCH:
                keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:aggregate-address-config', name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1])
                body = { "openconfig-bgp-ext:aggregate-address-config": { "aggregate-address": [{ "prefix": args[2], "config": { "prefix" : args[2], "summary-only": True if 'True' == args[3] else False }}] } }
        elif attr == 'openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_aggregate_address_config_aggregate_address_config_policy_name':
            # patch_openconfig_bgp_ext2461397931
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:aggregate-address-config/aggregate-address={prefix}/config/policy-name',
                    name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1], prefix=args[2])
            if op == OCEXTPREFIX_PATCH:
                keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:aggregate-address-config', name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1])
                body = { "openconfig-bgp-ext:aggregate-address-config": { "aggregate-address": [{ "prefix": args[2], "config": { "prefix" : args[2], "policy-name": args[3] }}] } }

        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_import_policy':
            # openconfig_network_instance3764031561
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/apply-policy/config/import-policy',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:import-policy": [ args[3] ] }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_export_policy':
            # openconfig_network_instance1837635724
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/apply-policy/config/export-policy',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:export-policy": [ args[3] ] }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/ipv4-unicast/prefix-limit/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:config" : { "max-prefixes" : int(args[3]) } }
                if args[4] != '0': body["openconfig-network-instance:config"]["warning-threshold-pct"] = int(args[4])
                if 'warning-only' in args[4:]: body["openconfig-network-instance:config"]["prevent-teardown"] = True
                if 'restart' in args[4:]: body["openconfig-network-instance:config"]["restart-timer"] = args[-1]
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_max_prefixes':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/ipv4-unicast/prefix-limit/config/max-prefixes',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:max-prefixes" : int(args[3]) }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_warning_threshold_pct':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/ipv4-unicast/prefix-limit/config/warning-threshold-pct',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:warning-threshold-pct" : int(args[3]) }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_prevent_teardown':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/ipv4-unicast/prefix-limit/config/prevent-teardown',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:prevent-teardown" : True if 'warning-only' in args[3] else False }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_restart_timer':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/ipv4-unicast/prefix-limit/config/restart-timer',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:restart-timer" : args[3] }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_default_policy_name':
            # openconfig_bgp_ext841615068
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/ipv4-unicast/config/openconfig-bgp-ext:default-policy-name',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:default-policy-name" : args[3] }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_send_default_route':
            # openconfig_network_instance1624994673
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/ipv4-unicast/config/send-default-route',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:send-default-route" : True if args[3] == 'True' else False}
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config':
            # openconfig_network_instance1753955874
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/ipv6-unicast/prefix-limit/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:config" : { "max-prefixes" : int(args[3]) } }
                if args[4] != '0': body["openconfig-network-instance:config"]["warning-threshold-pct"] = int(args[4])
                if 'warning-only' in args[4:]: body["openconfig-network-instance:config"]["prevent-teardown"] = True
                if 'restart' in args[4:]: body["openconfig-network-instance:config"]["restart-timer"] = args[-1]
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_max_prefixes':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/ipv6-unicast/prefix-limit/config/max-prefixes',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:max-prefixes" : int(args[3]) }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_warning_threshold_pct':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/ipv6-unicast/prefix-limit/config/warning-threshold-pct',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:warning-threshold-pct" : int(args[3]) }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_prevent_teardown':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/ipv6-unicast/prefix-limit/config/prevent-teardown',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:prevent-teardown" : True if 'warning-only' in args[3] else False }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_restart_timer':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/ipv6-unicast/prefix-limit/config/restart-timer',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:restart-timer" : args[3] }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_l2vpn_evpn_config_prefix_limit_config':
            # openconfig_network_instance985144991
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/l2vpn-evpn/prefix-limit/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:config" : { "max-prefixes" : int(args[3]) } }
                if args[4] != '0': body["openconfig-network-instance:config"]["warning-threshold-pct"] = int(args[4])
                if 'warning-only' in args[4:]: body["openconfig-network-instance:config"]["prevent-teardown"] = True
                if 'restart' in args[4:]: body["openconfig-network-instance:config"]["restart-timer"] = args[-1]
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_l2vpn_evpn_config_prefix_limit_config_max_prefixes':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/l2vpn-evpn/prefix-limit/config/max-prefixes',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:max-prefixes" : int(args[3]) }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_l2vpn_evpn_config_prefix_limit_config_warning_threshold_pct':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/l2vpn-evpn/prefix-limit/config/warning-threshold-pct',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:warning-threshold-pct" : int(args[3]) }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_l2vpn_evpn_config_prefix_limit_config_prevent_teardown':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/l2vpn-evpn/prefix-limit/config/prevent-teardown',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:prevent-teardown" : True if 'warning-only' in args[3] else False }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_l2vpn_evpn_config_prefix_limit_config_restart_timer':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/l2vpn-evpn/prefix-limit/config/restart-timer',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:restart-timer" : args[3] }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_default_policy_name':
            # openconfig_bgp_ext2059791605
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/ipv6-unicast/config/openconfig-bgp-ext:default-policy-name',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:default-policy-name" : args[3] }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_send_default_route':
            # openconfig_network_instance4125292543 
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={neighbor_address}/afi-safis/afi-safi={afi_safi_name}/ipv6-unicast/config/send-default-route',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:send-default-route" : True if args[3] == 'True' else False }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_timers_config_minimum_advertisement_interval':
            # openconfig_network_instance1223315985
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/timers/config/minimum-advertisement-interval',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:minimum-advertisement-interval":  args[2]  }

        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_import_policy':
            # openconfig_network_instance1779097864
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/apply-policy/config/import-policy',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:import-policy":  [ args[3] ] }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_export_policy':
            # openconfig_network_instance251836598
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/apply-policy/config/export-policy',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:export-policy": [ args[3] ] }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config':
            # openconfig_network_instance3096500951
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/ipv4-unicast/prefix-limit/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:config" : { "max-prefixes" : int(args[3]) } }
                if args[4] != '0': body["openconfig-network-instance:config"]["warning-threshold-pct"] = int(args[4])
                if 'warning-only' in args[4:]: body["openconfig-network-instance:config"]["prevent-teardown"] = True
                if 'restart' in args[4:]: body["openconfig-network-instance:config"]["restart-timer"] = args[-1]
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_max_prefixes':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/ipv4-unicast/prefix-limit/config/max-prefixes',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:max-prefixes" : int(args[3]) }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_warning_threshold_pct':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/ipv4-unicast/prefix-limit/config/warning-threshold-pct',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:warning-threshold-pct" : int(args[3]) }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_prevent_teardown':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/ipv4-unicast/prefix-limit/config/prevent-teardown',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:prevent-teardown" : True if 'warning-only' in args[3] else False }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_restart_timer':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/ipv4-unicast/prefix-limit/config/restart-timer',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:restart-timer" : args[3] }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_default_policy_name':
            # openconfig_bgp_ext2561500065
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/ipv4-unicast/config/openconfig-bgp-ext:default-policy-name',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:default-policy-name" : args[3] }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_send_default_route':
            # openconfig_network_instance626341485
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/ipv4-unicast/config/send-default-route',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:send-default-route" : True if args[3] == 'True' else False }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_default_policy_name':
            # openconfig_bgp_ext777259601
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/ipv6-unicast/config/openconfig-bgp-ext:default-policy-name',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:default-policy-name" : args[3] }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_send_default_route':
            # openconfig_network_instance1514043555
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/ipv6-unicast/config/send-default-route',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:send-default-route" : True if args[3] == 'True' else False }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config':
            # openconfig_network_instance1753955874
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/ipv6-unicast/prefix-limit/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:config" : { "max-prefixes" : int(args[3]) } }
                if args[4] != '0': body["openconfig-network-instance:config"]["warning-threshold-pct"] = int(args[4])
                if 'warning-only' in args[4:]: body["openconfig-network-instance:config"]["prevent-teardown"] = True
                if 'restart' in args[4:]: body["openconfig-network-instance:config"]["restart-timer"] = args[-1]
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_max_prefixes':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/ipv6-unicast/prefix-limit/config/max-prefixes',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:max-prefixes" : int(args[3]) }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_warning_threshold_pct':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/ipv6-unicast/prefix-limit/config/warning-threshold-pct',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:warning-threshold-pct" : int(args[3]) }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_prevent_teardown':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/ipv6-unicast/prefix-limit/config/prevent-teardown',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:prevent-teardown" : True if 'warning-only' in args[3] else False }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_restart_timer':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/ipv6-unicast/prefix-limit/config/restart-timer',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:restart-timer" : args[3] }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_l2vpn_evpn_config_prefix_limit_config':
            # openconfig_network_instance202630882
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/l2vpn-evpn/prefix-limit/config',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:config" : { "max-prefixes" : int(args[3]) } }
                if args[4] != '0': body["openconfig-network-instance:config"]["warning-threshold-pct"] = int(args[4])
                if 'warning-only' in args[4:]: body["openconfig-network-instance:config"]["prevent-teardown"] = True
                if 'restart' in args[4:]: body["openconfig-network-instance:config"]["restart-timer"] = args[-1]
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_l2vpn_evpn_config_prefix_limit_config_max_prefixes':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/l2vpn-evpn/prefix-limit/config/max-prefixes',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:max-prefixes" : int(args[3]) }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_l2vpn_evpn_config_prefix_limit_config_warning_threshold_pct':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/l2vpn-evpn/prefix-limit/config/warning-threshold-pct',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:warning-threshold-pct" : int(args[3]) }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_l2vpn_evpn_config_prefix_limit_config_prevent_teardown':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/l2vpn-evpn/prefix-limit/config/prevent-teardown',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:prevent-teardown" : True if 'warning-only' in args[3] else False }
        elif attr == 'openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_l2vpn_evpn_config_prefix_limit_config_restart_timer':
            # openconfig_network_instance3828573403
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/l2vpn-evpn/prefix-limit/config/restart-timer',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-network-instance:restart-timer" : args[3] }
        elif attr == 'openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_attribute_unchanged_config_as_path':
            # openconfig_bgp_ext2045507776
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:attribute-unchanged/config/as-path',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:as-path" : True if args[3] == 'True' else False }
        elif attr == 'openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_attribute_unchanged_config_next_hop':
            # openconfig_bgp_ext2045507776
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:attribute-unchanged/config/next-hop',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:next-hop" : True if args[3] == 'True' else False }
        elif attr == 'openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_filter_list_config_import_policy':
            # openconfig_bgp_ext284495364
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:filter-list/config/import-policy',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:import-policy" : args[3] }
        elif attr == 'openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_filter_list_config_export_policy':
            # openconfig_bgp_ext4092261296
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:filter-list/config/export-policy',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:export-policy" : args[3] }
        elif attr == 'openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_prefix_list_config_import_policy':
            # openconfig_bgp_ext367772702
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:prefix-list/config/import-policy',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:import-policy" : args[3] }
        elif attr == 'openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_prefix_list_config_export_policy':
            # openconfig_bgp_ext1376237526
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:prefix-list/config/export-policy',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:export-policy" : args[3] }
        elif attr == 'openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_remove_private_as_config_enabled':
            # openconfig_bgp_ext2741086768
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:remove-private-as/config/enabled',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:enabled" : True if args[3] == 'True' else False }
        elif attr == 'openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_remove_private_as_config_replace_as':
            # openconfig_bgp_ext1124459141
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/peer-groups/peer-group={peer_group_name}/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:remove-private-as/config/replace-as',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:repplace-as" : True if args[3] == 'True' else False }
        elif attr == 'openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_default_route_distance_config_external_route_distance':
            # openconfig_bgp_ext1219850592
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:default-route-distance/config/external-route-distance',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:external-route-distance" : int(args[2]) }
        elif attr == 'openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_default_route_distance_config_internal_route_distance':
            # openconfig_bgp_ext1240612726
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:default-route-distance/config/internal-route-distance',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:internal-route-distance" : int(args[2]) }
        elif attr == 'openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_default_route_distance_config_local_route_distance':
            # openconfig_bgp_ext1240612726
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/afi-safis/afi-safi={afi_safi_name}/openconfig-bgp-ext:default-route-distance/config/local-route-distance',
                name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1])
            if op == OCEXTPREFIX_PATCH:
                body = { "openconfig-bgp-ext:internal-route-distance" : int(args[2]) }
        else:
            return api.cli_not_implemented(func)
        if op == OCEXTPREFIX_PATCH:
            return api.patch(keypath, body)
        else:
            return api.delete(keypath)

    # OC-prefixes can be substring of parent prefixes, so check the longer child prefixes before the parents.
    elif func[0:DELETE_NEIGAF_OCPREFIX_LEN] == DELETE_NEIGAF_OCPREFIX or func[0:DELETE_EXTNGHAF_OCPREFIX_LEN] == DELETE_EXTNGHAF_OCPREFIX:
        uri = restconf_map[attr]
        keypath = cc.Path(uri.replace('{neighbor-address}', '{neighbor_address}').replace('{afi-safi-name}', '{afi_safi_name}'),
               name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1], afi_safi_name=args[2])
        return api.delete(keypath)
    elif func[0:DELETE_NEIGHB_OCPREFIX_LEN] == DELETE_NEIGHB_OCPREFIX or func[0:DELETE_EXTNGH_OCPREFIX_LEN] == DELETE_EXTNGH_OCPREFIX:
        uri = restconf_map[attr]
        keypath = cc.Path(uri.replace('{neighbor-address}', '{neighbor_address}'),
               name=args[0], identifier=IDENTIFIER, name1=NAME1, neighbor_address=args[1])
        return api.delete(keypath)
    elif func[0:DELETE_PGAF_OCPREFIX_LEN] == DELETE_PGAF_OCPREFIX or func[0:DELETE_EXTPGAF_OCPREFIX_LEN] == DELETE_EXTPGAF_OCPREFIX:
        uri = restconf_map[attr]
        keypath = cc.Path(uri.replace('{peer-group-name}', '{peer_group_name}').replace('{afi-safi-name}', '{afi_safi_name}'),
               name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1], afi_safi_name=args[2])
        return api.delete(keypath)
    elif func[0:DELETE_PEERGP_OCPREFIX_LEN] == DELETE_PEERGP_OCPREFIX or func[0:DELETE_EXTPG_OCPREFIX_LEN] == DELETE_EXTPG_OCPREFIX:
        uri = restconf_map[attr]
        keypath = cc.Path(uri.replace('{peer-group-name}', '{peer_group_name}'),
               name=args[0], identifier=IDENTIFIER, name1=NAME1, peer_group_name=args[1])
        return api.delete(keypath)
    elif func[0:DELETE_GLOBAF_OCPREFIX_LEN] == DELETE_GLOBAF_OCPREFIX:
        uri = restconf_map[attr]
        keypath = cc.Path(uri.replace('{afi-safi-name}', '{afi_safi_name}'),
               name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1])
        return api.delete(keypath)
    elif func[0:DELETE_EXTGLOBAF_OCPREFIX_LEN] == DELETE_EXTGLOBAF_OCPREFIX:
        uri = restconf_map[attr]
        if uri.find('={prefix}') < 0:
            keypath = cc.Path(uri.replace('{afi-safi-name}', '{afi_safi_name}'),
               name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1])
        else:
            keypath = cc.Path(uri.replace('{afi-safi-name}', '{afi_safi_name}'),
               name=args[0], identifier=IDENTIFIER, name1=NAME1, afi_safi_name=args[1], prefix=args[2])
        return api.delete(keypath)
    elif func[0:DELETE_GLOBAL_OCPREFIX_LEN] == DELETE_GLOBAL_OCPREFIX or func[0:DELETE_EXTGLB_OCPREFIX_LEN] == DELETE_EXTGLB_OCPREFIX:
        keypath = cc.Path(restconf_map[attr],
               name=args[0], identifier=IDENTIFIER, name1=NAME1)
        return api.delete(keypath)

    return api.cli_not_implemented(func)

def seconds_to_wdhm_str(seconds):
    d = datetime.now()
    d = d - timedelta(seconds=int(seconds))
    weeks = 0
    days = d.day  
    if days != 0:
       days = days - 1 
       if days != 0:
          weeks = days // 7
          days = days % 7
    if weeks != 0:
        wdhm = '{}w{}d{:02}h'.format(int(weeks), int(days), int(d.hour))
    elif days != 0:
        wdhm = '{}d{:02}h{:02}m'.format(int(days), int(d.hour), int(d.minute))
    else:
        wdhm = '{:02}:{:02}:{:02}'.format(int(d.hour), int(d.minute), int(d.second))

    return wdhm

def seconds_to_dhms_str(seconds):
    sec = int(seconds)
    hours = int(sec)/(60*60)
    sec %= (60*60)
    minutes = sec/60
    sec %= 60
    return "%02i:%02i:%02i" % (hours, minutes, sec)

def get_bgp_nbr_iptype(nbr, afisafiname):
    unnumbered = False
    is_afmatch = False
    nbr_afisafiname = "openconfig-bgp-types:IPV4_UNICAST"
    if 'afi-safis' in nbr:
       afisafis = nbr['afi-safis']['afi-safi']
       for afisafi in afisafis:
           if 'state' in afisafi:
               nbr_afisafiname = afisafi['state']['afi-safi-name']
           else:
               nbr_afisafiname = "openconfig-bgp-types:IPV4_UNICAST"
           if nbr_afisafiname == afisafiname or afisafiname == 'ipAll':
              break
    try:
        ipaddr = netaddr.IPAddress(nbr['neighbor-address'])
    except:
        unnumbered = True
    if nbr_afisafiname == afisafiname or afisafiname == 'ipAll':
       is_afmatch = True
    return is_afmatch, unnumbered

def preprocess_bgp_nbrs(afisafiname, nbrs):
    new_nbrs = []
    un_enbrs = []
    un_pnbrs = []
    un_vnbrs = []
    un_lnbrs = []
    un_nbrs = []
    for nbr in nbrs:
        is_afmatch = False
        unnumbered = False
        is_afmatch, unnumbered = get_bgp_nbr_iptype(nbr, afisafiname)
 
        if is_afmatch:
            if 'state' in nbr:
                if 'session-state' in nbr['state'] and 'last-established' in nbr['state']:
                   if nbr['state']['session-state'] == 'ESTABLISHED':
                       last_estbd = nbr['state']['last-established']
                       nbr['state']['last-established'] = seconds_to_wdhm_str(last_estbd)
                   else:
                       nbr['state']['last-established'] = 'never'

                if 'openconfig-bgp-ext:last-write' in nbr['state']:
                    last_write = nbr['state']['openconfig-bgp-ext:last-write']
                    nbr['state']['openconfig-bgp-ext:last-write'] = seconds_to_dhms_str(last_write)

                if 'openconfig-bgp-ext:last-read' in nbr['state']:
                    last_read = nbr['state']['openconfig-bgp-ext:last-read']
                    nbr['state']['openconfig-bgp-ext:last-read'] = seconds_to_dhms_str(last_read)

                if 'openconfig-bgp-ext:last-reset-time' in nbr['state']:
                    last_reset_time = nbr['state']['openconfig-bgp-ext:last-reset-time']
                    nbr['state']['openconfig-bgp-ext:last-reset-time'] = seconds_to_dhms_str(last_reset_time)

            if unnumbered == True:
                ifName = nbr['neighbor-address']
                if ifName.startswith("Ethernet"):
                   un_enbrs.append(nbr)
                elif ifName.startswith("PortChannel"):
                   un_pnbrs.append(nbr)
                elif ifName.startswith("Vlan"):
                   un_vnbrs.append(nbr)
                elif ifName.startswith("Loopback"):
                   un_lnbrs.append(nbr)
                else:
                   un_nbrs.append(nbr)
            else:
                new_nbrs.append(nbr)

    tup = new_nbrs
    new_nbrs = sorted(tup, key=getNbr)
    tup = un_enbrs
    un_enbrs = sorted(tup, key=getIntfId)
    tup = un_pnbrs
    un_pnbrs = sorted(tup, key=getIntfId)
    tup = un_vnbrs
    un_vnbrs = sorted(tup, key=getIntfId)
    tup = un_lnbrs
    un_lnbrs = sorted(tup, key=getIntfId)
    tup = un_nbrs
    un_nbr = sorted(tup, key=getIntfId)

    un_enbrs.extend(un_pnbrs)
    un_enbrs.extend(un_vnbrs)
    un_enbrs.extend(un_lnbrs)
    un_enbrs.extend(un_nbrs)
    un_enbrs.extend(new_nbrs)
    return un_enbrs

def generate_show_bgp_dampening(args=[]):
    damp_option = ""
    i=2
    for arg in args[2:]:
        if "dampening" == arg:
             damp_option = args[i+1]
        i = i + 1

    keypath = []
    body = None
    vrf = args[0]
    afisafi = "IPV4_UNICAST"
    api = cc.ApiClient()

    keypath = cc.Path('/restconf/operations/sonic-bgp-show:show-bgp')
    inputs = {"vrf-name":vrf, "address-family":afisafi}
    inputs['query-type'] = "DAMPENING"

    if damp_option == "dampened-paths" :
        inputs['dampening'] = "DAMPENED-PATHS"
    elif damp_option == "flap-statistics" :
        inputs['dampening'] = "FLAP-STATISTICS"
    elif damp_option == "parameters" :
        inputs['dampening'] = "PARAMETERS"

    d = {}
    body = {"sonic-bgp-show:input": inputs}
    response = api.post(keypath, body)
    if not response:
        return 1
    if(response.ok()):
        d = response.content['sonic-bgp-show:output']['response']
        if len(d) != 0 and "warning" not in d and "Unknown command:" not in d:
            try:
                if damp_option == "dampened-paths" :
                    d = json.loads(d, object_pairs_hook=OrderedDict)
                    show_cli_output("show_ip_bgp_damp_path.j2", d)
                elif damp_option == "flap-statistics" :
                    d = json.loads(d, object_pairs_hook=OrderedDict)
                    show_cli_output("show_ip_bgp_damp_stats.j2",d)
                elif damp_option == "parameters" :
                    show_cli_output("show_ip_bgp_damp_param.j2", d)
            except:
                return 1
        else:
          d = json.loads(d)
          print(d['warning'])
    else:
        print response.error_message()
        return 1


def invoke_show_api(func, args=[]):
    api = cc.ApiClient()
    keypath = []
    body = None
    tmp = {}

    if func == 'get_show_bgp':
        return generate_show_bgp_routes(args)

    elif func == 'get_ip_bgp_summary':
        d = {}
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global', name=args[1], identifier=IDENTIFIER, name1=NAME1)
        response = api.get(keypath)
        if response.ok() and response.content is not None:
            d.update(response.content)
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors', name=args[1], identifier=IDENTIFIER, name1=NAME1)
            response = api.get(keypath)
            if response.ok() and response.content is not None:
                if args[2] == 'ipv6':
                    afisafiname = 'openconfig-bgp-types:IPV6_UNICAST'
                elif args[2] == 'evpn':
                    afisafiname = 'openconfig-bgp-types:L2VPN_EVPN'
                else:
                    afisafiname = 'openconfig-bgp-types:IPV4_UNICAST'
                d['afisafiname'] = afisafiname

                if 'openconfig-network-instance:neighbors' in response.content:
                    tmp['neighbor'] = preprocess_bgp_nbrs(afisafiname, response.content['openconfig-network-instance:neighbors']['neighbor'])
                    d['openconfig-network-instance:neighbors'] = tmp
                return d
            else:
                print response.error_message()
        else:
            print response.error_message()

        return d

    elif func == 'get_ip_bgp_neighbors_neighborip':
        d = {}
        if args[2] == 'ipv6':
            afisafiname = 'openconfig-bgp-types:IPV6_UNICAST'
        elif args[2] == 'evpn':
            afisafiname = 'openconfig-bgp-types:L2VPN_EVPN'
        elif args[2] == 'ipAll':
            afisafiname = args[2]
        else:
            afisafiname = 'openconfig-bgp-types:IPV4_UNICAST'
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/state', name=args[1], identifier=IDENTIFIER, name1=NAME1)
        response = api.get(keypath)
        if response.ok() and response.content is not None:
            d.update(response.content)

            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors/neighbor={nbr_addr}', name=args[1], identifier=IDENTIFIER, name1=NAME1, nbr_addr=args[3])
            response = api.get(keypath)
            if response.ok() and response.content is not None:
               if 'openconfig-network-instance:neighbor' in response.content:
                  tmp['neighbor'] = preprocess_bgp_nbrs(afisafiname, response.content['openconfig-network-instance:neighbor'])
                  d['openconfig-network-instance:neighbors'] = tmp
               return d
            else:
                print response.error_message()
        else:
           print response.error_message()
        return d
    elif func == 'get_ip_bgp_neighbors':
        d = {}
        if args[2] == 'ipv6':
            afisafiname = 'openconfig-bgp-types:IPV6_UNICAST'
        elif args[2] == 'evpn':
            afisafiname = 'openconfig-bgp-types:L2VPN_EVPN'
        elif args[2] == 'ipAll':
            afisafiname = args[2]
        else:
            afisafiname = 'openconfig-bgp-types:IPV4_UNICAST'
        keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/global/state', name=args[1], identifier=IDENTIFIER, name1=NAME1)
        response = api.get(keypath)
        if response.ok() and response.content is not None:
            d.update(response.content)
            keypath = cc.Path('/restconf/data/openconfig-network-instance:network-instances/network-instance={name}/protocols/protocol={identifier},{name1}/bgp/neighbors', name=args[1], identifier=IDENTIFIER, name1=NAME1)
            response = api.get(keypath)
            if response.ok() and response.content is not None:
               if 'openconfig-network-instance:neighbors' in response.content:
                   tmp['neighbor'] = preprocess_bgp_nbrs(afisafiname, response.content['openconfig-network-instance:neighbors']['neighbor'])
                   d['openconfig-network-instance:neighbors'] = tmp
               return d
            else:
                print response.error_message()
        else:
            print response.error_message()

        return d
    elif func == 'get_show_bgp_prefix':
        return generate_show_bgp_prefix_routes(args)

    elif func == 'get_show_bgp_peer_group':
        return generate_show_bgp_peer_groups(args, False)

    elif func == 'get_show_bgp_peer_group_all':
        return generate_show_bgp_peer_groups(args, True)

    else:
        body = {}

    return api.cli_not_implemented(func)

def mkArgs2dict(args):
    dct = {}
    for e in args:
        k, v = e.split(':', 1)
        if v: dct[k] = v
    return dct

def mkArgds2list(argds, *argv):
    lst = []
    for k in argv:
        if argds.get(k): lst.append(argds.get(k))
    return lst

def parseInvoke_api(func, args=[]):
    response = invoke_api(func, args)
    if response.ok():
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            print(api_response)
            if api_response is None:
                print("Failed")
                return 1
    else:
        print response.error_message()
        return 1
    return 0

def parseGlobl(vrf_name, cmd, args=[]):
    argds = mkArgs2dict(args)

    rc = 0
    if cmd == 'no router bgp':
         for aft in [ 'IPV4_UNICAST', 'IPV6_UNICAST' ]:
             for proto in [ 'connected', 'static', 'ospf' ]:
                 if aft == 'IPV6_UNICAST' and proto == 'ospf':
                    rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_table_connections_table_connection', [ vrf_name ] + [ aft, 'ospf3' ])
                 rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_table_connections_table_connection', [ vrf_name ] + [ aft, proto ])
         rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp', [ vrf_name ])
    elif cmd == 'max-med':
         if not argds.get('maxmedval'):
             if argds.get('maxmedopts') == 'on-startup':
                rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_max_med_config_max_med_val', [ vrf_name ])
             else:
                rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_max_med_config_admin_max_med_val', [ vrf_name ])
         rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_max_med_config', [ vrf_name ] + mkArgds2list(argds, 'maxmedopts', 'stime', 'maxmedval'))
    elif cmd == 'update-delay':
         if not argds.get('maxmedval'):
             rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_update_delay_config_establish_wait', [ vrf_name ])
         rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_update_delay_config', [ vrf_name ] + mkArgds2list(argds, 'time', 'maxmedval'))
    elif cmd == 'bestpath med':
         rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_route_selection_options_config_med_missing_as_worst', [ vrf_name ] + mkArgds2list(argds, 'missing-as-worst'))
         rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_route_selection_options_config_med_confed', [ vrf_name ] + mkArgds2list(argds, 'confed'))
    elif cmd == 'listen range':
         rc += parseInvoke_api('patch_openconfig_network_instance1717438887', [ vrf_name ] + mkArgds2list(argds, 'addr', 'pgname'))
    elif cmd == 'listen limit':
         rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_config_max_dynamic_neighbors', [ vrf_name ] + mkArgds2list(argds, 'lmt-val'))
    elif cmd == 'confederation':
         if argds.get('conf-opt') == 'identifier':
             rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_confederation_config_identifier', [ vrf_name ] + mkArgds2list(argds, 'id-as'))
         else:
             rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_confederation_config_member_as', [ vrf_name ] + mkArgds2list(argds, 'peer-as'))
    elif cmd == 'timers':
          rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_config_keepalive_interval', [ vrf_name ] + mkArgds2list(argds, 'keepalive-intvl'))
          rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_config_hold_time', [ vrf_name ] + mkArgds2list(argds, 'hold-time'))
    elif cmd == 'no max-med':
         if argds.get('maxmedopts') == 'on-startup':
             rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_max_med_config_time', [ vrf_name ])
             rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_max_med_config_max_med_val', [ vrf_name ])
         else:
             rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_max_med_config_administrative', [ vrf_name ])
             rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_max_med_config_admin_max_med_val', [ vrf_name ])
    elif cmd == 'no update-delay':
         rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_update_delay_config_max_delay', [ vrf_name ])
         rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_update_delay_config_establish_wait', [ vrf_name ])
    elif cmd == 'no bestpath as-path multipath-relax':
         if argds.get('as-set'):
             rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_use_multiple_paths_ebgp_config_as_set', [ vrf_name ])
         else:
             rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_use_multiple_paths_ebgp_config_allow_multiple_as', [ vrf_name ])
             rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_use_multiple_paths_ebgp_config_as_set', [ vrf_name ])
    elif cmd == 'no bestpath med':
         rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_route_selection_options_config_med_missing_as_worst', [ vrf_name ] + mkArgds2list(argds, 'missing-as-worst'))
         rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_route_selection_options_config_med_confed', [ vrf_name ] + mkArgds2list(argds, 'confed'))
    elif cmd == 'no address-family ipv4':
         for proto in [ 'connected', 'static', 'ospf' ]:
             rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_table_connections_table_connection', [ vrf_name ] + [ 'IPV4_UNICAST', proto ])
         rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi', [ vrf_name ] + [ 'IPV4_UNICAST' ])
    elif cmd == 'no address-family ipv6':
         for proto in [ 'connected', 'static', 'ospf', 'ospf3' ]:
             rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_table_connections_table_connection', [ vrf_name ] + [ 'IPV6_UNICAST', proto ])
         rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi', [ vrf_name ] + [ 'IPV6_UNICAST' ])
    elif cmd == 'no listen':
         if argds.get('listen-opt') == 'range':
             rc += parseInvoke_api('delete_openconfig_network_instance1717438887', [ vrf_name ] + mkArgds2list(argds, 'addr', 'pgname'))
         else:
             rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_config_max_dynamic_neighbors', [ vrf_name ] + mkArgds2list(argds, 'lmt-val'))
    elif cmd == 'no confederation':
         if argds.get('conf-opt') == 'identifier':
             rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_confederation_config_identifier', [ vrf_name ] + mkArgds2list(argds, 'id-as'))
         else:
             rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_global_confederation_config_member_as', [ vrf_name ])
    elif cmd == 'no timers':
          rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_config_keepalive_interval', [ vrf_name ] + mkArgds2list(argds, 'keepalive-intvl'))
          rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_config_hold_time', [ vrf_name ] + mkArgds2list(argds, 'hold-time'))
    else:
        print cc.ApiClient().cli_not_implemented(cmd).error_message()
        return 1
    return rc

def parseNeigh(vrf_name, nbr_addr, cmd, args=[]):
    argds = mkArgs2dict(args)

    rc = 0
    if cmd == 'ebgp-multihop':
         if argds.get('hop-count'):
             rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_ebgp_multihop_config', [ vrf_name, nbr_addr ] + [ 'True' ] + mkArgds2list(argds, 'hop-count'))
         else:
             rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_ebgp_multihop_config', [ vrf_name, nbr_addr ] + [ 'True', '255' ])
    elif cmd == 'remote-as':
         if argds.get('remtype') == 'internal' or argds.get('remtype') == 'external':
             rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_peer_type', [ vrf_name, nbr_addr ] + mkArgds2list(argds, 'remtype'))
         else:
             rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_peer_as', [ vrf_name, nbr_addr ] + mkArgds2list(argds, 'as-num-dot'))
    elif cmd == 'timers':
         if argds.get('timertype') == 'connect':
             rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_timers_config_connect_retry', [ vrf_name, nbr_addr ] + mkArgds2list(argds, 'connect-time'))
         else:
             rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_timers_config_keepalive_interval', [ vrf_name, nbr_addr ] + mkArgds2list(argds, 'keepalive-intvl'))
             rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_timers_config_hold_time', [ vrf_name, nbr_addr ] + mkArgds2list(argds, 'hold-time'))
    elif cmd == 'shutdown':
         if argds.get('message'):
             rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_shutdown_message', [ vrf_name, nbr_addr ] + mkArgds2list(argds, 'MSG'))
         rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_enabled', [ vrf_name, nbr_addr ] + [ 'False' ])
    elif cmd == 'bfd':
         if argds.get('check-control-plane-failure'):
             rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_enable_bfd_config_bfd_check_control_plane_failure', [ vrf_name, nbr_addr ] + [ 'True' ])
         rc += parseInvoke_api('patch_openconfig_bfd_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_enable_bfd_config_enabled', [ vrf_name, nbr_addr ] + [ 'True' ])
    elif cmd == 'local-as':
         if argds.get('no-prepend'):
             rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_local_as_no_prepend', [ vrf_name, nbr_addr ] + [ 'True' ])
         else:
             rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_local_as_no_prepend', [ vrf_name, nbr_addr ] + [ 'False' ])
         if argds.get('replace-as'):
             rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_local_as_replace_as', [ vrf_name, nbr_addr ] + [ 'True' ])
         else:
             rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_local_as_replace_as', [ vrf_name, nbr_addr ] + [ 'False' ])
         rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_local_as', [ vrf_name, nbr_addr ] + mkArgds2list(argds, 'asnum'))
    elif cmd == 'no ebgp-multihop':
         rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_ebgp_multihop_config_enabled', [ vrf_name, nbr_addr ])
         rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_ebgp_multihop_config_multihop_ttl', [ vrf_name, nbr_addr ])
    elif cmd == 'no remote-as':
         rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_peer_as', [ vrf_name, nbr_addr ] + mkArgds2list(argds, 'as-num-dot'))
         rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_peer_type', [ vrf_name, nbr_addr ] + mkArgds2list(argds, 'internal', 'external'))
    elif cmd == 'no timers':
         if argds.get('timertype') == 'connect':
             rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_timers_config_connect_retry', [ vrf_name, nbr_addr ] + mkArgds2list(argds, 'connect-time'))
         else:
             rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_timers_config_keepalive_interval', [ vrf_name, nbr_addr ] + mkArgds2list(argds, 'keepalive-intvl'))
             rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_timers_config_hold_time', [ vrf_name, nbr_addr ] + mkArgds2list(argds, 'hold-time'))
    elif cmd == 'no shutdown':
         rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_enabled', [ vrf_name, nbr_addr ] + [ 'True' ])
         rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_shutdown_message', [ vrf_name, nbr_addr ] + mkArgds2list(argds, 'MSG'))
    elif cmd == 'no bfd':
         if argds.get('check-control-plane-failure'):
             rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_enable_bfd_config_bfd_check_control_plane_failure', [ vrf_name, nbr_addr ])
         else:
             rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_enable_bfd_config_bfd_check_control_plane_failure', [ vrf_name, nbr_addr ])
             rc += parseInvoke_api('delete_openconfig_bfd_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_enable_bfd_config_enabled', [ vrf_name, nbr_addr ])
    elif cmd == 'no local-as':
         rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_local_as', [ vrf_name, nbr_addr ])
         rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_local_as_no_prepend', [ vrf_name, nbr_addr ])
         rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_config_local_as_replace_as', [ vrf_name, nbr_addr ])
    else:
        print cc.ApiClient().cli_not_implemented(cmd).error_message()
        return 1
    return rc

def parsePeerg(vrf_name, template_name, cmd, args=[]):
    argds = mkArgs2dict(args)

    rc = 0
    if cmd == 'ebgp-multihop':
         if argds.get('hop-count'):
             rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_ebgp_multihop_config', [ vrf_name, template_name ] + [ 'True' ] + mkArgds2list(argds, 'hop-count'))
         else:
             rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_ebgp_multihop_config', [ vrf_name, template_name ] + [ 'True', '255' ])
    elif cmd == 'remote-as':
         if argds.get('remtype') == 'internal' or argds.get('remtype') == 'external':
             rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_peer_type', [ vrf_name, template_name ] + mkArgds2list(argds, 'remtype'))
         else:
             rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_peer_as', [ vrf_name, template_name ] + mkArgds2list(argds, 'as-num-dot'))
    elif cmd == 'timers':
         if argds.get('timertype') == 'connect':
             rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_timers_config_connect_retry', [ vrf_name, template_name ] + mkArgds2list(argds, 'connect-time'))
         else:
             rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_timers_config_keepalive_interval', [ vrf_name, template_name ] + mkArgds2list(argds, 'keepalive-intvl'))
             rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_timers_config_hold_time', [ vrf_name, template_name ] + mkArgds2list(argds, 'hold-time'))
    elif cmd == 'shutdown':
         if argds.get('message'):
             rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_shutdown_message', [ vrf_name, template_name ] + mkArgds2list(argds, 'MSG'))
         rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_enabled', [ vrf_name, template_name ] + [ 'False' ])
    elif cmd == 'bfd':
         if argds.get('check-control-plane-failure'):
             rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_enable_bfd_config_bfd_check_control_plane_failure', [ vrf_name, template_name ] + [ 'True' ])
         rc += parseInvoke_api('patch_openconfig_bfd_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_enable_bfd_config_enabled', [ vrf_name, template_name ] + [ 'True' ])
    elif cmd == 'local-as':
         if argds.get('no-prepend'):
             rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_local_as_no_prepend', [ vrf_name, template_name ] + [ 'True' ])
         else:
             rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_local_as_no_prepend', [ vrf_name, template_name ] + [ 'False' ])
         if argds.get('replace-as'):
             rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_local_as_replace_as', [ vrf_name, template_name ] + [ 'True' ])
         else:
             rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_local_as_replace_as', [ vrf_name, template_name ] + [ 'False' ])
         rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_local_as', [ vrf_name, template_name ] + mkArgds2list(argds, 'asnum'))
    elif cmd == 'no ebgp-multihop':
         rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_ebgp_multihop_config_enabled', [ vrf_name, template_name ])
         rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_ebgp_multihop_config_multihop_ttl', [ vrf_name, template_name ])
    elif cmd == 'no remote-as':
         rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_peer_as', [ vrf_name, template_name ] + mkArgds2list(argds, 'as-num-dot'))
         rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_peer_type', [ vrf_name, template_name ] + mkArgds2list(argds, 'internal', 'external'))
    elif cmd == 'no timers':
         if argds.get('timertype') == 'connect':
             rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_timers_config_connect_retry', [ vrf_name, template_name ] + mkArgds2list(argds, 'connect-time'))
         else:
             rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_timers_config_keepalive_interval', [ vrf_name, template_name ] + mkArgds2list(argds, 'keepalive-intvl'))
         rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_timers_config_hold_time', [ vrf_name, template_name ] + mkArgds2list(argds, 'hold-time'))
    elif cmd == 'no shutdown':
         rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_enabled', [ vrf_name, template_name ] + [ 'True' ])
         rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_shutdown_message', [ vrf_name, template_name ] + mkArgds2list(argds, 'MSG'))
    elif cmd == 'no bfd':
         if argds.get('check-control-plane-failure'):
             rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_enable_bfd_config_bfd_check_control_plane_failure', [ vrf_name, template_name ])
         else:
             rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_enable_bfd_config_bfd_check_control_plane_failure', [ vrf_name, template_name ])
             rc += parseInvoke_api('delete_openconfig_bfd_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_enable_bfd_config_enabled', [ vrf_name, template_name ])
    elif cmd == 'no local-as':
         rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_local_as', [ vrf_name, template_name ])
         rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_local_as_no_prepend', [ vrf_name, template_name ])
         rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_config_local_as_replace_as', [ vrf_name, template_name ])
    else:
        print cc.ApiClient().cli_not_implemented(cmd).error_message()
        return 1
    return rc

def parseGloblV4(vrf_name, cmd, args=[]):
    argds = mkArgs2dict(args)

    rc = 0
    if cmd == 'redistribute':
        if argds.get('route-map-name'):
            rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_table_connections_table_connection_config_import_policy', [ vrf_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'protocol', 'route-map-name'))
            rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_table_connections_table_connection_config_import_policy', [ vrf_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'protocol', 'route-map-name'))
        elif not argds.get('metric'):
            rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_table_connections_table_connection_config', [ vrf_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'protocol'))
        if argds.get('metric'):
            rc += parseInvoke_api('patch_openconfig_network_instance_ext_network_instances_network_instance_table_connections_table_connection_config_metric', [ vrf_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'protocol', 'metvalue'))
    elif cmd == 'maximum-paths ibgp':
        rc += parseInvoke_api('patch_openconfig_network_instance1543452951', [ vrf_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'ipaths'))
        rc += parseInvoke_api('patch_openconfig_bgp_ext3691744053', [ vrf_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'equal-cluster-length'))
    elif cmd == 'network':
        if argds.get('backdoor') == 'x':
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_network_config_network_config_backdoor', [ vrf_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'prefix'))
        if not argds.get('route-map'):
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_network_config_network_config_policy_name', [ vrf_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'prefix'))
        rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_network_config_network_config', [ vrf_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'prefix', 'backdoor', 'route-map-name'))
    elif cmd == 'aggregate-address':
        if argds.get('rtemap'):
            rc += parseInvoke_api('PATCH_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_aggregate_address_config_aggregate_address_config_policy_name', [ vrf_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'prefix', 'rtemap'))
        if not argds.get('as-set'):
            rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_aggregate_address_config_aggregate_address_config_as_set', [ vrf_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'prefix'))
        if not argds.get('summary-only'):
            rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_aggregate_address_config_aggregate_address_config_summary_only', [ vrf_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'prefix'))
        rc += parseInvoke_api('PATCH_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_aggregate_address_config_aggregate_address_config', [ vrf_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'prefix', 'as-set', 'summary-only'))
    elif cmd == 'dampening':
        if not argds.get('reusethr'):
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_route_flap_damping_config_reuse_threshold', [ vrf_name, 'IPV4_UNICAST' ])
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_route_flap_damping_config_suppress_threshold', [ vrf_name, 'IPV4_UNICAST' ])
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_route_flap_damping_config_max_suppress', [ vrf_name, 'IPV4_UNICAST' ])
            if not argds.get('halflife'):
                rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_route_flap_damping_config_half_life', [ vrf_name, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_route_flap_damping_config', [ vrf_name, 'IPV4_UNICAST' ] + [ 'True' ] + mkArgds2list(argds, 'halflife', 'reusethr', 'suppressthr', 'maxsuppress'))
    elif cmd == 'no redistribute':
        rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_table_connections_table_connection', [ vrf_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'protocol'))
        rc += parseInvoke_api('delete_openconfig_network_instance_ext_network_instances_network_instance_table_connections_table_connection_config_metric', [ vrf_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'protocol'))
    elif cmd == 'no maximum-paths ibgp':
        rc += parseInvoke_api('delete_openconfig_network_instance1543452951', [ vrf_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'ipaths'))
        rc += parseInvoke_api('delete_openconfig_bgp_ext3691744053', [ vrf_name, 'IPV4_UNICAST' ])
    elif cmd == 'no network':
        if argds.get('backdoor'):
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_network_config_network_config_backdoor', [ vrf_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'prefix'))
        if argds.get('route-map'):
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_network_config_network_config_policy_name', [ vrf_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'prefix'))
        elif not argds.get('backdoor'):
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_network_config_network', [ vrf_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'prefix'))
    elif cmd == 'no distance bgp':
        rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_default_route_distance_config_external_route_distance', [ vrf_name, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_default_route_distance_config_internal_route_distance', [ vrf_name, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_default_route_distance_config_local_route_distance', [ vrf_name, 'IPV4_UNICAST' ])
    elif cmd == 'no dampening':
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_route_flap_damping_config_enabled', [ vrf_name, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_route_flap_damping_config_half_life', [ vrf_name, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_route_flap_damping_config_reuse_threshold', [ vrf_name, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_route_flap_damping_config_suppress_threshold', [ vrf_name, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_route_flap_damping_config_max_suppress', [ vrf_name, 'IPV4_UNICAST' ])
    else:
        print cc.ApiClient().cli_not_implemented(cmd).error_message()
        return 1
    return rc

def parseNeighV4(vrf_name, nbr_addr, cmd, args=[]):
    argds = mkArgs2dict(args)

    rc = 0
    if cmd == 'allowas-in':
        if argds.get('value'):
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_as_count', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'value'))
        else:
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_as_count', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'value'))
        if argds.get('origin'):
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_origin', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + [ 'True' ])
        else:
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_origin', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + [ 'False' ])
        rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_enabled', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + [ 'True' ])
    elif cmd == 'route-map':
        if argds.get('direction') == 'in':
             rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
             rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
        else:
             rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
             rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
    elif cmd == 'attribute-unchanged':
        optstr = argds.get('as-path', '') + argds.get('med', '') + argds.get('next-hop', '')
        if optstr == '' or optstr == 'as-pathmednext-hop':
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_attribute_unchanged_config', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ]  + [ 'as-path', 'med', 'next-hop' ])
        else:
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_attribute_unchanged_config', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'as-path', 'med', 'next-hop'))
    elif cmd == 'default-originate':
        if argds.get('route-map'):
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_send_default_route', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + [ 'True' ])
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_default_policy_name', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'rtemap'))
        else:
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_send_default_route', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + [ 'True' ])
    elif cmd == 'filter-list':
        if argds.get('filtopt') == 'in':
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_filter_list_config_import_policy', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'fname'))
        else:
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_filter_list_config_export_policy', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'fname'))
    elif cmd == 'next-hop-self':
        if not argds.get('force'):
           rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_next_hop_self_config_force', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_next_hop_self_config', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + [ 'True' ] + mkArgds2list(argds, 'force'))
    elif cmd == 'prefix-list':
        if argds.get('prfopt') == 'in':
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_prefix_list_config_import_policy', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'pname'))
        else:
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_prefix_list_config_export_policy', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'pname'))
    elif cmd == 'remove-private-as':
        if not argds.get('all'):
           rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_remove_private_as_config_all', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ])
        if not argds.get('replace-as'):
           rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_remove_private_as_config_replace_as', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_remove_private_as_config', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + [ 'True' ] + mkArgds2list(argds, 'all', 'replace-as'))
    elif cmd == 'maximum-prefix':
        if argds.get('threshold-val') == '0':
             rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_warning_threshold_pct', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ])
        if not argds.get('warning-only'):
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_prevent_teardown', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ])
        if not argds.get('restart'):
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_restart_timer', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'max-prefix-val', 'threshold-val', 'maxpfopt', 'interval'))
    elif cmd == 'no allowas-in':
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_as_count', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'value'))
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_enabled', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + [ 'False' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_origin', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ])
    elif cmd == 'no route-map':
        if argds.get('direction') == 'in':
             rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
        elif argds.get('direction') == 'out':
             rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
        else:
             rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
             rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
    elif cmd == 'no attribute-unchanged':
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_attribute_unchanged_config_as_path', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_attribute_unchanged_config_med', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_attribute_unchanged_config_next_hop', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ])
    elif cmd == 'no default-originate':
        rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_send_default_route', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + [ 'False' ])
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_default_policy_name', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'rtemap'))
    elif cmd == 'no filter-list':
        if argds.get('filtopt') == 'in':
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_filter_list_config_import_policy', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'fname'))
        else:
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_filter_list_config_export_policy', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'fname'))
    elif cmd == 'no next-hop-self':
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_next_hop_self_config_enabled', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_next_hop_self_config_force', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ])
    elif cmd == 'no prefix-list':
        if argds.get('prfopt') == 'in':
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_prefix_list_config_import_policy', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'pname'))
        else:
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_prefix_list_config_export_policy', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'pname'))
    elif cmd == 'no remove-private-as':
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_remove_private_as_config_enabled', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_remove_private_as_config_all', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_remove_private_as_config_replace_as', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ])
    elif cmd == 'no maximum-prefix':
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_max_prefixes', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_warning_threshold_pct', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_prevent_teardown', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_restart_timer', [ vrf_name, nbr_addr, 'IPV4_UNICAST' ])
    else:
        print cc.ApiClient().cli_not_implemented(cmd).error_message()
        return 1
    return rc

def parsePeergV4(vrf_name, template_name, cmd, args=[]):
    argds = mkArgs2dict(args)

    rc = 0
    if cmd == 'allowas-in':
        if argds.get('value'):
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_as_count', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'value'))
        else:
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_as_count', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'value'))
        if argds.get('origin'):
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_origin', [ vrf_name, template_name, 'IPV4_UNICAST' ] + [ 'True' ])
        else:
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_origin', [ vrf_name, template_name, 'IPV4_UNICAST' ] + [ 'False' ])
        rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_enabled', [ vrf_name, template_name, 'IPV4_UNICAST' ] + [ 'True' ])
    elif cmd == 'route-map':
        if argds.get('direction') == 'in':
          rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
          rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
        else:
          rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
          rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
    elif cmd == 'attribute-unchanged':
        optstr = argds.get('as-path', '') + argds.get('med', '') + argds.get('next-hop', '')
        if optstr == '' or optstr == 'as-pathmednext-hop':
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_attribute_unchanged_config', [ vrf_name, template_name, 'IPV4_UNICAST' ] + [ 'as-path', 'med', 'next-hop' ])
        else:
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_attribute_unchanged_config', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'as-path', 'med', 'next-hop'))
    elif cmd == 'default-originate':
        if argds.get('route-map'):
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_send_default_route', [ vrf_name, template_name, 'IPV4_UNICAST' ] + [ 'True' ])
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_default_policy_name', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'rtemap'))
        else:
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_send_default_route', [ vrf_name, template_name, 'IPV4_UNICAST' ] + [ 'True' ])
    elif cmd == 'filter-list':
        if argds.get('filtopt') == 'in':
            rc += parseInvoke_api('PATCH_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_filter_list_config_import_policy', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'fname'))
        else:
            rc += parseInvoke_api('PATCH_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_filter_list_config_export_policy', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'fname'))
    elif cmd == 'next-hop-self':
        rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_next_hop_self_config', [ vrf_name, template_name, 'IPV4_UNICAST' ] + [ 'True' ] + mkArgds2list(argds, 'force'))
        if not argds.get('force'):
           rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_next_hop_self_config_force', [ vrf_name, template_name, 'IPV4_UNICAST' ])
    elif cmd == 'prefix-list':
        if argds.get('prfopt') == 'in':
            rc += parseInvoke_api('PATCH_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_prefix_list_config_import_policy', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'pname'))
        else:
            rc += parseInvoke_api('PATCH_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_prefix_list_config_export_policy', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'pname'))
    elif cmd == 'remove-private-as':
        if not argds.get('all'):
           rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_remove_private_as_config_all', [ vrf_name, template_name, 'IPV4_UNICAST' ])
        if not argds.get('replace-as'):
           rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_remove_private_as_config_replace_as', [ vrf_name, template_name, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_remove_private_as_config', [ vrf_name, template_name, 'IPV4_UNICAST' ] + [ 'True' ] + mkArgds2list(argds, 'all', 'replace-as'))
    elif cmd == 'maximum-prefix':
        if argds.get('threshold-val') == '0':
             rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_warning_threshold_pct', [ vrf_name, template_name, 'IPV4_UNICAST' ])
        if not argds.get('warning-only'):
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_prevent_teardown', [ vrf_name, template_name, 'IPV4_UNICAST' ])
        if not argds.get('restart'):
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_restart_timer', [ vrf_name, template_name, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'max-prefix-val', 'threshold-val', 'maxpfopt', 'interval'))
    elif cmd == 'no allowas-in':
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_as_count', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'value'))
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_origin', [ vrf_name, template_name, 'IPV4_UNICAST' ] + [ 'False' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_enabled', [ vrf_name, template_name, 'IPV4_UNICAST' ] + [ 'False' ])
    elif cmd == 'no route-map':
        if argds.get('direction') == 'in':
             rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
        elif argds.get('direction') == 'out':
             rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
        else:
             rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
             rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
    elif cmd == 'no attribute-unchanged':
        rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_attribute_unchanged_config_as_path', [ vrf_name, template_name, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_attribute_unchanged_config_med', [ vrf_name, template_name, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_attribute_unchanged_config_next_hop', [ vrf_name, template_name, 'IPV4_UNICAST' ])
    elif cmd == 'no default-originate':
        rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_send_default_route', [ vrf_name, template_name, 'IPV4_UNICAST' ] + [ 'False' ])
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_default_policy_name', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'rtemap'))
    elif cmd == 'no filter-list':
        if argds.get('filtopt') == 'in':
            rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_filter_list_config_import_policy', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'fname'))
        else:
            rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_filter_list_config_export_policy', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'fname'))
    elif cmd == 'no next-hop-self':
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_next_hop_self_config_enabled', [ vrf_name, template_name, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_next_hop_self_config_force', [ vrf_name, template_name, 'IPV4_UNICAST' ])
    elif cmd == 'no prefix-list':
        if argds.get('prfopt') == 'in':
            rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_prefix_list_config_import_policy', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'pname'))
        else:
            rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_prefix_list_config_export_policy', [ vrf_name, template_name, 'IPV4_UNICAST' ] + mkArgds2list(argds, 'pname'))
    elif cmd == 'no remove-private-as':
        rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_remove_private_as_config_enabled', [ vrf_name, template_name, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_remove_private_as_config_all', [ vrf_name, template_name, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_remove_private_as_config_replace_as', [ vrf_name, template_name, 'IPV4_UNICAST' ])
    elif cmd == 'no maximum-prefix':
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_max_prefixes', [ vrf_name, template_name, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_warning_threshold_pct', [ vrf_name, template_name, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_prevent_teardown', [ vrf_name, template_name, 'IPV4_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv4_unicast_config_prefix_limit_config_restart_timer', [ vrf_name, template_name, 'IPV4_UNICAST' ])
    else:
        print cc.ApiClient().cli_not_implemented(cmd).error_message()
        return 1
    return rc

def parseGloblV6(vrf_name, cmd, args=[]):
    argds = mkArgs2dict(args)

    rc = 0
    if cmd == 'redistribute':
        if argds.get('route-map-name'):
            rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_table_connections_table_connection_config_import_policy', [ vrf_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'protocol', 'route-map-name'))
        elif not argds.get('metric'):
            rc += parseInvoke_api('patch_openconfig_network_instance_network_instances_network_instance_table_connections_table_connection_config', [ vrf_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'protocol'))
        if argds.get('metric'):
            rc += parseInvoke_api('patch_openconfig_network_instance_ext_network_instances_network_instance_table_connections_table_connection_config_metric', [ vrf_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'protocol', 'metvalue'))
    elif cmd == 'maximum-paths ibgp':
        rc += parseInvoke_api('patch_openconfig_network_instance1543452951', [ vrf_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'ipaths'))
        rc += parseInvoke_api('patch_openconfig_bgp_ext3691744053', [ vrf_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'equal-cluster-length'))
    elif cmd == 'network':
        if not argds.get('route-map'):
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_network_config_network_config_policy_name', [ vrf_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'prefix'))
        rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_network_config_network_config', [ vrf_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'prefix', 'route-map-name'))
    elif cmd == 'aggregate-address':
        if argds.get('rtemap'):
            rc += parseInvoke_api('PATCH_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_aggregate_address_config_aggregate_address_config_policy_name', [ vrf_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'prefix', 'rtemap'))
        if not argds.get('as-set'):
            rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_aggregate_address_config_aggregate_address_config_as_set', [ vrf_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'prefix'))
        if not argds.get('summary-only'):
            rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_aggregate_address_config_aggregate_address_config_summary_only', [ vrf_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'prefix'))
        rc += parseInvoke_api('PATCH_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_aggregate_address_config_aggregate_address_config', [ vrf_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'prefix', 'as-set', 'summary-only'))
    elif cmd == 'no redistribute':
        rc += parseInvoke_api('delete_openconfig_network_instance_network_instances_network_instance_table_connections_table_connection', [ vrf_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'protocol'))
        rc += parseInvoke_api('delete_openconfig_network_instance_ext_network_instances_network_instance_table_connections_table_connection_config_metric', [ vrf_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'protocol'))
    elif cmd == 'no maximum-paths ibgp':
        rc += parseInvoke_api('delete_openconfig_network_instance1543452951', [ vrf_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'ipaths'))
        rc += parseInvoke_api('delete_openconfig_bgp_ext3691744053', [ vrf_name, 'IPV6_UNICAST' ])
    elif cmd == 'no network':
        if argds.get('route-map'):
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_network_config_network_config_policy_name', [ vrf_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'prefix'))
        else:
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_network_config_network', [ vrf_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'prefix'))
    elif cmd == 'no distance bgp':
        rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_default_route_distance_config_external_route_distance', [ vrf_name, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_default_route_distance_config_internal_route_distance', [ vrf_name, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_global_afi_safis_afi_safi_default_route_distance_config_local_route_distance', [ vrf_name, 'IPV6_UNICAST' ])
    else:
        print cc.ApiClient().cli_not_implemented(cmd).error_message()
        return 1
    return rc

def parseNeighV6(vrf_name, nbr_addr, cmd, args=[]):
    argds = mkArgs2dict(args)

    rc = 0
    if cmd == 'allowas-in':
        if argds.get('value'):
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_as_count', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'value'))
        else:
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_as_count', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'value'))
        if argds.get('origin'):
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_origin', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + [ 'True' ])
        else:
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_origin', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + [ 'False' ])
        rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_enabled', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + [ 'True' ])
    elif cmd == 'route-map':
        if argds.get('direction') == 'in':
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
        else:
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
    elif cmd == 'attribute-unchanged':
        optstr = argds.get('as-path', '') + argds.get('med', '') + argds.get('next-hop', '')
        if optstr == '' or optstr == 'as-pathmednext-hop':
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_attribute_unchanged_config', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + [ 'as-path', 'med', 'next-hop' ])
        else:
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_attribute_unchanged_config', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'as-path', 'med', 'next-hop'))
    elif cmd == 'default-originate':
        if argds.get('route-map'):
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_send_default_route', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + [ 'True' ])
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_default_policy_name', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'rtemap'))
        else:
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_send_default_route', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + [ 'True' ])
    elif cmd == 'filter-list':
        if argds.get('filtopt') == 'in':
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_filter_list_config_import_policy', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'fname'))
        else:
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_filter_list_config_export_policy', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'fname'))
    elif cmd == 'next-hop-self':
        if not argds.get('force'):
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_next_hop_self_config_force', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_next_hop_self_config', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ]  + [ 'True' ] + mkArgds2list(argds, 'force'))
    elif cmd == 'prefix-list':
        if argds.get('prfopt') == 'in':
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_prefix_list_config_import_policy', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'pname'))
        else:
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_prefix_list_config_export_policy', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'pname'))
    elif cmd == 'remove-private-as':
        if not argds.get('all'):
           rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_remove_private_as_config_all', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ])
        if not argds.get('replace-as'):
           rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_remove_private_as_config_replace_as', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_remove_private_as_config', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ]  + [ 'True' ] + mkArgds2list(argds, 'all', 'replace-as'))
    elif cmd == 'maximum-prefix':
        if argds.get('threshold-val') == '0':
             rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_warning_threshold_pct', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ])
        if not argds.get('warning-only'):
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_prevent_teardown', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ])
        if not argds.get('restart'):
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_restart_timer', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'max-prefix-val', 'threshold-val', 'maxpfopt', 'interval'))
    elif cmd == 'no allowas-in':
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_as_count', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'value'))
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_enabled', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + [ 'False' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_origin', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ])
    elif cmd == 'no route-map':
        if argds.get('direction') == 'in':
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
        elif argds.get('direction') == 'out':
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
        else:
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
    elif cmd == 'no attribute-unchanged':
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_attribute_unchanged_config_as_path', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_attribute_unchanged_config_med', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_attribute_unchanged_config_next_hop', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ])
    elif cmd == 'no default-originate':
        rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_send_default_route', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + [ 'False' ])
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_default_policy_name', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'rtemap'))
    elif cmd == 'no filter-list':
        if argds.get('filtopt') == 'in':
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_filter_list_config_import_policy', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'fname'))
        else:
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_filter_list_config_export_policy', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'fname'))
    elif cmd == 'no next-hop-self':
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_next_hop_self_config_enabled', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_next_hop_self_config_force', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ])
    elif cmd == 'no prefix-list':
        if argds.get('prfopt') == 'in':
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_prefix_list_config_import_policy', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'pname'))
        else:
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_prefix_list_config_export_policy', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'pname'))
    elif cmd == 'no remove-private-as':
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_remove_private_as_config_enabled', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_remove_private_as_config_all', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_remove_private_as_config_replace_as', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ])
    elif cmd == 'no maximum-prefix':
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_max_prefixes', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_warning_threshold_pct', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_prevent_teardown', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_restart_timer', [ vrf_name, nbr_addr, 'IPV6_UNICAST' ])
    else:
        print cc.ApiClient().cli_not_implemented(cmd).error_message()
        return 1
    return rc

def parsePeergV6(vrf_name, template_name, cmd, args=[]):
    argds = mkArgs2dict(args)

    rc = 0
    if cmd == 'allowas-in':
        if argds.get('value'):
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_as_count', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'value'))
        else:
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_as_count', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'value'))
        if argds.get('origin'):
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_origin', [ vrf_name, template_name, 'IPV6_UNICAST' ] + [ 'True' ])
        else:
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_origin', [ vrf_name, template_name, 'IPV6_UNICAST' ] + [ 'False' ])
        rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_enabled', [ vrf_name, template_name, 'IPV6_UNICAST' ] + [ 'True' ])
    elif cmd == 'route-map':
        if argds.get('direction') == 'in':
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
        else:
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
    elif cmd == 'attribute-unchanged':
        optstr = argds.get('as-path', '') + argds.get('med', '') + argds.get('next-hop', '')
        if optstr == '' or optstr == 'as-pathmednext-hop':
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_attribute_unchanged_config', [ vrf_name, template_name, 'IPV6_UNICAST' ] + [ 'as-path', 'med', 'next-hop' ])
        else:
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_attribute_unchanged_config', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'as-path', 'med', 'next-hop'))
    elif cmd == 'default-originate':
        if argds.get('route-map'):
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_send_default_route', [ vrf_name, template_name, 'IPV6_UNICAST' ] + [ 'True' ])
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_default_policy_name', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'rtemap'))
        else:
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_send_default_route', [ vrf_name, template_name, 'IPV6_UNICAST' ] + [ 'True' ])
    elif cmd == 'filter-list':
        if argds.get('filtopt') == 'in':
            rc += parseInvoke_api('PATCH_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_filter_list_config_import_policy', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'fname'))
        else:
            rc += parseInvoke_api('PATCH_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_filter_list_config_export_policy', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'fname'))
    elif cmd == 'next-hop-self':
        rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_next_hop_self_config', [ vrf_name, template_name, 'IPV6_UNICAST' ]  + [ 'True' ] + mkArgds2list(argds, 'force'))
        if not argds.get('force'):
           rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_next_hop_self_config_force', [ vrf_name, template_name, 'IPV6_UNICAST' ])
    elif cmd == 'prefix-list':
        if argds.get('prfopt') == 'in':
            rc += parseInvoke_api('PATCH_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_prefix_list_config_import_policy', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'pname'))
        else:
            rc += parseInvoke_api('PATCH_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_prefix_list_config_export_policy', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'pname'))
    elif cmd == 'remove-private-as':
        if not argds.get('all'):
           rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_remove_private_as_config_all', [ vrf_name, template_name, 'IPV6_UNICAST' ])
        if not argds.get('replace-as'):
           rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_remove_private_as_config_replace_as', [ vrf_name, template_name, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_remove_private_as_config', [ vrf_name, template_name, 'IPV6_UNICAST' ]  + [ 'True' ] + mkArgds2list(argds, 'all', 'replace-as'))
    elif cmd == 'maximum-prefix':
        if argds.get('threshold-val') == '0':
             rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_warning_threshold_pct', [ vrf_name, template_name, 'IPV6_UNICAST' ])
        if not argds.get('warning-only'):
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_prevent_teardown', [ vrf_name, template_name, 'IPV6_UNICAST' ])
        if not argds.get('restart'):
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_restart_timer', [ vrf_name, template_name, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'max-prefix-val', 'threshold-val', 'maxpfopt', 'interval'))
    elif cmd == 'no allowas-in':
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_as_count', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'value'))
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_origin', [ vrf_name, template_name, 'IPV6_UNICAST' ] + [ 'False' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_enabled', [ vrf_name, template_name, 'IPV6_UNICAST' ] + [ 'False' ])
    elif cmd == 'no route-map':
        if argds.get('direction') == 'in':
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
        elif argds.get('direction') == 'out':
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
        else:
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'route-name-str'))
    elif cmd == 'no attribute-unchanged':
        rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_attribute_unchanged_config_as_path', [ vrf_name, template_name, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_attribute_unchanged_config_med', [ vrf_name, template_name, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_attribute_unchanged_config_next_hop', [ vrf_name, template_name, 'IPV6_UNICAST' ])
    elif cmd == 'no default-originate':
        rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_send_default_route', [ vrf_name, template_name, 'IPV6_UNICAST' ] + [ 'False' ])
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_default_policy_name', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'rtemap'))
    elif cmd == 'no filter-list':
        if argds.get('filtopt') == 'in':
            rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_filter_list_config_import_policy', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'fname'))
        else:
            rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_filter_list_config_export_policy', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'fname'))
    elif cmd == 'no next-hop-self':
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_next_hop_self_config_enabled', [ vrf_name, template_name, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_next_hop_self_config_force', [ vrf_name, template_name, 'IPV6_UNICAST' ])
    elif cmd == 'no prefix-list':
        if argds.get('prfopt') == 'in':
            rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_prefix_list_config_import_policy', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'pname'))
        else:
            rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_prefix_list_config_export_policy', [ vrf_name, template_name, 'IPV6_UNICAST' ] + mkArgds2list(argds, 'pname'))
    elif cmd == 'no remove-private-as':
        rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_remove_private_as_config_enabled', [ vrf_name, template_name, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_remove_private_as_config_all', [ vrf_name, template_name, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_remove_private_as_config_replace_as', [ vrf_name, template_name, 'IPV6_UNICAST' ])
    elif cmd == 'no maximum-prefix':
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_max_prefixes', [ vrf_name, template_name, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_warning_threshold_pct', [ vrf_name, template_name, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_prevent_teardown', [ vrf_name, template_name, 'IPV6_UNICAST' ])
        rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_ipv6_unicast_config_prefix_limit_config_restart_timer', [ vrf_name, template_name, 'IPV6_UNICAST' ])
    else:
        print cc.ApiClient().cli_not_implemented(cmd).error_message()
        return 1
    return rc

def parseNeighEvpn(vrf_name, nbr_addr, cmd, args=[]):
    argds = mkArgs2dict(args)

    rc = 0
    if cmd == 'allowas-in':
        if argds.get('value'):
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_as_count', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'value'))
        else:
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_as_count', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'value'))
        if argds.get('origin'):
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_origin', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ] + [ 'True' ])
        else:
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_origin', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ] + [ 'False' ])
        rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_enabled', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ] + [ 'True' ])
    elif cmd == 'route-map':
        if argds.get('direction') == 'in':
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'route-name-str'))
        else:
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'route-name-str'))
    elif cmd == 'attribute-unchanged':
        optstr = argds.get('as-path', '') + argds.get('med', '') + argds.get('next-hop', '')
        if optstr == '' or optstr == 'as-pathmednext-hop':
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_attribute_unchanged_config', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ] + [ 'as-path', 'med', 'next-hop' ])
        else:
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_attribute_unchanged_config', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'as-path', 'med', 'next-hop'))
    elif cmd == 'next-hop-self':
        if not argds.get('force'):
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_next_hop_self_config_force', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ])
        rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_next_hop_self_config', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ]  + [ 'True' ] + mkArgds2list(argds, 'force'))
    elif cmd == 'no allowas-in':
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_as_count', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'value'))
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_enabled', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ] + [ 'False' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_allow_own_as_config_origin', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ])
    elif cmd == 'no route-map':
        if argds.get('direction') == 'in':
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'route-name-str'))
        elif argds.get('direction') == 'out':
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'route-name-str'))
        else:
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'route-name-str'))
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'route-name-str'))
    elif cmd == 'no attribute-unchanged':
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_attribute_unchanged_config_as_path', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_attribute_unchanged_config_med', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_attribute_unchanged_config_next_hop', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ])
    elif cmd == 'no next-hop-self':
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_next_hop_self_config_enabled', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_neighbors_neighbor_afi_safis_afi_safi_next_hop_self_config_force', [ vrf_name, nbr_addr, 'L2VPN_EVPN' ])
    else:
        print cc.ApiClient().cli_not_implemented(cmd).error_message()
        return 1
    return rc

def parsePeergEvpn(vrf_name, template_name, cmd, args=[]):
    argds = mkArgs2dict(args)

    rc = 0
    if cmd == 'allowas-in':
        if argds.get('value'):
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_as_count', [ vrf_name, template_name, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'value'))
        else:
            rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_as_count', [ vrf_name, template_name, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'value'))
        if argds.get('origin'):
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_origin', [ vrf_name, template_name, 'L2VPN_EVPN' ] + [ 'True' ])
        else:
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_origin', [ vrf_name, template_name, 'L2VPN_EVPN' ] + [ 'False' ])
        rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_enabled', [ vrf_name, template_name, 'L2VPN_EVPN' ] + [ 'True' ])
    elif cmd == 'route-map':
        if argds.get('direction') == 'in':
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, template_name, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'route-name-str'))
        else:
            rc += parseInvoke_api('PATCH_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, template_name, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'route-name-str'))
    elif cmd == 'attribute-unchanged':
        optstr = argds.get('as-path', '') + argds.get('med', '') + argds.get('next-hop', '')
        if optstr == '' or optstr == 'as-pathmednext-hop':
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_attribute_unchanged_config', [ vrf_name, template_name, 'L2VPN_EVPN' ] + [ 'as-path', 'med', 'next-hop' ])
        else:
            rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_attribute_unchanged_config', [ vrf_name, template_name, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'as-path', 'med', 'next-hop'))
    elif cmd == 'next-hop-self':
        rc += parseInvoke_api('patch_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_next_hop_self_config', [ vrf_name, template_name, 'L2VPN_EVPN' ]  + [ 'True' ] + mkArgds2list(argds, 'force'))
        if not argds.get('force'):
           rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_next_hop_self_config_force', [ vrf_name, template_name, 'L2VPN_EVPN' ])
    elif cmd == 'no allowas-in':
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_as_count', [ vrf_name, template_name, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'value'))
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_origin', [ vrf_name, template_name, 'L2VPN_EVPN' ] + [ 'False' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_allow_own_as_config_enabled', [ vrf_name, template_name, 'L2VPN_EVPN' ] + [ 'False' ])
    elif cmd == 'no route-map':
        if argds.get('direction') == 'in':
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, template_name, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'route-name-str'))
        elif argds.get('direction') == 'out':
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, template_name, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'route-name-str'))
        else:
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_import_policy', [ vrf_name, template_name, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'route-name-str'))
            rc += parseInvoke_api('DELETE_openconfig_network_instance_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_apply_policy_config_export_policy', [ vrf_name, template_name, 'L2VPN_EVPN' ] + mkArgds2list(argds, 'route-name-str'))
    elif cmd == 'no attribute-unchanged':
        rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_attribute_unchanged_config_as_path', [ vrf_name, template_name, 'L2VPN_EVPN' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_attribute_unchanged_config_med', [ vrf_name, template_name, 'L2VPN_EVPN' ])
        rc += parseInvoke_api('DELETE_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_attribute_unchanged_config_next_hop', [ vrf_name, template_name, 'L2VPN_EVPN' ])
    elif cmd == 'no next-hop-self':
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_next_hop_self_config_enabled', [ vrf_name, template_name, 'L2VPN_EVPN' ])
        rc += parseInvoke_api('delete_openconfig_bgp_ext_network_instances_network_instance_protocols_protocol_bgp_peer_groups_peer_group_afi_safis_afi_safi_next_hop_self_config_force', [ vrf_name, template_name, 'L2VPN_EVPN' ])
    else:
        print cc.ApiClient().cli_not_implemented(cmd).error_message()
        return 1
    return rc

def parseGloblShow(vrf_name, cmd, args=[]):
    try:
        pipe_idx = args.index('\|')
        args = args[:pipe_idx]
    except:
        # no pipe
        pass

    if cmd == 'show bgp l2vpn evpn summary':
      return generate_show_bgp_neighbors(args)

    if cmd == 'show bgp ipv4' or cmd == 'show bgp ipv6':
        if vrf_name == 'all':
            generate_show_bgp_vrf_all(args)
            return 0

        if len(args) == 0:
            return get_show_bgp(args)
        if args[0] == 'statistics':
            return generate_show_bgp_stats(args)
        elif args[0] == 'ip-prefix':
            return generate_show_bgp_prefix_routes(args)
        elif args[0] == 'neighbors':
            nbr_subcmds = [ 'routes', 'received-routes', 'advertised-routes' ]
            if args[-1] in  nbr_subcmds:
                return generate_show_bgp_routes(args)
            elif args[1] == 'neighbor-ip':
                response = invoke_show_api('get_ip_bgp_neighbors_neighborip',  [ None, vrf_name, 'ipv6' if cmd == 'show bgp ipv6' else 'ipv4', args[-1] ])
                show_cli_output('show_ip_bgp_neighbors.j2', response)
            elif args[1] == 'interface':
                response = invoke_show_api('get_ip_bgp_neighbors_neighborip',  [ None, vrf_name, 'ipv6' if cmd == 'show bgp ipv6' else 'ipv4', args[-1] ])
                show_cli_output('show_ip_bgp_neighbors.j2', response)
            else:
                response = invoke_show_api('get_ip_bgp_neighbors', [ None, vrf_name, 'ipv6' if cmd == 'show bgp ipv6' else 'ipv4' ] + args[4:])
                show_cli_output('show_ip_bgp_neighbors.j2', response)
            return 0
        elif args[0] == 'summary':
            return generate_show_bgp_neighbors(args)
        elif args[0] == 'dampening':
            return generate_show_bgp_dampening([ vrf_name, 'ipv6' if cmd == 'show bgp ipv6' else 'ipv4' ] + args[4:])
        else:
            return generate_show_bgp_routes(args)

    elif cmd == 'show bgp all':
        vrf_arg = [ 'vrf' , vrf_name ]
        if args[0] == 'peer-group':
            if len(args) == 5 or args[4] == 'vrf' and len(args) == 7:
                response = invoke_show_api('get_show_bgp_peer_group_all', vrf_arg + args)
            else:
                response = invoke_show_api('get_show_bgp_peer_group', vrf_arg + args)
        elif args[0] == 'neighbors':
            if args[1] == 'neighbor-ip':
                response = invoke_show_api('get_ip_bgp_neighbors_neighborip', [ None, vrf_name, 'ipAll', args[-1] ])
                show_cli_output('show_ip_bgp_neighbors.j2', response)
            elif args[1] == 'interface':
                response = invoke_show_api('get_ip_bgp_neighbors_neighborip', [ None, vrf_name, 'ipAll', args[-1] ])
                show_cli_output('show_ip_bgp_neighbors.j2', response)
            else:
                response = invoke_show_api('get_ip_bgp_neighbors', [ None, vrf_name, 'ipAll' ])
                show_cli_output('show_ip_bgp_neighbors.j2', response)
        return 0

    print cc.ApiClient().cli_not_implemented(cmd).error_message()
    return 1

def invoke_parse(pycmd, args=[]):
    op = pycmd.split(':')[1]
    idx = 1 if op[0] == 'G' else 2
    start = idx
    end = len(args)
    while idx < end:
        if args[idx] == '\n':
            end = idx
            idx += 1
            break
        elif args[idx][-1] == '\n':
            args[idx] = args[idx][:-1]
            idx += 1
            end = idx
            break
        idx += 1
    cmd = ' '.join(args[start:end])

    if op == 'Gbl':
        return parseGlobl(args[0], cmd, args[idx:])
    elif op == 'GblV4':
        return parseGloblV4(args[0], cmd, args[idx:])
    elif op == 'GblV6':
        return parseGloblV6(args[0], cmd, args[idx:])
    elif op == 'Nbr':
        return parseNeigh(args[0], args[1], cmd, args[idx:])
    elif op == 'NbrV4':
        return parseNeighV4(args[0], args[1], cmd, args[idx:])
    elif op == 'NbrV6':
        return parseNeighV6(args[0], args[1], cmd, args[idx:])
    elif op == 'NbrEvpn':
        return parseNeighEvpn(args[0], args[1], cmd, args[idx:])
    elif op == 'Pgp':
        return parsePeerg(args[0], args[1], cmd, args[idx:])
    elif op == 'PgpV4':
        return parsePeergV4(args[0], args[1], cmd, args[idx:])
    elif op == 'PgpV6':
        return parsePeergV6(args[0], args[1], cmd, args[idx:])       
    elif op == 'PgpEvpn':
        return parsePeergEvpn(args[0], args[1], cmd, args[idx:]) 
    elif op == 'GblShow':
        return parseGloblShow(args[0], cmd, args[idx:])

    print cc.ApiClient().cli_not_implemented(cmd).error_message()
    return 1

def run(func, args):
    if func == 'get_show_bgp':
        response = invoke_show_api(func, args)
    elif func == 'get_ip_bgp_summary':
        response = invoke_show_api(func, args)
        show_cli_output(args[0], response)
    elif func == 'get_ip_bgp_neighbors_neighborip':
        response = invoke_show_api(func, args)
        show_cli_output(args[0], response)
    elif func == 'get_ip_bgp_neighbors':
        response = invoke_show_api(func, args)
        show_cli_output(args[0], response)
    elif func == 'get_show_bgp_prefix':
        response = invoke_show_api(func, args)
    elif func == 'get_show_bgp_peer_group':
        response = invoke_show_api(func, args)
    elif func == 'get_show_bgp_peer_group_all':
        response = invoke_show_api(func, args)
    elif func[:9] == '_PyParse:':
        ret = invoke_parse(func, args)
        if ret != 0:
            return 1
    else:
        response = invoke_api(func, args)
        if response.ok():
            if response.content is not None:
                # Get Command Output
                api_response = response.content
                print(api_response)
                if api_response is None:
                    print("Failed")
                    return 1
        else:
            print response.error_message()
            return 1

if __name__ == '__main__':

    pipestr().write(sys.argv)
    func = sys.argv[1]

    run(func, sys.argv[2:])

