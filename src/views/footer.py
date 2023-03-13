from tkinter import Frame, Label

from conf import cf

class Footer(Frame):
    ''' Runs the status bar at the bottom of the screen. I would like to see this
        displaying useful information, but I'm not sure what that would be yet.
        Process run times, remote connections, etc. '''
    def __init__(self, view):
        super().__init__(view)
        self.pack(side='bottom', fill='x')
        self._make_label()

    def set_status(self, text) -> None:
        ''' Set the status bar text and reset it after the duration '''
        text = str(text)
        self.status.config(text=text)
        self.after(cf.status_bar_duration, self.scroll_text, text)

    def scroll_text(self, text:str) -> None:
        ''' Scrolls the text our of the status bar once the duration has passed '''
        if len(text) == 0 or not cf.status_bar_scrolling:
            self._reset_label()
        else:
            text = text[1:]
            self.status.config(text=text)
            self.after(100, self.scroll_text, text)

    # Private methods
    def _make_label(self) -> None:
        ''' Main constructor for the status bar '''
        self.status = Label(self, text=cf.status_bar_default_text, relief='flat', anchor='w')
        self.status.pack(expand=True, fill='x')

    def _reset_label(self, force=False) -> None:
        ''' Return status bar to default text. Force will override the freeze setting.'''
        if not cf.status_bar_freeze or force:
            self.status.config(text=cf.status_bar_default_text)