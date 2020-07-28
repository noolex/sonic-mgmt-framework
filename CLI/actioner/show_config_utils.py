
import logging
import logging.handlers
import collections
import re


log_format = "%(filename)s:%(funcName)s:%(message)s"
log = logging.getLogger('clish_showrun')
formatter = logging.Formatter(log_format)

#stream_handler = logging.StreamHandler()
#stream_handler.setFormatter(formatter)
#log.addHandler(stream_handler)

sh  = logging.handlers.SysLogHandler()
sh.setFormatter(formatter)
log.addHandler(sh)
log.setLevel('WARN')


cmdlist = []
f2ecmdlst = []
DUMMYSTR = 'dummystr'


#  parse table path, returns dict of table key, value
def get_view_table_keys(table_path):

    table_keys_map = {}
    for path in table_path.split('/'):
        for sub_path in path.split(','):
            match = re.search(r"(.+)={(.+)}", sub_path)
            if match is not None:
                log.debug("subpath {}, group1 {}, group2 {}" .format( sub_path, match.group(1), match.group(2)))
                table_keys_map.update({match.group(1):match.group(2)})

    return table_keys_map


def printcmd():
    global cmdlist
    global f2ecmdlst

    tmplst = []
    tmplst = list(cmdlist)
    f2ecmdlst.append(tmplst)

def parammatch(xmlval, dbparamval):

    if xmlval.lower() != dbparamval.lower():
        return False

    return True 

def formatcmdstr(view_member, dbpathstr, nodestr, tables, view_keys):
    global cmdlist

    log.debug('dbpathstr {} nodestr {} table_keys {} ' .format(dbpathstr, nodestr, tables.keys()))

    key_val = (nodestr.split('|', 1)[0]).split('##')
    present_n   = key_val[5] # P or NP
    mode_n      = 'M'
    # mode_n  = key_val[3] # M or O
    key_n       = key_val[1] # - or valid key
    dbpath_n    = key_val[2] # - or valid dbpath
    name_n      = key_val[0] # %s or namest
    valid_n     = False

    log.debug('present_n {} mode_n {} key_n {} dbpath_n {}, name_n {}'
        .format(present_n, mode_n, key_n, dbpath_n, name_n))

    if dbpath_n == '':
        if present_n == 'NP':
            cmdlist.append(DUMMYSTR)
        else:
            cmdlist.append(name_n)
        valid_n = True    
    else:
         #TODO handle config-view here.
         #dbpath str missing for config-view
        if dbpathstr == '':
            pass
        paramval = ''
        if dbpathstr in dbpath_n:
            paramval = dbpath_n.replace(dbpathstr, '')[1:]
        else:
            #check if table object is given.
            #Get Bare table name
            #match keys, only exact match allowed here.
            dbpath_table = '/'.join(dbpath_n.split('/')[:-1])

            for table_path in tables:
                table_path_nokeys = '/'.join(table_path.split('/')[:-1])

                log.debug("dbpath_table {}, table_path {}, table_path_no_keys {}"\
                 .format(dbpath_table, table_path, table_path_nokeys))
                if dbpath_table == table_path_nokeys:
                    dbpathstr = table_path_nokeys
                    filter_keys = collections.OrderedDict()
                    table_path_keys = get_view_table_keys(table_path)
                    paramval = dbpath_n.replace(dbpathstr, '')[1:]
                    log.debug("table_path_keys {}" .format(table_path_keys))

                    for table_path_key, table_path_key_value in table_path_keys.items():
                        view_key_val = view_keys.get(table_path_key_value)
                        if view_key_val:
                            if view_key_val != "*":
                                filter_keys.update({table_path_key: view_key_val})
                            else:
                                log.warn("key {} missing, skippingg node" .format(table_path_key_value))
                                return valid_n
                    log.debug("filter keys {} table_path {} " .format(filter_keys, table_path))

                    table = tables[table_path]
                    log.debug("table {} " .format(table))  
                    match = True
                    for key, value in filter_keys.items():
                        if key not in table:
                            match = False
                            break
                        if table[key] != value:
                            match = False
                            break
                    if match == True:
                        log.debug("found rec with keys {}" .format(filter_keys))
                        view_member = table
                    else:
                        log.debug("rec not found for keys {}" .format(filter_keys))
                        return valid_n

        xml_paramval = paramval.split('=')
        
        if present_n == 'P':
            if xml_paramval[0] not in view_member:
                log.debug("PARAM {} not in db, process next cmd option "\
                 .format(xml_paramval[0]) )
                return False

            valid_n = True
            cmdstr = ''
            value_str = ''
            value = view_member[xml_paramval[0]]

            if value is not None:
                if isinstance(value, bool):
                    value_str = str(value).lower()
                else:    
                    value_str = str(value)

                    #if value is zero length string skip and proceed to next cmd argument
                    if value_str == '':
                        return False

                    #if value is multi word string, enclose it in quotes.
                    if len(value_str.split()) > 1:
                        value_str = "\"" + value_str + "\""

                if len(xml_paramval) > 1:
                    if parammatch(value_str, xml_paramval[1]) == False:
                        log.debug("Param match failed db val {}, xml val {}" .format(value_str, xml_paramval[1]))
                        return False
                if name_n != '%s':
                    cmdstr = name_n
                else:
                    cmdstr = value_str

                cmdlist.append(cmdstr)
            else:
                log.debug(" DB value for key {} is None, skip to next cmd option" .format(xml_paramval[0]))
                return False

        else:
            # The PARAM should not be present in the XML context which
            # we are working under,
            # if PARAM == present, return False
            # if PARAM == not present, return True
            if xml_paramval[0] not in view_member:
                cmdlist.append(DUMMYSTR)
                return True

            #if param exist in db and dbpath_n  is not of the form parm=val
            #return False.
            value_str = ''
            value = view_member[xml_paramval[0]]
            if value:
                if isinstance(value, bool):
                    value_str = str(value).lower()
                else:    
                    value_str = str(value)

            if len(xml_paramval) > 1:
                if parammatch(value_str, xml_paramval[1]) == False:
                    cmdlist.append(DUMMYSTR)
                    return True

    log.debug("cmdlist {}" .format(cmdlist))
    return valid_n              



def process_node(view_member, dbpathstr, nodestr, tables, view_keys):

    log.debug('dbpathstr {} nodestr {} viewkey{} ' .format(dbpathstr, nodestr, view_keys))

    nodestr_parts = nodestr.split('|', 1)
    key_val = (nodestr_parts[0]).split('##')

    present_n = key_val[5] #P or NP
    mode_n  = "M"
    #mode_n = key_val[3] # M or O
    key_n   = key_val[1]  # '' or valid key 
    dbpath_n = key_val[2]  # '' or valid dbpath
    name_n  = key_val[0]  # %s or namestr 

    log.debug('present_n {} mode_n {} key_n {} dbpath_n {}, name_n {}'
        .format(present_n, mode_n, key_n, dbpath_n, name_n))

    ret = formatcmdstr(view_member, dbpathstr, nodestr_parts[0], tables, view_keys)
    if ret is False:
        log.debug("Failed to process nodestr {}" .format(nodestr_parts[0]))
        return False

    if len(nodestr_parts) ==1:
        printcmd()
        cmdlist.pop()
        return ret

    ret = process_node(view_member, dbpathstr, nodestr_parts[1], tables, view_keys)

    cmdlist.pop()
    return ret



def process_cmd(view_member, dbpathstr, table_list, tables, view_keys, cmd_line):
    global f2ecmdlst
    cmdmap = {}
    cmdfound = False
    log.debug("Enter: dbpathstr: {},  table_list: {}, view_keys: {}"
                    .format(dbpathstr, table_list, view_keys))

    cmd_line_parts = cmd_line.split(':::')
    cmdoptlst = (cmd_line_parts[0]).split(';;;')

    for cmdopt in cmdoptlst:
        cmdopt_parts = cmdopt.split('%%%')
        cmdmap_key = cmdopt_parts[0]
        cmdmap_value = (cmdopt_parts[1]).split(";;")
        cmdmap[cmdmap_key] = cmdmap_value


    swnodelst = cmdoptlst
    fcmdlst = []
    for swnode in swnodelst:
        nodestrlst = cmdmap[swnode.split('%%%')[0]]
        for nodestr in nodestrlst:
            ret= process_node(view_member, dbpathstr, nodestr, tables, view_keys)
        log.debug('f2ecmdlst {}' .format(f2ecmdlst))

        if f2ecmdlst:
            cmdfound = True
            jlist = []
            for f2ecmd in f2ecmdlst:
                filtered = [ v for v in f2ecmd if v != DUMMYSTR ]
                jlist.append(' '.join(filtered))
                fcmdlst += jlist
            f2ecmdlst = []

    fcmdlst = sorted(list(set(fcmdlst)), key=len)
    log.debug('fcmdlst {}' .format(fcmdlst))

    printlst_tmp =[]
    for i, j in enumerate(fcmdlst):
        match = False
        for k in fcmdlst[i+1:]:
           if k.startswith(j + ' '):
              match = True
        if match == False:
           printlst_tmp.append(j)
           
    return printlst_tmp, cmdfound
