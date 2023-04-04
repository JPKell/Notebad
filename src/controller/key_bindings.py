from settings import Configuration
from modules.logging import Log

cfg = Configuration()
logger = Log(__name__)

''' Here's an empty keybinding dictionary.
    {'name': '', 'key': '< >', 'category': '',
        'widget_class': '', 'active': True, 'can_override': False
        'bind_func': self.app.bind, 
        'callback': lambda event: , 
        },
'''

###
# Various tk keybindings that exist by default
# 
# <Control-p> previous line
# <Control-k> delete to end of line
###

class KeyBindings:
    ''' This class is responsible for binding all the key bindings to the self.app. 
        It is called from the app class. '''
    def __init__(self, controller):
        self.controller = controller
        self.app = self.controller.app
        
        # Holds all the key bindings
        self.binder = []
        self.user_binder = []

        self._load_user_settings()
        self._unbindings()
        self._app_triggers()
        self._init_no_override_bindings()
        self._syntax_highlighting()
        self._textbox_important_bindings()
        self._assignable_bindings()
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
        if name in self.user_binder and can_override:
            key = self.user_binder[name]['key']

        # Do not process duplicates. Log a warning and return. Maybe raise an error? If there is a duplicate, it should be fixed.
        for binding in self.binder:
            if binding['name'] == name and widget_class == None:
                logger.warn(f"Key binding {name} already exists.")


        self.binder += [{
            'name': name,
            'category': category,
            'bind_func': bind_func, 
            'key': key, 
            'callback': callback, 
            'widget_class': widget_class, 
            'active': active, 
            'can_override': can_override }]

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
        
    def _app_triggers(self):
        ''' These are triggers that get fired on app events not key codes'''

        triggers = [{'name': '', 'key': '<<NotebookTabChanged>>', 'category': 'App triggers',
            'widget_class': None, 'active': True, 'can_override': False,
            'bind_func': self.app.bind, 
            'callback': lambda event: self.controller.view.tab_change(), 
            },
        ]
        
        for binding in triggers:
            self.register_binding(**binding)

    def _load_user_settings(self):
        ''' Loads the user key bindings from the config file. '''
        ... # Still to be implemented

    # It would be better and more efficient to unbind this when we dont need it.
    # Or perhaps just bind to the textbox. I'm not sure. But I'm sure its worth considering 
    def _syntax_highlighting(self):
        ''' These are the key bindings that are specific to the syntax highlighting. '''
        syntax_bindings = [
            {'name': 'Syntax: on keypress', 'key': '<Key>', 'category': 'Syntax',
                'widget_class': None, 'active': True, 'can_override': False,
                'bind_func': self.app.bind, 
                'callback': lambda event: self.controller.language.dynamic_syntax_formatting(event), 
                },

            # I think this is needed, but might be redundant. Need to check
            {'name': 'Syntax: on space', 'key': '<space>', 'category': 'Syntax',
                'widget_class': None, 'active': True, 'can_override': False,
                'bind_func': self.app.bind_all, 
                'callback': lambda event: self.controller.language.dynamic_syntax_formatting(event), 
                },
        
            {'name': 'Syntax: keypad enter', 'key': '<KP_Enter>', 'category': 'Syntax',
                'widget_class': None, 'active': True, 'can_override': False,
                'bind_func': self.app.bind, 
                'callback': lambda event: self.controller.language.dynamic_syntax_formatting(event),
                },

            {'name': 'Syntax: statis formatting', 'key': '<Alt-p>', 'category': 'Syntax',
                'widget_class': None, 'active': True, 'can_override': True,
                'bind_func': self.app.bind, 
                'callback': lambda event: self.controller.language.static_syntax_formatting(), 
                },
        ]

        for binding in syntax_bindings:
            self.register_binding(**binding)

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

            {'name': 'Close tab', 'key': '<Control-w>', 'category': 'File management',
                'bind_func': self.app.bind, 
                'callback': lambda event: self.controller.view.tabs.close_tab(), 
                },

            # Find entry overrides
            # Ctrl-o inserts a newline character by default. A second binding specific to the Text class overrides this.
            {'name': 'Open file', 'key': '<Control-o>', 'category': 'File management',
                'widget_class': 'Text',
                'bind_func': self.app.bind_class,
                'callback': lambda event: self.controller.file_system.open_file()},

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
             },

            # Linux uses Button-4 and Button-5 for the mouse wheel
            {'name': 'Increase Font', 'key': '<Control-Button-4>', 'category': 'Text editor',
             'widget_class': 'Text', 'active': True, 'can_override': False,
             'bind_func': self.app.bind_class,
             'callback': lambda event: self.controller.view.ui.font_size_bump(increase=True)
             },

            {'name': 'Decrease Font', 'key': '<Control-Button-5>', 'category': 'Text editor',
             'widget_class': 'Text', 'active': True, 'can_override': False,
             'bind_func': self.app.bind_class,
             'callback': lambda event: self.controller.view.ui.font_size_bump(increase=False)
             },

            # Windows uses <Mousewheel> and then the events have to be parsed
            {'name': 'Increase/Decrease Font', 'key': '<Control-MouseWheel>', 'category': 'Text editor',
             'widget_class': 'Text', 'active': True, 'can_override': False,
             'bind_func': self.app.bind_class,
             'callback': lambda event: self.controller.view.ui.parse_windows_mousewheel(event, callback=self.controller.view.ui.font_size_bump)
             },

            {'name': 'Delete line', 'key': '<Control-d>', 'category': 'Text editor',
                'widget_class': 'Text', 'active': True, 'can_override': True,
                'bind_func': self.app.bind_class, 
                'callback': lambda event: self.controller.view.textbox.editor.delete_line(), 
                },

            {'name': 'Duplicate line', 'key': '<Control-l>', 'category': 'Text editor',
                'widget_class': 'Text', 'active': True, 'can_override': True,
                'bind_func': self.app.bind_class, 
                'callback': lambda event: self.controller.view.textbox.editor.duplicate_line(), 
                },

            {'name': 'Move line up', 'key': '<Alt-Shift-Up>', 'category': 'Text editor',
                'widget_class': None, 'active': True, 'can_override': True,
                'bind_func': self.app.bind, 
                'callback': lambda event: self.controller.view.textbox.editor.move_line(direction=1), 
                },

            {'name': 'Move line down', 'key': '<Alt-Shift-Down>', 'category': 'Text editor',
                'widget_class': None, 'active': True, 'can_override': True,
                'bind_func': self.app.bind, 
                'callback': lambda event: lambda event: self.controller.view.textbox.editor.move_line(direction=-1), 
                },
        ]
        for binding in textbox_bindings:
            self.register_binding(**binding)

    def _assignable_bindings(self):
        ''' Key bindings are attached here. There is an important thing to know, 
            that they will be called in order from the class level up to 
            the app level. That means to override a key binding, you need to assign
            it at the class level and then return 'break' to stop the event from
            propagating up the levels. 
            
            These should all be user updatable key commands. Might be worth splitting them out at some point. 
            Or consolidating into a single function. Pros and cons to both. '''
        
        bindings = [ 
            # Settings window
            {'name': 'Open settings', 'key': '<Control-Key-comma>', 'category': 'Application settings',
                'widget_class': None, 'active': True, 'can_override': True,
                'bind_func': self.app.bind, 
                'callback': self.controller.view.open_settings_window, 
                },

            {'name': 'Increase font', 'key': '<Control-equal>', 'category': 'Text editor',
                'widget_class': None, 'active': True, 'can_override': True,
                'bind_func': self.app.bind, 
                'callback': lambda event: self.controller.view.ui.font_size_bump(increase=True), 
                },

            {'name': 'Decrease font', 'key': '<Control-minus>', 'category': 'Text editor',
                'widget_class': None, 'active': True, 'can_override': True,
                'bind_func': self.app.bind, 
                'callback': lambda event: self.controller.view.ui.font_size_bump(increase=False), 
                },

            {'name': 'Calculator', 'key': '<Alt-c>', 'category': 'Utilities',
                'widget_class': None, 'active': True, 'can_override': True,
                'bind_func': self.app.bind, 
                'callback': lambda event: self.controller.utilities.open_calculator(), 
                },

            {'name': 'Toggle theme', 'key': '<Alt-d>', 'category': 'Ui',
                'widget_class': 'Text', 'active': True, 'can_override': True,
                'bind_func': self.app.bind_class, 
                'callback': lambda event: self.controller.view.ui.toggle_theme(), 
                },

            {'name': 'Test theme', 'key': '<Alt-t>', 'category': 'Ui',
                'widget_class': 'Text', 'active': True, 'can_override': True,
                'bind_func': self.app.bind_class, 
                'callback': lambda event: self.controller.view.ui.test_theme(), 
                },

            {'name': 'Find', 'key': '<Control-f>', 'category': 'Text editor',
                'widget_class': None, 'active': True, 'can_override': True,
                'bind_func': self.app.bind, 
                'callback': lambda event: self.controller.view.toolbar.find_entry.focus(), 
                },

            {'name': 'Find next no focus', 'key': '<Control-g>', 'category': 'Text editor',
                'widget_class': None, 'active': True, 'can_override': True,
                'bind_func': self.app.bind, 
                'callback': lambda event: lambda event: self.controller.view.textbox.editor.find_text(
                    self.controller.view.toolbar.find_entry.get(), direction=1), 
                },
        
            {'name': 'Find prev no focus', 'key': '<Control-Shift-G>', 'category': 'Text editor',
                'widget_class': None, 'active': True, 'can_override': True,
                'bind_func': self.app.bind, 
                'callback': lambda event: self.controller.view.textbox.editor.find_text(
                    self.controller.view.toolbar.find_entry.get(), direction=-1), 
                },

            {'name': 'Python eval', 'key': '<Alt-e>', 'category': 'Python',
                'widget_class': None, 'active': True, 'can_override': True,
                'bind_func': self.app.bind, 
                'callback': lambda event: self.controller.utilities.eval_selection(), 
                },
        ]

        for binding in bindings:
            self.register_binding(**binding)