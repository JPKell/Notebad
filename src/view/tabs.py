from modules.logging import Log
from settings   import Configuration
from widgets    import NNotebook, NTabFrame, prompt_yes_no
# Views 
from .ide       import Ide
from .profiler  import ProgressProfiler

cfg = Configuration()
logger = Log(__name__)

class Tabs(NNotebook):
    ''' The tabbed interface for the app each tab should be a NTabeFrame as it has the common 
        methods and attributes for the tabs.'''
    
    # Every tab class should superclass NTabFrame and be added to this dict
    tab_widgets = {
            'ide': Ide,
            'profiler': ProgressProfiler
        }

    def __init__(self, view) -> None:
        logger.debug("Tabs begin init")
        super().__init__(view)
        self.view = view
        self.bind('<ButtonPress-1>',   lambda event: self.on_close_press(event), True)
        self.bind('<ButtonRelease-1>', lambda event: self.on_close_release(event))
        self.active_hover = None
        self.new_tab(cfg.default_tab_style)
        logger.debug("Tabs finish init")  
           
    @property
    def cur_tab(self) -> NTabFrame:
        ''' Returns the current tab '''
        frm = self.nametowidget(self.select())
        return frm
       
    def new_tab(self, tab_style:str, *args, **kwargs) -> None:
        ''' Opens a new tab of the given style. '''
        logger.debug(f"Creating new { tab_style } tab")

        # Fail fast and hard
        if tab_style not in self.tab_widgets:
            logger.fatal(f"Unknown tab style { tab_style }")
            raise ValueError(f"Unknown tab style { tab_style }")

        self.set_tabs_unfocused()

        # Instantiate the new tab
        new_tab = self.tab_widgets[tab_style](self, *args, **kwargs)
        # Add the tab to the notebook and set the tab name
        self.add(new_tab, text=new_tab.tab_title)
        self.move_to_tab()
        # The tab can not set it's own name until it is added to the notebook and is 
        # being managed by the notebook.
        new_tab.tab_tk_name = self.select()

        logger.debug(f"New { tab_style } tab created")
        
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
        
        if self.cur_tab.tab_save_on_close and not cfg.hardcore_mode:
            prompt_yes_no("Whoa, there...", "There are changes not yet saved. Save before you giddy on off??", self._event())

        # Remove tab from the notebook
        self.forget(tab_name)
        self.event_generate("<<NotebookTabClosed>>")

        logger.debug(f"Tab closed: {tab_name}")

        # If there are no tabs left, create a new one
        if len(self.tabs()) == 0:
            self.new_tab(cfg.default_tab_style)
    
    def move_to_tab(self, tab_name:str=None) -> None:
        ''' Selects a tab by name. tabs.select() defaults to the last created tab '''
        if not tab_name:
            tabs = self.tabs()     # returns a list of tab names 
            tab_name = tabs[-1]    # get the last tab name
        self.set_tabs_unfocused()
        self.select(tab_name)
        logger.debug(f"Tab moved to: {tab_name}")

    def set_tabs_unfocused(self) -> None:
        ''' Sets all textboxes to unfocused. This focus flag should be used 
            to maintain activity in only one textbox.'''
        ...
        # _tabs = self.tabs()
        # for _tab in _tabs:
        #     frm = self.nametowidget(_tab)
        #     textbox = frm.winfo_children()[0]
        #     textbox.is_focus = False
        # logger.verbose("All textboxes unfocused")
