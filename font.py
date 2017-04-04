from tkinter import Frame
from configparser import ConfigParser

class Font(object):
	"""
	Stores cached information about fonts in memory.
	Attributes:
		name
		path
		category: serif, sans, display, etc.
		languages
		thickness
		slant = 0
		width = 0
		style: bold, thin, italic etc.
		ascender: space between lowercase height and uppercase height
		descender: length of tail on 'p', 'q', and others
		features: str of special characters supported
		TODO curve quantification
	"""
	def __init__(self, name, cp):
		if type(cp) is ConfigParser:
			#load from config
			raise NotImplementedError("Font cannot yet load from config.")
			return
		self.name = name
		self.path = cp
		
		

	def display(self, master):
		frame = Frame(master)
		frame.pack()

		self.button = Button(
			frame, text="QUIT", fg="red", command=frame.quit
			)
		self.button.pack(side=LEFT)
		
		self.hi_there = Button(frame, text="Hello", command=self.say_hi)
		self.hi_there.pack(side=LEFT)

		

