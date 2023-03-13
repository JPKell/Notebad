import tkinter as     tk
from   tkinter import ttk

class View(tk.Toplevel):
    PAD = 1
    MAX_BUTTONS_PER_ROW = 4
    button_captions = [
        'C', '+/-', '%', '/',
          7,     8,   9, '*',
          4,     5,   6, '-',
          1,     2,   3, '+',
          0,   '.',  '='
    ]
    

    def __init__(self, controller, style: ttk.Style) -> None:
        super().__init__() # Init the tk.Tk class
        self.title("Mathbad") 

        CALC_SIZE = (400, 325)
        self.geometry(f"{CALC_SIZE[0]}x{CALC_SIZE[1]}")
        # Max size of window
        self.maxsize(*CALC_SIZE)
        self.minsize(*CALC_SIZE)

        self.controller = controller
        self.style = style
        # Set up look and feel
        self.config(bg="black")
        self.configure_button_styles()

        self.value_var = "0"      

        self._make_main_frame()
        self._make_label()
        self._make_buttons()

    def main(self):
        self.mainloop()

    def configure_button_styles(self):
        common_style = {
            'font': ('Arial', 16, 'bold'), 
            'relief': 'ridge', # groove , ridge     # winner raised
            'width': 5, 
            'padding': 5,
            'borderwidth': 1,
            'bordercolor': 'black',
            }
        # Number buttons
        self.style.configure('N.TButton', foreground="white", background='#696969', **common_style) 
        # Operator buttons
        self.style.configure('O.TButton', foreground="black", background='orange', **common_style)
        # Alt buttons
        self.style.configure('A.TButton', foreground="black", background='grey', **common_style)
    def _make_main_frame(self):
        self.main_frm = ttk.Frame(self)
        self.main_frm.pack(padx=self.PAD, pady=self.PAD) 

    def _make_label(self):
        ''' ent does not have to be an attribute of class since we have access to the value with self.value_var '''
        self.lbl = tk.Label( self.main_frm, 
                       text=self.value_var, 
                       anchor='e',
                       bg='black', 
                       fg='white',
                       font=('Arial',18), height=2
                       )
        self.lbl.pack(fill='x')

    def _make_buttons(self):
        outer_frm = ttk.Frame(self.main_frm)
        outer_frm.pack(fill='both', expand=True)
        outer_frm.pack()

        is_first_row = True
        buttons_in_row = 0
        for caption in self.button_captions:
            if is_first_row or buttons_in_row == self.MAX_BUTTONS_PER_ROW:
                is_first_row = False
                buttons_in_row = 0
                frm = ttk.Frame(outer_frm)
                frm.pack(fill='x')

            if isinstance(caption, int):
                style_prefix = 'N'
            elif self._is_operator(caption):
                style_prefix = 'O'
            else:
                style_prefix = 'A'

            style_name = f"{style_prefix}.TButton"

            btn = ttk.Button(frm, text=caption, command=(lambda button=caption: self.controller.button_click(button)), style=style_name) 
            
            if caption == 0:
                fill = 'x'
                expand = 1
            else:
                fill = 'none'
                expand = 0

            btn.pack(side='left', fill=fill, expand=expand)
            buttons_in_row += 1

    def _is_operator(self, caption):
        ops = ['/', '*', '-', '+', '=']
        return caption in ops

    def _update(self):
        self.lbl.config(text=self.value_var)
        self.update_idletasks()
        self.update()