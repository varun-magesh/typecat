from font import Font
import tkinter as tk
import pickle
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

# for idx, i in enumerate(fontlist):
#    fonts.append(Font("{}/{}".format(fontdir, i)))

# fg = Font("/home/varun/.fonts/LibreBaskerville-Italic.ttf")
fg = pickle.load(open("/home/varun/.types/Libre_Baskerville_Italic", "rb"))
print(fg.__dict__)
fg.save()

w = fg.display(500, 400)
w.configure(highlightbackground="#000000")
w.grid()
root.geometry("500x500")
root.mainloop()
