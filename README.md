# Notebad
An accidental project which has turned into a mildly useful notepad like editor. It wont replace your IDE, but it might give you an idea on how to implement an MVC architecture in tkinter. 


# Architecture overview

The MVC model is fairly common, and I tried my best to maintain the concepts of encaptulation that are behind the MVC model.

The three parts of MVC are:

- **Model**: The model in this case is the language lexer/parser. The lexer is a pure Python implementation of lex / yacc from a Python library [PLY](https://www.dabeaz.com/ply/). The documentation in the [git repo](https://github.com/dabeaz/ply) is excellent and explains things well. The model has no awareness of the other components. It's the business logic and that should not change base on UI changes.
- **View**: View is the UI component, in this case it's the primary interface into tk the GUI library. Any UI items are found in view and since there are many of them most items are broken out into their own files. The view is aware of the controller and should have limited access back into the controller. 
- **Controller**: The controller is the orchestrator if the app. It controls the IO but in user input and filesystem access but moving data from the textbox to the model and back. The controller knows about both the view and the model. 


## Model

The language model is primarily based on ABL currently so many things are specialized. This might change in the future, but will involve a rework. HTML would be easy enough as the html module could be used. Same with Python as the ast library would be available. The language model is still very much in development so things will change but the idea is you instantiate lex with a model and you feed it txt. It returns the text as tokens, which can then be processed. The second half of PLY is unused at the moment, but would involve defining the grammar of the language. Once that is done the parser can be used to build and abstract syntax tree, and more powerful analysis can be done. It will continue to work toward this end. We might be able to get some hints from [Proparse](https://github.com/consultingwerk/proparse). 

## View

Most of the classes in the view are inheriting from tk widgets. The heirarchy looks something like

- app: Tk() root of the tk app. starts up the underlying tk interpreter
  - NoteView(): Frame() the frame houses everything within the Notebad app 
    - Menubar(): Menu() doesn't inherit directly from Menu but houses the whole menu bar
    - Tabs(): Notebook() a ttk element for the tabs
      - Textbbox(): Text() where everything happens really. 
        - LineNumbers(): Canvas() the canvas gets updated with the line numbers. Kinda a pain as it needs a proxy to work. 
        - scrollbars: Scrollbar() the scrollbars 
        - Footer(): Frame() parent frame to the labels
          - status: Label() the status you can update
          - pos_lbl: Label() the cursor position in the document


## Controller

Mainly just handles what happens to inputs and routes events to functions. 

