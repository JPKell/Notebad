from tkinter import Menu

class Menubar:
    ''' Holds all the menu bar items, mainly just a nice place to keep it all'''
    def __init__(self, view, controller) -> None:
        self.view = view
        self.controller = controller
        self.menu_list = [] # List of all menu bar items to make theming easier
        self._make_menu()

    def _make_menu(self):
        ''' Creates the menu bar items. Lambda functions are required in some 
            cases when we need to pass arguments, or the parent class isn't 
            fully instantiated yet.'''
        self.menu = Menu(self.view.master, border=0,) # Menu bar master object
        self.view.master.config(menu=self.menu)       # Set as the menu bar

        # File menu
        self.file_menu = Menu(self.menu, tearoff=0)
        self.menu_list.append(self.file_menu)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New",     accelerator="Ctrl N",       command=self.controller.new_textbox)
        self.file_menu.add_command(label="Open",    accelerator="Ctrl O",       command=self.controller.open_file)
        self.file_menu.add_command(label="Save",    accelerator="Ctrl S",       command=self.controller.save_file)
        self.file_menu.add_command(label="Save As", accelerator="Ctrl Shift S", command=self.controller.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Close tab", accelerator="Ctrl W",     command=lambda: self.view.tabs.close_tab()) 
        self.file_menu.add_command(label="Exit app",  accelerator="Alt F4",     command=self.controller.exit_app)

        # Edit menu
        self.edit_menu = Menu(self.menu, tearoff=0)
        self.menu_list.append(self.edit_menu)
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Cut",   accelerator="Ctrl X",  command=self.controller.cut_text)
        self.edit_menu.add_command(label="Copy",  accelerator="Ctrl C",  command=self.controller.copy_text)
        self.edit_menu.add_command(label="Paste", accelerator="Ctrl V",  command=self.controller.paste_text)
        self.edit_menu.add_separator()
        # self.tools_menu.add_command(label="Find", accelerator="Ctrl F", command=self.controller.find_text) # TODO: Implement find text
        # self.tools_menu.add_command(label="Replace", accelerator="Ctrl R", command=self.controller.replace_text) # TODO: Implement replace text

        self.edit_menu.add_command(label="Undo",  accelerator="Ctrl Z",  command=self.controller.undo)
        self.edit_menu.add_command(label="Redo",  accelerator="Ctrl Y",  command=self.controller.redo)

        # View menu
        self.view_menu = Menu(self.menu, tearoff=0)
        self.menu_list.append(self.view_menu)
        self.menu.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Dark Mode", accelerator="Ctrl D", command=self.view.ui.toggle_theme)
        self.view_menu.add_command(label="Font +",    accelerator="Ctrl +", command=lambda: self.view.tabs.textbox.change_font(size='+'))
        self.view_menu.add_command(label="Font -",    accelerator="Ctrl -", command=lambda: self.view.tabs.textbox.change_font(size='-'))
                                   
        # Tools menu
        self.tools_menu = Menu(self.menu, tearoff=0)
        self.menu_list.append(self.tools_menu)
        self.menu.add_cascade(label="Tools", menu=self.tools_menu)
        self.tools_menu.add_command(label="Calculator", accelerator="Alt C", command=self.controller.open_calculator)
        
        self.py_menu = Menu(self.tools_menu, tearoff=0)
        self.menu_list.append(self.py_menu)
        self.menu.add_cascade(label="Py", menu=self.py_menu)
        self.py_menu.add_command(label="Eval line/selection", accelerator="Alt E", command=self.controller.eval_selection)

