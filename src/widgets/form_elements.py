from tkinter import Listbox
from tkinter.ttk import Button, Checkbutton, Combobox, Entry, Label, Labelframe, Radiobutton, Scale, Spinbox


class NButton(Button):
    ''' A button with a name. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)


class NCheckbutton(Checkbutton):
    ''' A checkbutton with a name. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        

class NCombobox(Combobox):
    ''' A combobox with a name. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        

class NEntry(Entry):
    ''' An entry with a name. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        

class NLabel(Label):
    ''' A label with a name. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        

class NLabelframe(Labelframe):
    ''' A labelframe with a name. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        

class NListbox(Listbox):
    ''' A listbox with a name. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        

class NRadiobutton(Radiobutton):
    ''' A radiobutton with a name. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        

class NScale(Scale):
    ''' A scale with a name. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        

class NSpinbox(Spinbox):
    ''' A spinbox with a name. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        