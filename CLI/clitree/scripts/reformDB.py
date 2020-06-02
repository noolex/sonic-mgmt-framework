#!/usr/bin/env python
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
import rconfig
import sys
pretagxpath="/rpc-reply/data"
CMDSEPERATOR=';;'
CMDCOMBSEPERATOR=';;;'
def prependcrxpathstr(lst):
     global pretagxpath
     i = 0
     tmplst = list(lst)
     for f2cr in tmplst:
         f2crlst = f2cr.split('=')
         f2crlst[0]=pretagxpath+f2crlst[0]
         f2crlst[1]=pretagxpath+f2crlst[1]
         tmplst[i]='='.join(f2crlst)
         i+=1
     return tmplst
##
# @brief This function gets a list of xpath strings and prepends each
#        string with '/rpc-reply/data'
# @param lst The list of xpath strings,
#        format: [<xpath-key1>,<xpath-key2>]
# @return tmplst The list contains each string prepended with the
#                '/rpc-reply/data'
#        format: [/rpc-reply/data/<xpath-key1>,/rpc-reply/data/<xpath-key2>]
def prependxpathstr(lst):
     global pretagxpath
     i = 0
     tmplst = list(lst)
     for f2cr in tmplst:
         f2cr=pretagxpath+f2cr
         tmplst[i]=f2cr
         i+=1
     return tmplst

##
# @brief This function gets a list of xpath strings which are prepended with
#        the string '/rpc-reply/data', and concatenate all the strings to form
#        a new field2
# @param keylst The list of xpath strings
#        format: [/rpc-reply/data/<xpath-key1>,/rpc-reply/data/<xpath-key2>]
# @param crlst The list of cross referenced xpath strings
#        format: [/rpc-reply/data/<cr-xpath>]
# @return f2str Returns a concatenated output of all strings in keylst and
#               crlst
#        format: "/rpc-reply/data/<xpath-key1>,/rpc-reply/data/<xpath-key2>,..;
#                cr:/rpc-reply/data/<cr-xpath>"
def getfield2str(keylst, crlst):
    f2str = ""
    if keylst!=[]:
        f2str = ",".join(keylst)
        if crlst!=[]:
            f2str +=";"
            f2str = f2str + ",".join(crlst)
    return f2str

def f2processing(field2):
    # f2lstkey = [<xpath-key1>,<xpath-key2>]
    f2lstkey = (field2.split(';')[0]).split(',')
    #f2lstkey = [/rpc-reply/data/<xpath-key1>,/rpc-reply/data/<xpath-key2>]
    f2lstkey = prependxpathstr(f2lstkey)
    # process cross-ref alone
    f2lstcr =[]
    if len(field2.split(';'))>1:
        # f2lstcr = [<cr-xapth>]
        f2lstcr = (field2.split(';')[1]).split(',')
        # f2lstcr = [/rpc/reply/<cr-xpath>]
        f2lstcr = prependcrxpathstr(f2lstcr)

    # field2 format is "/rpc-reply/data/<xpath-key1>,
    #/rpc-reply/data/<xpath-key2>,...;cr:/rpc-reply/data/<cr-xpath>"
    return getfield2str(f2lstkey, f2lstcr)

##
# @brief This function gets field1 or the command field of the DB line
#        preprocess all xpath strings in it and prepend all xpath strings
#        '/rpc-reply/data'
# @param field1 Represents the field1 string in a DB line.
# @return Returns a processed field1 or cmd field string in a DB line, where
#         all xpath strings are prepended with '/rpc-reply/data'
def preprocessfield1str(field1):
    #field1 process
    f1lst = field1.split(CMDSEPERATOR)
    k = 0
    for f1 in f1lst:
        elemlst = f1.split('|')
        j = 0
        for elem in elemlst:
            sublst = elem.split('--')
            i = 0
            for sub in sublst:
                nodelst = sub.split('##')
                #print nodelst
                val_n = nodelst[0]
                xpath_n = nodelst[1]
                key_n = nodelst[2]
                sw_n = nodelst[3]
                mode_n = nodelst[4]
                if xpath_n == "":
                    if key_n != "":
                        newlst = []
                        newlst.append(key_n)
                        key_n = f2processing(key_n)
                    sublst[i] = val_n+'##'+xpath_n+'##'+key_n+'##'+sw_n+'##'+mode_n
                else:
                    newlst = []
                    newlst.append(xpath_n)
                    xpath_n = (prependxpathstr(newlst))[0]
                    if key_n != "":
                        newlst = []
                        newlst.append(key_n)
                        key_n = f2processing(key_n)
                    sublst[i] = val_n+'##'+xpath_n+'##'+key_n+'##'+sw_n+'##'+mode_n
                i += 1
            elemlst[j] = sublst[0]
            if i == 2:
                elemlst[j] += '--'+sublst[1]
            j += 1
        f1lst[k] = ""
        for node in elemlst:
            if f1lst[k] == "":
                f1lst[k] += node
            else:
                f1lst[k] += '|'+node
        k += 1
    field1 = ""
    for f1 in f1lst:
        if field1 == "":
            field1 += f1
        else:
            field1 += CMDSEPERATOR+f1
    return field1

def linesinfile(db_file):
    fd = open(db_file, 'r')
    lines = []

    for line in fd:
        if line[-1] == "\n":
            lines.append(line[:-1])
        else:
            lines.append(line)
    fd.close()
    return lines

if __name__ == "__main__":
    if sys.argv[1] == "--help":
        print ("Usage: reformDB.py <input-DB-file-path> <output-DB-file-path>")
        sys.exit(0)

    if len(sys.argv) < 3:
        print ("Error: Missing Parameter " + os.linesep +
               "Usage: reformDB.py <input-DB-file-path> <output-DB-file-path>")
        sys.exit(0)

    # swstr:<swstr1>,<swstr2>; swstr:<swstr1>; etc
    reformedlst = []
    for db_line in linesinfile(sys.argv[1]):
        db_line_list = db_line.split(':::')
        swnodelst = rconfig.rconfigsw_main(db_line_list[0]+':::')
        cmdlst = []
        for swnode in swnodelst:
            nodestrlst = rconfig.rconfig_main(swnode+':::')
            cmdlst.append(swnode+"%%%"+CMDSEPERATOR.join(nodestrlst))
        db_line_list[0] = CMDCOMBSEPERATOR.join(cmdlst)
        reformedlst.append(":::".join(db_line_list))
    fd = open(sys.argv[2], 'w')
    fd.writelines(["%s\n" % item for item in reformedlst])
    fd.close()
