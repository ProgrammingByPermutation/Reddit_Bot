import praw
import os
import pickle


class RedditClient:
    """
    A facade for dealing with PRAW since PRAW can be a nightmare. You may use the api directly for simple calls.
    """

    def __init__(self, user_data_filename):
        """
        Initializes a new instance of the Reddit_Client class.
        :param user_data_filename: The file that should be created or read in with user data.
        """
        # The Reddit API instance
        self.api = praw.Reddit(user_agent="windows:reddit_play_thing:v1.0.0")

        # The hard coded application information we registered with Reddit
        self.api.set_oauth_app_info("NvFC9EM7Z1jB4Q", "", "http://127.0.0.1:65010/authorize_callback")

        # The number of times we can fail to make a call before stopping a loop
        self.FAILURE_LIMIT = 10

        # The file to save the user data in that needs to be persisted between runs
        self.user_data_filename = user_data_filename

        # A dictionary from the Reddit API containing the following:
        # "scope": Our access permissions per https://github.com/reddit/reddit/wiki/OAuth2
        # "access_token": The access token the user provided us when they gave us permissions to use their username
        # "refresh_token": The refresh token used to refresh our permissions to the user
        self.access_information = None

        try:
            if self.user_data_filename is not None and os.path.isfile(self.user_data_filename):
                with open(self.user_data_filename, "rb") as file:
                    self.access_information = pickle.load(file)
        except Exception as e:
            print("Error loading user data and refreshing :", e)

        # Try to login if we had information saved
        if self.access_information is not None:
            self.login(self.access_information["refresh_token"])

    def launch_authorization_page(self):
        """
        Launches the Reddit authorization page in a web browser for the user.
        """
        url = self.api.get_authorize_url('reddit_play_thing', 'creddits edit flair history identity modconfig '
                                                              'modcontributors modflair modlog modothers modposts '
                                                              'modself modwiki mysubreddits privatemessages read '
                                                              'report save submit subscribe vote wikiedit '
                                                              'wikiread', True)
        import webbrowser
        webbrowser.open(url)

    def login_first_time(self, access_token):
        """
        Login to Reddit using the Reddit access token. This is only used the first time a user access the application.
        You must login before you will be allowed to perform other operations.
        :param access_token: The access token returned from launch_authorization_page.
        :return: True if successful, false otherwise.
        """
        try:
            self.access_information = self.api.get_access_information(access_token)
        except Exception as e:
            print("Error logging in:", e)
            return False

        if self.access_information is not None and self.user_data_filename is not None:
            directory = os.path.dirname(self.user_data_filename)
            if not os.path.exists(directory):
                os.makedirs(directory)

            with open(self.user_data_filename, "wb") as file:
                pickle.dump(self.access_information, file)

        return True

    def login(self, refresh_token):
        """
        Login to Reddit using the Reddit refresh token. You must login before you will be allowed to perform other
        operations.
        :param refresh_token: The refresh token returned from launch_authorization_page of a previous session.
        :return: True if successful, false otherwise.
        """
        try:
            self.access_information = self.api.refresh_access_information(refresh_token)
            return True
        except Exception as e:
            print("Error logging in:", e)
            return False

    def is_logged_in(self):
        """
        Checks if a user is currently logged into the client.
        :return: True if logged in, false otherwise.
        """
        try:
            return self.api.get_me() is not None
        except:
            return False
