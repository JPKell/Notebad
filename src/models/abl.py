# This module contains lexing rules for Progress ABL
# Things are processed top down. And putting largest up top prevents picking smaller keywords out of larger ones
from .modules.lex import TOKEN
from .abl_rules.word_lists import tokens, reserved_no_abr, reserved_w_abr, non_reserved_w_abr, non_reserved_no_abr

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

reserved = {**reserved_no_abr, **non_reserved_no_abr}

def build_regex(full_word:str, abr:str) -> str:
    ''' Build a regular expression to match anything up to the abbreviation '''
    reg = r'\b(?:' + full_word.replace('-','\-')
    # build it backwards so that the longest match is found first
    for i in range(len(abr), len(full_word))[::-1]:
        reg += r'|'+ full_word[:i].replace('-','\-')
    reg += r')\b'
    return reg

###                        
# Rules are executed top down 
# So grab the comments and strings first to prevent mistakes
###        

# If newline is not checked first then any comment or string might wipe out
# the line number counters correctness 
def t_newline(t):
    r'\n+'
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
    r"""(?:'([fF]1[0-2]|[fF][1-9])'|"([fF]1[0-2]|[fF][1-9])"|\b([fF]1[0-2]|[fF][1-9])\b)"""
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
    t.lexer.lineno += t.value.count('\n')
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
    r'\b-?\d*\.\d+\b'
    t.value = t.value
    t.tag = 'magenta' 
    return t

def t_INT_STRING(t):
    r'\b-?\d+\b'
    t.tag = 'orange'
    return t

def t_DBL_STRING(t):
    r'\"[^"]*\"'
    t.tag='violet'
    return t

def t_SNG_STRING(t):
    r"\'[^']*\'"
    t.tag='violet'
    return t

# This is a workaround to subdue the errors that come when live 
# syntax highlighting with the lexer. There really should be 2
# states for this.
# def t_NOT_ILLEGAL(t):
#     r'[&\s\(\)\{\}\[\]\+\-\*\/\%\^\|\<\>\=\!\?\:\;\,\.!@#\}\{]+'

#     return t


### Various preprocessing rules these dont exist in the word list yet. 
def t_SCOPED_DEFINE(t):
    r'&SCOPED\-DEFINE'
    t.tag='blue'
    return t

###
# The following are all reserved keywords from the list. 
# The should probably get sorted to make it easier to find
###

@TOKEN(build_regex('ACCUMULATE', 'ACCUM'))
def t_ACCUMULATE(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('AMBIGUOUS', 'AMBIG'))
def t_AMBIGUOUS(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('ANALYZE', 'ANALYZ'))
def t_ANALYZE(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('ASCENDING', 'ASC'))
def t_ASCENDING(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('ATTR-SPACE', 'ATTR'))
def t_ATTR_SPACE(t):

    t.tag='cyan'
    return t
        
@TOKEN(build_regex('AUTO-RETURN', 'AUTO-RET'))
def t_AUTO_RETURN(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('AVAILABLE', 'AVAIL'))
def t_AVAILABLE(t):
    t.tag = 'cyan' 
    return t
        
@TOKEN(build_regex('BACKGROUND', 'BACK'))
def t_BACKGROUND(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('BEFORE-HIDE', 'BEFORE-H'))
def t_BEFORE_HIDE(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('CASE-SENSITIVE', 'CASE-SEN'))
def t_CASE_SENSITIVE(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('CENTERED', 'CENTER'))
def t_CENTERED(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('CHARACTER', 'CHA'))
def t_CHARACTER(t):
    t.tag='cyan'
    return t
    
@TOKEN(build_regex('COLUMN-LABEL', 'COLUMN-LAB'))
def t_COLUMN_LABEL(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('CURRENT-LANGUAGE', 'CURRENT-LANG'))
def t_CURRENT_LANGUAGE(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('CURSOR', 'CURS'))
def t_CURSOR(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('DATA-RELATION', 'DATA-REL'))
def t_DATA_RELATION(t):
    return t
        
@TOKEN(build_regex('DBRESTRICTIONS', 'DBREST'))
def t_DBRESTRICTIONS(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('DBVERSION', 'DBVERS'))
def t_DBVERSION(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('DEFAULT-NOXLATE', 'DEFAULT-NOXL'))
def t_DEFAULT_NOXLATE(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('DEFINE', 'DEF'))
def t_DEFINE(t):
    t.tag = 'blue'
    return t
        
@TOKEN(build_regex('DELETE', 'DEL'))
def t_DELETE(t):
    t.tag = 'blue'
    return t
        
@TOKEN(build_regex('DESCENDING', 'DESC'))
def t_DESCENDING(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('DICTIONARY', 'DICT'))
def t_DICTIONARY(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('DISCONNECT', 'DISCON'))
def t_DISCONNECT(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('DISPLAY', 'DISP'))
def t_DISPLAY(t):
    t.tag='blue'
    return t
        
@TOKEN(build_regex('ERROR-STATUS', 'ERROR-STAT'))
def t_ERROR_STATUS(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('EXCLUSIVE-LOCK', 'EXCLUSIVE'))
def t_EXCLUSIVE_LOCK(t):
    t.tag='red'
    return t
        
@TOKEN(build_regex('FIELDS', 'FIELD'))
def t_FIELDS(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('FILE-INFORMATION', 'FILE-INFO'))
def t_FILE_INFORMATION(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('FORMAT', 'FORM'))
def t_FORMAT(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('FRAME', 'FRAM'))
def t_FRAME(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('FRAME-INDEX', 'FRAME-INDE'))
def t_FRAME_INDEX(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('FRAME-VALUE', 'FRAME-VAL'))
def t_FRAME_VALUE(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('FROM-CHARS', 'FROM-C'))
def t_FROM_CHARS(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('FROM-PIXELS', 'FROM-P'))
def t_FROM_PIXELS(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('GATEWAYS', 'GATEWAY'))
def t_GATEWAYS(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('GET-FILE-OFFSET', 'GET-FILE-OFFSE'))
def t_GET_FILE_OFFSET(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('GET-KEY-VALUE', 'GET-KEY-VAL'))
def t_GET_KEY_VALUE(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('GO-PENDING', 'GO-PEND'))
def t_GO_PENDING(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('GRAPHIC-EDGE', 'GRAPHIC-E'))
def t_GRAPHIC_EDGE(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('INPUT-OUTPUT', 'INPUT-O'))
def t_INPUT_OUTPUT(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('IS-ATTR-SPACE', 'IS-ATTR'))
def t_IS_ATTR_SPACE(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('IS-LEAD-BYTE', 'IS-ATTR'))
def t_IS_LEAD_BYTE(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('KEY-FUNCTION', 'KEY-FUNC'))
def t_KEY_FUNCTION(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('KEYFUNCTION', 'KEYFUNC'))
def t_KEYFUNCTION(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('LAST-EVENT', 'LAST-EVEN'))
def t_LAST_EVENT(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('LINE-COUNTER', 'LINE-COUNT'))
def t_LINE_COUNTER(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('LISTING', 'LISTI'))
def t_LISTING(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('LOGICAL', 'LOG'))
def t_LOGICAL(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('NO-ATTR-LIST', 'NO-ATTR'))
def t_NO_ATTR_LIST(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('NO-ATTR-SPACE', 'NO-ATTR'))
def t_NO_ATTR_SPACE(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('NO-FILL', 'NO-F'))
def t_NO_FILL(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('NO-LABELS', 'NO-LABEL'))
def t_NO_LABELS(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('NO-MESSAGE', 'NO-MES'))
def t_NO_MESSAGE(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('NO-PREFETCH', 'NO-PREFE'))
def t_NO_PREFETCH(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('NO-VALIDATE', 'NO-VAL'))
def t_NO_VALIDATE(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('NUM-ALIASES', 'NUM-ALI'))
def t_NUM_ALIASES(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('PAGE-BOTTOM', 'PAGE-BOT'))
def t_PAGE_BOTTOM(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('PAGE-NUMBER', 'PAGE-NUM'))
def t_PAGE_NUMBER(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('PARAMETER', 'PARAM'))
def t_PARAMETER(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('PERSISTENT', 'PERSIST'))
def t_PERSISTENT(t):
    t.tag='blue'
    return t
        
@TOKEN(build_regex('PREPROCESS', 'PREPROC'))
def t_PREPROCESS(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('PROC-HANDLE', 'PROC-HA'))
def t_PROC_HANDLE(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('PROC-STATUS', 'PROC-ST'))
def t_PROC_STATUS(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('PROMPT-FOR', 'PROMPT-F'))
def t_PROMPT_FOR(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('PROVERSION', 'PROVERS'))
def t_PROVERSION(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('PUT-KEY-VALUE', 'PUT-KEY-VAL'))
def t_PUT_KEY_VALUE(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('RCODE-INFORMATION', 'RCODE-INFO'))
def t_RCODE_INFORMATION(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('RECTANGLE', 'RECT'))
def t_RECTANGLE(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('SAX-COMPLETE', 'SAX-COMPLE'))
def t_SAX_COMPLETE(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('SETUSERID', 'SETUSER'))
def t_SETUSERID(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('SHARE-LOCK', 'SHARE'))
def t_SHARE_LOCK(t):
    t.tag='red'
    return t
        
@TOKEN(build_regex('SHOW-STATS', 'SHOW-STAT'))
def t_SHOW_STATS(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('TERMINAL', 'TERM'))
def t_TERMINAL(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('UNDERLINE', 'UNDERL'))
def t_UNDERLINE(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('UNFORMATTED', 'UNFORM'))
def t_UNFORMATTED(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('WINDOW-MAXIMIZED', 'WINDOW-MAXIM'))
def t_WINDOW_MAXIMIZED(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('WINDOW-MINIMIZED', 'WINDOW-MINIM'))
def t_WINDOW_MINIMIZED(t):
    t.tag='cyan'
    return t
        
@TOKEN(build_regex('WORK-TABLE', 'WORK-TAB'))
def t_WORK_TABLE(t):
    t.tag='cyan'
    return t





###
# These are non reserved keywords with abreviations
###

@TOKEN(build_regex('ABSOLUTE', 'ABS'))
def t_ABSOLUTE(t):
    t.tag='orange'
    return t

@TOKEN(build_regex('APPL-ALERT-BOXES', 'APPL-ALERT'))
def t_APPL_ALERT_BOXES(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('AUTO-COMPLETION', 'AUTO-COMP'))
def t_AUTO_COMPLETION(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('AUTO-INDENT', 'AUTO-IND'))
def t_AUTO_INDENT(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('AUTO-ZAP', 'AUTO-Z'))
def t_AUTO_ZAP(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('AVERAGE', 'AVE'))
def t_AVERAGE(t):
    t.tag='orange'
    return t

@TOKEN(build_regex('BACKWARDS', 'BACKWARD'))
def t_BACKWARDS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('BATCH-MODE', 'BATCH'))
def t_BATCH_MODE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('BGCOLOR', 'BGC'))
def t_BGCOLOR(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('BLOCK-LEVEL', 'BLOCK-LEV'))
def t_BLOCK_LEVEL(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('BORDER-BOTTOM-CHARS', 'BORDER-B'))
def t_BORDER_BOTTOM_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('BORDER-BOTTOM-PIXELS', 'BORDER-BOTTOM-P'))
def t_BORDER_BOTTOM_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('BORDER-LEFT-CHARS', 'BORDER-L'))
def t_BORDER_LEFT_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('BORDER-LEFT-PIXELS', 'BORDER-LEFT-P'))
def t_BORDER_LEFT_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('BORDER-RIGHT-CHARS', 'BORDER-R'))
def t_BORDER_RIGHT_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('BORDER-RIGHT-PIXELS', 'BORDER-RIGHT-P'))
def t_BORDER_RIGHT_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('BORDER-TOP-CHARS', 'BORDER-T'))
def t_BORDER_TOP_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('BORDER-TOP-PIXELS', 'BORDER-TOP-P'))
def t_BORDER_TOP_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('BOX-SELECTABLE', 'BOX-SELECT'))
def t_BOX_SELECTABLE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('BUTTONS', 'BUTTON'))
def t_BUTTONS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('CLEAR-SELECTION', 'CLEAR-SELECT'))
def t_CLEAR_SELECTION(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('CLEAR-SORT-ARROWS', 'CLEAR-SORT-ARROW'))
def t_CLEAR_SORT_ARROWS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('COLON-ALIGNED', 'COLON-ALIGN'))
def t_COLON_ALIGNED(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('COLUMN', 'COL'))
def t_COLUMN(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('CONVERT-TO-OFFSET', 'CONVERT-TO-OFFS'))
def t_CONVERT_TO_OFFSET(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('CURRENT-ENVIRONMENT', 'CURRENT-ENV'))
def t_CURRENT_ENVIRONMENT(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('DATA-ENTRY-RETURN', 'DATA-ENTRY-RET'))
def t_DATA_ENTRY_RETURN(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('DATA-TYPE', 'DATA-T'))
def t_DATA_TYPE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('DATE-FORMAT', 'DATE-F'))
def t_DATE_FORMAT(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('DDE-ID', 'DDE-I'))
def t_DDE_ID(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('DEBUG', 'DEBU'))
def t_DEBUG(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('DECIMAL', 'DEC'))
def t_DECIMAL(t):
    t.tag='blue'
    return t

@TOKEN(build_regex('DEFAULT-BUTTON', 'DEFAUT-B'))
def t_DEFAULT_BUTTON(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('DEFAULT-EXTENSION', 'DEFAULT-EX'))
def t_DEFAULT_EXTENSION(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('DISPLAY-TYPE', 'DISPLAY-T'))
def t_DISPLAY_TYPE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('EDGE-CHARS', 'EDGE'))
def t_EDGE_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('EDGE-PIXELS', 'EDGE-P'))
def t_EDGE_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('ERROR-COLUMN', 'ERROR-COL'))
def t_ERROR_COLUMN(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('EVENT-TYPE', 'EVENT-T'))
def t_EVENT_TYPE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('FGCOLOR', 'FGC'))
def t_FGCOLOR(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('FILE-OFFSET', 'FILE-OFF'))
def t_FILE_OFFSET(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('FIRST-PROCEDURE', 'FIRST-PROC'))
def t_FIRST_PROCEDURE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('FIRST-TAB-ITEM', 'FIRST-TAB-I'))
def t_FIRST_TAB_ITEM(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('FOREGROUND', 'FORE'))
def t_FOREGROUND(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('FORMATTED', 'FORMATTE'))
def t_FORMATTED(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('FORWARDS', 'FORWARD'))
def t_FORWARDS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('FRAGMENT', 'FRAGMEN'))
def t_FRAGMENT(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('FRAME-SPACING', 'FRAME-SPA'))
def t_FRAME_SPACING(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('FROM-CURRENT', 'FROM-CUR'))
def t_FROM_CURRENT(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('FULL-HEIGHT-CHARS', 'FULL-HEIGHT'))
def t_FULL_HEIGHT_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('FULL-HEIGHT-PIXELS', 'FULL-HEIGHT-P'))
def t_FULL_HEIGHT_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('FULL-PATHNAME', 'FULL-PATHN'))
def t_FULL_PATHNAME(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('FULL-WIDTH-CHARS', 'FULL-WIDTH'))
def t_FULL_WIDTH_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('FULL-WIDTH-PIXELS', 'FULL-WIDTH-P'))
def t_FULL_WIDTH_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('GET-BLUE-VALUE', 'GET-BLUE'))
def t_GET_BLUE_VALUE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('GET-GREEN-VALUE', 'GET-GREEN'))
def t_GET_GREEN_VALUE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('GET-RED-VALUE', 'GET-RED'))
def t_GET_RED_VALUE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('GET-SELECTED-WIDGET', 'GET-SELECTED'))
def t_GET_SELECTED_WIDGET(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('GET-TEXT-HEIGHT-CHARS', 'GET-TEXT-HEIGHT'))
def t_GET_TEXT_HEIGHT_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('GET-TEXT-HEIGHT-PIXELS', 'GET-TEXT-HEIGHT-P'))
def t_GET_TEXT_HEIGHT_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('GET-TEXT-WIDTH-CHARS', 'GET-TEXT-WIDTH'))
def t_GET_TEXT_WIDTH_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('GET-TEXT-WIDTH-PIXELS', 'GET-TEXT-WIDTH-P'))
def t_GET_TEXT_WIDTH_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('GRID-FACTOR-HORIZONTAL', 'GRID-FACTOR-H'))
def t_GRID_FACTOR_HORIZONTAL(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('GRID-FACTOR-VERTICAL', 'GRID-FACTOR-V'))
def t_GRID_FACTOR_VERTICAL(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('GRID-UNIT-HEIGHT-CHARS', 'GRID-UNIT-HEIGHT'))
def t_GRID_UNIT_HEIGHT_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('GRID-UNIT-HEIGHT-PIXELS', 'GRID-UNIT-HEIGHT-P'))
def t_GRID_UNIT_HEIGHT_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('GRID-UNIT-WIDTH-CHARS', 'GRID-UNIT-WIDTH'))
def t_GRID_UNIT_WIDTH_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('GRID-UNIT-WIDTH-PIXELS', 'GRID-UNIT-WIDTH-P'))
def t_GRID_UNIT_WIDTH_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('HEIGHT-CHARS', 'HEIGHT'))
def t_HEIGHT_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('HEIGHT-PIXELS', 'HEIGHT-P'))
def t_HEIGHT_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('HORIZONTAL', 'HORI'))
def t_HORIZONTAL(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('IMAGE-SIZE-CHARS', 'IMAGE-SIZE-C'))
def t_IMAGE_SIZE_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('IMAGE-SIZE-PIXELS', 'IMAGE-SIZE-P'))
def t_IMAGE_SIZE_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('INFORMATION', 'INFO'))
def t_INFORMATION(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('INHERIT-BGCOLOR', 'INHERIT-BGC'))
def t_INHERIT_BGCOLOR(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('INHERIT-FGCOLOR', 'INHERIT-FGC'))
def t_INHERIT_FGCOLOR(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('INITIAL', 'INIT'))
def t_INITIAL(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('INSERT-BACKTAB', 'INSERT-B'))
def t_INSERT_BACKTAB(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('INSERT-TAB', 'INSERT-T'))
def t_INSERT_TAB(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('INTEGER', 'INT'))
def t_INTEGER(t):
    t.tag='blue'
    return t

@TOKEN(build_regex('IS-CLASS', 'IS-CLAS'))
def t_IS_CLASS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('IS-PARTITIONED', 'IS-PARTITIONE'))
def t_IS_PARTITIONED(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('KEEP-FRAME-Z-ORDER', 'KEEP-FRAME-Z'))
def t_KEEP_FRAME_Z_ORDER(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('LABEL-BGCOLOR', 'LABEL-BGC'))
def t_LABEL_BGCOLOR(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('LABEL-DCOLOR', 'LABEL-DC'))
def t_LABEL_DCOLOR(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('LABEL-FGCOLOR', 'LABEL-FGC'))
def t_LABEL_FGCOLOR(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('LABEL-PFCOLOR', 'LABEL-PFC'))
def t_LABEL_PFCOLOR(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('LANGUAGES', 'LANGUAGE'))
def t_LANGUAGES(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('LAST-PROCEDURE', 'LAST-PROCE'))
def t_LAST_PROCEDURE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('LAST-TAB-ITEM', 'LAST-TAB-I'))
def t_LAST_TAB_ITEM(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('LEFT-ALIGNED', 'LEFT-ALIGN'))
def t_LEFT_ALIGNED(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('LOAD-MOUSE-POINTER', 'LOAD-MOUSE-P'))
def t_LOAD_MOUSE_POINTER(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MARGIN-HEIGHT-CHARS', 'MARGIN-HEIGHT'))
def t_MARGIN_HEIGHT_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MARGIN-HEIGHT-PIXELS', 'MARGIN-HEIGHT-P'))
def t_MARGIN_HEIGHT_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MARGIN-WIDTH-CHARS', 'MARGIN-WIDTH'))
def t_MARGIN_WIDTH_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MARGIN-WIDTH-PIXELS', 'MARGIN-WIDTH-P'))
def t_MARGIN_WIDTH_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MAX-HEIGHT-CHARS', 'MAX-HEIGHT-C'))
def t_MAX_HEIGHT_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MAX-HEIGHT-PIXELS', 'MAX-HEIGHT-P'))
def t_MAX_HEIGHT_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MAX-VALUE', 'MAX-VAL'))
def t_MAX_VALUE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MAX-WIDTH-CHARS', 'MAX-WIDTH'))
def t_MAX_WIDTH_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MAX-WIDTH-PIXELS', 'MAX-WIDTH-P'))
def t_MAX_WIDTH_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MAXIMUM', 'MAX'))
def t_MAXIMUM(t):
    t.tag='orange'
    return t

@TOKEN(build_regex('MENU-KEY', 'MENU-K'))
def t_MENU_KEY(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MENU-MOUSE', 'MENU-M'))
def t_MENU_MOUSE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MIN-COLUMN-WIDTH-CHARS', 'MIN-COLUMN-WIDTH-C'))
def t_MIN_COLUMN_WIDTH_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MIN-COLUMN-WIDTH-PIXELS', 'MIN-COLUMN-WIDTH-P'))
def t_MIN_COLUMN_WIDTH_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MIN-HEIGHT-CHARS', 'MIN-HEIGHT'))
def t_MIN_HEIGHT_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MIN-HEIGHT-PIXELS', 'MIN-HEIGHT-P'))
def t_MIN_HEIGHT_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MIN-VALUE', 'MIN-VAL'))
def t_MIN_VALUE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MIN-WIDTH-CHARS', 'MIN-WIDTH'))
def t_MIN_WIDTH_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MIN-WIDTH-PIXELS', 'MIN-WIDTH-P'))
def t_MIN_WIDTH_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MINIMUM', 'MIN'))
def t_MINIMUM(t):
    t.tag='orange'
    return t

@TOKEN(build_regex('MODULO', 'MOD'))
def t_MODULO(t):
    t.tag='orange'
    return t

@TOKEN(build_regex('MOUSE-POINTER', 'MOUSE-P'))
def t_MOUSE_POINTER(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MOVE-AFTER-TAB-ITEM', 'MOVE-AFTER'))
def t_MOVE_AFTER_TAB_ITEM(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MOVE-BEFORE-TAB-ITEM', 'MOVE-BEFOR'))
def t_MOVE_BEFORE_TAB_ITEM(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MOVE-COLUMN', 'MOVE-COL'))
def t_MOVE_COLUMN(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MOVE-TO-BOTTOM', 'MOVE-TO-B'))
def t_MOVE_TO_BOTTOM(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('MOVE-TO-TOP', 'MOVE-TO-T'))
def t_MOVE_TO_TOP(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('NEXT-TAB-ITEM', 'NEXT-TAB-I'))
def t_NEXT_TAB_ITEM(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('NO-INHERIT-BGCOLOR', 'NO-INHERIT-BGC'))
def t_NO_INHERIT_BGCOLOR(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('NO-INHERIT-FGCOLOR', 'NO-INHERIT-FGC'))
def t_NO_INHERIT_FGCOLOR(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('NO-UNDERLINE', 'NO-UND'))
def t_NO_UNDERLINE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('NUM-BUTTONS', 'NUM-BUT'))
def t_NUM_BUTTONS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('NUM-COLUMNS', 'NUM-COL'))
def t_NUM_COLUMNS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('NUM-LOCKED-COLUMNS', 'NUM-LOCKED-COL'))
def t_NUM_LOCKED_COLUMNS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('NUM-SELECTED-WIDGETS', 'NUM-SELECTED'))
def t_NUM_SELECTED_WIDGETS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('NUMERIC-FORMAT', 'NUMERIC-F'))
def t_NUMERIC_FORMAT(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('ON-FRAME-BORDER', 'ON-FRAME'))
def t_ON_FRAME_BORDER(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('OS-DRIVES', 'OS-DRIVE'))
def t_OS_DRIVES(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('PAGE-WIDTH', 'PAGE-WID'))
def t_PAGE_WIDTH(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('PBE-HASH-ALGORITHM', 'PBE-HASH-ALG'))
def t_PBE_HASH_ALGORITHM(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('PFCOLOR', 'PFC'))
def t_PFCOLOR(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('PIXELS-PER-COLUMN', 'PIXELS-PER-COL'))
def t_PIXELS_PER_COLUMN(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('POPUP-MENU', 'POPUP-M'))
def t_POPUP_MENU(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('POPUP-ONLY', 'POPUP-O'))
def t_POPUP_ONLY(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('PRESELECT', 'PRESEL'))
def t_PRESELECT(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('PREV-TAB-ITEM', 'PREV-TAB-I'))
def t_PREV_TAB_ITEM(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('PRIVATE-DATA', 'PRIVATE-D'))
def t_PRIVATE_DATA(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('PROCEDURE', 'PROCE'))
def t_PROCEDURE(t):
    t.tag='magenta'
    return t

@TOKEN(build_regex('PROGRESS-SOURCE', 'PROGRESS-S'))
def t_PROGRESS_SOURCE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('RESIZABLE', 'RESIZA'))
def t_RESIZABLE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('RETURN-INSERTED', 'RETURN-INS'))
def t_RETURN_INSERTED(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('RETURN-TO-START-DIR', 'RETURN-TO-START-DI'))
def t_RETURN_TO_START_DIR(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('RETURN-VALUE', 'RETURN-VAL'))
def t_RETURN_VALUE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('RIGHT-ALIGNED', 'RETURN-ALIGN'))
def t_RIGHT_ALIGNED(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('ROW-HEIGHT-CHARS', 'HEIGHT'))
def t_ROW_HEIGHT_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('ROW-HEIGHT-PIXELS', 'HEIGHT-P'))
def t_ROW_HEIGHT_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('SCREEN-VALUE', 'SCREEN-VAL'))
def t_SCREEN_VALUE(t):
    t.tag='blue'
    return t

@TOKEN(build_regex('SCROLL-TO-ITEM', 'SCROLL-TO-I'))
def t_SCROLL_TO_ITEM(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('SCROLLBAR-HORIZONTAL', 'SCROLLBAR-H'))
def t_SCROLLBAR_HORIZONTAL(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('SCROLLBAR-VERTICAL', 'SCROLLBAR-V'))
def t_SCROLLBAR_VERTICAL(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('SCROLLED-ROW-POSITION', 'SCROLLED-ROW-POS'))
def t_SCROLLED_ROW_POSITION(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('SET-BLUE-VALUE', 'SET-BLUE'))
def t_SET_BLUE_VALUE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('SET-GREEN-VALUE', 'SET-GREEN'))
def t_SET_GREEN_VALUE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('SET-RED-VALUE', 'SET-RED'))
def t_SET_RED_VALUE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('SIDE-LABEL-HANDLE', 'SIDE-LABEL-H'))
def t_SIDE_LABEL_HANDLE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('SIDE-LABELS', 'SIDE-LAB'))
def t_SIDE_LABELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('SIZE-CHARS', 'SIZE-C'))
def t_SIZE_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('SIZE-PIXELS', 'SIZE-P'))
def t_SIZE_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('STOPPED', 'STOPPE'))
def t_STOPPED(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('STORED-PROCEDURE', 'STORED-PROC'))
def t_STORED_PROCEDURE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('SUB-AVERAGE', 'SUB-AVE'))
def t_SUB_AVERAGE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('SUB-MAXIMUM', 'SUM-MAX'))
def t_SUB_MAXIMUM(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('SUB-MENU', 'SUB-'))
def t_SUB_MENU(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('SUB-MINIMUM', 'SUB-MIN'))
def t_SUB_MINIMUM(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('SUBSTITUTE', 'SUBST'))
def t_SUBSTITUTE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('SUBSTRING', 'SUBSTR'))
def t_SUBSTRING(t):
    t.tag='orange'
    return t

@TOKEN(build_regex('SUPPRESS-WARNINGS', 'SUPPRESS-W'))
def t_SUPPRESS_WARNINGS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('SYSTEM-ALERT-BOXES', 'SYSTEM-ALERT'))
def t_SYSTEM_ALERT_BOXES(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('TEMP-DIRECTORY', 'TEMP-DIR'))
def t_TEMP_DIRECTORY(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('TITLE-BGCOLOR', 'TITLE-BGC'))
def t_TITLE_BGCOLOR(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('TITLE-DCOLOR', 'TITLE-DC'))
def t_TITLE_DCOLOR(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('TITLE-FGCOLOR', 'TITLE-FGC'))
def t_TITLE_FGCOLOR(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('TITLE-FONT', 'TITLE-FO'))
def t_TITLE_FONT(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('TRUNCATE', 'TRUNC'))
def t_TRUNCATE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('UNBUFFERED', 'UNBUFF'))
def t_UNBUFFERED(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('VARIABLE', 'VAR'))
def t_VARIABLE(t):
    t.tag='blue'
    return t

@TOKEN(build_regex('VERTICAL', 'VERT'))
def t_VERTICAL(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('VIRTUAL-HEIGHT-CHARS', 'VIRTUAL-HEIGHT'))
def t_VIRTUAL_HEIGHT_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('VIRTUAL-HEIGHT-PIXELS', 'VIRTUAL-HEIGHT-P'))
def t_VIRTUAL_HEIGHT_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('VIRTUAL-WIDTH-CHARS', 'VIRTUAL-WIDTH'))
def t_VIRTUAL_WIDTH_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('VIRTUAL-WIDTH-PIXELS', 'VIRTUAL-WIDTH-P'))
def t_VIRTUAL_WIDTH_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('WIDGET-ENTER', 'WIDGET-E'))
def t_WIDGET_ENTER(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('WIDGET-LEAVE', 'WIDGET-L'))
def t_WIDGET_LEAVE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('WIDTH-CHARS', 'WIDTH'))
def t_WIDTH_CHARS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('WIDTH-PIXELS', 'WIDTH-P'))
def t_WIDTH_PIXELS(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('WINDOW-STATE', 'WINDOW-STA'))
def t_WINDOW_STATE(t):
    t.tag='cyan'
    return t

@TOKEN(build_regex('send-sql-statement', 'send-sql'))
def t_send_sql_statement(t):
    t.tag='cyan'
    return t

def t_COMPARISON_OP(t):
    r'\b(?:GE|LE|GT|LT)\b'
    return t

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



# This will track whitespace and adds a lot of time to processing. Ideally it
# would not be needed, but indentation rules has not been implemented yet. 
t_WHITESPACE = r'\s+'

literals = [ '+','-','*','/', '"', "'", '(', ')', '[', ']', '{', '}', ',', ':', ';', '=', '?', '~', '.', '>', '<', '!' ]

# Some of these might be better not ignored. However for syntax highlighting
# they throw a lot of errors. As this is continuing, it might be better to 
# define 2 states, one for syntax highlighting and one for parsing.
# t_ignore = r'.'
t_ignore = '}\t'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_\-\.0-9]*[a-zA-Z_\-0-9]|\b[a-zA-Z]\b'
    result = reserved.get(t.value.upper(),'ID')    # Check for reserved words
    if isinstance(result, tuple):
        t.type = result[0]
        t.tag  = result[1]
    # All non progress words
    elif result == 'ID':
        t.result = result
        t.tag = 'grey'
    else:
        t.type = result
        t.tag = 'cyan' 
    return t

# This isn't really doing much i think... 
def t_WORK_IN_PROGRESS(t):
    r'{[a-zA-Z_ ]*[a-zA-Z_\-\.0-9]*'

    t.tag = 'grey'
    return t

def t_error(t):
    print(f"Illegal character {t.value[0:50]} @ ln:{t.lineno} col:{t.colno}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    return t
    # t.lexer.skip(1)
