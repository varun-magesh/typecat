import tkinter as tk
import config
import font2img as f2i
import manager
from font import Font


class InfoPanel(tk.Frame):

    def __init__(self, name, w=500, h=500, master=None):
        super().__init__(master, borderwidth=1, relief=tk.SOLID, width=w,
                         height=h, highlightbackground="#000000")
        hpad = int(h / 100)
        wpad = int(w / 100)
        self.font = manager.fonts[name]

        # draw title
        titlesize = int(w/len(self.font.name))
        title = tk.Label(self, text=self.font.name,
                         font=config.heading_font(titlesize),
                         padx=wpad, pady=hpad)
        title.grid(sticky=tk.N, in_=self, columnspan=2)

        # display preview
        label = tk.Label(relief=tk.SOLID, borderwidth=1)

        # TODO varying colors and randomly chosen phrases
        user_text = "Handgloves"

        # callback to set text and text size
        def set_text(text, size=self.size):
            # TODO not good practice
            if size != self.size and (type(size) == int or size.isdigit()):
                size = int(size)
                # Things get nasty if you punch in a number too big
                if(size > 200):
                    size = 200
                self.font.set_size(size)
            # TODO automatically set font size to a reasonable level when
            # started
            # FIXME if you change the size and then the text it sometimes
            # won't change until you change the text again
            # photo = f2i.multiline_tk(text, self.font.pilfont,
            #                          (int(w), int(h/2)),
            #                          padx=wpad, pady=hpad)
            photo = f2i.fingerprint(self.font.pilfont)

            label.image = photo
            label.configure(image=photo)
            label.grid(padx=wpad, pady=hpad, row=1, column=0,
                       sticky=tk.N, in_=self, columnspan=2)

        set_text(user_text)

        self.grid_columnconfigure(1, minsize=int(w/75))
        self.grid_columnconfigure(0, weight=1)

        # text entry
        svtext = tk.StringVar()
        svtext.trace("w", lambda n, idx, mode,
                     sv=svtext: set_text(svtext.get()))
        textin = tk.Entry(self, textvariable=svtext)
        textin.delete(0, tk.END)
        textin.insert(0, "Handgloves")
        textin.grid(sticky=tk.W+tk.E, padx=wpad, pady=hpad, in_=self,
                    row=2, column=0)

        # font size entry
        sv1 = tk.StringVar()
        sv1.trace("w", lambda n, idx, mode, sv=sv1:
                  set_text(svtext.get(), sv.get()))
        sizein = tk.Entry(self, textvariable=sv1, width=3)
        sizein.delete(0, tk.END)
        sizein.insert(0, str(self.font.size))
        sizein.grid(sticky=tk.E, padx=wpad, pady=hpad,
                    in_=self, row=2, column=1)

        # attributes with a scrollbar
        scrollbar = tk.Scrollbar(self)
        scrollbar.grid(sticky=tk.W+tk.N+tk.S, row=3, column=1,
                       padx=wpad, pady=hpad)
        listbox = tk.Listbox(self)
        listbox.grid(sticky=tk.E+tk.W, padx=wpad, pady=hpad,
                     row=3, column=0)
        for i in Font.DISPLAY_CATEGORIES:
            listbox.insert(tk.END, self.font.category_str(i[0], i[1]))
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
