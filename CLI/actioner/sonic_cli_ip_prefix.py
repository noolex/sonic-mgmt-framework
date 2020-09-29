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

import sys
import time
import json
import ast
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output

import urllib3
urllib3.disable_warnings()

def generate_ipprefix_uri(args, delete):
    _action = "PERMIT"
    _mode = set_name = ge = le = _maskrange_length = _ip_prefix = ''
    ge_val = le_val = seq_no = seqno_exists = prefix_exists = le_exists = ge_exists = is_error = i = 0
    for arg in args:
        if "permit" == arg:
           _action = "PERMIT"
        elif "deny" == arg:
           _action = "DENY"
        elif "seq" == arg:
           seq_no = int(args[i+1])
           seqno_exists = 1
        elif "prefix-list" == arg:
           set_name = args[i+1]
           if len(args) > 6:
              _ip_prefix = args[i+5]
              prefix_exists = 1
        elif "ge" == arg:
           ge_exists = 1
           ge_val = int(args[i+1])
           ge = args[i+1]
        elif "le" == arg:
           le_exists = 1
           le_val = int(args[i+1])
           le = args[i+1]
        elif "ip" == arg:
           _mode = "IPV4"
           max = "32"
        elif "ipv6" == arg:
           _mode = "IPV6"
           max = "128"
        else:
           temp = 1
        i = i + 1
    if seqno_exists and prefix_exists:
       _prefix, _mask = _ip_prefix.split("/")
       mask_val = int(_mask)
       if (ge_exists == 0 and le_exists == 0):
          _maskrange_length = "exact"
       elif (ge_exists == 1 and le_exists == 0):
          if (ge_val < mask_val):
             is_error = 1
          _maskrange_length = ge + ".." + max
       elif (ge_exists == 0 and le_exists == 1):
          if (mask_val > le_val):
             is_error = 1
          _maskrange_length = _mask+".."+le
       else:
          if ((ge_val < mask_val) or (mask_val > le_val) or (ge_val > le_val)):
             is_error = 1
          _maskrange_length = ge+".."+le

       if is_error:
          print ("%Error: Invalid prefix range, make sure: len <= ge <= le")
          exit(1)
       if delete:
          keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/defined-sets/prefix-sets/prefix-set={prefix_list_name}/openconfig-routing-policy-ext:prefixes-ext/prefix={sequence_no},{prefix}%2F{mask},{masklength_range}', prefix_list_name=set_name, sequence_no=str(seq_no), prefix=_prefix, mask=_mask, masklength_range=_maskrange_length)
          body = None
       else:
          keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/defined-sets/prefix-sets')
          body = {"openconfig-routing-policy:prefix-sets":{"prefix-set":[{"name": set_name,"config":{"name": set_name,
                  "mode": _mode},"openconfig-routing-policy-ext:prefixes-ext":{"prefix":[{"sequence-number": seq_no,"ip-prefix": _ip_prefix,"masklength-range": _maskrange_length,"config": {
                  "sequence-number": seq_no,"ip-prefix": _ip_prefix,"masklength-range": _maskrange_length,"openconfig-routing-policy-ext:action": _action}}]}}]}}
    else:
       keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/defined-sets/prefix-sets/prefix-set={prefix_list_name}',
                prefix_list_name=set_name)
       body = None

    return keypath, body


def invoke(func, args):
    body = None
    aa = cc.ApiClient()

    if func == 'ip_prefix_create':
        keypath, body = generate_ipprefix_uri(args, 0)
        return aa.patch(keypath, body)

    elif func == 'ip_prefix_delete':
        keypath, body = generate_ipprefix_uri(args, 1)
        return aa.delete(keypath)

    elif func == 'ip_prefix_show_specific':
        if len(args) > 1:
            keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/defined-sets/prefix-sets/prefix-set={name}',name=args[1])
        else:
            # show all
            keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/defined-sets/prefix-sets')
        return aa.get(keypath)

    elif func == 'ipv6_prefix_show_specific':
        if len(args) > 1:
            keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/defined-sets/prefix-sets/prefix-set={name}',name=args[1])
        else:
            # show all
            keypath = cc.Path('/restconf/data/openconfig-routing-policy:routing-policy/defined-sets/prefix-sets')
        return aa.get(keypath)

    else:
        return aa.cli_not_implemented(func)


def run(func, args):
  try:
    response = invoke(func,args)

    if response.ok():
        if response.content is not None:
            # Get Command Output
            api_response = response.content
            if api_response is None:
                print ("%Error: Internal error.")
                return
            #print api_response
            show_cli_output(args[0], api_response)
    else:
        print response.error_message()
        return
  except Exception as e:
    print ("%Error: Internal error.")

  return



if __name__ == '__main__':

    pipestr().write(sys.argv)
    run(sys.argv[1], sys.argv[2:])

