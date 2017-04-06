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
fg.display(root)

italic = 0
ni = 0
regular = 0
nr = 0
for i in fonts:
    if i.style == "Italic":
        italic += i.slant
        ni += 1
    else:
        regular += i.slant
        nr += 1

print("Regular:{} Italic:{}".format(regular/nr, italic/ni))

root.mainloop()
