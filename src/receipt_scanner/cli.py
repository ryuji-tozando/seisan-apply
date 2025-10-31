"""Command line entry point for the receipt scanner."""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .config import ScannerConfig
from .watcher import ReceiptScanner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Auto OCR receipts and append them to a CSV file")
    parser.add_argument("watch_dir", type=Path, help="Directory that stores receipt images")
    parser.add_argument("output_csv", type=Path, help="Destination CSV file path")
    parser.add_argument("--recursive", action="store_true", help="Watch subdirectories for receipts")
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=1.0,
        help="Polling interval for file system observer fallbacks (seconds)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Run OCR without writing to CSV")
    parser.add_argument(
        "--process-existing",
        action="store_true",
        help="Process existing files before starting the watcher",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity",
    )
    parser.add_argument(
        "--lang",
        default="jpn",
        help="Language hint passed to Tesseract (default: jpn)",
    )
    return parser


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    configure_logging(args.log_level)

    config = ScannerConfig.from_cli(
        watch_dir=str(args.watch_dir),
        output_csv=str(args.output_csv),
        recursive=args.recursive,
        poll_interval=args.poll_interval,
        ocr_lang=args.lang,
    )
    scanner = ReceiptScanner(config, dry_run=args.dry_run)

    if args.process_existing:
        scanner.process_existing()
    if args.dry_run:
        return 0

    try:
        scanner.start()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
