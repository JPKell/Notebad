# Local imports
from modules.logging    import Log
from settings           import Configuration
from view.ide.clipboard import Clipboard
from view.ide.editor    import Editor
from view.ide.history   import History
from view.ide.toolbar   import Toolbar
from widgets            import NText, NTabFrame, TextFooter


cfg = Configuration()
logger = Log(__name__)

class Ide(NTabFrame):
    ''' This is where the magic happens. This is the text area where the user 
        is typing. This class is responsible for the text area, line numbers, 
        and scrollbars. Syntax highlighting is a beast of it's own and is 
        separated into it's own module. '''

    def __init__(self, parent) -> None:
        super().__init__(parent, padding=0, border=0, relief='flat')
        logger.debug("Textbox begin init")

        # Class variables
        self._language  = None                  # Programming language of source
        self.disable_line_no_update = False     # Line number proxy drags on mass edits
        self.file_name = cfg.new_file_name 

        # Build the objects
        self.text      = NText(self)
        self.editor    = Editor(text=self.text)
        self.clipboard = Clipboard(editor=self.editor, text=self.text)
        self.history   = History(ide=self, editor=self.editor, text=self.text)
        self.toolbar   = Toolbar(ide=self, editor=self.editor, text=self.text)
        self.footer    = TextFooter(parent=self, text=self.text)

        self._binds()
        self._prep_ide()
        self._grid()

        logger.debug(f"Textbox finish init: {self.file_name}")

    def __repr__(self) -> str:
        ''' Override how the class looks when printed.'''
        return f"IDE: {self.file_name} TK: {self.tab_tk_name}"

    @property
    def language(self) -> str:
        return self._language
    
    @language.setter
    def language(self, language:str) -> None:
        ''' Updating the language will also update the syntax highlighting 
            if it is enabled. '''
        self._language = language
        self.footer.lang_lbl.config(text=language)
        logger.debug(f"Language set to: {language}")
        
    @property
    def is_blank(self) -> bool:
        ''' Returns True if the text area has not had a single character entered. 
            By default a text area will house a new line character. So len is not
            a good way to check if the text area is blank. Also, Ctrl-o default
            behavior is to add a newline. So we check for a double new line when
            trying to open a file on a blank tab using a hotkey.
        '''
        return self.text.get(1.0, 'end') == '\n' or self.text.get(1.0, 'end') == '\n\n'

    ###
    # Public methods
    ###

    ###
    # Private methods
    ###
    def _binds(self) -> None:
        ''' Some keys need specific bindings to behave how you expect in a text editor '''

        # I am not certain about bind vs bind_all and where we need each. This should get documented somewhere. 
        self.text.bind("<KP_Enter>", lambda event: self.editor.add_newline())
        self.text.bind_all("<<Cut>>", lambda event: self.clipboard.cut_text())
        self.text.bind_all("<<Copy>>", lambda event: self.clipboard.copy_text())
        self.text.bind_all("<<Paste>>", lambda event: self.clipboard.paste_text())
        self.text.bind_all("<<Undo>>", lambda event: self.history.undo())
        self.text.bind_all("<<Redo>>", lambda event: self.history.redo())
        self.bind_all("<<FindNext>>", lambda event:self.editor.find_next(direction=1))
        self.bind_all("<<FindPrev>>", lambda event: self.editor.find_next(direction=-1))


        # This is currently the primary way to check if the line numbers
        # need to be redrawn. This may need to be changed when the language server 
        # is updated (created).  
        self.text.bind('<Key>', lambda event: self._check_on_key(event))

    def _check_on_key(self, event) -> None:
        ''' This is the function that runs upon every keypress. If there is a
            way to do any of these outside of checking every keystroke that's 
            a better option. The functions called from here tend to be blocking
            and will cause user input to be delayed. 
        
            Event state 16 is when no modifier keys are pressed. It will not 
            fire when shift and an alphanumeric key is pressed.'''
        
        # Check if the document has been updated since last saved
        if not self.tab_save_on_close and event.state == 16:
            self.history.stackify()
            self.tab_save_on_close = True
            self.tab_title = f'{self.file_name} *'
            return

        # Pushes the current state of the document onto the stack for undo
        if event.char in [' ', '\t', '\n']:
            self.history.stackify()

    def _grid(self) -> None:
        ''' Grid the text area and line numbers '''
        # Build the parent frame
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.grid(row=0, column=0, sticky='nswe') 

        self.toolbar.grid(row=0, column=0, pady=(3,5), sticky='nsew')
        self.text.grid(row=1, column=0, sticky='nsew')
        self.footer.grid(row=2, column=0, sticky='nsew')

    def _prep_ide(self) -> None:
        ''' This is called after the init is finished. It is used to 
            call functions that need to be called after the init is 
            finished. '''
        self.text.focus_set()
        self.text.mark_set("insert", "1.0")
        self.text.see("insert")
        self.text.focus_set()

        self.tab_title = self.file_name

    def _set_theme(self):
        self.text._set_theme()