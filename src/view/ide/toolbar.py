from tkinter import IntVar, StringVar, SEL, SEL_FIRST, SEL_LAST

from modules.logging import Log
from widgets import NCheckbutton, NButton, NEntry, NLabel, NFrame, NText
from .editor import Editor


logger = Log(__name__)


class Toolbar(NFrame):
    ''' The toolbar appears above the tab titles and below the menubar.
        It is designed to house things like a find/searchbar '''
    def __init__(self, ide, editor: Editor, text: NText):
        super().__init__(ide)
        # Gather IDE objects
        self.ide = ide
        self.editor = editor
        self.text = text

        self.find_txt = StringVar(self)
        self._make_find_case_toggle()
        self._make_find_next_buttons()
        self._make_find_entry()
        self._make_find_label()

        self.find_entry.bind_all("<<FindFocus>>", lambda event: self.find_entry.focus_set())
        logger.debug("Toolbar init")

    # Private methods
    def _make_find_case_toggle(self):
        self.case_variable = IntVar()
        self.case_toggle = NCheckbutton(self, text="Aa", variable=self.case_variable, onvalue=1, offvalue=0,
                                       command=lambda: self.editor.set_find_case(self.case_variable.get()))
        self.case_toggle.setvar(value=1)   # Default to "Checked"
        self.case_toggle.pack(side="right", padx=2)

    def _make_find_next_buttons(self):
        self.find_next_btn = NButton(self, text="►", width=1, command=lambda: self.editor.find_text(self.find_entry.get(), direction=1))
        self.find_prev_btn = NButton(self, text="◄", width=1, command=lambda: self.editor.find_text(self.find_entry.get(), direction=-1))
        self.find_next_btn.pack(side="right", padx=2)
        self.find_prev_btn.pack(side="right", padx=0)

    def _make_find_entry(self) -> None:
        ''' Build the Find entry widget '''
        self.placeholder_txt = "Ctrl+f..."
        self.find_entry = NEntry(self, textvariable=self.find_txt)
        self.find_entry.pack(side="right", padx=4)
        self.find_entry.bind("<FocusIn>", self.find_entry_focus)
        self.find_entry.bind("<FocusOut>", self.find_entry_lose_focus)
        self.find_entry.insert(0, self.placeholder_txt)
        self.find_entry.configure(foreground='grey')

    def _make_find_label(self) -> None:
        ''' Label the Find entry widget '''
        self.find_label = NLabel(self, text="Find in tab:")
        self.find_label.pack(side="right")

    def get_current_text(self, *args):
        ''' Get the current text in the find entry and pass it along to the editor for processing textbox text '''
        current_txt = self.find_entry.get()
        self.editor.find_text(current_txt)

    def find_entry_focus(self, *args):
        ''' When the find entry widget gains focus, clear the
            placeholder text and update the foreground color to black '''
        if self.find_entry.get() == self.placeholder_txt:
            self.find_entry.delete(0, 'end')
            self.find_entry.configure(foreground='black')

        ''' If there's a selection in the textbox, insert it into the find entry on focus. 
            Otherwise, select all text in the find entry when focus is gained '''
        if self.text.tag_ranges(SEL):
            self.find_entry.delete(0, 'end')
            self.find_entry.insert(0, self.text.get(SEL_FIRST, SEL_LAST))
        else:
            self.find_entry.select_range(0, 'end')

    def find_entry_lose_focus(self, event):
        ''' When the find entry is blank and loses focus, add the placeholder text back in
            and set the foreground colour back to grey '''
        if self.find_entry.get() == "":
            self.find_entry.insert(0, self.placeholder_txt)
            self.find_entry.configure(foreground='grey')
