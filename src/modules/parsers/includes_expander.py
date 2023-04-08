import os, re
from settings import Configuration

cfg = Configuration()
 


def expand_includes(filename:str) -> list:
    # Validate file path
    path = os.path.join(cfg.project_src, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f'File not found: {filename}')
    
    with open(path, 'r') as f:
        lines = f.readlines()

    output = []
    # Todo refine this regex to not match includes in comments. 
    pattern = r'^\{.*\.[piw]\}'
    for ln in lines:
        if re.search(pattern, ln):
            # Get the file name
            # {filename.p new} -> filename.p
            _filename = ln.split('{')[1].split('}')[0].strip()
            if _filename.find(' ') != -1:
                _filename = _filename.split(' ')[0]
            results = expand_includes(_filename)
            # Add the file contents to the output
            output.extend(results)
        else:
            output.append(ln)

    return output