from tkinter import Text

from modules.logging import Log

logger = Log(__name__)

class Clipboard:
    ''' Clipboard management
        The OS can provide some of these functions, but this gives us more control
        These should override the OS clipboard functions. Except for the paste function,
        which should be able to paste from the OS clipboard as well as our own. 
        This all might be excessive management and I should just use the OS clipboard
    '''
    def __init__(self, textbox: Text) -> None:
        self.textbox = textbox
        self.clipboard = ""
        logger.debug("Clipboard init")

    def cut_text(self) -> None:
        ''' Don't run with scissors '''
        self.copy_text()
        self.textbox.editor.delete_selection()  
        logger.debug(f"Cut text {self.textbox.meta.tk_name}")

    def copy_text(self) -> None:
        ''' Plagurism is bad ''' 
        self.clipboard = self.textbox.editor.get_selection()
        self.textbox.clipboard_append(self.clipboard)
        logger.debug(f"Copied text {self.textbox.meta.tk_name}")

    def paste_text(self) -> None:
        ''' Hand me that paper bag '''
        # If there is text selected, delete it
        if self.textbox.cursor.has_selection():
            self.textbox.editor.delete_selection()
        self.textbox.insert('insert', self.clipboard)
        logger.debug(f"Pasted text {self.textbox.meta.tk_name}")
