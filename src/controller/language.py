from modules.logging import Log
from language import LanguageModel

logger = Log(__name__)

class LanguageTools:
    ''' The language tools are the tools that are used to manipulate the text
        in the textbox from the model. This includes syntax highlighting '''
    def __init__(self, controller, view):
        self.controller = controller
        self.view = view
        self.model = LanguageModel()
        self.conf = controller.conf
        logger.debug('LanguageTools init')

    def load_language(self, lang:str) -> None:
        ''' Loads a language into the model '''

        self.model.load_language(lang)
        logger.debug('load_language finish')


    @logger.performance
    def load_with_basic_highlighting(self, txt) -> None:
        ''' Capitalizes syntax in current textbox '''
        logger.debug('load_with_basic_highlighting begin')
        textbox = self.view.textbox
        cur_index = textbox.index('insert')

        results = self.model.format_syntax(txt, expand=False, upper=False)

        # We want to disable the line number update otherwise we will 
        # end up blocking the app with thousands of inserts which trigger
        # events which will block in the Tk main loop. 
        textbox.disable_line_no_update = True

        # textbox.editor.clear_all()
        for tok in results:
            textbox.insert('insert',tok.value, tok.tag)

        textbox.disable_line_no_update = False
        # Return the cursor to the same position by deleting the place it
        # ended up and then setting it back to the original position 
        textbox.mark_unset('insert')
        textbox.mark_set('insert', cur_index)
        textbox.see('insert')
        logger.debug('load_with_basic_highlighting finish')


    @logger.performance
    def capitalize_syntax(self, event) -> None:
        ''' Capitalizes syntax in current textbox '''
        logger.debug('capitalize_syntax begin')
        textbox = self.view.textbox
        cur_index = textbox.index('insert')

        results = self.model.format_syntax(textbox.editor.get_all())

        # We want to disable the line number update otherwise we will 
        # end up blocking the app with thousands of inserts which trigger
        # events which will block in the Tk main loop. 
        textbox.disable_line_no_update = True

        textbox.editor.clear_all()
        nl = True
        for tok in results:

            ###
            # STOP! the commented out code is if whitespace is not tracked.
            ###
            # spc = '' if tok.value in ['.', ',', ':', '(', ')'] or nl else ' '
            # nl = False
            # if tok.tag == 'nl':
            #     textbox.insert('insert', tok.value)
            #     nl=True
            #     continue
            # # For some characters we dont want a trailing space
            # if tok.value in [':']:
            #     # This is a hack, maybe worth it's own variable. 
            #     nl = True
            # textbox.insert('insert',spc+tok.value, tok.tag)
            textbox.insert('insert',tok.value, tok.tag)
            ###
            # If restoring , delete the above line and uncomment the rest
            ###


        textbox.disable_line_no_update = False
        # Return the cursor to the same position by deleting the place it
        # ended up and then setting it back to the original position 
        textbox.mark_unset('insert')
        textbox.mark_set('insert', cur_index)
        textbox.see('insert')
        logger.debug('capitalize_syntax finish')

    # Dont need the performance running on this all the time but the last time 
    # it was run it was taking 0.00013 seconds.
    # @logger.performance
    def format_code(self, event) -> None:
        ''' To properly implement syntax highlighting we need to understand the
            context of the word we are working on. This means that if we are on 
            line 5 of a multi line comment we need to know that.'''
        if self.model.language_module is None:
            return
        
        logger.verbose('format_code')

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
        if self.conf.os == 'nt':
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
            for i,tok in enumerate(tokens):

                ###
                # STOP! the commented out code is if whitespace is not tracked.
                ###
                # spc = '' if tok.value in ['.', ','] or nl else ' '
                # nl = False
                # if tok.tag == 'nl':
                #     textbox.insert('insert', tok.value)
                #     nl=True
                #     continue
                # textbox.insert('insert',spc+tok.value, tok.tag)
                textbox.insert('insert',tok.value, tok.tag)
                ###
                # If restoring , delete the above line and uncomment the rest
                ###
            
            # Return the cursor to the new line
            textbox.mark_set('insert', 'insert +1l linestart')
            textbox.disable_line_no_update = False
    
        # Otherwise we just want to get and format one word
        else:
            # # Get the current word
            # txt, index = textbox.get_trailing_word_and_index()
            # print('before syntax',txt, index)
            # token = self.model.get_syntax_token(txt) 
            # print(token)
            # # If the token is empty we need to print the char, bail
            # if len(token) == 0:
            #     return
            # textbox.disable_line_no_update = True
            # textbox.delete(index[0], index[1])
            # textbox.insert(index[0], token[0].value, token[0].tag)
            # textbox.disable_line_no_update = False

            txt = textbox.editor.get_current_line_text()
            index = textbox.index('insert')
            # I like the idea of expanding as you type, but it causes some issues
            # Mainly inserting the cursor in the right place after expanding words
            tokens = self.model.format_syntax(txt, no_nl=True, expand=False, upper=False) 
            # We want to disable the line number update otherwise we will block
            textbox.disable_line_no_update = True
            textbox.editor.delete_cur_line()
            nl = True
            for i,tok in enumerate(tokens):

                ###
                # STOP! the commented out code is if whitespace is not tracked.
                ###
                # spc = '' if tok.value in ['.', ','] or nl else ' '
                # nl = False
                # if tok.tag == 'nl':
                #     textbox.insert('insert', tok.value)
                #     nl=True
                #     continue
                # textbox.insert('insert',spc+tok.value, tok.tag)
                textbox.insert('insert',tok.value, tok.tag)
                ###
                # If restoring , delete the above line and uncomment the rest
                ###
            
            # Return the cursor to the new line
            textbox.mark_set('insert', index)
            textbox.disable_line_no_update = False
        logger.verbose('format_code finish')