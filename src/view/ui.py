import os
from   tkinter     import font, PhotoImage, Tk
from   tkinter.ttk import Style

from   settings        import Configuration
from   modules.logging import Log
from   widgets         import NFrame
from   .colors         import Themes
from  .ide             import Ide

cfg = Configuration()
logger = Log(__name__)

class UI:
    ''' Manages the appearance of the app. Custom colors are set in the colors.py file. ''
        Primarily used to toggle between light and dark themes.
        '''
    def __init__(self, view: NFrame, root: Tk) -> None:
        self.view = view

        self.style = Style()
        self.font = font.nametofont('TkFixedFont')
        self._font_size = cfg.font_size

        self._init_root_tk_window(root)
        self._init_style()
        logger.debug("UI initialized")

    @property
    def font_size(self) -> int:
        return self._font_size
    
    @font_size.setter
    def font_size(self, size: int) -> None:
        self._font_size = size
        self.font.configure(size=size)
        self.view.cur_tab.text.config(font=(cfg.program_font, str(self.font_size)))
        self.view.event_generate('<<Change>>')   # This gets the line numbers to update
        logger.debug(f"Font size set to {size}")
    
    def font_size_bump(self, increase=True) -> None:
        ''' Increase or decrease the font size by 1 '''
        if increase:
            self.font_size += 1
        else:
            self.font_size -= 1

    def change_font(self, font:str):
        self.font.configure(family=font)
        logger.debug(f"Font changed to {font}")

    ## UI look and feel ##
    def toggle_theme(self, reload=False) -> None:
        ''' Toggle the theme between dark and light '''
        # We don't want to toggle the theme if we are just reloading
        # so just load the default colors otherwise toggle the theme 
        if reload:                      
            self.style.theme_use(cfg.theme)
            if cfg.theme == 'forest-dark':
                cfg.theme = 'forest-dark'
                colors = Themes.dark
            else:
                cfg.theme = 'forest-light'
                colors = Themes.light
        # If we are not reloading then we want to toggle themes
        elif cfg.theme == 'forest-dark':
            cfg.theme = 'forest-light'
            colors = Themes.light
            self.style.theme_use('forest-light')
        else:
            cfg.theme = 'forest-dark'
            colors = Themes.dark
            self.style.theme_use('forest-dark')

        self.view.event_generate('<<ThemeToggle>>')

        logger.debug(f"Theme set to {cfg.theme}")
     
        ### 
        # Menu bars are not easily modified in the windows system, 
        # so rather than have ugly menus, dark mode will have light
        # menus for now. I would like to change this, but it's a low 
        # priority.   
        if cfg.os != 'nt':
            # Menu bar styles     
            menu_colors = {
                'bg': colors.background, 
                'fg': colors.foreground, 
                'activebackground': colors.bg_highlight, 
                'activeforeground':colors.foreground,
                'relief': 'flat',
                }
            self.view.menu.configure(**menu_colors)   
            
            # Loop through the menu items and set the colors 
            for menu in self.view.menu.menu_list:
                menu.config(**menu_colors)     

        # Loop through the tabs and set the colors
        for tab in self.view.tabs.tabs():
            frame = self.view.nametowidget(tab)
            frame._set_theme()
        # logger.verbose("All textboxes unfocused")

    @staticmethod
    def parse_windows_mousewheel(event, callback=None):
        ''' Translate Windows mouse scroll events into their delta value to differentiate between up and down.
            A Delta of 120 is up, and -120 is down. Fast scrolling seems to multiply the delta value, e.g. 240, 360, etc...'''
        if event.delta > 0:
            mouse_wheel_up = True
        elif event.delta < 0:
            mouse_wheel_up = False
        callback(mouse_wheel_up)

    ###
    # Private methods
    ###
    def _init_root_tk_window(self, root: Tk) -> None:
        ''' Initialize the root tkinter window. '''
        # Add the themes to TK
        root.tk.call('source', os.path.join(cfg.theme_dir, 'forest-dark.tcl'))
        root.tk.call('source', os.path.join(cfg.theme_dir, 'forest-light.tcl'))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        root.title(cfg.app_title)  
        root.geometry(cfg.geometry) 
        root.minsize(*cfg.min_size)

        # Todo this needs to be moved to the view
        if cfg.os == 'nt': 
            root.iconbitmap(os.path.join(cfg.current_dir, 'assets', 'icon.ico'))
        else:
            logo = PhotoImage(os.path.join(cfg.current_dir, 'assets', 'icon.gif'))
            root.call('wm', 'iconphoto', root._w, logo)

    def _init_style(self) -> None:
        ''' This will get everything set up for the theme.'''

        # Initialize to the correct theme
        if cfg.theme == 'forest-dark':
            self.style.theme_use('forest-dark')
        else:
            self.style.theme_use('forest-light')
