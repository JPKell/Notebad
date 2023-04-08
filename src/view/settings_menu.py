from tkinter import IntVar, StringVar


from settings import Configuration
from modules.logging import Log
from widgets import NButton, NCheckbutton, NFrame, NLabel, NLabelframe, NListbox, NScale, NSpinbox, NToplevel

logger = Log(__name__)
cfg = Configuration()


class SettingsDialog(NToplevel):
    ''' Settings Toplevel widget. Allows the user to change and save their personal settings.
        This class will reference the Configuration class and update the users personal.cf file.
        All the settings are created as different objects and displayed inside a LabelFrame
        widget in this class. '''
    def __init__(self, view):
        super().__init__(view)
        self.view = view
        self.resizable(False, False)
        self.title("Settings")
        self.rowconfigure(0, weight=2)      # Give "weight" to certain rows or columns when laying out the grid
        self.rowconfigure(1, weight=1)
        self._make_settings_selection()
        self._make_buttons()
        self._make_settings_frame()
        self._build_layout()
        self.grab_set()     # Set focus on settings window and stop user from interacting with the root window
        self.setting_selection.focus()

    def update_settings_frame(self, *args):
        ''' Take the current setting selection and update the right-hand frame with it. '''
        self.general_settings = GeneralSettings(self.cur_settings_frame)
        self.general_settings.grid(column=0, row=0, sticky='nesw', padx=10, pady=10)

    def save_settings(self):
        ''' Save the current settings section to the personal.cf file '''
        pass

    def _make_settings_selection(self):
        ''' Settings selection lets us divide up the settings into related groups. '''
        self.settings_sections = ["General Settings", "Font Settings", "Colours/Appearance", "Keybindings"]
        self.settings_list = StringVar(value=self.settings_sections)
        self.setting_selection = NListbox(self, width=20, height=10, listvariable=self.settings_list)
        self.setting_selection.selection_set(0)     # Default to "General Settings" section
        self.setting_selection.bind("<<ListboxSelect>>", self.update_settings_frame)

    def _make_buttons(self):
        ''' Make the usual "Apply" and "Close" buttons. '''
        self.btn_frame = NFrame(self)
        self.apply_btn = NButton(self.btn_frame, text="Apply", width=20, command=self.save_settings)
        self.close_btn = NButton(self.btn_frame, text="Close", width=20, command=self.destroy)

        self.apply_btn.grid(column=0, row=1, sticky='ew', padx=5, pady=5)
        self.close_btn.grid(column=0, row=2, sticky='ew', padx=5, pady=5)

    def _make_settings_frame(self):
        ''' This frame is fixed in size and allows the user to view different
            settings sections. Each settings section is an object with its own widgets and layout '''
        self.cur_settings_frame = NFrame(self, width=450, height=350)
        self.update_settings_frame()

    def _build_layout(self):
        ''' Layout the widgets using the grid layout manager '''
        self.setting_selection.grid(column=0, row=0, sticky='nesw', padx=5, pady=12)
        self.btn_frame.grid(column=0, row=1, sticky='esw')
        self.cur_settings_frame.grid(column=1, row=0, rowspan=2, sticky='nesw', padx=5, pady=5)
        self.cur_settings_frame.grid_propagate(0)       # Stops frame from resizing to it's contents


class GeneralSettings(NFrame):
    '''
        General Settings include:
            - Start in Fullscreen y/N
            - Startup window size (if not starting in fullscreen already)
            - Factory Reset ALL settings - Deletes the users personal.cf file
                                           so they can start again.

        Add to the list whatever should be under this category.
    '''
    def __init__(self, view):
        super().__init__(view)
        self.view = view
        # self.screen_layout_frame = LabelFrame(self, text=" Fullscreen / Program Geometry ")
        self.reset_btn_frame = NLabelframe(self, text=" Reset All Settings: ")
        self._make_fullscreen_toggle()
        self._make_default_size_options()
        self._make_factory_reset_btn()
        self.reset_btn_frame.grid(column=0, row=1, sticky='nesw', padx=5, pady=5)

    def update_screen_settings(self):
        if self.fullscreen_toggle.get():
            self.screen_width.configure(state='disabled')
            self.screen_height.configure(state='disabled')
        else:
            self.screen_width.configure(state='normal')
            self.screen_height.configure(state='normal')

    def _make_fullscreen_toggle(self):
        self.fullscreen_toggle = IntVar()
        self.fullscreen_checkbtn = NCheckbutton(self, text="Start Fullscreen",
                                               variable=self.fullscreen_toggle,
                                               onvalue=True, offvalue=False,
                                               command=self.update_screen_settings)
        self.fullscreen_checkbtn.grid(column=0, row=0, sticky='nesw', padx=5, pady=5)

    def _make_default_size_options(self):
        ''' Set the default window size when opening the program. Currently set to max out at 8k. '''
        self.wxh_label = NLabel(self, text="Set the width and height for the program window on startup:")
        self.width_label = NLabel(self, text="Program Window Width:")
        self.height_label = NLabel(self, text="Program Window Height:")

        self.width_value = StringVar()
        self.height_value = StringVar()
        self.screen_width = NSpinbox(self, from_=cfg.min_size[0], to=7680, increment=1, textvariable=self.width_value, width=4)
        self.screen_height = NSpinbox(self, from_=cfg.min_size[1], to=4320, increment=1, textvariable=self.height_value, width=4)

        # Set the default values to display
        config_geometry = cfg.geometry.split("x")
        self.screen_width.set(config_geometry[0])
        self.screen_height.set(config_geometry[1])

        self.wxh_label.grid(column=0, row=1, columnspan=2, sticky='nesw', padx=5, pady=5)
        self.width_label.grid(column=0, row=2, sticky='e', padx=5, pady=5)
        self.height_label.grid(column=0, row=3, sticky='e', padx=5, pady=5)
        self.screen_width.grid(column=1, row=2, sticky='w', padx=5, pady=5)
        self.screen_height.grid(column=1, row=3, sticky='w', padx=5, pady=5)

    def _make_factory_reset_btn(self):
        self.reset_btn = NButton(self.reset_btn_frame, text="Delete All Settings", bg="#aa0000", command=cfg.delete_user_settings)
        self.reset_btn.grid(column=0, row=0, columnspan=2, sticky='nesw', padx=20, pady=20)


class FontSettings(NFrame):
    ''' Contains all widgets needed for updating font settings. Including font-family,
        font-size and an editable Text widget that updates to show the selected font. '''
    def __init__(self, view):
        super().__init__(view)
        self.view = view
