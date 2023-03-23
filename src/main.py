''' This is the main entry point to Notebad. This is an MVC architecture and 
    the view and model (language) is loaded from within the controller.'''
import pathlib
from controller import NoteController
from conf import Configuration

cfg = Configuration()

# Set the path of the root directory. The os module should be used for all file
# operations. This will handle the path differences between Windows and Linux
current_dir = pathlib.Path(__file__).parent.resolve() # current directory 
cfg.set_root_dir(current_dir)

if __name__ == '__main__':
    # Set up and load configuration before loading program
    
    # Load the controller
    controller = NoteController(current_dir)
    controller.run()
    