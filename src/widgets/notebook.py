from tkinter.ttk import Notebook


class NNotebook(Notebook):
    ''' A notebook with a name. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
    def _event(self, event:str) -> object:
        def callback(*_): # This is the function that is returned to the caller
            self.event_generate(event)
        return callback     