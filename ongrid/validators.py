"""Validation utilities for OnGrid data"""

import re
import logging

from typing import Dict, Any, List, Optional

from ongrid.enums import Gender

logger = logging.getLogger(__name__)


def validate_candidate_data(
    candidate_data: Dict[str, Any], consent_text: str
) -> List[str]:
    """
    Validate candidate data and return list of validation errors.

    Args:
        candidate_data: Dictionary containing candidate information
        consent_text: Consent text to validate

    Returns:
        List of validation error messages (empty if no errors)
    """
    validation_errors = []

    name = candidate_data.get("name")
    profession_id = candidate_data.get("profession_id")
    gender = candidate_data.get("gender")
    city = candidate_data.get("city")
    phone = candidate_data.get("phone")
    has_consent = candidate_data.get("has_consent")
    email = candidate_data.get("email")
    alternate_phone = candidate_data.get("alternate_phone")
    dob = candidate_data.get("dob")
    joining_date = candidate_data.get("joining_date")
    ln_code = candidate_data.get("ln_code")

    required_fields = {
        "name": name,
        "profession_id": profession_id,
        "gender": gender,
        "city": city,
        "phone": phone,
        "consent_text": consent_text,
    }

    for field_name, field_value in required_fields.items():
        if not field_value:
            validation_errors.append(
                f"Required field '{field_name}' is missing or empty"
            )

    if has_consent is None:
        validation_errors.append("Required field 'has_consent' is missing")
    elif not isinstance(has_consent, bool):
        validation_errors.append(
            "Field 'has_consent' must be a boolean value (true/false)"
        )

    if gender:
        valid_genders = [g.value for g in Gender]
        if gender not in valid_genders:
            validation_errors.append(
                f"Invalid gender '{gender}'. Must be one of: {', '.join(valid_genders)}"
            )

    if phone:
        if not phone.strip():
            validation_errors.append("Phone number cannot be empty")
        else:
            cleaned_phone = (
                phone.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
            )
            if not cleaned_phone.isdigit():
                validation_errors.append(f"Invalid phone number format: {phone}")

    if email:
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            validation_errors.append(f"Invalid email format: {email}")

    if alternate_phone:
        if not alternate_phone.strip():
            validation_errors.append("Alternate phone number cannot be empty")
        else:
            cleaned_alt_phone = (
                alternate_phone.replace("-", "")
                .replace(" ", "")
                .replace("(", "")
                .replace(")", "")
            )
            if not cleaned_alt_phone.isdigit():
                validation_errors.append(
                    f"Invalid alternate phone number format: {alternate_phone}"
                )

    if dob:
        if not (
            re.match(r"^\d{4}-\d{2}-\d{2}$", dob) or re.match(r"^\d{4}$", dob)
        ):
            validation_errors.append(
                f"Invalid date of birth format: {dob}. Must be 'yyyy-MM-dd' or 'yyyy'"
            )

    if joining_date:
        if not (
            re.match(r"^\d{4}-\d{2}-\d{2}$", joining_date)
            or re.match(r"^\d{4}$", joining_date)
        ):
            validation_errors.append(
                f"Invalid joining date format: {joining_date}. Must be 'yyyy-MM-dd' or 'yyyy'"
            )

    if ln_code and ln_code != "hi-IN":
        validation_errors.append("Only 'hi-IN' is supported for language code")

    return validation_errors


def validate_file_path(file_path: str) -> List[str]:
    """
    Validate file path exists and is accessible.

    Args:
        file_path: Path to file

    Returns:
        List of validation error messages (empty if no errors)
    """
    import os

    validation_errors = []

    if not file_path:
        validation_errors.append("File path is required")
        return validation_errors

    if not isinstance(file_path, str):
        validation_errors.append("File path must be a string")
        return validation_errors

    if not os.path.exists(file_path):
        validation_errors.append(f"File does not exist: {file_path}")
        return validation_errors

    if not os.path.isfile(file_path):
        validation_errors.append(f"Path is not a file: {file_path}")
        return validation_errors

    if os.path.getsize(file_path) == 0:
        validation_errors.append(f"File is empty: {file_path}")

    return validation_errors


def validate_date_format(date_str: Optional[str], field_name: str) -> List[str]:
    """
    Validate date format (yyyy-MM-dd or yyyy).

    Args:
        date_str: Date string to validate
        field_name: Name of the field for error messages

    Returns:
        List of validation error messages (empty if no errors)
    """
    validation_errors = []

    if not date_str:
        return validation_errors

    if not isinstance(date_str, str):
        validation_errors.append(f"{field_name} must be a string")
        return validation_errors

    if not (re.match(r"^\d{4}-\d{2}-\d{2}$", date_str) or re.match(r"^\d{4}$", date_str)):
        validation_errors.append(
            f"Invalid {field_name} format: {date_str}. Must be 'yyyy-MM-dd' or 'yyyy'"
        )

    return validation_errors


def validate_pan_number(pan: str) -> List[str]:
    """
    Validate PAN number format.

    Args:
        pan: PAN number to validate

    Returns:
        List of validation error messages (empty if no errors)
    """
    validation_errors = []

    if not pan:
        validation_errors.append("PAN number is required")
        return validation_errors

    if not isinstance(pan, str):
        validation_errors.append("PAN number must be a string")
        return validation_errors

    pan = pan.strip().upper()

    if len(pan) != 10:
        validation_errors.append(f"PAN number must be 10 characters long, got {len(pan)}")
        return validation_errors

    pan_pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"
    if not re.match(pan_pattern, pan):
        validation_errors.append(
            f"Invalid PAN number format: {pan}. Must match pattern: ABCDE1234F"
        )

    return validation_errors


def validate_email(email: Optional[str], field_name: str = "email") -> List[str]:
    """
    Validate email format.

    Args:
        email: Email address to validate
        field_name: Name of the field for error messages

    Returns:
        List of validation error messages (empty if no errors)
    """
    validation_errors = []

    if not email:
        return validation_errors

    if not isinstance(email, str):
        validation_errors.append(f"{field_name} must be a string")
        return validation_errors

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        validation_errors.append(f"Invalid {field_name} format: {email}")

    return validation_errors


def validate_phone_number(phone: Optional[str], field_name: str = "phone") -> List[str]:
    """
    Validate phone number format.

    Args:
        phone: Phone number to validate
        field_name: Name of the field for error messages

    Returns:
        List of validation error messages (empty if no errors)
    """
    validation_errors = []

    if not phone:
        return validation_errors

    if not isinstance(phone, str):
        validation_errors.append(f"{field_name} must be a string")
        return validation_errors

    if not phone.strip():
        validation_errors.append(f"{field_name} cannot be empty or whitespace")
        return validation_errors

    cleaned_phone = (
        phone.replace("-", "")
        .replace(" ", "")
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
    )

    if not cleaned_phone.isdigit():
        validation_errors.append(f"Invalid {field_name} format: {phone}")
    elif len(cleaned_phone) < 10:
        validation_errors.append(f"{field_name} must be at least 10 digits: {phone}")

    return validation_errors


def validate_positive_integer(value: Optional[int], field_name: str) -> List[str]:
    """
    Validate positive integer value.

    Args:
        value: Integer value to validate
        field_name: Name of the field for error messages

    Returns:
        List of validation error messages (empty if no errors)
    """
    validation_errors = []

    if value is None:
        return validation_errors

    if not isinstance(value, int):
        validation_errors.append(f"{field_name} must be an integer")
        return validation_errors

    if value <= 0:
        validation_errors.append(f"{field_name} must be a positive integer, got {value}")

    return validation_errors


def validate_year(year: Optional[int], field_name: str = "year") -> List[str]:
    """
    Validate year value.

    Args:
        year: Year to validate
        field_name: Name of the field for error messages

    Returns:
        List of validation error messages (empty if no errors)
    """
    validation_errors = []

    if year is None:
        return validation_errors

    if not isinstance(year, int):
        validation_errors.append(f"{field_name} must be an integer")
        return validation_errors

    if year < 1900 or year > 2100:
        validation_errors.append(
            f"Invalid {field_name}: {year}. Must be between 1900 and 2100"
        )

    return validation_errors


def validate_required_string(
    value: str, field_name: str, max_length: int = 256
) -> List[str]:
    """
    Validate required string field.

    Args:
        value: String value to validate
        field_name: Name of the field for error messages
        max_length: Maximum allowed length (default: 256)

    Returns:
        List of validation error messages (empty if no errors)
    """
    validation_errors = []

    if not value:
        validation_errors.append(f"{field_name} is required")
        return validation_errors

    if not isinstance(value, str):
        validation_errors.append(f"{field_name} must be a string")
        return validation_errors

    if not value.strip():
        validation_errors.append(f"{field_name} cannot be empty or whitespace")
        return validation_errors

    if len(value) > max_length:
        validation_errors.append(
            f"{field_name} exceeds maximum length of {max_length} characters "
            f"(got {len(value)})"
        )

    return validation_errors


def validate_optional_string(
    value: Optional[str], field_name: str, max_length: int = 256
) -> List[str]:
    """
    Validate optional string field.

    Args:
        value: String value to validate
        field_name: Name of the field for error messages
        max_length: Maximum allowed length (default: 256)

    Returns:
        List of validation error messages (empty if no errors)
    """
    validation_errors = []

    if value is None:
        return validation_errors

    if not isinstance(value, str):
        validation_errors.append(f"{field_name} must be a string")
        return validation_errors

    if len(value) > max_length:
        validation_errors.append(
            f"{field_name} exceeds maximum length of {max_length} characters "
            f"(got {len(value)})"
        )

    return validation_errors


def validate_education_level(level: str) -> List[str]:
    """
    Validate education level.

    Args:
        level: Education level to validate

    Returns:
        List of validation error messages (empty if no errors)
    """
    validation_errors = []

    if not level:
        validation_errors.append("Education level is required")
        return validation_errors

    valid_levels = [
        "NO_EDUCATION",
        "LESS_THEN_FIFTH_STD",
        "FIFTH_STD",
        "EIGHT_STD",
        "TENTH_STD",
        "TWELFTH_STD",
        "DIPLOMA",
        "GRADUATE",
        "PROFESSIONAL_COURSE",
        "MASTERS",
        "PHD",
        "POST_DOC",
        "POT_GRADUATE_DIPLOMA",
        "OTHER",
        "NA",
    ]

    if level not in valid_levels:
        validation_errors.append(
            f"Invalid education level: {level}. Must be one of: {', '.join(valid_levels)}"
        )

    return validation_errors
