# Local imports
from modules.logging import Log
from widgets import NText
# Relative imports
from .editor import Editor


logger = Log(__name__)

class Clipboard:
    ''' Clipboard management
        The OS can provide some of these functions, but this gives us more control
        These should override the OS clipboard functions. Except for the paste function,
        which should be able to paste from the OS clipboard as well as our own. 
        This all might be excessive management and I should just use the OS clipboard
    '''
    def __init__(self, editor: Editor, text: NText) -> None:
        # Gather IDE objects
        self.editor = editor
        self.text   = text
        self.clipboard = ""
        logger.debug("Clipboard init")

    def cut_text(self) -> None:
        ''' Don't run with scissors '''
        self.copy_text()
        self.editor.delete_selection()  
        logger.debug(f"Cut text")

    def copy_text(self) -> None:
        ''' Plagiarism is bad ''' 
        self.clipboard = self.editor.get_selection()
        self.text.clipboard_append(self.clipboard)
        logger.debug(f"Copied text")

    def paste_text(self) -> None:
        ''' Hand me that paper bag '''
        # If there is text selected, delete it
        if self.text.has_selection():
            self.editor.delete_selection()
        self.text.insert('insert', self.clipboard)
        logger.debug(f"Pasted text")
