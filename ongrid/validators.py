"""Validation utilities for OnGrid data"""

import re
import logging

from typing import Dict, Any, List

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
