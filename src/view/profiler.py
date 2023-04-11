from tkinter import StringVar

from modules.logging import Log
from settings import Configuration
from widgets  import NButton, NFrame, NLabel, NTabFrame, NText, NTreeview, NNotebook, open_file_dialog

cfg = Configuration()
logger = Log(__name__)

'''
Something super cool to do here would be to have this ssh into the server and grab the profiler data
This will require adding an ssh profile to the app and then using that to connect to the server
'''

class ProgressProfiler(NTabFrame):
    ''' Displays the profiler data '''
    def __init__(self, tab_widget:NNotebook) -> None:
        logger.debug("Profiler begin init")

        # Build the outer frame
        super().__init__(tab_widget)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.grid(row=0, column=0, sticky='nswe')

        # Tab widget is the parent widget
        self.tab_title = 'Profiler'

        # Tab variables
        self.filename  = StringVar()
        self.timestamp = StringVar()
        self.mode      = StringVar(value="Source")
        self.profiler_data = {}

        # Build everything
        self._build_toolbar()
        self._build_summary_view()

        
    def load_profiler_data(self, data:dict) -> None:
        ''' Load the profiler data into the tree after destroying the existing tree '''
        self.profiler_data = data
        if self.mode.get() == 'Source':
            self._build_summary_view()
        else:
            self._build_src_view()

    ###
    # Private methods
    ###

    def _prompt_for_file(self, *_) -> None:
        ''' Retry getting the file name '''
        user_input = open_file_dialog(filetypes=[('Progress Profiler Files', '*.prof*'), ('All Files', '*.*')])
        if user_input:
            self.filename.set(user_input)
            self.event_generate('<<ProfilerFileChanged>>')

    def _build_toolbar(self) -> None:
        ''' Build the toolbar for the profiler. We dont need to assign everything to self because
            we are not going to be using it anywhere else. We can change the values with StringVar '''
        self.toolbar = NFrame(self)
        self.toolbar.grid(row=0, column=0, sticky='nsew', padx=5, pady=(5,2))
        self.toolbar.columnconfigure(1, weight=1)
        self.toolbar.columnconfigure(3, weight=1)

        # Build the meta data frame
        NLabel(self.toolbar, text='File:').grid(row=0, column=0, sticky='w', padx=(5,0))
        NLabel(self.toolbar, textvariable=self.filename).grid(row=0, column=1, sticky='w')
        NLabel(self.toolbar, text='Datetime:').grid(row=0, column=2, sticky='w',)
        NLabel(self.toolbar, textvariable=self.timestamp).grid(row=0, column=3, sticky='w')
        NButton(self.toolbar, textvariable=self.mode, width=8, command=self._toggle_mode).grid(row=0, column=4, sticky='e',pady=(0,5), padx=5)
        NButton(self.toolbar, text='Open profile', width=15, command=self._prompt_for_file).grid(row=0, column=5, sticky='e',pady=(0,5), padx=5)

    def _toggle_mode(self, *_) -> None:
        ''' Toggle between source and summary view '''
        if self.mode.get() == 'Source':
            self.mode.set('Summary')
            self._build_src_view()
        else:
            self.mode.set('Source')
            self._build_summary_view()

    def _build_summary_view(self) -> None:
        ''' Summary shows a treeview of the data with a focus on the number of lines
            executed and the time spent executing them. '''
        
        # Build the main frame
        self.main_frame = NFrame(self)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        # Build the treeview
        self.tree = NTreeview(self.main_frame, columns=('line',  'exec_time', 'tot_time', 'exec_count'))
        # It would be nice to have a lot of this in the treeview class
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

        if self.profiler_data:
            # Build the treeview data
            for src, d in self.profiler_data.items():
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

            self.timestamp.set(self.profiler_data['meta']['timestamp'])



    def _build_src_view(self, *_) -> None:
        ''' Build the source code view. This has a treeview on the left and a text 
            widget on the right that shows the source code. The profiler results 
            are with expanded includes. That means the files must be built.
             
            Currently the there is a discrepancy between the line numbers in the 
            debugger and the profiler.  '''

        # Build the main frame
        self.main_frame = NFrame(self)
        self.main_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.rowconfigure(1, weight=2)

        # Att the treeview to the left
        self.tree = NTreeview(self.main_frame, columns=('exec_time', 'lines'))
        self.tree.heading('#0', text='Source', anchor='w')
        self.tree.heading('exec_time', text='Time', anchor='w')
        self.tree.heading('lines', text='Lines', anchor='w')
        self.tree.column('#0', width=200, stretch=True)
        self.tree.column('exec_time', width=50)
        self.tree.column('lines', width=30)

        # Setup the tree to generate an event when a row is clicked
        self.tree.on_click(self._event('<<ProfilerSourceView>>'))

        # Build the treeview data
        for src, d in self.profiler_data.items():
            if src == 'meta':
                continue

            exec_time = f"{d['exec_time']:0.3f}" if d['exec_time'] else ''

            self.tree.insert('', 'end', src,text=src, values=(exec_time, d['line_count']))
            for line_no, ln_dic in d['lines'].items():
                if ln_dic['func'] != None:
                    name = ln_dic['func']
                else:
                    name = ln_dic['name']
                exec_time = f"{ln_dic['exec_time']:0.4f}" if ln_dic['exec_time'] else ''
                self.tree.insert(src, 'end', text=line_no, values=(exec_time, ''))


        self.tree.grid(row=0, column=1, sticky='nsew')
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=5)
        self.main_frame.rowconfigure(0, weight=1)

        # Add the textbox to the right
        # Todo This needs to be themed and have a scrollbar
        self.text = NText(self.main_frame)
        self.text.grid(row=0, column=2, sticky='nsew')

    def _set_theme(self, theme: str) -> None:
        ''' Set the theme for the profiler '''
        if hasattr(self, 'text'):
            self.text._set_theme()
