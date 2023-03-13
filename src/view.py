from   tkinter import messagebox, filedialog, Frame

from conf          import cf
from views.colors  import Themes
from views.footer  import Footer
from views.menu    import Menubar
from views.tabs    import Tabs
from views.ui      import UI


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
        super().__init__(controller.app) # This class is a frame that live right inside the main window
        self.controller = controller    
        self.app = controller.app        # The main window
        self._make()

    def _make(self) -> None:
        ''' The meat of the view, this is where we create the widgets '''
        self.ui     = UI(self)
        self.menu   = Menubar(self, self.controller)
        self.tabs   = Tabs(self)
        self.footer = Footer(self)
        # OG tkinter widgets need themes reloaded on first build
        self.ui.toggle_theme(reload=True)
        self.pack(fill='both', expand=True)
        self.textbox.focus_set()    # Make sure we can start typing right away  

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
    def update_title(self, text:str=None) -> None:
        ''' Update the title of the window. Will defualt to Notebad - filename 
            unless text is passed in. '''
        self.app.title(f"{cf.app_title} - {self.textbox.file_name}")
