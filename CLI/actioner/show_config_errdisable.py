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



def show_config_errdisable_cause(render_tables):
    enabled_cause_list = []

    if 'sonic-errdisable:sonic-errdisable/ERRDISABLE/ERRDISABLE_LIST' in render_tables:
        if len(render_tables['sonic-errdisable:sonic-errdisable/ERRDISABLE/ERRDISABLE_LIST']) == 1:
            for cause in render_tables['sonic-errdisable:sonic-errdisable/ERRDISABLE/ERRDISABLE_LIST'][0].keys():
                if render_tables['sonic-errdisable:sonic-errdisable/ERRDISABLE/ERRDISABLE_LIST'][0][cause] == 'enabled':
                    enabled_cause_list.append(cause)

    cmd_str = ''
    cmd_prfx = 'errdisable recovery cause '
    for cause in enabled_cause_list:
        cmd_str = cmd_str + ";" + cmd_prfx + cause

    return 'CB_SUCCESS', cmd_str


