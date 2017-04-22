import manager
import tkinter as tk
import font2img as f2i
import config


class FontButton(tk.Button):
    def __init__(self, name, callback, w=500, h=25, master=None, **options):
        super().__init__(master, **options)

        self.config(borderwidth=1, width=w)
        self.font = manager.fonts[name]

        hpad = int(h/100)
        wpad = int(w/100)
        size = int(h/1.5)
        self.font.set_size(size)
        text = "xgcZa"
        photo = f2i.multiline_tk(text, self.font.pilfont,
                                 (int(w/4), int(h+2*hpad)),
                                 padx=wpad, pady=hpad)
        self.config(image=photo, text=self.font.name, compound=tk.LEFT,
                    anchor=tk.W, font=config.body_font(int(size/1.2)))
        self.image = photo
        self.config(command=callback)


class FontList(tk.Frame):
    def generate_command(self, font):
        return lambda *args: self.show_info(font)

    def __init__(self, info_callback, num_list=20, master=None, **options):
        """ Takes a list of string dict indices and displays them """
        super().__init__(master, **options)
        self.current_display = []
        self.num_list = num_list
        self.start = 0
        self.refresh()
        self.show_info = info_callback

    def refresh(self):
        for i in self.current_display:
            i.grid_forget()

        self.current_display = []
        for num, name in enumerate(manager.keys[
                                   self.start:self.start + self.num_list]):
            # +1 for the search bar
            f = FontButton(name, self.generate_command(name), 500, 25)
            f.grid(column=1, row=num, in_=self,
                   sticky=tk.E+tk.N+tk.W+tk.S, padx=0, pady=0, columnspan=2)
            self.current_display.append(f)
