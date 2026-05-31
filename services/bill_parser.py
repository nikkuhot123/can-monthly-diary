import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

import pdfplumber
import pytesseract
from PIL import Image

from config import settings

if settings.OCR_TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = settings.OCR_TESSERACT_CMD


GSTIN_RE = re.compile(r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b")
MONEY_RE = re.compile(r"(?<![A-Za-z0-9])(?:rs\.?|inr|₹)?\s*(-?\d+(?:,\d{2,3})*(?:\.\d{1,2})?)(?![A-Za-z0-9])", re.I)
DATE_RE = re.compile(
    r"\b("
    r"\d{1,2}[./-]\d{1,2}[./-]\d{2,4}"
    r"|\d{4}[./-]\d{1,2}[./-]\d{1,2}"
    r"|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}"
    r")\b"
)


@dataclass
class ParsedHotelBill:
    raw_text: str = ""
    warnings: list[str] = field(default_factory=list)
    hotel_name: str = ""
    city: str = ""
    invoice_date: Optional[date] = None
    invoice_number: str = ""
    vendor_gstin: str = ""
    checkin_date: Optional[date] = None
    checkout_date: Optional[date] = None
    lodging_amount: float = 0.0
    boarding_amount: float = 0.0
    gst_amount: float = 0.0
    total_amount: float = 0.0
    gst_percent: float = 0.0


def extract_bill_text(file_path: str, file_type: str) -> tuple[str, list[str]]:
    ext = file_type.lower().lstrip(".")
    path = Path(file_path)
    warnings: list[str] = []

    if ext == "pdf":
        with pdfplumber.open(path) as pdf:
            pages = list(pdf.pages)  # Force into list to avoid iterator exhaustion
            text_parts: list[str] = []
            for idx, page in enumerate(pages):
                # Try text extraction first
                try:
                    page_text = page.extract_text()
                except Exception:
                    page_text = ""
                if page_text and page_text.strip():
                    text_parts.append(page_text.strip())
                    continue

                # Fall back to OCR for this page
                try:
                    image = page.to_image(resolution=180).original
                    ocr_text = pytesseract.image_to_string(image)
                    if ocr_text and ocr_text.strip():
                        text_parts.append(ocr_text.strip())
                    else:
                        warnings.append(f"Page {idx + 1}: No text could be extracted")
                except pytesseract.TesseractNotFoundError:
                    warnings.append("Tesseract OCR is not installed or not available in PATH.")
                    break  # No point continuing if OCR is unavailable
                except Exception as exc:
                    warnings.append(f"Page {idx + 1} OCR failed: {exc}")

        return "\n\n".join(text_parts), warnings

    if ext in {"jpg", "jpeg", "png"}:
        try:
            return pytesseract.image_to_string(Image.open(path)), warnings
        except pytesseract.TesseractNotFoundError:
            warnings.append("Tesseract OCR is not installed or not available in PATH.")
        except Exception as exc:
            warnings.append(f"OCR failed: {exc}")
        return "", warnings

    warnings.append(f"Unsupported bill file type: {ext}")
    return "", warnings


def parse_hotel_bill(file_path: str, file_type: str) -> ParsedHotelBill:
    raw_text, warnings = extract_bill_text(file_path, file_type)
    parsed = ParsedHotelBill(raw_text=raw_text, warnings=warnings)

    text = _normalize_text(raw_text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return parsed

    parsed.vendor_gstin = _first_match(GSTIN_RE, text)
    parsed.invoice_number = _find_labeled_text(
        lines,
        ("invoice no", "invoice number", "bill no", "bill number", "receipt no", "folio no"),
    )
    parsed.invoice_date = _find_labeled_date(lines, ("invoice date", "bill date", "receipt date", "date"))
    parsed.checkin_date = _find_labeled_date(lines, ("check in", "check-in", "arrival", "arrival date"))
    parsed.checkout_date = _find_labeled_date(lines, ("check out", "check-out", "departure", "departure date"))
    parsed.hotel_name = _find_hotel_name(lines)
    parsed.city = _find_city(text)

    total = _find_labeled_amount(lines, ("grand total", "net amount", "amount payable", "total amount", "total"))
    gst_amount = _sum_labeled_amounts(lines, ("cgst", "sgst", "igst", "tax amount", "gst amount"))
    room_amount = _find_labeled_amount(lines, ("room tariff", "room rent", "room rent total", "room charges", "lodging", "accommodation"))
    food_amount = _find_labeled_amount(lines, ("food", "restaurant", "boarding", "meal", "breakfast"))

    if total:
        parsed.total_amount = total
    if gst_amount:
        parsed.gst_amount = gst_amount

    if room_amount:
        parsed.lodging_amount = room_amount
        parsed.boarding_amount = food_amount or 0.0
    elif parsed.total_amount:
        parsed.lodging_amount = max(parsed.total_amount - parsed.gst_amount, 0.0)

    if parsed.total_amount and parsed.lodging_amount:
        implied_tax = round(parsed.total_amount - parsed.lodging_amount - parsed.boarding_amount, 2)
        if implied_tax >= 0 and (not parsed.gst_amount or abs(parsed.gst_amount - implied_tax) > 5):
            parsed.gst_amount = implied_tax

    if parsed.lodging_amount and parsed.gst_amount:
        parsed.gst_percent = round((parsed.gst_amount / parsed.lodging_amount) * 100, 2)

    if not parsed.checkout_date and parsed.checkin_date:
        parsed.checkout_date = parsed.checkin_date + timedelta(days=1)

    return parsed


def _normalize_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def _first_match(pattern: re.Pattern, text: str) -> str:
    match = pattern.search(text.upper())
    return match.group(0) if match else ""


def _find_labeled_text(lines: list[str], labels: tuple[str, ...]) -> str:
    for line in lines:
        lower = line.lower()
        if any(label in lower for label in labels):
            value = re.split(r"[:#-]", line, maxsplit=1)
            if len(value) > 1:
                candidate = value[1].strip()
                candidate = re.sub(r"\s{2,}.*$", "", candidate)
                if candidate:
                    return candidate[:100]
    return ""


def _find_labeled_date(lines: list[str], labels: tuple[str, ...]) -> Optional[date]:
    for line in lines:
        lower = line.lower()
        if any(label in lower for label in labels):
            parsed = _parse_first_date(line)
            if parsed:
                return parsed
    return None


def _parse_first_date(text: str) -> Optional[date]:
    match = DATE_RE.search(text)
    if not match:
        return None

    token = match.group(1)
    for fmt in (
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%d/%m/%y",
        "%d-%m-%y",
        "%d.%m.%y",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d %b %Y",
        "%d %B %Y",
        "%d %b %y",
        "%d %B %y",
    ):
        try:
            return datetime.strptime(token, fmt).date()
        except ValueError:
            pass
    return None


def _find_hotel_name(lines: list[str]) -> str:
    ignore = ("tax invoice", "invoice", "receipt", "gstin", "original", "duplicate")
    hotel_terms = ("hotel", "residency", "inn", "lodge", "rooms", "resort", "guest house")

    for index, line in enumerate(lines[:25]):
        lower = line.lower()
        if any(term in lower for term in hotel_terms) and not any(term in lower for term in ignore):
            if "lodging" in lower and index > 0:
                candidate = _find_nearby_business_name(lines[max(index - 6, 0):index])
                if candidate:
                    return candidate
            return _clean_name(line)

    for line in lines[:8]:
        lower = line.lower()
        if not any(term in lower for term in ignore) and len(line) > 3:
            return _clean_name(line)
    return ""


def _find_nearby_business_name(lines: list[str]) -> str:
    blocked = ("road", "highway", "towards", "ph-", "mob", "email", "@", "www", "gst", "invoice")
    for line in reversed(lines):
        lower = line.lower()
        if any(term in lower for term in blocked):
            continue
        candidate = _clean_name(line)
        letters = re.sub(r"[^A-Za-z]", "", candidate)
        if len(letters) >= 4:
            return candidate
    return ""


def _clean_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9 &.,'/-]", " ", value)
    value = re.sub(r"\s+", " ", value).strip(" -")
    return value[:200]


def _find_city(text: str) -> str:
    upper = text.upper()
    if "AHMED" in upper:
        return "Ahmednagar"
    known_cities = set(settings.CITY_CATEGORY) | set(settings.HA_CITY_OVERRIDE)
    for city in sorted(known_cities, key=len, reverse=True):
        if re.search(rf"\b{re.escape(city)}\b", upper):
            return city.title()
    return ""


def _find_labeled_amount(lines: list[str], labels: tuple[str, ...]) -> float:
    candidates: list[float] = []
    for line in lines:
        lower = line.lower()
        if any(label in lower for label in labels):
            amounts = _amounts_in_line(line)
            if amounts:
                candidates.append(amounts[-1])
    return max(candidates) if candidates else 0.0


def _sum_labeled_amounts(lines: list[str], labels: tuple[str, ...]) -> float:
    total = 0.0
    seen_lines: set[int] = set()
    for idx, line in enumerate(lines):
        lower = line.lower()
        if idx in seen_lines:
            continue
        if "gstin" in lower:
            continue
        if any(label in lower for label in labels):
            amounts = _amounts_in_line(line)
            if amounts:
                total += amounts[-1]
                seen_lines.add(idx)
    return round(total, 2)


def _amounts_in_line(line: str) -> list[float]:
    values: list[float] = []
    for match in MONEY_RE.finditer(line):
        raw = match.group(1).replace(",", "")
        try:
            values.append(float(raw))
        except ValueError:
            pass
    return values
