import os

from modules.logging import Log
from settings import Configuration
from view.ide import Ide


cfg = Configuration()
logger = Log(__name__)

class FileManagement:
    ''' Handles all file management. '''
    def __init__(self, controller):
        self.controller = controller
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
            full_path = self.controller.view.open_file_dialogue()   # Tkinter filedialog returns '/' filepath, even for Windows! Woohoo!

        if full_path:
            textbox = self.controller.view.textbox         # Get the current textbox
            path_parts = self.parts_from_file_path(full_path)
            if not textbox.is_blank:            # Don't open a new tab if the current one is blank
                self.controller.view.tabs.new_tab(file_name=path_parts['file'])
                self.controller.view.tabs.move_to_tab()
                textbox = self.controller.view.textbox     # Grab the newly minted textbox object 

            textbox.full_path=full_path.strip()
            
            self.write_file_to_textbox(textbox, full_path)
            textbox.cursor.set_position('1.0')      # Set cursor at beginning of file
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
        full_path = self.controller.view.save_file_dialogue(file_name=textbox.meta.file_name, path=textbox.meta.file_path)
        if full_path:
            self.write_textbox_to_file(full_path, textbox)
        logger.info(f'Saved file as: {full_path}')

    def parts_from_file_path(self, full_path:str) -> dict:
        ''' Take the full path name and return a dictionary with the path and file name.
            `{ 'path': ..., 'file': ... }`
        '''
        parts = full_path.split('/')
        return {'path': '/'.join(parts[:-1]), 'file': parts[-1]}

    def write_file_to_textbox(self, textbox:Ide, full_path:str) -> None:
        ''' Writes the contents of a file to the textbox '''

        ext = full_path.split('.')[-1]
        with open(full_path, "r") as file:
            
            if not cfg.syntax_on_load: # Just load the file
                textbox.insert('end', file.read())
            
            elif ext in ['p', 'w', 'i', 'cls']: # Else see if we can handle the syntax
                self.controller.language.load_language('abl')
                self.controller.language.static_syntax_formatting(file_txt=file.read())
            
            else: # Else just load the file
                textbox.insert('end', file.read())  # Insert the file contents into the textbox

            textbox.tab_save_on_close = False # Reset the changed flag since we just opened the file
            textbox.history.stackify()          # Add the file contents to the undo stack
        logger.debug(f'Wrote file to textbox: {full_path}')

    def write_textbox_to_file(self, full_path:str, textbox:Ide) -> None:
        ''' Private method to write file to disk. Needs encoding option. '''
        with open(full_path, "w") as file:
            txt = textbox.get(1.0, 'end')
            if len(txt) > 1:   
                txt = txt[:-1] # Trailing newline character that needs to be removed
            file.write(txt)

        # Update the textbox properties
        path_parts = self.parts_from_file_path(full_path)
        textbox.full_path = full_path
        textbox.tab_save_on_close = False
        self.controller.view.tabs.set_properties(textbox.meta.tk_name, text=textbox.meta.file_name)

        # Update the window title
        self.controller.app.title(f"{cfg.app_title} - {textbox.meta.file_name}")
        logger.debug(f'Wrote file to textbox: {full_path}')



class Meta:
    def __init__(self, ide):
        self.ide = ide

        self._recent_files = os.path.join(cfg.current_dir, 'app_data/recent_files.txt')

    # Do this from controller reacting to event from view
    def add_recent_file(self):
        ''' When meta is updated, add the full filepath to the recent files '''
        recent_files = []
        if self.full_path is not None:
            # Check "recent files" file exists and extract contents to manipulate the paths inside
            if os.path.exists(self._recent_files):
                with open(self._recent_files, 'r') as f:
                    recent_files = f.readlines()

                # Loop through and remove any filepaths that no longer exist
                for file in recent_files:
                    if not os.path.exists(file.strip()):
                        recent_files.remove(file)

                # Check if current file exists in the list and remove it
                if recent_files.count(self.full_path + '\n') != 0:
                    recent_files.remove(self.full_path + '\n')
                # Or trim the list if it's more than 10 items long
                elif len(recent_files) >= 10:
                    recent_files.pop(0)

            # Write "recent filepaths" to file
            recent_files.append(self.full_path)
            with open(self._recent_files, 'w') as f:
                for file in recent_files:
                    f.write(file.strip() + '\n')
