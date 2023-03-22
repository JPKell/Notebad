from tkinter.ttk import Frame, Scrollbar

from modules.logging import Log

logger = Log(__name__)

class Scrollbars:
    ''' The place where ancient scholars hang out. s '''

    def __init__(self, textbox: Frame) -> None:
        self.textbox = textbox
        self.vertical = Scrollbar(self.textbox.frame, orient='vertical')
        self.horizontal = Scrollbar(self.textbox.frame, orient='horizontal')
        self.vertical_visible = True
        self.horizontal_visible = True
        self._make_scrollbars()
        self.hide_unused()
        logger.debug("Scrollbars initialized")

    def _make_scrollbars(self) -> None:
        ''' Add vertical and horizontal scrollbars to the text area '''
        self.vertical.config(command=self._scroll_multi)
        self.horizontal.config(command=self.textbox.xview)
        self.vertical.pack(side='right', fill='y')
        self.horizontal.pack(side='bottom', fill='x')

        # The scrollbars require a connection both ways. So changes to one will
        # be reflected in the other.
        # Connect the scrollbars to the text area
        self.textbox.configure(
            xscrollcommand=self.horizontal.set, 
            yscrollcommand=self._update_scroll
            )

    # These are not used to scroll both, btu might be used to do diffs in the future
    def _scroll_multi(self, action, position, type=None) -> None:
        ''' Controls multile widges with one scrollbar '''
        self.textbox.yview_moveto(position)
        # self.linenumbers.yview_moveto(position)

    def _update_scroll(self, first, last, type=None) -> None:
        self.textbox.yview_moveto(first)
        # self.linenumbers.yview_moveto(first)
        self.vertical.set(first, last)


    # This isn't the best since you have to redraw the text area to fit the 
    # scrollbar in the pack. There might be a way to do it better. Perhaps 
    # anchoring the text window and removing fill or something.  
    def hide_unused(self) -> None:
        ''' This checks the scrollbars to see if they are needed. 
            Currently the vertical scrollbar is always visible and
            the horizontal scrollbar is only visible when needed.

            Updates every 100ms.

            The vertical scrollbar could be hidden but it needs more logic
            to work well with opening files that are longer than the window.
        '''
        horizontal = self.horizontal.get()
        if self.horizontal_visible == False and (horizontal[0] != 0 or horizontal[1] != 1):
            self.horizontal_visible = True
            # Must remove the textbox, then add the scrollbar, then add the textbox
            self.textbox.pack_forget()
            self.horizontal.pack(side='bottom', fill='x')
            self.textbox.pack(fill='both', expand=True)
            logger.debug("Showing horizontal scrollbar")

        vertical = self.vertical.get()
        if self.vertical_visible == False and (vertical[0] != 0 or vertical[1] != 1):
            self.vertical_visible = True
            # Must remove the textbox, then add the scrollbar, then add the textbox
            self.textbox.pack_forget()
            self.vertical.pack(side='right', fill='y')
            self.textbox.pack(fill='both', expand=True)
            logger.debug("Showing vertical scrollbar", )

        # Once both are set we can stop trying to show them 
        if not (self.horizontal_visible and self.vertical_visible):
            logger.verbose(f"Checking for scrollbars {self.textbox.meta.tk_name}")
            self.textbox.after(250, self.hide_unused)

