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
        self._tab_title = kwargs.get('tab_title', '') 
        self.tab_save_on_close = kwargs.get('tab_save_on_close', False)
        self._tab_tk_name = None

    ### Properties ###
    @property
    def tab_title(self) -> str:
        return self._tab_title
    
    @tab_title.setter
    def tab_title(self, tab_title:str) -> None:
        ''' Updating the tab title will also update the tab name in the parent widget '''
        self._tab_title = tab_title
        
        # If no tab tk name is set, then we can't update the tab title
        if self.tab_tk_name:
            parent_widget = self.nametowidget(self.winfo_parent())
            parent_widget.tab(self.tab_tk_name, text=tab_title)

    @property
    def tab_tk_name(self) -> str:
        return self._tab_tk_name
    
    @tab_tk_name.setter
    def tab_tk_name(self, tab_tk_name:str) -> None:
        ''' Updating the tab tk name will also update the tab name in the parent widget '''
        self._tab_tk_name = tab_tk_name
        parent_widget = self.nametowidget(self.winfo_parent())
        parent_widget.tab(self.tab_tk_name, text=self._tab_title)
        print(self.tab_tk_name,'G', self._tab_title)


    def _event(self, event:str) -> object:
        def callback(*_): # This is the function that is returned to the caller
            self.event_generate(event)
        return callback   


class NToplevel(Toplevel):
    ''' A toplevel with a name. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
    def _event(self, event:str) -> object:
        def callback(): # This is the function that is returned to the caller
            self.event_generate(event)
        return callback 