from tkinter import IntVar, Text

from langs.abl import syntax_words


class SyntaxMarker:
    ''' This code is from a video here https://coderslegacy.com/python-gui-projects-with-tkinter-code/

    '''
    def __init__(self, textbox: Text):
        self.textbox = textbox

        ## Load the syntax highlighting tags
        # This code from https://coderslegacy.com/python-gui-projects-with-tkinter-code/
        
        font = self.textbox.font
        self.textbox.tag_configure("red",    foreground = "#E26D5C", font=font)
        self.textbox.tag_configure("green",  foreground = "#C3EB78", font=font)
        self.textbox.tag_configure("blue",   foreground = "#3066BE", font=font)
        self.textbox.tag_configure("orange", foreground = "#DC851F", font=font)
        self.textbox.tag_configure("purple", foreground = "#665FAB", font=font)
        self.textbox.tag_configure("yellow", foreground = "#FAF2A1", font=font)
        self.textbox.tag_configure("cyan",   foreground = "#80DED9", font=font)
 
        self.tags = ["red","green","blue","orange","purple","yellow","cyan",]
 
        self.syntax_color_list = ['red', 'green', 'blue', 'orange', 'purple', 'yellow', 'cyan']


    def tagHighlight(self):
        start = "1.0"
        end = "end"
         
        for syntax_color, word_list in syntax_words.items():

            for word in word_list:
                self.textbox.mark_set("matchStart", start)
                self.textbox.mark_set("matchEnd", start)
                self.textbox.mark_set("SearchLimit", end)
 
                mycount = IntVar()
                 
                while True:
                    index= self.textbox.search(word,"matchEnd","SearchLimit", count=mycount, regexp = False)
 
                    if index == "": break
                    if mycount.get() == 0: break
 
                    self.textbox.mark_set("matchStart", index)
                    self.textbox.mark_set("matchEnd", "%s+%sc" % (index, mycount.get()))
 
                    preIndex = "%s-%sc" % (index, 1)
                    postIndex = "%s+%sc" % (index, mycount.get())
                     
                    if self.check(index, preIndex, postIndex):
                        self.textbox.tag_add(syntax_color, "matchStart", "matchEnd")
                         
 
    def check(self, index, pre, post):
        letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p",
                   "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
 
        if self.textbox.get(pre) == self.textbox.get(index):
            pre = index
        else:
            if self.textbox.get(pre) in letters:
                return 0
 
        if self.textbox.get(post) in letters:
            return 0
        return 1
 
 
    def scan(self):
        start = "1.0"
        end = "end"
        mycount = IntVar()
 
        regex_patterns = [r'".*"', r'#.*']
 
        for pattern in regex_patterns:
            self.textbox.mark_set("start", start)
            self.textbox.mark_set("end", end)
 
            num = int(regex_patterns.index(pattern))
 
            while True:
                index = self.textbox.search(pattern, "start", "end", count=mycount, regexp = True)
 
                if index == "": break
 
                if (num == 1):
                    self.textbox.tag_add(self.tags[4], index, index + " lineend")
                elif (num == 0):
                    self.textbox.tag_add(self.tags[3], index, "%s+%sc" % (index, mycount.get()))
 
                self.textbox.mark_set("start", "%s+%sc" % (index, mycount.get()))
 