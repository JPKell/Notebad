# Standard Library imports
from tkinter import StringVar
# Local imports
from modules.logging import Log
from settings        import Configuration
from widgets         import NText

cfg = Configuration()
logger = Log(__name__)

class Editor:
    def __init__(self, text: NText) -> None:
        logger.debug("Editor init")
        # Gather IDE objects
        self.text = text
        
        self.current_find = ""
        self.current_find_positions = []
        self.find_position_index = 0
        self.find_case = 1    # Default the find entry to search case-insensitive. Switch to 0 to make case-sensitive

    def add_indent(self) -> None:
        ''' Adds an indent to the textbox '''
        #Get the current cursor position
        cursor_pos = self.text.index('insert')
        x_pos = int(cursor_pos.split('.')[1])
        # Adjust the cursor position to the nearest indent
        x_pos = x_pos % cfg.indent_size
        self.text.insert('insert', ' ' * (cfg.indent_size - x_pos))
        return 'break'

    def get_current_line_text(self) -> str:
        ''' Return the text of the current line including the newline character '''
        return self.text.get('insert linestart', 'insert lineend')
    
    def get_previous_line(self) -> str:
        ''' Return the text of the previous line including the newline character '''
        return self.text.get('insert -1l linestart', 'insert -1l lineend')
    
    def get_trailing_word_and_index(self) -> tuple:
        ''' Return the word the cursor is currently on or just ahead of. 
            This is great for syntax highlighting since we can return the
            word before a space and handle it. 

            This can get language specific because ABL can have a hypen in the word or 
            a number of other things.
        '''
        cur_index = self.text.index('insert')
        # If we are at the start of a line dont try to get the word. 
        if cur_index[-2:] == '.0':
            return '', (cur_index, cur_index)
        
        ln,col = cur_index.split('.')
        offset = 1
        if int(col) < 3:
            word = self.text.get(f'{ln}.0', 'insert')
        else:
            word = self.text.get(f'insert -{offset}c wordstart', 'insert')

        # If the word is a space we are past the end of the word and need to move
        # back one more character.
        if word == ' ':
            offset = 2
            word = self.text.get(f'insert -{offset}c wordstart', 'insert')

        if word == '  ': # Double space, lets assume we dont want that word
            return '', (cur_index, cur_index)

        # There is an annoying trait of tkinter where if you are at the start 
        # of the line and the line above is empty, the index will be at the 
        # start of the line above. So we need to check for this. 
        # Perhaps there is a better way. 
        idx = self.text.index(f'insert -{offset}c wordstart')
        idx = idx.split('.')
        cur_index = cur_index.split('.')
        start_index = f"{cur_index[0]}.{idx[1]}"
        
        # The offset here is to try to make up for 
        index = (start_index, self.text.index(f'insert -{offset - 1}c'))  # Might need to adjust the end index. 
        return word, index

    def get_selection(self) -> str:
        ''' Return the text selected in the textbox '''
        # Throws an error if there is no selection so we look for the tag first
        if self.text.tag_ranges('sel') == (): 
            return ""
        else:
            return self.text.get('sel.first', 'sel.last')

    def add_newline(self) -> None:
        ''' There are times we need to add a new line. For instance the 
            Enter key on the numberpad does not create a new line. '''
        self.text.insert('insert', '\n')
        # Have the window scroll to the new line
        self.text.see('insert')

    def clear_all(self):
        ''' Clears all text in the textbox '''
        self.text.delete("1.0", "end")
        logger.debug("Cleared all text")

    def delete_cur_line(self) -> None:
        ''' Delete the current line '''
        self.text.delete('insert linestart', 'insert lineend')

    def delete_line(self) -> None:
        ''' Delete the current line and remove the blank line.
            More for the users use than the delete_cur_line function '''
        self.text.delete('insert linestart', 'insert lineend+1c')

    def delete_selection(self):
        self.text.delete('sel.first', 'sel.last')

    def get_all(self) -> str:
        ''' Returns all text in the textbox '''
        return self.text.get("1.0", "end - 1c")

    def set_find_case(self, toggle_value):
        ''' Set find_case to 0 - case-sensitive, or 1 - case-insensitive '''
        self.find_case = toggle_value

        # Reset current find so that the results are recalculated
        self.current_find = ""

    def find_text(self, find_txt, direction=1):
        ''' Clear all current "find" tags and loop through the textbox
            to find any current matching text '''
        self.text.delete_tags_by_name("find")

        if find_txt != self.current_find:
            self.current_find = find_txt
            self.current_find_positions = []
            self.find_position_index = 0

            start_index = "1.0"
            count_matches = StringVar()


            while start_index != "end":
                find_position = self.text.search(find_txt, start_index, stopindex="end", count=count_matches,
                                               nocase=self.find_case)    # Search for matching case (0) or any case (1 - Default)

                # Tkinter error is thrown if an empty position is passed.
                # Instead, break out of loop if that happens.
                if find_position == "":
                    break

                start_index = "%s + %sc" % (find_position, int(count_matches.get()) + 1)

                # Update find_positions list
                self.current_find_positions.append("%s + %sc" % (find_position, count_matches.get()))

            # Update status bar with find information
            # self.tb.footer.set_status(f"Find Result {self.find_position_index + 1} of {len(self.current_find_positions)}", revert=False)

            self.find_next(direction=0)

            return 'break'

        self.find_next(direction=direction)

        return "break"

    def find_next(self, direction=1):
        ''' Move to the first/next/prev result in the find_positions list.
            Direction can equal 1, -1 or 0. 0 sets the find index to 0 for a new find to start from the top '''

        if self.current_find_positions == []:
            # self.tb.footer.set_status("No results found...", revert=True)
            self.text.bell()   # Play system bell
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

        # self.tb.footer.set_status(f"Find Result {self.find_position_index + 1} of {len(self.current_find_positions)}",
                                #   revert=False)

        find_position_and_chars = self.current_find_positions[self.find_position_index]
        position = find_position_and_chars.split("+")
        self.text.tag_add("find", position[0], find_position_and_chars)

        # Make sure that the find result is moved into view
        self.text.see(find_position_and_chars)

    def move_line(self, direction):
        ''' Move a line or selection of lines up or down. '''
        '''
        SELECTION MOVE CODE - WIP...
        # Check for selection text
        if self.get_selection() != "":
            # Reset the cursor position
            # self.tb.set_position('insert + %sl' % direction)

            # Get indexes for first and last line of selection
            first_line = self.tb.index('sel.first')
            last_line = self.tb.index('sel.last')

            if self.tb.index('insert') < first_line:
                print("Moving on up!")
            elif self.tb.index('insert') > first_line:
                print("Moving down!")

            # Create the start and end indexes for the selection lines
            start_selection = self.tb.split_index(first_line)
            end_selection = self.tb.split_index(last_line)
            selection_text = self.tb.get('%s.0' % start_selection[0], '%s.end' % end_selection[0])
            print(start_selection, ":", end_selection)
            print(selection_text)
        '''

        # Clear the default selection tkinter applies to the shift key
        self.text.tag_remove("sel", "1.0", "end")

        # Get indexes for destination and current lines
        destination_pos = self.text.index('insert')
        current_pos = str(float(destination_pos) + direction)

        # Use linestart/lineend to collect all the text from the line
        destination_line_txt = self.text.get(destination_pos + "linestart", destination_pos + "lineend")
        current_line_txt = self.text.get(current_pos + "linestart", current_pos + "lineend")

        # Clear the lines of any existing text
        self.text.delete(destination_pos + "linestart", destination_pos + "lineend")
        self.text.delete(current_pos + "linestart", current_pos + "lineend")

        # Insert the text on the flipped lines
        self.text.insert(current_pos + "linestart", destination_line_txt)
        self.text.insert(destination_pos + "linestart", current_line_txt)

    def duplicate_line(self):
        ''' Duplicate the current line the cursor is on '''
        current_line = self.get_current_line_text()
        self.text.insert('insert lineend', "\n" + current_line)
        self.text.set_position('insert + 1l')

