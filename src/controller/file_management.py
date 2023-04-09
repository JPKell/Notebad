import os

from modules.logging import Log
from settings import Configuration
from view.ide import Ide
from view.profiler import ProgressProfiler

from widgets import open_file_dialog, save_file_dialog, prompt_yes_no


cfg = Configuration()
logger = Log(__name__)

class FileManagement:
    ''' Handles all file management. '''
    def __init__(self, controller):
        self.controller = controller
        self._recent_files = os.path.join(cfg.data_dir, 'recent_files.txt') # TODO make a function in settings that returns the path to a file in the data dir So cfg.data_file('recent_files.txt')
        logger.debug('Initialized FileManagement')

    def new_file(self) -> None:
        ''' Creates a new tab and a crisp fresh textbox. '''
        logger.debug('Creating new file')
        self.controller.view.tabs.new_tab('ide')
        self.controller.view.tabs.move_to_tab()    # Move focus to the new tab
        logger.info('New file created')

    def open_file(self, full_path=None) -> None:
        ''' Opens a file. There should be an encoding option here. But there 
            isn't, that should get added and this note removed. '''
        if full_path is None:
            full_path = open_file_dialog()   # Tkinter filedialog returns '/' filepath, even for Windows! Woohoo!

        if full_path:
            tab = self.controller.get_current_tab()         # Get the current tab

            if 'prof' in full_path[-8:]:
                self.controller.view.tabs.new_tab('profiler')
                self.controller.view.tabs.move_to_tab()

                tab.full_path = full_path.strip()
                self.write_file_to_textbox(tab, full_path)
                tab.text.set_position('1.0')
            else:             
                
                if isinstance(tab, Ide) and not tab.is_blank: # Don't open a new tab if the current one is blank
                    # TODO replace this with a cleaner way to open a new tab
                    self.controller.view.tabs.new_tab('ide')
                    self.controller.view.tabs.move_to_tab()
                    tab = self.controller.get_current_tab()     # Grab the newly minted textbox object 

                tab.full_path = full_path.strip()
                self.write_file_to_textbox(tab, full_path)
                tab.text.set_position('1.0')      # Set cursor at beginning of file
            
        logger.info(f'Opened file: {full_path}')
        return 'break'

    def save_file(self) -> None:
        ''' Saves current textbox to disk. If not written to disk before,
            save_as_file is called to let the user name it. Also thinking 
            about just sequentially naming all the files to make like hard. jk'''
        textbox = self.controller.view.textbox

        # If the current file still has the default file name, prompt for a new name
        if textbox.meta.file_name == cfg.new_file_name:
            self.save_as_file(textbox)
        else:
            self.write_textbox_to_file(textbox.meta.full_path, textbox)
        logger.info(f'Saved file: {textbox.meta.full_path}')
        
    def save_as_file(self, textbox:Ide=None) -> None:
        ''' Saves textbox to disk. If no textbox is given, the current tab is used.'''

        # I am giving the option here to pass a textbox object in to be saved. 
        # the time this would be useful would be in a save all function. But is that
        # something to worry about now? No. 
        if textbox is None:             
            textbox = self.controller.view.textbox
        full_path = save_file_dialog(file_name=textbox.file_name, path=textbox.file_path)
        if full_path:
            self.write_textbox_to_file(full_path, textbox)
        logger.info(f'Saved file as: {full_path}')

    def parts_from_file_path(self, full_path:str) -> dict:
        ''' Take the full path name and return a dictionary with the path and file name.
            `{ 'path': ..., 'file': ... }`
        '''
        parts = full_path.split('/')
        return {'path': '/'.join(parts[:-1]), 'file': parts[-1]}

    def write_file_to_textbox(self, ide:Ide, full_path:str) -> None:
        ''' Writes the contents of a file to the textbox '''

        ext = full_path.split('.')[-1]
        with open(full_path, "r") as file:
            
            if not cfg.syntax_on_load: # Just load the file
                ide.text.insert('end', file.read())
            
            elif ext in ['p', 'w', 'i', 'cls']: # Else see if we can handle the syntax
                self.controller.language.load_language('abl')
                self.controller.language.static_syntax_formatting(file_txt=file.read())
            
            else: # Else just load the file
                ide.text.insert('end', file.read())  # Insert the file contents into the textbox

            ide.tab_save_on_close = False # Reset the changed flag since we just opened the file
            ide.history.stackify()          # Add the file contents to the undo stack
        
        self._add_recent_file(full_path)
        logger.debug(f'Wrote file to textbox: {full_path}')

    def write_textbox_to_file(self, full_path:str, ide:Ide) -> None:
        ''' Private method to write file to disk. Needs encoding option. '''
        with open(full_path, "w") as file:
            txt = ide.text.get(1.0, 'end')
            if len(txt) > 1:   
                txt = txt[:-1] # Trailing newline character that needs to be removed
            file.write(txt)

        # Update the textbox properties
        ide.full_path = full_path
        ide.tab_save_on_close = False

        self._add_recent_file(full_path)
        logger.debug(f'Wrote file to textbox: {full_path}')


    ###
    # Private methods
    ###

    def _add_recent_file(self, full_path:str) -> None:
        ''' When meta is updated, add the full filepath to the recent files '''
        recent_files = []

        # Check "recent files" file exists and extract contents to manipulate the paths inside
        if os.path.exists(self._recent_files):
            with open(self._recent_files, 'r') as f:
                recent_files = f.readlines()

            # Loop through and remove any filepaths that no longer exist
            for file in recent_files:
                if not os.path.exists(file.strip()):
                    recent_files.remove(file)

            # Check if current file exists in the list and remove it
            if recent_files.count(full_path + '\n') != 0:
                recent_files.remove(full_path + '\n')
            # Or trim the list if it's more than 10 items long
            elif len(recent_files) >= 10:
                recent_files.pop(0)

        # Write "recent filepaths" to file
        recent_files.append(full_path)
        with open(self._recent_files, 'w') as f:
            for file in recent_files:
                f.write(file.strip() + '\n')

        # Send an event to update the recent files menu
        self.controller.menu.make_recent_file_list()