from tkinter import filedialog

from modules.logging import Log
from settings import Configuration
from widgets import NButton, NFrame, NLabel, NLabelframe, NTabFrame, NText, NTreeview, NNotebook

cfg = Configuration()
logger = Log(__name__)

'''
Something super cool to do here would be to have this ssh into the server and run the profiler
This will require adding an ssh profile to the app and then using that to connect to the server
'''

class ProgressProfiler(NTabFrame):
    ''' Displays the profiler data '''
    def __init__(self, tab_widget:NNotebook) -> None:
        logger.debug("Profiler begin init")
        # Build the outer frame
        super().__init__(tab_widget)
        self.grid_columnconfigure(0, weight=1)
        self.tab_title = 'Profiler'

        self.tab_widget = tab_widget # This can go as soon as that monster call is gone
        self.pack(expand=True, fill='both') # Change this to grid 
        self.filename = self._get_file_name()
        self.text = NText
        self._build_summary()
        
    # Change this into controller method
    def _get_file_name(self) -> str:
        ''' Returns the file name from the path '''
        # filedialog.askopenfilename(filetypes=[('Progress Profiler Files', '*.prof'), ('All Files', '*.*')])
        return '/home/jpk/profile.profile'
    
    def _retry_file_name(self, *_) -> None:
        ''' Retry getting the file name '''
        self.filename = self._get_file_name()
        self.meta_frame.destroy()
        self._build_summary()


    def _build_summary(self) -> None:
        ''' Create the widgets '''
        
        self.meta_frame = NLabelframe(self, text='Profiler meta data', labelanchor='n')
        self.meta_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        for i in range(4):
            self.meta_frame.columnconfigure(i, weight=1)

        if not self.filename:
            NLabel(self.meta_frame, text=f'You must supply a profiler output to use this feature').pack( )
            NButton(self.meta_frame, text='Select file', command=self._retry_file_name).pack()
            return
        
        # We have a filename so parse the data and display it
        self.data = self.tab_widget.view.controller.parse_progress_profiler(self.filename)

        # Build the meta data frame
        NLabel(self.meta_frame, text=f"File: {self.filename}").grid(row=0, column=0, padx=(5,0), sticky='w')
        NLabel(self.meta_frame, text=f"Run: {self.data['meta']['timestamp']}").grid(row=0, column=1, sticky='w')
        NButton(self.meta_frame, text='View src', width=8, command=self._build_src_view).grid(row=0, column=2, sticky='e',pady=(0,5), padx=5)
        NButton(self.meta_frame, text='New file', width=8, command=self._retry_file_name).grid(row=0, column=3, sticky='e',pady=(0,5), padx=5)

        # Build the main frame
        self.main_frame = NFrame(self)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.rowconfigure(1, weight=1)

        # Build the treeview
        self.tree = NTreeview(self.main_frame, columns=('line',  'exec_time', 'tot_time', 'exec_count'))
        self.tree.heading('#0', text='Source', anchor='w')

        self.tree.heading('line', text='Lines', anchor='w')
        self.tree.heading('exec_time', text='Execution time', anchor='w')
        self.tree.heading('tot_time', text='Total time', anchor='w')
        self.tree.heading('exec_count', text='Count', anchor='w')
        self.tree.column('#0', width=200, stretch=True)
        self.tree.column('line', width=20, stretch=True)
        self.tree.column('exec_time', width=50, stretch=True)
        self.tree.column('tot_time', width=50, stretch=True)
        self.tree.column('exec_count', width=20, stretch=True)
        self.tree.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Build the treeview data
        for src, d in self.data.items():
            if src == 'meta':
                continue

            exec_time = f"{d['exec_time']:0.6f}" if d['exec_time'] else 0
            tot_time = f"{d['tot_time']:0.6f}" if d['tot_time'] else 0

            self.tree.insert('', 'end', src,text=src, values=(d['line_count'], exec_time, tot_time, ''))
            for line_no, ln_dic in d['lines'].items():
                if ln_dic['func'] != None:
                    name = ln_dic['func']
                else:
                    name = ln_dic['name']
                exec_time = f"{ln_dic['exec_time']:0.6f}" if ln_dic['exec_time'] else 0
                tot_time = f"{ln_dic['tot_time']:0.6f}" if ln_dic['tot_time'] else 0
                self.tree.insert(src, 'end', text=name, values=(line_no, exec_time, tot_time, int(ln_dic['exec_count'])))



    # def _get_file_name(self) -> str:

    def _build_src_view(self, *_) -> None:
        ''' Build the source view '''
        
        # This will need the source code to be built from the various includes
        
        # The tab will show the tree view on the left hand side and the source code on the right. 
        # you wont be able to edit the source since it will be a combination of files. Might be 
        # nice to have a button to open the file in the editor though.
        
        self.file = self.tree.focus()

        # First destroy the existing main frame
        self.main_frame.destroy()

        # Build the main frame
        self.main_frame = NFrame(self)
        self.main_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.rowconfigure(1, weight=2)

        # Att the treeview to the left
        self.tree = NTreeview(self.main_frame, columns=('exec_time', 'exec_count'))
        self.tree.heading('#0', text='Source', anchor='w')
        self.tree.heading('exec_time', text='Execution time', anchor='w')
        self.tree.heading('exec_count', text='Count', anchor='w')
        self.tree.column('#0', width=100, stretch=True)
        self.tree.column('exec_time', width=50, stretch=True)
        self.tree.column('exec_count', width=20, stretch=True)

        # Build the treeview data
        for src, d in self.data.items():
            if src == 'meta':
                continue

            exec_time = f"{d['exec_time']:0.6f}" if d['exec_time'] else 0

            self.tree.insert('', 'end', src,text=src, values=(exec_time))
            for line_no, ln_dic in d['lines'].items():
                if ln_dic['func'] != None:
                    name = ln_dic['func']
                else:
                    name = ln_dic['name']
                exec_time = f"{ln_dic['exec_time']:0.6f}" if ln_dic['exec_time'] else 0
                self.tree.insert(src, 'end', text=line_no, values=(exec_time, int(ln_dic['exec_count'])))


        self.tree.grid(row=0, column=1, sticky='nsew')
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=5)
        self.main_frame.rowconfigure(0, weight=1)

        # Add the textbox to the right
        # Todo This needs to be themed and have a scrollbar
        self.text = NText(self.main_frame)
        self.text.grid(row=0, column=2, sticky='nsew')

        self.event_generate('<<ProfilerSourceView>>')