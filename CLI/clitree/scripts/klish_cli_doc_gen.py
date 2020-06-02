import pdb, os, sys, logging, glob, copy
from bs4 import BeautifulSoup
from collections import OrderedDict
try:
    from StringIO import StringIO ## for Python 2
except ImportError:
    from io import StringIO ## for Python 3
from lxml import etree

# set up global logger
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__file__)

# Globals
reference_guide_name = 'industry_standard_cli_reference_guide.md'

class CliDoc:
    # Default KLish XMLs directory path
    currentDir = os.path.dirname(os.path.realpath(__file__)) 
    klish_xml_path_dir = os.path.join(currentDir, "../../../../build/cli/command-tree/")
    cmdList = []
    noformCmdSoupDict = OrderedDict()
    modelsDict = OrderedDict()
    viewsDict = OrderedDict()
    viewsCmdDict = OrderedDict()
    viewsSoupDict = OrderedDict()
    ptyperoot = None
    feature_to_cli = OrderedDict()
    pytypesDict = dict()

    """
    Implementation for CLI document generator
    """    
    def __init__(self):
        pass
    
    @staticmethod
    def create_viewDict(command, view_name):        
        viewFp = None
        if view_name not in CliDoc.viewsDict:
            viewFp2 = StringIO()   
            viewFp2.write("<viewroot>")
            CliDoc.viewsDict[view_name] = viewFp2
            viewFp = viewFp2
            CliDoc.viewsCmdDict[view_name] = list()
        else:
            viewFp = CliDoc.viewsDict[view_name]                        
        
        if command not in CliDoc.viewsCmdDict[view_name]:
            CliDoc.viewsCmdDict[view_name].append(command)
            viewFp.write(str(command))

    @staticmethod
    def parse_klish_xmls():
        """
        Reads Klish XMLs and 
        creates a CLI model in a BeautifulSoup object format
        """
        log.info("XML DIR: " + CliDoc.klish_xml_path_dir)
        models = glob.glob(os.path.join(CliDoc.klish_xml_path_dir,'*.xml'))
        ptypeFp = StringIO()
        ptypeFp.write("<ptyperoot>")  
        for model in models:
            has_ptype = False
            with open(model, "r") as fp:
                soup = BeautifulSoup(fp, "xml")

                if soup.find('PTYPE'):
                    has_ptype = True

                if model not in CliDoc.modelsDict:
                    CliDoc.modelsDict[model] = soup
                    for command in soup.select('COMMAND[view]'):
                        CliDoc.create_viewDict(command, command['view'])
                        
                    for param in soup.select('PARAM[view]'):
                        CliDoc.create_viewDict(param.find_parent('COMMAND'), param['view'])

                    for ptype in soup.find_all('PTYPE'):
                        ptypeFp.write(str(ptype))                      
            
            if has_ptype:
                parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
                root = etree.parse(model, parser)
                PTYPE_EXPR = ".//{http://www.dellemc.com/sonic/XMLSchema}PTYPE"
                
                for ptype in root.findall(PTYPE_EXPR):
                    p_name = ptype.attrib['name']
                    if p_name not in CliDoc.pytypesDict:
                        CliDoc.pytypesDict[p_name] = str(model) + ': ' + str(ptype.sourceline)
                    else:
                        log.warning("Redefinition of PTYPE: %s at %s first defined at %s" \
                            % ( p_name, str(model) + ': ' + str(ptype.sourceline), CliDoc.pytypesDict[p_name]))

        ptypeFp.write("</ptyperoot>")
        ptype_root = BeautifulSoup(ptypeFp.getvalue(), "xml")        
        CliDoc.ptyperoot = ptype_root.ptyperoot
        
        for view in CliDoc.viewsDict:
            viewFp = CliDoc.viewsDict[view]
            viewFp.write("</viewroot>")
            view_root = BeautifulSoup(viewFp.getvalue(), "xml")
            CliDoc.viewsSoupDict[view] = view_root.viewroot
    
    @staticmethod
    def return_in_param_form(param_tag, subcmd=False):
        if subcmd:
            return ' %s' % (param_tag['name'])
        else:
            return ' <%s>' % (param_tag['name'])

    @staticmethod
    def handle_optional_params(param_tag):
        parent_optional = False
        parent = param_tag.parent
        if parent.name == "PARAM":
            if 'mode' in parent.attrs:
                if parent['mode'] == "switch":
                    for parent in param_tag.parents:
                        if parent.name != "PARAM" or 'optional' not in parent.attrs:
                            break
                        if parent["optional"] == "true":
                            parent_optional = True
        return parent_optional

    @staticmethod
    def get_param_value(param_tag, cli_string, paramDescList):
        param_val = ""
        ignore_desc = False
        if 'mode' in param_tag.attrs:
            if param_tag['mode'] == "switch":
                param_val = ''
                ignore_desc = True
            elif param_tag['mode'] == "subcommand":
                param_val =  CliDoc.return_in_param_form(param_tag, True)
                ignore_desc = True
        else:         
            param_val = CliDoc.return_in_param_form(param_tag)

        if len(param_val) > 0 and not ignore_desc:

            param_info = { 
                'name': param_tag['name'],
                'description': '',
                'dtype': ''
            }
            # Extract required details from PTYPE
            ptype_tag = CliDoc.ptyperoot.find('PTYPE', attrs={'name':param_tag['ptype']})
            if ptype_tag is not None:
                
                # setting description
                if 'help' in ptype_tag.attrs:
                    param_info['description'] = ptype_tag['help']
                
                # setting type
                p_type = ""
                if 'method' in ptype_tag.attrs:
                    if "integer" in ptype_tag['method'].lower():
                        p_type = "Integer"
                    if ptype_tag['method'] == "select":
                        p_type = "Select"                        
                else:
                    p_type = 'String'
                if 'pattern' in ptype_tag.attrs:
                    if p_type == "Select":
                        p_type = p_type + ' [' + ptype_tag['pattern'] + ' ]'
                
                param_info['dtype'] = p_type
            
            paramDescList.append(param_info)

        return param_val

    @staticmethod
    def handle_param(param_tag, cli_string, paramerDescList=[]):
        
        optional = False
        if 'optional' in param_tag.attrs:
            if param_tag["optional"] == "true":
                optional = True
        if CliDoc.handle_optional_params(param_tag):
            optional = True
        
        retrieved_param_value = CliDoc.get_param_value(param_tag, cli_string, paramerDescList)
        if len(retrieved_param_value) > 0:
            if optional:
                cli_string = cli_string + ' [' + retrieved_param_value
            else:
                cli_string = cli_string + retrieved_param_value

        paramsList = param_tag.find_all('PARAM', recursive=False)
        if len(paramsList) > 1 and param_tag.parent.name != "PARAM":
            cli_string = cli_string + ' {'
        for index, child in enumerate(paramsList):
            if index !=0 :
                if 'mode' in param_tag.attrs:
                    if param_tag['mode'] == "switch":
                        cli_string = cli_string + ' | '    
            if len(child.find_all('PARAM', recursive=False)) > 0:
                cli_string = cli_string + ' {'
            cli_string = CliDoc.handle_param(child, cli_string, paramerDescList)
            if len(child.find_all('PARAM', recursive=False)) > 0:
                cli_string = cli_string + ' }'
        if len(paramsList) > 1 and param_tag.parent.name != "PARAM":
            cli_string = cli_string + ' }'
        
        if optional:
            cli_string = cli_string + ' ]'

        return cli_string

    @staticmethod
    def handle_params(command_tag, cli_string, cmdList=[], paramerDescList=[]):
        for param_tag in command_tag.find_all('PARAM', recursive=False):
            cli_string = CliDoc.handle_param(param_tag, cli_string, paramerDescList)
            cli_string = CliDoc.filter_extra_spaces(cli_string)        
            cmdList.append(cli_string)
        #print(cli_string)

    @staticmethod
    def add_params_to_cli(param_tag, cmd_tokens):
        optional = False
        if 'optional' in param_tag.attrs:
            if param_tag["optional"] == "true":
                optional = True
        if CliDoc.handle_optional_params(param_tag):
            optional = True

        if 'mode' in param_tag.attrs:
            if param_tag['mode'] == "switch":
                return
            elif param_tag['mode'] == "subcommand":
                if optional:
                    cmd_tokens.append(']')            
                cmd_tokens.append(CliDoc.return_in_param_form(param_tag, True))
                if optional:
                    cmd_tokens.append(' [')
        else:
            if optional:
                cmd_tokens.append(']')            
            cmd_tokens.append(CliDoc.return_in_param_form(param_tag))
            if optional:
                cmd_tokens.append(' [')

    @staticmethod
    def filter_extra_spaces(cmd_string):
            return " ".join(list(filter(None,cmd_string.split(' '))))        

    @staticmethod
    def get_cmd_for_mode(param_tag, cli_string):
        cmd_tokens = []
        cmd_string = ""
        for parent in param_tag.parents:
            if parent.name == "COMMAND":
                break
            CliDoc.add_params_to_cli(parent, cmd_tokens)
            
        if len(cmd_tokens) > 0:
            cmd_tokens = reversed(cmd_tokens)
            cmd_string = cli_string + " ".join(cmd_tokens)
        else:
            cmd_string = cli_string 
        
        return CliDoc.filter_extra_spaces(CliDoc.handle_param(param_tag, cmd_string))

    @staticmethod
    def print_doc_lines(docString, fp):
        if docString is not None:
            lines = list(filter(None,docString.replace('\t','    ').split('\n')))                            
            number_of_leading_space = 0
            for index, line in enumerate(lines):
                line = line.rstrip()                                
                if index == 0:
                    number_of_leading_space = len(line) - len(line.lstrip())                                
                fp.write("%s\n" %(line[number_of_leading_space:]))

    @staticmethod
    def commandBuilder():
        """
        Walks over Command tags and generates a CLI documentation for it
        """
        commandsGuideDict = dict()
        for model in CliDoc.modelsDict:
            soup = CliDoc.modelsDict[model]
            for command_tag in soup.find_all('COMMAND'):
                cmdList = []
                modeCmdList = set()  
                paramsList = []        
                action_tag = command_tag.find('ACTION')
                if action_tag is not None or 'view' in command_tag.attrs:
                    # Prepare data for syntax and params section
                    if action_tag is not None and 'builtin' in action_tag.attrs and 'view' not in command_tag.attrs:
                        if action_tag["builtin"] == "clish_nop":
                            continue
                    cli_string = command_tag["name"]

                    if cli_string.startswith("no "):
                        if cli_string not in CliDoc.noformCmdSoupDict:
                            CliDoc.noformCmdSoupDict[cli_string] = [command_tag]
                        else:
                            CliDoc.noformCmdSoupDict[cli_string].append(command_tag)
                        continue

                    if cli_string == "exit" \
                        or '!' in cli_string \
                            or cli_string == "end":
                        continue
                    if command_tag.find('PARAM') is not None:
                        CliDoc.handle_params(command_tag, cli_string, cmdList, paramsList)                        
                    else:
                        cmdList.append(CliDoc.filter_extra_spaces(cli_string))
                    
                    # Prepare data for mode section
                    view_name = command_tag.find_parent('VIEW')['name']
                    if view_name == "configure-view":
                        modeCmdList.add("configure terminal")
                    elif view_name == "enable-view":
                        pass
                    else:
                        pass
                    
                    if view_name not in CliDoc.viewsSoupDict:
                        log.warning("There is no command which takes to view with name: " + view_name)
                    else:                    
                        view_soup = CliDoc.viewsSoupDict[view_name]
                        for ViewCmd in view_soup.find_all('COMMAND'):
                            if ViewCmd is None:
                                log.info("There is no command tag associated with view %s" % (view_name))
                            else:
                                baseCmd = ViewCmd['name']
                                param_tags = ViewCmd.find_all('PARAM', attrs={'view':view_name})
                                if len(param_tags) > 0:
                                    for param_tag in param_tags:
                                        modeCmd = CliDoc.get_cmd_for_mode(param_tag, baseCmd)
                                        modeCmd = CliDoc.filter_extra_spaces(modeCmd)
                                        if modeCmd == "exit" or modeCmd == "!" or modeCmd == "end":
                                            pass
                                        else:
                                            modeCmdList.add(modeCmd)
                                else:
                                    if baseCmd == "exit" or baseCmd == "!" or baseCmd == "end":
                                        pass
                                    else:
                                        modesList = []                     
                                        if ViewCmd.find('PARAM') is not None:
                                            tempModesList = []
                                            CliDoc.handle_params(ViewCmd, baseCmd, tempModesList)
                                            if len(tempModesList) > 0:
                                                modesList.append(tempModesList[-1])
                                        else:
                                            modesList.append(CliDoc.filter_extra_spaces(baseCmd))
                                        modeCmdList = modeCmdList.union(set(modesList))

                    cliGuideFp = StringIO()
                    if command_tag["name"] not in commandsGuideDict:                      
                        commandsGuideDict[command_tag["name"]] = []
                    
                    cmd_entry = {
                        'view_name': view_name,
                        'fp': cliGuideFp
                    }
                    commandsGuideDict[command_tag["name"]].append(cmd_entry)

                    # Add Command Section
                    cliGuideFp.write("## %s \n\n" %(command_tag["name"]))
                    # Extract DocGen tags if there are any
                    docgen = command_tag.find('DOCGEN')
                    
                    # Description sub section
                    if docgen is not None:
                        cmd_description = docgen.find('DESCRIPTION')
                    else:
                        cmd_description = None                        
                    if cmd_description is not None:                           
                        cmd_description = cmd_description.string
                        cliGuideFp.write("### %s \n" %("Description"))
                        cliGuideFp.write("\n```\n")
                        CliDoc.print_doc_lines(cmd_description, cliGuideFp)
                        cliGuideFp.write("\n```\n")
                    elif 'help' in command_tag.attrs:
                        cliGuideFp.write("### %s \n" %("Description"))                        
                        cliGuideFp.write("\n```\n")
                        cliGuideFp.write("%s \n\n" %(command_tag['help']))
                        cliGuideFp.write("\n```\n")
                    else:
                        pass
                        
                    # Modes sub section
                    if len(modeCmdList) > 0:
                        cliGuideFp.write("### %s \n" %("Parent Commands (Modes)"))
                        cliGuideFp.write("\n```\n")
                        for modeCmd in sorted(modeCmdList):
                            if modeCmd.startswith('no '):
                                continue
                            cliGuideFp.write("%s\n" %(modeCmd))
                        cliGuideFp.write("\n```\n")

                    # Syntax sub section
                    if len(cmdList) > 0:
                        cmd_to_consider = cmdList[-1]
                        cliGuideFp.write("### %s \n" %("Syntax"))
                        cliGuideFp.write("\n```\n")
                        cliGuideFp.write("%s\n" %(cmd_to_consider))
                        cliGuideFp.write("\n```\n")

                    # Parameters sub section
                    if len(paramsList) > 0:
                        cliGuideFp.write("### %s \n" %("Parameters"))
                        cliGuideFp.write("\n| Name | Description | Type |\n")
                        cliGuideFp.write("|:---:|:-----:|:-----:|\n")                                
                        paramSet = set()
                        for param in paramsList:
                            if param['name'] not in paramSet:
                                paramSet.add(param['name'])
                            else:
                                continue
                            cliGuideFp.write("| %s | %s  | %s  |\n" % (param["name"], param["description"].replace('|', ' or '), param["dtype"]))
                        cliGuideFp.write("\n\n")
                        
                    if docgen is not None:
                        # Usage Guidelines sub section
                        usage_guideline = docgen.find('USAGE')
                        if usage_guideline is not None:
                            cliGuideFp.write("### %s \n" %("Usage Guidelines"))
                            cliGuideFp.write("\n```\n")
                            CliDoc.print_doc_lines(usage_guideline.string, cliGuideFp)
                            cliGuideFp.write("\n```\n")
                        
                        # Examples sub section
                        examples = docgen.find_all('EXAMPLE')
                        if len(examples) > 0:
                            cliGuideFp.write("### %s \n" %("Examples"))
                        for example in examples:
                            if 'summary' in example.attrs:
                                cliGuideFp.write("#### %s \n" %(example["summary"]))
                            cliGuideFp.write("\n```\n")
                            CliDoc.print_doc_lines(example.string, cliGuideFp)
                            cliGuideFp.write("\n```\n")

                        # Features sub section
                        features = docgen.find_all('FEATURE')
                        if len(features) > 0:
                            cliGuideFp.write("### %s \n" %("Features this CLI belongs to"))
                        for feature in features:
                            if feature.string not in CliDoc.feature_to_cli:
                                CliDoc.feature_to_cli[feature.string] = list()
                            CliDoc.feature_to_cli[feature.string].append(command_tag["name"])                                
                            CliDoc.print_doc_lines('* ' +feature.string, cliGuideFp)
                        if len(features) > 0:
                            cliGuideFp.write("\n\n")

                        # ALTCMD sub section
                        altcmds = docgen.find_all('ALTCMD')
                        if len(altcmds) > 0:
                            cliGuideFp.write("### %s \n" %("Alternate command"))
                        for altcmd in altcmds:
                            if 'type' in altcmd.attrs:
                                cliGuideFp.write("#### %s \n" %(altcmd["type"]))
                            cliGuideFp.write("\n```\n")
                            CliDoc.print_doc_lines(altcmd.string, cliGuideFp)
                            cliGuideFp.write("\n```\n")                            

        with open(CliDoc.klish_xml_path_dir + '/' + reference_guide_name, "w") as cliGuideFp:
            cliGuideFp.write("# The SONiC Industry Standard CLI Reference Guide \n\n")
            cliGuideFp.write("# Table Of Commands \n\n")
            command_key_set = set()
            for command_key in sorted (commandsGuideDict.keys()):
                if command_key not in command_key_set:
                    cliGuideFp.write("[%s](#%s)\n\n" % (command_key, command_key.replace(' ','-')))
                    command_key_set.add(command_key)
            
            cliGuideFp.write("# CLIs By Feature \n\n")
            feature_key_set = set()
            for feature_key in sorted (CliDoc.feature_to_cli.keys()):
                if feature_key not in feature_key_set:
                    cliGuideFp.write("## %s \n\n" % format(feature_key))
                    for feature_cli in CliDoc.feature_to_cli[feature_key]:
                        cliGuideFp.write("[%s](#%s)\n\n" % (feature_cli, feature_cli.replace(' ','-')))
                    feature_key_set.add(feature_key)

            for content_key in sorted (commandsGuideDict.keys()):
                for cmd_entry in commandsGuideDict[content_key]:
                    contents = cmd_entry['fp'].getvalue()
                    cmd_view = cmd_entry['view_name']
                    noForm = 'no ' + content_key
                    if noForm in CliDoc.noformCmdSoupDict:
                        noCmdFp = StringIO()
                        noCmdPresent = False
                        for noFormSoup in CliDoc.noformCmdSoupDict[noForm]:
                            noFormSoup_view = noFormSoup.find_parent('VIEW')['name']
                            if cmd_view != noFormSoup_view:
                                continue
                            noCmd = None
                            insertindex = 0
                            noCmdPresent = True
                            for index, line in enumerate(filter(None,contents.split('\n'))):
                                noCmdFp.write(line + '\n')
                                if noCmd is not None and index == insertindex:
                                    noCmdFp.write(noCmd + "\n")
                                    noCmd = None              
                                if line.startswith("### Syntax") and noCmd is None:
                                    cmdListNoForm = []
                                    paramsListNoForm = []
                                    no_cli_string = noFormSoup['name']
                                    if noFormSoup.find('PARAM') is not None:
                                        CliDoc.handle_params(noFormSoup, no_cli_string, cmdListNoForm, paramsListNoForm)                        
                                    else:
                                        cmdListNoForm.append(CliDoc.filter_extra_spaces(no_cli_string))
                                    noCmd = cmdListNoForm[-1]
                                    insertindex = index + 2
                        if noCmdPresent:
                            contents = noCmdFp.getvalue()
                    cliGuideFp.write(contents)
                            
if __name__== "__main__":
    if len(sys.argv) > 1:
        CliDoc.klish_xml_path_dir =  sys.argv[1]   
    CliDoc.parse_klish_xmls()
    CliDoc.commandBuilder()
    log.info("Please find document at " + CliDoc.klish_xml_path_dir + '/' + reference_guide_name)    
