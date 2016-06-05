import tkinter
import gui
import reddit_client
from constants import *


def on_login():
    """
    Handles logging into Reddit.
    """
    access_info = reddit.login_first_time(main_form.entry_access_token.get())

    if access_info is not None:
        main_form.setup_state(main_form.panel_login, tkinter.DISABLED)
        main_form.label_current_user.configure(text=reddit.api.get_me())


# Create reddit client
reddit = reddit_client.RedditClient(user_data_file)

# Create main form
main_form = gui.MainForm()

# Attach delegates
main_form.button_get_token.configure(command=lambda: reddit.launch_authorization_page())
main_form.button_login.configure(command=on_login)

# Attempt to use previously entered user information
if reddit.is_logged_in():
    main_form.setup_state(main_form.panel_login, tkinter.DISABLED)
    main_form.label_current_user.configure(text=reddit.api.get_me())

# Show form
main_form.show()
