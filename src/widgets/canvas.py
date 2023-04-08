from tkinter import Canvas

class NCanvas(Canvas):
    ''' This is a wrapper for the tkinter Canvas. It adds some
        extra functionality and makes it easier to use. '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
