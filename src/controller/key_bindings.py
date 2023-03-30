from settings import Configuration
from modules.logging import Log

cfg = Configuration()
logger = Log(__name__)

''' Here's an empty keybinding dictionary.
    {'name': '', 'key': '< >', 'bind_func': self.app.bind, 'callback': lambda event: , 'widget_class': '', 'active': True, 'can_override': False},
'''


class KeyBindings:
    ''' This class is responsible for binding all the key bindings to the self.app. 
        It is called from the app class. '''
    def __init__(self, controller):
        self.controller = controller
        self.app = self.controller.app
        
        # Holds all the key bindings
        self.binder = {}
        self.user_binder = {}

        self._load_user_settings()
        self._unbindings()
        self._init_no_override_bindings()
        self._textbox_important_bindings()
        self.bind_keys()
        logger.debug("Key bindings initialized")

    def register_binding(self,
                         name:str, 
                         category:str,
                         bind_func:object, 
                         key:str, 
                         callback:object, 
                         widget_class:str=None, 
                         active:bool=True, 
                         can_override:bool=False,
                         **kwargs):
        ''' This is a wrapper for the bind method. It is used to register key bindings 
            and allow for custom key bindings to be loaded from the config file. 
            
            bind_func: The method that is used to bind the key. eg: self.app.bind
            name: The display name of the key binding. eg: "Save File"
            category: The category of the key binding. eg: "File Management"
            key: The key to bind. eg: "<Control-s>"
            callback: The callback function to bind to the key. eg: self.controller.file_system.save_file
            widget_class: The widget class to bind the key to. eg: "Text" 
            active: Whether the key binding is active or not. eg: True
            override: Whether the key binding can be overridden by the user. eg: False'''
        if name in self.user_binder:
            key = self.user_binder[name]['key']

        self.binder[name] = { 
            'category': category,
            'bind_func': bind_func, 
            'key': key, 
            'callback': callback, 
            'widget_class': widget_class, 
            'active': active, 
            'can_override': can_override }

        if active:
            if widget_class:
                bind_func(widget_class, key, callback, **kwargs)
            else:
                bind_func(key, callback, **kwargs)

    def _unbindings(self):
        ''' These unbind the default bindings for TK widgets. 
            Tracked here so they can be found easily. '''
        # Unbind the default tab key for all widgets before overriding it
        self.app.unbind_all("<Tab>")    
        
    def _load_user_settings(self):
        ''' Loads the user key bindings from the config file. '''
        ... # Still to be implemented

    def _init_no_override_bindings(self):
        ''' These are the key bindings that are not overridden by the user.'''

        no_override_bindings = [
            # File management
            {'name': 'New file', 'key': '<Control-n>', 'category': 'File management',
                'bind_func': self.app.bind,
                'callback': lambda event: self.controller.file_system.new_file()},

            {'name': 'Open file', 'key': '<Control-o>', 'category': 'File management', 
                'bind_func': self.app.bind, 
                'callback': lambda event: self.controller.file_system.open_file()},

            {'name': 'Save file', 'key': '<Control-s>', 'category': 'File management', 
                'bind_func': self.app.bind, 
                'callback': lambda event: self.controller.file_system.save_file()},

            {'name': 'Save as file', 'key': '<Control-S>', 'category': 'File management', 
             'bind_func': self.app.bind, 
             'callback': lambda event: self.controller.file_system.save_as_file()},

            # Find entry overrides
            {'name': 'Find next', 'key': '<Return>', 'category': 'Text editor',
                'widget_class': 'Entry', 
                'bind_func': self.app.bind_class, 
                'callback': lambda event: self.controller.view.textbox.editor.find_text(
                                                self.controller.view.toolbar.find_entry.get())},

            {'name': 'Find previous', 'key': '<Shift-Return>', 'category': 'Text editor',
                'widget_class': 'Entry', 
                'bind_func': self.app.bind_class, 
                'callback': lambda event: self.controller.view.textbox.editor.find_text(
                                                self.controller.view.toolbar.find_entry.get(), direction=-1)},

            {'name': 'Find return focus', 'key': '<Escape>', 'category': 'Text editor',
                'widget_class': 'Entry', 
                'bind_func': self.app.bind_class, 
                'callback': lambda event: self.controller.view.textbox.focus()},       
        ]

        for binding in no_override_bindings:
            self.register_binding(**binding, active=True, can_override=False)


    # Bad name. Needs a new one
    def _textbox_important_bindings(self):
        ''' These are the key bindings that are specific to the textbox. Some of them
            are not overridden by the user, others are. ''' 
        textbox_bindings = [
            {'name': 'Undo', 'key': '<Control-z>', 'category': 'Text editor',
                'widget_class': 'Text', 'active': True, 'can_override': False,
                'bind_func': self.app.bind_class, 
                'callback': lambda event: self.controller.view.textbox.history.undo()},

            {'name': 'Redo', 'key': '<Control-y>', 'category': 'Text editor',
                'widget_class': 'Text', 'active': True, 'can_override': False,
                'bind_func': self.app.bind_class, 
                'callback': lambda event: self.controller.view.textbox.history.redo()},

            {'name': 'Paste', 'key': '<Control-v>', 'category': 'Text editor',
                'active': True, 'can_override': False,
                'bind_func': self.app.bind, 
                'callback': lambda event: self.controller.view.textbox.clipboard.paste_text()
             },

            {'name': 'Select all', 'key': '<Control-a>', 'category': 'Text editor',
                'active': True, 'can_override': False,
                'bind_func': self.app.bind, 
                'callback': lambda event: self.controller.view.tabs.textbox.cursor.select_all() 
             },
            {'name': 'Indent', 'key': '<Tab>', 'category': 'Text editor',
                'widget_class': 'Text', 'active': True, 'can_override': False,
                'bind_func': self.app.bind_class, 
                'add':False, ## Additional parameter to the bind function
                'callback': lambda event: self.controller.view.tabs.textbox.editor.add_indent(), 
             },
            {'name': 'Cancel find highlight ', 'key': '<Escape>', 'category': 'Text editor',
                'widget_class': 'Text', 'active': True, 'can_override': False,
                'bind_func': self.app.bind_class, 
                'callback': lambda event: self.controller.view.tabs.textbox.delete_tags_by_name("find")
             }
        ]
        for binding in textbox_bindings:
            self.register_binding(**binding)

    def bind_keys(self):
        ''' Key bindings are attached here. There is an important thing to know, 
            that they will be called in order from the class level up to 
            the app level. That means to override a key binding, you need to assign
            it at the class level and then return 'break' to stop the event from
            propagating up the levels. '''

        # Settings window
        self.app.bind("<Control-Key-comma>", self.controller.view.open_settings_window)

        # UI management
        self.app.bind("<Control-equal>", lambda event: self.controller.view.ui.font_size_bump(increase=True))
        self.app.bind("<Control-minus>", lambda event: self.controller.view.ui.font_size_bump(increase=False))
        self.app.bind("<Alt-c>", lambda event: self.controller.utilities.open_calculator())

        # Textbox overrides
        self.app.bind_class("Text", "<Alt-d>", lambda event: self.controller.view.ui.toggle_theme())
        self.app.bind_class("Text", "<Control-d>", lambda event: self.controller.view.textbox.editor.delete_line())
        self.app.bind_class("Text", "<Control-l>", lambda event: self.controller.view.textbox.editor.duplicate_line())

        self.app.bind("<Alt-Shift-Up>", lambda event: self.controller.view.textbox.editor.move_line(direction=1))
        self.app.bind("<Alt-Shift-Down>", lambda event: self.controller.view.textbox.editor.move_line(direction=-1))

        # Textbox management
        
        self.app.bind("<Control-f>", lambda event: self.controller.view.toolbar.find_entry.focus())
        self.app.bind("<Control-g>", lambda event: self.controller.view.textbox.editor.find_text(
            self.controller.view.toolbar.find_entry.get(), direction=1))
        self.app.bind("<Control-Shift-G>", lambda event: self.controller.view.textbox.editor.find_text(
            self.controller.view.toolbar.find_entry.get(), direction=-1))


        # Syntax highlighting
        self.app.bind("<Key>", lambda event: self.controller.language.dynamic_syntax_formatting(event))
        self.app.bind_all("<space>", lambda event: self.controller.language.dynamic_syntax_formatting(event))
        #self.app.bind_all("<Return>", lambda event: self.controller.language.dynamic_syntax_formatting(event))
        self.app.bind("<KP_Enter>", lambda event: self.controller.language.dynamic_syntax_formatting(event))
        
        self.app.bind("<Alt-p>", lambda event: self.controller.language.static_syntax_formatting())

        # Tab management
        self.app.bind("<<NotebookTabChanged>> ", lambda event: self.controller.view.tab_change())
        self.app.bind("<Control-w>",    lambda event: self.controller.view.tabs.close_tab())
        
        # Clipboard management
        self.app.bind("<Alt-e>", lambda event: self.controller.utilities.eval_selection())

        ###
        # Various tk keybindings that exist by default
        # 
        # <Control-p> previous line
        # <Control-k> delete to end of line
        ###