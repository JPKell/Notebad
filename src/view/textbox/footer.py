from tkinter import Frame, Label, StringVar

from settings import Configuration
from modules.logging import Log

cfg = Configuration()
logger = Log(__name__)

class Footer(Frame):
    ''' Runs the status bar at the bottom of the screen. I would like to see this
        displaying useful information, but I'm not sure what that would be yet.
        Process run times, remote connections, etc. '''
    def __init__(self, frm, view):
        super().__init__(frm, height=30)
        self.view = view
        self.pack(side='bottom', fill='x')
        self.status_txt = StringVar(self, value=cfg.status_bar_default_text)
        self._make_label()
        self._make_selection_labels()
        self._make_position_labels()
        self._make_language_label()
        logger.debug("Footer init")

    def set_status(self, text, revert=True) -> None:
        ''' Set the status bar text and optionally revert it after the duration '''
        text = str(text)
        old_txt = self.status_txt.get()
        self.status_txt.set(text)
        if revert:
            self.after(cfg.status_bar_duration, self.status_txt.set, old_txt)
        logger.debug(f"Status bar set to: {text}")

    def update_cursor_pos(self) -> None:
        ''' Update the status bar position on custom <<Change>> event '''
        textbox = self.view.textbox
        ## Cursor stats
        index = textbox.index('insert') 
        index = index.split('.')
        self.pos_lbl.config(text=f"ln {index[0]} col {index[1]} ")

    def update_selection_stats(self, selection_text):
        ''' Update selection stats when <<Selection>> event is triggered '''
        lines = selection_text.count('\n')
        chars = len(selection_text)
        if lines + chars == 0:
            self.sel_lbl.config(text=' ')
        else:
            self.sel_lbl.config(text=f'(sel ln {lines} ch {chars})')

    def update_find_results(self):
        ''' Show the number of results returned from the find entry '''
        pass

    # Private methods
    def _make_label(self) -> None:
        ''' Main constructor for the status bar '''
        self.status = Label(self, textvariable=self.status_txt, relief='flat', anchor='w')
        self.status.pack(fill='x')

    def _make_selection_labels(self):
        self.sel_lbl = Label(self.status, text="()", relief='flat', anchor='e')
        self.sel_lbl.pack(side='right')

    def _make_position_labels(self):
        self.pos_lbl = Label(self.status, text="ln 1 col 0 ", relief='flat', anchor='e', padx=10)
        self.pos_lbl.pack(side='right')

    def _make_language_label(self):
        self.lang_lbl = Label(self.status, text="python", relief='flat', anchor='e')
        self.lang_lbl.pack(side='right')

    def _reset_label(self, force=False) -> None:
        ''' Return status bar to default text. Force will override the freeze setting.'''
        if not cfg.status_bar_freeze or force:
            self.status.config(text=cfg.status_bar_default_text)