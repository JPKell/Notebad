from tkinter.ttk import Style

from .model import Model
from .view  import View

from modules.logging import Log

logger = Log(__name__)

class Calculator:       # a.k.a Controller
    ''' The calculator is a simple MVC architecture. It was added to Notebad as 
        a more simplified example without heaps of methods and classes. It carries
        the styles from the main app since it is running on the same Tk interpreter '''
    def __init__(self, style:Style, conf):
        self.conf = conf 
        self.model = Model()           # Model does not know about controller
        self.view  = View(self, style) # View does. Pass the controller into view
        self._bind_keys()
        logger.info("Calc controller init")

    def main(self) -> None:
        ''' Fire up the main loop. Since this example is very basic the view holds
            all the tkinter modules including the TopLevel widget. '''
        self.view.main()

    def button_click(self, caption) -> None:
        ''' Take the caption (text on the button pressed) and pass it along to 
            the model to make sense of. '''
        result = self.model.calculate(caption)
        if len(result['value']) > 20:    # If the output of the model is too long let float convert to -e notation
            result['value'] = f"{float(result['value'])}"

        self.view.value_var = result['value']
        self.view.prev_val  = result['prev_value']
        self.view.operator  = result['operator']
        self.view.equals_buffer = result['equals_buffer']
        self.view._update() # update the display
        logger.verbose(f"Button click: {caption}")

    def keyboard_click(self, key) -> None:
        '''Take the keyboard input and convert numbers to integers so they are 
           handled properly downstream '''
        if key in '0123456789':
            # The numlock key will mean keypad keys still get here, but might not be a number
            try:
                self.button_click(int(key))
            except ValueError:
                pass
        else:
            self.button_click(key)
        logger.verbose(f"Keyboard click: {key}")

    def _bind_keys(self) -> None:
        ''' Bind keys to the calculator window '''
        self.view.bind('<Return>',      lambda event: self.keyboard_click('='))
        self.view.bind('<KP_Enter>',    lambda event: self.keyboard_click('='))
        self.view.bind('<Escape>',      lambda event: self.keyboard_click('C'))
        self.view.bind('<BackSpace>',   lambda event: self.keyboard_click('C'))
        self.view.bind('<Delete>',      lambda event: self.keyboard_click('C'))
        self.view.bind('<Key>',         lambda event: self.keyboard_click(str(event.char)))

        # Configure is called when there is a change of configuration as far as I can tell
        # resize events, that sort of thing. When the theme changes the buttons loose their
        # styling. This is a work around in the mean time. But ideally the ui should get configured
        # for both sets of buttons.  
        self.view.bind('<Configure>',   lambda event: self.view.configure_button_styles())
