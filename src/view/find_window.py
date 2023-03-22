from tkinter import Toplevel, Frame


class FindWindow(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.root = Frame(self)
        self.geometry("100x100")
        self.root.pack()