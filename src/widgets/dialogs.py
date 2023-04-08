from tkinter import messagebox, filedialog


_filetypes = [('All Files', '*.*'),
                          ('Progress Include Files', '*.i'),
                          ('Progress Files', '*.p'),
                          ('Progress Window Procedure Files', '*.w'),
                          ('Python Files', '*.py'),
                          ('Text Documents', '*.txt')]

def prompt_yes_no(title:str, msg:str, callback:callable) -> None:
    ''' Show a message and call a callback function when done '''
    if messagebox.askokcancel(title, msg):
        callback()

def open_file_dialog(filetypes:list=_filetypes) -> str:  
    ''' Open a file dialogue and returns the path the user selected 
        - filetypes is a list of tuples in the format (description, extension)
        - There is a default list of filetypes that is used unless overridden
    '''
    file_path = filedialog.askopenfilename(filetypes=filetypes)
    return file_path

def save_file_dialog(file_name:str=None, path:str=None) -> str:
    filepath = filedialog.asksaveasfilename(defaultextension=".txt",
                                            initialfile=file_name,
                                            initialdir=path,
                                            filetypes=_filetypes)
    return filepath