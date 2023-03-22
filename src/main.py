''' This is the main entry point to Notebad. This is an MVC architecture and 
    the view and model (language) is loaded from within the controller.'''
import pathlib
from controller import NoteController

if __name__ == '__main__':
    current_dir = pathlib.Path(__file__).parent.resolve() # current directory 
    controller = NoteController(current_dir)
    controller.run()
    