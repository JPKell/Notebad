from tkinter import ttk
s = ttk.Style()
s.theme_use('classic')
b = ttk.Notebook(None)
bClass = b.winfo_class()
print(bClass)
layout = s.layout('TButton')


print(s.element_options('TNotebook.Tab'))