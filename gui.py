from tkinter import *


def callback(*args):
    pass


class MainForm(Tk):
    def __init__(self):
        # Call base
        Tk.__init__(self)

        # Log in panel
        self.panel_login = LabelFrame(self, text="Login", padx=5, pady=5)
        Label(self.panel_login, text="Token:").grid(row=0, column=0)
        self.entry_access_token = Entry(self.panel_login)
        self.entry_access_token.grid(row=0, column=1, sticky=E + W)
        self.button_get_token = Button(self.panel_login, text="Get Token")
        self.button_get_token.grid(row=1, column=1, sticky=E)
        self.button_login = Button(self.panel_login, text="Log In")
        self.button_login.grid(row=1, column=1, sticky=W)
        self.panel_login.grid(row=0, columnspan=2, sticky=E + W)

        # User panel
        self.panel_current_user = LabelFrame(self, text="Authenticated User", padx=5, pady=5)
        self.label_current_user = Label(self.panel_current_user, text="")
        self.label_current_user.grid(column=0, row=0, sticky=W)
        self.panel_current_user.grid(row=1, columnspan=2, sticky=E + W)

        # Actions panel
        self.radiobutton_action = IntVar()
        self.radiobutton_action.trace("w", lambda *args: self.set_action_label())
        self.panel_actions = LabelFrame(self, text="Actions", padx=5, pady=5)
        Radiobutton(self.panel_actions, text="User", variable=self.radiobutton_action, value=1).grid(row=0, sticky=W)
        Radiobutton(self.panel_actions, text="Post Comments", variable=self.radiobutton_action, value=2).grid(row=1,
                                                                                                              sticky=W)
        Radiobutton(self.panel_actions, text="Post Users and Comments", variable=self.radiobutton_action, value=3).grid(
            row=2, sticky=W)
        self.panel_actions.grid(row=2, column=0, sticky=N + S + E + W)

        self.panel_data = LabelFrame(self, text="Action Data", padx=5, pady=5)
        self.label_data = Label(self.panel_data, text="")
        self.label_data.grid(row=0, column=0, sticky=W)
        self.entry_data = Entry(self.panel_data)
        self.entry_data.grid(row=0, column=1, sticky=E + W)
        self.button_execute = Button(self.panel_data, text="Execute")
        self.button_execute.grid(row=1, column=0, columnspan=2)
        self.panel_data.grid(row=2, column=1, sticky=E + W)

        # Results panel
        self.panel_results = LabelFrame(self, text="Results")
        self.results = ScrollableControlBecauseTkinterIsAShitTechnology(self.panel_results)
        self.results.grid(row=3)
        self.panel_results.grid(row=3, column=0, columnspan=2)

        # Setup the form to be universally resizable
        MainForm.setup_resizable(self)

        # Specifically override
        Grid.columnconfigure(self.panel_login, 0, weight=0)
        Grid.columnconfigure(self.panel_data, 0, weight=0)
        Grid.rowconfigure(self, 0, weight=0)
        Grid.rowconfigure(self, 1, weight=0)

        # Default values
        self.radiobutton_action.set("1")

    def set_action_label(self):
        """
        Sets the correct action label based on the radio button selection.
        """
        selection = self.radiobutton_action.get()
        if selection == 1:
            self.label_data.configure(text="Username:")
        elif selection == 2 or selection == 3:
            self.label_data.configure(text="Post Id:")

    @staticmethod
    def setup_resizable(control):
        """
        Recursively loops through the controls of the form to set the properties required for the form to be
        resizable.
        :param control: The control to recursively loop through.
        """
        size = control.grid_size()

        for x in range(0, size[0]):
            Grid.columnconfigure(control, x, weight=1)

        for x in range(0, size[1]):
            Grid.rowconfigure(control, x, weight=1)

        for child in control.children.values():
            MainForm.setup_resizable(child)

    @staticmethod
    def setup_state(control, state):
        """
        Recursively sets all sub-controls to the provided state.
        :param control: The control to recurse through.
        :param state: The state to set.
        """
        try:
            control.configure(state=state)
        except:
            pass

        for child in control.children.values():
            MainForm.setup_state(child, state)

    def show(self):
        """
        Shows the form.
        """
        self.mainloop()


class ScrollableControlBecauseTkinterIsAShitTechnology(Frame):
    def __init__(self, root):

        Frame.__init__(self, root)
        self.canvas = Canvas(root, borderwidth=0, background="#ffffff")
        self.frame = Frame(self.canvas, background="#ffffff")
        self.vsb = Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.grid(row=0, sticky=N+S+E)
        self.canvas.grid(row=0, sticky=N+S+E+W)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw",
                                  tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)

        self.populate()

    def populate(self):
        '''Put in some fake data'''
        for row in range(100):
            Label(self.frame, text="%s" % row, width=3, borderwidth="1",
                     relief="solid").grid(row=row, column=0)
            t="this is the second column for row %s" %row
            Label(self.frame, text=t).grid(row=row, column=1)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))