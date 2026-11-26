
class AuthService:

    def __init__(self):

        # Login details provided for the system.
        self.accounts = {
            "admin": {
                "password": "@dm!n",
                "role": "Administrator"
            },
            "teacher": {
                "password": "t3@ch3r",
                "role": "Teacher"
            }
        }

    def login(self, username, password):

        # Make sure the user enters a username.
        if not username or not username.strip():
            return None, "Please enter your username."

        # Make sure the password field is not empty.
        if not password:
            return None, "Please enter your password."

        # Find the account that matches the entered username.
        account = self.accounts.get(username.strip().lower())

        # Check if the username exists.
        if account is None:
            return None, "Incorrect username."

        # Check if the password is correct.
        if account["password"] != password:
            return None, "Incorrect password."

        # Return the user's role after successful login.
        return account["role"], "Login successful."
