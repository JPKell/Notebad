from settings import Configuration
from modules.logging import Log
from language import LanguageModel

cfg = Configuration()
logger = Log(__name__)

class LanguageTools:
    ''' The language tools are the tools that are used to manipulate the text
        in the textbox from the model. This includes syntax highlighting '''
    def __init__(self, controller, view):
        self.controller = controller
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
    def syntax_on_file_load(self, txt) -> None:
        ''' Capitalizes syntax in current textbox '''

        # Bail if we are not doing syntax highlighting
        if self.model.language_module is None or cfg.syntax_on_load is False:
            return        

        logger.debug('syntax_on_file_load begin')
        textbox = self.view.textbox
        cur_index = textbox.index('insert')

        results = self.model.format_syntax(txt, expand=False, upper=False)

        # We want to disable the line number update otherwise we will 
        # end up blocking the app with thousands of inserts which trigger
        # events which will block in the Tk main loop. 
        textbox.disable_line_no_update = True

        nl = True
        indent_level = 0
        indent = ''
        if not self.model.track_whitepace:
            for tok in results:
                # This is SUPER chatty. Only turn on if you need it. 
                logger.verbose(tok)
                
                spc = '' if nl or tok.value in ['.', ',', ':', '(', ')']  else ' '
                nl = False
                if tok.tag == 'nl':
                    # Add the indent only after a newline
                    indent = ' ' * (cfg.indent_size * indent_level)
                    textbox.insert('insert', tok.value)
                    nl=True
                    continue
                # For some characters we dont want a trailing space
                if tok.value in [':','(']:
                    # This is a hack, maybe worth it's own variable. 
                    nl = True
                    spc = ''

                # represents a negative indent immediately on ends of blocks
                if tok.indent == -99:
                    tok.indent = -1
                    indent = indent[:-cfg.indent_size]
                
                textbox.insert('insert',indent+spc+tok.value, tok.tag)

                # Increase and decrease points are set in the model
                indent_level += tok.indent
                # reset the indent so it's not between every line
                indent = ''

        else: # Dont track whitespace
            for tok in results:
                textbox.insert('insert',tok.value, tok.tag)

        textbox.disable_line_no_update = False
        # Return the cursor to the same position by deleting the place it
        # ended up and then setting it back to the original position 
        textbox.mark_unset('insert')
        textbox.mark_set('insert', cur_index)
        textbox.see('insert')
        logger.debug('syntax_on_file_load finish')


    @logger.performance
    def syntax_on_command(self, event) -> None:
        ''' Capitalizes syntax in current textbox '''

        logger.debug('syntax_on_command begin')
        textbox = self.view.textbox
        cur_index = textbox.index('insert')

        results = self.model.format_syntax(textbox.editor.get_all())

        # We want to disable the line number update otherwise we will 
        # end up blocking the app with thousands of inserts which trigger
        # events which will block in the Tk main loop. 
        textbox.disable_line_no_update = True

        textbox.editor.clear_all()

        nl = True
        indent_level = 0
        indent = ''
        if not self.model.track_whitepace:
            for tok in results:
                # This is SUPER chatty. Only turn on if you need it. 
                logger.verbose(tok)
                
                spc = '' if tok.value in ['.', ',', ':', '(', ')'] or nl else ' '
                nl = False
                if tok.tag == 'nl':
                    # Add the indent only after a newline
                    indent = ' ' * (cfg.indent_size * indent_level)
                    textbox.insert('insert', tok.value)
                    nl=True
                    continue
                # For some characters we dont want a trailing space
                if tok.value in [':','(']:
                    # This is a hack, maybe worth it's own variable. 
                    nl = True
                    spc = ''

                # represents a negative indent immediately on ends of blocks
                if tok.indent == -99:
                    tok.indent = -1
                    indent = indent[:-cfg.indent_size]
                
                textbox.insert('insert',indent+spc+tok.value, tok.tag)

                # Increase and decrease points are set in the model
                indent_level += tok.indent
                # reset the indent so it's not between every line
                indent = ''

        else: # Dont track whitespace
            for tok in results:
                textbox.insert('insert',tok.value, tok.tag)

        logger.debug("Replaced text")

        textbox.disable_line_no_update = False
        # Return the cursor to the same position by deleting the place it
        # ended up and then setting it back to the original position 
        textbox.mark_unset('insert')
        textbox.mark_set('insert', cur_index)
        textbox.see('insert')
        logger.debug('syntax_on_command finish')

    # Dont need the performance running on this all the time but the last time 
    # it was run it was taking 0.00013 seconds.
    # @logger.performance
    def syntax_while_typing(self, event) -> None:
        ''' To properly implement syntax highlighting we need to understand the
            context of the word we are working on. This means that if we are on 
            line 5 of a multi line comment we need to know that.'''
        
        # Bail if we are not using syntax highlighting
        if self.model.language_module is None or cfg.syntax_on_type is False:
            return
        
        logger.verbose('syntax_while_typing')

        textbox = self.view.textbox

        if textbox.meta.language == '':
            return

        # If the key pressed is a special key, we don't want to do anything
        if event.char == '' and event.keysym != 'Up' and event.keysym != 'Down':
            return

        if event.keysym == 'BackSpace':
            return

        # The existing tags should give us the context of the word we are working on
        existing_tags = textbox.tag_names('insert -1c')

        # if 'comment' in existing_tags bail. we don't want to format comments
        if 'green' in existing_tags:
            return
        
        # There are times where we will end up formatting part way through a word or
        # statement, then there's also the case of a comment. In both cases we want
        # context outside of the tags we have.  
        if cfg.os == 'nt':
            rtn = 13
            up = 38
            down = 40
            kp_enter = 104
            key = [rtn,kp_enter,down]
        else:
            rtn = 36
            up = 111
            down = 116
            kp_enter = 104
            key = [rtn,kp_enter,down]


        if event.keycode in key: # If the key pressed is a Enter
            # Get the current line
            textbox.mark_set('insert', f'insert -1l')
            txt = textbox.editor.get_current_line_text()
            # I like the idea of expanding as you type, but it causes some issues
            # Mainly inserting the cursor in the right place after expanding words
            tokens = self.model.format_syntax(txt, no_nl=True, expand=True) 
            # We want to disable the line number update otherwise we will block
            textbox.disable_line_no_update = True
            textbox.editor.delete_cur_line()


            nl = True
            indent_level = 0
            indent = ''
            if not self.model.track_whitepace:
                for tok in tokens:
                    # This is SUPER chatty. Only turn on if you need it. 
                    logger.verbose(tok)
                    
                    spc = '' if tok.value in ['.', ',', ':', '(', ')'] or nl else ' '
                    nl = False
                    if tok.tag == 'nl':
                        # Add the indent only after a newline
                        indent = ' ' * (cfg.indent_size * indent_level)
                        textbox.insert('insert', tok.value)
                        nl=True
                        continue
                    # For some characters we dont want a trailing space
                    if tok.value in [':','(']:
                        # This is a hack, maybe worth it's own variable. 
                        spc = ''
                        nl = True

                    # represents a negative indent immediately on ends of blocks
                    if tok.indent == -99:
                        tok.indent = -1
                        indent = indent[:-cfg.indent_size]
                    
                    textbox.insert('insert',indent+spc+tok.value, tok.tag)

                    # Increase and decrease points are set in the model
                    indent_level += tok.indent
                    # reset the indent so it's not between every line
                    indent = ''

            else: # Dont track whitespace
                for tok in tokens:
                    textbox.insert('insert',tok.value, tok.tag)
            
            # Return the cursor to the new line
            textbox.mark_set('insert', 'insert +1l linestart')
            textbox.disable_line_no_update = False
    
        # Otherwise we just want to get and format one word
        else:
            txt = textbox.editor.get_current_line_text()
            index = textbox.index('insert')

            # I like the idea of expanding as you type, but it causes some issues
            # Mainly inserting the cursor in the right place after expanding words
            tokens = self.model.format_syntax(txt, no_nl=True, expand=False, upper=False) 
            
            # We want to disable the line number update otherwise we will block
            textbox.disable_line_no_update = True
            textbox.editor.delete_cur_line()

            nl = True
            indent_level = 0
            indent = ''
            if not self.model.track_whitepace:
                for tok in tokens:
                    # This is SUPER chatty. Only turn on if you need it. 
                    logger.verbose(tok)
                    
                    spc = '' if tok.value in ['.', ',', ':', '(', ')'] or nl else ' '
                    nl = False
                    if tok.tag == 'nl':
                        # Add the indent only after a newline
                        indent = ' ' * (cfg.indent_size * indent_level)
                        textbox.insert('insert', tok.value)
                        nl=True
                        continue
                    # For some characters we dont want a trailing space
                    if tok.value in [':','(']:
                        # This is a hack, maybe worth it's own variable. 
                        spc = ''
                        nl = True

                    # represents a negative indent immediately on ends of blocks
                    if tok.indent == -99:
                        tok.indent = -1
                        indent = indent[:-cfg.indent_size]
                    
                    textbox.insert('insert',indent+spc+tok.value, tok.tag)

                    # Increase and decrease points are set in the model
                    indent_level += tok.indent
                    # reset the indent so it's not between every line
                    indent = ''

            else: # Dont track whitespace
                for tok in tokens:
                    textbox.insert('insert',tok.value, tok.tag)
            
            
            # Return the cursor to the new line
            textbox.mark_set('insert', index)
            textbox.disable_line_no_update = False
        logger.verbose('syntax_while_typing finish')