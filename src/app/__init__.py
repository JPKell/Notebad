import pathlib, os
import tkinter as tk
from tkinter import Tk

from app.file_management import FileManagement
from app.key_bindings    import KeyBindings
from app.language_tools  import LanguageTools
from app.utilities       import Utilities    

from modules.parsers  import progress_profiler
from modules.parsers  import includes_expander
from view  import NotebadView
from widgets import prompt_yes_no

from settings  import Configuration
from modules.logging import Log

cfg = Configuration()
logger = Log(__name__)

class NotebadApp(Tk):
    ''' The controller is the glue between the model and the view. It is the
        controller that binds the view to the model. The controller is also
        responsible for managing the application. '''

    def __init__(self):
        logger.info('Notebad AB-LM IDE Initializing...')
        logger.debug('Controller begin init')

        # Set up the root frame
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.exit_app)

        # Instantiate the view
        self.view        = NotebadView(self) # View is instantiated here, passing the controller into the view

        # Order is important 
        self.file_system = FileManagement(self, self.view)     
        self.language    = LanguageTools(self, self.view) # Language tools are instantiated here, passing the controller into the language tools
        self.utilities   = Utilities(self, self.view) # Utilities are instantiated here, passing the controller into the utilities
        # Feed the view to the modules who need it

        # NoteController.view = self.view # This is a hack to get the view into the textbox class
        self.key_bindings = KeyBindings(self, self.view) 
        
        self.events_master()
        
        # This might be better done as a function on its own. 
        # At that point, maybe we stash the open tabs at close and reopen them 
        if cfg.preload_file:
            textbox = self.view.cur_tab         
            self.file_system.write_file_to_textbox(ide=textbox, full_path=cfg.preload_file)
            textbox.full_path=cfg.preload_file

        logger.debug('Controller finish init')

    ###
    # Application management
    ###
    def events_master(self) -> None:
        ''' Events are things that happen in the application. '''
        self.events = {
        # Profiler events
        '<<ProfilerFileChanged>>': self.parse_progress_profiler,
        '<<ProfilerSourceView>>':  self.build_profiler_source,
        # Window events
        '<<OpenKeyCommandList>>':  self.populate_key_commands,
        '<<OpenCalculator>>':      self.utilities.open_calculator,
        '<<ExitApp>>':             self.exit_app,
        # File management events
        '<<NewFile>>':             self.file_system.new_file,
        '<<OpenFile>>':            self.file_system.open_file,
        '<<OpenRecentFile>>':      self.file_system.open_recent_file,
        '<<SaveFile>>':            self.file_system.save_file,
        '<<SaveFileAs>>':          self.file_system.save_file_as,
        # Language events

        # Nifty
        '<<PyEvalLine>>':         self.utilities.eval_selection,  
        }
        for k,v in self.events.items():
            self.bind_all(k, v)

    def exit_app(self) -> None:
        ''' Exit the application. Optional hardcore mode will disable the prompt.
            This is useful for testing. To quote the devs at Bethseda, 
                "Save often, the plains of Oblivion are a dangerous place." 
        ''' 
        tab_list = self.view.tabs.tabs()
        if not cfg.hardcore_mode:
            for tab in tab_list:
                self.view.tabs.select(tab)
                if self.view.cur_tab.tab_save_on_close:
                    prompt_yes_no(
                        "You have unsaved changes", 
                        f"Save {self.view.cur_tab.file_name}?", 
                        self.file_system.save_file)
        self.view.master.destroy()
        logger.debug('Application closed')

    def run(self) -> None:
        ''' Start 'er up! Run is called from outside the controller allowing for 
            everything to be set up first. '''
        logger.debug('Starting the main loop')

        # Todo update this to work in linux too. See tkinter python epub for code.
        if cfg.start_fullscreen:
            self.state("zoomed")
        self.mainloop()

    ###
    # Function routing
    ### 

    ### Profiler ###
    def build_profiler_source(self, event) -> str:
        ''' Build the text to be parsed. '''
        profiler = event.widget
        if cfg.project_src:
            results = includes_expander.expand_includes(profiler.tree.current_line())
            profiler.text.delete('1.0', tk.END)
            profiler.text.insert(tk.END, ''.join(results))

    def parse_progress_profiler(self, event) -> None:
        ''' Parse the progress profiler output file. '''
        profiler = event.widget
        filename = profiler.filename.get()
        parser_data = progress_profiler.parse_profiler_data(filename)
        profiler.load_profiler_data(parser_data)

    ### Language ###
    def load_language(self, language:str) -> None:
        ''' Update the language of the current textbox. '''
        self.language.load_language(language)

    ### Key command window
    def populate_key_commands(self, event) -> None:
        ''' Populate the key commands list. '''
        data = self.key_bindings.binder
        event.widget.list_key_commands(data)




