from tkinter import StringVar

from settings        import Configuration
from modules.logging import Log
from view.colors     import Themes
from widgets         import NFrame, NLabel, NText

cfg = Configuration()
logger = Log(__name__)

# TODO Make it listen for <<Change>> events and update the status bar

class TextFooter(NFrame):
    ''' Runs the status bar at the bottom of the screen. I would like to see this
        displaying useful information, but I'm not sure what that would be yet.
        Process run times, remote connections, etc. '''
    def __init__(self,parent, text: NText):
        logger.debug("Footer init")
        super().__init__(parent)       
        # Gather IDE objects
        self.text = text

        self.status_txt = StringVar(self, value=cfg.status_bar_default_text) 

        self._binds()
        self._make_labels()
        self._set_theme()
        self._grid()
        

    def set_status(self, text:str, revert=True) -> None:
        ''' Set the status bar text and optionally revert it after the duration '''
        old_txt = self.status_txt.get()
        self.status_txt.set(text)
        # If a blank string is passed, reset the status bar default text immediately
        if text == "" and revert:
            self.status_txt.set(cfg.status_bar_default_text)
        elif revert:
            self.after(cfg.status_bar_duration, self.status_txt.set, old_txt)
        logger.debug(f"Status bar set to: {text}")

    def update_cursor_pos(self, event) -> None:
        ''' Update the status bar position on custom <<Change>> event '''
        index = self.text.index('insert') 
        index = index.split('.')
        self.pos_lbl.config(text=f"ln {index[0]} col {index[1]} ")

    def update_selection_stats(self, event):
        ''' Update selection stats when <<Selection>> event is triggered '''
        # If there is no selection tk throws an error on selection get so bail early
        try:
            selection_text = self.text.selection_get()
        except:
            return
        lines = selection_text.count('\n')
        chars = len(selection_text)
        if lines + chars == 0:
            self.sel_lbl.config(text=' ')
        else:
            self.sel_lbl.config(text=f'(sel ln {lines} ch {chars})')
    ###
    # Private methods
    ###
    def _binds(self) -> None:
        ''' Bind events to methods '''
        self.text.bind('<<Change>>', self.update_cursor_pos)
        self.text.bind('<<Selection>>', self.update_selection_stats)
        self.bind_all('<<ThemeToggle>>',lambda event: self._set_theme())

    def _make_labels(self) -> None:
        ''' Main constructor for the status bar '''
        self.status   = NLabel(self, textvariable=self.status_txt, relief='flat', anchor='w')
        self.lang_lbl = NLabel(self, text="txt", relief='flat', anchor='e')
        self.pos_lbl  = NLabel(self, text="ln 1 col 0 ", relief='flat', anchor='e')
        self.sel_lbl  = NLabel(self, text="()", relief='flat', anchor='e')

    def _grid(self) -> None:
        ''' Grid the status bar '''
        self.columnconfigure(0, weight=1)
        self.status.grid(  row=0, column=0, padx=3, sticky='w')
        self.lang_lbl.grid(row=0, column=1, padx=3, sticky='e')
        self.pos_lbl.grid( row=0, column=2, padx=3, sticky='e')
        self.sel_lbl.grid( row=0, column=3, padx=3, sticky='e')

    def _set_theme(self) -> None:
        print("MARCO")
        if cfg.theme == 'forest-dark':
            colors = Themes.dark
        else:
            colors = Themes.light
        self.status.config(  background=colors.background, foreground=colors.foreground)
        self.pos_lbl.config( background=colors.background, foreground=colors.syn_orange)
        self.lang_lbl.config(background=colors.background, foreground=colors.syn_yellow)
        self.sel_lbl.config( background=colors.background, foreground=colors.syn_orange)

        return