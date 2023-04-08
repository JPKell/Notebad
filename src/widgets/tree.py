from tkinter.ttk import Treeview

from widgets import NFrame, NVertScrollbar, NHorizScrollbar

class NTreeview(Treeview):
    ''' A treeview with a name. '''
    def __init__(self, parent, **kwargs):
        self.frame = NFrame(parent)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        super().__init__(self.frame, **kwargs)
        self._build_ui_elements()

    ###
    # Overridden methods
    ###
    def grid(self, **kwargs):
        ''' Grid the frame not the treeview'''
        self.frame.grid(**kwargs)
        self.v_scroll.grid(row=0, column=1, sticky='ns')
        self.h_scroll.grid(row=1, column=0, sticky='ew')
        super().grid(row=0, column=0, sticky='nsew')


    ###
    # Private methods
    ###

    def _build_ui_elements(self):
        ''' Build the UI elements '''

        # Build the scrollbars
        self.v_scroll = NVertScrollbar(self.frame)
        self.h_scroll = NHorizScrollbar(self.frame)
        self.v_scroll.config(command=self.yview)
        self.h_scroll.config(command=self.xview)
        self.configure(
            xscrollcommand=self.h_scroll.set,
            yscrollcommand=self.v_scroll.set,
            )
        
    