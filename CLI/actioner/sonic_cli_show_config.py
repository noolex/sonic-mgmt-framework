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

from jinja2 import Template, Environment, FileSystemLoader
import collections
import os
import sys
import copy

import cli_client as cc
from scripts.render_cli import write
from rpipe_utils import pipestr
from show_config_data import render_filelst
from show_config_data import config_view_hierarchy
from show_config_data import view_dependency
from show_config_data import render_cb_dict
from show_config_data import table_sort_cb_dict
from show_config_utils import process_cmd
from show_config_utils import get_view_table_keys
from show_config_utils import log
from show_config_table_sort import natsort_list

CLI_XML_VIEW_MAP = {}

CONFIG_VIEW_CMD_IDX =0
CONFIG_VIEW_TABLE_KEYS_IDX=1
CONFIG_VIEW_TABLES_IDX=2
CONFIG_VIEW_SEC_TABLE_KEYS_IDX=3
CONFIG_VIEW_CMD_TABLES_IDX=4
CONFIG_VIEW_DB_RENDER_IDX=5
CONFIG_VIEW_RENDER_VIEW_IDX=6
CONFIG_VIEW_RENDER_CMD_IDX=7
CONFIG_VIEW_NAME_IDX=8
CONFIG_VIEW_IDX_LEN=9

NODE_ELEM_NAME_IDX =0
NODE_ELEM_DBPATH_IDX =1
NODE_ELEM_DBKEY_IDX =2
NODE_ELEM_PARENT_SW_IDX =3
NODE_ELEM_TYPE_IDX=4


CMD_FAIL = "CMD_FAIL"
CMD_SUCCESS = "CMD_SUCCESS"
CB_FAIL = "CB_FAIL"
CB_SUCCESS = "CB_SUCCESS"

RENDERER_TEMPLATE_PATH=os.getenv("RENDERER_TEMPLATE_PATH", "/usr/sbin/cli/render-templates")
FORMAT_FILE = "DB.txt"


DB_Cache = {}

format_read = False

jinja_loader = {}

CMDS_STRING = ''


def cache_view_commands(command_list, indent, ctxt):
    global CMDS_STRING

    log.debug("command_list {}" .format(command_list))
    fmtst = ''
    for idx, command in enumerate(command_list):

        if command:
            if CMDS_STRING =='':
                fmtst = (' ' *indent) + '!'
                CMDS_STRING = '\n' + fmtst
                CMDS_STRING += '\n'
            elif (ctxt and idx ==0):
                fmtst = (' ' *indent) + '!'
                CMDS_STRING += fmtst
                CMDS_STRING += '\n'
            fmtst = (' ' *indent) + command
            CMDS_STRING += fmtst
            CMDS_STRING += '\n'

def get_rendered_template_output(template_file, response, render_view):
    # Create the jinja2 environment.
    # Notice the use of trim_blocks, which greatly helps control whitespace.
    t_str = ""
    loader = None
    if template_file  not in jinja_loader:

        template_path = os.path.join(RENDERER_TEMPLATE_PATH,"showrunning")
        j2_env = Environment(loader=FileSystemLoader(template_path),extensions=['jinja2.ext.do','jinja2.ext.loopcontrols'])
        j2_env.trim_blocks = True
        j2_env.lstrip_blocks = True
        j2_env.rstrip_blocks = False
        loader = j2_env.get_template(template_file)
        jinja_loader.update({template_file: loader})
    else:
        loader = jinja_loader.get(template_file)

    if response:
        t_str = (loader.render(json_output=response, view=render_view))
    return t_str


def get_rest_table(table_path):

    log.debug('table path: {}' .format(table_path))


    #TODO optimize by filtering based on keys, if all keys of the table are available

    #table_path format "sonic:sonic/TABLE_NAME/keys"
    #The response of DB get() is cached.
    #On the next get request, first the cache is queried.
    #This is to avoid multiple REST api calls, which are expensive.
    sonic_table = '/'.join(table_path.split('/')[:-1])


    if sonic_table in DB_Cache:
       return DB_Cache.get(sonic_table)

    sonic_table_yang_path = '/restconf/data/' + sonic_table
    log.debug("sonic_table_name {}" .format(sonic_table_yang_path))

    api = cc.ApiClient()
    keypath=[]

    keypath = cc.Path(sonic_table_yang_path)
    response = api.get(keypath)
    if(response.ok()):
        if (response.content is None) or (not (isinstance(response.content, dict))):
            log.info("Get Table {} response failure, continue next table or next view " .format(sonic_table_yang_path) )
            return None

        modulename = sonic_table.split(':')[0]
        bare_table_name = sonic_table.split(':')[1].split('/')[-1]
        yang_table_fmt = modulename + ":" + bare_table_name
        response_table = response.content.get(yang_table_fmt)
        if response_table is None:
            # Cache to denote get request is done.
            DB_Cache.update({sonic_table:None})
            log.info("Table {} not in ConfigDB continue next table or next view" .format(yang_table_fmt))
            return None

        #get table sorting callback if given. otherwise use default natsort.
        sort_callback =  table_sort_cb_dict.get(sonic_table)
        if sort_callback is None:
           sort_callback= natsort_list 
        response_table = sort_callback(response_table, table_path)

        #cache table
        DB_Cache.update({sonic_table:response_table}) 
        return response_table
    else:
        log.warn("Response failure for {} in configDB" .format(sonic_table_yang_path))    
    return None

def update_table_keys(table_keys, view_member):
    table_key_values = {}
    for key, value in table_keys.items():
        if key not in view_member:
            log.warning("key {} not in table " .format(key))
            continue
        table_key_values.update({value: view_member[key]})

    return table_key_values


class cli_xml_view:

    def __init__(self, command_line):

        #xml view name (for e.g, config-router-bgp)
        self.name = command_line[CONFIG_VIEW_NAME_IDX]

        #List of command lines from DB.txt
        self.view_cmd_list = []
        self.primary_table = ""
        self.dbpathstr = ""

        #All table keys for this view. for e.g. for config-router-bgp: vrfname=*, ip-prfx=*
        #Data represented as "view-keys" tag in the xml.
        self.table_keys = collections.OrderedDict()
        for keyVal in command_line[CONFIG_VIEW_TABLE_KEYS_IDX].split(','):
            if len(keyVal.split("=")) != 2:
               log.warning("cli_xml_view init: Invalid key format; skip this key {}" .format(keyVal))
               continue

            self.table_keys.update({keyVal.split("=")[0]:keyVal.split("=")[1]})

        #List of all tables to be accessed for this view. This aggregated while parsing every command for the view.
        #Primary table is added to this list.

        table_lst = command_line[CONFIG_VIEW_TABLES_IDX].split(';')

        #remove empty string from list
        self.table_list = list(filter(None, table_lst))

        if not self.table_list:
            log.warn("cli_xml_view init: table list length zero for view {}" .format(self.name))
        else:
            #Primary table for this view. for e.g. "sonic-bgp-global:sonic-bgp-global/BGP_GLOBALS/vrf_name={vrf-name}"
            #Data represented as "view_table" tag in the xml.
            self.primary_table =self.table_list[0]
            self.dbpathstr = '/'.join(self.primary_table.split('/')[:-1])

        log.debug("name: {}, table_keys: {}, primary_table: {} dbpathstr {} tablelist" \
                .format(self.name, self.table_keys, self.primary_table, self.dbpathstr, self.table_list))

    def print_view(self):
        log.info('---------------------------------------------------------')
        log.info("view-name {}" .format(self.name))
        for cmd in self.view_cmd_list:
            log.info("\t{}" .format(self.view_cmd_list))
            log.info('---------------------------------------------------------')

    #only config-view case.
    def process_view_commands_no_table(self, member_keys,indent):

        log.debug('ENTER view {} ' .format(self.name))
        if not self.view_cmd_list:
            return CMD_SUCCESS

        #In executing "show running-configuration", a view with no primary table fo e.g. configure-view,
        #view_keys are not expected. Each command is mapped to a different table, and keys for the command table
        #are specified by command_keys tag and read later in process_command.
        #For "show configuration" of a view which is rendered using a callback, keys are specified as argument to
        #the API. These keys are passed to this function as argument member_keys and
        #applicable to the parent command which changes to a new view.

        for cmd in  self.view_cmd_list:
            view_keys = copy.deepcopy(member_keys)
            ret, is_view_rendered = process_command(self, None, self.table_list, view_keys, self.dbpathstr,\
                                                False, cmd, indent)
        #Process child views.

        if view_dependency.get(self.name) is not None:

            #form the keys for the dependency view tables.
            for view in view_dependency[self.name]:
            #     #get keys from parent

                view_key_values = collections.OrderedDict()
                cli_view = CLI_XML_VIEW_MAP.get(view)
                if cli_view == None:
                    continue

                view_keys = cli_view.table_keys
                log.info("Preparing for child view: {}, child view keys: {}, parent view: {}, parent member keys: {} " \
                 .format(view, view_keys, self.name,  member_keys))

                for key, value in view_keys.items():
                    # set default key value to wildcard
                    # check if key has a value or a dbpath to parent member key name.
                    view_key_values.update({key.lstrip():"*"})
                    if value and value != "*":
                        keypath_list = value.split('/')
                        if len(keypath_list) > 1:
                            log.warn("no table member to get key value {} ". format(self.name))
                            pass
                        else:
                            view_key_values.update({key.lstrip():keypath_list[0]})

                log.info("Preparing for child view {}, child view keys {} " .format(cli_view.name, view_key_values))
                cmd_status = cli_view.process_view_commands(view_key_values, indent+1)

        log.debug(' Exit.view {}, status {}' .format(self.name, CMD_SUCCESS))
        return CMD_SUCCESS


    #Process the primary view table records using the provided keys.
    #Parse the first command in the record list, if successful parse all the
    #remaining commands.
    #Then process dependent views.
    def process_view_commands(self, view_table_keys, indent):

        log.debug("Enter: table_list= {}, view_table_keys= {}" \
                    .format(self.table_list, view_table_keys))

        #get primary table
        primary_table_path = self.primary_table

        #get table keys from table path in form of dict ={key:value, key1:value,..}
        primary_table_keys = get_view_table_keys(primary_table_path)
        log.debug("Primary table path {},  keys {}" .format(primary_table_path, primary_table_keys))

        #get configDB table using rest call.
        response = get_rest_table(primary_table_path)

        if response is None:
            log.info('Table {} not found return SUCCESS to continue next table/view' .format(primary_table_path))
            return CMD_SUCCESS

        #get view primary table from response.


        filter_keys = collections.OrderedDict()
        for table_key, table_key_val in primary_table_keys.items():
            if table_key_val in view_table_keys:
                view_key_val = view_table_keys.get(table_key_val)
                if view_key_val:
                    if view_key_val != "*":
                        filter_keys.update({table_key:view_key_val})
                else:
                    log.warn('Key {} missing in table {}, skip view' .format(table_key_val, primary_table_path))
                    return CMD_SUCCESS

        log.debug('Table keys {}, to filter primary table {}' .format(filter_keys, primary_table_path))

        for member in response:

            #create member keys for processing commands and dependent tables
            member_keys =update_table_keys(primary_table_keys, member)
            log.debug("Member key values {}, filter keys {}" .format(member_keys, filter_keys))

            skip_record = False
            for filter_key, filter_key_value in filter_keys.items():
                if ((filter_key not in member)) or (str(member[filter_key]) != filter_key_value):
                    log.debug("Skipping record; member keys {}, given key {}"  .format(member_keys, member[filter_key]))
                    skip_record = True
                    break
            if skip_record == True:
                continue

            #process first command, if success continue others othewise
            #return to process next context.

            ret, is_view_rendered = process_command(self, member, self.table_list, member_keys, self.dbpathstr,\
                                                              True, self.view_cmd_list[0], indent)

            if is_view_rendered:
                log.info(' Entire view rendred by template for {}' .format(self.name))


            if ret == CMD_SUCCESS:
            #process all remaining commands under this view.
            #if view is rendered skip processing commands, go to child view.
                if is_view_rendered == False:
                    for cmd in  self.view_cmd_list[1:]:
                        ret, is_view_rendered = process_command(self, member, self.table_list, member_keys, self.dbpathstr,\
                                                        False, cmd, indent +1)

                #Process child views.

                if view_dependency.get(self.name) is not None:

                    #form the keys for the dependency view tables.
                    for view in view_dependency[self.name]:
                    #     #get keys from parent

                        view_key_values = collections.OrderedDict()
                        cli_view = CLI_XML_VIEW_MAP.get(view)
                        if cli_view == None:
                            continue

                        view_keys = cli_view.table_keys
                        log.info("Preparing for child view: {}, child view keys: {}, parent view: {}, parent member keys: {} " \
                         .format(view, view_keys, self.name,  member_keys))

                        for key, value in view_keys.items():
                            # set default key value to wildcard
                            # check if key has a value or a dbpath to parent member key name.
                            view_key_values.update({key.lstrip():"*"})
                            if value and value != "*":
                                keypath_list = value.split('/')
                                if len(keypath_list) > 1:
                                    table_attr = keypath_list[-1]
                                    if table_attr is None:
                                        log.info("Invalid view key {}, value {}, attr is None. Setting to wildcard" .format(key, value))
                                        continue
                                    if  table_attr in member:
                                        view_key_values.update({key.lstrip():member[table_attr]})
                                else:
                                    view_key_values.update({key.lstrip():keypath_list[0]})

                        log.info("Preparing for child view {}, child view keys {} " .format(cli_view.name, view_key_values))
                        cmd_status = cli_view.process_view_commands(view_key_values, indent+1)

        log.debug(' Exit.view {}, view keys {}, status {}' .format(self.name, view_table_keys, CMD_SUCCESS))
        return CMD_SUCCESS



    def process_cli_view(self, keys, depth):

        log.info ("Processing view: {}, keys {}, depth {} "\
                                  .format(self.name, keys, depth))
        table_keys = keys
        cmd_status = CMD_SUCCESS

        if self.table_list:
            log.info("table list {}" .format(self.table_list))
            cmd_status= self.process_view_commands(table_keys, depth)            
        else:
            log.warn("table list empty for {}, next view, maybe command views" .format(self.name))            
            cmd_status= self.process_view_commands_no_table(table_keys, depth)     
   
        log.debug(os.linesep)

        return cmd_status



def process_command(view, view_member, table_list, member_keys, dbpathstr, is_view_first_cmd, cmd_line, indent):

    render_tables = {}
    view_tables = {}
    log.debug("Enter: view: {}, \nmember: {}, \nview_table_list: {}, member_keys: {}, dbpathstr: {} is_view_fist_cmd: {}"\
                            .format(view.name, view_member, table_list, member_keys, dbpathstr, is_view_first_cmd))

    #split command attributes

    if member_keys is None:
        member_keys = {}

    cmd_list = []
    cmd_line_parts = cmd_line.split(":::")
    if len(cmd_line_parts) != CONFIG_VIEW_IDX_LEN:
        return CMD_FAIL, False

    #if a render view is given.
    db_render_callback = cmd_line_parts[CONFIG_VIEW_DB_RENDER_IDX]
    render_view_callback = cmd_line_parts[CONFIG_VIEW_RENDER_VIEW_IDX]
    render_cmd_callback = cmd_line_parts[CONFIG_VIEW_RENDER_CMD_IDX]

    #update tables only for render_view
    if not db_render_callback:
        #Get additional tables for view and command rendering
        #add view_member. if view_member not present it must
        # to process view_command without primary table.
        if view_member:
            view_tables.update({view.primary_table:view_member})

            #For render templates strip keys from the table path, create another dict
            #to pass to render templates

            table_name = ('/').join(view.primary_table.split('/')[:-1])
            log.debug('Adding view table {} to view_tables list' .format(table_name))
            render_tables.update({table_name: view_member})

        ## Add keys for primary table
        if table_list and len(table_list) >1 :
            for table_path in table_list[1:]:
                response = get_rest_table(table_path)

                if response is not None:
                    table_name = ('/').join(table_path.split('/')[:-1])
                    log.debug('Adding view table {} to view_tables list' .format(table_name))
                    render_tables.update({table_name: response})

    #Get command related tables

    if render_view_callback:
        cmd_status  = process_render_callback(render_view_callback, render_tables, member_keys, is_view_first_cmd, indent)
        return cmd_status, True

    cmd_table_list = []
    if cmd_line_parts[CONFIG_VIEW_CMD_TABLES_IDX]:
        cmd_table_list.extend(cmd_line_parts[CONFIG_VIEW_CMD_TABLES_IDX].split(';'))

    cmd_table_present = False
    cmd_table = None
    for idx, cmd_table_path in enumerate(cmd_table_list):

        log.debug("Process command_table {} " .format(cmd_table_path))
        if idx == 0:
            #if first command table same as view table,
            #ignore command table
            if dbpathstr and dbpathstr in cmd_table_path:
                log.warning("Command table same as primary view table, process only member provided from primary view table {}, {}"\
                 .format(dbpathstr, cmd_table_path) )
                break
            cmd_table_present = True
            # new dbpathstr and keys from cmd table
            dbpathstr = '/'.join(cmd_table_path.split('/')[:-1])

            if not member_keys:
                log.info(" No view keys for table {} " .format(cmd_table_path))


        if not db_render_callback:
            response = get_rest_table(cmd_table_path)
            if response is not None:

                view_tables.update({cmd_table_path:response})
                cmd_table_name = ('/').join(cmd_table_path.split('/')[:-1])
                log.debug('Adding table {} to render_tables list' .format(cmd_table_name))
                render_tables.update({cmd_table_name: response})

                if idx == 0:
                    cmd_table = response
                    log.info("set primary table for this cmd as {}" .format(cmd_table))
            else:
                log.warn('Response none for table  {}' .format(cmd_table_path))

            log.debug('Final view_tables list members {}' .format(view_tables.keys()))

    #get command keys from tag if present.

    if cmd_line_parts[CONFIG_VIEW_SEC_TABLE_KEYS_IDX]:
        log.debug('cmd_keys tag {}' .format(cmd_line_parts[CONFIG_VIEW_SEC_TABLE_KEYS_IDX]))
        for cmd_key in cmd_line_parts[CONFIG_VIEW_SEC_TABLE_KEYS_IDX].split(','):
            cmd_key_lst = cmd_key.split("=")
            if len(cmd_key_lst) != 2:
                log.warning("Invalid key format; skip this key {}, view_name {}, key_tag {}" \
                    .format(cmd_key, view.name, cmd_line_parts[CONFIG_VIEW_SEC_TABLE_KEYS_IDX]))
                continue
            #remove invalid keys
            key = cmd_key_lst[0].lstrip()
            value = cmd_key_lst[1].rstrip()

            if value is None or value == '*' or len(value.split('/')) >1:
                log.warning("command key invalid {} for view {}, skip key " .format(cmd_key, view))
                continue
            member_keys.update({key:value})


    if db_render_callback:
        log.info("Render db callback {}" .format(db_render_callback))
        db_render_callback_func = render_cb_dict.get(db_render_callback)
        if db_render_callback_func:
            cb_status = CB_FAIL
            cmd_list_str = ''
            is_view_rendered = False

            try:
                cb_status, cmd_list_str, is_view_rendered = db_render_callback_func(member_keys)
            except Exception as e:
                log.error("Callback {} exception: {} " .format(db_render_callback_func, e))
                return CMD_FAIL, True
            else:
                if cb_status == CB_FAIL:
                    log.warn("Db render callback func failure, return SUCCESS for next view/command")
                    return CMD_FAIL, True
                else:
                    cache_view_commands(cmd_list_str.split(';'), indent, is_view_first_cmd)
                    return CMD_SUCCESS, is_view_rendered
        else:
            log.error("Db render callback func is None, return SUCCESS for next view")
            return CMD_FAIL, True


    if render_cmd_callback:
        cmd_status  = process_render_callback(render_cmd_callback, render_tables, member_keys, is_view_first_cmd, indent)
        return cmd_status, False


    if  cmd_table_present == False and view_member:

        cmdlst, cmdfound = process_cmd(view_member, dbpathstr, cmd_table_list, view_tables, member_keys, cmd_line)
        if cmdfound:
            cache_view_commands(cmdlst, indent, is_view_first_cmd)
        else:
            log.debug("Exit status {}" .format(CMD_FAIL))
            return CMD_FAIL, False

    elif cmd_table is not None:
        #loop through cmd table

        log.info("processing command_table {}, member_keys {}" .format(cmd_table, member_keys))
        cmd_table_keys =get_view_table_keys(cmd_table_path)
        filter_keys = collections.OrderedDict()
        for table_key, table_key_val in cmd_table_keys.items():
            if table_key_val in member_keys:
                view_key_val = member_keys.get(table_key_val)
                if view_key_val:
                    if view_key_val != "*":
                        filter_keys.update({table_key:view_key_val})
                else:
                    log.warn('Key {} missing in table {}, skip cmd table' .format(table_key_val, dbpathstr))
                    return CMD_SUCCESS

        log.debug('Cmd table keys {}, to filter table {}' .format(filter_keys, dbpathstr))

        for cmd_member in cmd_table:
            #update dbpathstr to new table
            #Match the keys

            skip_record = False
            for filter_key, filter_key_value in filter_keys.items():

                if filter_key in cmd_member:
                    if str(cmd_member[filter_key]) != filter_key_value:
                       skip_record  = True
                       log.debug("Skipping record; member keys {}, given key {}"  .format(member_keys, cmd_member[filter_key]))
                       break
                else:
                    skip_record = True
                    log.debug("Skipping record; member keys {}, filter_key {} missing in record"  .format(member_keys, filter_key))
                    break
                    
            if skip_record == True:
                continue
            
            cmdlst, cmdfound = process_cmd(cmd_member, dbpathstr, cmd_table_list, view_tables, member_keys, cmd_line)
            if cmdfound:
                cache_view_commands(cmdlst, indent, is_view_first_cmd)
            else:
                continue

    log.debug("Exit status {}" .format(CMD_SUCCESS))
    return CMD_SUCCESS, False


def process_render_callback(render_callback, render_tables, member_keys, is_view_first_cmd, indent):

    log.info("Render callback {}" .format(render_callback))
    #first check if python callback exists
    render_tables.update(member_keys)
    render_callback_func = render_cb_dict.get(render_callback)

    if render_callback_func:
        cb_status = CB_FAIL
        cmd_list_str = ''

        try:
            cb_status, cmd_list_str = render_callback_func(render_tables)
        except Exception as e:
            log.error("Callback {} exception: {}" .format(render_callback_func, e))
            return CMD_FAIL

        else:
            if cb_status == CB_FAIL:
               return CMD_FAIL

        log.debug("Callback rendered cmd_list {}" .format(cmd_list_str))
        cache_view_commands(cmd_list_str.split(';'), indent, is_view_first_cmd)
        return CMD_SUCCESS

    template_file = render_filelst.get(render_callback)
    if template_file:
        cmd_list_str = get_rendered_template_output(template_file, render_tables, render_callback)
        log.debug("Template rendered cmd_list {}" .format(cmd_list_str))

        cache_view_commands(cmd_list_str.split(';'), indent, is_view_first_cmd)
        return CMD_SUCCESS
    else:
        log.error("Callback or template missing for cmd callback, {}" .format(render_callback))
        return CMD_FAIL



def parse_command_line(command_line):

    cmd_attributes = command_line.split(":::")
    if len(cmd_attributes) != CONFIG_VIEW_IDX_LEN:
        log.error("Invalid number of command attributes {}: {} " .format(cmd_attributes, len(cmd_attributes)))
        sys.exit(1)

    #create cli-xml view if not exist
    cli_view = None

    if cmd_attributes[CONFIG_VIEW_NAME_IDX] in CLI_XML_VIEW_MAP:
        cli_view = CLI_XML_VIEW_MAP[cmd_attributes[CONFIG_VIEW_NAME_IDX]]
    else:
        cli_view = cli_xml_view(cmd_attributes)
        CLI_XML_VIEW_MAP.update({cmd_attributes[CONFIG_VIEW_NAME_IDX]: cli_view})

    cli_view.view_cmd_list.append(command_line)


def render_cli_config(view_name = '', view_keys = {}):
    global CMDS_STRING
    depth = 0
    if view_name:
        if view_name in CLI_XML_VIEW_MAP:
            cli_view = CLI_XML_VIEW_MAP[view_name]
            cli_view.process_cli_view(view_keys, depth)
    else:

        for config_view in config_view_hierarchy:
            #get corresponding view_class for the view
            if config_view in CLI_XML_VIEW_MAP:
                cli_view = CLI_XML_VIEW_MAP[config_view]
                cli_view_keys = cli_view.table_keys

                cli_view.process_cli_view(cli_view_keys, depth)
            else:
                log.warning("render_cli_config: config view {} does not exist, skip rendering" .format(config_view))
                continue

    # write to output.            
    write(CMDS_STRING)
    CMDS_STRING = ''
    DB_Cache.clear()


def print_cli_views(view_name=''):

    if view_name:
        cli_view = CLI_XML_VIEW_MAP.get(view_name)
        if cli_view is not None:
            cli_view.print_view()
    else:
        for view in CLI_XML_VIEW_MAP.values():
            view.print_view()

def read_cli_format_file(format_file):

    f = open(format_file, 'r')
    command_lines = f.read().splitlines()

    for command in command_lines:
        parse_command_line(command)


def show_views(func, args = []):

    log.debug('args {}' .format(args))
    
    views = []	
    view_keys = []
    for arg in args:
      if arg.startswith("views="):
          views_str= arg.lstrip("views=")
          views=views_str.split(',')
      if arg.startswith("view_keys="):
          view_keys_str = arg.lstrip("view_keys=")
          view_keys_str = view_keys_str.replace('"','')
          view_keys = view_keys_str.split(',')
    
    if not views:
      log.warn("Missing view name, args {}" .format(args))
      return

    if func=='show_view' and len(views) > 1:
       log.warn("Multiple views specified for 'show_view' option, {}" .format(views))
       return
    viewKV = {} 
    #parse keys only for single view case
    if len(views) == 1:
        for key in view_keys: 
            key_split = key.split('=')
            if len(key_split) != 2:
                log.error("Invalid keys {}" .format(key_split))
                return
            if key_split[1]:
               viewKV.update({key_split[0]:key_split[1]})
    log.debug('view-keys {}' .format(viewKV))
    for view_name in views:
        render_cli_config(view_name, viewKV)


def run(func = '', args=[]):
    global format_read
    log.debug("args {}" .format(args)) 
    if format_read == False:
        template_path = os.getenv('SHOW_CONFIG_TOOLS', RENDERER_TEMPLATE_PATH)
        format_file = os.path.join(template_path, FORMAT_FILE)

        log.debug("format_file {}" .format(format_file))
        read_cli_format_file(format_file)
        format_read = True
    
    full_cmd = os.getenv('USER_COMMAND', None)
    if full_cmd is not None:
        pipestr().write(full_cmd.split())

    if  func == 'show_view' or func == 'show_multi_views':
        show_views(func, args) 
    else:
        render_cli_config()


if __name__ ==  "__main__":
    pipestr().write(sys.argv) 
    run(args=sys.argv)
