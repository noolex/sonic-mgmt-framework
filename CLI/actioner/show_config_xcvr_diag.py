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

from natsort import natsorted

def fixup_ifname(name):
    ret = name
    if name.startswith("Ethernet"):
        ret = "Ethernet {0}".format(name[8:])
    elif name.startswith("Eth"):
        ret = "Eth {0}".format(name[3:])
    return ret

def show_xcvr_diag_ctrl(render_tables):
    data = []
    cmds = []

    # skip if render_tables is None
    if render_tables is None:
        return 'CB_SUCCESS', ''

    key = 'sonic-transceiver:sonic-transceiver/TRANSCEIVER_DIAG/TRANSCEIVER_DIAG_LIST'
    if key in render_tables:
        data = render_tables[key]
    if len(data) < 1:
        return 'CB_SUCCESS', ''

    # sort dictionary by value (i.e. config command)
    for row in natsorted(data, key=lambda x: x['ifname']):
        ifn = fixup_ifname(row['ifname'])

        # interface transceiver diagnostics loopback
        pre = 'interface transceiver diagnostics loopback'
        if row.get('lb_host_input_enabled') == 'true':
            cmds.append("{0} host-side-input {1}".format(pre, ifn))
        if row.get('lb_host_output_enabled') == 'true':
            cmds.append("{0} host-side-output {1}".format(pre, ifn))
        if row.get('lb_media_input_enabled') == 'true':
            cmds.append("{0} media-side-input {1}".format(pre, ifn))
        if row.get('lb_media_output_enabled') == 'true':
            cmds.append("{0} media-side-output {1}".format(pre, ifn))

        # interface transceiver diagnostics pattern
        pre = 'interface transceiver diagnostics pattern'
        if row.get('prbs_chk_host_enabled') == 'true':
            cmds.append("{0} checker-host {1}".format(pre, ifn))
        if row.get('prbs_chk_media_enabled') == 'true':
            cmds.append("{0} checker-media {1}".format(pre, ifn))
        if row.get('prbs_gen_host_enabled') == 'true':
            cmds.append("{0} generator-host {1}".format(pre, ifn))
        if row.get('prbs_gen_media_enabled') == 'true':
            cmds.append("{0} generator-media {1}".format(pre, ifn))

    return 'CB_SUCCESS', "\n".join(cmds)
