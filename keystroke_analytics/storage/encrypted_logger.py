"""
AES-encrypted log storage using Fernet.

Each log line is individually encrypted and base64-encoded before being
written, so partial reads are possible without decrypting the whole file.
The encryption key is derived from a user-supplied passphrase via
PBKDF2-HMAC-SHA256 with a random salt stored alongside the logs.
"""

import base64
import logging
from pathlib import Path
from threading import Lock

logger = logging.getLogger(__name__)

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    import os

    _HAS_CRYPTO = True
except ImportError:
    _HAS_CRYPTO = False


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a passphrase and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))


class EncryptedLogger:
    """
    Encrypts individual log lines with Fernet (AES-128-CBC + HMAC).

    The salt is written as the first line of each log file so that the
    same passphrase can decrypt it later.

    Parameters:
        log_dir: Directory for encrypted log files.
        passphrase: Secret used to derive the encryption key.
        prefix: Filename prefix.
    """

    def __init__(
        self,
        log_dir: Path,
        passphrase: str,
        prefix: str = "encrypted_session",
    ) -> None:
        if not _HAS_CRYPTO:
            raise ImportError(
                "The 'cryptography' package is required for encrypted storage. "
                "Install it with: uv add cryptography"
            )

        self._log_dir = log_dir
        self._prefix = prefix
        self._lock = Lock()

        self._log_dir.mkdir(parents=True, exist_ok=True)

        # Generate a random salt for this session.
        self._salt = os.urandom(16)
        key = _derive_key(passphrase, self._salt)
        self._fernet = Fernet(key)

        # Open the log file and write the salt as the first line.
        from datetime import datetime

        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self._path = self._log_dir / f"{self._prefix}_{ts}.enc"
        self._file = open(self._path, "w", encoding="utf-8")
        self._file.write(base64.urlsafe_b64encode(self._salt).decode() + "\n")
        self._file.flush()

    @property
    def current_path(self) -> Path:
        return self._path

    def write(self, line: str) -> None:
        """Encrypt and write a single log line."""
        token = self._fernet.encrypt(line.encode("utf-8"))
        with self._lock:
            self._file.write(token.decode("utf-8") + "\n")
            self._file.flush()

    def close(self) -> None:
        """Close the underlying file."""
        with self._lock:
            self._file.close()

    @staticmethod
    def decrypt_file(path: Path, passphrase: str) -> list[str]:
        """
        Decrypt an encrypted log file and return the plaintext lines.

        The first line of the file is the base64-encoded salt.
        """
        if not _HAS_CRYPTO:
            raise ImportError("cryptography package required for decryption")

        lines = path.read_text(encoding="utf-8").strip().splitlines()
        if not lines:
            return []

        salt = base64.urlsafe_b64decode(lines[0])
        key = _derive_key(passphrase, salt)
        fernet = Fernet(key)

        plaintext: list[str] = []
        for token_line in lines[1:]:
            plaintext.append(fernet.decrypt(token_line.encode()).decode("utf-8"))
        return plaintext
