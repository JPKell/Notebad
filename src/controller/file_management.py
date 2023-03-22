from view.textbox import Textbox
from modules.logging import Log

logger = Log(__name__)

class FileManagement:
    ''' Handles all file management. '''
    def __init__(self, controller):
        self.controller = controller
        self.conf       = self.controller.conf
        logger.debug('Initialized FileManagement')


    ## File management ##
    def new_file(self) -> None:
        ''' Creates a new tab and a crisp fresh textbox. '''
        logger.debug('Creating new file')
        self.controller.view.tabs.new_tab()
        self.controller.view.tabs.move_to_tab()    # Move focus to the new tab
        logger.info('New file created')

    def open_file(self) -> None:
        ''' Opens a file. There should be an encoding option here. But there 
            isn't, that should get added and this note removed. '''
        full_path = self.controller.view.open_file_dialogue()
        if full_path:
            textbox = self.controller.view.textbox         # Get the current textbox
            path_parts = self.parts_from_file_path(full_path)
            if not textbox.is_blank:            # Don't open a new tab if the current one is blank
                self.controller.view.tabs.new_tab(file_name=path_parts['file'])
                self.controller.view.tabs.move_to_tab()
                textbox = self.controller.view.textbox     # Grab the newly minted textbox object 

            textbox.meta.set_meta(
                tk_name=self.controller.view.tabs.select(),
                full_path=full_path,
                file_path=path_parts['path'], 
                file_name=path_parts['file'], 
                )
            self.write_file_to_textbox(textbox, full_path)
            self.controller.view.tab_change()
        logger.info(f'Opened file: {full_path}')

    def save_file(self) -> None:
        ''' Saves current textbox to disk. If not written to disk before,
            save_as_file is called to let the user name it. Also thinking 
            about just sequentially naming all the files to make like hard. jk'''
        textbox = self.controller.view.textbox
        if textbox.meta.file_name == self.conf.new_file_name:
            self.save_as_file(textbox)
        else:
            self.write_textbox_to_file(textbox.meta.full_path, textbox)
        logger.info(f'Saved file: {textbox.meta.full_path}')
        
    def save_as_file(self, textbox:Textbox=None) -> None:
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
        if self.conf.os == 'nt':         # Windows
            parts = full_path.split('\\')
            return {'path': '\\'.join(parts[:-1]), 'file': parts[-1]}
        else:                       # Linux/Mac
            parts = full_path.split('/')
            return {'path': '/'.join(parts[:-1]), 'file': parts[-1]}

    def write_file_to_textbox(self, textbox:Textbox, full_path:str) -> None:
        ''' Writes the contents of a file to the textbox '''

        ext = full_path.split('.')[-1]
        with open(full_path, "r") as file:
            if ext in ['p', 'w', 'i', 'cls']:
                self.controller.language.load_language('abl')
                self.controller.language.load_with_basic_highlighting(txt=file.read())
            else:
                textbox.insert('end', file.read())  # Insert the file contents into the textbox
            textbox.changed_since_saved = False # Reset the changed flag since we just opened the file
            textbox.history.stackify()                  # Add the file contents to the undo stack
        logger.debug(f'Wrote file to textbox: {full_path}')

    def write_textbox_to_file(self, full_path:str, textbox:Textbox) -> None:
        ''' Private method to write file to disk. Needs encoding option. '''
        with open(full_path, "w") as file:
            txt = textbox.get(1.0, 'end')
            if len(txt) > 1:   
                txt = txt[:-1] # Trailing newline character that needs to be removed
            file.write(txt)
        # Update the textbox properties
        path_parts = self.parts_from_file_path(full_path)
        textbox.meta.set_meta(tk_name=self.controller.view.tabs.cur_tab_tk_name(),
                    full_path=full_path,
                    file_path=path_parts['path'], 
                    file_name=path_parts['file'], )
        textbox.changed_since_saved = False
        self.controller.view.tabs.set_properties(textbox.meta.tk_name, text=textbox.meta.file_name)
        # Update the window title
        self.controller.app.title(f"{self.conf.app_title} - {textbox.meta.file_name}")
        logger.debug(f'Wrote file to textbox: {full_path}')
