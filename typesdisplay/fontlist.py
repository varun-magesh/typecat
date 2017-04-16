import manager
import tkinter as tk


class FontButton(tk.Button):
    def __init__(self, name, callback, master=None):
        f = manager.fonts[name].display(500, 25, master)
        f.grid_propagate(0)
        f.configure()


class FontList(tk.Frame):
    @staticmethod
    def generate_command(font):
        return lambda *args: show_info(font)

    def __init__(self, inputlist, num_list=20):
        """ Takes a list of string dict indices and displays them """
        tk.Frame()
        self.current_display = []
        self.refresh()
        self.num_list = num_list

    def refresh(self):
        for i in self.current_display:
            i.grid_forget()

        self.current_display = []
        for num, name in enumerate(manager.keys[:self.num_list]):
            # +1 for the search bar
            f = FontButton(name, command=FontList.generate_command(name))
            f.grid(column=1, row=num,
                   sticky=tk.E+tk.N+tk.W+tk.S, padx=0, pady=0, columnspan=2)
            self.current_display.append(f)
