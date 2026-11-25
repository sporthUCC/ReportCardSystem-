import os
import tempfile
import unittest

from models.administrator import Administrator
from models.teacher import Teacher
from repositories.auth_repository import AuthRepository
from services.auth_service import (
    AuthenticationError,
    AuthorizationError,
    AuthService,
)


class TestAuthenticationBackend(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self._users_file = os.path.join(self._temp_dir.name, "users.json")
        self.repo = AuthRepository(file_path=self._users_file)
        self.service = AuthService(self.repo)
        self.service.seed_default_users()

    def tearDown(self) -> None:
        self._temp_dir.cleanup()

    def test_successful_administrator_login(self) -> None:
        user = self.service.authenticate("admin", "@dm!n")
        self.assertIsInstance(user, Administrator)
        self.assertEqual(self.service.get_user_id(user), "ADM-001")
        self.assertEqual(self.service.get_user_role(user), "Administrator")

    def test_successful_teacher_login(self) -> None:
        user = self.service.authenticate("teacher", "t3@ch3r")
        self.assertIsInstance(user, Teacher)
        self.assertEqual(self.service.get_user_id(user), "TCH-001")
        self.assertEqual(self.service.get_user_role(user), "Teacher")

    def test_incorrect_password_rejected(self) -> None:
        with self.assertRaises(AuthenticationError):
            self.service.authenticate("admin", "wrong_password")

    def test_nonexistent_username_rejected(self) -> None:
        with self.assertRaises(AuthenticationError):
            self.service.authenticate("unknown_user", "@dm!n")

    def test_role_identification(self) -> None:
        admin_user = self.service.authenticate("admin", "@dm!n")
        teacher_user = self.service.authenticate("teacher", "t3@ch3r")

        self.assertEqual(admin_user.get_role(), "Administrator")
        self.assertEqual(teacher_user.get_role(), "Teacher")

    def test_permission_handling(self) -> None:
        admin_user = self.service.authenticate("admin", "@dm!n")
        teacher_user = self.service.authenticate("teacher", "t3@ch3r")

        # Administrator permissions allowed
        self.assertTrue(self.service.authorize(admin_user, "manage_student"))
        self.assertTrue(self.service.authorize(admin_user, "generate_report"))

        # Teacher permissions allowed
        self.assertTrue(self.service.authorize(teacher_user, "enter_grades"))
        self.assertTrue(self.service.authorize(teacher_user, "update_grades"))

        # Cross-role restricted actions blocked
        with self.assertRaises(AuthorizationError):
            self.service.authorize(teacher_user, "manage_student")

        with self.assertRaises(AuthorizationError):
            self.service.authorize(admin_user, "enter_grades")


if __name__ == "__main__":
    unittest.main(verbosity=2)