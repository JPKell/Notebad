from tkinter.ttk import Scrollbar


class NVertScrollbar(Scrollbar):
    ''' A vertical scrollbar with a name. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, orient='vertical', **kwargs)


class NHorizScrollbar(Scrollbar):
    ''' A horizontal scrollbar with a name. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, orient='horizontal', **kwargs)

        