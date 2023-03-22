''' This is the main entry point to Notebad. This is an MVC architecture and 
    the view and model (language) is loaded from within the controller.'''
import pathlib
from controller import NoteController
from conf import Configuration


cfg = Configuration()


if __name__ == '__main__':
    # Set up and load configuration before loading program
    current_dir = pathlib.Path(__file__).parent.resolve() # current directory 
    cfg.set_root_dir(current_dir)
    cfg.enable_dev_mode()

    # Load the controller
    controller = NoteController(current_dir)
    controller.run()
    