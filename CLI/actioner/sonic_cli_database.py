#!/usr/bin/python
import sys
from scripts.render_cli import show_cli_output
from swsssdk import SonicDBConfig

def invoke(func, args):
    if func == 'map':
        return show_database_map(args)

def show_database_map(args):
    try:
        db_names = SonicDBConfig.get_dblist()
        display_dict = dict()
        for db_name in db_names:
            db_dict = dict()
            db_dict["name"] = db_name
            db_dict["id"] = SonicDBConfig.get_dbid(db_name)
            db_dict["port"] = SonicDBConfig.get_port(db_name)
            db_dict["socket"] = SonicDBConfig.get_socket(db_name)
            db_dict["instance"] = SonicDBConfig.get_instancename(db_name)
            display_dict[SonicDBConfig.get_dbid(db_name)] = db_dict
        show_cli_output(args[0], display_dict)
    except:
        print("%Error: Cannot read database configuration")
        return -1

def run(func, args):
    try:
        return invoke(func, args)
    except Exception as ex:
        print(ex)
        print("%Error: Transaction Failure")
        return -1
