def show_copp_police(render_tables):
    cmd_str = ''
    cmd_prfx = 'police'
    if 'sonic-copp:sonic-copp/COPP_GROUP' in render_tables:
        print render_tables
        police_inst = render_tables['sonic-copp:sonic-copp/COPP_GROUP']
        if 'cir' in police_inst:
            cmd_prfx += ' cir ' + police_inst['cir']
            if 'cbs' in police_inst:
                cmd_prfx += ' cbs ' + police_inst['cbs']
                if 'pir' in police_inst:
                    cmd_prfx += ' pir ' + police_inst['pir']
                    if 'pbs' in police_inst:
                        cmd_prfx += ' pbs ' + police_inst['pbs']
        if 'meter_type' in police_inst:
            meter_type = police_inst['meter_type']
            if meter_type == 'packets':
                meter_type = 'pps'
            if meter_type == 'bytes':
                meter_type = 'bps'
            cmd_prfx += ';police meter-type ' + meter_type
        if 'mode' in police_inst:
            cmd_prfx += ';police mode ' + police_inst['mode']
            if 'green_action' in police_inst:
                cmd_prfx += ' green ' + police_inst['green_action']
            if 'yellow_action' in police_inst:
                cmd_prfx += ' yellow ' + police_inst['yellow_action']
            if 'red_action' in police_inst:
                cmd_prfx += ' red ' + police_inst['red_action']
        cmd_str = cmd_prfx

    return 'CB_SUCCESS', cmd_str
