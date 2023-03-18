import pathlib, os
import tkinter as tk

from calc.controller import Calculator
from conf  import cf
from model import LanguageModel
from view  import NoteView
from views.textbox import Textbox

import time

class NoteController:
    ''' The controller is the glue between the model and the view. It is the
        controller that binds the view to the model. The controller is also
        responsible for managing the application. '''
    def __init__(self, model:LanguageModel):
        self.app = tk.Tk()          # Root window
        self.model = model          # Model is passed in from main.py, this may change?
        self.view  = NoteView(self) # View is instantiated here, passing the controller into the view
        self.clipboard = ''         # Clipboard is an application feature and thus lives here
        self._bind_keys()
        self._app_protocols()

        if cf.preload_file:
            self.__write_file_to_textbox(self.view.textbox, cf.preload_file)


    def _app_protocols(self) -> None:
        ''' Application protocols deal with system commands such as closing the window. '''
        self.app.protocol("WM_DELETE_WINDOW", self.exit_app)

    def relative_to_abs_path(self, rel_path:str) -> str:
        ''' Returns the absolute path of a relative path. '''
        current_dir = pathlib.Path(__file__).parent.resolve() # current directory
        return os.path.join(current_dir, rel_path) 

    def run(self) -> None:
        ''' Start 'er up! Run is called from outside the controller allowing for 
            everything to be set up first. '''
        self.app.mainloop()

    def exit_app(self) -> None:
        ''' Exit the application. Optional hardcore mode will disable the prompt.
            This is useful for testing. To quote the devs at Bethseda, 
                "Save often, the plains of Oblivion are a dangerous place." 
        ''' 
        tab_list = self.view.tabs.tabs()
        if not cf.hardcore_mode:
            for tab in tab_list:
                self.view.tabs.select(tab)
                if self.view.textbox.changed_since_saved:
                    self.view.prompt_yes_no(
                        "You have unsaved changes", 
                        f"Save {self.view.textbox.file_name}?", 
                        self.save_file)
        self.view.master.destroy()


    ## File management ##
    def new_textbox(self) -> None:
        ''' Creates a new tab and a crisp fresh textbox. '''
        self.view.tabs.new_tab()
        self.view.tabs.move_to_tab()    # Move focus to the new tab

    def open_file(self) -> None:
        ''' Opens a file. There should be an encoding option here. But there 
            isn't, that should get added and this note removed. '''
        full_path = self.view.open_file_dialogue()
        if full_path:
            textbox = self.view.textbox         # Get the current textbox
            path_parts = self._parts_from_file_path(full_path)
            if not textbox.is_blank:            # Don't open a new tab if the current one is blank
                self.view.tabs.new_tab(file_name=path_parts['file'])
                self.view.tabs.move_to_tab()
                textbox = self.view.textbox     # Grab the newly minted textbox object 

            textbox.set_meta(
                tk_name=self.view.tabs.select(),
                full_path=full_path,
                file_path=path_parts['path'], 
                file_name=path_parts['file'], 
                )
            self.__write_file_to_textbox(textbox, full_path)
            self.view.update_title()

    def save_file(self) -> None:
        ''' Saves current textbox to disk. If not written to disk before,
            save_as_file is called to let the user name it. Also thinking 
            about just sequentially naming all the files to make like hard. jk'''
        textbox = self.view.textbox
        if textbox.file_name == cf.new_file_name:
            self.save_as_file(textbox)
        else:
            self._write_textbox_to_file(textbox.full_path, textbox)
        
    def save_as_file(self, textbox:Textbox=None) -> None:
        ''' Saves textbox to disk. If no textbox is given, the current tab is used.'''
        # I am giving the option here to pass a textbox object in to be saved. 
        # the time this would be useful would be in a save all function. But is that
        # something to worry about now? No. 
        if textbox is None:             
            textbox = self.view.textbox
        full_path = self.view.save_file_dialogue(file_name=textbox.file_name)
        if full_path:
            self._write_textbox_to_file(full_path, textbox)

    def _parts_from_file_path(self, full_path:str) -> dict:
        ''' Take the full path name and return a dictionary with the path and file name.
            `{ 'path': ..., 'file': ... }`
        '''
        if os.name == 'nt':         # Windows
            parts = full_path.split('\\')
            return {'path': '\\'.join(parts[:-1]), 'file': parts[-1]}
        else:                       # Linux/Mac
            parts = full_path.split('/')
            return {'path': '/'.join(parts[:-1]), 'file': parts[-1]}

    def __write_file_to_textbox(self, textbox:Textbox, full_path:str) -> None:
        ''' Writes the contents of a file to the textbox '''
        with open(full_path, "r") as file:
            textbox.insert('end', file.read())  # Insert the file contents into the textbox
            textbox.changed_since_saved = False # Reset the changed flag since we just opened the file
            textbox.stackify()                  # Add the file contents to the undo stack

    def _write_textbox_to_file(self, full_path:str, textbox:Textbox) -> None:
        ''' Private method to write file to disk. Needs encoding option. '''
        with open(full_path, "w") as file:
            txt = textbox.get(1.0, 'end')
            if len(txt) > 1:   
                txt = txt[:-1] # Trailing newline character that needs to be removed
            file.write(txt)
        # Update the textbox properties
        path_parts = self._parts_from_file_path(full_path)
        textbox.set_meta(tk_name=self.view.tabs.cur_tab_tk_name(),
                    full_path=full_path,
                    file_path=path_parts['path'], 
                    file_name=path_parts['file'], )
        textbox.changed_since_saved = False
        self.view.tabs.set_properties(textbox.tk_name, text=textbox.file_name)
        # Update the window title
        self.app.title(f"{cf.app_title} - {textbox.file_name}")

        
    ## Clipboard management ##
    # The OS can provide some of these functions, but this gives us more control
    # These should override the OS clipboard functions. Except for the paste function,
    # which should be able to paste from the OS clipboard as well as our own. 
    # This all might be excessive management and I should just use the OS clipboard
    def cut_text(self) -> None:
        ''' Don't run with scissors '''
        textbox = self.view.textbox
        self.clipboard = textbox.get_selection()    # This is our clipboard
        self.view.clipboard_append(self.clipboard)  # This is the OS clipboard
        textbox.delete_selection()  

    def copy_text(self) -> None:
        ''' Plagurism is bad '''
        textbox = self.view.tabs.textbox
        self.clipboard = textbox.get_selection()
        self.view.master.clipboard_append(self.clipboard)

    def paste_text(self) -> None:
        ''' Hand me that paper bag '''
        textbox = self.view.tabs.textbox
        textbox.insert('insert', self.clipboard)

    ###            ###
    # Language tools #
    ###            ###

    def capitalize_syntax(self, event) -> None:
        ''' Capitalizes syntax in current textbox '''
        t = time.time()
        textbox = self.view.textbox
        cur_index = textbox.index('insert')
        results = self.model.capitalize_syntax(textbox.get_all())

        # We want to disable the line number update otherwise we will 
        # end up blocking the app with thousands of inserts which trigger
        # events which will block in the Tk main loop. 
        textbox.disable_line_no_update = True

        textbox.clear_all()
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

        if cf.time_functions:
            print('Process took:', time.time() - t, 'seconds')


    def format_code(self, event) -> None:
        ''' To properly implement syntax highlighting we need to understand the
            context of the word we are working on. This means that if we are on 
            line 5 of a multi line comment we need to know that.'''

        # If the key pressed is a special key, we don't want to do anything
        if event.char == '':
            return

        if event.keysym == 'BackSpace':
            return

        textbox = self.view.textbox
        # The existing tags should give us the context of the word we are working on
        existing_tags = textbox.tag_names('insert -1c')

        # if 'comment' in existing_tags bail. we don't want to format comments
        if 'green' in existing_tags:
            return
        
        # There are times where we will end up formatting part way through a word or
        # statement, then there's also the case of a comment. In both cases we want
        # context outside of the tags we have.  
        
        if event.keycode == 36: # If the key pressed is a Enter
            # Get the current line
            textbox.mark_set('insert', 'insert -1l')
            txt = textbox.get_current_line_text()
            # I like the idea of expanding as you type, but it causes some issues
            # Mainly inserting the cursor in the right place after expanding words
            tokens = self.model.capitalize_syntax(txt, no_nl=True, expand=True) 
            # We want to disable the line number update otherwise we will block
            textbox.disable_line_no_update = True
            textbox.delete_cur_line()
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
            textbox.mark_set('insert', 'insert +1l')
            textbox.disable_line_no_update = False
    
        # Otherwise we just want to get and format one word
        else:
            # Get the current word
            txt, index = textbox.get_trailing_word_and_index()
            token = self.model.get_syntax_token(txt) 

            # If the token is empty we need to print the char, bail
            if len(token) == 0:
                return
            textbox.disable_line_no_update = True
            textbox.delete(index[0], index[1])
            textbox.insert(index[0], token[0].value, token[0].tag)
            textbox.disable_line_no_update = False


    ###          ###
    # Nifty things #
    ###          ###
    def eval_selection(self) -> None:
        ''' Evaluate a line or selection of code. The result is displayed in 
            the footer.
        
            Since Python is interpreted, we can evaluate code right in the text 
            box. This is handy to doing math or other simple things.'''
        selection = self.view.textbox.get_selection()
        # If there is nothing selected, evaluate the current line
        if selection == '':  
            selection = self.view.textbox.get_current_line_text()
        # If there is nothing still selected, do nothing
        if selection == '': 
            result = "Nothing to evaluate"
        else:
            # It's bad enough we are evaluating any user input, so lets at least 
            try: # to catch any errors that might occur.
                result = eval(selection)
            except:
                result = "Invalid Python syntax" 
        self.view.footer.set_status(result) # Return result to user

    def open_calculator(self):
        ''' Opens a calculator window. The calculator is basic, but maybe will improve.
            Maybe one day it will be a full scientific calculator, or have business 
            functions. Who knows. Might even have it's own tab. '''
        calculator = Calculator(self.view.ui.style)
        calculator.main()

    ###          ###
    # Key bindings #
    ###          ###
    def _bind_keys(self):
        ''' Key bindings are attached here. There is an important thing to know, 
            that they will be called in order from the class level up to 
            the app level. That means to override a key binding, you need to assign
            it at the class level and then return 'break' to stop the event from
            propagating up the levels. '''
        # File management
        self.app.bind("<Control-n>", lambda event: self.new_textbox())
        self.app.bind("<Control-o>", lambda event: self.open_file())
        self.app.bind("<Control-s>", lambda event: self.save_file())
        self.app.bind("<Control-S>", lambda event: self.save_as_file())  # Ctrl+Shift+s

        # UI management
        self.app.bind("<Control-equal>", lambda event: self.view.ui.font_size_bump(increase=True))
        self.app.bind("<Control-minus>", lambda event: self.view.ui.font_size_bump(increase=False))
        self.app.bind("<Alt-c>", lambda event: self.open_calculator())

        # Textbox overides #
        self.app.bind_class("Text", "<Control-d>", lambda event: self.view.ui.toggle_theme())
        self.app.bind_class("Text", "<Control-z>", lambda event: self.view.textbox.undo())
        self.app.bind_class("Text", "<Control-y>", lambda event: self.view.textbox.redo())

        self.app.unbind_all("<Tab>")    # Unbind the default tab key for all widgets before overriding it
        self.app.bind_class("Text", "<Tab>", lambda event: self.view.tabs.add_indent(), add=False)

        # Textbox management
        self.app.bind("<Control-a>", lambda event: self.view.tabs.textbox.select_all())
        
        # Syntax highlighting
        self.app.bind("<Key>", lambda event: self.format_code(event))
        self.app.bind_all("<space>", lambda event: self.format_code(event))
        self.app.bind_all("<Return>", lambda event: self.format_code(event))

        # Tab management
        self.app.bind("<<NotebookTabChanged>> ", lambda event: self.view.update_title())
        self.app.bind("<Control-w>",    lambda event: self.view.tabs.close_tab())
        self.app.bind("<Return>",       lambda event: self.view.tabs.textbox.hide_unused_scrollbars())
        self.app.bind("<space>",        lambda event: self.view.tabs.textbox.hide_unused_scrollbars())
        
        # Clipboard management
        self.app.bind("<Alt-e>", lambda event: self.eval_selection())

        # DEVELOPMENT ONLY
        self.app.bind("<Alt-p>", lambda event: self.capitalize_syntax(event))


        ###
        # Various tk keybindings that exist by default
        # 
        # <Control-p> previous line
        ###