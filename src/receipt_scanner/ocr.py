"""OCR helpers for extracting text from receipt images."""
from __future__ import annotations

from pathlib import Path
from typing import Final

import cv2
import numpy as np
import pytesseract


PREPROCESSING_FLAGS: Final[int] = cv2.IMREAD_COLOR


def load_image(image_path: Path) -> np.ndarray:
    """Load an image from disk and ensure it exists."""

    image = cv2.imread(str(image_path), PREPROCESSING_FLAGS)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")
    return image


def preprocess_image(image: np.ndarray) -> np.ndarray:
    """Apply simple preprocessing to improve OCR accuracy."""

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


def extract_text(image_path: Path, lang: str = "jpn") -> str:
    """Extract text from ``image_path`` using Tesseract OCR."""

    image = load_image(image_path)
    processed = preprocess_image(image)
    custom_config = "--psm 6"
    text = pytesseract.image_to_string(processed, lang=lang, config=custom_config)
    return text
