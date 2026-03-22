"""
Command-line interface for keystroke analytics.

Parses arguments, builds an ``AppConfig``, and launches the engine.
Also provides a ``decrypt`` subcommand to read encrypted log files.
"""

import argparse
import sys
from pathlib import Path

from keystroke_analytics.config import AppConfig, StorageConfig
from keystroke_analytics.engine import AnalyticsEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="keystroke-analytics",
        description="Cross-platform keystroke analytics with typing biometrics.",
    )
    sub = parser.add_subparsers(dest="command")

    # -- run (default) ------------------------------------------------
    run_p = sub.add_parser("run", help="Start a capture session")
    run_p.add_argument(
        "-c", "--config",
        type=Path,
        default=None,
        help="Path to a YAML or JSON config file.",
    )
    run_p.add_argument(
        "--encrypt",
        action="store_true",
        help="Enable AES encryption for log files.",
    )
    run_p.add_argument(
        "--passphrase",
        type=str,
        default=None,
        help="Passphrase for encrypted logs (prompted if omitted).",
    )
    run_p.add_argument(
        "--no-analytics",
        action="store_true",
        help="Disable the biometrics analyzer.",
    )
    run_p.add_argument(
        "--log-dir",
        type=Path,
        default=None,
        help="Override the log output directory.",
    )
    run_p.add_argument(
        "--webhook-url",
        type=str,
        default=None,
        help="Webhook endpoint for remote delivery.",
    )

    # -- decrypt ------------------------------------------------------
    dec_p = sub.add_parser("decrypt", help="Decrypt an encrypted log file")
    dec_p.add_argument("file", type=Path, help="Path to the .enc log file.")
    dec_p.add_argument(
        "--passphrase",
        type=str,
        default=None,
        help="Decryption passphrase (prompted if omitted).",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Default to "run" if no subcommand given.
    if args.command is None:
        args.command = "run"
        args = parser.parse_args(["run"] + (argv or sys.argv[1:]))

    if args.command == "run":
        _cmd_run(args)
    elif args.command == "decrypt":
        _cmd_decrypt(args)


def _cmd_run(args: argparse.Namespace) -> None:
    # Load config from file or use defaults.
    if args.config and args.config.exists():
        config = AppConfig.from_file(args.config)
    else:
        config = AppConfig()

    # Apply CLI overrides.
    if args.encrypt:
        config.storage.encrypt = True
    if args.passphrase:
        config.storage.passphrase = args.passphrase
    if args.log_dir:
        config.storage.log_dir = args.log_dir
    if args.no_analytics:
        config.analytics.enabled = False
    if args.webhook_url:
        config.webhook.url = args.webhook_url

    # Prompt for passphrase if encryption is on but no passphrase given.
    if config.storage.encrypt and not config.storage.passphrase:
        import getpass
        config.storage.passphrase = getpass.getpass("Encryption passphrase: ")

    engine = AnalyticsEngine(config)
    engine.start()


def _cmd_decrypt(args: argparse.Namespace) -> None:
    from keystroke_analytics.storage.encrypted_logger import EncryptedLogger

    passphrase = args.passphrase
    if not passphrase:
        import getpass
        passphrase = getpass.getpass("Decryption passphrase: ")

    try:
        lines = EncryptedLogger.decrypt_file(args.file, passphrase)
        for line in lines:
            print(line)
    except Exception as exc:
        print(f"Decryption failed: {exc}", file=sys.stderr)
        sys.exit(1)
