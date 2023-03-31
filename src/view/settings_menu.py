from tkinter import Toplevel, Button, Frame, LabelFrame, Checkbutton, IntVar, StringVar, Label
from tkinter.ttk import Combobox
from settings import Configuration

cfg = Configuration()


class SettingsDialog(Toplevel):
    ''' Settings Toplevel widget. Allows the user to change and save their personal settings.
        This class will reference the Configuration class and update the users personal.cf file '''
    def __init__(self, view):
        super().__init__(view)
        self.view = view
        #self.geometry('300x100')
        self.resizable(False, False)
        self.title("Settings")
        self._make_startup_frame()
        self._make_textbox_frame()
        self.grab_set()     # Set focus on settings window and stop user from interacting with the root window
        self.focus()

    def _make_startup_frame(self):
        ''' Stores widgets for changing startup settings '''
        self.startup_frame = LabelFrame(self, text="Startup")
        self.startup_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Theme settings
        self.theme_label = Label(self.startup_frame, text="Default Theme")
        self.theme_value = StringVar()
        self.theme_selection = Combobox(self.startup_frame, textvariable=self.theme_value)
        self.theme_selection.state(["readonly"])   # Only allow selection from predefined list
        self.theme_selection["values"] = ("Light", "Dark")
        self.theme_selection.current(self.theme_selection['values'].index(cfg.default_theme.capitalize()))
        self.theme_selection.bind("<<ComboboxSelected>>", lambda event: cfg.save_personal_settings(default_theme='"%s"' % self.theme_value.get().lower()))
        self.theme_label.grid(column=0, row=0, sticky="w", padx=10, pady=10)
        self.theme_selection.grid(column=1, row=0, sticky="e", padx=10, pady=10)

        # Fullscreen settings
        self.fullscreen_toggle = IntVar()
        self.start_fullscreen = Checkbutton(self.startup_frame, variable=self.fullscreen_toggle,
                                            onvalue=True, offvalue=False, text="Start Fullscreen",
                                            command=lambda: cfg.save_personal_settings(start_fullscreen=self.fullscreen_toggle.get()))
        self.start_fullscreen.grid(column=0, row=1, sticky="ew", padx=10, pady=10)

    def _make_textbox_frame(self):
        ''' Stores widgets for textbox appearance settings. '''
        self.textbox_frame = LabelFrame(self, text="Textbox")
        self.textbox_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.font_size_label = Label(self.textbox_frame, text="Size")
        self.font_size_selection = StringVar()
        self.font_size = Combobox(self.textbox_frame, textvariable=self.font_size_selection, width=4)
        self.font_size["values"] = (6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 25, 29, 36, 48, 64)
        self.font_size.current(6)       # Default value
        self.font_size.bind("<<ComboboxSelected>>", lambda event: cfg.save_personal_settings(font_size=int(self.font_size_selection.get())))
        self.font_size_label.grid(column=1, row=0, sticky="w", padx=10, pady=10)
        self.font_size.grid(column=1, row=1, sticky="e", padx=10, pady=10)

        self.font_family_label = Label(self.textbox_frame, text="Font Family")
        self.font_family_selection = StringVar()
        self.font_family = Combobox(self.textbox_frame, textvariable=self.font_family_selection, state='readonly')
        self.font_family["values"] = ('Cascadia Mono', 'Cascadia Mono SemiBold', 'Cascadia Mono SemiLight', 'Consolas', 'Courier New', 'DejaVu Sans Mono', 'Fixedsys', 'Lucida Console', 'Terminal')
        self.font_family.current(self.font_family["values"].index(cfg.program_font))        # Default value
        self.font_family.bind("<<ComboboxSelected>>", lambda event: cfg.save_personal_settings(program_font='"%s"' % self.font_family.get()))
        self.font_family_label.grid(column=0, row=0, sticky='w', padx=10, pady=10)
        self.font_family.grid(column=0, row=1, sticky='w', padx=10, pady=10)
