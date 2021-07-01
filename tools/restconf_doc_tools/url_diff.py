#! /usr/bin/env python3
################################################################################
#                                                                              #
#  Copyright 2021 Broadcom. The term Broadcom refers to Broadcom Inc. and/or   #
#  its subsidiaries.                                                           #
#                                                                              #
#  Licensed under the Apache License, Version 2.0 (the "License");             #
#  you may not use this file except in compliance with the License.            #
#  You may obtain a copy of the License at                                     #
#                                                                              #
#     http://www.apache.org/licenses/LICENSE-2.0                               #
#                                                                              #
#  Unless required by applicable law or agreed to in writing, software         #
#  distributed under the License is distributed on an "AS IS" BASIS,           #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    #
#  See the License for the specific language governing permissions and         #
#  limitations under the License.                                              #
#                                                                              #
################################################################################
import glob
import argparse
import os, sys, io
import json
from collections import OrderedDict
import utils.json_delta as json_delta
import pyang
if pyang.__version__ > '2.4':
    from pyang.repository import FileRepository
    from pyang.context import Context
else:
    from pyang import FileRepository
    from pyang import Context
import pdb

currentDir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(currentDir + '/../pyang/pyang_plugins/')
import openapi

ACTION_DICT = {
    '+': 'URL_ADDED',
    '-': 'URL_REMOVED',
    ' ': 'URL_NO_CHANGE',
    True: 'PAYLOAD_MODIFIED',
    False: 'PAYLOAD_NO_CHANGE'
}
def mod_init(ctx, dict_store):
    for entry in ctx.repository.modules:
        mod_name = entry[0]
        mod = entry[2][1]
        if '/common/' not in mod:
            try:
                fd = io.open(mod, "r", encoding="utf-8")
                text = fd.read()
            except IOError as ex:
                sys.stderr.write("error %s: %s\n" % (mod_name, str(ex)))
                sys.exit(3)
            mod_obj = ctx.add_module(mod_name, text)
            if mod_name not in dict_store:
                dict_store[mod_name] = mod_obj

def generate_urls(ctx, mod_dict, mod_doc_dict):
    for mod_name in mod_dict:
        module = mod_dict[mod_name]
        if module.keyword == "submodule":
            continue
        openapi.currentTag = module.i_modulename
        openapi.globalCtx = ctx
        openapi.globalCtx.opts = args
        openapi.resetSwaggerDict()
        openapi.resetDocJson()
        openapi.walk_module(module)
        doc_config = openapi.docJson["config"]
        if "/restconf/data/" in doc_config:
            del(doc_config["/restconf/data/"])
        doc_operstate = openapi.docJson["operstate"]
        if "/restconf/data/" in doc_operstate:
            del(doc_operstate["/restconf/data/"])
        doc_operations = openapi.docJson["operations"]
        if "/restconf/data/" in doc_operations:
            del(doc_operations["/restconf/data/"])

        if len(doc_config) > 0 or len(doc_operstate) > 0 or len(doc_operations) > 0:
            if mod_name not in mod_doc_dict:
                mod_doc_dict[mod_name] = OrderedDict()            
            mod_doc_dict[mod_name]["config"] = doc_config
            mod_doc_dict[mod_name]["state"] = doc_operstate
            mod_doc_dict[mod_name]["operations"] = doc_operations

def write_payload(writer, lines, method, reqPrefix="Request"):
    writer.write(
        "\n<details>\n<summary>%s payload for %s</summary>\n<p>" % (reqPrefix, method.upper()))
    writer.write("\n\n```json\n")
    writer.write(lines)
    writer.write("\n```\n")
    writer.write("</p>\n</details>\n\n")

def sorting(item):
    if isinstance(item, dict):
        return sorted((key, sorting(values)) for key, values in item.items())
    if isinstance(item, list):
        return sorted(sorting(x) for x in item)
    else:
        return item
        
def dump_payload_diff(payload_writer, source_dict, target_dict, mode, url, action, unified):
    payload_differs = False
    writer = io.StringIO()
    if action == '+':
        for method in ['put', 'post', 'patch', 'get']:
            if method == 'get':
                prefix = 'Response'
            else:
                prefix = 'Request'
            if method in source_dict[mode][url]:
                left = {}
                right = json.loads(json.dumps(source_dict[mode][url][method]['body']))
                if sorting(left) != sorting(right):
                    payload_differs = True
                    diff_lines = '\n'.join(list(json_delta._udiff.udiff(left, right, indent=2, use_ellipses=False))[1:])
                    write_payload(writer, diff_lines, method, prefix)
    elif action == '-':
        for method in ['put', 'post', 'patch', 'get']:
            if method == 'get':
                prefix = 'Response'
            else:
                prefix = 'Request'
            if method in source_dict[mode][url]:
                left = json.loads(json.dumps(source_dict[mode][url][method]['body']))
                right = {}
                if sorting(left) != sorting(right):
                    payload_differs = True
                    diff_lines = '\n'.join(list(json_delta._udiff.udiff(left, right, indent=2, use_ellipses=False))[:-1])
                    write_payload(writer, diff_lines, method, prefix)
    else:
        for method in ['put', 'post', 'patch', 'get']:
            if method == 'get':
                prefix = 'Response'
            else:
                prefix = 'Request'
            if method in source_dict[mode][url]:
                left = json.loads(json.dumps(target_dict[mode][url][method]['body']))
                right = json.loads(json.dumps(source_dict[mode][url][method]['body']))
                if sorting(left) != sorting(right):
                    payload_differs = True
                    diff_lines = '\n'.join(json_delta._udiff.udiff(left, right, indent=2, use_ellipses=False))
                    write_payload(writer, diff_lines, method, prefix)
    
    if payload_differs or unified:
        payload = writer.getvalue()
        if len(payload) > 0:
            payload_writer.write('\n### {}\n'.format(url))
        payload_writer.write(payload)
    return payload_differs

def dump_diff_url(writer, payload_writer, source_dict, target_dict, mode, unified=False):
    added_urls = set(source_dict[mode].keys()) - set(target_dict[mode].keys())
    removed_urls = set(target_dict[mode].keys()) - set(source_dict[mode].keys())
    action = None
    for url in set(source_dict[mode].keys()) | set(target_dict[mode].keys()):
        if url in added_urls:
            action = '+'
        elif url in removed_urls:
            action = '-'
        else:
            action = ' '
        payload_differs = dump_payload_diff(payload_writer, source_dict, target_dict, mode, url, action, unified)
        if not unified or payload_differs:
            if url in added_urls or url in removed_urls or payload_differs:
                writer.write("| %s | %s [%s](%s) |\n" % (url, ACTION_DICT[action], ACTION_DICT[payload_differs], url.replace('/','').replace(':','').replace('=','').replace('{','').replace('}','')))
        else:
            writer.write("| %s | %s [%s](%s) |\n" % (url, ACTION_DICT[action], ACTION_DICT[payload_differs], url.replace('/','').replace(':','').replace('=','').replace('{','').replace('}','')))
        
def dump_url_from_single_source(writer, payload_writer,  source_dict, source_dict_ext, mode, action):    
    for url in source_dict:
        writer.write("| %s | %s %s |\n" % (url, ACTION_DICT[action], ACTION_DICT[True]))
        dump_payload_diff(payload_writer, source_dict_ext, None, mode, url, action, True)

def write_urls(writer, source_dict, target_dict=None, unified=False):
    payload_writer = io.StringIO()
    if target_dict is None:
        dump_url_from_single_source(writer, payload_writer,  source_dict['config'].keys(), source_dict, 'config', '+',)
        dump_url_from_single_source(writer, payload_writer,  source_dict['state'].keys(), source_dict, 'state', '+')
        dump_url_from_single_source(writer, payload_writer,  source_dict['operations'].keys(), source_dict, 'operations', '+')
    elif source_dict is None:
        dump_url_from_single_source(writer, payload_writer,  target_dict['config'].keys(), target_dict, 'config', '-')
        dump_url_from_single_source(writer, payload_writer,  target_dict['state'].keys(), target_dict, 'state', '-')
        dump_url_from_single_source(writer, payload_writer,  target_dict['operations'].keys(), target_dict, 'operations', '-')
    else:
        if args.unified:
            dump_diff_url(writer, payload_writer, source_dict, target_dict, 'config', True)
            dump_diff_url(writer, payload_writer, source_dict, target_dict, 'state', True)
            dump_diff_url(writer, payload_writer, source_dict, target_dict, 'operations', True)
        else:
            dump_diff_url(writer, payload_writer, source_dict, target_dict, 'config')
            dump_diff_url(writer, payload_writer, source_dict, target_dict, 'state')
            dump_diff_url(writer, payload_writer, source_dict, target_dict, 'operations')
    writer.write("\n## Below section contains payload diffs for URLs\n")
    writer.write(payload_writer.getvalue())
    payload_writer.close()
def process(args):
    #Validate the source and target paths
    if not os.path.exists(args.sourcedir) or not os.path.exists(args.targetdir):
        print("No such source/target directory")
        sys.exit(1)

    sourcedir = "/" + "/".join(list(filter(None,args.sourcedir.split('/'))))
    targetdir = "/" + "/".join(list(filter(None,args.targetdir.split('/'))))

    if not sourcedir.endswith('sonic-mgmt-common'):
        print("--sourceRepo must end at sonic-mgmt-common")
        sys.exit(2)
    sourcedir = sourcedir + '/build/yang'
    if not targetdir.endswith('sonic-mgmt-common'):
        print("--targetRepo must end at sonic-mgmt-common")
        sys.exit(2)
    targetdir = targetdir + '/build/yang'

    if not os.path.exists(sourcedir) or not os.path.exists(targetdir):
        print("Makesure build/yang exists, otherwise please perform YANG compilation.")
        sys.exit(2)
    
    # Init Repo
    source_path = sourcedir+'/:/'+sourcedir+'/common:/'+sourcedir+'/extensions'
    target_path = targetdir+'/:/'+targetdir+'/common:/'+targetdir+'/extensions'
    source_repo = FileRepository(source_path, use_env=False)
    source_ctx = Context(source_repo)
    target_repo = FileRepository(target_path, use_env=False)
    target_ctx = Context(target_repo)
    source_mod_dict = OrderedDict()
    target_mod_dict = OrderedDict()
    
    # Init Modules
    mod_init(source_ctx, source_mod_dict)
    mod_init(target_ctx, target_mod_dict)
    source_ctx.validate()
    target_ctx.validate()

    # Generate URLs
    source_doc_dict = OrderedDict()
    target_doc_dict = OrderedDict()
    print("Processing Source YANGs...")
    generate_urls(source_ctx, source_mod_dict, source_doc_dict)
    print("Processing Target YANGs...")
    generate_urls(target_ctx, target_mod_dict, target_doc_dict)
    print("Generating Diff Docs...")

    if args.shell:
        print("Command-line feature is not yet supported. Thank You!!")
        sys.exit(0)
    else:
        fp_dict = OrderedDict()
        for mod in set(source_doc_dict.keys()) | set(target_doc_dict.keys()):
            fp_dict[mod] = io.StringIO()
            fp_dict[mod].write("# {} - RESTCONF URL Diff Document\n".format(mod))
            fp_dict[mod].write('| URL | Action |\n')
            fp_dict[mod].write('| --- | --- |\n')
        
        for mod in set(source_doc_dict.keys()) - set(target_doc_dict.keys()):        
            write_urls(fp_dict[mod], source_doc_dict[mod])

        for mod in set(target_doc_dict.keys()) - set(source_doc_dict.keys()):    
            write_urls(fp_dict[mod], target_doc_dict[mod])
        
        for mod in set(source_doc_dict.keys()) & set(target_doc_dict.keys()):
            write_urls(fp_dict[mod], source_doc_dict[mod], target_doc_dict[mod],args)

        for mod in fp_dict:
            content = fp_dict[mod].getvalue()
            with open("{}/{}.md".format(args.outdir, mod), "w") as fp:
                fp.write(content)
            fp_dict[mod].close()
        print("Access URL Diffs Docs at {}".format(args.outdir))

if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--sourcedir', dest='sourcedir', help='Source sonic-mgmt-common directory', required=True)
    parser.add_argument('--targetdir', dest='targetdir', help='Target sonic-mgmt-common directory', required=True)
    parser.add_argument('--unified', dest='unified', action='store_true', help='Prints All URLs, otherwise only Diff Urls are printed')
    parser.add_argument('--shell', dest='shell', action='store_true', help='Starts a command-line interface')
    parser.add_argument('--outdir', dest='outdir', help='The output directory to dump the diff docs')
    parser.add_argument('--no_oneof', dest='no_oneof')
    args = parser.parse_args()
    if not args.shell:
        if args.outdir is None or not os.path.exists(args.outdir):
            print("Please specify valid output directory")
            sys.exit(3)    
    process(args)
