import unittest

from kids_exo.auth.passwords import hash_password, verify_password


class PasswordHashTests(unittest.TestCase):
    def test_hashes_password_with_random_salt(self) -> None:
        first_hash = hash_password("secret password")
        second_hash = hash_password("secret password")

        self.assertNotEqual(first_hash, "secret password")
        self.assertNotEqual(first_hash, second_hash)
        self.assertTrue(verify_password("secret password", first_hash))
        self.assertTrue(verify_password("secret password", second_hash))

    def test_rejects_wrong_password_and_malformed_hash(self) -> None:
        password_hash = hash_password("secret password")

        self.assertFalse(verify_password("wrong password", password_hash))
        self.assertFalse(verify_password("secret password", "not-a-valid-hash"))

    def test_rejects_empty_password_when_hashing(self) -> None:
        with self.assertRaisesRegex(ValueError, "Password is required"):
            hash_password("")


if __name__ == "__main__":
    unittest.main()
