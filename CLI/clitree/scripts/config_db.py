#! /usr/bin/env python
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

""" The script config-DB.py is used to build the Configuration-DB text file,
        which will  be used by the renderer module to generate the CLI
        running-configuration

        The DICT_FILE passed to the script will be the target file to
        which DB entries will be written to.

        The script start with adding DB entries for commands in configure-view.
        The START_FILE passed,will be the first file the script look into,
        while searching for a view.If start_file is not passed,default file
        to start with will be configure_mode.xml.
        As the DB entries are getting written, if any command encountered,
        change the view (Eg interface CLI change view to configure-if-view),then
        the script will continue adding  DB entries for commands in the changed
        view.On adding DB entries for all the commands in the changed view,
        the script will resume adding DB entries for the parent view.

        In case any command has no dbpath configured,either in COMMAND tag or
        or PARAM tag,no DB entry will be added for that command

         Usage: config_db.py inDir out_dict_file [start_file] [--debug]
                config_db.py --help
"""

import logging, glob, os, sys

from bs4 import BeautifulSoup

from config_db_data import VIEW_PRIORITY_FILE_MAP

VIEW_TAG_STR = "VIEW"
CONFIG_VIEW_STR = "configure-view"

COMMAND_TAG_STR = "COMMAND"
PARAM_TAG_STR = "PARAM"

ATTR_NAME = "name"
ATTR_VIEW = "view"
ATTR_VIEW_KEYS = "view_keys"
ATTR_VIEW_TABLES = "view_tables"
ATTR_COMMAND_TABLES = "command_tables"
ATTR_COMMAND_KEYS = "command_keys"
ATTR_DB_PATH = "dbpath"
ATTR_DB_TABLE = "dbtable"
ATTR_OPTIONAL = 'optional'
ATTR_RENDER_VIEW_CB = "render_view_cb"
ATTR_RENDER_CMD_CB = "render_command_cb"
ATTR_DB_AND_RENDER_CB = "data_and_render_cb"
ATTR_MODE = "mode"
ATTR_ADD_CONFIG_ENTRY = "add_config_entry"
ATTR_DB_FLAG = 'db_flag'
PARAM_VAL_STR = "%s"
SEP_CLI_FLAG = "SEP_CLI"

CMD_SUCCESS= "CMD_SUCCESS"
CMD_FAIL= "CMD_FAIL"
PARAM_SUCCESS= "PARAM_SUCCESS"
PARAM_FAIL= "PARAM_FAIL"
PARAM_SEP_CLI_PENDING = "PARAM_SEP_CLI_PENDING"
PARAM_SEP_CLI_COMPLETED = "PARAM_SEP_CLI_COMPLETED"

NODE_DELIMITER = "|"
NODE_ITEM_DELIMITER = "##"
COMMAND_DELIMITER = ";;"
FIELD_DELIMITER = ":::"
DB_FLAG_DELIMITER = "|"
VIEW_ATTR_DELIMITER = "|"

MANDATORY_STR = "M"
OPTIONAL_STR = "O"
PARAM_VAL_STR = "%s"
SWITCH_NODE_STR = "sw"

log_format = "\n%(filename)s:%(funcName)s:%(message)s"
log = logging.getLogger(__file__)

# Use FileHandler() to log to a file
stream_handler = logging.StreamHandler()
formatter = logging.Formatter(log_format)
stream_handler.setFormatter(formatter)
log.addHandler(stream_handler)

log.setLevel('DEBUG')

klish_xml_dir = "..\\cli-xml"


#FILE_LIST = ['interface.xml', 'bgp.xml', 'bgp_af_ipv4.xml', 'bgp_af_l2vpn.xml','configure_mode.xml']

#FILE_LIST = ['bgp.xml', 'bgp_af_ipv4.xml', 'bgp_af_l2vpn.xml','configure_mode.xml']


#FILE_LIST = ['interface.xml', 'udld.xml', 'storm_control.xml', 'configure_mode.xml']

FILE_LIST = ['udld.xml', 'tacacs.xml', 'configure_mode.xml']

FILE_TREE_MAP = {}
PARENT_NODE_SEP_CLI_CHILD_MAP = {}

NODE_VIEW_KEYS_LIST_MAP= {}
NODE_VIEW_TABLES_LIST_MAP = {}
NODE_COMMAND_TABLES_LIST_MAP = {}
NODE_COMMAND_KEYS_LIST_MAP = {}
NODE_DB_AND_RENDER_LIST_MAP = {}
NODE_RENDER_VIEW_CB_LIST_MAP = {}
NODE_RENDER_CMD_CB_LIST_MAP = {}


CMD_TARGET_VIEW_MAP = {}


def process_view_name(view_name):

    log.debug("Processing view name '{}'" .format(view_name))

    priorityFileList = VIEW_PRIORITY_FILE_MAP.get(view_name)

    if priorityFileList is not None:
        for filename in priorityFileList:
            filetree = FILE_TREE_MAP.get(filename)
            if filetree is not None:
                view_tag = filetree.find(VIEW_TAG_STR, {ATTR_NAME : view_name})
                if view_tag is not None:
                    log.debug("Processing view {} from file {}" .format(view_name, filename))
                    process_view_tag(view_name, view_tag)

    if priorityFileList is None or STARTFILE not in priorityFileList:
        filetree = FILE_TREE_MAP.get(STARTFILE)
        view_tag = filetree.find(VIEW_TAG_STR, {ATTR_NAME : view_name})
        if view_tag is not None:
            log.debug("Processing view {} from file {}" .format(view_name, STARTFILE))
            process_view_tag(view_name, view_tag)

    for file, filetree in FILE_TREE_MAP.items():
        if file != STARTFILE and (priorityFileList is None or file not in priorityFileList):
            view_tag = filetree.find(VIEW_TAG_STR, {ATTR_NAME : view_name})
            if view_tag is not None:
                log.debug("Processing view {} from file {}" .format(view_name, file))
                process_view_tag(view_name, view_tag)
    return


def get_view_keys(node_tag):

    """Return the view_keys to be picked in the current iteration
       from the command"""
    view_keys = ''
    if ATTR_VIEW_KEYS in node_tag.attrs:

        if node_tag not in NODE_VIEW_KEYS_LIST_MAP:
            view_keys_str = node_tag[ATTR_VIEW_KEYS]
            view_keys_list = view_keys_str.split(VIEW_ATTR_DELIMITER)
            NODE_VIEW_KEYS_LIST_MAP.update({node_tag : view_keys_list})

        view_keys = NODE_VIEW_KEYS_LIST_MAP[node_tag].pop(0)
        if len(NODE_VIEW_KEYS_LIST_MAP[node_tag]) == 0:
            NODE_VIEW_KEYS_LIST_MAP.pop(node_tag, None)

    return view_keys


def get_view_tables(node_tag):

    """Return the view_tables to be picked in the current iteration
       from the command"""

    view_tables = ''
    if ATTR_VIEW_TABLES in node_tag.attrs:

        if node_tag not in NODE_VIEW_TABLES_LIST_MAP:
            view_tables_str = node_tag[ATTR_VIEW_TABLES]
            view_tables_list = view_tables_str.split(VIEW_ATTR_DELIMITER)
            NODE_VIEW_TABLES_LIST_MAP.update({node_tag : view_tables_list})

        view_tables = NODE_VIEW_TABLES_LIST_MAP[node_tag].pop(0)
        if len(NODE_VIEW_TABLES_LIST_MAP[node_tag]) == 0:
            NODE_VIEW_TABLES_LIST_MAP.pop(node_tag, None)

    return view_tables


def get_command_tables(node_tag):

    """Return the command tables to be picked in the current iteration
       from the command"""

    command_tables = ''

    if ATTR_COMMAND_TABLES in node_tag.attrs:
        if node_tag not in NODE_COMMAND_TABLES_LIST_MAP:
            command_tables_str = node_tag[ATTR_COMMAND_TABLES]
            command_tables_list = command_tables_str.split(VIEW_ATTR_DELIMITER)
            NODE_COMMAND_TABLES_LIST_MAP.update({node_tag : command_tables_list})

        command_tables = NODE_COMMAND_TABLES_LIST_MAP[node_tag].pop(0)
        if len(NODE_COMMAND_TABLES_LIST_MAP[node_tag]) == 0:
            NODE_COMMAND_TABLES_LIST_MAP.pop(node_tag, None)

    return command_tables



def get_command_keys(node_tag):

    """Return the command tables to be picked in the current iteration
       from the command"""

    command_keys = ''

    if ATTR_COMMAND_KEYS in node_tag.attrs:
        if node_tag not in NODE_COMMAND_KEYS_LIST_MAP:
            command_keys_str = node_tag[ATTR_COMMAND_KEYS]
            command_keys_list = command_keys_str.split(VIEW_ATTR_DELIMITER)
            NODE_COMMAND_KEYS_LIST_MAP.update({node_tag : command_keys_list})

        command_keys = NODE_COMMAND_KEYS_LIST_MAP[node_tag].pop(0)
        if len(NODE_COMMAND_KEYS_LIST_MAP[node_tag]) == 0:
            NODE_COMMAND_KEYS_LIST_MAP.pop(node_tag, None)

    return command_keys



def get_db_and_render_cb(node_tag):

    """Return the view_keys to be picked in the current iteration
       from the command"""
    db_render_cb = ''

    if ATTR_DB_AND_RENDER_CB in node_tag.attrs:
        if node_tag not in NODE_DB_AND_RENDER_LIST_MAP:
            db_and_render_cb_str = node_tag[ATTR_DB_AND_RENDER_CB]
            db_and_render_cb_list = db_and_render_cb_str.split(VIEW_ATTR_DELIMITER)
            NODE_DB_AND_RENDER_LIST_MAP.update({node_tag : db_and_render_cb_list})

        db_render_cb = NODE_DB_AND_RENDER_LIST_MAP[node_tag].pop(0)
        if len(NODE_DB_AND_RENDER_LIST_MAP[node_tag]) == 0:
            NODE_DB_AND_RENDER_LIST_MAP.pop(node_tag, None)
    return db_render_cb


def get_render_view_cb(node_tag):

    """Return the view_keys to be picked in the current iteration
       from the command"""
    render_view_cb = ''

    if ATTR_RENDER_VIEW_CB in node_tag.attrs:
        if node_tag not in NODE_RENDER_VIEW_CB_LIST_MAP:
            render_view_cb_str = node_tag[ATTR_RENDER_VIEW_CB]
            render_view_cb_list = render_view_cb_str.split(VIEW_ATTR_DELIMITER)
            NODE_RENDER_VIEW_CB_LIST_MAP.update({node_tag : render_view_cb_list})

        render_view_cb = NODE_RENDER_VIEW_CB_LIST_MAP[node_tag].pop(0)
        if len(NODE_RENDER_VIEW_CB_LIST_MAP[node_tag]) == 0:
            NODE_RENDER_VIEW_CB_LIST_MAP.pop(node_tag, None)
    return render_view_cb


def get_render_cmd_cb(node_tag):

    """Return the view_keys to be picked in the current iteration
       from the command"""
    render_cmd_cb = ''

    if ATTR_RENDER_CMD_CB in node_tag.attrs:
        if node_tag not in NODE_RENDER_CMD_CB_LIST_MAP:
            render_cmd_cb_str = node_tag[ATTR_RENDER_CMD_CB]
            render_cmd_cb_list = render_cmd_cb_str.split(VIEW_ATTR_DELIMITER)
            NODE_RENDER_CMD_CB_LIST_MAP.update({node_tag : render_cmd_cb_list})

        render_cmd_cb = NODE_RENDER_CMD_CB_LIST_MAP[node_tag].pop(0)
        if len(NODE_RENDER_CMD_CB_LIST_MAP[node_tag]) == 0:
            NODE_RENDER_CMD_CB_LIST_MAP.pop(node_tag, None)
    return render_cmd_cb



def process_view_tag(view_name, view_tag):
    target_view = ""

    for command_tag in view_tag.find_all(COMMAND_TAG_STR):
        #log.info('pkx1: %s'%  command_tag.prettify())

        if is_db_flag_set(command_tag, SEP_CLI_FLAG):

            param_status = PARAM_SEP_CLI_PENDING
            while param_status == PARAM_SEP_CLI_PENDING:

                render_cb_pr = False
                db_render_cb = get_db_and_render_cb(command_tag)
                render_view_cb = get_render_view_cb(command_tag)
                render_cmd_cb = get_render_cmd_cb(command_tag)

                if db_render_cb or render_view_cb or render_cmd_cb:
                    render_cb_pr = True

                ret, field1_str, param_status = process_command(view_name, command_tag, render_cb_pr)

                if ret == CMD_SUCCESS:
                    if command_tag in CMD_TARGET_VIEW_MAP:
                        target_view = CMD_TARGET_VIEW_MAP[command_tag].pop(0)

                    add_dict_entry(view_tag, command_tag, field1_str, target_view, \
                        get_view_keys(command_tag), get_view_tables(command_tag), \
                        get_command_keys(command_tag), get_command_tables(command_tag),\
                        db_render_cb, render_view_cb, render_cmd_cb, DICT_FILE)
                    # Check if PARAM tag has view configured
                    if target_view:
                        process_view_name(target_view)
                    target_view = ""

                else:
                    break

            param_status = PARAM_SEP_CLI_PENDING

            log.info('\t {} :{}' .format(ret, command_tag[ATTR_NAME]))

            # check if COMMAND is changing mode by looking for
            # view attribute inside COMMAND tag

            if (ret == CMD_SUCCESS) and (ATTR_VIEW in command_tag.attrs):
                process_view_name(command_tag[ATTR_VIEW])
        else:
            render_cb_pr = False
            db_render_cb = get_db_and_render_cb(command_tag)
            render_view_cb = get_render_view_cb(command_tag)
            render_cmd_cb = get_render_cmd_cb(command_tag)

            if db_render_cb or render_view_cb or render_cmd_cb:
               render_cb_pr = True

            ret, field1_str, param_status = process_command(view_name, command_tag, render_cb_pr)

            log.debug(" ret {}, commmand name {}" .format(ret, command_tag[ATTR_NAME]))

            if ret == CMD_SUCCESS:

                if ATTR_VIEW in command_tag.attrs:
                    target_view = command_tag[ATTR_VIEW]

                add_dict_entry(view_tag, command_tag, field1_str, target_view, \
                       get_view_keys(command_tag), get_view_tables(command_tag), \
                       get_command_keys(command_tag), get_command_tables(command_tag), \
                       db_render_cb, render_view_cb, render_cmd_cb, DICT_FILE)

                if target_view:
                    process_view_name(target_view)

        field1_str = ""
        target_view = ""
        if command_tag in CMD_TARGET_VIEW_MAP:
            del CMD_TARGET_VIEW_MAP[command_tag]

    return


def process_command(view_name, command_tag, render_template_present):


    log.debug ('process_command: command name {} view present {}' \
        .format(command_tag[ATTR_NAME], render_template_present))

    outstr = field1_str = process_output_str(command_tag)
    has_opt_param_in_subtree = False
    param_dbpath_present = False
    cmd_dbpath_present = False
    param_status = PARAM_SUCCESS
    cmd_str = command_tag[ATTR_NAME]

    if check_cmd_need_running_entry(command_tag) == False:
        log.info("process_command: no running_entry {}" .format(command_tag[ATTR_NAME]))
        return CMD_FAIL, field1_str, param_status

    if ATTR_DB_PATH in command_tag.attrs:
        cmd_dbpath_present = True

    if command_tag.find(PARAM_TAG_STR) is None:

        if cmd_dbpath_present == True or render_template_present == True:
            log.info('process_command: outstr {}' .format(outstr))
            return CMD_SUCCESS, field1_str, param_status

        else:
            log.info("process_command: {} does not have dbpath and params" .format(command_tag[ATTR_NAME]))
            return CMD_FAIL, field1_str, param_status


    log.info('process_command: outstr {}' .format(outstr))

     #If we come here, it means Command has PARAMs
    for param_tag in command_tag.find_all(PARAM_TAG_STR, recursive=False):

        if has_opt_param_in_subtree:
            field1_str = field1_str + COMMAND_DELIMITER + outstr

        outstr, has_opt_param_in_subtree, field1_str, param_dbpath_present, \
                param_status = process_param(command_tag, param_tag, outstr,
                                             field1_str, param_dbpath_present,
                                             param_status)
        log.debug ('process_command: CMD :{}, PARAM: %s outstr {}, has_opt_param_in_subtree {}'
                      .format(command_tag[ATTR_NAME],
                        param_tag[ATTR_NAME],
                        outstr, has_opt_param_in_subtree))


    if (param_dbpath_present == True) or (cmd_dbpath_present == True) or (render_template_present == True):
        # Check if Yang path is present in any of the params of the command
        return CMD_SUCCESS, field1_str, param_status
    else:
        return CMD_FAIL, field1_str, param_status


def process_param(cmd_tag, param_tag, prefixstr, field1_str,
                  is_dbpath_present, param_status):

    """Function to process parameters of a command"""

    outstr = prefixstr
    formatstr = process_output_str(param_tag)
    if formatstr != "":
        outstr = prefixstr + NODE_DELIMITER + formatstr
        field1_str = field1_str + NODE_DELIMITER + formatstr

    has_opt_param_in_subtree = False
    is_opt_param = check_optional_param(param_tag)
    is_switch_mode = check_switch_mode(param_tag)
    is_parent_switch_mode = False
    param_parent_tag = param_tag.parent
    empty_list = []

    if ATTR_DB_PATH in param_tag.attrs:
        is_dbpath_present = True

    if ATTR_VIEW in param_tag.attrs:
        if cmd_tag not in CMD_TARGET_VIEW_MAP:
            CMD_TARGET_VIEW_MAP.update({cmd_tag : empty_list})
        CMD_TARGET_VIEW_MAP[cmd_tag].append(param_tag[ATTR_VIEW])


    for child_param in param_tag.find_all(PARAM_TAG_STR, recursive=False):

        if has_opt_param_in_subtree:
            field1_str = field1_str + COMMAND_DELIMITER + outstr


        if is_db_flag_set(param_tag, SEP_CLI_FLAG):
            if (param_tag not in PARENT_NODE_SEP_CLI_CHILD_MAP) or \
              (child_param not in PARENT_NODE_SEP_CLI_CHILD_MAP[param_tag]):
                return handle_sw_sep_cli_flag(cmd_tag, param_tag,
                                              child_param, outstr, field1_str,
                                              is_dbpath_present, param_status)
            else:
                continue


        outstr, has_opt_param_in_subtree, field1_str, is_dbpath_present, \
                     param_status = process_param(cmd_tag, child_param,
                                   outstr, field1_str, is_dbpath_present,
                                   param_status)

        log.debug('process_param: PARAM: {}, outstr {}, has_opt_param_in_subtree {}'
                       .format(child_param[ATTR_NAME],
                        outstr, has_opt_param_in_subtree))

    if param_parent_tag.name == PARAM_TAG_STR:
        is_parent_switch_mode = check_switch_mode(param_parent_tag)

    log.debug("is_opt_param {}, is_switch_mode {}, is_parent_switchmode {}," \
        .format(is_opt_param, is_switch_mode, is_parent_switch_mode))

    if((not is_opt_param)  and (not is_switch_mode) and
       (not is_parent_switch_mode)):
        return outstr, has_opt_param_in_subtree, field1_str,\
               is_dbpath_present, param_status
    else:
        return prefixstr, True, field1_str, is_dbpath_present, param_status



def handle_sw_sep_cli_flag(cmd_tag, param_tag, child_param, outstr, \
                           field1_str, is_dbpath_present, param_status):

    """ Process PARAM whose parant has SEP_CLI flag set """

    empty_list = []

    if param_tag not in PARENT_NODE_SEP_CLI_CHILD_MAP:
        PARENT_NODE_SEP_CLI_CHILD_MAP.update({param_tag : empty_list})

    outstr, has_opt_param_in_subtree, field1_str, \
    is_dbpath_present, param_status =   \
        process_param(cmd_tag, child_param, outstr, field1_str,
                      is_dbpath_present, param_status)

    if param_status != PARAM_SEP_CLI_PENDING:
        PARENT_NODE_SEP_CLI_CHILD_MAP[param_tag].append(child_param)

    if len(PARENT_NODE_SEP_CLI_CHILD_MAP[param_tag]) == \
        len([child.tag for child in param_tag.find_all(PARAM_TAG_STR, recursive=False)]):

        PARENT_NODE_SEP_CLI_CHILD_MAP.pop(param_tag, None)
        return outstr, has_opt_param_in_subtree, \
               field1_str, is_dbpath_present, \
               PARAM_SEP_CLI_COMPLETED
    else:
        return outstr, has_opt_param_in_subtree, \
               field1_str, is_dbpath_present, \
               PARAM_SEP_CLI_PENDING


def get_dbpath_str(tag):
    dbpath_str = ""
    if ATTR_DB_PATH in tag.attrs:
        dbpath_str = tag[ATTR_DB_PATH]

    return  dbpath_str


def get_dbtable_str(tag):
    dbtable_str = ""
    if ATTR_DB_TABLE in tag.attrs:
        dbpath_str = tag[ATTR_DB_TABLE]

    return  dbtable_str


def is_subcommand_keyword(param_tag):

    if ATTR_MODE in param_tag.attrs:
        if param_tag[ATTR_MODE].lower() == "subcommand":
            return True

    return False


def get_param_cmdstr(param_tag):

    if is_subcommand_keyword(param_tag):
        return param_tag.attrs[ATTR_NAME]

    return PARAM_VAL_STR


def is_db_flag_set(node_tag, flag):

    """ Return True if the attribute db_flag has the flag passed set.
        False otherwise """

    if ATTR_DB_FLAG in node_tag.attrs:
        flag_list = \
         node_tag[ATTR_DB_FLAG].replace(" ", "").split(DB_FLAG_DELIMITER)
        if flag in flag_list:
            return True
    return False


def check_switch_mode(param_tag):

    """Function to check if the given PARAM is a switch node"""

    if ATTR_MODE in param_tag.attrs:
        if param_tag[ATTR_MODE].lower() == "switch":
            return True
    return False


def check_show_cmd(command_tag):
    cmd_name = command_tag[ATTR_NAME]

    if cmd_name.split(" ")[0] == 'show':
        return True
    else:
        return False


def check_cmd_need_running_entry(command_tag):

    result = True
#    if check_show_cmd(cmd_element) or check_no_cmd(cmd_element):
#        result = False

    if check_show_cmd(command_tag):
        result = False

    if ATTR_ADD_CONFIG_ENTRY in command_tag.attrs:
        if command_tag[ATTR_ADD_CONFIG_ENTRY].tolower() == 'true':
            result = True
        else:
            result = False
    return result

def check_switch_mode(param_tag):

    """Function to check if the given PARAM is a switch node"""

    if ATTR_MODE in param_tag.attrs:
        if param_tag[ATTR_MODE].lower() == "switch":
            return True
    return False

def check_optional_param(param_tag):

    """Function to check if a PARAM is optional or Mandatory"""

    if ATTR_OPTIONAL in param_tag.attrs:
        if param_tag[ATTR_OPTIONAL].lower() == "true":
            return True
    return False

def get_param_presence_str(param_tag):

    """Function to check if a PARAM is optional or mandatory
       and return appropriate string to be filed for field1"""

    param_parent = param_tag.parent

    if check_optional_param(param_tag):
        return OPTIONAL_STR
    else:
        # Check if PARAM's parent is a switch node with optional true
        if ((param_parent.tag == PARAM_TAG_STR) and
              check_switch_mode(param_parent) and
              check_optional_param(param_parent)):
            return OPTIONAL_STR
        else:
            return MANDATORY_STR


def process_output_str(tag):

    if tag.name == COMMAND_TAG_STR:
        cmd_str = tag[ATTR_NAME]
#        dbtable_str = get_dbtable_str(tag)
        dbtable_str = ""
        dbpath_str = get_dbpath_str(tag)
        parent_switch_str = ""
        presence_str = MANDATORY_STR
    else:
        if check_switch_mode(tag):
            return ""
        cmd_str = get_param_cmdstr(tag)
#        dbtable_str = get_dbtable_str(tag)
        dbtable_str = ""
        dbpath_str = get_dbpath_str(tag)
        presence_str = get_param_presence_str(tag)
        parent_tag = tag.parent
        is_parent_switch_node = check_switch_mode(parent_tag)
        if is_parent_switch_node:
            parent_switch_str = SWITCH_NODE_STR
        else:
            parent_switch_str = ""

    formatstr = cmd_str + NODE_ITEM_DELIMITER + dbtable_str + \
                NODE_ITEM_DELIMITER + dbpath_str + \
                NODE_ITEM_DELIMITER + parent_switch_str + \
                NODE_ITEM_DELIMITER + presence_str

    return formatstr



def get_command_view(view_tag, target_view):

    if target_view:
        target_view = target_view.split("-view")[0]
    else:
        target_view = view_tag[ATTR_NAME].split("-view")[0]

    return  target_view


def add_dict_entry(view_tag, cmd_tag, field1str, target_view, view_keys, \
                   view_tables, command_keys, command_tables, db_render_cb, \
                   render_view_cb, render_cmd_cb, dictfile):

    command_view = get_command_view(view_tag, target_view)

    dict_entry=field1str + FIELD_DELIMITER + view_keys + \
               FIELD_DELIMITER + view_tables + FIELD_DELIMITER + command_keys + FIELD_DELIMITER + command_tables + \
               FIELD_DELIMITER + db_render_cb + FIELD_DELIMITER + render_view_cb + \
               FIELD_DELIMITER + render_cmd_cb + FIELD_DELIMITER + command_view + '\n'

    log.debug('add_dict_entry: CMD :{}, Dict Entry: {}' \
                   .format(cmd_tag[ATTR_NAME], dict_entry))

    fd = open(dictfile, "a")
    fd.write(dict_entry)
    fd.close()
    return

if __name__ == "__main__":

    if sys.argv[1] == "--help":
        print("Usage: python config_db.py inDir outDictFile [startfile] [--debug]")
        sys.exit(0)

    if len(sys.argv) < 3:
        print("Error: Missing parameter" + os.linesep +
              "Usage: python config_db.py inDir outDictFile [startfile] [--debug]")
        sys.exit(0)

    IN_DIR_PATH = sys.argv[1]
    DICT_FILE = sys.argv[2]
    DBG_FLAG = False

    if len(sys.argv) > 3:
        if sys.argv[3] == "--debug":
            DBG_FLAG = True
            STARTFILE = "configure_mode.xml"
        else:
            STARTFILE = sys.argv[3]
    else:
        STARTFILE = "configure_mode.xml"

    if len(sys.argv) > 4 and sys.argv[4] == "--debug":
            DBG_FLAG = True

    if os.path.isfile(DICT_FILE):
       os.remove(DICT_FILE)

    models = glob.glob(os.path.join(IN_DIR_PATH, '*.xml'))
    for model in models:
        fname = os.path.basename(model)
        with open(model, "r") as fp:
                soup = BeautifulSoup(fp, "xml")
                log.debug('M: File to be parsed: {}' .format(model))
                FILE_TREE_MAP.update({fname:soup})

    process_view_name(CONFIG_VIEW_STR)
