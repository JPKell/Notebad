
from settings import Configuration

from modules.logging import Log
from view.colors  import Themes
from view.tabs    import Tabs
from view.ui      import UI

from view.key_commands import KeyCommandList
from view.settings_menu import SettingsDialog
from widgets import NFrame

cfg = Configuration()
logger = Log(__name__)

class NoteView(NFrame):
    ''' The noteview class handles the look and feel of the application
        Generally the view should not be reliant on the controller, but there 
        are applications for it since the menu is very much a look and feel
        thing, but needs to be able to call controller functions.

        Items in the heirarchy should mainly handle themselves and child
        widgets. The main business logic and data handling should be in the
        model. The controller should be the glue between the two and orchestrate
        the flow of data and the logic of the application.
    '''
    def __init__(self, controller) -> None:
        logger.debug("View begin init")
        super().__init__(controller.app) # This class is a frame that live right inside the main window
        self.controller = controller    
        self.app        = controller.app     # The main window
        self.theme      = ''       
        self._make()

        logger.debug("View finish init")

    def _make(self) -> None:
        ''' The meat of the view, this is where we create the widgets '''
        self.ui      = UI(self)
        self.tabs    = Tabs(self)
    
        # OG tkinter widgets need themes reloaded on first build
        self.ui.toggle_theme(reload=True)
        self.pack(fill='both', expand=True)
        # self.cur_tab.focus_set()    # Make sure we can start typing right away
        # self.textbox.footer.update_cursor_pos()    # Update the footer position data
        self.settings_window = None   # Assign to SettingsDialog object when the toplevel is needed

    ## Class properties ##
    @property
    def cur_tab(self):           # So common it needs to be a property in view
        return self.tabs.cur_tab

    def key_command_list(self):
        KeyCommandList(self)


    ## Window functions ##
    def tab_change(self, text:str=None) -> None:
        ''' Update the title of the window. Will default to Notebad - filename
            unless text is passed in. '''
        self.tabs.set_tabs_unfocused()

        textbox = self.cur_tab
        textbox.is_focus = True

        # This is a shitty fix. The issue is if we add new tabs other than textboxes
        # they will needs to match certain attributes. This is a quick fix for now
        # but should be reworked in the near future
        try:
            self.app.title(f"{cfg.app_title} - {textbox.meta.file_name}")
            # textbox.footer.lang_lbl.config(text=textbox.meta.language)
            self.controller.load_language(textbox.meta.language)

            logger.debug(f"Tab changed to {textbox.meta.file_name}")
        except:
            self.app.title(f"{cfg.app_title} - Profiler")
            logger.debug(f"Tab changed to profiler")

    def open_settings_window(self, *args):
        SettingsDialog(self)
