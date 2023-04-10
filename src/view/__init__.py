from modules.logging import Log
from settings import Configuration

from widgets import NFrame
from .key_commands  import KeyCommandList
from .menu          import Menubar
from .settings_menu import SettingsDialog
from .tabs          import Tabs
from .ui            import UI


cfg = Configuration()
logger = Log(__name__)

class NotebadView(NFrame):
    ''' The noteview class is a launching point for the UI. It initializes
        the UI and the tabs. The tabs are the main container for the content
        of the application. 

        Additional panes and gutters can be added here, and new windows can 
        be created here or in the controller.

        Generally the view should not be reliant on the controller and communicate 
        via events. An event generated in the view carries with it a copy of the
        widget that generated the event. This is how the view passes data to the 
        controller.

        Items in the heirarchy should mainly handle themselves and child
        widgets. The main business logic and data handling should be in the
        model. The controller should be the glue between the two and orchestrate
        the flow of data and the logic of the application.
    '''
    def __init__(self, parent) -> None:
        logger.debug("View begin init")

        # Set up the root frame
        super().__init__(parent) 

        # Build the app frame
        self._build_objects(parent)
        self._setup_and_grid()

        logger.debug("View finish init")


    ## Class properties ##
    @property
    def cur_tab(self):           # So common it needs to be a property in view
        return self.tabs.cur_tab

    def key_command_list(self):
        KeyCommandList(self)

    def open_settings_window(self, *args):
        SettingsDialog(self)

    ###
    # Private methods
    ###

    def _build_objects(self, root) -> None:
        ''' The meat of the view, this is where we create the widgets '''
        self.ui       = UI(self, root)
        self.tabs     = Tabs(self)
        self.menu     = Menubar(root, view=self, tabs=self.tabs, ui=self.ui)
        self.l_gutter = NFrame(self)
        self.r_gutter = NFrame(self)

    def _setup_and_grid(self) -> None:
        ''' This is where we set up the widgets and grid them '''
        # OG tkinter widgets need themes reloaded on first build
        self.ui.toggle_theme(reload=True)

        # Set up weights. This will have to change when we add content to the gutters
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Grid everything
        self.grid(row=0, column=0, sticky='nsew')
        self.l_gutter.grid(row=0, column=0, sticky='nsew')
        self.r_gutter.grid(row=0, column=2, sticky='nsew')

        self.tabs.grid(row=0, column=1, padx=2, pady=(0,2), sticky='nsew')
