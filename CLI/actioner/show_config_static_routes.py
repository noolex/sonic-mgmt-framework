import socket
from show_config_if_cmd import show_render_if_cmd

#Gets all static routes CLI configured for a prefix in a VRF or default instance
def static_route_nh_cli(cmd_str, intf_list , ip_list, bh_list , nh_vrf_list, dist_list, track_list):
   all_cmd=''
   no_of_nh = 0 
   if len(ip_list) != 0 :
      no_of_nh = len(ip_list)
   elif len(intf_list) != 0:
      no_of_nh = len(intf_list)
   elif len(bh_list) != 0:
      no_of_nh = len(bh_list)
   if (no_of_nh == 0): return None
   len_attr = len(ip_list)
   if (len_attr != 0  and len_attr != no_of_nh): return None
   len_attr = len(intf_list)
   if (len_attr != 0  and len_attr != no_of_nh): return None
   len_attr = len(bh_list)
   if (len_attr != 0  and len_attr != no_of_nh): return None
   len_attr = len(dist_list)
   if (len_attr != 0  and len_attr != no_of_nh): return None
   len_attr = len(nh_vrf_list)
   if (len_attr != 0  and len_attr != no_of_nh): return None
   len_attr = len(track_list)
   if (len_attr != 0  and len_attr != no_of_nh): return None
   
   for iter in range (0, no_of_nh):
      this_cmd = cmd_str
      if bh_list  and bh_list[iter] == 'true':
         this_cmd = this_cmd +' blackhole' 
         if dist_list and dist_list[iter]:
            if dist_list[iter] != '0':
               this_cmd = this_cmd + ' ' + dist_list[iter]
         all_cmd = all_cmd + this_cmd +';'
         continue
      if ip_list and ip_list[iter]:
        if ip_list[iter] != '0.0.0.0' and ip_list[iter] != '0:0:0:0:0:0:0:0' and ip_list[iter] != '::':
           this_cmd = this_cmd + ' ' + ip_list[iter]
      if track_list and track_list[iter]:
        if track_list[iter] != '0':
           this_cmd = this_cmd + ' track ' + track_list[iter]
      if intf_list and intf_list[iter]:
        table_rec = {"ifname" : intf_list[iter]}
        int_syntax = show_render_if_cmd(table_rec, 'ifname', '', '')
        if int_syntax:  
           this_cmd = this_cmd + ' interface '+ int_syntax
      if nh_vrf_list and  nh_vrf_list[iter]:
        this_cmd = this_cmd + ' nexthop-vrf '+  nh_vrf_list[iter]
      if dist_list and dist_list[iter]:
        if dist_list[iter] != '0':
           this_cmd = this_cmd + ' ' + dist_list[iter]
      all_cmd = all_cmd + this_cmd +';'

   return all_cmd  

def show_ntwk_static_v4route(render_tables):
   cmd_prfx = 'ip route '
   return static_route_ntwk_inst("ipv4", cmd_prfx, render_tables)

def show_ntwk_static_v6route(render_tables):
   cmd_prfx = 'ipv6 route '
   return static_route_ntwk_inst("ipv6", cmd_prfx, render_tables)

def static_route_get_prefix_type(prefix):
   ip_prf = prefix.split('/')
   if (ip_prf is not None):
      addr = ip_prf[0]
      try:
         socket.inet_pton(socket.AF_INET, addr)
         return "ipv4"
      except socket.error:
         try:
            socket.inet_pton(socket.AF_INET6, addr)
            return "ipv6"
         except socket.error:
            return None 
   return None 
       
def static_route_ntwk_inst(ip_version, cmd_prfx, render_tables):
   cmd_str = cmd_str_to_send = cmd_for_vrf = ''
   vrf_key =  render_tables['vrf_name']

   if vrf_key is None:
      return 'CB_SUCCESS', cmd_str 

   if 'sonic-static-route:sonic-static-route/STATIC_ROUTE/STATIC_ROUTE_LIST' in render_tables:
      for rt_inst in render_tables['sonic-static-route:sonic-static-route/STATIC_ROUTE/STATIC_ROUTE_LIST']:
         # print rt_inst
         cmd_for_vrf =''
         if not rt_inst['vrf-name']:
            continue
         if (vrf_key == 'default' and rt_inst['vrf-name'] != vrf_key):
            continue
         if (vrf_key == 'Vrf*'):
            if('Vrf' not in rt_inst['vrf-name']): 
                continue
            else:
                cmd_for_vrf = "vrf "+ rt_inst['vrf-name'] 

         prefix = rt_inst['prefix'] 
         prefix_type = static_route_get_prefix_type(prefix)
         if prefix_type is None:
            continue

         if (ip_version == 'ipv6' and prefix_type != "ipv6"):
            continue 
         elif (ip_version == 'ipv4' and prefix_type != "ipv4"):
            continue

         if not cmd_for_vrf: 
            cmd_str = cmd_prfx + prefix
         else:
            cmd_str = cmd_prfx + cmd_for_vrf + ' ' + prefix

         intf_list = bh_list = ip_list = nh_vrf_list = dist_list = track_list = [] 
         for nh_attr in rt_inst:
            if 'ifname' in nh_attr:
               intf_list = rt_inst['ifname'].split(',')
            elif 'nexthop-vrf' in nh_attr:
               nh_vrf_list = rt_inst['nexthop-vrf'].split(',')
            elif 'nexthop' in nh_attr:
               ip_list = rt_inst['nexthop'].split(',')
            elif 'blackhole' in nh_attr:
               bh_list = rt_inst['blackhole'].split(',')
            elif 'distance' in nh_attr:
               dist_list = rt_inst['distance'].split(',')
            elif 'track' in nh_attr:
               track_list = rt_inst['track'].split(',')
            else:
               pass

         nh_pram_cli = static_route_nh_cli(cmd_str, intf_list , ip_list, bh_list , nh_vrf_list, dist_list, track_list)
         if (nh_pram_cli is not None):
            cmd_str_to_send = cmd_str_to_send + nh_pram_cli 
          
   return 'CB_SUCCESS', cmd_str_to_send
