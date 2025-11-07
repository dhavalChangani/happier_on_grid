"""Verification request service"""

import logging

from typing import Dict, Any, List, Optional

from ongrid.exceptions import ValidationException
from ongrid.http_client import HttpClient
from ongrid import validators

logger = logging.getLogger(__name__)


class VerificationService:
    """Service for managing verification requests"""

    def __init__(self, http_client: HttpClient):
        """
        Initialize verification service.

        Args:
            http_client: HTTP client instance
        """
        self.http = http_client

    def request_pan_verification(
        self, individual_id: int, document_id: int
    ) -> Dict[str, Any]:
        """
        Request PAN verification for an individual.

        Args:
            individual_id: Individual's unique ID at OnGrid
            document_id: ID of the PAN document to verify

        Returns:
            API response dictionary

        Raises:
            ValidationException: If validation fails
            OnGridException: If request fails
        """
        validation_errors = []
        validation_errors.extend(
            validators.validate_positive_integer(individual_id, "individual_id")
        )
        validation_errors.extend(
            validators.validate_positive_integer(document_id, "document_id")
        )

        if validation_errors:
            raise ValidationException(f"Validation failed: {'; '.join(validation_errors)}")

        with self.http.handle_api_exceptions("request PAN verification"):
            endpoint = f"/app/v1/individual/{individual_id}/panv"

            payload = {"documentId": document_id}

            response = self.http.make_request(
                method="POST", endpoint=endpoint, data=payload
            )

            logger.info(
                f"PAN verification requested for individual ID {individual_id}, "
                f"document ID {document_id}, request ID: {response.get('requestId')}"
            )
            return response

    def request_education_verification(
        self, individual_id: int, education_document_id: int
    ) -> Dict[str, Any]:
        """
        Request education verification for an individual.

        Args:
            individual_id: Individual's unique ID at OnGrid
            education_document_id: ID of the education document to verify

        Returns:
            API response dictionary

        Raises:
            ValidationException: If validation fails
            OnGridException: If request fails
        """
        validation_errors = []
        validation_errors.extend(
            validators.validate_positive_integer(individual_id, "individual_id")
        )
        validation_errors.extend(
            validators.validate_positive_integer(education_document_id, "education_document_id")
        )

        if validation_errors:
            raise ValidationException(f"Validation failed: {'; '.join(validation_errors)}")

        with self.http.handle_api_exceptions("request education verification"):
            endpoint = f"/app/v1/individual/{individual_id}/eduv"

            payload = {"educationDocumentId": education_document_id}

            response = self.http.make_request(
                method="POST", endpoint=endpoint, data=payload
            )

            logger.info(
                f"Education verification requested for individual ID {individual_id}, "
                f"education document ID {education_document_id}, "
                f"request ID: {response.get('requestId')}"
            )
            return response

    def request_employment_verification(
        self, individual_id: int, employment_record_id: int
    ) -> Dict[str, Any]:
        """
        Request employment verification for an individual.

        Args:
            individual_id: Individual's unique ID at OnGrid
            employment_record_id: ID of the employment record to verify

        Returns:
            API response dictionary

        Raises:
            ValidationException: If validation fails
            OnGridException: If request fails
        """
        validation_errors = []
        validation_errors.extend(
            validators.validate_positive_integer(individual_id, "individual_id")
        )
        validation_errors.extend(
            validators.validate_positive_integer(employment_record_id, "employment_record_id")
        )

        if validation_errors:
            raise ValidationException(f"Validation failed: {'; '.join(validation_errors)}")

        with self.http.handle_api_exceptions("request employment verification"):
            endpoint = f"/app/v1/individual/{individual_id}/empv"

            payload = {"employmentRecordId": employment_record_id}

            response = self.http.make_request(
                method="POST", endpoint=endpoint, data=payload
            )

            logger.info(
                f"Employment verification requested for individual ID {individual_id}, "
                f"employment record ID {employment_record_id}, "
                f"request ID: {response.get('requestId')}"
            )
            return response

    def request_employment_history_check(
        self, individual_id: int, uans: List[str]
    ) -> Dict[str, Any]:
        """
        Request employment history check for an individual.

        Args:
            individual_id: Individual's unique ID at OnGrid
            uans: List of UAN numbers of the individual

        Returns:
            API response dictionary

        Raises:
            ValidationException: If validation fails
            OnGridException: If request fails
        """
        validation_errors = []
        validation_errors.extend(
            validators.validate_positive_integer(individual_id, "individual_id")
        )

        if not uans or not isinstance(uans, list):
            validation_errors.append("uans must be a non-empty list of UAN numbers")
        elif len(uans) == 0:
            validation_errors.append("uans list cannot be empty")

        if validation_errors:
            raise ValidationException(f"Validation failed: {'; '.join(validation_errors)}")

        with self.http.handle_api_exceptions("request employment history check"):
            endpoint = f"/app/v1/individual/{individual_id}/ehc"

            payload = {"uans": uans}

            response = self.http.make_request(
                method="POST", endpoint=endpoint, data=payload
            )

            logger.info(
                f"Employment history check requested for individual ID {individual_id}, "
                f"UAN count: {len(uans)}, request ID: {response.get('requestId')}"
            )
            return response

    def request_prc(
        self,
        individual_id: int,
        schema_id: int,
        reference_provider_name: str,
        reference_provider_email: str,
        organisation: str,
        designation: str,
        reference_type: str,
        reporting_manager: bool,
        reference_provider_id: Optional[int] = None,
        reference_provider_phone: Optional[str] = None,
        reference_provider_phone_country_code: Optional[str] = None,
        start_year_of_association: Optional[int] = None,
        end_year_of_association: Optional[int] = None,
        individual_designation: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Request a Professional Reference Check for an individual.

        Args:
            individual_id: Individual's unique ID at OnGrid
            schema_id: Schema ID for data collection
            reference_provider_name: Name of reference provider
            reference_provider_email: Email of reference provider
            organisation: Organisation name
            designation: Designation of reference provider
            reference_type: Type of reference (Academic/Professional)
            reporting_manager: Whether reference provider is reporting manager
            reference_provider_id: ID of reference provider (optional)
            reference_provider_phone: Phone of reference provider (optional)
            reference_provider_phone_country_code: Country code of phone (optional)
            start_year_of_association: Start year of association (optional)
            end_year_of_association: End year of association (optional)
            individual_designation: Individual's designation (optional)

        Returns:
            API response dictionary

        Raises:
            ValidationException: If validation fails
            OnGridException: If request fails
        """
        validation_errors = []

        validation_errors.extend(
            validators.validate_positive_integer(individual_id, "individual_id")
        )
        validation_errors.extend(
            validators.validate_positive_integer(schema_id, "schema_id")
        )
        validation_errors.extend(
            validators.validate_required_string(reference_provider_name, "reference_provider_name")
        )
        validation_errors.extend(
            validators.validate_email(reference_provider_email, "reference_provider_email")
        )
        validation_errors.extend(
            validators.validate_required_string(organisation, "organisation")
        )
        validation_errors.extend(
            validators.validate_required_string(designation, "designation")
        )

        if reference_type not in ["Academic", "Professional"]:
            validation_errors.append(
                "reference_type must be either 'Academic' or 'Professional'"
            )

        if not isinstance(reporting_manager, bool):
            validation_errors.append("reporting_manager must be a boolean value")

        validation_errors.extend(
            validators.validate_positive_integer(reference_provider_id, "reference_provider_id")
        )
        validation_errors.extend(
            validators.validate_phone_number(reference_provider_phone, "reference_provider_phone")
        )
        validation_errors.extend(
            validators.validate_optional_string(reference_provider_phone_country_code, "reference_provider_phone_country_code", max_length=5)
        )
        validation_errors.extend(
            validators.validate_year(start_year_of_association, "start_year_of_association")
        )
        validation_errors.extend(
            validators.validate_year(end_year_of_association, "end_year_of_association")
        )
        validation_errors.extend(
            validators.validate_optional_string(individual_designation, "individual_designation")
        )

        if validation_errors:
            raise ValidationException(f"Validation failed: {'; '.join(validation_errors)}")

        with self.http.handle_api_exceptions("request PRC"):
            endpoint = f"/app/v1/individual/{individual_id}/prc"

            payload = self.http.build_form_data(
                required_fields={
                    "schemaId": schema_id,
                    "referenceProviderName": reference_provider_name,
                    "referenceProviderEmail": reference_provider_email,
                    "organisation": organisation,
                    "designation": designation,
                    "referenceType": reference_type,
                    "reportingManager": reporting_manager,
                },
                optional_fields={
                    "referenceProviderId": reference_provider_id,
                    "referenceProviderPhone": reference_provider_phone,
                    "referenceProviderPhoneCountryCode": reference_provider_phone_country_code,
                    "startYearOfAssociation": start_year_of_association,
                    "endYearOfAssociation": end_year_of_association,
                    "individualDesignation": individual_designation,
                },
            )

            response = self.http.make_request(
                method="POST", endpoint=endpoint, data=payload
            )

            logger.info(
                f"PRC requested for individual ID {individual_id}, "
                f"request ID: {response.get('requestId')}"
            )
            return response
