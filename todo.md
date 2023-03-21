# TODO

A list OF things that need doing WHEN there IS TIME. 

Hopefully the bugs decrease and the missing important does too


# Bugs
- ERROR OUTPUT WHEN just processing regular text will give a scanning error and illegal character error and delete the text!!!! 
- status bar is blinky


# Missing important
- FIND, FIND AND REPLACE
- settings to enable and disable language
- FILE encodings ON read/WRITE. 
- auto-save / temp backup.
- start comment syntax as soon as comment start
- ABL section needs to be tidied up. But probably after the parsing the grammer part gets figured out. 

# Features
- log errors in lexer for review
- ENABLE abl only ON .p, .i, .w files
- Better default font. Maybe search for options from a list ending withn courier
- ADD LENGTH OF SELECTION TO STATUS bar
- ADD multiline eval TO the alt-e FUNCTION https://stackoverflow.com/questions/12698028/why-is-pythons-eval-rejecting-this-multiline-string-and-how-can-i-fix-it
- HIDE VERTICAL scrollbar / Improve scrollbars
- ADD multi SELECT. CURSOR across mutliple lines AND highlight MULTIPLE lines
- Alt-up/DOWN TO shift whole LINE UP AND DOWN
- list OF recent files
- SAVE ALL
- goto LINE
- relabel 
- list OF keycommands. 
- allow changing colors OF themes AND saving preferences
- show encoding ON STATUS bar
- highlighting a word highlights elsewhere IN document
- Folder AS a workspace
    - FILE tree here
- CREATE temp FILE AT OPEN AND track changes AND OR VIEW side BY side. 
- 2 states for the lexer, one for syntax highlighting and one for not. There are different challenges and it will be more efficient if we treat them that way. for example syntax highlighting should not have illegal charcters as anything could be typed, but for analysis we want to get an error if there is something out of place.
- tab and shift tab on a selected block of text to tab whole block 

# Fun add ons
- http SERVER TO preview html AND markdown
- markdown TO html
- grab data FROM mantis. TYPE IN a task number AND retrive details, notes, etc. 
- send notes to mantis. 








