from conf import Configuration
from modules.logging import Log

cfg = Configuration()
logger = Log(__name__)

class Meta:
    def __init__(self,textbox, tabs):
        self.textbox = textbox
        self.tabs = tabs
        self._file_name = cfg.new_file_name  # class property
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
        self.textbox.footer.lang_lbl.config(text=language)
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
        logger.debug(f"Meta data set: {self.file_name}")

