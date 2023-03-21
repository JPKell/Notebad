from collections import deque
from tkinter import Text, Canvas, IntVar
from tkinter.ttk import Notebook, Scrollbar, Frame

from conf import cf
from .colors import Themes

class Textbox(Text):
    ''' This is where the magic happens. This is the text area where the user 
        is typing. This class is responsible for the text area, line numbers, 
        and scrollbars. Syntax highlighting is a beast of it's own and is 
        separated into it's own module. '''
    def __init__(self, tabs:Notebook) -> None:
        # Line number updates is a whole thing. It uses a proxy and if we are 
        # doing mass updates we want to be able to turn that off. 
        self.disable_line_no_update = False
        # tabs is the parent widget
        self.tabs = tabs
        self.font = tabs.view.ui.font
        self.font_size = 0  # This allows different font sizes between windows
        # This frame houses the text area, line numbers and scrollbars
        self.frame = Frame(tabs)
        # Initialize the text area
        super().__init__(self.frame, undo=False, border=0, relief='flat', wrap='none') 
        # Instantiate the line numbers
        self.line_nos_drawn = 0
        self._make_line_numbers()
        # Instantiate the scrollbar
        self._make_scrollbars()
        # Handle special keybindings
        self._bind_keys()

        # File settings
        self.full_path = ""
        self.file_path  = ""
        self._file_name = cf.new_file_name
        self.tk_name    = ""
        self.changed_since_saved = False

        # Stack for undo/redo
        self.undo_stack = deque(maxlen = cf.max_undo)
        self.redo_stack = deque(maxlen = cf.max_undo)

        # Text area settings
        self._make_text_area(tabs) 
        
        # This is currently the primary way to check if the line numbers
        # need to be redrawn. This may need to be changed when the language server 
        # is updated (created).  
        self.bind('<Key>', lambda event: self.check_on_key(event))  

        # Syntax highlighting. Until this is a little more stable I don't want 
        # it to be the default
        if cf.enable_syntax_highlighting: 
            ...
            # self._setup_syntax_highlighting()

    ###              ###
    # Class properties #
    ###              ###

    @property
    def is_blank(self) -> bool:
        ''' Returns True if the text area has not had a single character entered. 
            By default a text area will house a new line character. So len is not
            a good way to check if the text area is blank.
        '''
        return self.get(1.0, 'end') == '\n'
    
    @property
    def file_name(self) -> str:
        return self._file_name
    
    @file_name.setter
    def file_name(self, file_name:str) -> None:
        ''' Updating the filename will also update the tab name '''
        self._file_name = file_name
        self.tabs.tab(self.tk_name, text=file_name)

    ###                        ###
    # Underlying file operations #
    ###                        ###

    def set_full_path(self, full_path:str) -> None:
        ''' Sets the path of the file and splits the path apart for different uses '''
        full_path = full_path.split('/')
        file_name = full_path.pop()
        file_path = ''

    def set_meta(self, file_path:str=None, file_name:str=None, full_path:str=None, tk_name:str=None) -> None:
        ''' Set various pieces of meta data. The tk name is the name of the tab in 
            tkinter land '''
        self.tk_name = tk_name      if tk_name   else self.tk_name
        self.file_path = file_path  if file_path else self.file_path
        self.file_name = file_name  if file_name else self.file_name
        self.full_path = full_path  if full_path else self.full_path

    ###              ###  
    # Get and set text #
    ###              ###

    def get_current_line_text(self) -> str:
        ''' Return the text of the current line including the newline character '''
        return self.get('insert linestart', 'insert lineend')
    
    def get_previous_line(self) -> str:
        ''' Return the text of the previous line including the newline character '''
        return self.get('insert -1l linestart', 'insert -1l lineend')
    
    def get_trailing_word_and_index(self) -> tuple:
        ''' Return the word the cursor is currently on or just ahead of. 
            This is great for syntax highlighting since we can return the
            word before a space and handle it. 

            This can get language specific because ABL can have a hypen in the word or 
            a number of other things.
        '''
        cur_index = self.index('insert')
        # If we are at the start of a line dont try to get the word. 
        if cur_index[-2:] == '.0':
            return '', (cur_index, cur_index)
        
        ln,col = cur_index.split('.')
        offset = 1
        if int(col) < 3:
            word = self.get(f'{ln}.0', 'insert')
        else:
            word = self.get(f'insert -{offset}c wordstart', 'insert')
        print(word)
        # If the word is a space we are past the end of the word and need to move
        # back one more character.
        if word == ' ':
            offset = 2
            word = self.get(f'insert -{offset}c wordstart', 'insert')

        if word == '  ': # Double space, lets assume we dont want that word
            return '', (cur_index, cur_index)

        # There is an annoying trait of tkinter where if you are at the start 
        # of the line and the line above is empty, the index will be at the 
        # start of the line above. So we need to check for this. 
        # Perhaps there is a better way. 
        idx = self.index(f'insert -{offset}c wordstart')
        idx = idx.split('.')
        cur_index = cur_index.split('.')
        start_index = f"{cur_index[0]}.{idx[1]}"
        
        # The offset here is to try to make up for 
        index = (start_index, self.index(f'insert -{offset - 1}c'))  # Might need to adjust the end index. 
        return word, index

    def get_selection(self) -> str:
        ''' Return the text selected in the textbox '''
        # Throws an error if there is no selection so we look for the tag first
        if self.tag_ranges('sel') == (): 
            return ""
        else:
            return self.get('sel.first', 'sel.last')
        
    def add_newline(self) -> None:
        ''' There are times we need to add a new line. For instance the 
            Enter key on the numberpad does not create a new line. '''
        self.insert('insert', '\n')
        # Have the window scroll to the new line
        self.see('insert')

    def clear_all(self):
        ''' Clears all text in the textbox '''
        self.delete("1.0", "end")

    def delete_cur_line(self) -> None:
        ''' Delete the current line '''
        self.delete('insert linestart', 'insert lineend') 

    def get_all(self) -> str:
        ''' Returns all text in the textbox '''
        return self.get("1.0", "end - 1c")

    ###                        ### 
    # Text selections and cursor #
    ###                        ###

    def delete_selection(self):
        self.delete('sel.first', 'sel.last')

    def has_selection(self) -> bool:
        ''' Returns True if there is text selected '''
        return self.tag_ranges('sel') != ()

    def select_all(self) -> None:
        ''' Select all text in the textbox '''
        self.tag_add('sel', 1.0, 'end')


    ###           ###
    # Undo and redo #
    ###           ###

    # I bypass the tkinter undo/redo because this gives more control. 
    # It may be memory inefficient and it might be better to use marks 
    # in the future take a look once the language server is running. 

    def stackify(self):
        self.undo_stack.append(self.get("1.0", "end - 1c"))
 
    def undo(self):
        try:
            cur_txt = self.get("1.0", "end - 1c")
            self.redo_stack.append(cur_txt)
            txt = self.undo_stack.pop()
            self.clear_all()
            self.insert("0.0", txt)
        except IndexError:
            self.tabs.view.footer.set_status("Nothing to undo")

    def redo(self):
        try:
            txt = self.redo_stack.pop()
            self.undo_stack.append(txt)
            self.clear_all()
            self.insert("0.0", txt)
        except IndexError:
            self.tabs.view.footer.set_status("Nothing to redo")

    ####################
    ## Event handlers ##
    ####################

    def check_on_key(self, event) -> None:
        ''' This is the function that runs upon every keypress. If there is a
            way to do any of these outside of checking every keystroke that's 
            a better option. The functions called from here tend to be blocking
            and will cause user input to be delayed. 
        
            Event state 16 is when no modifier keys are pressed. It will not 
            fire when shift and an alphanumeric key is pressed.'''
        
        # Check if the document has been updated since last saved
        if not self.changed_since_saved and event.state == 16:
            self.changed_since_saved = True
            self.tabs.set_properties(self.tk_name, text=f'{self.file_name} *')

        # Put a delay on this so the cursor has a chance to move with the character
        # placed on the screen before we update the position. 
        self.after(10, self.tabs.view.footer.update_pos)

        # Pushes the current state of the document onto the stack for undo
        if event.char in [' ', '\t', '\n']:
            self.stackify()


    def _bind_keys(self) -> None:
        ''' Some keys need specific bindings to behave how you expect in a text editor '''
        self.bind("<KP_Enter>", lambda event: self.add_newline())

    ## Scrollbar events ##
    def hide_unused_scrollbars(self) -> None:
        ''' This checks the scrollbars to see if they are needed. 
            Currently the vertical scrollbar is always visible and
            the horizontal scrollbar is only visible when needed.

            The vertical scrollbar could be hidden but it needs more logic
            to work well with opening files that are longer than the window.
        '''
        hori_bar = self.horiz_scroll.get()

        if hori_bar[0] == 0 and hori_bar[1] == 1 :
            if self.horiz_scroll_visible == True:
                self.horiz_scroll_visible = False
                self.horiz_scroll.pack_forget()
        else:
            if self.horiz_scroll_visible == False:
                self.horiz_scroll_visible == True
                self.horiz_scroll.pack(expand=True, side='right', fill='x')

    def _on_change(self, event):
        self.linenumbers.redraw()

    ###                 ###
    # Constructor helpers #
    ###                 ###

    def _make_text_area(self, tabs:Notebook) -> None:
        ''' Create a new textbox and add it to the notebook '''
        if tabs.view.ui.theme == 'dark':
            colors = Themes.dark
        else:
            colors = Themes.light
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
        self.mark_unset("insert")
        self.mark_set("insert", "1.0")
        self.focus_set()

    def _make_line_numbers(self) -> None:
        ''' Add line numbers Canvas to the text area '''
        linenumbers = TextLineNumbers(self.frame, width=cf.line_number_width)
        linenumbers.attach(self)
        linenumbers.pack(side="left", fill="y")
        self.linenumbers = linenumbers
        self.bind("<<Change>>", self._on_change)
        self.bind("<Configure>", self._on_change)

        # create a proxy for the underlying widget
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
            print(args)
            print(e)
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


    ### Scrollbars ###
    def _make_scrollbars(self) -> None:
        ''' Add vertical and horizontal scrollbars to the text area '''
        # Add scrollbars to text area
        self.vert_scroll=Scrollbar(self.frame, orient='vertical')
        self.vert_scroll.pack(side='right', fill='y')
        self.vert_scroll.config(command=self._scroll_both)
        self.vert_scroll_visible = False
        self.horiz_scroll=Scrollbar(self.frame, orient='horizontal')
        self.horiz_scroll.config(command=self.xview)
        self.horiz_scroll_visible = False

        # The scrollbars require a connection both ways. So changes to one will
        # be reflected in the other.

        # Connect the scrollbars to the text area
        self.configure(
            xscrollcommand=self.horiz_scroll.set, 
            yscrollcommand=self._update_scroll
            )
        # Connect the text area to the scrollbars

    def _scroll_both(self, action, position, type=None):
        self.yview_moveto(position)
        self.linenumbers.yview_moveto(position)

    def _update_scroll(self, first, last, type=None):
        self.yview_moveto(first)
        self.linenumbers.yview_moveto(first)
        self.vert_scroll.set(first, last)



    # def _setup_syntax_highlighting(self) -> None:
    #     ''' This creates a proxy method for the text widget that will 
    #         intercept any events and call the syntax highlighter. 
    #         I would like to get rid of the proxy because it does not play well 
    #         with try catch blocks. Something will get caught in the proxy and
    #         fail in the original. 
    #     '''
    #     self.syntax = SyntaxMarker(self)



class TextLineNumbers(Canvas):
    ''' Line numbers for the edge of a textbox. These are drawn on a canvas 
        and are updated when the window is changed. ''' 
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args,**kwargs)
        self.textwidget = None
        self.color = 'grey'
        

    def attach(self, text_widget: Textbox) -> None:
        ''' Attach the line numbers to a textbox to retrive line info. '''
        self.textwidget = text_widget
        self.redraw() # Kick it off once attached to a widget

    def redraw(self, *args) -> None:
        ''' Redraw the line numbers on the canvas '''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        # Enter the endless loop
        while True:
            # Get the line dimensions in tuple (x,y,width,height,baseline)
            dline= self.textwidget.dlineinfo(i)
            # Leave the loop if the line is empty
            if dline is None: 
                break
            # Get the y coordinate of the line
            y = dline[1] + 1
            # Get the line number
            linenum = str(i).split(".")[0]
            # Set the font size
            size = 10
            # 10,000+ lines should be small. Or make the canvas bigger. I like font smaller. 
            if len(linenum) > 4:
                size = 7
            self.create_text(
                2,                      # x coordinate of the text. 
                y,
                anchor="nw", 
                text=linenum,           
                font=('arial',size), 
                tags='lineno',          # Let us get the line numbers later
                fill=self.color         
                )
            # Get the next line
            i = self.textwidget.index("%s+1line" % i)
        # self.after(50, self.redraw)