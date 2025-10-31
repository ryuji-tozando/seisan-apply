"""File-system watcher orchestrating OCR and CSV output."""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Iterable

from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from watchdog.observers import Observer

from .config import ScannerConfig
from .csv_writer import append_record
from .ocr import extract_text
from .parser import ReceiptRecord, parse_receipt_text

logger = logging.getLogger(__name__)


class ReceiptEventHandler(FileSystemEventHandler):
    """Handles new files appearing in the watched directory."""

    def __init__(self, config: ScannerConfig, *, dry_run: bool = False) -> None:
        super().__init__()
        self.config = config
        self.dry_run = dry_run

    def on_created(self, event: FileCreatedEvent) -> None:  # type: ignore[override]
        path = Path(event.src_path)
        if path.is_dir():
            return
        if path.suffix.lower() not in self.config.supported_extensions:
            logger.debug("Skipping unsupported file: %s", path)
            return
        try:
            process_receipt(path, self.config, dry_run=self.dry_run)
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Failed to process receipt: %s", path)


class ReceiptScanner:
    """High-level API used by the CLI to process receipts."""

    def __init__(self, config: ScannerConfig, *, dry_run: bool = False) -> None:
        self.config = config
        self.dry_run = dry_run
        self.event_handler = ReceiptEventHandler(config, dry_run=dry_run)
        self.observer = Observer(timeout=config.poll_interval)

    def start(self) -> None:
        """Start watching the file system and block until interrupted."""

        self.config.ensure_directories()
        logger.info("Watching directory: %s", self.config.watch_dir)
        self.observer.schedule(self.event_handler, str(self.config.watch_dir), recursive=self.config.recursive)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping receipt scanner...")
        finally:
            self.observer.stop()
            self.observer.join()

    def process_existing(self) -> None:
        """Process all existing files in the watch directory."""

        self.config.ensure_directories()
        paths = iter_receipt_files(self.config.watch_dir, self.config.supported_extensions, self.config.recursive)
        for path in paths:
            process_receipt(path, self.config, dry_run=self.dry_run)


def iter_receipt_files(directory: Path, extensions: Iterable[str], recursive: bool) -> Iterable[Path]:
    """Yield receipt images within ``directory`` matching ``extensions``."""

    if recursive:
        yield from (path for path in directory.rglob("*") if path.suffix.lower() in extensions)
    else:
        yield from (path for path in directory.iterdir() if path.suffix.lower() in extensions)


def process_receipt(image_path: Path, config: ScannerConfig, *, dry_run: bool = False) -> ReceiptRecord:
    """Perform OCR on ``image_path`` and append the result to the CSV."""

    logger.info("Processing receipt: %s", image_path)
    text = extract_text(image_path, lang=config.ocr_lang)
    record = parse_receipt_text(text)
    if dry_run:
        logger.info("Dry run mode - record would be appended: %s", record)
    else:
        append_record(config.output_csv, record)
        logger.info("Appended receipt to %s", config.output_csv)
    return record
