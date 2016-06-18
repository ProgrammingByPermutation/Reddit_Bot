import tkinter
import gui
import reddit_client
import praw
import logger
from constants import *


def on_button_login_click():
    """
    Handles clicking the login button.
    """
    # Disable to login panel to avoid someone clicking it again
    gui.setup_state(main_form.panel_login, tkinter.DISABLED)

    # Asynchronously login
    reddit.login_first_time(main_form.entry_access_token.get())


def on_login_first_time(is_logged_in):
    """
    Handles an attempt to login.
    :param is_logged_in: True if logged in, false otherwise.
    """
    # If we're not logged in set the background color of the token to red since it's the problem.
    if not is_logged_in:
        gui.setup_state(main_form.panel_login, tkinter.NORMAL)
        main_form.entry_access_token.configure(bg="red")

    # Perform the remainder of the GUI updates
    on_is_logged_in(is_logged_in)


def on_is_logged_in(is_logged_in):
    """
    Handles responding to the login state of the reddit client changing.
    :param is_logged_in: True if logged in, false otherwise.
    """
    if is_logged_in:
        main_form.entry_access_token.configure(bg="white")
        gui.setup_state(main_form.panel_login, tkinter.DISABLED)
        reddit.add_callback("get_me", lambda username: main_form.label_current_user.configure(text=username), 1)
        reddit.get_me()
    else:
        gui.setup_state(main_form.panel_login, tkinter.NORMAL)
        main_form.label_current_user.configure(text="")


def on_button_get_click():
    """
    Handles clicking the get button which retrieves information without taking action.
    """
    # Disable so no one can push again until we're done.
    disable_actions()

    # Clear the results window.
    main_form.results.clear()

    # Process the request.
    if main_form.radiobutton_action_type.get() == gui.ActionType.User.value:
        username = main_form.entry_data.get()
        if username is not None:
            reddit.add_callback("get_user", on_get_user, 1)
            reddit.get_user(username, True, True)
    elif main_form.radiobutton_action_type.get() == gui.ActionType.Post_Comments.value:
        post_id = main_form.entry_data.get()
        if post_id is not None:
            reddit.add_callback("get_post", on_get_post, 1)
            reddit.get_post(post_id, True)
    elif main_form.radiobutton_action_type.get() == gui.ActionType.Post_User_Comments.value:
        pass


def on_get_user(user):
    """
    Writes all user data to the form.
    :param user: The user data.
    """
    if user is None:
        main_form.results.add_content("User not found!")
        enable_actions()
        return

    # Write all the posts to the screen.
    main_form.results.add_title("POSTS")
    if user.posts is not None:
        for post in user.posts:
            content = main_form.results.add_content(str(post))
            content.id = post.name
    else:
        main_form.results.add_content("No posts!")

    # Write all the comments to the screen.
    main_form.results.add_title("COMMENTS")
    if user.all_comments is not None:
        for comment in user.all_comments:
            content = main_form.results.add_content(str(comment))
            content.id = comment.name
    else:
        main_form.results.add_content("No comments!")

    enable_actions()


def on_get_post(post):
    """
    Writes all post data to the form.
    :param post: The post data.
    """
    if post is None:
        main_form.results.add_content("Post not found!")
        enable_actions()
        return

    # Write all comments to the screen.
    main_form.results.add_title("COMMENTS")
    if post.all_comments is not None:
        for comment in post.all_comments:
            comment.control = main_form.results.add_content(str(comment))
    else:
        main_form.results.add_content("No comments!")

    enable_actions()


def on_vote(entry, success):
    """
    The results of a vote.
    :param entry: The entry that was voted on.
    :param success: True if successful, false otherwise.
    """
    control = main_form.results.get_content(
        lambda control: control.id == entry.name if hasattr(control, "id") else False)

    if control is None:
        logger.log("main.on_vote: Unable to find control associated with comment.")
        return

    if success:
        control.configure(bg="green")
    else:
        control.configure(bg="red")


def on_button_execute_click():
    """
    Handles the execute operation.
    """
    # Disable so no one can push again until we're done.
    disable_actions()

    # Clear the results window.
    main_form.results.clear()

    # Process the request.
    if main_form.radiobutton_action_type.get() == gui.ActionType.User.value:
        username = main_form.entry_data.get()
        if username is not None:
            reddit.add_callback("get_user", on_execute_user, 1)
            reddit.get_user(username, True, True)
    elif main_form.radiobutton_action_type.get() == gui.ActionType.Post_Comments.value:
        post_id = main_form.entry_data.get()
        if post_id is not None:
            reddit.add_callback("get_post", on_execute_post, 1)
            reddit.get_post(post_id, True)
    elif main_form.radiobutton_action_type.get() == gui.ActionType.Post_User_Comments.value:
        pass


def on_execute_user(user):
    """
    Handles response from the execute user request.
    :param user: The user data.
    """
    if user is None:
        main_form.results.add_content("User not found!")
        enable_actions()
        return

    on_get_user(user)
    if main_form.radiobutton_action.get() == gui.Action.Upvote.value:
        reddit.vote(True, user.posts, on_vote)
        reddit.vote(True, user.all_comments, on_vote)
    elif main_form.radiobutton_action.get() == gui.Action.Downvote.value:
        reddit.vote(False, user.posts, on_vote)
        reddit.vote(False, user.all_comments, on_vote)
    elif main_form.radiobutton_action.get() == gui.Action.Clear.value:
        reddit.vote(None, user.posts, on_vote)
        reddit.vote(None, user.all_comments, on_vote)


def on_execute_post(post):
    """
    Handles the response from the execute post request.
    :param post: The post data.
    """
    if post is None:
        main_form.results.add_content("Post not found!")
        enable_actions()
        return

    on_get_post(post)
    if main_form.radiobutton_action.get() == gui.Action.Upvote.value:
        reddit.vote(True, post.all_comments, on_vote)
    elif main_form.radiobutton_action.get() == gui.Action.Downvote.value:
        reddit.vote(False, post.all_comments, on_vote)
    elif main_form.radiobutton_action.get() == gui.Action.Clear.value:
        reddit.vote(None, post.all_comments, on_vote)


def disable_actions():
    """
    Disables all controls associated with taking action on a post.
    """
    gui.setup_state(main_form.panel_data, tkinter.DISABLED)
    gui.setup_state(main_form.panel_actions, tkinter.DISABLED)
    gui.setup_state(main_form.panel_actions_type, tkinter.DISABLED)


def enable_actions():
    """
    Enables all controls associated with taking action on a post.
    """
    gui.setup_state(main_form.panel_data, tkinter.NORMAL)
    gui.setup_state(main_form.panel_actions, tkinter.NORMAL)
    gui.setup_state(main_form.panel_actions_type, tkinter.NORMAL)


if __name__ == "__main__":
    # Create main form
    main_form = gui.MainForm()

    # Attach delegates
    main_form.button_get_token.configure(command=lambda: reddit.launch_authorization_page())
    main_form.button_login.configure(command=on_button_login_click)
    main_form.button_get.configure(command=on_button_get_click)
    main_form.button_execute.configure(command=on_button_execute_click)

    # Create reddit client
    reddit = reddit_client.RedditProxy(user_data_file)
    reddit.add_callback("is_logged_in", on_is_logged_in)
    reddit.add_callback("login_first_time", on_login_first_time)
    reddit.is_logged_in()

    # Show form
    main_form.show()
