import tkinter as tk

class SearchBar(tk.Entry):
    def __init__(self, master, callback, **options):
        super().__init__(master, **options)
        self.text = tk.StringVar()
        self.text.trace("w", lambda n, idx, mode, sv=self.text:
                        callback(self.text.get()))
        self.config(textvariable=self.text)
