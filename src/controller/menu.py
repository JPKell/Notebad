from tkinter import Menu, Tk

from modules.logging import Log

logger = Log(__name__)

class Menubar(Menu):
    ''' Holds all the menu bar items, mainly just a nice place to keep it all'''
    def __init__(self, root:Tk, controller) -> None:
        ''' Initializes the menu bar object. '''
        super().__init__(root, border=0)
        root.config(menu=self)       # Register as the menu bar with root
 
        self.controller = controller
        self.view = None
        self.menu_list = [] # List of all menu bar items to make theming easier
        logger.debug("Menu bar initialized")

    def set_view(self, view):
        ''' Sets the view object. This is needed because the view object is 
            created after the menu bar object. '''
        self.view = view
        self._make_menu()

    def _make_menu(self):
        ''' Creates the menu bar items. Lambda functions are required in some 
            cases when we need to pass arguments, or the parent class isn't 
            fully instantiated yet.'''


        # File menu
        self.file_menu = Menu(self, tearoff=0)
        self.menu_list.append(self.file_menu)
        self.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New",     accelerator="Ctrl N",       command=self.controller.file_system.new_file)
        self.file_menu.add_command(label="Open",    accelerator="Ctrl O",       command=self.controller.file_system.open_file)
        self.file_menu.add_command(label="Save",    accelerator="Ctrl S",       command=self.controller.file_system.save_file)
        self.file_menu.add_command(label="Save As", accelerator="Ctrl Shift S", command=self.controller.file_system.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Close tab", accelerator="Ctrl W",     command=lambda: self.view.tabs.close_tab()) 
        self.file_menu.add_command(label="Exit app",  accelerator="Alt F4",     command=self.controller.exit_app)

        # Edit menu
        self.edit_menu = Menu(self, tearoff=0)
        self.menu_list.append(self.edit_menu)
        self.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Cut",   accelerator="Ctrl X",  command=self.controller.view.textbox.clipboard.cut_text)
        self.edit_menu.add_command(label="Copy",  accelerator="Ctrl C",  command=self.controller.view.textbox.clipboard.copy_text)
        self.edit_menu.add_command(label="Paste", accelerator="Ctrl V",  command=self.controller.view.textbox.clipboard.paste_text)
        self.edit_menu.add_separator()
        # self.tools_menu.add_command(label="Find", accelerator="Ctrl F", command=self.controller.find_text) # TODO: Implement find text
        # self.tools_menu.add_command(label="Replace", accelerator="Ctrl R", command=self.controller.replace_text) # TODO: Implement replace text

        self.edit_menu.add_command(label="Undo",  accelerator="Ctrl Z",  command=lambda: self.view.textbox.history.undo())
        self.edit_menu.add_command(label="Redo",  accelerator="Ctrl Y",  command=lambda: self.view.textbox.history.redo())

        # View menu
        self.view_menu = Menu(self, tearoff=0)
        self.menu_list.append(self.view_menu)
        self.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Dark Mode", accelerator="Ctrl D", command=lambda: self.view.ui.toggle_theme())
        self.view_menu.add_command(label="Font +",    accelerator="Ctrl +", command=lambda: self.view.ui.font_size_bump(increase=True))
        self.view_menu.add_command(label="Font -",    accelerator="Ctrl -", command=lambda: self.view.ui.font_size_bump(increase=False))
                                   
        # Tools menu
        self.tools_menu = Menu(self, tearoff=0)
        self.menu_list.append(self.tools_menu)
        self.add_cascade(label="Tools", menu=self.tools_menu)
        self.tools_menu.add_command(label="Calculator", accelerator="Alt C", command=lambda: self.controller.utilities.open_calculator())
        
        self.py_menu = Menu(self, tearoff=0)
        self.menu_list.append(self.py_menu)
        self.add_cascade(label="Py", menu=self.py_menu)
        self.py_menu.add_command(label="Eval line/selection", accelerator="Alt E", command=lambda: self.controller.utilities.eval_selection())

####  This needs to have the ui set at first load cause it's wrong. 