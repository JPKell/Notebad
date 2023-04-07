from datetime import datetime as dt

def parse_profiler_data(file_path:str) -> dict:
    ''' Take the profiler data from progress and parses it into a dict for use
        in the profiler module.

        Args:
            file_path (str): The profiler data from progress'''

    with open(file_path, 'r') as f:
        data = f.read()

    # Profiler data is split into 5 sections. Each section is separated by a new line with a single period.
    # The last sections contains many sections and remains a list of each section
    data      = data.split('\n.')
    header    = data[0]
    src_path  = data[1]
    call_tree = data[2]
    timings   = data[3]
    lines_run = data[4:]

    # Start building the profile_data dict
    profile_data = {}

    # Parse the profiler meta data
    # Example output:
    # ['1 04/05/2023 ', 'testing', ' 15:46:34 ', 'jkell', '']
    header = header.split('"')
    date = header[0].split(' ')[1]
    time = header[2].strip()
    datetime = dt.strptime(f"{date} {time}", "%m/%d/%Y %H:%M:%S")
    title = header[1]
    user  = header[3]
    profile_data['meta'] = {'timestamp': datetime, 'title': title, 'user': user}

    # Parse the source path
    # Example output:
    # 239 "PrintMusicSearch tty.im.PrintMusicSearch" "" 0 330 ""
    profile_data['src'] = {}
    for row in src_path.split('\n'):
        if row == '':
            continue
        row = row.split('"')
        _id = row.pop(0).strip()
        src = row.pop(0).strip()
        # Some rows will not have a function name
        if src.find(' ') != -1:
            src  = src.split(' ')
            func = src[0]
            src  = src[1]
        else:
            func = None

        row.pop(0)  # Remove the empty string between double quotes ...h" "" 0...
        debug_info = row.pop(0).strip()
        other_info = row.pop(0).strip() # not certain what this is

        profile_data['src'][_id] = {'src': src, 'func':func, 'debug_info': debug_info, 'other_info': other_info}

    # Parse the call tree
    # Example output:
    # 522 118 523 2
    profile_data['call_tree'] = []
    for row in call_tree.split('\n'):
        # skip blank rows
        if row == '':
            continue
        caller, src_line, callee, count = row.split(' ')

        profile_data['call_tree'] += [{'caller':caller,'src_line': src_line, 'callee': callee, 'count': count}]

    # Parse the timings
    # Example output:
    # 18 422 1 0.000022 0.000034
    profile_data['timings'] = []
    for row in timings.split('\n'):
        # skip blank rows
        if row == '':
            continue
        _id, src_line, exec_count, exec_time, tot_time  = row.split(' ')
        profile_data['timings'] += [{'id': _id, 'src_line': src_line, 'exec_count': exec_count, 'exec_time': exec_time, 'tot_time': tot_time}]


    # Parse the rows run
    # Example output multiline:
    # 71 "set-direction" 3      <- Metadata, src id, name, lines_exec
    # 645                       <- Line number executed
    # 646
    # 647
    profile_data['exec_path'] = []
    for row in lines_run:
        # skip blank rows
        if row == '':
            continue
        row = [ x for x in row.split('\n') if x != '']
        if len(row) == 0:
            continue
        src_id, name, lines_exec = row.pop(0).split(' ')
        profile_data['exec_path'] += [{'src_id': src_id, 'name': name, 'lines_exec': lines_exec, 'lines': [x.strip() for x in row]}]


    src_unique = list(set([x['src'] for x in profile_data['src'].values()]))

    output = {'meta': profile_data['meta']}
    for src in src_unique:
        output[src] = {'ids': [], 'lines': {}}

        id_list = [k for k,v in profile_data['src'].items() if v['src'] == src]
        # Build the initial dictionary for the source file
        # { 'src': {'ids': [], 'lines': {'func':..., 'name':...,'lines_exec':..., 'exec_count', 'exec_time', 'tot_time', 'callee', 'call_count'} }
        exec_path = [ x for x in profile_data['exec_path'] if x['src_id'] in id_list]
        for line in exec_path:
            func = profile_data['src'][line['src_id']]['func']
            name = line['name'].replace('"', '')
            for ln in line['lines']:
                output[src]['lines'][ln] = {'func': func, 'name': name, 'lines_exec': line['lines_exec'], 'exec_count': 0, 'exec_time': 0, 'tot_time': 0, 'callee': None, 'call_count': None}

        # Add the call tree components
        call_tree = [ x for x in profile_data['call_tree'] if x['caller'] in id_list ]
        for line in call_tree:
            if line['src_line'] not in output[src]['lines']:
                src_dict = profile_data['src'][line['caller']]
                func = src_dict['func']
                # name = src_dict['name']
                output[src]['lines'][line['src_line']] = {'func': func, 'name': '', 'lines_exec': None, 'exec_count': 0, 'exec_time': 0, 'tot_time': 0, 'callee': None, 'call_count': None}
            output[src]['lines'][line['src_line']]['callee'] = line['callee']
            output[src]['lines'][line['src_line']]['call_count']  = line['count']

        # Add the timing components
        timings = [ x for x in profile_data['timings'] if x['id'] in id_list ]
        for line in timings:
            if line['src_line'] not in output[src]['lines'].keys():
                src_dict = profile_data['src'][line['id']]

                func = src_dict['func']
                # name = src_dict['name']
                output[src]['lines'][line['src_line']] = {'func': func, 'name': '', 'lines_exec': None, 'exec_count': 0, 'exec_time': 0, 'tot_time': 0, 'callee': None, 'call_count': None}
            output[src]['lines'][line['src_line']]['exec_count'] += float(line['exec_count'])
            output[src]['lines'][line['src_line']]['exec_time']  += float(line['exec_time'])
            output[src]['lines'][line['src_line']]['tot_time']   += float(line['tot_time'])
    
        # Add the ids
        output[src]['ids'] = id_list

    return output


if __name__ == '__main__':
    parse_profiler_data('/home/jpk/profile.profile')