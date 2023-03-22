from tkinter import Canvas

from modules.logging import Log

logger = Log(__name__)

class LineNumbers(Canvas):
    ''' Line numbers for the edge of a textbox. These are drawn on a canvas 
        and are updated when the window is changed. ''' 
    def __init__(self, textbox):
        self.conf    = textbox.conf
        super().__init__(textbox.frame, width=self.conf.line_number_width)
        # Canvas.__init__(textbox.frame)
        self.textbox = textbox
        self.color = 'grey'
        self.pack(side="left", fill="y")
        self.redraw() # Kick it off 
        logger.debug("TextLineNumbers init")
        

    def redraw(self, *args) -> None:
        ''' Redraw the line numbers on the canvas '''
        self.delete("all")

        i = self.textbox.index("@0,0")
        # Enter the endless loop
        while True:
            # Get the line dimensions in tuple (x,y,width,height,baseline)
            dline= self.textbox.dlineinfo(i)
            # Leave the loop if the line is empty
            if dline is None: 
                break
            # Get the y coordinate of the line
            y = dline[1] + 1
            # Get the line number
            linenum = str(i).split(".")[0]
            # Set the font size
            size = 10
            # 10,000+ lines should be small. Or make the canvas bigger. I like font smaller. 
            if len(linenum) > 4:
                size = 7
            self.create_text(
                2,                      # x coordinate of the text. 
                y,
                anchor="nw", 
                text=linenum,           
                font=('arial',size), 
                tags='lineno',          # Let us get the line numbers later
                fill=self.color         
                )
            # Get the next line
            i = self.textbox.index("%s+1line" % i)

        logger.verbose("Line numbers redrawn")



