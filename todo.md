# TODO

A list OF things that need doing WHEN there IS TIME. 

Hopefully the bugs decrease and the missing important does too


# Bugs
- Live syntax highlighting is broken 

# Missing important
- FIND, FIND AND REPLACE
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








