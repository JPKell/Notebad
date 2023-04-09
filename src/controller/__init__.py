import pathlib, os
import tkinter as tk

from controller.file_management import FileManagement
from controller.key_bindings    import KeyBindings
from controller.translate       import LanguageTools
from view.menu            import Menubar
from controller.utilities       import Utilities    

from modules.parsers  import progress_profiler
from modules.parsers  import includes_expander
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
        self.app.tk.call('source', os.path.join(cfg.theme_dir, f'forest-dark.tcl'))
        self.app.tk.call('source', os.path.join(cfg.theme_dir, f'forest-light.tcl'))
        self.app.columnconfigure(0, weight=1)
        self.app.rowconfigure(0, weight=1)
        self.app.title(cfg.app_title)  
        self.app.geometry(cfg.geometry) 
        self.app.minsize(*cfg.min_size)

        if cfg.os == 'nt': 
            self.app.iconbitmap(self.relative_to_abs_path('assets/icon.ico'))
        else:
            logo = tk.PhotoImage(file=self.relative_to_abs_path('assets/icon.gif'))
            self.app.call('wm', 'iconphoto', self.app._w, logo)

        self.file_system = FileManagement(self)     

        # Instantiate the view
        self.view      = NoteView(self.app) # View is instantiated here, passing the controller into the view
        # Order is important 
        self.language  = LanguageTools(self, self.view) # Language tools are instantiated here, passing the controller into the language tools
        self.utilities = Utilities(self, self.view) # Utilities are instantiated here, passing the controller into the utilities
        # Feed the view to the modules who need it

        # NoteController.view = self.view # This is a hack to get the view into the textbox class
        self.key_bindings = KeyBindings(self) 
        
        self.events_master()
        self._app_protocols()
        

        # This might be better done as a function on its own. 
        # At that point, maybe we stash the open tabs at close and reopen them 
        if cfg.preload_file:
            textbox = self.view.cur_tab         
            self.file_system.write_file_to_textbox(textbox, cfg.preload_file)
            path_parts = self.file_system.parts_from_file_path(cfg.preload_file)
            textbox.full_path=cfg.preload_file

        logger.debug('Controller finish init')

    def events_master(self) -> None:
        ''' Events are things that happen in the application. '''
        self.events = {
        # Profiler events
        '<<ProfilerFileChanged>>': self.parse_progress_profiler,
        '<<ProfilerSourceView>>':  self.build_text_for_parser,
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
            self.app.bind_all(k, v)


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

    def get_current_tab(self) -> None:
        ''' Get the current tab. '''
        return self.view.cur_tab

    def exit_app(self) -> None:
        ''' Exit the application. Optional hardcore mode will disable the prompt.
            This is useful for testing. To quote the devs at Bethseda, 
                "Save often, the plains of Oblivion are a dangerous place." 
        ''' 
        tab_list = self.view.tabs.tabs()
        if not cfg.hardcore_mode:
            for tab in tab_list:
                self.view.tabs.select(tab)
                if self.view.cur_tab.meta.changed_since_saved:
                    self.view.prompt_yes_no(
                        "You have unsaved changes", 
                        f"Save {self.view.cur_tab.meta.file_name}?", 
                        self.file_system.save_file)
        self.view.master.destroy()
        logger.debug('Application closed')

    def load_language(self, language:str) -> None:
        ''' Update the language of the current textbox. '''
        self.language.load_language(language)

    def populate_key_commands(self, event) -> None:
        ''' Populate the key commands list. '''
        data = self.key_bindings.binder
        event.widget.list_key_commands(data)

    def parse_progress_profiler(self, event) -> None:
        ''' Parse the progress profiler output file. '''
        profiler = event.widget
        filename = profiler.filename.get()
        parser_data = progress_profiler.parse_profiler_data(filename)
        profiler.load_profiler_data(parser_data)


    def build_text_for_parser(self, event) -> str:
        ''' Build the text to be parsed. '''
        profiler = event.widget
        if cfg.project_src:
            results = includes_expander.expand_includes(profiler.tree.current_line())
            profiler.text.delete('1.0', tk.END)
            profiler.text.insert(tk.END, ''.join(results))
