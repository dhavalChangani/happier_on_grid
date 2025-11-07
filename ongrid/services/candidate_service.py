"""Candidate onboarding service"""

import logging

from typing import Dict, Any, List, Optional

from ongrid.exceptions import OnGridException, ValidationException
from ongrid.http_client import HttpClient
from ongrid.validators import validate_candidate_data

logger = logging.getLogger(__name__)


class CandidateService:
    """Service for managing candidate onboarding operations"""

    def __init__(
        self, http_client: HttpClient, community_id: str, consent_text: str
    ):
        """
        Initialize candidate service.

        Args:
            http_client: HTTP client instance
            community_id: OnGrid community ID
            consent_text: Consent text for candidates
        """
        self.http = http_client
        self.community_id = community_id
        self.consent_text = consent_text

    def onboard_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Onboard an individual in the OnGrid community.

        Args:
            candidate_data: Dictionary containing candidate information

        Returns:
            API response containing individual details

        Raises:
            ValidationException: If required fields are missing or invalid
            OnGridException: If the API request fails
        """
        try:
            validation_errors = validate_candidate_data(
                candidate_data, self.consent_text
            )

            if validation_errors:
                error_message = (
                    "Validation failed with the following errors:\n"
                    + "\n".join(f"  - {error}" for error in validation_errors)
                )
                raise ValidationException(error_message)

            payload = self._build_onboard_payload(candidate_data)

            logger.info(
                f"Onboarding individual: {candidate_data.get('name')} "
                f"(email: {candidate_data.get('email') or 'N/A'})"
            )
            endpoint = f"/app/v1/community/{self.community_id}/individuals"
            response = self.http.make_request("POST", endpoint, data=payload)

            logger.info(f"Individual onboarded successfully: ID {response.get('id')}")
            return response

        except ValidationException as e:
            logger.error(f"Validation error: {e}")
            raise
        except OnGridException as e:
            logger.error(f"Onboarding failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during onboarding: {e}")
            raise OnGridException(f"Onboarding failed: {str(e)}")

    def onboard_and_initiate_verifications(
        self,
        candidate_data: Dict[str, Any],
        verifications: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Onboard an individual and simultaneously initiate background verifications.

        Args:
            candidate_data: Dictionary containing candidate information
            verifications: List of verification objects to initiate

        Returns:
            API response containing individual and verification details

        Raises:
            ValidationException: If required fields are missing or invalid
            OnGridException: If the API request fails
        """
        try:
            validation_errors = validate_candidate_data(
                candidate_data, self.consent_text
            )

            if validation_errors:
                error_message = (
                    "Validation failed with the following errors:\n"
                    + "\n".join(f"  - {error}" for error in validation_errors)
                )
                raise ValidationException(error_message)

            payload = self._build_onboard_payload(candidate_data)

            if verifications:
                payload["verifications"] = verifications

            logger.info(
                f"Onboarding and initiating verifications for: {candidate_data.get('name')}"
            )
            if verifications:
                verification_codes = [
                    str(v.get("code", "UNKNOWN")) for v in verifications
                ]
                logger.info(f"Initiating verifications: {', '.join(verification_codes)}")

            endpoint = f"/app/v1/community/{self.community_id}/individuals/initiate"
            response = self.http.make_request("POST", endpoint, data=payload)

            individual_id = response.get("individual", {}).get("id")
            logger.info(f"Individual onboarded successfully: ID {individual_id}")

            if "verifications" in response and response["verifications"]:
                logger.info(f"Initiated {len(response['verifications'])} verification(s)")
                for verification in response["verifications"]:
                    logger.info(
                        f"  - {verification.get('code')}: "
                        f"Request ID {verification.get('requestId')}"
                    )

            return response

        except ValidationException as e:
            logger.error(f"Validation error: {e}")
            raise
        except OnGridException as e:
            logger.error(f"Onboarding and verification initiation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during onboarding and verification: {e}")
            raise OnGridException(f"Onboarding and verification failed: {str(e)}")

    def _build_onboard_payload(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build API payload from candidate data.

        Args:
            candidate_data: Dictionary containing candidate information

        Returns:
            Payload dictionary for API request
        """
        payload = {
            "name": candidate_data.get("name"),
            "professionId": candidate_data.get("profession_id"),
            "gender": candidate_data.get("gender"),
            "city": candidate_data.get("city"),
            "phone": candidate_data.get("phone"),
            "phoneCountryCode": candidate_data.get("phone_country_code", "91"),
            "hasConsent": candidate_data.get("has_consent"),
            "consentText": self.consent_text,
        }

        optional_field_mapping = {
            "individual_id": "individualId",
            "uid": "uid",
            "email": "email",
            "dob": "dob",
            "other_profession": "otherProfession",
            "permanent_address": "permanentAddress",
            "current_address": "currentAddress",
            "current_address_country": "currentAddressCountry",
            "current_address_id": "currentAddressId",
            "employee_id": "employeeId",
            "other_identifiers": "otherIdentifiers",
            "l_current_address": "lCurrentAddress",
            "ln_code": "lnCode",
            "fathers_name": "fathersName",
            "alternate_phone": "alternatePhone",
            "alternate_phone_country_code": "alternatePhoneCountryCode",
            "joining_date": "joiningDate",
            "tags": "tags",
            "deduplication_keys": "deduplicationKeys",
            "uans": "uans",
        }

        for python_key, api_key in optional_field_mapping.items():
            if python_key in candidate_data and candidate_data[python_key] is not None:
                payload[api_key] = candidate_data[python_key]

        return payload
