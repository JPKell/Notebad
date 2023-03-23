''' This file generates the rules that are used by the lexer to tokenize the code. 
    Any changes to the keywords should be made in _keywords.py

    The rules are generated from the keywords in _keywords.py.
'''
from ._keywords import keyword_master 
from .config import colors, default_color
import os

### 
# Replace whitespace
### 
track_whitespace = False


def build_regex(full_word:str, abr:str=None) -> str:
    ''' Build a regular expression to match anything up to the abbreviation '''
    reg = r'\b(?:' + full_word.replace('-','\-')
    
    if abr != None:
        # build it backwards so that the longest match is found first
        for i in range(len(abr), len(full_word))[::-1]:
            reg += r'|'+ full_word[:i].replace('-','\-')
    
    # Close off the expression
    reg += r')\b'
    return reg


kw_lookup_file = open(os.path.join('abl_lookup.py'), 'w')
kw_list = [ k for k in keyword_master if k['abr'] is None and not k['starts_block'] and not k['ends_block'] ]

kw_lookup_file.write('''#This file was generated by src/models/abl_rules/build.py
# Do not edit this file directly.
# If you want to change the keywords, edit src/models/abl_rules/_keywords.py
# If you want to change the colors, edit src/models/abl_rules/config.py

kw_lookup = {
''')
            
for k in kw_list:
    k['tag'] += [colors.get(k['cat'], default_color)]
    new_dict = {ky: v for ky, v in k.items() if ky in ['keyword', 'token', 'cat', 'tag', 'mark']}
    if k['keyword'] == "'":
        kw_lookup_file.write(f'    "{k["keyword"]}": {new_dict}, \n')
    else:
        kw_lookup_file.write(f"    '{k['keyword']}': {new_dict}, \n")

kw_lookup_file.write('''
}
''')
kw_lookup_file.close()


# You should change this to the path to your abl_rules directory
file = open(os.path.join('abl.py'), 'w')


# Write the file comments and warning that its generated
file.write('''# This was generated by src/language/abl_rules/build.py
# Do not edit this file directly.
# If you want to change the keywords, edit src/language/abl_rules/_keywords.py
# If you want to change the colors, edit src/language/abl_rules/config.py''')

# Write the imports
file.write('''
from .modules.lex import TOKEN
from .abl_lookup import kw_lookup
from .abl_rules.word_lists import tokens, reserved_no_abr, reserved_w_abr, non_reserved_w_abr, non_reserved_no_abr
''')
           
# Write out the tokens
file.write(f'''

# If false, this will not track whitespace and force the user to comply
# This is required for the language model wether True or False
track_whitespace = {track_whitespace}

# Some of these contain tuples for syntax highlighting. so pull the value out of those. 
for v in reserved_no_abr.values():
    if isinstance(v, tuple):
        tokens.append(v[0])
    else:
        tokens.append(v)
for v in non_reserved_no_abr.values():
    if isinstance(v, tuple):
        tokens.append(v[0])
    else:
        tokens.append(v)

tokens += reserved_w_abr.values()
tokens += non_reserved_w_abr.values()
''')

# Simple tokens
file.write('''
# Regular expression rules for simple tokens
t_GTEQ = r'>='
t_LTEQ = r'<='
t_NE   = r'<>'
t_GT = r'>'
t_LT = r'<'
t_EQUALS = r'='
t_PLUS   = r'\+'
t_MINUS  = r'\-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'\/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_PERIOD = r'\.'
t_COMMA  = r'\,'
t_COLON  = r'\:'
t_SEMICOLON = r'\;'
t_ASSIGN = r'\:='
t_UNKNOWN = r'\?'
t_TILDE = r'~'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
'''
)

# Write out the functions which need manual regex
file.write('''
###                        
# Rules are executed top down 
# So grab the comments and strings first to prevent mistakes
###        

# If newline is not checked first then any comment or string might wipe out
# the line number counters correctness 
def t_newline(t):
    r'\\n+'
    t.lexer.lineno += len(t.value)
    t.lexer.colno = 0
    # This extra space is a fix for the fact that sometimes the : separates an object and method
    # and sometimes it starts a block. The need for no space around the first and a space around 
    # the second can be solved adding a space to before the newline. 
    t.value = ' ' + t.value
    t.tag = 'nl'
    return t

# Seems excessive, but it's what's needed. 
def t_FUNCTION_KEY(t):
    r"""(?:'([fF]1[0-2]|[fF][1-9])'|"([fF]1[0-2]|[fF][1-9])"|\\b([fF]1[0-2]|[fF][1-9])\\b)"""
    t.tag = 'red'  
    return t

def t_SNG_COMMENT(t):
    r'//.*'
    t.tag='green'
    return t

# r'/\*[\s\S]*?\*/'     # Zero nested
# r'/\*(?:(?:(?!\*/)[\s\S])*?(?:/\*(?:(?!\*/)[\s\S])*?(?:/\*(?:(?!\*/)[\s\S])*?\*/(?:(?!\*/)[\s\S])*?)*\*/(?:(?!\*/)[\s\S])*?)*\*/' # Triple nested
def t_MULTI_COMMENT(t):
    r'/\*(?:(?:(?!\*/)[\s\S])*?(?:/\*(?:(?!\*/)[\s\S])*?\*/(?:(?!\*/)[\s\S])*?)*)\*/' # Double nested
    t.lexer.lineno += t.value.count('\\n')
    t.tag='green'
    return t

# Comments that have started are going to be a challenge
def t_COMMENT_STARTED(t):
    r'/\*.*'
    t.tag='green'
    return t

def t_CURLY_BRACE(t):
    r'\{[\s\S]*?\}'
    t.tag='yellow'
    return t

def t_ARRAY_BRACE(t):
    r'\[[\s\S]*?\]'
    t.tag = 'yellow'
    return t

def t_DATE_STR(t):
    r'(?:0?[1-9]|1[0-2])[/\-\.](?:0?[1-9]|[12][0-9]|3[01])[/\-\.](?:\d{4}|\d{2})'
    t.tag = 'violet'
    return t

# Decimal must come before int or 0.5 will be int 0 and float .5
def t_DEC_STRING(t):
    r'\\b-?\d*\.\d+\\b'
    t.value = t.value
    t.tag = 'magenta' 
    return t

def t_INT_STRING(t):
    r'\\b-?\d+\\b'
    t.tag = 'orange'
    return t

def t_DBL_STRING(t):
    r'\\"[^"]*\\"'
    t.tag='violet'
    return t

def t_SNG_STRING(t):
    r"\\'[^']*\\'"
    t.tag='violet'
    return t

def t_COMPARISON_OP(t):
    r'\\b(?:GE|LE|GT|LT)\\b'
    return t

## Proceduraly generated the next large block of defines

# Starting with indent statements.

''')

## Build the stard and stop blocks words here
start_or_stop = [ kw for kw in keyword_master if kw['starts_block'] or kw['ends_block']]
for a in start_or_stop:
    # Get the syntax highlighting
    tag = colors.get(a["cat"], default_color)
    
    # Build out marks if there are any 
    mark = f"\n    t.mark = '{','.join(a['mark'])}'" if len(a['mark']) != 0 else ''

    # Build out indent if appropriate
    indent = ''
    if a['starts_block']:
        indent = "\n    t.indent += 1"
    if a['ends_block']:
        indent = "\n    t.indent -= 1"

    file.write(f'''
def t_{a['token']}(t):
    r'{build_regex(a['keyword'])}'
    t.tag = '{tag}'{mark}{indent}
    return t
    ''')


file.write("""
###
# And now abbreviated keywords. Damn those abbreviated keywords. 
###

""")

## Build the abriviated words here
abr = [ kw for kw in keyword_master if kw['abr'] != None and not kw['starts_block'] and not kw['ends_block']]
for a in abr:
    # Get the syntax highlighting
    tag = colors.get(a["cat"], default_color)
    
    # Build out marks if there are any 
    mark = f"\n    t.mark = '{','.join(a['mark'])}'" if len(a['mark']) != 0 else ''

    file.write(f'''
def t_{a['token']}(t):
    r'{build_regex(a['keyword'],a['abr'])}'
    t.tag = '{tag}'{mark}
    return t
    ''')

if track_whitespace:
    file.write(""" 
# This will track whitespace and adds a lot of time to processing. Not tracking 
# it however will force the user into the indent scheme
t_WHITESPACE = r'\s+'

literals = [ '+','-','*','/', '"', "'", '(', ')', '[', ']', '{', '}', ',', ':', ';', '=', '?', '~', '.', '>', '<', '!' ]

# Some of these might be better not ignored. However for syntax highlighting
# they throw a lot of errors. As this is continuing, it might be better to 
# define 2 states, one for syntax highlighting and one for parsing.
# t_ignore = r'.'
t_ignore = '}\\t'

""")
else:
    file.write("""
literals = [ '+','-','*','/', '"', "'", '(', ')', '[', ']', '{', '}', ',', ':', ';', '=', '?', '~', '.', '>', '<', '!' ]

# Some of these might be better not ignored. However for syntax highlighting
# they throw a lot of errors. As this is continuing, it might be better to 
# define 2 states, one for syntax highlighting and one for parsing.
# t_ignore = r'.'
t_ignore = ' }\\t'
    
    """)

file.write('''
#####
### End of proceduraly generated code
#####

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_\-\.0-9]*[a-zA-Z_\-0-9]|\\b[a-zA-Z]\\b'
    _id = {'keyword': '', 'token': 'ID', 'cat': '', 'tag': ['alt_blue'], 'mark': []}
    result = kw_lookup.get(t.value.upper(),_id)    # Check for reserved words
    t.type = result['token']
    t.tag  = result['tag']
    return t

# This is a hack to prevent the lexer from throwing an error on a bad word and deleting it.
def t_CATCHALL(t):
    r'[0-9][a-zA-Z_0-9\.,\-=]*'
    t.type = 'ERROR'
    t.tag = 'error'
    return t

    

def t_error(t):
    print(f"Illegal character {t.value[0:50]} @ ln:{t.lineno} col:{t.colno}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    return t
    # t.lexer.skip(1)
''')



file.close()