import pathlib, os
import tkinter as tk

from controller.file_management import FileManagement
from controller.key_bindings    import KeyBindings
from controller.translate        import LanguageTools
from controller.menu            import Menubar
from controller.utilities       import Utilities    

from view  import NoteView

from settings  import Configuration
from modules.logging import Log

cfg = Configuration()
logger = Log(__name__)

class NoteController:
    ''' The controller is the glue between the model and the view. It is the
        controller that binds the view to the model. The controller is also
        responsible for managing the application. '''
    
    view = None

    def __init__(self):
        logger.info('Notebad AB-LM IDE Initializing...')
        logger.debug('Controller begin init')

        # Instantiate controller objects
        # Root window
        self.app       = tk.Tk()
        self.file_system = FileManagement(self)     
        self.menu      = Menubar(self.app, controller=self)   
        # Instantiate the view
        self.view      = NoteView(self) # View is instantiated here, passing the controller into the view
        # Order is important 
        self.language  = LanguageTools(self, self.view) # Language tools are instantiated here, passing the controller into the language tools
        self.utilities = Utilities(self, self.view) # Utilities are instantiated here, passing the controller into the utilities
        # Feed the view to the modules who need it
        self.menu.set_view(self.view)
        NoteController.view = self.view # This is a hack to get the view into the textbox class
        
        self.key_bindings = KeyBindings(self) 
        self._app_protocols()

        # This might be better done as a function on its own. 
        # At that point, maybe we stash the open tabs at close and reopen them 
        if cfg.preload_file:
            textbox = self.view.textbox         
            self.file_system.write_file_to_textbox(textbox, cfg.preload_file)
            path_parts = self.file_system.parts_from_file_path(cfg.preload_file)
            textbox.meta.set_meta(tk_name=self.view.tabs.cur_tab_tk_name(),
                        full_path=cfg.preload_file,
                        file_path=path_parts['path'], 
                        file_name=path_parts['file'], )
        logger.debug('Controller finish init')

    def _app_protocols(self) -> None:
        ''' Application protocols deal with system commands such as closing the window. '''
        self.app.protocol("WM_DELETE_WINDOW", self.exit_app)

    def relative_to_abs_path(self, rel_path:str) -> str:
        ''' Returns the absolute path of a relative path. '''
        return os.path.join(cfg.current_dir, rel_path) 

    def run(self) -> None:
        ''' Start 'er up! Run is called from outside the controller allowing for 
            everything to be set up first. '''
        logger.debug('Starting the main loop')
        if cfg.start_fullscreen:
            self.app.state("zoomed")
        self.app.mainloop()

    def exit_app(self) -> None:
        ''' Exit the application. Optional hardcore mode will disable the prompt.
            This is useful for testing. To quote the devs at Bethseda, 
                "Save often, the plains of Oblivion are a dangerous place." 
        ''' 
        tab_list = self.view.tabs.tabs()
        if not cfg.hardcore_mode:
            for tab in tab_list:
                self.view.tabs.select(tab)
                if self.view.textbox.meta.changed_since_saved:
                    self.view.prompt_yes_no(
                        "You have unsaved changes", 
                        f"Save {self.view.textbox.meta.file_name}?", 
                        self.file_system.save_file)
        self.view.master.destroy()
        logger.debug('Application closed')

    def load_language(self, language:str) -> None:
        ''' Update the language of the current textbox. '''
        self.language.load_language(language)
