from tkinter.ttk import Notebook

from .textbox import Textbox

from modules.logging import Log

logger = Log(__name__)

class Tabs(Notebook):
    ''' The tabbed interface for the app '''
    def __init__(self, view) -> None:
        logger.debug("Tabs begin init")
        super().__init__(view)
        self.view = view
        self.conf = view.conf
        self.pack(expand=True, fill='both')
        self.bind('<ButtonPress-1>',   lambda event: self.on_close_press(event), True)
        self.bind('<ButtonRelease-1>', lambda event: self.on_close_release(event))
        self.active_hover = None
        self.new_tab()
        logger.debug("Tabs finish init")  
           
    @property
    def textbox(self) -> Textbox:
        ''' Returns the current tab '''
        frm = self.nametowidget(self.select())
        return frm.winfo_children()[0]
        
    def new_tab(self, file_name:str=None) -> None:
        ''' Opens a new tab with the filename as the tab name.
        If no filename is given, the tab will be named the default name.
        '''
        logger.debug(f"New tab requested: {file_name=}")

        # Set up a new textbox and add it to the tabs
        self.set_textboxes_unfocused()
        textbox = Textbox(self)  
        self.add(textbox.frame, text=textbox.meta.file_name)
        self.move_to_tab()

        # Set the meta data for the textbox
        textbox.meta.tk_name = self.select()
        textbox.meta.language = 'text'
        if file_name:
            textbox.meta.set_meta(file_name=file_name)

        logger.debug(f"New tab created: {textbox.meta.file_name}")
        
        
    def on_close_press(self, event) -> None:
        """ Called when the button is pressed over the close button 
            of a tab. returns 'break' to stop the event from propagating """
        # Find the element under the pointer
        element = self.identify(event.x, event.y)

        # The element is what we created in the style
        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self.active_hover = index
            return "break"

    def on_close_release(self, event) -> None:
        """Called when the button is released"""
        if not self.instate(['pressed']):
            return

        # element name of whats under the mouse
        element =  self.identify(event.x, event.y)
        if "close" not in element:
            # user moved the mouse off of the close button
            return

        # Match the tab index to the active hover index from on close press
        index = self.index("@%d,%d" % (event.x, event.y))
        if self.active_hover == index:
            self.close_tab(index)

        # Reset the button state if not closed
        self.state(["!pressed"])
        self.active_hover = None

    def close_tab(self, tab_name:str=None) -> None:
        ''' Closes a tab by name. If no name is given, the current tab is closed. '''
        if not tab_name:
            tab_name = self.select()
        
        if self.textbox.meta.changed_since_saved and not self.conf.hardcore_mode:
            self.view.prompt_yes_no("Whoa, there...", "There are changes not yet saved. Save before you giddy on off??", self.view.controller.save_file)

        # Remove tab from the notebook
        self.forget(tab_name)
        self.event_generate("<<NotebookTabClosed>>")

        logger.debug(f"Tab closed: {tab_name}")

        # If there are no tabs left, create a new one
        if len(self.tabs()) == 0:
            self.new_tab()
    
    def move_to_tab(self, tab_name:str=None) -> None:
        ''' Selects a tab by name. tabs.select() defaults to the last created tab '''
        if not tab_name:
            tabs = self.tabs()     # returns a list of tab names 
            tab_name = tabs[-1]    # get the last tab name
        self.set_textboxes_unfocused()
        self.select(tab_name)
        logger.debug(f"Tab moved to: {tab_name}")

    def set_textboxes_unfocused(self) -> None:
        ''' Sets all textboxes to unfocused. This focus flag should be used 
            to maintain activity in only one textbox.'''
        _tabs = self.tabs()
        for _tab in _tabs:
            frm = self.nametowidget(_tab)
            textbox = frm.winfo_children()[0]
            textbox.is_focus = False
        logger.verbose("All textboxes unfocused")

    def set_properties(self, tab_name:str, **kwargs) -> None:
        ''' Set properties of a tab '''
        self.tab(tab_name, **kwargs)
        logger.debug(f"Tab properties set: {tab_name}")
    
    def cur_tab_tk_name(self) -> str:
        ''' Returns the name of the current tab '''
        return self.select()