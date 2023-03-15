''' This is the main entry point to Notebad. This is an MVC architecture and 
    the view is loaded from within the controller.'''

from model import LanguageModel
from controller import NoteController

class NotebadApp:
    def __init__(self):
        model = LanguageModel()    
        controller = NoteController(model)
        controller.run()

if __name__ == '__main__':
    app = NotebadApp()

