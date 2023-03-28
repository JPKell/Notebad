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
        self.textbox.insert(new_position, "")

    def get_coordinates(self):
        ''' Get the current input cursor position as separate line and char values '''
        current_pos = self.textbox.index(INSERT)
        coordinates = current_pos.split(".")
        current_line = coordinates[0]
        current_char = coordinates[1]
        return current_line, current_char