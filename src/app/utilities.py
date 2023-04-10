from tkinter import Tk

from calc.controller import Calculator
from modules.logging import Log
from settings        import Configuration
from view            import NotebadView

cfg = Configuration()
logger = Log(__name__)


class Utilities:
    ''' This class contains all the functions that are not directly related to

        the text box. These are functions that are used to manipulate the

        application itself. '''
    
    def __init__(self, app: Tk, view: NotebadView):
        self.app  = app
        self.view = view
        logger.debug('Utilities init')


    def eval_selection(self, event=None) -> None:
        ''' Evaluate a line or selection of code. The result is displayed in 
            the footer.
        
            Since Python is interpreted, we can evaluate code right in the text 
            box. This is handy to doing math or other simple things.'''
        ide = event.widget 
        if selection == '':  
            selection = ide.editor.get_current_line_text()

        if selection == '': 
            result = "Nothing to evaluate"
        else:
            # It's bad enough we are evaluating any user input, so lets at least 
            # try to catch any errors that might occur.
            try: 
                result = eval(selection)
            except:
                result = "Invalid Python syntax" 
        logger.debug(f'Python eval: {selection} Result: {result}')
        ide.footer.set_status(result) # Return result to user
        

    def open_calculator(self):
        ''' Opens a calculator window. The calculator is basic, but maybe will improve.
            Maybe one day it will be a full scientific calculator, or have business 
            functions. Who knows. Might even have it's own tab. '''
        calculator = Calculator(self.view.ui.style)
        calculator.main()
