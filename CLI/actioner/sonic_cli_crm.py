#!/usr/bin/python
###########################################################################
#
# Copyright 2020 Broadcom. The term Broadcom refers to Broadcom Inc. and/or
# its subsidiaries.
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
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output
import cli_client as cc

def run(func, args):

    # omit pipe arguments
    if '\\|' in args:
        args = args[:args.index('\\|')]

    last = len(args)
    if func == "patch":
        if last > 0:
            last -= 1
        data = args[last]
    else:
        data = None

    for idx in range(0, last):
        func += "-"
        func += args[idx]

    uri_conf = '/restconf/data/openconfig-system:system/openconfig-system-crm:crm'
    uri_stat = '/restconf/data/openconfig-system:system/openconfig-system-crm:crm/statistics'
    uri_stat_acl = '/restconf/data/openconfig-system:system/openconfig-system-crm:crm/acl-statistics'

    tmpl = None
    path = None
    body = None

    aa = cc.ApiClient()

    # GET/SHOW CONFIG
    if func == "show-crm-summary":
        tmpl = "show_crm_summary.j2"
        path = cc.Path(uri_conf + "/config")
    elif func == "show-crm-thresholds-acl-group":
        tmpl = "show_crm_thresholds_acl_group.j2"
        path = cc.Path(uri_conf + "/threshold/acl/group")
    elif func == "show-crm-thresholds-acl-table":
        tmpl = "show_crm_thresholds_acl_table.j2"
        path = cc.Path(uri_conf + "/threshold/acl/table/config")
    elif func == "show-crm-thresholds-dnat":
        tmpl = "show_crm_thresholds_dnat.j2"
        path = cc.Path(uri_conf + "/threshold/dnat/config")
    elif func == "show-crm-thresholds-fdb":
        tmpl = "show_crm_thresholds_fdb.j2"
        path = cc.Path(uri_conf + "/threshold/fdb/config")
    elif func == "show-crm-thresholds-ipmc":
        tmpl = "show_crm_thresholds_ipmc.j2"
        path = cc.Path(uri_conf + "/threshold/ipmc/config")
    elif func == "show-crm-thresholds-ipv4-neighbor":
        tmpl = "show_crm_thresholds_ipv4_neighbor.j2"
        path = cc.Path(uri_conf + "/threshold/ipv4/neighbor/config")
    elif func == "show-crm-thresholds-ipv4-nexthop":
        tmpl = "show_crm_thresholds_ipv4_nexthop.j2"
        path = cc.Path(uri_conf + "/threshold/ipv4/nexthop/config")
    elif func == "show-crm-thresholds-ipv4-route":
        tmpl = "show_crm_thresholds_ipv4_route.j2"
        path = cc.Path(uri_conf + "/threshold/ipv4/route/config")
    elif func == "show-crm-thresholds-ipv6-neighbor":
        tmpl = "show_crm_thresholds_ipv6_neighbor.j2"
        path = cc.Path(uri_conf + "/threshold/ipv6/neighbor/config")
    elif func == "show-crm-thresholds-ipv6-nexthop":
        tmpl = "show_crm_thresholds_ipv6_nexthop.j2"
        path = cc.Path(uri_conf + "/threshold/ipv6/nexthop/config")
    elif func == "show-crm-thresholds-ipv6-route":
        tmpl = "show_crm_thresholds_ipv6_route.j2"
        path = cc.Path(uri_conf + "/threshold/ipv6/route/config")
    elif func == "show-crm-thresholds-nexthop-group-member":
        tmpl = "show_crm_thresholds_nexthop_group_member.j2"
        path = cc.Path(uri_conf + "/threshold/nexthop/group-member/config")
    elif func == "show-crm-thresholds-nexthop-group-object":
        tmpl = "show_crm_thresholds_nexthop_group_object.j2"
        path = cc.Path(uri_conf + "/threshold/nexthop/group-object/config")
    elif func == "show-crm-thresholds-snat":
        tmpl = "show_crm_thresholds_snat.j2"
        path = cc.Path(uri_conf + "/threshold/snat/config")
    elif func == "show-crm-thresholds-all":
        tmpl = "show_crm_thresholds_all.j2"
        path = cc.Path(uri_conf + "/threshold")

    # SET/PATCH CONFIG
    elif func == "patch-crm-polling-interval":
        body = { "openconfig-system-crm:polling-interval": int(data) }
        path = cc.Path(uri_conf + '/config/polling-interval')

    elif func == "patch-crm-thresholds-acl-group-counter-type":
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/acl/group/counter/config/type')
    elif func == "patch-crm-thresholds-acl-group-counter-high":
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/acl/group/counter/config/high')
    elif func == "patch-crm-thresholds-acl-group-counter-low":
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/acl/group/counter/config/low')

    elif func == "patch-crm-thresholds-acl-group-entry-type":
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/acl/group/entry/config/type')
    elif func == "patch-crm-thresholds-acl-group-entry-high":
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/acl/group/entry/config/high')
    elif func == "patch-crm-thresholds-acl-group-entry-low":
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/acl/group/entry/config/low')

    elif func == "patch-crm-thresholds-acl-group-type":
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/acl/group/config/type')
    elif func == "patch-crm-thresholds-acl-group-high":
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/acl/group/config/high')
    elif func == "patch-crm-thresholds-acl-group-low":
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/acl/group/config/low')

    elif func == "patch-crm-thresholds-acl-table-type":
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/acl/table/config/type')
    elif func == "patch-crm-thresholds-acl-table-high":
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/acl/table/config/high')
    elif func == "patch-crm-thresholds-acl-table-low":
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/acl/table/config/low')

    elif func == "patch-crm-thresholds-dnat-type":
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/dnat/config/type')
    elif func == "patch-crm-thresholds-dnat-high":
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/dnat/config/high')
    elif func == "patch-crm-thresholds-dnat-low":
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/dnat/config/low')

    elif func == "patch-crm-thresholds-snat-type":
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/snat/config/type')
    elif func == "patch-crm-thresholds-snat-high":
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/snat/config/high')
    elif func == "patch-crm-thresholds-snat-low":
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/snat/config/low')

    elif func == "patch-crm-thresholds-fdb-type":
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/fdb/config/type')
    elif func == "patch-crm-thresholds-fdb-high":
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/fdb/config/high')
    elif func == "patch-crm-thresholds-fdb-low":
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/fdb/config/low')

    elif func == "patch-crm-thresholds-ipmc-type":
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/ipmc/config/type')
    elif func == "patch-crm-thresholds-ipmc-high":
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipmc/config/high')
    elif func == "patch-crm-thresholds-ipmc-low":
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipmc/config/low')

    elif func == "patch-crm-thresholds-ipv4-neighbor-type":
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/ipv4/neighbor/config/type')
    elif func == "patch-crm-thresholds-ipv4-neighbor-high":
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv4/neighbor/config/high')
    elif func == "patch-crm-thresholds-ipv4-neighbor-low":
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv4/neighbor/config/low')

    elif func == "patch-crm-thresholds-ipv4-nexthop-type":
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/ipv4/nexthop/config/type')
    elif func == "patch-crm-thresholds-ipv4-nexthop-high":
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv4/nexthop/config/high')
    elif func == "patch-crm-thresholds-ipv4-nexthop-low":
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv4/nexthop/config/low')

    elif func == "patch-crm-thresholds-ipv4-route-type":
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/ipv4/route/config/type')
    elif func == "patch-crm-thresholds-ipv4-route-high":
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv4/route/config/high')
    elif func == "patch-crm-thresholds-ipv4-route-low":
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv4/route/config/low')

    elif func == "patch-crm-thresholds-ipv6-neighbor-type":
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/ipv6/neighbor/config/type')
    elif func == "patch-crm-thresholds-ipv6-neighbor-high":
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv6/neighbor/config/high')
    elif func == "patch-crm-thresholds-ipv6-neighbor-low":
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv6/neighbor/config/low')

    elif func == "patch-crm-thresholds-ipv6-nexthop-type":
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/ipv6/nexthop/config/type')
    elif func == "patch-crm-thresholds-ipv6-nexthop-high":
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv6/nexthop/config/high')
    elif func == "patch-crm-thresholds-ipv6-nexthop-low":
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv6/nexthop/config/low')

    elif func == "patch-crm-thresholds-ipv6-route-type":
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/ipv6/route/config/type')
    elif func == "patch-crm-thresholds-ipv6-route-high":
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv6/route/config/high')
    elif func == "patch-crm-thresholds-ipv6-route-low":
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv6/route/config/low')

    elif func == "patch-crm-thresholds-nexthop-group-member-type":
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/nexthop/group-member/config/type')
    elif func == "patch-crm-thresholds-nexthop-group-member-high":
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/nexthop/group-member/config/high')
    elif func == "patch-crm-thresholds-nexthop-group-member-low":
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/nexthop/group-member/config/low')

    elif func == "patch-crm-thresholds-nexthop-group-object-type":
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/nexthop/group-object/config/type')
    elif func == "patch-crm-thresholds-nexthop-group-object-high":
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/nexthop/group-object/config/high')
    elif func == "patch-crm-thresholds-nexthop-group-object-low":
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/nexthop/group-object/config/low')

    elif func == "patch-crm-thresholds-all-type":
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/acl/group/counter/config/type')
        aa.patch(path, body)
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/acl/group/entry/config/type')
        aa.patch(path, body)
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/acl/group/config/type')
        aa.patch(path, body)
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/acl/table/config/type')
        aa.patch(path, body)
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/dnat/config/type')
        aa.patch(path, body)
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/snat/config/type')
        aa.patch(path, body)
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/fdb/config/type')
        aa.patch(path, body)
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/ipmc/config/type')
        aa.patch(path, body)
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/ipv4/neighbor/config/type')
        aa.patch(path, body)
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/ipv4/nexthop/config/type')
        aa.patch(path, body)
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/ipv4/route/config/type')
        aa.patch(path, body)
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/ipv6/neighbor/config/type')
        aa.patch(path, body)
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/ipv6/nexthop/config/type')
        aa.patch(path, body)
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/ipv6/route/config/type')
        aa.patch(path, body)
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/nexthop/group-member/config/type')
        aa.patch(path, body)
        body = { "openconfig-system-crm:type": data.upper() }
        path = cc.Path(uri_conf + '/threshold/nexthop/group-object/config/type')
        aa.patch(path, body)
        return

    elif func == "patch-crm-thresholds-all-high":
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/acl/group/counter/config/high')
        aa.patch(path, body)
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/acl/group/entry/config/high')
        aa.patch(path, body)
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/acl/group/config/high')
        aa.patch(path, body)
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/acl/table/config/high')
        aa.patch(path, body)
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/dnat/config/high')
        aa.patch(path, body)
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/snat/config/high')
        aa.patch(path, body)
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/fdb/config/high')
        aa.patch(path, body)
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipmc/config/high')
        aa.patch(path, body)
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv4/neighbor/config/high')
        aa.patch(path, body)
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv4/nexthop/config/high')
        aa.patch(path, body)
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv4/route/config/high')
        aa.patch(path, body)
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv6/neighbor/config/high')
        aa.patch(path, body)
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv6/nexthop/config/high')
        aa.patch(path, body)
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv6/route/config/high')
        aa.patch(path, body)
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/nexthop/group-member/config/high')
        aa.patch(path, body)
        body = { "openconfig-system-crm:high": int(data) }
        path = cc.Path(uri_conf + '/threshold/nexthop/group-object/config/high')
        aa.patch(path, body)
        return

    elif func == "patch-crm-thresholds-all-low":
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/acl/group/counter/config/low')
        aa.patch(path, body)
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/acl/group/entry/config/low')
        aa.patch(path, body)
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/acl/group/config/low')
        aa.patch(path, body)
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/acl/table/config/low')
        aa.patch(path, body)
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/dnat/config/low')
        aa.patch(path, body)
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/snat/config/low')
        aa.patch(path, body)
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/fdb/config/low')
        aa.patch(path, body)
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipmc/config/low')
        aa.patch(path, body)
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv4/neighbor/config/low')
        aa.patch(path, body)
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv4/nexthop/config/low')
        aa.patch(path, body)
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv4/route/config/low')
        aa.patch(path, body)
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv6/neighbor/config/low')
        aa.patch(path, body)
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv6/nexthop/config/low')
        aa.patch(path, body)
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/ipv6/route/config/low')
        aa.patch(path, body)
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/nexthop/group-member/config/low')
        aa.patch(path, body)
        body = { "openconfig-system-crm:low": int(data) }
        path = cc.Path(uri_conf + '/threshold/nexthop/group-object/config/low')
        aa.patch(path, body)
        return

    # DELETE CONFIG
    elif func == "no-crm-all":
        path = cc.Path(uri_conf + '/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/acl/group/counter/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/acl/group/entry/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/acl/group/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/acl/table/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/dnat/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/snat/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/ipmc/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/fdb/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/ipv4/neighbor/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/ipv4/nexthop/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/ipv4/route/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/ipv6/neighbor/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/ipv6/nexthop/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/ipv6/route/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/nexthop/group-member/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/nexthop/group-object/config')
        aa.delete(path)
        return

    elif func == "no-crm-thresholds-all":
        path = cc.Path(uri_conf + '/threshold/acl/group/counter/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/acl/group/entry/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/acl/group/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/acl/table/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/dnat/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/snat/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/ipmc/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/fdb/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/ipv4/neighbor/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/ipv4/nexthop/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/ipv4/route/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/ipv6/neighbor/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/ipv6/nexthop/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/ipv6/route/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/nexthop/group-member/config')
        aa.delete(path)
        path = cc.Path(uri_conf + '/threshold/nexthop/group-object/config')
        aa.delete(path)
        return

    elif func == "no-crm-polling-interval":
        path = cc.Path(uri_conf + '/config/polling-interval')

    elif func == "no-crm-thresholds-acl-group-counter-type":
        path = cc.Path(uri_conf + '/threshold/acl/group/counter/config/type')
    elif func == "no-crm-thresholds-acl-group-counter-high":
        path = cc.Path(uri_conf + '/threshold/acl/group/counter/config/high')
    elif func == "no-crm-thresholds-acl-group-counter-low":
        path = cc.Path(uri_conf + '/threshold/acl/group/counter/config/low')

    elif func == "no-crm-thresholds-acl-group-entry-type":
        path = cc.Path(uri_conf + '/threshold/acl/group/entry/config/type')
    elif func == "no-crm-thresholds-acl-group-entry-high":
        path = cc.Path(uri_conf + '/threshold/acl/group/entry/config/high')
    elif func == "no-crm-thresholds-acl-group-entry-low":
        path = cc.Path(uri_conf + '/threshold/acl/group/entry/config/low')

    elif func == "no-crm-thresholds-acl-group-type":
        path = cc.Path(uri_conf + '/threshold/acl/group/config/type')
    elif func == "no-crm-thresholds-acl-group-high":
        path = cc.Path(uri_conf + '/threshold/acl/group/config/high')
    elif func == "no-crm-thresholds-acl-group-low":
        path = cc.Path(uri_conf + '/threshold/acl/group/config/low')

    elif func == "no-crm-thresholds-acl-table-type":
        path = cc.Path(uri_conf + '/threshold/acl/table/config/type')
    elif func == "no-crm-thresholds-acl-table-high":
        path = cc.Path(uri_conf + '/threshold/acl/table/config/high')
    elif func == "no-crm-thresholds-acl-table-low":
        path = cc.Path(uri_conf + '/threshold/acl/table/config/low')

    elif func == "no-crm-thresholds-dnat-type":
        path = cc.Path(uri_conf + '/threshold/dnat/config/type')
    elif func == "no-crm-thresholds-dnat-high":
        path = cc.Path(uri_conf + '/threshold/dnat/config/high')
    elif func == "no-crm-thresholds-dnat-low":
        path = cc.Path(uri_conf + '/threshold/dnat/config/low')

    elif func == "no-crm-thresholds-snat-type":
        path = cc.Path(uri_conf + '/threshold/snat/config/type')
    elif func == "no-crm-thresholds-snat-high":
        path = cc.Path(uri_conf + '/threshold/snat/config/high')
    elif func == "no-crm-thresholds-snat-low":
        path = cc.Path(uri_conf + '/threshold/snat/config/low')

    elif func == "no-crm-thresholds-fdb-type":
        path = cc.Path(uri_conf + '/threshold/fdb/config/type')
    elif func == "no-crm-thresholds-fdb-high":
        path = cc.Path(uri_conf + '/threshold/fdb/config/high')
    elif func == "no-crm-thresholds-fdb-low":
        path = cc.Path(uri_conf + '/threshold/fdb/config/low')

    elif func == "no-crm-thresholds-ipmc-type":
        path = cc.Path(uri_conf + '/threshold/ipmc/config/type')
    elif func == "no-crm-thresholds-ipmc-high":
        path = cc.Path(uri_conf + '/threshold/ipmc/config/high')
    elif func == "no-crm-thresholds-ipmc-low":
        path = cc.Path(uri_conf + '/threshold/ipmc/config/low')

    elif func == "no-crm-thresholds-ipv4-neighbor-type":
        path = cc.Path(uri_conf + '/threshold/ipv4/neighbor/config/type')
    elif func == "no-crm-thresholds-ipv4-neighbor-high":
        path = cc.Path(uri_conf + '/threshold/ipv4/neighbor/config/high')
    elif func == "no-crm-thresholds-ipv4-neighbor-low":
        path = cc.Path(uri_conf + '/threshold/ipv4/neighbor/config/low')

    elif func == "no-crm-thresholds-ipv4-nexthop-type":
        path = cc.Path(uri_conf + '/threshold/ipv4/nexthop/config/type')
    elif func == "no-crm-thresholds-ipv4-nexthop-high":
        path = cc.Path(uri_conf + '/threshold/ipv4/nexthop/config/high')
    elif func == "no-crm-thresholds-ipv4-nexthop-low":
        path = cc.Path(uri_conf + '/threshold/ipv4/nexthop/config/low')

    elif func == "no-crm-thresholds-ipv4-route-type":
        path = cc.Path(uri_conf + '/threshold/ipv4/route/config/type')
    elif func == "no-crm-thresholds-ipv4-route-high":
        path = cc.Path(uri_conf + '/threshold/ipv4/route/config/high')
    elif func == "no-crm-thresholds-ipv4-route-low":
        path = cc.Path(uri_conf + '/threshold/ipv4/route/config/low')

    elif func == "no-crm-thresholds-ipv6-neighbor-type":
        path = cc.Path(uri_conf + '/threshold/ipv6/neighbor/config/type')
    elif func == "no-crm-thresholds-ipv6-neighbor-high":
        path = cc.Path(uri_conf + '/threshold/ipv6/neighbor/config/high')
    elif func == "no-crm-thresholds-ipv6-neighbor-low":
        path = cc.Path(uri_conf + '/threshold/ipv6/neighbor/config/low')

    elif func == "no-crm-thresholds-ipv6-nexthop-type":
        path = cc.Path(uri_conf + '/threshold/ipv6/nexthop/config/type')
    elif func == "no-crm-thresholds-ipv6-nexthop-high":
        path = cc.Path(uri_conf + '/threshold/ipv6/nexthop/config/high')
    elif func == "no-crm-thresholds-ipv6-nexthop-low":
        path = cc.Path(uri_conf + '/threshold/ipv6/nexthop/config/low')

    elif func == "no-crm-thresholds-ipv6-route-type":
        path = cc.Path(uri_conf + '/threshold/ipv6/route/config/type')
    elif func == "no-crm-thresholds-ipv6-route-high":
        path = cc.Path(uri_conf + '/threshold/ipv6/route/config/high')
    elif func == "no-crm-thresholds-ipv6-route-low":
        path = cc.Path(uri_conf + '/threshold/ipv6/route/config/low')

    elif func == "no-crm-thresholds-nexthop-group-member-type":
        path = cc.Path(uri_conf + '/threshold/nexthop/group-member/config/type')
    elif func == "no-crm-thresholds-nexthop-group-member-high":
        path = cc.Path(uri_conf + '/threshold/nexthop/group-member/config/high')
    elif func == "no-crm-thresholds-nexthop-group-member-low":
        path = cc.Path(uri_conf + '/threshold/nexthop/group-member/config/low')

    elif func == "no-crm-thresholds-nexthop-group-object-type":
        path = cc.Path(uri_conf + '/threshold/nexthop/group-object/config/type')
    elif func == "no-crm-thresholds-nexthop-group-object-high":
        path = cc.Path(uri_conf + '/threshold/nexthop/group-object/config/high')
    elif func == "no-crm-thresholds-nexthop-group-object-low":
        path = cc.Path(uri_conf + '/threshold/nexthop/group-object/config/low')

    # SHOW ACL_GROUP_STATS
    elif func == "show-crm-resources-acl-group":
        tmpl = "show_crm_resources_acl_group.j2"
        path = cc.Path(uri_stat_acl)
    elif func == "show-crm-resources-acl-table":
        tmpl = "show_crm_resources_acl_table.j2"
        path = cc.Path(uri_stat_acl)

    # SHOW STATS
    elif func == "show-crm-resources-dnat":
        tmpl = "show_crm_resources_dnat.j2"
        path = cc.Path(uri_stat)
    elif func == "show-crm-resources-fdb":
        tmpl = "show_crm_resources_fdb.j2"
        path = cc.Path(uri_stat)
    elif func == "show-crm-resources-ipmc":
        tmpl = "show_crm_resources_ipmc.j2"
        path = cc.Path(uri_stat)
    elif func == "show-crm-resources-ipv4-neighbor":
        tmpl = "show_crm_resources_ipv4_neighbor.j2"
        path = cc.Path(uri_stat)
    elif func == "show-crm-resources-ipv4-nexthop":
        tmpl = "show_crm_resources_ipv4_nexthop.j2"
        path = cc.Path(uri_stat)
    elif func == "show-crm-resources-ipv4-route":
        tmpl = "show_crm_resources_ipv4_route.j2"
        path = cc.Path(uri_stat)
    elif func == "show-crm-resources-ipv6-neighbor":
        tmpl = "show_crm_resources_ipv6_neighbor.j2"
        path = cc.Path(uri_stat)
    elif func == "show-crm-resources-ipv6-nexthop":
        tmpl = "show_crm_resources_ipv6_nexthop.j2"
        path = cc.Path(uri_stat)
    elif func == "show-crm-resources-ipv6-route":
        tmpl = "show_crm_resources_ipv6_route.j2"
        path = cc.Path(uri_stat)
    elif func == "show-crm-resources-nexthop-group-member":
        tmpl = "show_crm_resources_nexthop_group_member.j2"
        path = cc.Path(uri_stat)
    elif func == "show-crm-resources-nexthop-group-object":
        tmpl = "show_crm_resources_nexthop_group_object.j2"
        path = cc.Path(uri_stat)
    elif func == "show-crm-resources-snat":
        tmpl = "show_crm_resources_snat.j2"
        path = cc.Path(uri_stat)
    elif func == "show-crm-resources-all":
        stat = {}
        tmpl = "show_crm_resources_all.j2"
        path = cc.Path(uri_stat)
        resp = aa.get(path)
        if (resp is not None) and resp.ok() and 'openconfig-system-crm:statistics' in resp.content:
            stat.update(resp.content['openconfig-system-crm:statistics'])
        path = cc.Path(uri_stat_acl)
        resp = aa.get(path)
        if (resp is not None) and resp.ok() and 'openconfig-system-crm:acl-statistics' in resp.content:
            stat.update(resp.content['openconfig-system-crm:acl-statistics'])
        show_cli_output(tmpl, stat)
        return

    if path == None:
        return

    op = func.split('-')[0]
    if (op == 'show'):
        resp = aa.get(path)
    elif (op == 'no'):
        resp = aa.delete(path)
    elif (op == 'patch') and (body is not None):
        resp = aa.patch(path, body)
    else:
        resp = None
    if (resp is not None) and resp.ok():
        if tmpl is not None:
            show_cli_output(tmpl, resp.content)
    else:
        print resp.error_message()

if __name__ == '__main__':
    pipestr().write(sys.argv)
    # pdb.set_trace()
    run(sys.argv[1], sys.argv[2:])
