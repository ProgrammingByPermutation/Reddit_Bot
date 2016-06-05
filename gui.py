from tkinter import *


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
        self.panel_login.grid(sticky=E + W)

        # User panel
        self.panel_current_user = LabelFrame(self, text="Authenticated User", padx=5, pady=5)
        self.label_current_user = Label(self.panel_current_user, text="")
        self.label_current_user.grid(column=0, row=0, sticky=W)
        self.panel_current_user.grid(sticky=E + W)

        # Setup the form to be universally resizable
        MainForm.setup_resizable(self)

        # Specifically override
        Grid.columnconfigure(self.panel_login, 0, weight=0)

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
