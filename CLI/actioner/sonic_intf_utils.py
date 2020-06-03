
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

import re

def name_to_int_val(ifName):
    val = 0
    if ifName.startswith('Eth'):
        tk = ifName.split('.')
        plist = re.findall(r'\d+', tk[0])
        val = 0
        if len(plist) == 1:  #ex: Ethernet40
           val = int(plist[0]) * 10000
        elif len(plist) == 2:  #ex: Eth1/5
           val= int(plist[0]+plist[1].zfill(3)+'000000')
        elif len(plist) == 3:  #ex: Eth1/5/2
           val= int(plist[0]+plist[1].zfill(3)+plist[2].zfill(2)+'0000')

        if len(tk) == 2:   #ex: 2345 in Eth1/1.2345
           val += int(tk[1])
    elif ifName.startswith('PortChannel'):
        val = 2000000000 + int(ifName[11:])
    elif ifName.startswith('Vlan'):
        val = 3000000000 + int(ifName[4:])

    return val

