from tkinter import Text, INSERT, font

from settings        import Configuration
from modules.logging import Log
from view.colors     import Themes
from widgets         import NCanvas, NFrame, NVertScrollbar, NHorizScrollbar

cfg = Configuration()
logger = Log(__name__)

class NText(Text):
    ''' A text with a name. '''
    def __init__(self, parent,  border=0, relief='flat', wrap='none', padx=0, pady=0, **kwargs):
        # This is the frame that houses the text area it needs to be the parent frame for everything
        self.frame = NFrame(parent)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        # Now initialize the text area
        super().__init__(self.frame,  border=border, relief=relief, wrap=wrap, padx=padx, pady=pady, **kwargs)

        # Setup variables
        self.disable_line_no_update = False

        self.frame.bind_all('<<ThemeChanged>>', lambda event: self._set_theme())

        self._build_ui_elements()
        self._init_line_numbers()

    ###
    # Cursor methods
    ###
    def has_selection(self) -> bool:
        ''' Returns True if there is text selected '''
        return self.tag_ranges('sel') != ()

    def select_all(self) -> None:
        ''' Select all text in the textbox '''
        self.tag_add('sel', 1.0, 'end')

    def get_position(self):
        ''' Get the current input cursor position '''
        return self.index(INSERT)

    def set_position(self, new_position):
        ''' Set the current input cursor position '''
        self.mark_set('insert', new_position)

    def split_index(self, current_index='index'):
        ''' Get a selected index or the current input cursor position as a list of
            separate line and char values '''
        current_pos = self.index(current_index)
        current_pos_split = current_pos.split(".")
        return current_pos_split
        
    def delete_tags_by_name(self, name) -> None:
        ''' Clear current textbox tags by name '''
        for tag in self.tag_names():
            if tag == name:
                self.tag_remove(tag, "1.0", "end")

        # self.footer.set_status("", revert=True)

        return 'break'


    ###
    # Overridden methods
    ###

    def grid(self,row=0, column=0, sticky='nsew', **kwargs) -> None:
        ''' Override the grid method to make sure the frame is used '''
        self.frame.grid(row=row, column=column, sticky=sticky,**kwargs)
        self.linenumbers.grid(row=0, column=0, sticky='nsew')
        self.v_scroll.grid(row=0, column=2, sticky='nsew')
        self.h_scroll.grid(row=1, column=0, columnspan=2, sticky='nsew')
        super().grid(row=0, column=1, sticky='nsew')
        # Methods to kick of once the widget is ready to draw
        self._set_theme()
        self._redraw_linenumbers()
        

    ###
    # Private methods
    ###

    def _build_ui_elements(self) -> None:
        ''' Build the UI '''

        # Create the scrollbars
        self.v_scroll = NVertScrollbar(self.frame)
        self.h_scroll = NHorizScrollbar(self.frame)
        self.v_scroll_visible = True
        self.h_scroll_visible = True
        self.v_scroll.config(command=self.yview)
        self.h_scroll.config(command=self.xview)    
        self.configure(
            xscrollcommand=self.h_scroll.set, 
            yscrollcommand=self.v_scroll.set,
            )

        # Create the line numbers
        self.linenumbers = NCanvas(self.frame, width=cfg.line_number_width)


    ###
    # Line numbers
    #
    # This bit with the proxy looks confusing, but what we are doing is overriding the tk call
    # function to our own _proxy function. This allows us to intercept the calls to the text
    # widget and do something with them. In this case we are listening for changes to the text
    # and then redrawing the line numbers.
    ###

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
    
    def _redraw_linenumbers(self, *args) -> None:
        ''' Redraw the line numbers on the canvas '''
        self.linenumbers.delete("all")


        i = self.index("@0,0")
        # Enter the endless loop
        while True:
            # Get the line dimensions in tuple (x,y,width,height,baseline)
            dline = self.dlineinfo(i)
            # Leave the loop if the line is empty
            if dline is None: 
                break
            # Get the y coordinate of the line
            y = dline[1] - 2
            # Get the line number
            linenum = str(i).split(".")[0]
            # Set the font size
            size = 10 if len(linenum) < 4 else 7
            self.linenumbers.create_text(
                2,                      # x coordinate of the text. 
                y,
                anchor="nw", 
                text=linenum,           
                font=('arial',size), 
                tags='lineno',          # Let us get the line numbers later
                fill='grey'             # Replace hardcoding                
                )
            # Get the next line
            i = self.index("%s+1line" % i)
        logger.verbose("Line numbers redrawn")

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
        ''' Triggered on <<Change>>. It will update the line numbers and cursor position in status bar (footer).
            - event: dummy argument to match the event handler signature.
        '''
        self._redraw_linenumbers()

    ###
    # Looks
    ###

    def _set_theme(self) -> None:
        if cfg.theme == 'forest-dark':
            colors = Themes.dark
        else:
            colors = Themes.light

        self.font = font.Font(family=cfg.program_font)
        self.font.configure(size=cfg.font_size)
        self.font_size = 0  # This allows different font sizes between windows

        self.configure(
            background=colors.text_background,          
            foreground=colors.text_foreground,
            highlightbackground=colors.text_background, # These 2 remove the quasi borders 
            highlightcolor=colors.text_background,      # around the textbox
            insertbackground=colors.cursor, 
            font=self.font,
            blockcursor=cfg.block_cursor,
            insertontime=cfg.cursor_on_time,
            insertofftime=cfg.cursor_off_time,
            padx=5, 
            pady=5)
            
        self.linenumbers.config(
            bg=colors.background, 
            highlightbackground=colors.background
            )
        
        # self.tag_configure("find", background=cfg.find_background)
