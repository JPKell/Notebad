from tkinter import font
import os

class Configuration:
    """ A class to hold configuration values for the app. This acts as a singleton 
        class and even though its instantiated multiple times, it will only ever
        return the same instance. """
    os = os.name
    current_dir = ''

    # Window settings
    app_title = 'Notebad'
    geometry = '800x600'
    min_size = (300, 200)
    default_theme = 'light'

    # Status bar settings
    status_bar_default_text = 'Status Bar'
    status_bar_scrolling    = True
    status_bar_duration     = 5000  # ms to display text before resetting  
    status_bar_freeze       = False # Prevent resetting of status bar       

    # File settings
    new_file_name = 'new.txt'
    hardcore_mode = False
    max_undo = 50

    # Textbox appearance
    font_size = 12
    line_number_width = 33

    # Textbox behaviour
    indent_size = 4
    enable_syntax_highlighting = True
    max_undo = 50              # This should get tested for memory usage

    # Language options
    syntax_uppercase = True
    syntax_expand = True    # Expand syntax tokens to full name    

    # Calculator settings
    calc_title = 'Mathbad'
    calc_bg    = '#111'
    calc_outer_pad = 3

    # Logging settings
    log_console_level = 2
    log_file_level = 2
    log_performance = False
    log_performance_to_file = True
    log_performance_to_console = True
    # These populate at runtime in main
    log_dir = ''
    log_file = ''
    log_performance_file = ''

    # Developer settings. Don't change these here. If you want developer functions, use dev mode. 
    preload_file = False

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Configuration, cls).__new__(cls)
        return cls.instance

    def set_root_dir(self, root_dir):
        self.current_dir = root_dir
        self.log_dir  = os.path.join(root_dir, 'logs')
        self.log_file = os.path.join(self.log_dir, 'notebad.log')
        self.log_performance_file = os.path.join(self.log_dir, 'performance.log')
        
        # Now that we know where we are we can look for personal settings
        self.init_personal_settings()
        self.load_personal_settings()

    def init_personal_settings(self) -> None:
        """ Look for personal settings and create them if they don't exist. """
        config_file = os.path.join(self.current_dir, 'personal.cf')
        if not os.path.isfile(config_file):
            with open(config_file, 'w') as f:
                f.write('')

    def load_personal_settings(self) -> None:
        ''' Load personal settings from the personal config file. '''

        config_file = os.path.join(self.current_dir, 'personal.cf')
        with open(config_file, 'r') as f:
            # Grab each line of the file and strip the newline character
            lines = [ l.strip() for l in f.readlines() if l[0] != '#' ]
            for ln in lines:
                # Split the line into key and value
                key, value = ln.split('=')
                # Strip the key and value of whitespace
                key = key.strip()
                value = value.strip() 

                # Set the value of the key
                setattr(self, key, eval(value))
