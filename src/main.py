''' This is the main entry point to Notebad. This is an MVC architecture and 
    the view and model (language) is loaded from within the controller.'''
from controller import NotebadApp
from settings import Configuration

if __name__ == '__main__':
    # Set up and load configuration before loading program
    # Configuration will load personal.cf if it exists or create it if needed
    cfg = Configuration()
    # Load the controller
    app = NotebadApp()
    app.run()
    