from tkinter import Toplevel
from tkinter.ttk import Frame, Labelframe, Label

class NFrame(Frame):
    ''' A vanilla frame with a name.'''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
    def _event(self, event:str='<<DefaultEvent>>') -> object:
        def callback(): # This is the function that is returned to the caller
            self.event_generate(event)
        return callback 

class NLabelframe(Labelframe):
    ''' A labelframe with a name. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        

class NTabFrame(Frame):
    ''' A frame with a name. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.tab_title = kwargs.get('tab_title', '')
        self.tab_tk_name = kwargs.get('tab_tk_name', '')
        self.tab_save_on_close = kwargs.get('tab_save_on_close', False)

    def _event(self, event:str='<<DefaultEvent>>') -> object:
        def callback(): # This is the function that is returned to the caller
            self.event_generate(event)
        return callback     


class NToplevel(Toplevel):
    ''' A toplevel with a name. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
    def _event(self, event:str='<<DefaultEvent>>') -> object:
        def callback(): # This is the function that is returned to the caller
            self.event_generate(event)
        return callback 