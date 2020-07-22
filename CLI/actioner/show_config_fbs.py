import cli_client as cc
from collections import OrderedDict
from natsort import natsorted


def show_fbs_classifier(render_tables):
    fbs_client = cc.ApiClient()
    body = {"sonic-flow-based-services:input": {}}
    keypath = cc.Path('/restconf/operations/sonic-flow-based-services:get-classifier')
    response = fbs_client.post(keypath, body)
    cmd_str = ''
    if response.ok():
        if response.content is not None and bool(response.content):
            output = response.content["sonic-flow-based-services:output"]["CLASSIFIERS"]
            render_data = OrderedDict()
            output_dict = dict()
            for entry in output:
                output_dict[entry["CLASSIFIER_NAME"]] = entry
            sorted_keys = natsorted(output_dict.keys())
            for key in sorted_keys:
                render_data[key] = output_dict[key]

            for class_name in render_data:
                class_data = render_data[class_name]
                match_type = class_data['MATCH_TYPE'].lower()
                cmd_str += '!;classifier {} match-type {};'.format(class_name, match_type)
                if match_type == 'copp':
                    if 'TRAP_IDS' in class_data.keys():
                        trap_id_list = class_data['TRAP_IDS'].split(',')
                        for trap_id in trap_id_list:
                            cmd_str += ' match protocol {};'.format(trap_id)
                elif match_type.lower() == 'acl':
                    pass

    return 'CB_SUCCESS', cmd_str, True


def show_fbs_policy(render_tables):
    fbs_client = cc.ApiClient()
    body = {"sonic-flow-based-services:input": {}}
    keypath = cc.Path('/restconf/operations/sonic-flow-based-services:get-policy')
    response = fbs_client.post(keypath, body)
    cmd_str = ''
    if response.ok():
        if response.content is not None and bool(response.content):
            render_data = OrderedDict()

            output = response.content["sonic-flow-based-services:output"]["POLICIES"]
            policy_names = []
            data = dict()
            for entry in output:
                policy_names.append(entry["POLICY_NAME"])
                data[entry["POLICY_NAME"]] = entry

            policy_names = natsorted(policy_names)
            for name in policy_names:
                render_data[name] = OrderedDict()
                policy_data = data[name]
                render_data[name]["TYPE"] = policy_data["TYPE"].lower()
                render_data[name]["DESCRIPTION"] = policy_data.get("DESCRIPTION", "")

                render_data[name]["FLOWS"] = OrderedDict()
                flows = dict()
                for flow in policy_data.get("FLOWS", list()):
                    flows[(flow["PRIORITY"], flow["CLASS_NAME"])] = flow

                flow_keys = natsorted(flows.keys(), reverse=True)
                for flow in flow_keys:
                    render_data[name]["FLOWS"][flow] = flows[flow]

                render_data[name]["APPLIED_INTERFACES"] = policy_data.get("APPLIED_INTERFACES", [])
            for policy_name in render_data:
                match_type = render_data[policy_name]['TYPE'].lower()
                cmd_str += '!;policy {} type {};'.format(policy_name, match_type)
                if match_type == 'copp':
                    for flow in render_data[policy_name]['FLOWS']:
                        flow_data = render_data[policy_name]['FLOWS'][flow]
                        cmd_str += ' class {};'.format(flow_data['CLASS_NAME'])
                        if 'TRAP_GROUP' in flow_data:
                            if flow_data['TRAP_GROUP'] != 'null':
                                cmd_str += '  set copp-action {};'.format(flow_data['TRAP_GROUP'])
                                cmd_str += ' !;'
                elif match_type == 'acl':
                    pass

    return 'CB_SUCCESS', cmd_str, True
