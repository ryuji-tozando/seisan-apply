"""Configuration helpers for the receipt scanner application."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ScannerConfig:
    """Runtime configuration for the receipt scanner.

    Attributes
    ----------
    watch_dir:
        Directory to watch for new receipt images.
    output_csv:
        Destination CSV file where parsed receipt information is appended.
    recursive:
        Whether subdirectories of ``watch_dir`` should be observed.
    poll_interval:
        Interval in seconds for polling-based observers. Only applies to
        platforms without native file system events.
    supported_extensions:
        Set of lowercase file suffixes that are considered valid receipt
        images. ``".pdf"`` is intentionally excluded because OCR pipelines
        for PDF require additional tooling.
    ocr_lang:
        Language hint passed to Tesseract OCR. Defaults to Japanese (``"jpn"``).
    """

    watch_dir: Path
    output_csv: Path
    recursive: bool = False
    poll_interval: float = 1.0
    ocr_lang: str = "jpn"
    supported_extensions: tuple[str, ...] = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp")

    @classmethod
    def from_cli(
        cls,
        watch_dir: str,
        output_csv: str,
        *,
        recursive: bool = False,
        poll_interval: float = 1.0,
        ocr_lang: str = "jpn",
    ) -> "ScannerConfig":
        """Factory used by the CLI to translate arguments into a config object."""

        return cls(
            watch_dir=Path(watch_dir).expanduser().resolve(),
            output_csv=Path(output_csv).expanduser().resolve(),
            recursive=recursive,
            poll_interval=poll_interval,
            ocr_lang=ocr_lang,
        )

    def ensure_directories(self) -> None:
        """Create watch and destination directories if they are missing."""

        self.watch_dir.mkdir(parents=True, exist_ok=True)
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
