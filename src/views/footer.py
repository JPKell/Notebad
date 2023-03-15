from tkinter import Frame, Label, StringVar

from conf import cf

class Footer(Frame):
    ''' Runs the status bar at the bottom of the screen. I would like to see this
        displaying useful information, but I'm not sure what that would be yet.
        Process run times, remote connections, etc. '''
    def __init__(self, view):
        super().__init__(view, height=30)
        self.view = view
        self.pack(side='bottom', fill='x')
        self.status_txt = StringVar(self, value=cf.status_bar_default_text)
        self._make_label()
        self._make_position_labels()

    def set_status(self, text, revert=True) -> None:
        ''' Set the status bar text and optionally revert it after the duration '''
        text = str(text)
        old_txt = self.status_txt.get()
        self.status_txt.set(text)
        if revert:
            self.after(cf.status_bar_duration, self.status_txt.set, old_txt)

    def update_pos(self) -> None:
        ''' Update the cursor index on the footer '''
        index = self.view.textbox.index('insert') 
        index = index.split('.')
        self.pos_lbl.config(text=f"ln {index[0]} col {index[1]} ")

    # Private methods
    def _make_label(self) -> None:
        ''' Main constructor for the status bar '''
        self.status = Label(self, textvariable=self.status_txt, relief='flat', anchor='w')
        self.status.pack(expand=True, fill='x', side='bottom')

    def _make_position_labels(self):
        self.pos_lbl = Label(self.status, text="ln 1 col 0 ", relief='flat', anchor='e')
        self.pos_lbl.pack(side='right')

    def _reset_label(self, force=False) -> None:
        ''' Return status bar to default text. Force will override the freeze setting.'''
        if not cf.status_bar_freeze or force:
            self.status.config(text=cf.status_bar_default_text)