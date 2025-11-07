"""OnGrid Background Verification Client"""

import logging
import os

from typing import Dict, Any, List, Optional

from ongrid.exceptions import OnGridException
from ongrid.http_client import HttpClient
from ongrid.services import (
    CandidateService,
    DocumentService,
    VerificationService,
    StatusService,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OnGridClient:
    """
    OnGrid Background Verification Client.

    This class provides interface to OnGrid's background verification APIs.
    """

    def __init__(self, community_id: str, enable_logging: bool = True):
        """
        Initialize OnGrid client.

        Args:
            community_id: OnGrid Community ID
            enable_logging: Enable/disable logging

        Raises:
            OnGridException: If required configuration is missing
        """
        client_id = os.getenv("ONGRID_CLIENT_ID", "your-client-id-here")
        client_secret = os.getenv("ONGRID_CLIENT_SECRET", "your-client-secret-here")
        base_url = os.getenv("ONGRID_BASE_URL", "https://api-staging.ongrid.in")
        consent_text = os.getenv(
            "ONGRID_CONSENT_TEXT", "I agree to background verification"
        )

        if not community_id:
            raise OnGridException("Community ID is required")
        if not consent_text:
            raise OnGridException("Consent text is required")

        if not enable_logging:
            logger.setLevel(logging.WARNING)

        self.community_id = community_id
        self.consent_text = consent_text

        self.http = HttpClient(client_id, client_secret, base_url)
        self.candidates = CandidateService(self.http, community_id, consent_text)
        self.documents = DocumentService(self.http)
        self.verifications = VerificationService(self.http)
        self.status = StatusService(self.http)

        logger.info("OnGrid client initialized")

    def onboard_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Onboard an individual in the OnGrid community.

        Args:
            candidate_data: Dictionary containing candidate information

        Returns:
            API response containing individual details
        """
        return self.candidates.onboard_candidate(candidate_data)

    def onboard_and_initiate_verifications(
        self,
        candidate_data: Dict[str, Any],
        verifications: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Onboard an individual and simultaneously initiate verifications.

        Args:
            candidate_data: Dictionary containing candidate information
            verifications: List of verification objects to initiate

        Returns:
            API response containing individual and verification details
        """
        return self.candidates.onboard_and_initiate_verifications(
            candidate_data, verifications
        )

    def add_document(
        self,
        individual_id: int,
        doc_type: str,
        file_path: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Add a document to individual record."""
        return self.documents.add_document(individual_id, doc_type, file_path, body)

    def add_pan_document(
        self,
        individual_id: int,
        file_path: str,
        document_uid: str,
        name_as_per_document: str,
        legal_guardian_name: Optional[str] = None,
        dob: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a PAN document to individual record."""
        return self.documents.add_pan_document(
            individual_id,
            file_path,
            document_uid,
            name_as_per_document,
            legal_guardian_name,
            dob,
        )

    def update_pan_document(
        self,
        individual_id: int,
        document_id: int,
        file_path: str,
        document_uid: str,
        name_as_per_document: str,
        legal_guardian_name: Optional[str] = None,
        dob: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing PAN document."""
        return self.documents.update_pan_document(
            individual_id,
            document_id,
            file_path,
            document_uid,
            name_as_per_document,
            legal_guardian_name,
            dob,
        )

    def add_education_document(
        self,
        individual_id: int,
        file_path: str,
        level: str,
        name_of_institute: str,
        degree: str,
        name_as_per_document: str,
        registration_number: str,
        year_of_passing: Optional[int] = None,
        field_of_study: Optional[str] = None,
        duration_in_months: Optional[int] = None,
        grade: Optional[str] = None,
        name_of_board_university: Optional[str] = None,
        issue_date: Optional[str] = None,
        document_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add an education document to individual record."""
        return self.documents.add_education_document(
            individual_id,
            file_path,
            level,
            name_of_institute,
            degree,
            name_as_per_document,
            registration_number,
            year_of_passing,
            field_of_study,
            duration_in_months,
            grade,
            name_of_board_university,
            issue_date,
            document_id,
        )

    def add_employment_record(
        self,
        individual_id: int,
        name_as_per_employer_records: str,
        employer_name: str,
        employment_record_id: Optional[int] = None,
        employee_id: Optional[str] = None,
        last_designation: Optional[str] = None,
        job_description: Optional[str] = None,
        last_working_city: Optional[str] = None,
        joining_date: Optional[str] = None,
        last_working_date: Optional[str] = None,
        annual_compensation: Optional[int] = None,
        salaryslip_path: Optional[str] = None,
        appointmentletter_path: Optional[str] = None,
        experienceletter_path: Optional[str] = None,
        manager_name: Optional[str] = None,
        manager_email: Optional[str] = None,
        manager_phone: Optional[str] = None,
        manager_phone_country_code: Optional[str] = None,
        hr_name: Optional[str] = None,
        hr_email: Optional[str] = None,
        hr_phone: Optional[str] = None,
        hr_phone_country_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add an employment record to individual record."""
        return self.documents.add_employment_record(
            individual_id,
            name_as_per_employer_records,
            employer_name,
            employment_record_id,
            employee_id,
            last_designation,
            job_description,
            last_working_city,
            joining_date,
            last_working_date,
            annual_compensation,
            salaryslip_path,
            appointmentletter_path,
            experienceletter_path,
            manager_name,
            manager_email,
            manager_phone,
            manager_phone_country_code,
            hr_name,
            hr_email,
            hr_phone,
            hr_phone_country_code,
        )

    def request_pan_verification(
        self, individual_id: int, document_id: int
    ) -> Dict[str, Any]:
        """Request PAN verification for an individual."""
        return self.verifications.request_pan_verification(individual_id, document_id)

    def request_education_verification(
        self, individual_id: int, education_document_id: int
    ) -> Dict[str, Any]:
        """Request education verification for an individual."""
        return self.verifications.request_education_verification(
            individual_id, education_document_id
        )

    def request_employment_verification(
        self, individual_id: int, employment_record_id: int
    ) -> Dict[str, Any]:
        """Request employment verification for an individual."""
        return self.verifications.request_employment_verification(
            individual_id, employment_record_id
        )

    def request_employment_history_check(
        self, individual_id: int, uans: List[str]
    ) -> Dict[str, Any]:
        """Request employment history check for an individual."""
        return self.verifications.request_employment_history_check(individual_id, uans)

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
        """Request a Professional Reference Check for an individual."""
        return self.verifications.request_prc(
            individual_id,
            schema_id,
            reference_provider_name,
            reference_provider_email,
            organisation,
            designation,
            reference_type,
            reporting_manager,
            reference_provider_id,
            reference_provider_phone,
            reference_provider_phone_country_code,
            start_year_of_association,
            end_year_of_association,
            individual_designation,
        )

    def get_pan_verification_status(
        self, individual_id: int, request_id: int
    ) -> Dict[str, Any]:
        """Get PAN verification status for an individual."""
        return self.status.get_pan_verification_status(individual_id, request_id)

    def get_education_verification_status(
        self, individual_id: int, request_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get education verification status for an individual."""
        return self.status.get_education_verification_status(individual_id, request_id)

    def get_employment_verification_status(
        self, individual_id: int, request_id: int
    ) -> Dict[str, Any]:
        """Get employment verification status for an individual."""
        return self.status.get_employment_verification_status(individual_id, request_id)

    def get_professional_reference_check_status(
        self, individual_id: int, request_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get professional reference check status for an individual."""
        return self.status.get_professional_reference_check_status(
            individual_id, request_id
        )
