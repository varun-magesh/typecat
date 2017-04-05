from font import Font
import tkinter as tk

root = tk.Tk()
f = Font("/home/varun/.fonts/Menlo-Regular.ttf")
fg = Font("/home/varun/.fonts/Libre_Baskerville/LibreBaskerville-Regular.ttf")
f.display(root)
print(f.__dict__)

root.mainloop()
