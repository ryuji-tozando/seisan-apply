"""Helper for appending structured receipts to a CSV file."""
from __future__ import annotations

import csv
from pathlib import Path

from .parser import ReceiptRecord


CSV_HEADERS = ("日付", "業者名", "内訳概要", "合計金額（税込）", "インボイス番号", "適用")


def append_record(csv_path: Path, record: ReceiptRecord) -> None:
    """Append a :class:`ReceiptRecord` to ``csv_path`` ensuring headers exist."""

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            writer.writerow(CSV_HEADERS)
        writer.writerow(
            [
                record.date,
                record.vendor,
                record.summary,
                record.total_amount,
                record.invoice_number,
                record.notes,
            ]
        )
