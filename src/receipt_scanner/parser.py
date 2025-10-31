"""Utilities for parsing OCR text into structured receipt data."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


DATE_PATTERNS = (
    re.compile(r"(?P<year>20\d{2})[./年](?P<month>\d{1,2})[./月](?P<day>\d{1,2})日?"),
    re.compile(r"(?P<month>\d{1,2})月(?P<day>\d{1,2})日"),
)
AMOUNT_PATTERN = re.compile(r"(?:(?:合計|金額)\s*[:：]?)?\s*([0-9,]+)\s*円")
INVOICE_PATTERN = re.compile(r"(T\d{2}-\d{6}-\d{5})")


@dataclass(slots=True)
class ReceiptRecord:
    """Structured representation of the fields required by the CSV output."""

    date: str
    vendor: str
    summary: str
    total_amount: str
    invoice_number: str
    notes: str = ""


def _normalize_amount(amount: str | None) -> str:
    if not amount:
        return ""
    digits = amount.replace(",", "")
    if digits.isdigit():
        return f"¥{int(digits):,}"
    return amount


def _find_first(patterns: Iterable[re.Pattern[str]], text: str) -> re.Match[str] | None:
    for pattern in patterns:
        if match := pattern.search(text):
            return match
    return None


def parse_date(text: str) -> str:
    match = _find_first(DATE_PATTERNS, text)
    if not match:
        return ""
    groups = match.groupdict()
    year = groups.get("year")
    month = groups.get("month")
    day = groups.get("day")
    today = datetime.today()
    if year is None:
        year = str(today.year)
    date = datetime(int(year), int(month), int(day))
    return date.strftime("%Y-%m-%d")


def parse_total_amount(text: str) -> str:
    match = AMOUNT_PATTERN.search(text)
    if not match:
        return ""
    return _normalize_amount(match.group(1))


def parse_invoice_number(text: str) -> str:
    match = INVOICE_PATTERN.search(text)
    if not match:
        return "要調査"
    return match.group(1)


def parse_vendor(lines: list[str]) -> str:
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
        if any(keyword in cleaned for keyword in ("株式会社", "有限会社", "合同会社", "店", "ショップ", "センター")):
            return cleaned
    return lines[0].strip() if lines else ""


def parse_summary(lines: list[str]) -> str:
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
        if any(keyword in cleaned for keyword in ("内訳", "摘要", "品目", "サービス")):
            return cleaned
    return ""


def parse_receipt_text(text: str) -> ReceiptRecord:
    lines = [line for line in (line.strip() for line in text.splitlines()) if line]
    date = parse_date(text)
    total_amount = parse_total_amount(text)
    invoice_number = parse_invoice_number(text)
    vendor = parse_vendor(lines)
    summary = parse_summary(lines)

    return ReceiptRecord(
        date=date,
        vendor=vendor,
        summary=summary,
        total_amount=total_amount,
        invoice_number=invoice_number,
        notes="",
    )
