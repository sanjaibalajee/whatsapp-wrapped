"""
Security utilities for file validation
"""

import re
from flask import current_app
from werkzeug.datastructures import FileStorage

# Optional: python-magic for MIME type detection
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False


class ValidationError(Exception):
    """Custom validation error"""
    pass


def validate_file_upload(file: FileStorage) -> tuple[bool, str]:
    """
    Validate uploaded file

    Args:
        file: Flask FileStorage object

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"

    if not file.filename:
        return False, "No filename provided"

    # Check file extension
    allowed_extensions = {'.txt'}
    ext = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        return False, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"

    # Check file size (read to check, then seek back)
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Seek back to start

    max_size = current_app.config.get("MAX_CONTENT_LENGTH", 10 * 1024 * 1024)
    if size > max_size:
        return False, f"File too large. Maximum size: {max_size // (1024 * 1024)}MB"

    if size == 0:
        return False, "File is empty"

    # Check MIME type using python-magic (if available)
    if HAS_MAGIC:
        try:
            header = file.read(2048)
            file.seek(0)

            mime = magic.from_buffer(header, mime=True)
            if mime not in ['text/plain', 'application/octet-stream']:
                try:
                    header.decode('utf-8')
                except UnicodeDecodeError:
                    return False, f"Invalid file type: {mime}"
        except Exception:
            pass

    # Check content looks like WhatsApp export
    try:
        content = file.read(5000).decode('utf-8')
        file.seek(0)

        # Log first few lines for debugging
        first_lines = content[:500].split('\n')[:5]
        current_app.logger.info(f"Upload validation - First lines preview: {first_lines}")

        # Support multiple WhatsApp timestamp formats:
        # [28/12/25, 5:30:00 PM] - US 12-hour with seconds
        # [28/12/25, 5:30 PM] - US 12-hour without seconds
        # [28/12/2025, 17:30:00] - 24-hour with 4-digit year
        # [12/28/25, 5:30:00 PM] - MM/DD/YY format
        # 28/12/25, 5:30 PM - Without brackets (some Android exports)
        patterns = [
            r'\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?::\d{2})?\s?(?:[APap][Mm])?\]',  # Bracketed formats
            r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?::\d{2})?\s?(?:[APap][Mm])?\s?[-–]',  # Non-bracketed with dash
        ]

        total_matches = 0
        pattern_matches = {}
        for pattern in patterns:
            matches = re.findall(pattern, content)
            pattern_matches[pattern[:30]] = len(matches)
            total_matches += len(matches)

        current_app.logger.info(f"Upload validation - Pattern matches: {pattern_matches}, total: {total_matches}")

        if total_matches < 2:
            current_app.logger.warning(f"Upload rejected - Not enough WhatsApp patterns found. Total matches: {total_matches}")
            return False, "File doesn't appear to be a WhatsApp chat export. Please ensure you're uploading a .txt file exported directly from WhatsApp."

    except UnicodeDecodeError as e:
        current_app.logger.warning(f"Upload rejected - UTF-8 decode error: {e}")
        return False, "File is not valid UTF-8 text"
    except Exception as e:
        current_app.logger.error(f"Upload validation error: {e}")
        return False, f"Error reading file: {str(e)}"

    return True, ""


def validate_year(year: int | str | None) -> tuple[bool, int, str]:
    """
    Validate year parameter

    Returns:
        Tuple of (is_valid, year_value, error_message)
    """
    if year is None:
        return True, 2025, ""  # Default year

    try:
        year_int = int(year)
    except (ValueError, TypeError):
        return False, 0, "Year must be a number"

    if year_int < 2009:
        return False, 0, "Year must be 2009 or later (WhatsApp was released in 2009)"

    if year_int > 2030:
        return False, 0, "Year must be 2030 or earlier"

    return True, year_int, ""


def validate_uuid(uuid_str: str) -> tuple[bool, str]:
    """
    Validate UUID format

    Returns:
        Tuple of (is_valid, error_message)
    """
    import uuid

    try:
        uuid.UUID(uuid_str)
        return True, ""
    except (ValueError, AttributeError):
        return False, "Invalid job ID format"
