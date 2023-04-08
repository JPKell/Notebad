from settings import Configuration
from modules.logging import Log
import os

cfg = Configuration()
logger = Log(__name__)

class Meta:
    def __init__(self, ide, tabs):
        self.ide = ide
        self.tabs = tabs
        self._file_name = cfg.new_file_name  # class property
        self._recent_files = os.path.join(cfg.current_dir, 'app_data/recent_files.txt')
        self._language  = None  # class property
        self.tk_name    = None
        self.file_path  = None
        self.full_path  = None
        self.changed_since_saved = False
        logger.debug("Meta init")

    @property
    def file_name(self) -> str:
        return self._file_name
    
    @file_name.setter
    def file_name(self, file_name:str) -> None:
        ''' Updating the filename will also update the tab name '''
        self._file_name = file_name
        self.tabs.tab(self.tk_name, text=file_name)

    @property
    def language(self) -> str:
        return self._language
    
    @language.setter
    def language(self, language:str) -> None:
        ''' Updating the language will also update the syntax highlighting 
            if it is enabled. '''
        self._language = language
        # self.ide.footer.lang_lbl.config(text=language)
        logger.debug(f"Language set to: {language}")


    # This could be tidied up. Also if we get a full path we should be able to
    # get the file name and path from that. so do that. Keep in mind windows and
    # linux paths are different.  
    def set_meta(self, file_path:str=None, file_name:str=None, full_path:str=None, tk_name:str=None) -> None:
        ''' Set various pieces of meta data. The tk name is the name of the tab in 
            tkinter land '''
        langs = {'py': 'python', 'p': 'abl', 'i': 'abl', 'w': 'abl', 'cls': 'abl', 'md': 'markdown', 'txt': 'text'}

        self.tk_name = tk_name      if tk_name   else self.tk_name
        self.file_path = file_path  if file_path else self.file_path
        self.file_name = file_name  if file_name else self.file_name
        self.full_path = full_path  if full_path else self.full_path
        
        if self.file_name:
            self.language = langs.get(self.file_name.split('.')[-1], 'text')

        self.add_recent_file()
        logger.debug(f"Meta data set: {self.file_name}")

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
