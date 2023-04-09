import os, pathlib

from tkinter import Toplevel
from tkinter.ttk import Frame, Labelframe, Label

from settings import Configuration

cfg = Configuration()

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
        self._file_name = kwargs.get('file_name', '') # Name of the file
        self._path_obj  = os.PathLike           # Path object of the file   
        self._has_focus = False                 # Reduce the number of events and pause loops
        
        self._tab_title = kwargs.get('tab_title', '') 
        self.tab_save_on_close = kwargs.get('tab_save_on_close', False)
        self._tab_tk_name = None

    ###            ###
    # Tab properties #
    ###            ###
    @property
    def tab_title(self) -> str:
        return self._tab_title
    
    @tab_title.setter
    def tab_title(self, tab_title:str) -> None:
        ''' Updating the tab title will also update the tab name in the parent widget '''
        self._tab_title = tab_title
        
        # If no tab tk name is set, then we can't update the tab title
        if self.tab_tk_name:
            self._set_titles()

    @property
    def tab_tk_name(self) -> str:
        return self._tab_tk_name
    
    @tab_tk_name.setter
    def tab_tk_name(self, tab_tk_name:str) -> None:
        ''' Updating the tab tk name will also update the tab name in the parent widget '''
        self._tab_tk_name = tab_tk_name
        self._set_titles()

    @property
    def has_focus(self) -> bool:
        return self._has_focus
    
    @has_focus.setter
    def has_focus(self, has_focus:bool) -> None:
        # Turn on any of the items in the event loop
        self._has_focus = has_focus
    ###             ###
    # File properties #
    ###             ###

    @property
    def file_name(self) -> str:
        return self._file_name
    
    @file_name.setter
    def file_name(self, file_name:str) -> None:
        ''' Updating the filename will also update the tab name '''
        self._file_name = file_name
        self.tab_title = file_name + ' *' if self.tab_save_on_close else ''

    @property
    def full_path(self) -> os.PathLike:
        return self._path_obj
    
    @full_path.setter
    def full_path(self, path_obj:pathlib.Path | str) -> None:
        ''' Updating the full path will also update the file name and path '''
        if isinstance(path_obj, str):
            path_obj = pathlib.Path(path_obj)
        self._path_obj = path_obj
        self._file_name = path_obj.name
        self._tab_title = path_obj.name
        self._set_titles()

    @property
    def file_path(self) -> os.PathLike:
        return os.path.dirname(str(self._path_obj))
    
    ###
    # Private methods
    ###

    def _event(self, event:str) -> object:
        def callback(*_): # This is the function that is returned to the caller
            self.event_generate(event)
        return callback   

    def _set_titles(self) -> None:
        ''' Set the tab title and the app title '''
        parent_widget = self.nametowidget(self.winfo_parent())
        parent_widget.tab(self.tab_tk_name, text=self._tab_title)

        # Get the root Tk window
        root = self.winfo_toplevel()
        root.title(f'{self.tab_title} - {cfg.app_title}')


class NToplevel(Toplevel):
    ''' A toplevel with a name. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
    def _event(self, event:str) -> object:
        def callback(): # This is the function that is returned to the caller
            self.event_generate(event)
        return callback 