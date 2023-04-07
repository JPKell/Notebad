import os
from tkinter import PhotoImage, Frame, font
from tkinter.ttk import Style


from settings  import Configuration
from .colors import Themes
from modules.logging import Log

cfg = Configuration()
logger = Log(__name__)

class UI:
    ''' Manages the appearance of the app. Custom colors are set in the colors.py file. ''
        Primarily used to toggle between light and dark themes.
        '''
    def __init__(self, view: Frame) -> None:
        self.view = view
        self.app  = view.controller.app
        self.theme = cfg.default_theme
        self.style = Style()
        self.font = font.nametofont('TkFixedFont')
        self._font_size = cfg.font_size

        self._init_style()
        self._root_window_setup()
        logger.debug("UI initialized")

    @property
    def font_size(self) -> int:
        return self._font_size
    
    @font_size.setter
    def font_size(self, size: int) -> None:
        self._font_size = size
        self.font.configure(size=size)
        self.view.textbox.config(font=(cfg.program_font, str(self.font_size)))
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
            self.style.theme_use(self.theme)
            if self.theme == 'forest-dark':
                colors = Themes.dark
            else:
                colors = Themes.light
        # If we are not reloading then we want to toggle themes
        elif self.theme == 'forest-dark':
            self.theme = 'forest-light'
            colors = Themes.light
            self.style.theme_use('forest-light')
        else:
            self.theme = 'forest-dark'
            colors = Themes.dark
            self.style.theme_use('forest-dark')

        logger.debug(f"Theme set to {self.theme}")
     
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
                'activeforeground':colors.foreground 
                }
            self.view.controller.menu.configure(**menu_colors)   
            # Loop through the menu items and set the colors 
            for menu in self.view.controller.menu.menu_list:
                menu.config(**menu_colors)     
    
        
        # Tab styles. We need to cycle through all the tabs and set the styles.
        # otherwise the active tab will be the only one to change. 
        for tab in self.view.tabs.tabs():
            # The tab is a frame so we need to get the textbox from the frame.
            # Other widgets are in the tab as well but they are in the ttk 
            # style so they will get updated with the theme.
            tab = self.view.tabs.nametowidget(tab)
            textbox = tab.winfo_children()[0]
            textbox.config(
                background=colors.text_background, 
                foreground=colors.text_foreground, 
                insertbackground=colors.cursor, 

                highlightbackground=colors.text_background, 
                highlightcolor=colors.text_background,
                )
            # Style the line numbers on the side
            textbox.linenumbers.config(bg=colors.background, highlightbackground=colors.background)
            
            # textbox.linenumbers.itemconfigure("lineno", fill=colors.text_foreground)
            
            # Style the syntax highlighting
            textbox.tag_configure("red", foreground = colors.syn_red)
            textbox.tag_configure("orange", foreground = colors.syn_orange)
            textbox.tag_configure("yellow", foreground = colors.syn_yellow)
            textbox.tag_configure("green", foreground = colors.syn_green)
            textbox.tag_configure("cyan", foreground = colors.syn_cyan)
            textbox.tag_configure("blue", foreground = colors.syn_blue)
            textbox.tag_configure("alt_blue", foreground = colors.syn_alt_blue)
            textbox.tag_configure("violet", foreground = colors.syn_violet)
            textbox.tag_configure("magenta", foreground = colors.syn_magenta)
            textbox.tag_configure("grey", foreground = colors.syn_grey)
            textbox.tag_configure("error", foreground = colors.syn_error)

            # Style the status bar
            textbox.footer.status.config(bg=colors.background, fg=colors.foreground)
            textbox.footer.pos_lbl.config(bg=colors.background, fg=colors.syn_orange)
            textbox.footer.lang_lbl.config(bg=colors.background, fg=colors.syn_yellow)
            textbox.footer.sel_lbl.config(bg=colors.background, fg=colors.syn_orange)

    @staticmethod
    def parse_windows_mousewheel(event, callback=None):
        ''' Translate Windows mouse scroll events into their delta value to differentiate between up and down.
            A Delta of 120 is up, and -120 is down. Fast scrolling seems to multiply the delta value, e.g. 240, 360, etc...'''
        if event.delta > 0:
            mouse_wheel_up = True
        elif event.delta < 0:
            mouse_wheel_up = False
        callback(mouse_wheel_up)


    # This is not currently in use. It was for the x's on the tabs to close them.
    def _init_img_pool(self) -> None:
        ''' Images used in the tabs. These look okay at best. Would be nice to replace these'''
        self.images = (
            PhotoImage("img_close", data='''
                R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
                '''),
            PhotoImage("img_closeactive", data='''
                R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
                AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
                '''),
            PhotoImage("img_closepressed", data='''
                R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
            ''')
        )

    def _init_style(self) -> None:
        ''' This will get everything set up for the theme.'''
        # Load a prefab theme

        self.app.tk.call('source', os.path.join(cfg.theme_dir, f'forest-dark.tcl'))
        self.app.tk.call('source', os.path.join(cfg.theme_dir, f'forest-light.tcl'))

        # This custom element is used to make a close element for us to map over the image. 

        # This section created the custom themes previously, It has the code for the close buttons.
        # they didn't work on windows, so there's something to figure out. Its here as a starting 
        # point for when it gets tackled.

        # self.style.element_create("close", "image", "img_close",
        #     ("active", "pressed", "!disabled", "img_closepressed"),
        #     ("active", "!disabled", "img_closeactive"), border=8, sticky='e')
        # This section creates the theme and sets the colors for the theme
        # for title, colors in [('forest-dark', Themes.dark), ('forest-light', Themes.light)]: 
        #     self.style.theme_create( title, parent="alt", settings={
        #         "TNotebook": {
        #             "configure": {
        #                 "tabmargins": [cfg.line_number_width + 2, 5, 10, 0], 
        #                 "foreground": colors.background,
        #                 "background": colors.background,
        #                 "borderwidth": 0,
        #                 "highlightthickness": 0,
        #                 } 
        #             },
        #         "TNotebook.Tab": {
        #             "configure": {
        #                 "padding": [10, 2, 10, 0], 
        #                 "background": colors.tab_unselect,
        #                 "foreground": colors.foreground,
        #                 "compound": "right",
        #                 "borderwidth": 0,
        #                 },
                    
        #             "map": {
        #                 "background": [("selected", colors.tab_select)],
        #                 "expand": [("selected", [0, 1, 1, 0])] 
        #                 },
        #             } ,
        #         } 
        #     ) 
        #     self._register_tab_close_button_with_style()
        #     logger.verbose(f"Created theme: {title}")

        # Initialize to the correct theme
        if self.theme == 'forest-dark':
            self.style.theme_use('forest-dark')
        else:
            self.style.theme_use('forest-light')

    def _register_tab_close_button_with_style(self) -> None:
        ''' The tab close is a custom element so we need to register it with the style.
            The main reason for this is so we can get that the close button is the element under 
            the cursor when clicking on the close icon. 
        '''
        # This section layout the tab close button and provides the element name "close" to the style
        self.style.layout("TNotebook", [("TNotebook.client", {"sticky": "nswe"})])
        self.style.layout("TNotebook.Tab", [
            ("TNotebook.tab", {
                "sticky": "nswe",
                "children": [
                    ("TNotebook.padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [(
                            "TNotebook.focus", {
                                "side": "top",
                                "sticky": "nswe",
                                "children": [
                                    ("TNotebook.label", {"side": "left", "sticky": ''}),
                                    ("TNotebook.close", {"side": "right", "sticky": ''})
                                    ]
                                }
                            )]
                        }
                    )]
                }
            )]
        )
            

    def _root_window_setup(self) -> None:
        ''' Basic geometry and title settings for the root window.'''
        app = self.view.app
        # Window settings 
        app.title(cfg.app_title)  
        app.geometry(cfg.geometry) 
        app.minsize(*cfg.min_size)

        path_func = self.view.controller.relative_to_abs_path
        if cfg.os == 'nt': 
            app.iconbitmap(path_func('assets/icon.ico'))
        else:
            logo = PhotoImage(file=path_func('assets/icon.gif'))
            app.call('wm', 'iconphoto', app._w, logo)
