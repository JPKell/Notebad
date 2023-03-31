from tkinter import Frame, Text, Toplevel


class KeyCommandList(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.keybindings = master.controller.key_bindings
        self.root = Frame(self)
        self.geometry("450x900")
        self.root.pack()
        self.list_canvas()

    def list_canvas(self):
        self.txt = Text(self.root, width=400, height=200, font=('courier', 10))
        
        kb = self.keybindings.binder

        categories = set([d['category'] for d in kb])

        self.txt.insert(1.0, "Key Commands\n")
        y = 2
        for category in categories:
            key_list = [ k for k in kb if k['category'] == category ]

            self.txt.insert(f'{y}.0', f'\n{category}\n\n')
            y += 2

            for key_dict in key_list:
                self.txt.insert(f'{y}.0', f"{key_dict['name']:30} - {key_dict['key']}\n")
                y += 1

        self.txt.config(state='disabled')
        self.txt.pack()