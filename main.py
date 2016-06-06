import tkinter
import gui
import reddit_client
import praw
from constants import *


def on_login():
    """
    Handles logging into Reddit.
    """
    access_info = reddit.login_first_time(main_form.entry_access_token.get())

    if access_info is not None:
        main_form.setup_state(main_form.panel_login, tkinter.DISABLED)
        main_form.label_current_user.configure(text=reddit.api.get_me())


def on_get():
    """
    Performs the get operation.
    """
    main_form.results.clear()

    posts = None
    comments = None

    if main_form.radiobutton_action_type.get() == gui.ActionType.User.value:
        username = main_form.entry_data.get()
        if username is not None:
            try:
                main_form.results.add_title("POSTS")

                user = reddit.api.get_redditor(username)
                posts = list(user.get_submitted(sort="new", time="all", limit=None))
                if posts is not None:
                    for post in posts:
                        post.control = main_form.results.add_content(str(post).replace("\r", " ").replace("\n", " "))
                else:
                    main_form.results.add_content("No posts!")

                main_form.results.add_title("COMMENTS")
                comments = list(user.get_comments(sort="new", time="all", limit=None))
                if comments is not None:
                    for comment in comments:
                        comment.control = main_form.results.add_content(
                            str(comment).replace("\r", " ").replace("\n", " "))
                else:
                    main_form.results.add_content("No comments!")
            except:
                pass
    elif main_form.radiobutton_action_type.get() == gui.ActionType.Post_Comments.value:
        post_id = main_form.entry_data.get()
        if post_id is not None:
            try:
                main_form.results.add_title("COMMENTS")

                post = reddit.api.get_submission(submission_id=post_id)
                post.replace_more_comments(limit=None, threshold=0)
                all_comments = praw.helpers.flatten_tree(post.comments)
                if all_comments is not None:
                    for comment in all_comments:
                        comment.control = main_form.results.add_content(
                            str(comment).replace("\r", " ").replace("\n", " "))
                else:
                    main_form.results.add_content("No comments!")
            except:
                pass
    elif main_form.radiobutton_action_type.get() == gui.ActionType.Post_User_Comments.value:
        pass

    return posts, comments


def on_execute():
    """
    Performs the execute operation.
    """
    posts, comments = on_get()

    command = None
    if main_form.radiobutton_action.get() == gui.Action.Upvote.value:
        command = "upvote"
    elif main_form.radiobutton_action.get() == gui.Action.Downvote.value:
        command = "downvote"
    elif main_form.radiobutton_action.get() == gui.Action.Clear.value:
        command = "clear_vote"

    if command is None:
        return

    if posts is not None:
        for post in posts:
            try:
                getattr(post, command)()
                post.control.configure(bg="green")
            except:
                post.control.configure(bg="red")

    if comments is not None:
        for comment in comments:
            try:
                getattr(comment, command)()
                comment.control.configure(bg="green")
            except:
                comment.control.configure(bg="red")


if __name__ == "__main__":
    # Create reddit client
    reddit = reddit_client.RedditProxy(user_data_file)

    # Create main form
    main_form = gui.MainForm()

    # Attach delegates
    # main_form.button_get_token.configure(command=lambda: reddit.launch_authorization_page())
    main_form.button_login.configure(command=on_login)
    main_form.button_get.configure(command=on_get)
    main_form.button_execute.configure(command=on_execute)

    # Attempt to use previously entered user information
    # if reddit.is_logged_in():
    #     gui.setup_state(main_form.panel_login, tkinter.DISABLED)
    #     main_form.label_current_user.configure(text=reddit.api.get_me())

    # Show form
    main_form.show()
