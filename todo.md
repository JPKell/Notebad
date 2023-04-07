# TODO

A list OF things that need doing when there is time. 

Hopefully the bugs decrease and the missing important does too


# Bugs
- Live syntax highlighting is broken 

# Missing important
- FIND AND REPLACE
- settings to enable and disable language
- FILE encodings ON read/WRITE. 
- auto-save / temp backup.
- start comment syntax as soon as comment start
- ABL section needs to be tidied up.
  - able tokens from kw_master 


# Refactor
## Priority

- Textbox needs to be able to freeze state when switching tab. 
  - The issue is the functions with callbacks keep running in the background. even when tab is closed. That's terrible for longer sessions. That could get out of hand with many tabs open. 
  - Currently this is only the scrollbar because they are on a couple hundred millisecond callback loop

# Language
- Continue to validate the effects of the language changes
- Check that indentation rules are being followed 
- Test that changes are idempotent and can be run repeatedly without changing the outcome. 
- . or colon followed by whitespace. should be a rule.

# Features
- log errors in lexer for review

# IDE functions 
- multiselect. cursor across multiple lines and highlight columns of multiple lines
- Alt-up/down to shift whole line up and down
- list of recently opened files
- save all Ctrl+Shift+S
- goto line Ctrl-g
- relabel all instances of variable 
- highlighting a word highlights elsewhere in document
- create temp file at open and track changes 
  - Figure out how to do a diff view? 
- tab and shift tab on a selected block of text to tab whole block
- Alt-j to select the next matching instance (multi-select same word over multiple lines)
- Bookmarks for quickly moving back and forth between sections of text
- Ctrl-w to select an entire word (depending on users settings):
  - First press - select word from inside CamelCase/snake_case, e.g. selection around "Chosen" in myChosenWord
  - Second press - select the rest of the word 
  - Third press (if text is inside parenthesis) - select the rest of the text within the parenthesis
  - Third/Fourth press (Third if previously no parenthesis) - select the rest of the line, minus any whitespace at the start or end
  - Fourth/Fifth press - select the rest of the line including any leading/trailing whitespace
  - Fifth/Sixth press - select the rest of the current code block/paragraph
  - Sixth/Seventh press - select the whole document (Ctrl-a style...)
- Typing any surrounding characters when text is selected will auto-surround the selection. "" '' [] {} () 
- Auto-complete available for built-in keywords as well as user defined variables, functions, methods, etc...
- Auto-double characters, e.g. typing "(" adds "()" to the document with the cursor between them

## UI / system
- UI window for changing and saving preferences
- allow changing colors of themes 
- folder as a workspace
    - file tree widget can be used here
- list OF key commands.  

## Nifty
- add multiline python eval to the alt-e function https://stackoverflow.com/questions/12698028/why-is-pythons-eval-rejecting-this-multiline-string-and-how-can-i-fix-it


# Fun add ons
- http SERVER TO preview html AND markdown
- markdown TO html
- grab data FROM mantis. TYPE IN a task number AND retrieve details, notes, etc. 
- send notes to mantis. 
- create and edit XML files, with a function that allows quick tabbing between tag data for fast edits.








