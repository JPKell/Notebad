from tkinter import Menu, END
import os

from settings import Configuration
from modules.logging import Log
from widgets import NFrame
from .tabs import Tabs
from .ui import UI

cfg = Configuration()
logger = Log(__name__)

class Menubar(Menu):
    ''' Holds all the menu bar items, mainly just a nice place to keep it all'''
    def __init__(self, root, view:NFrame, tabs:Tabs, ui:UI) -> None:
        ''' Initializes the menu bar object. '''
        super().__init__(root, border=0)
        root.config(menu=self)       # Register as the menu bar with root
        # Gather view objects
        self.view = view
        self.tabs = tabs
        self.ui   = ui

        self._recent_file = '' # A temporary variable to hold the recent file path for events
        self.menu_list = [] # List of all menu bar items to make theming easier
        self._make_menu()

        self.bind_all("<<UpdateRecentFiles>>", self.make_recent_file_list)

        logger.debug("Menu bar initialized")

    def _event(self, event, source:NFrame=None):
        ''' Event handler for menu bar items. '''
        if source is None: source = self.view
        def return_function(*_):
            source.event_generate(event)
        return return_function
    
    def _open_recent_event(self, file):
        ''' Event handler for the recent files menu. '''
        def return_function(*_):
            self._recent_file = file
            self.event_generate('<<OpenRecentFile>>')
        return return_function

    def _make_menu(self):
        ''' Creates the menu bar items. Lambda functions are required in some 
            cases when we need to pass arguments, or the parent class isn't 
            fully instantiated yet.'''

        # File menu
        self.file_menu = Menu(self, tearoff=0)
        self.menu_list.append(self.file_menu)
        self.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New",  accelerator="Ctrl N", command=self._event('<<NewFile>>'))
        self.file_menu.add_command(label="Open", accelerator="Ctrl O", command=self._event('<<OpenFile>>'))

        self.recent_files_menu = Menu(self.file_menu, tearoff=0)
        self.file_menu.add_cascade(menu=self.recent_files_menu, label="Open Recent...")
        self.make_recent_file_list()

        self.file_menu.add_command(label="Save",    accelerator="Ctrl S",       command=self._event('<<SaveFile>>', self.tabs.cur_tab))
        self.file_menu.add_command(label="Save As", accelerator="Ctrl Shift S", command=self._event('<<SaveFileAs>>', self.tabs.cur_tab))

        self.file_menu.add_separator()
        self.file_menu.add_command(label="Settings", accelerator="Ctrl ,",      command=self.view.open_settings_window)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Close tab", accelerator="Ctrl W",     command=lambda: self.tabs.close_tab())
        self.file_menu.add_command(label="Exit app",  accelerator="Alt F4",     command=self._event('<<ExitApp>>'))

        # Edit menu
        self.edit_menu = Menu(self, tearoff=0)
        self.menu_list.append(self.edit_menu)
        self.add_cascade(label="Edit", menu=self.edit_menu)

        self.edit_menu.add_command(label="Cut",   accelerator="Ctrl X",  command=self._event('<<Cut>>', self.tabs.cur_tab))
        self.edit_menu.add_command(label="Copy",  accelerator="Ctrl C",  command=self._event('<<Copy>>', self.tabs.cur_tab))
        self.edit_menu.add_command(label="Paste", accelerator="Ctrl V",  command=self._event('<<Paste>>', self.tabs.cur_tab))
        
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Find", accelerator="Ctrl F", command=self._event('<<FindFocus>>', self.tabs.cur_tab))

        self.edit_menu.add_command(label="Find Next", accelerator="Ctrl G", command=self._event('<<FindNext>>', self.tabs.cur_tab))
        self.edit_menu.add_command(label="Find Previous", accelerator="Ctrl Shift G", command=self._event('<<FindPrevious>>', self.tabs.cur_tab))

        # self.tools_menu.add_command(label="Replace", accelerator="Ctrl R", command=self.controller.replace_text) # TODO: Implement replace text
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Undo",  accelerator="Ctrl Z",  command=self._event('<<Undo>>', self.tabs.cur_tab))
        self.edit_menu.add_command(label="Redo",  accelerator="Ctrl Y",  command=self._event('<<Redo>>', self.tabs.cur_tab))

        # View menu
        self.view_menu = Menu(self, tearoff=0)
        self.menu_list.append(self.view_menu)
        self.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Dark Mode", accelerator="Ctrl D", command=lambda: self.ui.toggle_theme())
        self.view_menu.add_command(label="Font +",    accelerator="Ctrl +", command=lambda: self.ui.font_size_bump(increase=True))
        self.view_menu.add_command(label="Font -",    accelerator="Ctrl -", command=lambda: self.ui.font_size_bump(increase=False))
                                   
        # Tools menu
        self.tools_menu = Menu(self, tearoff=0)
        self.menu_list.append(self.tools_menu)
        self.add_cascade(label="Tools", menu=self.tools_menu)
        self.tools_menu.add_command(label="Calculator", accelerator="Alt C", command=self._event('<<OpenCalculator>>'))
        self.tools_menu.add_command(label="Key commands",  command=lambda: self.view.key_command_list())
        self.tools_menu.add_separator()
        self.tools_menu.add_command(label="Progress Profiler", command=lambda: self.tabs.new_tab('profiler'))
        
        self.py_menu = Menu(self, tearoff=0)
        self.menu_list.append(self.py_menu)
        self.add_cascade(label="Py", menu=self.py_menu)
        self.py_menu.add_command(label="Eval line/selection", accelerator="Alt E", command=self._event('<<PyEvalLine>>', self.tabs.cur_tab))


    def make_recent_file_list(self, event=None):
        ''' Create the recent files list in realtime to account for deleted
            files, and recently opened files in this session.
            Currently, this relies on a MenuSelect event and then checking the "y" value...
            Not sure this is the most concrete solution. May need revisiting in future. '''
        if True: #event is not None and event.y != 0:
            # Remove all existing recent file menu_commands
            last_item = self.recent_files_menu.index('end')
            if last_item is not None:
                self.recent_files_menu.delete(0, last_item + 1)

            # Build recent files list from recent files .txt file
            with open(os.path.join(cfg.data_dir, 'recent_files.txt'), 'r') as f:
                recent_files = f.readlines()
                recent_files.reverse()
                for file in recent_files:
                    file = file.strip()
                    # Check the filepath still exists on the system
                    if os.path.exists(file):
                        ### TODO Make this work
                        self.recent_files_menu.add_command(label=os.path.basename(file), command=lambda file=file: self._open_recent_event(file))
