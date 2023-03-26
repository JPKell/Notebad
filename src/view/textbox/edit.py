import tkinter
from tkinter import Text, StringVar, SEL_FIRST, SEL_LAST

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

    def delete_selection(self):
        self.tb.delete('sel.first', 'sel.last')

    def get_all(self) -> str:
        ''' Returns all text in the textbox '''
        return self.tb.get("1.0", "end - 1c")

    def find_text(self, find_txt, clear_tags=False):
        ''' Clear all current "find" tags and loop through the textbox
            to find any current matching text '''
        if clear_tags:
            for tag in self.tb.tag_names():
                self.tb.tag_remove(tag, "1.0", "end")

        start_index = "1.0"
        count_matches = StringVar()

        while start_index != "end":
            find_position = self.tb.search(find_txt, start_index, stopindex="end", count=count_matches)

            # Tkinter error is thrown if an empty position is passed.
            # Instead, break out of loop if that happens.
            if find_position == "":
                break

            start_index = "%s + %sc" % (find_position, int(count_matches.get()) + 1)
            self.tb.tag_configure("find", background="green")
            self.tb.tag_add("find", find_position, "%s + %sc" % (find_position, count_matches.get()))

            # Update current find and find_positions list
            if find_txt != "":
                if find_txt != self.current_find:
                    self.current_find = find_txt
                    self.current_find_positions = []
                self.current_find_positions.append("%s + %sc" % (find_position, count_matches.get()))


            # Move selection into view
            #self.tb.see("%s + %sc" % (find_position, count_matches.get()))

        print(self.current_find)
        print(self.current_find_positions)