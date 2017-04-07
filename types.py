from font import Font
import tkinter as tk
from os import listdir

root = tk.Tk()
fontdir = "/home/varun/.fonts"
fontlist = listdir(fontdir)
rmlist = []

for d in fontlist:
    if ".ttf" not in d:
        rmlist.append(d)
for i in rmlist:
    fontlist.remove(i)

fonts = []

for i in fontlist:
    fonts.append(Font("{}/{}".format(fontdir, i)))

fg = Font("/home/varun/.fonts/LibreBaskerville-Italic.ttf")

fg.display()

root.mainloop()
