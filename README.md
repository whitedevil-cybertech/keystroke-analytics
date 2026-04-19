# Keystroke Analytics

> Cross-platform input analytics engine with typing biometrics, encrypted storage, and modular architecture.

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Overview

**Keystroke Analytics** captures keyboard events in real time and applies
**keystroke-dynamics analysis** — a behavioural biometrics technique used in
security research for continuous user authentication and anomaly detection.

Instead of simply logging keys, it computes per-session biometric metrics:

| Metric | What it measures |
|---|---|
| **Words Per Minute** | Typing speed (5-char standard) |
| **Dwell Time** | How long each key is held (press → release) |
| **Flight Time** | Gap between consecutive key presses |
| **Rhythm Consistency** | Evenness of typing cadence (0 → 1 score) |
| **Key Frequency** | Distribution of keys and categories |

These metrics form a *keystroke-dynamics profile* — a fingerprint of how
someone types, not just what they type.

> **Disclaimer:** For authorized security research and education only.
> Unauthorized monitoring is illegal. Always obtain explicit consent.

---

## Key Features

- **Typing Biometrics** — Real-time WPM, dwell/flight time, rhythm scoring,
  key frequency heatmaps, and session analytics reports.
- **AES Encrypted Storage** — Logs encrypted with Fernet (AES-128-CBC + HMAC),
  key derived via PBKDF2-HMAC-SHA256. Includes a built-in decrypt command.
- **Cross-Platform** — Windows (win32gui + psutil), macOS (AppKit), and
  Linux (xdotool) window tracking with graceful fallbacks.
- **Modular Architecture** — Clean separation into `capture/`, `storage/`,
  `analytics/`, and `delivery/` subsystems.
- **Config File Support** — Load settings from YAML or JSON, with CLI overrides.
- **Webhook Delivery** — Batched HTTPS event delivery with configurable
  batch size and timeouts.
- **Log Rotation** — Automatic size-based rotation with timestamped filenames.
- **CLI Interface** — Full `argparse` CLI with `run` and `decrypt` subcommands.

---

## Architecture

```
                  ┌──────────────┐
                  │     CLI      │   argparse + config loading
                  └──────┬───────┘
                         │
                  ┌──────▼───────┐
                  │    Engine    │   Orchestrator
                  └──┬───┬───┬──┘
           ┌─────────┘   │   └─────────┐
    ┌──────▼──────┐ ┌────▼────┐ ┌──────▼──────┐
    │   Capture   │ │Analytics│ │   Storage   │
    │  keyboard   │ │biometri-│ │  encrypted  │
    │  + window   │ │   cs    │ │  + rotation │
    └─────────────┘ └─────────┘ └─────────────┘
                         │
                  ┌──────▼───────┐
                  │   Delivery   │   Webhook batching
                  └──────────────┘
```

Each subsystem is independently testable and replaceable.

---

## Quick Start

```bash
# Clone and enter the project
git clone <your-repo-url>
cd keylogger

# Setup (creates venv + installs everything)
uv sync --all-extras

# Run with default settings
uv run python -m keystroke_analytics run

# Run with encryption enabled
uv run python -m keystroke_analytics run --encrypt

# Decrypt a log file
uv run python -m keystroke_analytics decrypt path/to/session.enc
```

Press **Ctrl+C** to stop — you'll see a full typing analytics report:

```
═══════════════════════════════════════════
         TYPING ANALYTICS REPORT
═══════════════════════════════════════════

  Duration        : 45.2s
  Total Keystrokes: 312
  Typing Speed    : 68.4 WPM
  Avg Dwell Time  : 89.3 ms
  Avg Flight Time : 142.7 ms
  Rhythm Score    : 0.72 / 1.00

  Top Keys:
             e :   41  █████████████████████████████
             t :   28  ████████████████████████████
         [SPACE] :   52  ██████████████████████████████
  ...
═══════════════════════════════════════════
```

---

## Configuration

### CLI Flags

```
keystroke-analytics run [OPTIONS]

  -c, --config PATH       YAML or JSON config file
  --encrypt               Enable AES-encrypted log storage
  --passphrase TEXT       Encryption passphrase (prompted if omitted)
  --no-analytics          Disable biometrics analyzer
  --log-dir PATH          Override log output directory
  --webhook-url URL       Enable webhook delivery
```

### Config File (YAML)

```yaml
capture:
  log_special_keys: true
  track_windows: true
  window_poll_interval: 0.5

storage:
  log_dir: ~/.keystroke_analytics
  file_prefix: session
  max_file_size_mb: 5.0
  encrypt: false

analytics:
  enabled: true
  show_report_on_exit: true

webhook:
  url: null
  batch_size: 50
  timeout_secs: 5.0
```

---

## Project Structure

```
keystroke_analytics/
├── __init__.py              # Package exports, version
├── __main__.py              # python -m entry point
├── cli.py                   # CLI argument parsing (argparse)
├── config.py                # Dataclass config + YAML/JSON loading
├── models.py                # InputEvent, SessionStats, KeyCategory
├── engine.py                # AnalyticsEngine — central orchestrator
├── capture/
│   ├── keyboard.py          # KeyboardCapture — pynput press+release
│   └── window.py            # ActiveWindowDetector — Win/Mac/Linux
├── storage/
│   ├── encrypted_logger.py  # Fernet AES encryption with PBKDF2
│   └── rotation.py          # Size-based rotating file writer
├── analytics/
│   └── biometrics.py        # TypingBiometrics — WPM, dwell, flight, rhythm
└── delivery/
    └── webhook.py           # Batched HTTPS webhook sender

tests/
├── test_models.py           # InputEvent, SessionStats, KeyCategory
├── test_config.py           # AppConfig defaults and file loading
├── test_storage.py          # Rotation, encryption, decryption
├── test_analytics.py        # Biometrics calculations
└── test_delivery.py         # Webhook buffering and flush
```

---

## Development

```bash
# Install with dev dependencies
uv sync --extra dev

# Run tests
uv run pytest -v

# Lint
uv run ruff check keystroke_analytics/ tests/

# Type check
uv run mypy keystroke_analytics/
```

---

## How It Works

### Keystroke Dynamics

Keystroke dynamics is a behavioural biometrics technique that identifies
users by *how* they type rather than *what* they type. Two key measurements:

- **Dwell time** — Duration a key is held down (press → release). Varies
  per individual and per key; forms a unique pattern.
- **Flight time** — Interval between releasing one key and pressing the
  next. Captures typing rhythm and bigram transition speed.

The **rhythm consistency score** uses the coefficient of variation (CV) of
flight times: `score = 1 / (1 + CV)`. A metronome-like typist scores ~1.0;
an erratic one scores closer to 0.

### Encrypted Storage

When `--encrypt` is enabled:
1. A random 16-byte salt is generated per session.
2. The passphrase + salt are fed through **PBKDF2-HMAC-SHA256** (480,000
   iterations) to derive a 256-bit key.
3. Each log line is individually encrypted with **Fernet** (AES-128-CBC +
   HMAC-SHA256) and base64-encoded.
4. The salt is stored as the first line of the `.enc` file.

Decrypt with: `keystroke-analytics decrypt <file> --passphrase <pass>`

---

## License

MIT — see [LICENSE](LICENSE).
