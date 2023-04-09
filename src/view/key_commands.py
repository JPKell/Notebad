from widgets import NFrame, NText, NToplevel

class KeyCommandList(NToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.root = NFrame(self)
        self.geometry("550x900")
        self._build_objects()
        self.event_generate('<<OpenKeyCommandList>>')

    def _build_objects(self):
        self.txt = NText(self.root, font=('courier', 10))


    def list_key_commands(self, data:dict) -> None:
        categories = set([d['category'] for d in data])

        self.txt.insert(1.0, "Key Commands\n")
        y = 2
        for category in categories:
            key_list = [ k for k in data if k['category'] == category ]

            self.txt.insert(f'{y}.0', f'\n{category}\n\n')
            y += 2

            for key_dict in key_list:
                self.txt.insert(f'{y}.0', f"{key_dict['name']:30} - {key_dict['key']}\n")
                y += 1

        self.txt.config(state='disabled')
        self.root.grid(row=0, column=0, sticky='nsew')
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.txt.grid()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)