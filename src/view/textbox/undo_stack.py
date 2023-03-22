from collections import deque
from tkinter import Text

from modules.logging import Log

logger = Log(__name__)

# I bypass the tkinter undo/redo because this gives more control. 
# It may be memory inefficient and it might be better to use marks 
# in the future take a look once the language server is running. 
class History:
    def __init__(self, textbox: Text, footer) -> None:
        self.textbox = textbox
        self.conf    = textbox.conf
        self.footer  = footer
        # Stack for undo/redo
        self.undo_stack = deque(maxlen = self.conf.max_undo)
        self.redo_stack = deque(maxlen = self.conf.max_undo)
        logger.debug("History init")

    def stackify(self) -> None:
        ''' This is the undo history a deque is used to limit the size of the
            stack and make it more efficient. '''
        self.undo_stack.append(self.textbox.get("1.0", "end - 1c"))
        logger.debug(f"Stackified text {self.textbox.meta.tk_name}")
 
    def undo(self) -> None:
        ''' This is the undo function. It pops the last item off the undo stack 
            and pushes the current text onto the redo stack.'''
        try:
            cur_txt = self.textbox.get("1.0", "end - 1c")
            self.redo_stack.append(cur_txt)
            txt = self.undo_stack.pop()
            self.textbox.editor.clear_all()
            self.textbox.insert("0.0", txt)
            logger.debug(f"Undo {self.textbox.meta.tk_name}")
        except IndexError:
            self.textbox.footer.set_status("Nothing to undo")
            logger.debug("Nothing to undo")

    def redo(self) -> None:
        ''' This is the redo function. It pops the last item off the redo stack
            and pushes the current text onto the undo stack.'''
        try:
            txt = self.redo_stack.pop()
            self.undo_stack.append(txt)
            self.textbox.editor.clear_all()
            self.textbox.insert("0.0", txt)
            logger.debug(f"Redo {self.textbox.meta.tk_name}")
        except IndexError:
            self.textbox.footer.set_status("Nothing to redo")
            logger.debug("Nothing to redo")