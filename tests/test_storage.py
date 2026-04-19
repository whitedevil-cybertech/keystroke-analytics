"""Tests for keystroke_analytics.storage."""

import tempfile
from pathlib import Path

import pytest

from keystroke_analytics.storage.rotation import RotatingFileWriter


class TestRotatingFileWriter:
    @pytest.fixture()
    def tmp_dir(self):
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    def test_writes_to_file(self, tmp_dir):
        writer = RotatingFileWriter(tmp_dir, prefix="test", max_size_mb=5.0)
        writer.write("hello world")
        content = writer.read_current()
        assert "hello world" in content
        writer.close()

    def test_creates_directory(self, tmp_dir):
        nested = tmp_dir / "sub" / "dir"
        writer = RotatingFileWriter(nested, prefix="test")
        assert nested.exists()
        writer.close()

    def test_rotation_on_size(self, tmp_dir):
        writer = RotatingFileWriter(tmp_dir, prefix="test", max_size_mb=0.001)
        first = writer.current_path
        for i in range(100):
            writer.write(f"line-{i:04d}-padding-" + "x" * 50)
        logs = list(tmp_dir.glob("test_*.log"))
        assert len(logs) > 1
        assert writer.current_path != first
        writer.close()

    def test_survives_deleted_file(self, tmp_dir):
        writer = RotatingFileWriter(tmp_dir, prefix="test")
        writer.current_path.unlink()
        writer.write("after delete")
        assert writer.current_path.exists()
        writer.close()

    def test_independent_instances(self, tmp_dir):
        dir_a = tmp_dir / "a"
        dir_b = tmp_dir / "b"
        wa = RotatingFileWriter(dir_a, prefix="a")
        wb = RotatingFileWriter(dir_b, prefix="b")
        wa.write("only_a")
        wb.write("only_b")
        assert "only_a" in wa.read_current()
        assert "only_b" not in wa.read_current()
        assert "only_b" in wb.read_current()
        wa.close()
        wb.close()


class TestEncryptedLogger:
    """Only runs if cryptography is installed."""

    @pytest.fixture()
    def tmp_dir(self):
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    def test_encrypt_decrypt_roundtrip(self, tmp_dir):
        pytest.importorskip("cryptography")
        from keystroke_analytics.storage.encrypted_logger import EncryptedLogger

        logger = EncryptedLogger(tmp_dir, passphrase="testpass", prefix="enc")
        logger.write("secret line 1")
        logger.write("secret line 2")
        path = logger.current_path
        logger.close()

        # Raw file should not contain plaintext.
        raw = path.read_text(encoding="utf-8")
        assert "secret line 1" not in raw

        # Decrypt should recover the original.
        lines = EncryptedLogger.decrypt_file(path, "testpass")
        assert lines == ["secret line 1", "secret line 2"]

    def test_wrong_passphrase_fails(self, tmp_dir):
        pytest.importorskip("cryptography")
        from keystroke_analytics.storage.encrypted_logger import EncryptedLogger

        logger = EncryptedLogger(tmp_dir, passphrase="correct", prefix="enc")
        logger.write("data")
        path = logger.current_path
        logger.close()

        with pytest.raises(Exception):
            EncryptedLogger.decrypt_file(path, "wrong-passphrase")
