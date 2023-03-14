from tkinter import PhotoImage
from tkinter.ttk import Notebook

from .textbox import Textbox
from conf import cf


class Tabs(Notebook):
    ''' The tabbed interface for the app '''
    def __init__(self, view) -> None:
        super().__init__(view)
        self.view = view
        self.pack(expand=True, fill='both')
        self.bind('<ButtonPress-1>',   lambda event: self.on_close_press(event), True)
        self.bind('<ButtonRelease-1>', lambda event: self.on_close_release(event))
        self.active_hover = None
        self.new_tab()
        
           
    @property
    def textbox(self) -> Textbox:
        ''' Returns the current tab '''
        frm = self.nametowidget(self.select())
        return frm.winfo_children()[0]
        

    def new_tab(self, file_name:str=None) -> None:
        ''' Opens a new tab with the filename as the tab name.
        If no filename is given, the tab will be named the default name.
        '''
        textbox = Textbox(self)
        if file_name:
            textbox.file_name = file_name
        self.add(textbox.frame, text=textbox.file_name)
        self.move_to_tab()
        textbox.tk_name = self.select()
        
    ## Handle tab closing ##
    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""

        # Find the element under the pointer
        element = self.identify(event.x, event.y)
        # The element is what we created in the style
        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self.active_hover = index
            return "break"

    def on_close_release(self, event):
        """Called when the button is released"""
        if not self.instate(['pressed']):
            return

        element =  self.identify(event.x, event.y)
        if "close" not in element:
            # user moved the mouse off of the close button
            return

        index = self.index("@%d,%d" % (event.x, event.y))

        if self.active_hover == index:
            self.close_tab(index)

        self.state(["!pressed"])
        self.active_hover = None

    def close_tab(self, tab_name:str=None) -> None:
        ''' Closes a tab by name. If no name is given, the current tab is closed. '''
        if not tab_name:
            tab_name = self.select()
        
        if self.textbox.changed_since_saved and not cf.hardcore_mode:
            self.view.prompt_yes_no("Whoa, there...", "There are changes not yet saved. Save before you giddy on off??", self.view.controller.save_file)

        self.forget(tab_name)
        self.event_generate("<<NotebookTabClosed>>")

        if len(self.tabs()) == 0:
            self.new_tab()
    
    def move_to_tab(self, tab_name:str=None) -> None:
        ''' Selects a tab by name. tabs.select() defaults to the last created tab '''
        if not tab_name:
            tabs = self.tabs()
            tab_name = tabs[-1]
        self.select(tab_name)
    
    def set_properties(self, tab_name:str, **kwargs) -> None:
        ''' Set properties of a tab '''
        self.tab(tab_name, **kwargs)

    def add_indent(self) -> None:
        ''' Adds an indent to the textbox '''
        #Get the current cursor position
        cursor_pos = self.textbox.index('insert')
        x_pos = int(cursor_pos.split('.')[1])
        # Adjust the cursor position to the nearest indent
        x_pos = x_pos % cf.indent_size
        self.textbox.insert('insert', ' ' * (cf.indent_size - x_pos))
        return 'break'
    
    ## Simple abstractions ## 
    def cur_tab_tk_name(self) -> str:
        ''' Returns the name of the current tab '''
        return self.select()