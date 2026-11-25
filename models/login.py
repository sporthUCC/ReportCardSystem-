
class Login:

    def __init__(self, username, password, role):
        # Store the user's login credentials and role.
        self.__username = username
        self.__password = password
        self.__role = role

    # Return the user's username.
    def get_username(self):
        return self.__username

    # Return the user's password.
    def get_password(self):
        return self.__password

    # Return the user's assigned role.
    def get_role(self):
        return self.__role

