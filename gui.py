from tkinter import *


class MainForm(Tk):
    def __init__(self):
        # Call base
        Tk.__init__(self)

        # Log in panel
        self.login_panel = LabelFrame(self, text="Login", padx=5, pady=5)
        Label(self.login_panel, text="Token:").grid(row=0, column=0)
        self.entry_access_token = Entry(self.login_panel)
        self.entry_access_token.grid(row=0, column=1, sticky=E + W)
        self.button_get_token = Button(self.login_panel, text="Get Token")
        self.button_get_token.grid(row=1, column=0)
        self.button_login = Button(self.login_panel, text="Log In")
        self.button_login.grid(row=1, column=1)
        self.login_panel.grid(sticky=E + W)

        # Setup the form to be resizable
        MainForm.setup_resizable(self)

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
