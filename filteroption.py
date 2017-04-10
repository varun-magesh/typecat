import tkinter as tk


class FilterOption(tk.Frame):
    """
    Filter options at top of screen
    """
    def __init__(self, master, feature, callback):

        tk.Frame.__init__(self, master)
        self.feature = feature
        self.callback = callback

        self.checkbutton_var = tk.IntVar()
        self.checkbutton_state = 0
        self.check = tk.Checkbutton(self, text="Filter {}".format(feature),
                                    command=self.check_action,
                                    variable=self.checkbutton_var)
        self.check.grid(sticky=tk.W, row=0, column=0, ipadx=0, pady=0)

        # standard deviations off
        self.slider_state = 0
        self.slider = tk.Scale(self, from_=-5, to=5, orient=tk.HORIZONTAL,
                               command=self.slide_action)
        self.slider.grid(sticky=tk.E, row=0, column=1, padx=0, pady=0)

    def check_action(self, event=None):
        self.checkbutton_state = self.checkbutton_var.get()
        self.callback()

    def slide_action(self, event=None):
        self.slider_state = self.slider.get()
		if self.checkbutton_state:
			self.callback()
