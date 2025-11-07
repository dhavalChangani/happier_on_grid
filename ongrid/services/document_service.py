"""Document management service"""

import logging
import os

from typing import Dict, Any, Optional, List

from ongrid.enums import VerificationDocType
from ongrid.exceptions import ValidationException
from ongrid.http_client import HttpClient
from ongrid import validators

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for managing document operations"""

    def __init__(self, http_client: HttpClient):
        """
        Initialize document service.

        Args:
            http_client: HTTP client instance
        """
        self.http = http_client

    def add_document(
        self,
        individual_id: int,
        doc_type: str,
        file_path: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Add a document to individual record.

        Args:
            individual_id: Individual's unique ID at OnGrid
            doc_type: Document type (pan, edu, emp, etc.)
            file_path: Path to document file
            body: Form data for document

        Returns:
            API response dictionary

        Raises:
            OnGridException: If request fails
        """
        with self.http.handle_api_exceptions("add document"):
            endpoint = f"/app/v1/individual/{individual_id}/doc/{doc_type}"

            with open(file_path, "rb") as f:
                files = {
                    "file": (
                        os.path.basename(file_path),
                        f,
                        "application/octet-stream",
                    )
                }

                form_data = {}
                for key, value in body.items():
                    if value is not None:
                        form_data[key] = value

                response = self.http.make_request(
                    method="POST", endpoint=endpoint, files=files, data=form_data
                )

            logger.info(
                f"Document of type '{doc_type}' added for individual ID {individual_id}"
            )
            return response

    def add_pan_document(
        self,
        individual_id: int,
        file_path: str,
        document_uid: str,
        name_as_per_document: str,
        legal_guardian_name: Optional[str] = None,
        dob: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Add a PAN document to individual record.

        Args:
            individual_id: Individual's unique ID at OnGrid
            file_path: Path to PAN document file
            document_uid: PAN document unique identifier
            name_as_per_document: Name as per PAN document
            legal_guardian_name: Legal guardian's name (if applicable)
            dob: Date of birth as per PAN document (yyyy-MM-dd or yyyy)

        Returns:
            API response dictionary

        Raises:
            ValidationException: If validation fails
        """
        validation_errors = []

        validation_errors.extend(
            validators.validate_positive_integer(individual_id, "individual_id")
        )
        validation_errors.extend(validators.validate_file_path(file_path))
        validation_errors.extend(validators.validate_pan_number(document_uid))
        validation_errors.extend(
            validators.validate_required_string(name_as_per_document, "name_as_per_document")
        )
        validation_errors.extend(
            validators.validate_optional_string(legal_guardian_name, "legal_guardian_name")
        )
        validation_errors.extend(validators.validate_date_format(dob, "dob"))

        if validation_errors:
            raise ValidationException(f"Validation failed: {'; '.join(validation_errors)}")

        body = self.http.build_form_data(
            required_fields={
                "documentUID": document_uid,
                "nameAsPerDocument": name_as_per_document,
            },
            optional_fields={
                "legalGuardianName": legal_guardian_name,
                "dob": dob,
            },
        )

        return self.add_document(
            individual_id=individual_id,
            doc_type=VerificationDocType.PANV,
            file_path=file_path,
            body=body,
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
        """
        Update an existing PAN document on an individual record.

        Args:
            individual_id: Individual's unique ID at OnGrid
            document_id: ID of the PAN document to update
            file_path: Path to PAN document file
            document_uid: PAN document unique identifier
            name_as_per_document: Name as per PAN document
            legal_guardian_name: Legal guardian's name (if applicable)
            dob: Date of birth as per PAN document (yyyy-MM-dd)

        Returns:
            API response dictionary

        Raises:
            OnGridException: If request fails
            ValidationException: If validation fails
        """
        validation_errors = []

        validation_errors.extend(
            validators.validate_positive_integer(individual_id, "individual_id")
        )
        validation_errors.extend(
            validators.validate_positive_integer(document_id, "document_id")
        )
        validation_errors.extend(validators.validate_file_path(file_path))
        validation_errors.extend(validators.validate_pan_number(document_uid))
        validation_errors.extend(
            validators.validate_required_string(name_as_per_document, "name_as_per_document")
        )
        validation_errors.extend(
            validators.validate_optional_string(legal_guardian_name, "legal_guardian_name")
        )
        validation_errors.extend(validators.validate_date_format(dob, "dob"))

        if validation_errors:
            raise ValidationException(f"Validation failed: {'; '.join(validation_errors)}")

        with self.http.handle_api_exceptions("update PAN document"):
            endpoint = f"/app/v1/individual/{individual_id}/doc/pan/{document_id}"

            body = self.http.build_form_data(
                required_fields={
                    "documentUID": document_uid,
                    "nameAsPerDocument": name_as_per_document,
                },
                optional_fields={
                    "legalGuardianName": legal_guardian_name,
                    "dob": dob,
                },
            )

            with open(file_path, "rb") as f:
                files = {
                    "file": (
                        os.path.basename(file_path),
                        f,
                        "application/octet-stream",
                    )
                }

                response = self.http.make_request(
                    method="POST", endpoint=endpoint, files=files, data=body
                )

            logger.info(
                f"PAN document updated for individual ID {individual_id}, "
                f"document ID {document_id}"
            )
            return response

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
        """
        Add an education document to individual record.

        Args:
            individual_id: Individual's unique ID at OnGrid
            file_path: Path to education document file
            level: Education level
            name_of_institute: Name of institute as per document
            degree: Degree acquired
            name_as_per_document: Name as per document
            registration_number: Registration number on document
            year_of_passing: Year of passing
            field_of_study: Field of study
            duration_in_months: Duration of course in months
            grade: Grade obtained
            name_of_board_university: Affiliated board or university name
            issue_date: Date of issue (yyyy-MM-dd)
            document_id: Document ID for updates (optional)

        Returns:
            API response dictionary

        Raises:
            OnGridException: If request fails
            ValidationException: If validation fails
        """
        validation_errors = []

        validation_errors.extend(
            validators.validate_positive_integer(individual_id, "individual_id")
        )
        validation_errors.extend(validators.validate_file_path(file_path))
        validation_errors.extend(validators.validate_education_level(level))
        validation_errors.extend(
            validators.validate_required_string(name_of_institute, "name_of_institute")
        )
        validation_errors.extend(
            validators.validate_required_string(degree, "degree")
        )
        validation_errors.extend(
            validators.validate_required_string(name_as_per_document, "name_as_per_document")
        )
        validation_errors.extend(
            validators.validate_required_string(registration_number, "registration_number")
        )
        validation_errors.extend(
            validators.validate_year(year_of_passing, "year_of_passing")
        )
        validation_errors.extend(
            validators.validate_optional_string(field_of_study, "field_of_study")
        )
        validation_errors.extend(
            validators.validate_positive_integer(duration_in_months, "duration_in_months")
        )
        validation_errors.extend(
            validators.validate_optional_string(grade, "grade")
        )
        validation_errors.extend(
            validators.validate_optional_string(name_of_board_university, "name_of_board_university")
        )
        validation_errors.extend(
            validators.validate_date_format(issue_date, "issue_date")
        )
        validation_errors.extend(
            validators.validate_optional_string(document_id, "document_id")
        )

        if validation_errors:
            raise ValidationException(f"Validation failed: {'; '.join(validation_errors)}")

        body = self.http.build_form_data(
            required_fields={
                "level": level,
                "nameOfInstitute": name_of_institute,
                "degree": degree,
                "nameAsPerDocument": name_as_per_document,
                "registrationNumber": registration_number,
            },
            optional_fields={
                "yearOfPassing": (
                    str(year_of_passing) if year_of_passing is not None else None
                ),
                "fieldOfStudy": field_of_study,
                "durationInMonths": (
                    str(duration_in_months) if duration_in_months is not None else None
                ),
                "grade": grade,
                "nameOfBoardUniversity": name_of_board_university,
                "issueDate": issue_date,
                "documentId": document_id,
            },
        )

        return self.add_document(
            individual_id=individual_id,
            doc_type=VerificationDocType.EDUV,
            file_path=file_path,
            body=body,
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
        """
        Add an employment record to individual record.

        Args:
            individual_id: Individual's unique ID at OnGrid
            name_as_per_employer_records: Name as per employer records
            employer_name: Employer name
            employment_record_id: ID of employment record to update
            employee_id: Employee ID
            last_designation: Last designation
            job_description: Job description
            last_working_city: Last working city
            joining_date: Joining date (yyyy-MM-dd)
            last_working_date: Last working date (yyyy-MM-dd)
            annual_compensation: Annual compensation
            salaryslip_path: Path to salary slip file
            appointmentletter_path: Path to appointment letter file
            experienceletter_path: Path to experience letter file
            manager_name: Manager name
            manager_email: Manager email
            manager_phone: Manager phone
            manager_phone_country_code: Manager phone country code
            hr_name: HR name
            hr_email: HR email
            hr_phone: HR phone
            hr_phone_country_code: HR phone country code

        Returns:
            API response dictionary

        Raises:
            OnGridException: If request fails
            ValidationException: If validation fails
        """
        validation_errors = []

        validation_errors.extend(
            validators.validate_positive_integer(individual_id, "individual_id")
        )
        validation_errors.extend(
            validators.validate_required_string(name_as_per_employer_records, "name_as_per_employer_records")
        )
        validation_errors.extend(
            validators.validate_required_string(employer_name, "employer_name")
        )
        validation_errors.extend(
            validators.validate_positive_integer(employment_record_id, "employment_record_id")
        )
        validation_errors.extend(
            validators.validate_optional_string(employee_id, "employee_id")
        )
        validation_errors.extend(
            validators.validate_optional_string(last_designation, "last_designation")
        )
        validation_errors.extend(
            validators.validate_optional_string(job_description, "job_description")
        )
        validation_errors.extend(
            validators.validate_optional_string(last_working_city, "last_working_city")
        )
        validation_errors.extend(
            validators.validate_date_format(joining_date, "joining_date")
        )
        validation_errors.extend(
            validators.validate_date_format(last_working_date, "last_working_date")
        )
        validation_errors.extend(
            validators.validate_positive_integer(annual_compensation, "annual_compensation")
        )

        if salaryslip_path:
            validation_errors.extend(validators.validate_file_path(salaryslip_path))
        if appointmentletter_path:
            validation_errors.extend(validators.validate_file_path(appointmentletter_path))
        if experienceletter_path:
            validation_errors.extend(validators.validate_file_path(experienceletter_path))

        validation_errors.extend(
            validators.validate_optional_string(manager_name, "manager_name")
        )
        validation_errors.extend(
            validators.validate_email(manager_email, "manager_email")
        )
        validation_errors.extend(
            validators.validate_phone_number(manager_phone, "manager_phone")
        )
        validation_errors.extend(
            validators.validate_optional_string(manager_phone_country_code, "manager_phone_country_code", max_length=5)
        )
        validation_errors.extend(
            validators.validate_optional_string(hr_name, "hr_name")
        )
        validation_errors.extend(
            validators.validate_email(hr_email, "hr_email")
        )
        validation_errors.extend(
            validators.validate_phone_number(hr_phone, "hr_phone")
        )
        validation_errors.extend(
            validators.validate_optional_string(hr_phone_country_code, "hr_phone_country_code", max_length=5)
        )

        if validation_errors:
            raise ValidationException(f"Validation failed: {'; '.join(validation_errors)}")

        with self.http.handle_api_exceptions("add employment record"):
            endpoint = f"/app/v1/individual/{individual_id}/doc/emprecord"

            form_data = self.http.build_form_data(
                required_fields={
                    "nameAsPerEmployerRecords": name_as_per_employer_records,
                    "employerName": employer_name,
                },
                optional_fields={
                    "employmentRecordId": (
                        str(employment_record_id)
                        if employment_record_id is not None
                        else None
                    ),
                    "employeeId": employee_id,
                    "lastDesignation": last_designation,
                    "jobDescription": job_description,
                    "lastWorkingCity": last_working_city,
                    "joiningDate": joining_date,
                    "lastWorkingDate": last_working_date,
                    "annualCompensation": (
                        str(annual_compensation)
                        if annual_compensation is not None
                        else None
                    ),
                    "managerName": manager_name,
                    "managerEmail": manager_email,
                    "managerPhone": manager_phone,
                    "managerPhoneCountryCode": manager_phone_country_code,
                    "hrName": hr_name,
                    "hrEmail": hr_email,
                    "hrPhone": hr_phone,
                    "hrPhoneCountryCode": hr_phone_country_code,
                },
            )

            files = self.http.prepare_multiple_files(
                {
                    "salaryslip": salaryslip_path,
                    "appointmentletter": appointmentletter_path,
                    "experienceletter": experienceletter_path,
                }
            )

            try:
                response = self.http.make_request(
                    method="POST",
                    endpoint=endpoint,
                    files=files if files else None,
                    data=form_data,
                )
                logger.info(
                    f"Employment record added for individual ID {individual_id}"
                )
                return response
            finally:
                self.http.close_files(files)
