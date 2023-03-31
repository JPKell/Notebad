import os
import pathlib

# We can also use variables above the config class to have constant values
# Example: provincial tax rates and we have a calculate tax button on the calc. 
#          They are only needed in one place and we don't want the user to change
#          them. So we can just put them here and import them as needed.    

class Configuration:
    """ A class to hold configuration values for the app. This acts as a singleton 
        class and even though its instantiated multiple times, it will only ever
        return the same instance. """
    os = os.name
    current_dir = ''

    # This will get populated at runtime in main
    config_file = ''

    # Window settings
    app_title = 'Notebad'
    geometry = '800x600'
    min_size = (300, 200)
    start_fullscreen = False
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
    program_font = 'Courier New'
    font_size = 12
    line_number_width = 33
    find_background = '#25f55c'  # Default background colour for highlighted Find results
    block_cursor = False
    cursor_on_time = 600
    cursor_off_time = 300

    # Textbox behaviour
    indent_size = 4
    max_undo = 50              # This should get tested for memory usage

    # Language options
    syntax_on_load = False
    syntax_on_new_line = False
    syntax_on_type = False
    syntax_uppercase = True
    syntax_expand = True       # Expand syntax tokens to full name    
    
    # This may be a problem as we will have to track whitespace and ditch it when indenting
    # The whitespace would have to be tracked and ditched when assembling it back together
    # We could technically rebuild the language module and that would work, but rebuilding the
    # language model for a feature doesn't make sense. If it can be done quickly we may as well
    # track whitespace all the time, but unless we can do it quickly we should not track it and
    # just implement indenting. 
    syntax_indent = True    

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
            cls.instance.set_root_dir()
        return cls.instance

    def set_root_dir(self) -> None:
        """ Set the root directory of the app. This is the directory that the
            app source is from. """
        self.current_dir = pathlib.Path(__file__).parent.resolve()
        self.log_dir  = os.path.join(self.current_dir, 'logs')
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
                f.write('# Make changes here to override default configuration settings.\r')
        self.config_file = config_file

    def load_personal_settings(self) -> None:
        ''' Load personal settings from the personal config file. '''

        config_file = os.path.join(self.current_dir, 'personal.cf')
        with open(config_file, 'r') as f:
            # Grab each line of the file and strip the newline character
            lines = [ l.strip() for l in f.readlines() if l[0] != '#' ]
            for ln in lines:
                # Skip lines that don't have an equals sign to allow whitespace 
                if ln.find('=') == -1:
                    continue

                # Split the line into key and value
                key, value = ln.split('=')
                key   = key.strip()
                value = value.strip() 

                # Set the value of the key
                setattr(self, key, eval(value))

    def save_personal_settings(self, *args, **kwargs) -> None:
        ''' Save personal settings to the personal config file. Can take 
            any number of keyword arguments. Any strings must be passed with double quotes
            e.g. setting = '"user_setting"' OR setting = '"%s"' % setting_string '''
        # Update the values of the active config object
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Update the values of the config file
        config_file = os.path.join(self.current_dir, 'personal.cf')
        existing_config = []

        with open(config_file, 'r') as f: 
            existing_config = f.readlines()

        with open(config_file, 'w') as f:
            for ln in existing_config:
                # Write out the comment lines as is
                if ln[0] == '#' or ln.find('=') == -1:
                    f.write(ln)

                # Replace any existing settings
                else:
                    key, value = ln.split('=')
                    key = key.strip()
                    if key in kwargs:
                        value = kwargs.pop(key)
                        f.write(f'{key} = {value}\n')
                    else:
                        f.write(ln)
                    
            # Write out any new settings
            for key, value in kwargs.items():
                f.write(f'{key} = {value}\n')
