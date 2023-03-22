from tkinter import Frame, Label, StringVar

from modules.logging import Log

logger = Log(__name__)

class Footer(Frame):
    ''' Runs the status bar at the bottom of the screen. I would like to see this
        displaying useful information, but I'm not sure what that would be yet.
        Process run times, remote connections, etc. '''
    def __init__(self, frm, view):
        super().__init__(frm, height=30)
        self.view = view
        self.conf = view.conf
        self.pack(side='bottom', fill='x')
        self.status_txt = StringVar(self, value=self.conf.status_bar_default_text)
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
            self.after(self.conf.status_bar_duration, self.status_txt.set, old_txt)
        logger.debug(f"Status bar set to: {text}")

    def update_pos(self) -> None:
        ''' Update the status bar position and selection every 100ms '''
        textbox = self.view.textbox
        ## Cursor stats
        index = textbox.index('insert') 
        index = index.split('.')
        self.pos_lbl.config(text=f"ln {index[0]} col {index[1]} ")

        ## Selection stats
        selection = textbox.editor.get_selection()
        lines = selection.count('\n')
        chars = len(selection)
        if lines + chars == 0:
            self.sel_lbl.config(text=' ')
        else:
            self.sel_lbl.config(text=f'(sel ln {lines} ch {chars})')
        
        ## This logger if very verbose and should be used when required only.
        # Times it might be required:
        #   - When checking that the update is turned off when the textbox is not focused
        #   - When debugging the status bar
        # logger.verbose(f"Status bar updated: {self.pos_lbl['text']} {self.sel_lbl['text']}")
        if textbox.is_focus:
            # Update the status bar selection every 200ms
            self.after(200, self.update_pos)
    
    
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
        if not self.conf.status_bar_freeze or force:
            self.status.config(text=self.conf.status_bar_default_text)