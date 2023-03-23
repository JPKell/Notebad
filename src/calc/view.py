from   tkinter import Label, Toplevel
from   tkinter.ttk import Style, Frame, Button

from settings import Configuration
from modules.logging import Log

cfg = Configuration()
logger = Log(__name__)

class View(Toplevel):
    ''' The view does all the visuals. It's a calculator so pretty easy. 
        It leaves the logic of keeping the lines short enough to the model. 
        The number display and variables built from number input are all strings
        that means it can grow outside the display. Limited to 20 characters '''

    def __init__(self, controller, style: Style) -> None:
        super().__init__() # Init the Toplevel widget to create a new window
        self.controller = controller
        self.title(cfg.calc_title) 
        self.style = style
        # Set up look and feel
        self.config(bg=cfg.calc_bg)
        self.configure_button_styles()
        # Default value to display
        self.value_var = "0"
        self.prev_val  = ""
        self.operator  = ""    
        self.equals_buffer = ""  
        # Build the widgets
        self._make_main_frame()
        self._make_number_display()
        self._make_buttons()
        self._lock_window_size()
        self.protocol("WM_DELETE_WINDOW", self.exit_calc)
        logger.debug("Calc view init")

    def exit_calc(self) -> None:
        ''' Exit the calculator and destroy evidence on way out '''
        self.destroy()
        logger.info("Calculator close")

    def main(self) -> None:
        ''' The mainloop of the calc window '''
        self.mainloop()

    def configure_button_styles(self) -> None:
        ''' Calculator styling is kept over here. Calculator is intended to be a 
            standalone module called from the main app '''
        common_style = {
            'font': ('Arial', 16, 'bold'), 
            'relief': 'ridge', 
            'width': 5, 
            'padding': 5,
            'borderwidth': 1,
            'anchor': 'n'
            }
        # Number buttons
        self.style.configure('N.TButton', foreground="white", background='#696969', **common_style) 
        # Operator buttons
        self.style.configure('O.TButton', foreground="black", background='orange', **common_style)
        # Alt buttons
        self.style.configure('A.TButton', foreground="black", background='grey', **common_style)

    def _make_main_frame(self) -> None:
        ''' Create and pack the main frame all the other widgets live inside '''
        self.main_frm = Frame(self)
        self.main_frm.pack(padx=cfg.calc_outer_pad, pady=cfg.calc_outer_pad) 

    def _make_number_display(self) -> None:
        ''' Number display is a label we update the text of '''
        common = {
            'anchor':'e',
            'bg':'black', 
            'fg':'#EFEFEF',
        }
        self.prev_lbl = Label(
            self.main_frm,
            text = "",
            **common,
            font=('Arial', 14), height=1
        )
        self.prev_lbl.pack(fill='x')

        self.lbl = Label( 
            self.main_frm, 
            text=self.value_var, 
            **common,
            font=('Arial',18), height=1
        )
        self.lbl.pack(fill='x')

    def _make_buttons(self) -> None:
        ''' Make the buttons. Rather than make them one by one we loop through a list '''

        # I thought about putting more buttons in the future, but we will see how that goes. 
        MAX_BUTTONS_PER_ROW = 4
        button_captions = [
            'C', '+/-', '%', '/',
            7,     8,   9, '*',   # Note the numbers are int's not strings
            4,     5,   6, '-',   # This is to make picking them out easier.
            1,     2,   3, '+',
            0,   '.',  '='
        ]
        self.btn_frm = Frame(self.main_frm)
        self.btn_frm.pack(fill='both', expand=True)
        self.btn_frm.pack()

        is_first_row = True
        buttons_in_row = 0
        for caption in button_captions:
            # Create a new frame for each row so they pack in row how we want
            if is_first_row or buttons_in_row == MAX_BUTTONS_PER_ROW:
                is_first_row = False
                buttons_in_row = 0
                frm = Frame(self.btn_frm)
                frm.pack(fill='x')

            # Determine what type of button it is so it gets called properly 
            if isinstance(caption, int):
                style_prefix = 'N'
            elif self._is_operator(caption):
                style_prefix = 'O'
            else:
                style_prefix = 'A'
            style_name = f"{style_prefix}.TButton"
            # Create the button object
            btn = Button(frm, 
                             text=caption, 
                             command=(lambda button=caption: self.controller.button_click(button)),
                             style=style_name,
                             ) 
            # We want 0 to cover 2 spaces so set expand to yes.
            if caption == 0:
                fill = 'x'
                expand = 1
            else:
                fill = 'none'
                expand = 0
            # Pack the button in
            btn.pack(side='left', fill=fill, expand=expand)
            buttons_in_row += 1

    def _lock_window_size(self) -> None:
        ''' The window will draw to fit everything if not given a geometry. 
            Lock it in once everything is packed. '''
        self.resizable(False, False)

    def _is_operator(self, caption) -> None:
        ''' And abstraction to determine if the keypress was an operator'''
        ops = ['/', '*', '-', '+', '=']
        return caption in ops

    def _update(self) -> None:
        ''' Update the screen after number entry '''
        self.lbl.config(text=self.value_var)
        self.prev_lbl.config(text=f"{self.prev_val} {self.operator} {self.equals_buffer}")
        self.update_idletasks()
        self.update()