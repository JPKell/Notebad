from settings import Configuration
from modules.logging import Log

cfg = Configuration()
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
        self.app.bind("<Control-Shift-s>", lambda event: self.controller.file_system.save_as_file())

        # Settings window
        self.app.bind("<Control-Key-comma>", self.controller.view.open_settings_window)

        # UI management
        self.app.bind("<Control-equal>", lambda event: self.controller.view.ui.font_size_bump(increase=True))
        self.app.bind("<Control-minus>", lambda event: self.controller.view.ui.font_size_bump(increase=False))
        self.app.bind("<Alt-c>", lambda event: self.controller.utilities.open_calculator())

        # Find entry overrides
        self.app.bind_class("Entry", "<Return>",
                            lambda event: self.controller.view.textbox.editor.find_text(
                                self.controller.view.toolbar.find_entry.get()))
        self.app.bind_class("Entry", "<Shift-Return>",
                            lambda event: self.controller.view.textbox.editor.find_text(
                                self.controller.view.toolbar.find_entry.get(), direction=-1))
        self.app.bind_class("Entry", "<Escape>", lambda event: self.controller.view.textbox.focus())

        # Textbox overrides
        self.app.bind_class("Text", "<Alt-d>", lambda event: self.controller.view.ui.toggle_theme())
        self.app.bind_class("Text", "<Control-d>", lambda event: self.controller.view.textbox.editor.delete_line())
        self.app.bind_class("Text", "<Control-l>", lambda event: self.controller.view.textbox.editor.duplicate_line())
        self.app.bind_class("Text", "<Control-z>", lambda event: self.controller.view.textbox.history.undo())
        self.app.bind_class("Text", "<Control-y>", lambda event: self.controller.view.textbox.history.redo())
        self.app.unbind_all("<Tab>")    # Unbind the default tab key for all widgets before overriding it
        self.app.bind_class("Text", "<Tab>", lambda event: self.controller.view.tabs.textbox.editor.add_indent(), add=False)
        self.app.bind_class("Text", "<Escape>", lambda event: self.controller.view.tabs.textbox.delete_tags_by_name("find"))
        self.app.bind("<Alt-Shift-Up>", lambda event: self.controller.view.textbox.editor.move_line(direction=1))
        self.app.bind("<Alt-Shift-Down>", lambda event: self.controller.view.textbox.editor.move_line(direction=-1))

        # Textbox management
        self.app.bind("<Control-a>", lambda event: self.controller.view.tabs.textbox.cursor.select_all())
        self.app.bind("<Control-v>", lambda event: self.controller.view.textbox.clipboard.paste_text())
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