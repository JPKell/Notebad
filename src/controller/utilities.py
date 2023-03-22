from calc.controller import Calculator
from modules.logging import Log

logger = Log(__name__)

class Utilities:
    ''' This class contains all the functions that are not directly related to

        the text box. These are functions that are used to manipulate the

        application itself. '''
    
    def __init__(self, controller, view):
        self.controller = controller
        self.view = view
        logger.debug('Utilities init')


    def eval_selection(self) -> None:
        ''' Evaluate a line or selection of code. The result is displayed in 
            the footer.
        
            Since Python is interpreted, we can evaluate code right in the text 
            box. This is handy to doing math or other simple things.'''
        selection = self.view.textbox.editor.get_selection()
        # If there is nothing selected, evaluate the current line
        if selection == '':  
            selection = self.view.textbox.editor.get_current_line_text()
        # If there is nothing still selected, do nothing
        if selection == '': 
            result = "Nothing to evaluate"
        else:
            # It's bad enough we are evaluating any user input, so lets at least 
            try: # to catch any errors that might occur.
                result = eval(selection)
            except:
                result = "Invalid Python syntax" 
        logger.debug(f'Python eval: {selection} Result: {result}')
        self.view.textbox.footer.set_status(result) # Return result to user
        

    def open_calculator(self):
        ''' Opens a calculator window. The calculator is basic, but maybe will improve.
            Maybe one day it will be a full scientific calculator, or have business 
            functions. Who knows. Might even have it's own tab. '''
        calculator = Calculator(self.view.ui.style)
        calculator.main()
