from tkinter import Frame, StringVar, Entry, Label
from modules.logging import Log

logger = Log(__name__)


class Toolbar(Frame):
    ''' The toolbar appears above the tab titles and below the menubar.
        It is designed to house things like a find/searchbar '''
    def __init__(self, frm):
        super().__init__(frm, height=30)   #, bg="red")  # Red background for visibility while testing
        self.pack(side='top', fill='x')
        self.find_txt = StringVar(self)
        self._make_find_entry()
        self._make_find_label()
        logger.debug("Toolbar init")

    # Private methods
    def _make_find_entry(self) -> None:
        ''' Build the Find entry widget '''
        self.placeholder_txt = "Ctrl+f..."
        self.find_entry = Entry(self, textvariable=self.find_txt)
        self.find_entry.pack(side="right", padx=4)
        self.find_entry.bind("<FocusIn>", self.find_entry_focus)
        self.find_entry.bind("<FocusOut>", self.find_entry_lose_focus)
        self.find_entry.insert(0, self.placeholder_txt)
        self.find_entry.configure(fg='grey')

    def _make_find_label(self) -> None:
        ''' Label the Find entry widget '''
        self.find_label = Label(self, text="Find in tab:")
        self.find_label.pack(side="right")

    def find_entry_focus(self, event):
        ''' When the find entry widget gains focus, clear the
            placeholder text and update the foreground color to black '''
        '''
        * Get the current text and compare it to the placeholder text
        * If current text matches the placeholder text then clear the text
        * User config should have 3 settings (in priority order):
            - Insert selected text from current Tab/Textbox
            - Insert clipboard text 
            - Clear all text on focus
        * Check user config settings and manipulate entry widget accordingly
        '''
        if self.find_entry.get() == self.placeholder_txt:
            self.find_entry.delete(0, 'end')
            self.find_entry.configure(fg='black')

    def find_entry_lose_focus(self, event):
        if self.find_entry.get() == "":
            self.find_entry.insert(0, self.placeholder_txt)
            self.find_entry.configure(fg='grey')
