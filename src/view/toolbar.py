import tkinter
from tkinter import Frame, StringVar, Entry, Label
from modules.logging import Log

logger = Log(__name__)


class Toolbar(Frame):
    ''' The toolbar appears above the tab titles and below the menubar.
        It is designed to house things like a find/searchbar '''
    def __init__(self, view):
        super().__init__(view, height=30)   #, bg="red")  # Red background for visibility while testing
        self.view = view
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
        if self.find_entry.get() == self.placeholder_txt:
            self.find_entry.delete(0, 'end')
            self.find_entry.configure(fg='black')

        ''' If there's a selection in the textbox, insert it into the find entry on focus. 
            Otherwise, select all text in the find entry when focus is gained '''
        if self.view.textbox.tag_ranges(tkinter.SEL):
            self.find_entry.delete(0, 'end')
            self.find_entry.insert(0, self.view.textbox.get(tkinter.SEL_FIRST, tkinter.SEL_LAST))
        else:
            self.find_entry.select_range(0, 'end')

    def find_entry_lose_focus(self, event):
        ''' When the find entry is blank and loses focus, add the placeholder text back in
            and set the foreground colour back to grey '''
        if self.find_entry.get() == "":
            self.find_entry.insert(0, self.placeholder_txt)
            self.find_entry.configure(fg='grey')
