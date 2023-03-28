from tkinter import Text, StringVar
from settings import Configuration
from modules.logging import Log

cfg = Configuration()
logger = Log(__name__)

class Editor:
    def __init__(self, textbox: Text) -> None:
        self.tb = textbox
        logger.debug("Editor init")
        self.current_find = ""
        self.current_find_positions = []
        self.find_position_index = 0
        self.tb.tag_configure("find", background=cfg.find_background)
        self.find_case = 1    # Default the find entry to search case-insensitive. Switch to 0 to make case-sensitive

    def add_indent(self) -> None:
        ''' Adds an indent to the textbox '''
        #Get the current cursor position
        cursor_pos = self.tb.index('insert')
        x_pos = int(cursor_pos.split('.')[1])
        # Adjust the cursor position to the nearest indent
        x_pos = x_pos % cfg.indent_size
        self.tb.insert('insert', ' ' * (cfg.indent_size - x_pos))
        return 'break'

    def get_current_line_text(self) -> str:
        ''' Return the text of the current line including the newline character '''
        return self.tb.get('insert linestart', 'insert lineend')
    
    def get_previous_line(self) -> str:
        ''' Return the text of the previous line including the newline character '''
        return self.tb.get('insert -1l linestart', 'insert -1l lineend')
    
    def get_trailing_word_and_index(self) -> tuple:
        ''' Return the word the cursor is currently on or just ahead of. 
            This is great for syntax highlighting since we can return the
            word before a space and handle it. 

            This can get language specific because ABL can have a hypen in the word or 
            a number of other things.
        '''
        cur_index = self.tb.index('insert')
        # If we are at the start of a line dont try to get the word. 
        if cur_index[-2:] == '.0':
            return '', (cur_index, cur_index)
        
        ln,col = cur_index.split('.')
        offset = 1
        if int(col) < 3:
            word = self.tb.get(f'{ln}.0', 'insert')
        else:
            word = self.tb.get(f'insert -{offset}c wordstart', 'insert')

        # If the word is a space we are past the end of the word and need to move
        # back one more character.
        if word == ' ':
            offset = 2
            word = self.tb.get(f'insert -{offset}c wordstart', 'insert')

        if word == '  ': # Double space, lets assume we dont want that word
            return '', (cur_index, cur_index)

        # There is an annoying trait of tkinter where if you are at the start 
        # of the line and the line above is empty, the index will be at the 
        # start of the line above. So we need to check for this. 
        # Perhaps there is a better way. 
        idx = self.tb.index(f'insert -{offset}c wordstart')
        idx = idx.split('.')
        cur_index = cur_index.split('.')
        start_index = f"{cur_index[0]}.{idx[1]}"
        
        # The offset here is to try to make up for 
        index = (start_index, self.tb.index(f'insert -{offset - 1}c'))  # Might need to adjust the end index. 
        return word, index

    def get_selection(self) -> str:
        ''' Return the text selected in the textbox '''
        # Throws an error if there is no selection so we look for the tag first
        if self.tb.tag_ranges('sel') == (): 
            return ""
        else:
            return self.tb.get('sel.first', 'sel.last')

    def add_newline(self) -> None:
        ''' There are times we need to add a new line. For instance the 
            Enter key on the numberpad does not create a new line. '''
        self.tb.insert('insert', '\n')
        # Have the window scroll to the new line
        self.tb.see('insert')

    def clear_all(self):
        ''' Clears all text in the textbox '''
        self.tb.delete("1.0", "end")
        logger.debug("Cleared all text")

    def delete_cur_line(self) -> None:
        ''' Delete the current line '''
        self.tb.delete('insert linestart', 'insert lineend')

    def delete_line(self) -> None:
        ''' Delete the current line and remove the blank line.
            More for the users use than the delete_cur_line function '''
        current_line, current_char = self.tb.cursor.get_coordinates()
        self.tb.delete('insert linestart', current_line + ".end+1c")


    def delete_selection(self):
        self.tb.delete('sel.first', 'sel.last')

    def get_all(self) -> str:
        ''' Returns all text in the textbox '''
        return self.tb.get("1.0", "end - 1c")

    def set_find_case(self, toggle_value):
        ''' Set find_case to 0 - case-sensitive, or 1 - case-insensitive '''
        self.find_case = toggle_value

        # Reset current find so that the results are recalculated
        self.current_find = ""

    def find_text(self, find_txt, direction=1):
        ''' Clear all current "find" tags and loop through the textbox
            to find any current matching text '''
        self.tb.delete_tags_by_name("find")

        if find_txt != self.current_find:
            self.current_find = find_txt
            self.current_find_positions = []
            self.find_position_index = 0

            start_index = "1.0"
            count_matches = StringVar()


            while start_index != "end":
                find_position = self.tb.search(find_txt, start_index, stopindex="end", count=count_matches,
                                               nocase=self.find_case)    # Search for matching case (0) or any case (1 - Default)

                # Tkinter error is thrown if an empty position is passed.
                # Instead, break out of loop if that happens.
                if find_position == "":
                    break

                start_index = "%s + %sc" % (find_position, int(count_matches.get()) + 1)

                # Update find_positions list
                self.current_find_positions.append("%s + %sc" % (find_position, count_matches.get()))

            # Update status bar with find information
            self.tb.footer.set_status(f"Find Result {self.find_position_index + 1} of {len(self.current_find_positions)}", revert=False)

            self.find_next(direction=0)

            return 'break'

        self.find_next(direction=direction)

        return "break"

    def find_next(self, direction=1):
        ''' Move to the first/next/prev result in the find_positions list.
            Direction can equal 1, -1 or 0. 0 sets the find index to 0 for a new find to start from the top '''
        if self.current_find_positions == []:
            self.tb.footer.set_status("No results found...", revert=True)
            self.tb.bell()   # Play system bell
            return

        # Update index to next/prev find result
        self.find_position_index += direction

        # Wrap around again if user goes past the end.
        # If the direction is 0 then reset the index to 0.
        # This is for initial find results, otherwise you always end up on index 1
        if self.find_position_index > len(self.current_find_positions) - 1 or direction == 0:
            self.find_position_index = 0
        if self.find_position_index < 0:
            self.find_position_index = len(self.current_find_positions) - 1

        self.tb.footer.set_status(f"Find Result {self.find_position_index + 1} of {len(self.current_find_positions)}",
                                  revert=False)

        find_position_and_chars = self.current_find_positions[self.find_position_index]
        position = find_position_and_chars.split("+")
        self.tb.tag_add("find", position[0], find_position_and_chars)

        # Make sure that the find result is moved into view
        self.tb.see(find_position_and_chars)
