from tkinter     import SEL

from modules.logging        import Log
from settings               import Configuration

from view.ide.clipboard     import Clipboard
from view.ide.edit          import Editor
from view.ide.meta          import Meta
from view.ide.undo_stack    import History
from view.ide.toolbar       import Toolbar
from widgets import NText, NNotebook, NTabFrame


cfg = Configuration()
logger = Log(__name__)

class Ide(NTabFrame):
    ''' This is where the magic happens. This is the text area where the user 
        is typing. This class is responsible for the text area, line numbers, 
        and scrollbars. Syntax highlighting is a beast of it's own and is 
        separated into it's own module. '''

    def __init__(self, tab_widget:NNotebook) -> None:
        logger.debug("Textbox begin init")
        super().__init__(tab_widget, padding=0, border=0, relief='flat')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.tab_title = "CHANGE ME"

        self.tab_widget = tab_widget
        self.grid(row=0, column=0, sticky='nswe') 
        # If the area is in focus we want to be active. When inactive, things
        # on the event loop should be turned off.
        self._is_focus = False

        # Line number updates is a whole thing. It uses a proxy and if we are 
        # doing mass updates we want to be able to turn that off. 
        self.disable_line_no_update = False

        # tabs is the parent widget
        self.view = self.tab_widget.view

        
        # Build all the objects associated with the text area
        self.meta      = Meta(self, self.tab_widget)
        self.toolbar   = Toolbar(self)
        self.text      = NText(self)
        self.history   = History(self)
        self.clipboard = Clipboard(self)
        self.editor    = Editor(self.text)

        # Handle special keybindings
        self._bind_keys()

        # Text area settings
        self._make_text_area() 
        
        # This is currently the primary way to check if the line numbers
        # need to be redrawn. This may need to be changed when the language server 
        # is updated (created).  
        self.text.bind('<Key>', lambda event: self.check_on_key(event))

        # Store any selected text and weather the selection has changed
        # NOTE: de-selecting a current selection will also trigger the <<Selection>> event.
        self.current_selection_text = ""
        self.text.bind("<<Selection>>", self.update_selection)
       
        logger.debug(f"Textbox finish init: {self.meta.file_name}")

    ###              ###
    # Class properties #
    ###              ###

    @property
    def is_focus(self) -> bool:
        return self._is_focus
    
    @is_focus.setter
    def is_focus(self, is_focus:bool) -> None:
        # Turn on any of the items in the event loop
        self._is_focus = is_focus
        # if is_focus:
        #     self.scrollbars.hide_unused()
            # self.footer.update_cursor_pos()
        
    @property
    def is_blank(self) -> bool:
        ''' Returns True if the text area has not had a single character entered. 
            By default a text area will house a new line character. So len is not
            a good way to check if the text area is blank. Also, Ctrl-o default
            behavior is to add a newline. So we check for a double new line when
            trying to open a file on a blank tab using a hotkey.
        '''
        return self.text.get(1.0, 'end') == '\n' or self.text.get(1.0, 'end') == '\n\n'

    def check_on_key(self, event) -> None:
        ''' This is the function that runs upon every keypress. If there is a
            way to do any of these outside of checking every keystroke that's 
            a better option. The functions called from here tend to be blocking
            and will cause user input to be delayed. 
        
            Event state 16 is when no modifier keys are pressed. It will not 
            fire when shift and an alphanumeric key is pressed.'''
        
        # Check if the document has been updated since last saved
        if not self.meta.changed_since_saved and event.state == 16:
            self.history.stackify()
            self.meta.changed_since_saved = True
            self.tab_widget.set_properties(self.tab_tk_name, text=f'{self.meta.file_name} *')
            return

        # Pushes the current state of the document onto the stack for undo
        if event.char in [' ', '\t', '\n']:
            self.history.stackify()


    def _bind_keys(self) -> None:
        ''' Some keys need specific bindings to behave how you expect in a text editor '''
        self.text.bind("<KP_Enter>", lambda event: self.editor.add_newline())

    def _make_text_area(self) -> None:
        ''' Create a new textbox and add it to the notebook '''
        self.toolbar.grid(row=0, column=0, pady=(3,5), sticky='nsew')
        self.text.grid(row=1, column=0, sticky='nsew')
        self.text.mark_unset("insert")
        self.text.mark_set("insert", "1.0")
        self.text.focus_set()


    def update_selection(self, event):
        if self.text.tag_ranges(SEL):
            self.current_selection_text = self.selection_get()
        else:
            self.current_selection_text = ""
        # self.footer.update_selection_stats(self.current_selection_text)

