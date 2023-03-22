from   tkinter import messagebox, filedialog, Frame

from modules.logging import Log
from view.colors  import Themes
from controller.menu    import Menubar
from view.tabs    import Tabs
from view.ui      import UI


logger = Log(__name__)

class NoteView(Frame):
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
        self.conf     = controller.conf    # The config object
        self._make()
        logger.debug("View finish init")

    def _make(self) -> None:
        ''' The meat of the view, this is where we create the widgets '''
        self.ui     = UI(self)
        
        self.tabs   = Tabs(self)
        # self.menu   = Menubar(self, self.controller)
        # OG tkinter widgets need themes reloaded on first build
        self.ui.toggle_theme(reload=True)
        self.pack(fill='both', expand=True)
        self.textbox.focus_set()    # Make sure we can start typing right away
        self.textbox.footer.update_pos()    # Update the footer position data

    ## Class properties ##
    @property
    def textbox(self):           # So common it needs to be a property in view
        return self.tabs.textbox

    ###               ###
    # User interactions #
    ###               ###
    # Here we deal with user prompts and popups

    def prompt_yes_no(self, title:str, msg:str, callback:callable) -> None:
        ''' Show a message and call a callback function when done '''
        if messagebox.askokcancel(title, msg):
            callback()

    def open_file_dialogue(self) -> str:  
        ''' Open a file dialogue and returns the path the user selected '''
        file_path = filedialog.askopenfilename()
        return file_path
    
    def save_file_dialogue(self, file_name:str=None, path:str=None) -> str:
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=file_name, initialdir=path)
        return filepath

    ## Window functions ##
    def tab_change(self, text:str=None) -> None:
        ''' Update the title of the window. Will defualt to Notebad - filename 
            unless text is passed in. '''
        self.tabs.set_textboxes_unfocused()

        textbox = self.textbox
        textbox.is_focus = True
        self.app.title(f"{self.conf.app_title} - {textbox.meta.file_name}")
        textbox.footer.lang_lbl.config(text=textbox.meta.language)
        self.controller.load_language(textbox.meta.language)

        logger.debug(f"Tab changed to {textbox.meta.file_name}")

