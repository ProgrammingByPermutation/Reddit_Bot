from tkinter import *
from enum import Enum


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
        setup_resizable(child)


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
        setup_state(child, state)


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
        self.panel_login.grid(row=0, columnspan=3, sticky=E + W)
        setup_state(self.panel_login, DISABLED)

        # User panel
        self.panel_current_user = LabelFrame(self, text="Authenticated User", padx=5, pady=5)
        self.label_current_user = Label(self.panel_current_user, text="")
        self.label_current_user.grid(column=0, row=0, sticky=W)
        self.panel_current_user.grid(row=1, columnspan=3, sticky=N + S + E + W)

        # Action Type panel
        self.radiobutton_action_type = IntVar()
        self.radiobutton_action_type.trace("w", lambda *args: self.set_action_label())
        self.panel_actions_type = LabelFrame(self, text="Action Type", padx=5, pady=5)
        Radiobutton(self.panel_actions_type, text="User", variable=self.radiobutton_action_type,
                    value=ActionType.User.value).grid(row=0, sticky=W)
        Radiobutton(self.panel_actions_type, text="Post Comments", variable=self.radiobutton_action_type,
                    value=ActionType.Post_Comments.value).grid(row=1, sticky=W)
        Radiobutton(self.panel_actions_type, text="Post Users/Comments", variable=self.radiobutton_action_type,
                    value=ActionType.Post_User_Comments.value).grid(row=2, sticky=W)
        self.panel_actions_type.grid(row=2, column=0, sticky=N + S + E + W)

        # Action panel
        self.radiobutton_action = IntVar()
        self.panel_actions = LabelFrame(self, text="Action", padx=5, pady=5)
        Radiobutton(self.panel_actions, text="Upvote", variable=self.radiobutton_action,
                    value=Action.Upvote.value).grid(row=0, sticky=W)
        Radiobutton(self.panel_actions, text="Downvote", variable=self.radiobutton_action,
                    value=Action.Downvote.value).grid(row=1, sticky=W)
        Radiobutton(self.panel_actions, text="Clear Votes", variable=self.radiobutton_action,
                    value=Action.Clear.value).grid(row=2, sticky=W)
        self.panel_actions.grid(row=2, column=1, sticky=N + S + E + W)

        # Action Data
        self.panel_data = LabelFrame(self, text="Action Data", padx=5, pady=5)
        self.label_data = Label(self.panel_data, text="")
        self.label_data.grid(row=0, column=0, sticky=W)
        self.entry_data = Entry(self.panel_data)
        self.entry_data.grid(row=0, column=1, sticky=E + W)
        frame = Frame(self.panel_data)
        self.button_get = Button(frame, text="Get")
        self.button_get.grid(row=0, column=0)
        self.button_execute = Button(frame, text="Execute")
        self.button_execute.grid(row=0, column=1)
        frame.grid(row=1, column=0, columnspan=2)
        self.panel_data.grid(row=2, column=2, sticky=N + S + E + W)

        # Results panel
        self.panel_results = LabelFrame(self, text="Results")
        self.results = ScrollableControlBecauseTkinterIsAShitTechnology(self.panel_results)
        self.results.grid(sticky=N + S + E + W)
        self.panel_results.grid(row=3, column=0, columnspan=3, sticky=N + S + E + W)

        # Setup the form to be universally resizable
        setup_resizable(self)

        # Specifically override
        Grid.columnconfigure(self.panel_login, 0, weight=0)
        Grid.columnconfigure(self.panel_data, 0, weight=0)
        Grid.rowconfigure(self, 0, weight=0)
        Grid.rowconfigure(self, 1, weight=0)
        Grid.rowconfigure(self, 2, weight=0)

        # Default values
        self.radiobutton_action_type.set("1")
        self.radiobutton_action.set("2")

    def set_action_label(self):
        """
        Sets the correct action label based on the radio button selection.
        """
        selection = self.radiobutton_action_type.get()
        if selection == 1:
            self.label_data.configure(text="Username:")
        elif selection == 2 or selection == 3:
            self.label_data.configure(text="Post Id:")

    def show(self):
        """
        Shows the form.
        """
        self.mainloop()


class ActionType(Enum):
    """
    Specifies the types of actions that can be performed.
    """
    User = 1
    Post_Comments = 2
    Post_User_Comments = 3


class Action(Enum):
    """
    Specifies the actions that can be performed.
    """
    Upvote = 1
    Downvote = 2
    Clear = 3


class ScrollableControlBecauseTkinterIsAShitTechnology(Frame):
    """
    A scrollable control that you can add and remove labels from.
    """

    def __init__(self, root):
        Frame.__init__(self, root)
        self.canvas = Canvas(self, borderwidth=0)
        self.canvas.grid(row=0, sticky=N + S + E + W)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        self.vsb = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.vsb.grid(row=0, sticky=N + S + E)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.frame = Frame(self.canvas)
        self.frame_id = self.canvas.create_window((4, 4), window=self.frame, anchor="nw")
        self.frame.bind("<Configure>", self.on_frame_resize)

        setup_resizable(self.frame)

    def add_title(self, text):
        """
        Adds a title cell to the list.
        :param text: The text to display in the title.
        :return: The created control.
        """
        label = Label(self.frame, text=text, border=1, bg="grey")
        label.grid(row=len(self.frame.children), sticky=E + W)
        setup_resizable(self.frame)
        return label

    def add_content(self, text):
        """
        Add a control to the list.
        :param text: The text of the label to add.
        :return: The created control.
        """
        # Sanitize the text
        text = text.replace("\r", " ").replace("\n", " ").encode("ascii", "ignore")

        label = Label(self.frame, text=text)
        label.grid(row=len(self.frame.children), stick=W)
        setup_resizable(self.frame)
        return label

    def get_content(self, query):
        """
        Gets added content that matches a given query.
        :param query: The query.
        :return: The first instance of a given query, none if nothing is found.
        """
        for child in self.frame.children.values():
            if query(child):
                return child

        return None

    def clear(self):
        """
        Clears the panel of all added controls.
        """
        if self.frame is not None:
            self.frame.destroy()

        self.frame = Frame(self.canvas)
        self.frame_id = self.canvas.create_window((4, 4), window=self.frame, anchor="nw")
        self.frame.bind("<Configure>", self.on_frame_resize)

    def on_frame_resize(self, event):
        """
        Reset the scroll region to encompass the inner frame.
        :param event: The event arguments.
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_resize(self, event):
        """
        Resizes the control region of the canvas.
        :param event: The event arguments.
        """
        self.canvas.itemconfigure(self.frame_id, width=event.width)
