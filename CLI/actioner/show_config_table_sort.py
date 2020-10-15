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

from natsort import natsorted, ns
import logging
from show_config_utils import showrun_log
from show_config_utils import get_view_table_keys

def natsort_list(sonic_table_lst , table_path):

   
    table_keys = get_view_table_keys(table_path)

    if table_keys:
        try:
            sonic_table_lst = natsorted(sonic_table_lst,key=lambda t: t[table_keys[0][0]])
        except:
            showrun_log(logging.ERROR, "Table {} sorting failure ", table_path)
            pass
                
    return sonic_table_lst