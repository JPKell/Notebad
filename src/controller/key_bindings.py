from modules.logging import Log

logger = Log(__name__)

class KeyBindings:
    ''' This class is responsible for binding all the key bindings to the self.app. 
        It is called from the app class. '''
    def __init__(self, controller):
        self.controller = controller
        self.app = self.controller.app
        self.bind_keys()
        logger.debug("Key bindings initialized")

    def bind_keys(self):
        ''' Key bindings are attached here. There is an important thing to know, 
            that they will be called in order from the class level up to 
            the app level. That means to override a key binding, you need to assign
            it at the class level and then return 'break' to stop the event from
            propagating up the levels. '''
        # File management
        self.app.bind("<Control-n>", lambda event: self.controller.file_system.new_file())
        self.app.bind("<Control-o>", lambda event: self.controller.file_system.open_file())
        self.app.bind("<Control-s>", lambda event: self.controller.file_system.save_file())
        self.app.bind("<Control-S>", lambda event: self.controller.file_system.save_as_file())  # Ctrl+Shift+s

        # UI management
        self.app.bind("<Control-equal>", lambda event: self.controller.view.ui.font_size_bump(increase=True))
        self.app.bind("<Control-minus>", lambda event: self.controller.view.ui.font_size_bump(increase=False))
        self.app.bind("<Alt-c>", lambda event: self.controller.utilities.open_calculator())


        # Textbox overides #
        self.app.bind_class("Text", "<Control-d>", lambda event: self.controller.view.ui.toggle_theme())
        self.app.bind_class("Text", "<Control-z>", lambda event: self.controller.view.textbox.history.undo())
        self.app.bind_class("Text", "<Control-y>", lambda event: self.controller.view.textbox.history.redo())
        self.app.unbind_all("<Tab>")    # Unbind the default tab key for all widgets before overriding it
        self.app.bind_class("Text", "<Tab>", lambda event: self.controller.view.tabs.add_indent(), add=False)

        # Textbox management
        self.app.bind("<Control-a>", lambda event: self.controller.view.tabs.textbox.cursor.select_all())
        self.app.bind("<Control-v>", lambda event: self.controller.view.textbox.clipboard.paste_text())
        self.app.bind("<Control-f>", lambda event: self.controller.view.find())
        
    

        # Syntax highlighting
        self.app.bind("<Key>", lambda event: self.controller.language.format_code(event))
        self.app.bind_all("<space>", lambda event: self.controller.language.format_code(event))
        self.app.bind_all("<Return>", lambda event: self.controller.language.format_code(event))

        self.app.bind("<KP_Enter>", lambda event: self.controller.language.format_code(event))

        # Tab management
        self.app.bind("<<NotebookTabChanged>> ", lambda event: self.controller.view.tab_change())
        self.app.bind("<Control-w>",    lambda event: self.controller.view.tabs.close_tab())
        
        # Clipboard management
        self.app.bind("<Alt-e>", lambda event: self.controller.utilities.eval_selection())

        # DEVELOPMENT ONLY
        self.app.bind("<Alt-p>", lambda event: self.controller.language.capitalize_syntax(event))


        ###
        # Various tk keybindings that exist by default
        # 
        # <Control-p> previous line
        ###