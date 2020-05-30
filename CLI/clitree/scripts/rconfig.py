
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
import sys
import truthtbl
import copy
import itertools

oxpathlist = []
mxpathlist = []
swxpathlist = []
swmxpathlist = []
swlist = []
combswlst = []
nodestrlst=[]
field1lst=[]
updateswlst =[]
nodestr=''
CMDSEPARATOR=';;'
MULTICMDSEP='||'

class cmdparse(object):
    def __init__(self):
        self.value = ''
        self.present = False
        self.subdirs = {}
        self.cmdstr = ''
##
# @brief Calling this function would create a map object by calling
#        a constructor
# @return The object created on calling the constructor
def cmd_string_parse_init():
    return cmdparse()

##
# @brief Calling this function would destroy the map object, by
#        calling a destructor
# @param counts Map object to be destroyed
def cmd_string_parse_exit(counts):
    del counts

##
# @brief This function creates a tree with, against the command string
# @param counts Is the map object on which the tree is built
# @param cmdstr Is the command string against which a tree is built
def build_tree(counts, cmdstr):
    lines = []
    global oxpathlist
    global mxpathlist
    global swxpathlist

    for cmd in cmdstr.split(CMDSEPARATOR):
        lines.append(cmd)

    for p in lines:
        parts = p.split('|')
        branch = counts
        for part in parts:
            alist = part.split('--')
            klist = branch.subdirs.keys()
            found = 0
            if len(klist) != 0:
                for key in klist:
                    if alist[0] == key.split(".", 1)[1]:
                        branch = branch.subdirs.setdefault(key, cmd_string_parse_init())
                        found = 1
                        break
            if found == 0:
                branch = branch.subdirs.setdefault(str(len(klist))+'.'+alist[0]
                                                  , cmd_string_parse_init())
                if str(alist[0].split('##')[4])=='O':
                    oxpathlist.append(alist[0])
                else:
                    mxpathlist.append(alist[0])

            if len(alist)>1:
                branch.value = alist[1]
                if str(alist[1].split('##')[4])=='O':
                    oxpathlist.append(alist[0])
                else:
                    mxpathlist.append(alist[0])

##
# @brief This function creates a tree with, against the command string
# @param counts Is the map object on which the tree is built
# @param cmdstr Is the command string against which a tree is built
def build_tree_sw(counts, cmdstr):
    lines = []
    global swmxpathlist
    global swxpathlist

    for cmd in cmdstr.split(CMDSEPARATOR):
        lines.append(cmd)

    for p in lines:
        parts = p.split('|')
        branch = counts
        for part in parts:
            alist = part.split('--')
            klist = branch.subdirs.keys()
            found = 0
            if len(klist) != 0:
                for key in klist:
                    if alist[0] == key.split(".", 1)[1]:
                        branch = branch.subdirs.setdefault(key, cmd_string_parse_init())
                        found = 1
                        break
            if found == 0:
                branch = branch.subdirs.setdefault(str(len(klist))+'.'+alist[0]
                                                  , cmd_string_parse_init())
                if alist[0].split('##')[3] == "sw":
                    swxpathlist.append(alist[0])
                else:
                    swmxpathlist.append(alist[0])

            if len(alist)>1:
                branch.value = alist[1]
                if alist[1].split('##')[3] == "sw":
                    swxpathlist.append(alist[0])
                else:
                    swmxpathlist.append(alist[0])

##
# @brief This function generates a possible command from the
#        tree built using build_tree
# @param stats Is the map object on which the tree is built
def print_cmd(stats, allNP):
    global nodestr
    if allNP is False:
        for key in sorted(stats.subdirs.keys()):
            if stats.subdirs[key].present is False:
                # If Optional update as "NP"
                if (key.split(".",1)[1]).split('##')[4] == 'O':
                    if nodestr != '':
                        nodestr += '|'
                    nodestr += key.split(".",1)[1]+'##'+'NP'
                if (key.split(".",1)[1]).split('##')[1] == '':
                    print_cmd(stats.subdirs[key], True)
                continue
            if nodestr != '':
                nodestr += '|'
            nodestr += key.split(".",1)[1]+'##'+'P'
            print_cmd(stats.subdirs[key], allNP)
    else:
        # All node below this should have yang_name
        # not present in the XML data requested for
        for key in sorted(stats.subdirs.keys()):
            if nodestr != '':
                nodestr += '|'
            nodestr += key.split(".",1)[1]+'##'+'NP'
            print_cmd(stats.subdirs[key], allNP)



##
# @brief This function generates a possible command from the
#        tree built using build_tree
# @param stats Is the map object on which the tree is built
def print_cmd_sw(stats):
    global nodestrlst
    global field1lst

    for key in sorted(stats.subdirs.keys()):
        if stats.subdirs[key].present is False:
            continue
        if (key.split(".",1)[1]).split('##')[4] == 'O':
            subkeycount = 0
            keylst = (stats.subdirs[key]).subdirs.keys()
            if len(keylst) != 0:
                for subkey in sorted(keylst):
                    if (stats.subdirs[key]).subdirs[subkey].present is False:
                        subkeycount += 1
            if len(keylst) != 0:
                if subkeycount == len(keylst):
                    continue
        nodestrlst.append(key.split(".",1)[1])
        print_cmd_sw(stats.subdirs[key])
        nodestrlst.pop()
    if len(nodestrlst) != 0:
        field1lst.append('|'.join(nodestrlst))

##
# @brief This function creates a combination of "sw" commands
# @param stats Is the map object on which the tree is built
def buildswlst(stats):
    global swlist
    global combswlst
    for key in sorted(stats.subdirs.keys()):
        # Push the switch nodes into the tmplst
        if (key.split(".",1)[1]).split('##')[3] == "sw":
            swlist.append(key.split(".",1)[1])
        buildswlst(stats.subdirs[key])
        # Pop the switch nodes out of the tmplst
        if (key.split(".",1)[1]).split('##')[3] == "sw":
            swlist.pop()
    if len(stats.subdirs.keys()) == 0:
        combswlst.append(list(swlist))


def print_tree(stats, indent=''):
    for key in sorted(stats.subdirs.keys()):
        print(indent + str(key.split(".", 1)[1]) + ':' + str(stats.subdirs[key].value) + ':' + str(stats.subdirs[key].present))
        print_tree(stats.subdirs[key], indent + ' ')

##
# @brief This function resets the presence status of all
#        the visited nodes in the tree
# @param stats Is the map object on which the tree is built
def reset_present(stats):
    for key in sorted(stats.subdirs.keys()):
        stats.subdirs[key].present = False
        reset_present(stats.subdirs[key])
##
# @brief This function generates a possible command from the
#        tree against the list which contains valid xpath
# @param stats Is the map object on which the tree is built
# @param alist Is the list containing the valid xpath
def update_present(stats, alist):
    for key in sorted(stats.subdirs.keys()):
        xpath_str = str(key.split(".",1)[1])
        if  stats.subdirs[key].present is False:
            if xpath_str not in alist:
                stats.subdirs[key].present = False
            else:
                stats.subdirs[key].present = True
        update_present(stats.subdirs[key], alist)

def update_present_sw(stats):
    global updateswlst
    for key in sorted(stats.subdirs.keys()):
        if  stats.subdirs[key].present is False:
            if len(updateswlst)!=0:
                if key != updateswlst[0]:
                    stats.subdirs[key].present = False
                else:
                    updateswlst.pop(0)
                    stats.subdirs[key].present = True
        update_present_sw(stats.subdirs[key])

def get_cmd_str(db_line):
    return db_line.split(':::')[0]

##
# @brief This function is invoked to create a possible list of commands
#        generated by the field1 in a line in DB.txt file
# @param dbline Represents a line in DB.txt file
# @return A list containg the possible list of commands to be applied
#         the xml data
def rconfig_main(dbline):
    global oxpathlist
    global mxpathlist
    global nodestr
    cmdstr = get_cmd_str(dbline)

    counts = {}
    counts = cmd_string_parse_init()
    build_tree(counts, cmdstr)
    #print "MAN lst", len(mxpathlist)
    #print "OPT lst", len(oxpathlist)
    mxpathlist = list(set(mxpathlist))
    oxpathlist = list(set(oxpathlist))
    cmdlist = []

    if oxpathlist == []:
        update_present(counts, mxpathlist)
        nodestr = ''
        print_cmd(counts, False)
        reset_present(counts)
        cmdlist.append(nodestr)
    else:
        for comblst in truthtbl.combtable(oxpathlist):
            update_present(counts, mxpathlist+comblst)
            nodestr = ''
            print_cmd(counts, False)
            reset_present(counts)
            cmdlist.append(nodestr)

    # Setting global variables to default state
    mxpathlist = []
    oxpathlist = []
    nodestr = ''
    cmd_string_parse_exit(counts)
    return list(set(cmdlist))

def t_getswcmd(stats, indent=''):
    reversekey_l = reversed(sorted(stats.subdirs.keys()))
    for key in reversekey_l:
        print(indent + str(key.split(".", 1)[1])+':'+str(stats.subdirs[key].value)+':'+str(stats.subdirs[key].present))
        t_getswcmd(stats.subdirs[key],indent + ' ')

def getswcmd(stats, combcmdstr):
    key_l = sorted(stats.subdirs.keys())
    reversekey_l = key_l[::-1]
    atleastonce_n = False
    for key in reversekey_l:
        atleastonce_n = True
        sw_n = False
        if (key.split(".",1)[1]).split('##')[3] == 'sw':
            sw_n = True

        im_rit_node_index = key_l.index(key)+1
        im_rit_node_n = ''
        if im_rit_node_index < len(key_l):
            im_rit_node_n=key_l[im_rit_node_index]

        once_n = False
        for key_s in key_l[im_rit_node_index:len(key_l)]:
            if '##sw##' not in key_s:
                once_n = True
                break
        im_non_sw_n = key_l[key_l.index(key_s)] if once_n == True else ''

        # Below steps to be followed
        # 1. Check if the curnode is 'sw' or 'non-sw' node
        #    If 'sw', goto step 3
        #    If 'non-sw' goto step 2
        # 2. Check if the immediate right node is a 'sw' or 'non-sw' or 'last'
        #    Current node is 'non-sw'
        #    if im-rit-node is 'sw'
        #       combcmdstr_cur = concat(';') cmdstr of succesive 'sw' nodes
        #    if im-rit-node is 'non-sw'
        #       combcmdstr_cur = cmdstr of 'the non-sw' node
        #    if im-rit-node is 'no-node'
        #       combcmdstr_cur = comcmdstr inherited from parent node
        # 3. Get the immediate 'non-sw' or 'last'
        #    Current node is 'sw'
        #    if 'non-sw' node
        #       combcmdstr_cur = cmdstr of 'the non-sw' node
        #    if 'last' node
        #       combcmdstr_cur = comcmdstr inherited from parent node
        if sw_n == False:
            # Current node is a non switch node
            if ''==im_rit_node_n:
                combcmdstr_cur = combcmdstr
            elif '##sw##' in im_rit_node_n:
                curcmdstrlst = []
                for key_s in key_l[key_l.index(im_rit_node_n):len(key_l)]:
                    if '##sw##' not in key_s:
                        break
                    curcmdstrlst.append(stats.subdirs[key_s].cmdstr)
                combcmdstr_cur = MULTICMDSEP.join(curcmdstrlst)
            else:
                combcmdstr_cur = stats.subdirs[im_rit_node_n].cmdstr
        else:
            # Current node is a switch node
            if ''==im_non_sw_n:
                combcmdstr_cur = combcmdstr
            else:
                combcmdstr_cur = stats.subdirs[im_non_sw_n].cmdstr
        #print "Key:",key,"combcmdstr_cur:",combcmdstr_cur
        r_combcmdstr = getswcmd(stats.subdirs[key], combcmdstr_cur)
        #print "Key:",key, "r_combcmdstr:",r_combcmdstr
        # Update the 'cmdstr' for the current node, below steps to be followed
        stats.subdirs[key].cmdstr = (MULTICMDSEP.join(['|'.join([key,s]) for s in r_combcmdstr.split(MULTICMDSEP)])).rstrip('|')

    # There are subnodes under a particular node
    if atleastonce_n == True:
        # If the First Node branched out from the parent is 'non-sw'
        #     combcmdstr = cmdstr of that node
        # If the First Node branched out from the parent is 'sw'
        #     combcmdstr = concat(';') cmdstr of succesive 'sw' nodes
        if '##sw##' in key_l[0]:
            curcmdstrlst = []
            for key_s in key_l:
                if '##sw##' not in key_s:
                    break
                curcmdstrlst.append(stats.subdirs[key_s].cmdstr)
            combcmdstr = MULTICMDSEP.join(curcmdstrlst)
        else:
            combcmdstr = stats.subdirs[key_l[0]].cmdstr
    return combcmdstr

def rconfigsw_main(db_line):
    global field1lst
    global updateswlst
    global MULTICMDSEP

    cmdstr = get_cmd_str(db_line)
    counts = {}
    counts = cmd_string_parse_init()
    #print ("dbline %s" % db_line) 
    build_tree_sw(counts, cmdstr)

    cmdlist = []
    cmd_list_t = getswcmd(counts, '').split(MULTICMDSEP)
    for cmd in cmd_list_t:
        #print cmd
        field1lst = []
        updateswlst = cmd.split('|')

        update_present_sw(counts)
        print_cmd_sw(counts)

        reset_present(counts)
        cmdlist.append(CMDSEPARATOR.join(field1lst))
    cmd_string_parse_exit(counts)
    return list(cmdlist)
