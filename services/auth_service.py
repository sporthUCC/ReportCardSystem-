from typing import List, Optional

from models.user import User
from repositories.auth_repository import AuthRepository, hash_password, verify_password


class AuthenticationError(Exception):
    """Raised when login credentials are missing, unknown, or invalid."""


class AuthorizationError(Exception):
    """Raised when an authenticated user lacks permission for an action or page."""


class AuthService:
    """Authenticates users and checks permissions using existing User subclasses."""

    def __init__(self, auth_repository: AuthRepository) -> None:
        self._auth_repository = auth_repository

    def seed_default_users(self) -> None:
        """Create default admin and teacher accounts if no accounts exist yet."""
        if self._auth_repository.get_all_accounts():
            return

        default_accounts = [
            {
                "person_id": "ADM-001",
                "username": "admin",
                "password_hash": hash_password("@dm!n"),
                "role": "Administrator",
                "first_name": "System",
                "last_name": "Administrator",
                "email": "admin@caribbeanhigh.edu.jm",
                "access_level": "Full",
            },
            {
                "person_id": "TCH-001",
                "username": "teacher",
                "password_hash": hash_password("t3@ch3r"),
                "role": "Teacher",
                "first_name": "Subject",
                "last_name": "Teacher",
                "email": "teacher@caribbeanhigh.edu.jm",
                "subject_taught": "Mathematics",
            },
        ]
        self._auth_repository.save_accounts(default_accounts)

    def authenticate(self, username: str, password: str) -> User:
        """
        Verify username and password, then return the authenticated User instance.
        Raises AuthenticationError if credentials are invalid.
        """
        if not isinstance(username, str) or not username.strip():
            raise AuthenticationError("Username is required.")
        if not isinstance(password, str) or not password:
            raise AuthenticationError("Password is required.")

        account = self._auth_repository.get_account_by_username(username)
        if account is None:
            raise AuthenticationError("Invalid username or password.")

        stored_hash = account.get("password_hash", "")
        if not verify_password(password, stored_hash):
            raise AuthenticationError("Invalid username or password.")

        return self._auth_repository.build_user_model(account)

    def get_user_id(self, user: User) -> str:
        """Retrieve the authenticated user's ID from the Person/User model."""
        return user.get_person_id()

    def get_user_role(self, user: User) -> str:
        """Retrieve the authenticated user's role via User.get_role()."""
        return user.get_role()

    def get_permissions(self, user: User) -> List[str]:
        """Retrieve the authenticated user's permissions via User.get_user_permission()."""
        return list(user.get_user_permission())

    def has_permission(self, user: Optional[User], permission: str) -> bool:
        """Return True if the user's model permissions include the requested permission."""
        if user is None or not permission:
            return False
        return permission in user.get_user_permission()

    def authorize(self, user: Optional[User], required_permission: str) -> bool:
        """
        Verify that the authenticated user is permitted to access a feature/page.
        Raises AuthorizationError if denied.
        """
        if user is None:
            raise AuthorizationError("No authenticated user session found.")

        if not self.has_permission(user, required_permission):
            raise AuthorizationError(
                f"Role '{user.get_role()}' is not permitted to perform '{required_permission}'."
            )
        return True