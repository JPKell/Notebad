from tkinter import font
import os

class Configuration:
    """ A class to hold configuration values for the app. This acts as a singleton 
        class and even though its instantiated multiple times, it will only ever
        return the same instance. """

    os = os.name
    current_dir = ''
    dev_mode = False        # Change this in main.py to enable dev mode
    
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
    log_console_level = 4
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

    def enable_dev_mode(self):
        ''' Development related overrides '''
        self.dev_mode = True
        self.app_title += ' dev'
        self.default_theme = 'dark'
        self.geometry = '800x600'
        self.hardcore_mode = True
        self.enable_syntax_highlighting = True
        self.preload_file = '/home/jpk/gits/Notebad/test.p'
        self.log_performance = True

