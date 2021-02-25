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
def show_switch_resource_flow_scale_entry(render_tables):
	cmd = "drop-monitor flows "

	entries =  render_tables.get('sonic-switch-resource:sonic-switch-resource/SWITCH_RESOURCE_TABLE/SWITCH_RESOURCE_TABLE_LIST')
        if entries is None:
	    return 'CB_SUCCESS', ''

	if entries['flows'] == 'NONE':
            cmd = cmd + "none"
        elif entries['flows'] == 'MIN' :
            cmd = cmd + "min"

	if entries['routes'] == 'MAX':
            cmd = cmd + "max"	

        return 'CB_SUCCESS', cmd
