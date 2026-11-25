import hashlib
import hmac
import os
from typing import Any, Dict, List, Optional

from models.administrator import Administrator
from models.teacher import Teacher
from models.user import User

try:
    from config.settings import USERS_FILE as DEFAULT_USERS_FILE
except ImportError:
    DEFAULT_USERS_FILE = os.path.join("data", "users.json")

try:
    from storage.json_storage import JSONStorage
except ImportError:
    # Fallback if json_storage.py is placed at project root
    from json_storage import JSONStorage


def hash_password(password: str, salt: Optional[str] = None) -> str:
    """Hash a plain-text password using PBKDF2-HMAC-SHA256 with a per-user salt."""
    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string.")

    salt_hex = salt if salt is not None else os.urandom(16).hex()
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_hex.encode("utf-8"),
        100_000,
    )
    return f"{salt_hex}${derived_key.hex()}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verify a plain-text password against a 'salt$hash' string in constant time."""
    if not plain_password or not stored_hash or "$" not in stored_hash:
        return False

    salt_hex, expected_hex = stored_hash.split("$", 1)
    candidate_hash = hash_password(plain_password, salt=salt_hex).split("$", 1)[1]
    return hmac.compare_digest(candidate_hash, expected_hex)


class AuthRepository:
    """Handles persistence and retrieval of user login accounts via JSONStorage."""

    def __init__(self, file_path: str = DEFAULT_USERS_FILE) -> None:
        self._storage = JSONStorage(file_path)

    def get_all_accounts(self) -> List[Dict[str, Any]]:
        """Return all registered login account records from users.json."""
        data = self._storage.load_data()
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and isinstance(data.get("users"), list):
            return data["users"]
        return []

    def save_accounts(self, accounts: List[Dict[str, Any]]) -> None:
        """Persist the list of login account records to users.json."""
        self._storage.save_data(accounts)

    def add_account(self, account_record: Dict[str, Any]) -> None:
        """Add a new login account record if username and person_id are unique."""
        accounts = self.get_all_accounts()
        username = account_record.get("username", "").strip().lower()
        person_id = account_record.get("person_id")

        for existing in accounts:
            if existing.get("username", "").strip().lower() == username:
                raise ValueError(f"Username '{account_record.get('username')}' already exists.")
            if person_id and existing.get("person_id") == person_id:
                raise ValueError(f"User ID '{person_id}' already has a login account.")

        accounts.append(account_record)
        self.save_accounts(accounts)

    def get_account_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Retrieve a raw login account record by username (case-insensitive)."""
        if not isinstance(username, str) or not username.strip():
            return None

        target = username.strip().lower()
        for record in self.get_all_accounts():
            if str(record.get("username", "")).strip().lower() == target:
                return record
        return None

    def get_account_by_id(self, person_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a raw login account record by user/person ID."""
        if not person_id:
            return None

        for record in self.get_all_accounts():
            if str(record.get("person_id", "")) == str(person_id):
                return record
        return None

    def build_user_model(self, record: Dict[str, Any]) -> User:
        """Instantiate the appropriate User subclass (Administrator or Teacher) from a record."""
        role = str(record.get("role", "")).strip()
        person_id = record.get("person_id", "")
        first_name = record.get("first_name", role or "User")
        last_name = record.get("last_name", "Account")
        email = record.get("email", f"{record.get('username', 'user')}@caribbeanhigh.edu.jm")
        gender = record.get("gender")
        dob = record.get("date_of_birth")

        if role == "Administrator":
            access_level = record.get("access_level") or "Full"
            return Administrator(
                person_id=person_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                gender=gender,
                access_level=access_level,
                date_of_birth=dob,
            )

        if role == "Teacher":
            subject_taught = record.get("subject_taught") or "General Studies"
            return Teacher(
                person_id=person_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                gender=gender,
                subject_taught=subject_taught,
                date_of_birth=dob,
            )

        raise ValueError(f"Unsupported user role in account record: '{role}'")

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Retrieve a hydrated User instance (Administrator/Teacher) by username."""
        record = self.get_account_by_username(username)
        return self.build_user_model(record) if record else None

    def get_user_by_id(self, person_id: str) -> Optional[User]:
        """Retrieve a hydrated User instance (Administrator/Teacher) by person ID."""
        record = self.get_account_by_id(person_id)
        return self.build_user_model(record) if record else None