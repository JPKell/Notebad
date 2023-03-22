from tkinter     import Text, font
from tkinter.ttk import Notebook, Frame

from view.colors import Themes
from view.textbox.clipboard import Clipboard
from view.textbox.cursor    import Cursor
from view.textbox.edit      import Editor
from view.textbox.footer    import Footer
from view.textbox.line_numbers import LineNumbers
from view.textbox.meta       import Meta
from view.textbox.scrollbars import Scrollbars
from view.textbox.undo_stack import History
from modules.logging         import Log

logger = Log(__name__)

class Textbox(Text):
    ''' This is where the magic happens. This is the text area where the user 
        is typing. This class is responsible for the text area, line numbers, 
        and scrollbars. Syntax highlighting is a beast of it's own and is 
        separated into it's own module. '''

    def __init__(self, tabs:Notebook) -> None:
        logger.debug("Textbox begin init")
        self.conf = tabs.conf

        # If the area is in focus we want to be active. When inactive, things
        # on the event loop should be turned off.
        self._is_focus = False

        # Line number updates is a whole thing. It uses a proxy and if we are 
        # doing mass updates we want to be able to turn that off. 
        self.disable_line_no_update = False

        # tabs is the parent widget
        self.tabs = tabs

        # This frame houses the text area, line numbers, scrollbars, and footer
        self.frame = Frame(tabs, padding=0, border=0, relief='flat')

        # Initialize the text area
        super().__init__(self.frame, undo=False, border=0, relief='flat', wrap='none', padx=0, pady=0) 
        
        # Build all the objects associated with the text area
        self.footer = Footer(self.frame, self.tabs.view)
        self.meta   = Meta(self, self.tabs)
        self.linenumbers = LineNumbers(textbox=self)
        self.scrollbars  = Scrollbars(self)
        self.history   = History(self, self.footer)
        self.clipboard = Clipboard(self)
        self.editor    = Editor(self)
        self.cusor     = Cursor(self)

        # Instantiate the line numbers
        self._init_line_numbers()

        # Handle special keybindings
        self._bind_keys()


        # Text area settings
        self._make_text_area(tabs) 
        
        # This is currently the primary way to check if the line numbers
        # need to be redrawn. This may need to be changed when the language server 
        # is updated (created).  
        self.bind('<Key>', lambda event: self.check_on_key(event))  
       
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
        if is_focus:
            self.scrollbars.hide_unused()
            self.footer.update_pos()
        
    @property
    def is_blank(self) -> bool:
        ''' Returns True if the text area has not had a single character entered. 
            By default a text area will house a new line character. So len is not
            a good way to check if the text area is blank.
        '''
        return self.get(1.0, 'end') == '\n'


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
            self.tabs.set_properties(self.meta.tk_name, text=f'{self.meta.file_name} *')
            return

        # Pushes the current state of the document onto the stack for undo
        if event.char in [' ', '\t', '\n']:
            self.history.stackify()


    def _bind_keys(self) -> None:
        ''' Some keys need specific bindings to behave how you expect in a text editor '''
        self.bind("<KP_Enter>", lambda event: self.add_newline())

    def _make_text_area(self, tabs:Notebook) -> None:
        ''' Create a new textbox and add it to the notebook '''
        if tabs.view.ui.theme == 'dark':
            colors = Themes.dark
        else:
            colors = Themes.light

        self.font = font.nametofont('TkFixedFont')
        self.font.configure(size=self.conf.font_size)
        self.font_size = 0  # This allows different font sizes between windows

        self.configure(
            background=colors.text_background,          
            foreground=colors.text_foreground,
            highlightbackground=colors.text_background, # These 2 remove the quasi borders 
            highlightcolor=colors.text_background,      # around the textbox
            insertbackground=colors.cursor, 
            font=self.font,
            padx=5, 
            pady=5)
        self.pack(expand=True, fill='both')
        tabs.add(self.frame)
            
        self.linenumbers.config(
            bg=colors.background, 
            highlightbackground=colors.background
            )
        
        self.footer.status.config(bg=colors.background, fg=colors.foreground)
        self.footer.pos_lbl.config(bg=colors.background, fg=colors.syn_orange)
        self.footer.lang_lbl.config(bg=colors.background, fg=colors.syn_yellow)
        self.footer.sel_lbl.config(bg=colors.background, fg=colors.syn_orange)

        self.mark_unset("insert")
        self.mark_set("insert", "1.0")
        self.focus_set()




    def _init_line_numbers(self) -> None:
        ''' Make the necessary bindings and set up the proxy listener '''
        # These will call the _on_change method whenever the window is resized (<Configure>)
        # or the proxy fires a <<Change>> event 
        self.bind("<<Change>>", self._on_change)
        self.bind("<Configure>", self._on_change)

        # create a proxy for the text widget to listen for changes the 
        # line numbers need to react to.
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        
    def _proxy(self, *args):
        # let the actual widget perform the requested action
        cmd = (self._orig,) + args
        
        # Would be nice to get rid of this extra try catch. Would that speed things up? 
        try:
            result = self.tk.call(cmd)
        except Exception as e:
            logger.error(f"Error in _proxy: {e}")
            logger.error(f"cmd: {cmd}")
            result = ''

        # If we are doing thousands of tasks like reformatting a whole document
        # that will add thousands of inserts and that will cause this to fire. 
        # That means the main event loop will get hammered and the app will block. 
        if self.disable_line_no_update == True:
            return result
        
        # generate an event if something was added or deleted,
        # or the cursor position changed
        if (args[0] in ("insert", "replace", "delete") or 
            args[0:3] == ("mark", "set", "insert") or
            args[0:2] == ("xview", "moveto") or
            args[0:2] == ("xview", "scroll") or
            args[0:2] == ("yview", "moveto") or
            args[0:2] == ("yview", "scroll")
        ):
            self.event_generate("<<Change>>", when="tail")

        # return what the actual widget returned
        return result   

    def _on_change(self, event) -> None:
        ''' Triggered on <<Change>>. It will update the line numbers. 
            - event: dummy argument to match the event handler signature.
        '''
        self.linenumbers.redraw()