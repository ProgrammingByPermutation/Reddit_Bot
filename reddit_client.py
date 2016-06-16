import praw
import os
import pickle
import multiprocessing
import threading
import logger


class RedditClient:
    """
    A facade for dealing with PRAW since PRAW can be a nightmare. You may use the api directly for simple calls.
    """

    def __init__(self, user_data_filename):
        """
        Initializes a new instance of the RedditClient class.
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
            logger.log("RedditClient.__init__: Error loading user data and refreshing:", e)

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
            logger.log("RedditClient.login_first_time: Error logging in:", e)
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
            logger.log("RedditClient.login: Error logging in:", e)
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

    def get_me(self):
        """
        Returns the currently authenticated user's username.
        :return: the username if successful, None otherwise.
        """
        try:
            return self.api.get_me()
        except:
            return None


class EmbeddedProxy:
    def __init__(self, user_data_filename):
        """
        Initializes a new instance of the RedditProxy class.
        :param user_data_filename: The file that should be created or read in with user data.
        """
        # Two queues, one for requests and one for responses.
        self.producer_queue = multiprocessing.Queue()
        self.consumer_queue = multiprocessing.Queue()
        self.callbacks = {}

        # Create the producer in a different process.
        self.producer = multiprocessing.Process(target=self.producer_main,
                                                args=(self.producer_queue, self.consumer_queue, user_data_filename))
        self.producer.daemon = True
        self.producer.start()

        # Create the consumer in the same process for retrieving responses async.
        self.consumer = threading.Thread(target=self.consumer_main, args=(self.consumer_queue,))
        self.consumer.daemon = True
        self.consumer.start()

    def add_command(self, name, *args, **params):
        """
        Adds a command to the producer queue for processing.
        :param name: The name of the method to call.
        :param args: The arguments to pass to the method.
        :param params: The parameters to pass to the method.
        """
        self.producer_queue.put({"name": name, "args": args, "params": params})

    def add_callback(self, name, callback):
        """
        Adds a callback associated with an asynchronous return value.
        :param name: The name or identifier of the callback. This is nominally the method name.
        :param callback: The callback to pass the return value to.
        """
        if not callable(callback):
            logger.log("EmbeddedProxy.add_callback: Attempt to add un-callable data type to callback list.")
            return

        # Either create the list if it doesn't exist or add to the existing list.
        if name not in self.callbacks:
            self.callbacks[name] = [callback]
        else:
            self.callbacks[name].append(callback)

    def remove_callback(self, name, callback):
        """
        Removes a callback associated with an asynchronous return value.
        :param name: The name or identifier of the callback. This is nominally the method name.
        :param callback: The callback to pass the return value to.
        """
        # If the name isn't even in the list there's nothing to delete.
        if name not in self.callbacks:
            return

        # Get the list of callbacks.
        callback_list = self.callbacks[name]

        # If the callback is in the callback list, remove it.
        if callback in callback_list:
            callback_list.remove(callback)

        # If what we deleted was the last thing in the list, remove the callback list from the master collection.
        if len(callback_list) == 0:
            del self.callbacks[name]

    def producer_main(self, request_queue, response_queue, user_data_filename):
        """
        The main method for the RedditProxy in a seperate method. Used to make calls to the RedditClient class.
        :param request_queue: The queue we will receive requests on.
        :param response_queue: The queue we will use to respond.
        :param user_data_filename: The data file that contains existing user data.
        """
        # Create the reddit object we will use for the remainder of the simulation.
        reddit = RedditClient(user_data_filename)

        while True:
            # Passively wait for a request.
            message = request_queue.get()

            # If the message is None, that's the poison pill.
            if message is None:
                break

            # Make sure we have a method to call.
            if "name" not in message:
                logger.log("EmbeddedProxy.producer_main: Error method name not found on producer queue.")
                continue

            # Try to get the method we're supposed to call.
            method = getattr(reddit, message["name"])
            if not callable(method):
                logger.log("EmbeddedProxy.producer_main: Error the following method was not found \"", message["name"],
                           "\"", end="")
                continue

            # Call the method.
            ret = None
            try:
                args = message.get("args", None)
                params = message.get("params", None)

                if len(args) > 0 and len(params) > 0:
                    ret = method(*args, **params)
                elif len(args) > 0:
                    ret = method(*args)
                elif len(params) > 0:
                    ret = method(**params)
                else:
                    ret = method()
            except Exception as ex:
                logger.log("EmbeddedProxy.producer_main: Caught the following exception during method invocation: ", ex,
                           end="")

            # Put the response on the response queue for the other process.
            response_queue.put({"name": message["name"], "return": ret})

    def consumer_main(self, queue):
        """
        The main method for the RedditProxy in a separate method. Used to make calls to the RedditClient class.
        :param queue: The queue we will receive responses on.
        """
        while True:
            # Passively wait for a request.
            message = queue.get()

            if message is None:
                break

            # Make sure we know who to notify.
            if "name" not in message:
                continue

            # Is there someone that wants these notifications?
            name = message["name"]
            if name not in self.callbacks:
                continue

            # Note whether or not there was a return value.
            has_ret = "return" in message
            ret = message["return"] if has_ret else None

            # Perform each callback.
            callbacks = self.callbacks[name]
            for callback in callbacks:
                try:
                    if has_ret:
                        callback(ret)
                    else:
                        callback()
                except Exception as ex:
                    logger.log("EmbeddedProxy.consumer_main: Caught the following exception during method invocation: ",
                               ex, end="")


class RedditProxy(RedditClient):
    """
    A proxy for interacting with the RedditClient in another process.
    """

    def __init__(self, user_data_filename):
        """
        Initializes a new instance of the RedditProxy class.
        :param user_data_filename: The file that contains previously entered user data.
        """
        object.__setattr__(self, "_obj", EmbeddedProxy(user_data_filename))

    def __getattribute__(self, name):
        """
        Used as a pass through to the underlying object.
        :param name: The name of the attribute.
        :return: The method.
        """

        # If the method is from our proxied object then marshall the call to the "add_command" method.
        if hasattr(RedditClient, name):
            method = getattr(object.__getattribute__(self, "_obj"), "add_command")

            if method is None:
                return

            return lambda *args, **params: method(name, *args, **params)

        # Otherwise just get the method directly.
        return getattr(object.__getattribute__(self, "_obj"), name)

    def __delattr__(self, name):
        """
        Used as a pass through to the underlying object.
        :param name: The name of the attribute.
        """
        delattr(object.__getattribute__(self, "_obj"), name)

    def __setattr__(self, name, value):
        """
        Used as a pass through to the underlying object.
        :param name: The name of the attribute.
        :param value: The value to set to the attribute to.
        """
        setattr(object.__getattribute__(self, "_obj"), name, value)

    def __nonzero__(self):
        """
        Used as a pass through to the underlying object.
        :return: True if non-zero, false otherwise.
        """
        return bool(object.__getattribute__(self, "_obj"))

    def __str__(self):
        """
        Used as a pass through to the underlying object.
        :return: The string representation of the object.
        """
        return str(object.__getattribute__(self, "_obj"))

    def __repr__(self):
        """
        Used as a pass through to the underlying object.
        :return: The string representation of the object that acts as a constructable means to recreate the object.
        """
        return repr(object.__getattribute__(self, "_obj"))
