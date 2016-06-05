import os
import appdirs

user_data_folder = appdirs.user_data_dir("Reddit_Bot")
user_data_file = os.path.join(appdirs.user_data_dir("Reddit_Bot"), "UserData.dat")
