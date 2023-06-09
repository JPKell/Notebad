import pathlib, os
from tkinter import Tk

from language        import LanguageModel
from modules.logging import Log
from settings        import Configuration
from view            import NotebadView
from view.ide        import Ide
from view.profiler   import ProgressProfiler

cfg = Configuration()
logger = Log(__name__)

class LanguageTools:
    ''' The language tools are the tools that are used to manipulate the text
        in the textbox from the model. This includes syntax highlighting '''
    def __init__(self, app: Tk, view: NotebadView):
        self.app = app
        self.view = view
        self.current_language = None
        self.model = LanguageModel()
        logger.debug('LanguageTools init')

    def load_language(self, lang:str) -> None:
        ''' Loads a language into the model '''
        # Bail if we are already using this language
        if self.current_language == lang:
            return

        self.model.load_language(lang)
        self.current_language = lang
        logger.debug('load_language finish')

    @logger.performance
    def static_syntax_formatting(self, file_txt=None, expand=None, upper=None, indent=None) -> None:
        ''' Performs static syntax formatting on the textbox. Either event or txt
            must be passed in. Event comes along with the Tkinter event. txt is
        '''
        # Bail if we are not doing syntax highlighting
        if self.model.language_module is None:
            return
        # If passing text we must be loading the text directly from a file       
        if cfg.syntax_on_load is False and file_txt != None:
            return

        # If not passed config values, use the preferences
        expand = expand if expand is not None else cfg.syntax_expand
        upper  = upper  if upper  is not None else cfg.syntax_uppercase
        indent = indent if indent is not None else cfg.syntax_indent

        logger.debug('static_syntax_formatting begin')

        # Get the current textbox and cursor position
        ide = self.view.cur_tab if self.view.cur_tab is not None else Ide()
        cur_index = ide.text.index('insert')

        if file_txt is None:
            file_txt = ide.text.get('1.0', 'end')

        results = self.model.format_syntax(file_txt, expand=expand, upper=upper)

        # We want to disable the line number update otherwise we will 
        # end up blocking the app with thousands of inserts which trigger
        # events which will block in the Tk main loop. 
        ide.text.disable_line_no_update = True
        ide.editor.clear_all()

        nl = True
        indent_level = 0
        indent = ''
        if not self.model.track_whitepace or cfg.syntax_indent:
            # Incase the models DOES track whitespace but we are are indenting
            # we must ignore the whitespace tokens 
            ignore_whitespace = True if cfg.syntax_indent and self.model.track_whitepace else False

            for tok in results:
                # logger.warn(tok)
                if ignore_whitespace and tok.type == 'WHITESPACE':
                    continue
                # This is SUPER chatty. Only turn on if you need it. 
                # logger.verbose(tok)
                
                spc = '' if nl or tok.value in ['.', ',', ':', '(', ')']  else ' '
                nl = False
                if tok.tag == 'nl':
                    # Add the indent only after a newline. We build the indent 
                    # this line, and then add it to the next line
                    indent = ' ' * (cfg.indent_size * indent_level)
                    ide.text.insert('insert', tok.value)
                    nl=True
                    continue

                # For some characters we dont want a trailing space
                if tok.type in ['LPAREN']:
                    # This is a hack, maybe worth it's own variable. 
                    nl = True
                    spc = ''

                # Some we just want to remove the leading space
                if tok.type in ['COLON','ARRAY_BRACE']:
                    spc = ''

                # represents a negative indent immediately on ends of blocks
                if tok.indent == -99:
                    tok.indent = -1
                    indent = indent[:-cfg.indent_size]
                
                ide.text.insert('insert',indent+spc+tok.value, tok.tag)

                # Increase and decrease points are set in the model
                indent_level += tok.indent
                # reset the indent so it's not between every line
                indent = ''

        else: # Dont track whitespace
            for tok in results:
                ide.text.insert('insert',tok.value, tok.tag)

        ide.text.disable_line_no_update = False
        # Return the cursor to the same position by deleting the place it
        # ended up and then setting it back to the original position 
        ide.text.mark_unset('insert')
        ide.text.mark_set('insert', cur_index)
        ide.text.see('insert')
        logger.debug('syntax_on_file_load finish')


    # Dont need the performance running on this all the time but the last time 
    # it was run it was taking 0.00013 seconds.
    # @logger.performance
    def dynamic_syntax_formatting(self, event) -> None:
        ''' To properly implement syntax highlighting we need to understand the
            context of the word we are working on. This means that if we are on 
            line 5 of a multi line comment we need to know that.'''
        
        # These config options are set in personal options. They are currently 
        # not passed in, but could be. 
        expand = cfg.syntax_expand
        upper  = cfg.syntax_uppercase
        indent = cfg.syntax_indent

        # Bail if we are not using syntax highlighting
        if self.model.language_module is None or cfg.syntax_on_type is False:
            return

        # If the key pressed is a special key, we don't want to do anything
        # Except that we want to let up and down through as we may want to 
        # keep track of the indent level
        if event.char == '' and event.keysym != 'Up' and event.keysym != 'Down':
            return

        if event.keysym == 'BackSpace':
            return
        
        # Now we know we want to proceed lets get the textbox
        # the if statement is just to give us the code completion while working
        ide = self.view.cur_tab if self.view.cur_tab is not None else Ide()

        # The existing tags should give us the context of the word we are working on
        existing_tags = ide.text.tag_names('insert -1c')

        # if 'comment' in existing_tags bail. we don't want to format comments
        if 'green' in existing_tags:
            return
        

        # There are times where we will end up formatting part way through a word or
        # statement, then there's also the case of a comment. In both cases we want
        # context outside of the tags we have. When we do anything to go to the next 
        # line we need to handle it differently than if just typing
        if cfg.os == 'nt':
            rtn = 13
            up = 38
            down = 40
            kp_enter = 104
        else:
            rtn = 36
            up = 111
            down = 116
            kp_enter = 104

        # Not using up, but leaving the keycode in for now.
        trigger_keys = [rtn,kp_enter,down]
        if event.keycode in trigger_keys: 
            
            # Get the current line
            ide.text.mark_set('insert', f'insert -1l')           
            txt = ide.editor.get_current_line_text()

            # I like the idea of expanding as you type, but it causes some issues
            # Mainly inserting the cursor in the right place after expanding words
            tokens = self.model.format_syntax(txt, no_nl=True, expand=expand, upper=upper) 

            # We need to know the indent level of the current line so we dont strip the indent from it
            nl = True
            indent_level = (len(txt.replace('\t',' ' * cfg.indent_size)) - len(txt.lstrip())) // cfg.indent_size
            indent = ' ' * (cfg.indent_size * indent_level)

            # We want to disable the line number update otherwise we will block
            ide.text.disable_line_no_update = True
            ide.editor.delete_cur_line()
            if not self.model.track_whitepace or cfg.syntax_indent:
                ignore_whitespace = True if cfg.syntax_indent and self.model.track_whitepace else False
                for tok in tokens:
                    if ignore_whitespace and tok.type == 'WHITESPACE':
                        continue

                    spc = '' if tok.value in ['.', ',', ':', '(', ')'] or nl else ' '
                    nl = False

                    # For some characters we dont want a trailing space
                    if tok.type in ['COLON','LPAREN']:
                        # This is a hack, maybe worth it's own variable. 
                        spc = ''
                        nl = True
                    
                    ide.text.insert('insert',indent+spc+tok.value, tok.tag)

                    # represents a negative indent immediately on ends of blocks
                    if tok.indent == -99:
                        tok.indent = -1
                        indent = indent[:-cfg.indent_size]

                    # Increase and decrease points are set in the model
                    indent_level += tok.indent
                    # reset the indent so it's not between every line
                    indent = ''

            else: # Dont track whitespace
                for tok in tokens:
                    ide.text.insert('insert',tok.value, tok.tag)
            
            # Return the cursor to the new line
            ide.text.mark_set('insert', 'insert +1l linestart')

            if cfg.syntax_indent:
                indent = ' ' * (cfg.indent_size * indent_level)
                ide.text.insert('insert', indent)

            ide.text.disable_line_no_update = False

        # Otherwise we just want to get and format one word
        else:
            txt = ide.editor.get_current_line_text()
            index = ide.text.index('insert')

            # I like the idea of expanding as you type, but it causes some issues
            # Mainly inserting the cursor in the right place after expanding words
            tokens = self.model.format_syntax(txt, no_nl=True, expand=False, upper=False) 

            # We want to disable the line number update otherwise we will block
            ide.text.disable_line_no_update = True
            ide.editor.delete_cur_line()

            # else: # Dont track whitespace
            for tok in tokens:
                ide.text.insert('insert',tok.value, tok.tag)
            
            # Return the cursor to the new line
            ide.text.mark_set('insert', index)
            ide.text.disable_line_no_update = False

        logger.verbose('syntax_while_typing finish')

    @logger.performance
    def expand_includes(self, profiler:ProgressProfiler) -> None:
        ''' Expands the include statements in the current file. 
            This is a recursive function that will expand all the files
            that are included in the current file.
            
            It uses the full abl profile and thats excessive we just need to remove the ones 
            inside comments. Once the language is more solid it can get it's own simple profile.'''
        logger.debug('expand_includes start')
        filename = profiler.tree.current_line()

        # This should have a check first if the language is ABL if this is the solution
        self.load_language('abl')

        def expand_includes_recursive(fname):
            ''' Builds a list of all the files that are included in the current file. '''
            path = os.path.join(cfg.project_src, fname)
            if not os.path.exists(path):
                raise FileNotFoundError(f'File not found: {fname}')
            
            with open(path, 'r', encoding=cfg.file_encoding) as f:
                txt = f.read()

            tokens = self.model.format_syntax(txt, no_nl=False, expand=False, upper=False) 

            output = []
            for tok in tokens:
                if tok.type == 'CURLY_BRACE':
                    fn = tok.value[1:-1].split(' ')[0]
                    if fn.find('.') != -1:
                        profiler.text.insert('insert',f'Expanding: {fn}\n', 'orange')
                        
                        # By using update it slows down the process but it allows the user to see what is happening 
                        profiler.update() 
                        output += expand_includes_recursive(fn)
                    else:
                        output += [tok.value]
                else:
                    output += [tok.value]
                # ide.text.insert('insert',tok.value, tok.tag)
            return output
        
        # Clear output for the loading text        
        profiler.text.delete('1.0', 'end')

        # Start the recursive function
        output = expand_includes_recursive(filename)

        # Clear the loading text
        profiler.text.delete('1.0', 'end')

        profiler.text.disable_line_no_update = True
        for token in output:
            # Todo when this is more performant we can add the tags back in. They will need to be added back at the recursive level
            profiler.text.insert('insert',token)

        for ln in profiler.profiler_data[filename]['lines'].keys():
            profiler.text.highlight_line(ln)
        logger.debug('expand_includes finish')

        profiler.text.disable_line_no_update = False