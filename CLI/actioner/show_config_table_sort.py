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
from collections import OrderedDict
import re
from show_config_utils import log

#  parse table path, returns dict of table key, value
def get_view_table_keys(table_path):

    table_keys_map = OrderedDict()
    for path in table_path.split('/'):
        for sub_path in path.split(','):
            match = re.search(r"(.+)={(.+)}", sub_path)
            if match is not None:
                table_keys_map.update({match.group(1):match.group(2)})

    return table_keys_map



def natsort_list(sonic_table_lst , table_path):

   
    table_keys = get_view_table_keys(table_path)

    if table_keys:
        try:
            sonic_table_lst = natsorted(sonic_table_lst,key=lambda t: t[table_keys.keys()[0]])
        except:
            log.error("Table {} sorting failure " .format(table_path))
            pass
                
    return sonic_table_lst