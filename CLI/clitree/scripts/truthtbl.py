###########################################################################
#
# Copyright 2020 Dell, Inc.
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
##
# @brief Creates a truthtable
# @param n possible combinations to form a truthtable 2^n
# @return None
def truthtable(n):
    if n < 1:
        return [[]]
    subtable = truthtable(n-1)
    return [row + [v] for row in subtable for v in [0,1]]

##
# @brief Creates a list of sublists, with sublists containing
#        2^n possible combinations, applied against the
#        xapthlist
# @param xpathlist List containing the optional nodes in the
#                  command
# @return List of sublists, each sublist representing 2 ^ n possible
#         combinations
def combtable(xpathlist):
    comblst = []
    for comb in truthtable(len(xpathlist)):
        i = 0
        sublst = []
        for val in comb:
            if val != 0:
                sublst.append(xpathlist[i])
            i += 1
        comblst.append(sublst)
    return comblst
