def show_mirror_session(render_tables):
    cmd_str = ''
    cmd_prfx = ''

    if 'sonic-mirror-session:sonic-mirror-session/MIRROR_SESSION/MIRROR_SESSION_LIST' in render_tables:
        session = render_tables['sonic-mirror-session:sonic-mirror-session/MIRROR_SESSION/MIRROR_SESSION_LIST']
        if 'dst_port' in session:
            cmd_str="destination " + session['dst_port']
            if 'src_port' in session:
                cmd_str+=' source ' + session['src_port']
            if 'direction' in session:
                cmd_str+=' direction ' + session['direction'].lower()
        if 'dst_ip' in session:
            cmd_str="destination erspan dst-ip " + session['dst_ip']
            if 'src_ip' in session:
                cmd_str+=' src-ip ' + session['src_ip']
            if 'dscp' in session:
                cmd_str+=' dscp ' + str(session['dscp'])
            if 'gre_type' in session:
                cmd_str+=' gre ' + session['gre_type']
            if 'ttl' in session:
                cmd_str+=' ttl ' + str(session['ttl'])
            if 'queue' in session:
                cmd_str+=' queue ' + str(session['queue'])
            if 'src_port' in session:
                cmd_str+=' source ' + session['src_port']
            if 'direction' in session:
                cmd_str+=' direction ' + session['direction'].lower()

    return 'CB_SUCCESS', cmd_str
