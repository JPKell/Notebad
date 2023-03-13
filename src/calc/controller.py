from tkinter     import Tk 
from tkinter.ttk import Style

from .model import Model
from .view  import View

class Calculator:
    def __init__(self, app:Tk, style:Style):
        self.app = app
        self.model = Model()    # Model does not know about controller
        self.view  = View(self, style) # View does. Pass the controller into view
        self._bind_keys()

    def main(self):
        self.view.main()

    def button_click(self, caption):
        result = self.model.calculate(caption)
        self.view.value_var = result
        self.view._update()

    def keyboard_click(self, key):
        if key in '0123456789':
            self.button_click(int(key))
        elif key in '+-*/=':
            self.button_click(key)


    def _bind_keys(self):
        self.view.bind('<Return>',      lambda event: self.keyboard_click('='))
        self.view.bind('<KP_Enter>',    lambda event: self.keyboard_click('='))
        self.view.bind('<Escape>',      lambda event: self.keyboard_click('C'))
        self.view.bind('<BackSpace>',   lambda event: self.keyboard_click('C'))
        self.view.bind('<Delete>',      lambda event: self.keyboard_click('C'))
        self.view.bind('<Key>',         lambda event: self.keyboard_click(str(event.char)))
