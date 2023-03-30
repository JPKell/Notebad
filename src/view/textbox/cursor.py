from tkinter import Text, INSERT

class Cursor:

    def __init__(self, textbox: Text) -> None:
        self.textbox = textbox

    def has_selection(self) -> bool:
        ''' Returns True if there is text selected '''
        return self.textbox.tag_ranges('sel') != ()

    def select_all(self) -> None:
        ''' Select all text in the textbox '''
        self.textbox.tag_add('sel', 1.0, 'end')

    def get_position(self):
        ''' Get the current input cursor position '''
        return self.textbox.index(INSERT)

    def set_position(self, new_position):
        ''' Set the current input cursor position '''
        self.textbox.mark_set('insert', new_position)

    def split_index(self, current_index='index'):
        ''' Get a selected index or the current input cursor position as a list of
            separate line and char values '''
        current_pos = self.textbox.index(current_index)
        current_pos_split = current_pos.split(".")
        return current_pos_split
