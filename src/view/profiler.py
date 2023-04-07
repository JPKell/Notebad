from tkinter import filedialog
from tkinter.ttk import Frame, Label, Labelframe, Button, Treeview


class ProgressProfiler(Frame):
    ''' Displays the profiler data '''
    def __init__(self, tabs) -> None:
        super().__init__(tabs)
        self.grid_columnconfigure(0, weight=1)

        self.tabs = tabs
        self.pack(expand=True, fill='both')
        self.filename = self._get_file_name()
        self._build_ui()
        
    # Change this into controller method
    def _get_file_name(self) -> str:
        ''' Returns the file name from the path '''
        # filedialog.askopenfilename(filetypes=[('Progress Profiler Files', '*.prof'), ('All Files', '*.*')])
        return '/home/jpk/profile.profile'
    
    def _retry_file_name(self, *_) -> None:
        ''' Retry getting the file name '''
        self.filename = self._get_file_name()
        self.meta_frame.destroy()
        self._build_ui()


    def _build_ui(self) -> None:
        ''' Create the widgets '''
        
        self.meta_frame = Labelframe(self, text='Profiler meta data', labelanchor='n')
        self.meta_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.meta_frame.columnconfigure(0, weight=1)
        self.meta_frame.columnconfigure(1, weight=1)
        self.meta_frame.columnconfigure(2, weight=1)

        if not self.filename:
            Label(self.meta_frame, text=f'You must supply a profiler output to use this feature').pack()
            Button(self.meta_frame, text='Select file', command=self._retry_file_name).pack()
            return
        
        # We have a filename so parse the data and display it
        self.data = self.tabs.view.controller.parse_progress_profiler(self.filename)

        # Build the meta data frame
        Label(self.meta_frame, text=f"File name: {self.filename}").grid(row=0, column=0, sticky='w')
        Label(self.meta_frame, text=f"Timestamp: {self.data['meta']['timestamp']}").grid(row=0, column=1, sticky='w')
        Label(self.meta_frame, text=f"User: {self.data['meta']['user']}").grid(row=0, column=2, sticky='w')

        # Build the main frame
        self.main_frame = Frame(self)
        self.main_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.rowconfigure(1, weight=1)

        # Build the treeview
        self.tree = Treeview(self.main_frame, columns=('line', 'exec_count',  'exec_time', 'tot_time'))
        self.tree.heading('#0', text='Source', anchor='w')

        self.tree.heading('line', text='Line', anchor='w')
        self.tree.heading('exec_count', text='count', anchor='w')
        self.tree.heading('exec_time', text='exec_time', anchor='w')
        self.tree.heading('tot_time', text='tot_time', anchor='w')
        self.tree.column('#0', width=200, stretch=True)
        self.tree.column('line', width=20, stretch=True)
        self.tree.column('exec_count', width=20, stretch=True)
        self.tree.column('exec_time', width=50, stretch=True)
        self.tree.column('tot_time', width=50, stretch=True)
        self.tree.pack(expand=True, fill='both')

        # Build the treeview data
        for src, d in self.data.items():
            if src == 'meta':
                continue
            self.tree.insert('', 'end', src,text=src)
            for line_no, ln_dic in d['lines'].items():
                if ln_dic['func'] != None:
                    name = ln_dic['func']
                else:
                    name = ln_dic['name']
                exec_time = f"{ln_dic['exec_time']:0.6f}" if ln_dic['exec_time'] else 0
                tot_time = f"{ln_dic['tot_time']:0.6f}" if ln_dic['tot_time'] else 0
                self.tree.insert(src, 'end', text=name, values=(line_no, ln_dic['exec_count'], exec_time, tot_time))

            # self._build_meta_frame()
        # Build a form to get the file name  {'func': func, 'name': name, 'lines_exec': line['lines_exec'], 'exec_count': 0, 'exec_time': 0, 'tot_time': 0, 'callee': None, 'call_count': None}
        