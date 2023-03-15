class Configuration:
    """A class to hold configuration values for the app"""

    def __init__(self, dev_mode=False):
        self.dev_mode = dev_mode
        # Window settings
        self.app_title = 'Notebad'
        self.geometry = '800x600'
        self.min_size = (300, 200)
        self.default_theme = 'light'
        # Status bar settings
        self.status_bar_default_text = 'Status Bar'
        self.status_bar_scrolling    = True
        self.status_bar_duration     = 5000 # ms to display text before resetting  
        self.status_bar_freeze       = False # Prevent resetting of status bar       
        # File settings
        self.new_file_name = 'new.txt'
        self.hardcore_mode = False
        self.max_undo = 50
        # Textbox appearance
        self.font = {                   # This should get unpacked into the font.Font() constructor 
            'family': 'Consolas',       # usint the ** operator ie. **cf.font
            'size'  : 12,
            'weight': 'normal'
            }
        self.line_number_width = 33
        # Textbox behaviour
        self.indent_size = 4
        self.enable_syntax_highlighting = True
        self.max_undo = 50              # This should get tested for memory usage

        # Calculator settings
        self.calc_title = 'Mathbad'
        self.calc_bg    = '#111'
        self.calc_outer_pad = 3


        if dev_mode:
            self._dev_mode()

    def _dev_mode(self):
        ''' Development related overrides '''
        self.app_title += ' dev'
        # self.default_theme = 'dark'
        self.geometry = '800x600+3400+1'
        self.hardcore_mode = True
        self.enable_syntax_highlighting = True




cf = Configuration()