from tkinter.ttk import Notebook


class NNotebook(Notebook):
    ''' A notebook with a name. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
