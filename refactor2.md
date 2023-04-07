This is my second big refactor of this, and that's kinda been the way projects have been going for me. I get an idea, i run with it, it gets unweildly then I refactor. Usually the first refactor breaks into major classes and the second refactor makes the things I end up doing over and over easier. 

# Refactor goals
- Simplify calls from view to controlver via events
- Decrease boilerplate code through Custom widget classes
- Allow tabs to hold arbitrary widgets and retain tab behaviours
- Set up left and right gutters
  
# Events

My mental model of these events is like a website. You have the webpage (view) that is just html and buttons and when the user clicks on something it sends a message to the server. The server (controller) takes the request and any data the user has stored in a cookie (event). Sends all that information to the backend (model) of the site which processes and sends back data to fill in on the site. 

Heres a simple example to demo the idea. I have created custom button classes that have an attribute btn and then a few methods and superclass from a ttk.Button. Each button when it's created gets all the extra things we want a button to do in out app without having to write it every time. This also allows us to change the look and feel in once place. 

Once of the goals is to simplify things. so rather than writing lambda every time there will be a _event() that will generate events. It can also be used for other common times we want to use lambdas for events. 

Every button created will now be bound automatically to 3 events. A button click which will fire an internal function. That internal function that gets called will be passed in when it's initialized or automatically set up depending on the use case. It also responds to a global message to toggle theme. Wherever possible we should be using ttk elements because they will have the forest-* theme and get toggled automatically. Some elements do not have a ttk theme. Primarily menus and text boxes. So those will be best looking after their own appearance. Again those will get custom classes so it's set up from the get go. 

And finally the event "Marco" is bound to the method polo. This just demonstrates that when an event is fired the event carries a copy of the widget that fired the event. The important thing here is that the events get sent from the highest level widget that makes sense. So anything inside a tab should send the event from the Parent class of that tab. That way the controller will have easy access to the important bits. 

``` python 
import tkinter as tk
from tkinter import ttk

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.frame = ttk.Frame(self)
        self.frame.grid(sticky='nsew')

        # This button calls test in the app class but all in the button class because it
        # has a bindong on mouse click 
        self.button = SpecialButton(self.frame,btn="ONE", text='Test', command=self.test)
        self.button.grid(sticky='nsew')

        # This uses a helper method to generate the event rather than using a lambda expression
        self.button2 = SpecialButton(self.frame,btn="TWO", text='Toggle theme', command=self._event('<<ToggleTheme>>'))
        self.button2.grid(sticky='nsew')
        self.mainloop()

    # This could be defined with or without a parameter if the function was only ever sending one event. 
    def _event(self, event:str='<<DefaultEvent>>') -> object:
        def callback(): # This is the function that is returned to the caller
            self.event_generate(event)
        return callback 

    def test(self):
        print('Test main')

class SpecialButton(ttk.Button):
    def __init__(self, master, btn, **kwargs):
        super().__init__(master, **kwargs)  # Here we become a ttk.Button
        self.bind('<Button-1>', self.test)   # This binds to events on itself
        self.bind_all('<<ToggleTheme>>', self.toggle_theme) # This responds to global events
        self.bind_all('<<Marco>>', self.polo) # This responds to global events to demo the event sends widget
        self.btn = btn

    def test(self, event):
        print('Test')
        self.event_generate('<<Marco>>') # This sends an event out. Which gets picked up by the other buttons

    def polo(self, event):  # This is the event handler for the Marco event     
        print('Button:', event.widget.btn, 'polo!')  # This prints the button that sent the event 
        # Therefore we have the parent widget send the event and the controller has access to every attribute 
        # of the widget that sent the event. Full control to get anything to or from that class. 

    def toggle_theme(self, event):
        print('Toggle theme')

if __name__ == '__main__':
    App()
```

# Decreasing boilerplate code with custom classes

The idea is to override everything so that it's ready to go and the primary logic to create the view is not bogged down with boilerplate code. This may also end up with classes with multiple inheritence as there might be some default methods that we want included for some buttons, but not for others. 
Having a textbox is great but you have to build the scrollers and the line numbers very time you want to use it in a different style of tab. But if the text class just CAME with those already, that eliminates a lot of code when trying to reason about something. 

# Arbitrary widgets in tab
This kinda comes down to the custom classes too. I think we should be able to have multie different tools as tabs and they should all interact the same way (and house the event sender). Again this is a class that will run this all And likey be a frame as well. 

# Layout
I think having a file browser and other tools like schema viewer and such would be good to plan for at this stage. I envision a full length gutter down the left and right sides of the screen as optional places for frames. And maybe one across the bottom. These and all other things should be done in the grid geometry manager. It's the easiest for adding and removing widgets without having to repack everything.  

# Roadmap 

- Custom classes
  - These can be done one at a time and swapped in for existing widgets
    - textbox
      - scrollers, line numbers, text
      - themed
    - menu 
      - themed
    - tab frame
    - buttons
    - entry
      - validation set up
    - label
      - preloaded with StringVar etc.
    - checkbutton... 
  - Tabs need special attention
  - Widget base classes
    - standard set of custom methods that other classes will inherit from
- Events
  - The controller needs a good way to handle these.
    - Something like a dictionary with the event as the key and the callback the value.
    - then iterate over the dict to bind them all, much like the keybindings.
  - Once all the custom classes are set up they can start sending the events and we switch everything over
- Tabs to get the events plummed we will need the tab master class to be set up to send the events.

All in all I think that this should be fairly painless. It's a bunch of work to redo what's been done already, but I think it will be the best way forward. Get rid of these long train calls. 