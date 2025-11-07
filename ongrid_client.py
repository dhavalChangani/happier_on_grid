import re
import requests
import base64
import logging
import os

from typing import Dict, Any, List, Optional
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VerificationDocType(str, Enum):
    """OnGrid Verification Document Types"""
    PANV = "pan"  # PAN Verification
    EDUV = "edu"  # Education Verification
    EMPV = "emp"  # Employment Verification
    PRC = "prc"  # Professional Reference Check
    BAV = "ba"  # Bank Account Verification
    EHC = "ehc"  # Employment History Check Does not require documents

class Gender(str, Enum):
    """Gender options"""
    MALE = "M"
    FEMALE = "F"
    TRANSGENDER = "T"
    OTHER = "O"
    UNSPECIFIED = "U"

class FileDataType(str, Enum):
    """File data types for document uploads"""
    URL = "Url"
    BINARY = "Binary"
    BASE64 = "Base64"


class OnGridException(Exception):
    """Base exception for OnGrid operations"""
    pass


class ValidationException(OnGridException):
    """Validation error exception"""
    pass


class OnGridClient:
    """
    OnGrid Background Verification Client
    
    This class provides a simple interface to OnGrid's background verification APIs.
    It handles all the complexity of API calls, authentication, and error handling.
    
    Attributes:
        community_id (str): OnGrid Community ID
    """
    
    def __init__(
        self,
        community_id: str,
        enable_logging: bool = True
    ):
        self.client_id = os.getenv("ONGRID_CLIENT_ID", "your-client-id-here")
        self.client_secret = os.getenv("ONGRID_CLIENT_SECRET", "your-client-secret-here")
        self.community_id = community_id
        self.base_url = os.getenv("ONGRID_BASE_URL", "https://api-staging.ongrid.in")
        self.consent_text = os.getenv("ONGRID_CONSENT_TEXT", "I agree to background verification")

        if not self.community_id:
            raise OnGridException("Community ID is required")
        if not self.client_id or not self.client_secret:
            raise OnGridException("Client ID and Client Secret are required")
        if not self.base_url:
            raise OnGridException("Base URL is required")
        if not self.consent_text:
            raise OnGridException("Consent text is required")

        if not enable_logging:
            logger.setLevel(logging.WARNING)
        
        logger.info("OnGrid client initialized")
    
    def _validate_candidate_data(self, candidate_data: Dict[str, Any]) -> List[str]:
        """
        Validate candidate data and return list of validation errors.
        
        Args:
            candidate_data: Dictionary containing candidate information
            
        Returns:
            List of validation error messages (empty if no errors)
        """
        validation_errors = []
        
        # Extract fields
        name = candidate_data.get('name')
        profession_id = candidate_data.get('profession_id')
        gender = candidate_data.get('gender')
        city = candidate_data.get('city')
        phone = candidate_data.get('phone')
        has_consent = candidate_data.get('has_consent')
        consent_text = self.consent_text
        email = candidate_data.get('email')
        alternate_phone = candidate_data.get('alternate_phone')
        dob = candidate_data.get('dob')
        joining_date = candidate_data.get('joining_date')
        ln_code = candidate_data.get('ln_code')
        
        # Validate required fields
        required_fields = {
            'name': name,
            'profession_id': profession_id,
            'gender': gender,
            'city': city,
            'phone': phone,
            'consent_text': consent_text,
        }
        
        for field_name, field_value in required_fields.items():
            if not field_value:
                validation_errors.append(f"Required field '{field_name}' is missing or empty")
        
        # Validate has_consent
        if has_consent is None:
            validation_errors.append("Required field 'has_consent' is missing")
        elif not isinstance(has_consent, bool):
            validation_errors.append("Field 'has_consent' must be a boolean value (true/false)")
        
        # Validate gender if present
        if gender:
            valid_genders = [g.value for g in Gender]
            if gender not in valid_genders:
                validation_errors.append(
                    f"Invalid gender '{gender}'. Must be one of: {', '.join(valid_genders)}"
                )
        
        # Validate phone if present
        if phone:
            if not phone.strip():
                validation_errors.append("Phone number cannot be empty")
            else:
                cleaned_phone = phone.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
                if not cleaned_phone.isdigit():
                    validation_errors.append(f"Invalid phone number format: {phone}")
        
        # Validate email if provided
        if email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                validation_errors.append(f"Invalid email format: {email}")
        
        # Validate alternate phone if provided
        if alternate_phone:
            if not alternate_phone.strip():
                validation_errors.append("Alternate phone number cannot be empty")
            else:
                cleaned_alt_phone = alternate_phone.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
                if not cleaned_alt_phone.isdigit():
                    validation_errors.append(f"Invalid alternate phone number format: {alternate_phone}")
        
        # Validate date formats
        if dob:
            if not (re.match(r'^\d{4}-\d{2}-\d{2}$', dob) or re.match(r'^\d{4}$', dob)):
                validation_errors.append(
                    f"Invalid date of birth format: {dob}. Must be 'yyyy-MM-dd' or 'yyyy'"
                )
        
        if joining_date:
            if not (re.match(r'^\d{4}-\d{2}-\d{2}$', joining_date) or re.match(r'^\d{4}$', joining_date)):
                validation_errors.append(
                    f"Invalid joining date format: {joining_date}. Must be 'yyyy-MM-dd' or 'yyyy'"
                )
        
        # Validate language code if provided
        if ln_code and ln_code != "hi-IN":
            validation_errors.append("Only 'hi-IN' is supported for language code")
        
        return validation_errors
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        params: Optional[Dict] = None,
        is_multipart: bool = False
    ) -> Dict[str, Any]:
        """
        Make a configurable HTTP request to OnGrid API.
        
        Handles both JSON and multipart/form-data requests based on parameters.
        
        Args:
            method: HTTP method (POST, PUT, GET, etc.)
            endpoint: API endpoint path
            data: Request data (JSON body or form data)
            files: Dictionary of files to upload (triggers multipart mode)
            params: Query parameters
            is_multipart: Force multipart/form-data mode even without files
            
        Returns:
            API response as dictionary
            
        Raises:
            OnGridException: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        auth_str = f"{self.client_id}:{self.client_secret}"
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()
        
        if files or is_multipart:
            headers = {
                'Authorization': f'Basic {b64_auth_str}',
                'Accept': 'application/json'
            }
            request_kwargs = {
                'method': method,
                'url': url,
                'files': files,
                'data': data,
                'params': params,
                'headers': headers
            }
        else:
            headers = {
                'Authorization': f'Basic {b64_auth_str}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            request_kwargs = {
                'method': method,
                'url': url,
                'json': data,
                'params': params,
                'headers': headers
            }
        
        try:
            response = requests.request(**request_kwargs)
            
            if response.status_code >= 400:
                error_msg = f"OnGrid API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', error_msg)
                except:
                    error_msg = response.text or error_msg
                
                logger.error(f"API error: {error_msg}")
                raise OnGridException(error_msg)
            
            return response.json()
            
        except requests.exceptions.ConnectionError:
            raise OnGridException("Connection error - Cannot reach OnGrid API")
        except requests.exceptions.RequestException as e:
            raise OnGridException(f"Request failed: {str(e)}")

    def _build_form_data(self, required_fields: Dict[str, Any], optional_fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build form data dictionary from required and optional fields.
        
        Args:
            required_fields: Dictionary of required field name-value pairs
            optional_fields: Dictionary of optional field name-value pairs
            
        Returns:
            Dictionary with all non-None fields
        """
        form_data = required_fields.copy()
        
        for key, value in optional_fields.items():
            if value is not None:
                form_data[key] = value
                
        return form_data
    
    def _handle_api_exceptions(self, operation: str):
        """
        Context manager for handling API exceptions consistently.
        
        Args:
            operation: Name of the operation being performed (for error messages)
            
        Usage:
            with self._handle_api_exceptions("add document"):
                # API call code
        """
        from contextlib import contextmanager
        
        @contextmanager
        def exception_handler():
            try:
                yield
            except ValidationException as e:
                logger.error(f"Validation error: {e}")
                raise
            except OnGridException as e:
                logger.error(f"Failed to {operation}: {e}")
                raise
            except Exception as e:
                logger.exception(f"Unexpected error while {operation}: {e}")
                raise OnGridException(f"Failed to {operation}: {str(e)}")
        
        return exception_handler()
    
    def _prepare_file_upload(self, file_path: str, file_key: str = 'file') -> Dict[str, tuple]:
        """
        Prepare a single file for upload.
        
        Args:
            file_path: Path to the file
            file_key: Key to use in files dictionary
            
        Returns:
            Dictionary with file data ready for requests
        """
        return {
            file_key: (os.path.basename(file_path), open(file_path, 'rb'), 'application/octet-stream')
        }
    
    def _prepare_multiple_files(self, file_paths: Dict[str, Optional[str]]) -> Dict[str, tuple]:
        """
        Prepare multiple files for upload.
        
        Args:
            file_paths: Dictionary mapping file keys to file paths (None values ignored)
            
        Returns:
            Dictionary with file data ready for requests
        """
        files = {}
        for key, path in file_paths.items():
            if path:
                files[key] = (
                    os.path.basename(path),
                    open(path, 'rb'),
                    'application/octet-stream'
                )
        return files
    
    def _close_files(self, files: Dict[str, tuple]) -> None:
        """
        Close all open file handles.
        
        Args:
            files: Dictionary of file tuples from _prepare_multiple_files
        """
        for file_tuple in files.values():
            file_tuple[1].close()

    # ========================================================================
    # MAIN INTEGRATION METHOD - This is what happierWork will primarily use
    # ========================================================================
    
    def onboard_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Onboard an individual in the OnGrid community.
        
        This API creates a record of a candidate at OnGrid and returns the unique individual ID.
        After onboarding, various verifications can be triggered against the individual.
        
        Args:
            candidate_data (dict): Dictionary containing candidate information with the following keys:
                
                Required fields:
                    - name (str): Individual's full name
                    - profession_id (str): ID of the individual's profession
                    - gender (str): Gender - M, F, T, O, or U
                    - city (str): City where the individual is working
                    - phone (str): Mobile number of the individual
                    - has_consent (bool): Consent status
                
                Optional fields:
                    - phone_country_code (str): Country code (default: "91" for India)
                    - individual_id (int): Individual's ID for updates
                    - uid (str): Individual's UID
                    - email (str): Email of the individual
                    - dob (str): Date of birth (yyyy-MM-dd or yyyy format)
                    - other_profession (str): Designation if profession is 'Other'
                    - permanent_address (dict): Permanent address object
                    - current_address (str): Current address
                    - current_address_country (str): Current address country
                    - current_address_id (int): Current address ID
                    - employee_id (str): Employee ID at client's end
                    - other_identifiers (dict): Other identifiers (DL, PAN, Voter ID)
                    - l_current_address (str): Current address in local language
                    - ln_code (str): ISO language code (only 'hi-IN' supported)
                    - fathers_name (str): Father's name
                    - alternate_phone (str): Alternate mobile number
                    - alternate_phone_country_code (str): Country code for alternate phone
                    - joining_date (str): Date of joining (yyyy-MM-dd or yyyy format)
                    - tags (list): List of tag objects to apply
                    - deduplication_keys (list): Unique identifiers for deduplication
                    - uans (list): UAN numbers
        
        Example:
            ```python
            result = client.onboard_candidate({
                "name": "John Doe",
                "profession_id": "123",
                "gender": "M",
                "city": "Mumbai",
                "phone": "9876543210",
                "has_consent": True,
                "email": "john@example.com",
                "employee_id": "EMP001"
            })
            ```
        
        Returns:
            dict: Response containing:
                - id (int): Individual's unique ID at OnGrid
                - name (str): Individual's name
                - professionsId (str): Profession ID
                - gender (str): Gender
                - city (str): City
                - phone (str): Phone number
                - email (str): Email
                - employeeId (str): Employee ID
                - deduplicationKeys (list): Deduplication keys
                - ... other fields as per API response
        
        Raises:
            ValidationException: If required fields are missing or invalid
            OnGridException: If the API request fails
        """
        try:
            # Validate all candidate data at once
            validation_errors = self._validate_candidate_data(candidate_data)
            
            # If there are any validation errors, raise them all together
            if validation_errors:
                error_message = "Validation failed with the following errors:\n" + "\n".join(
                    f"  - {error}" for error in validation_errors
                )
                raise ValidationException(error_message)
            
            # Extract fields for payload building
            name = candidate_data.get('name')
            profession_id = candidate_data.get('profession_id')
            gender = candidate_data.get('gender')
            city = candidate_data.get('city')
            phone = candidate_data.get('phone')
            has_consent = candidate_data.get('has_consent')
            consent_text = self.consent_text
            email = candidate_data.get('email')
            
            # Build the request payload
            payload = {
                "name": name,
                "professionId": profession_id,
                "gender": gender,
                "city": city,
                "phone": phone,
                "phoneCountryCode": candidate_data.get('phone_country_code', "91"),
                "hasConsent": has_consent,
                "consentText": consent_text
            }
            
            # Add optional fields if present
            optional_field_mapping = {
                'individual_id': 'individualId',
                'uid': 'uid',
                'email': 'email',
                'dob': 'dob',
                'other_profession': 'otherProfession',
                'permanent_address': 'permanentAddress',
                'current_address': 'currentAddress',
                'current_address_country': 'currentAddressCountry',
                'current_address_id': 'currentAddressId',
                'employee_id': 'employeeId',
                'other_identifiers': 'otherIdentifiers',
                'l_current_address': 'lCurrentAddress',
                'ln_code': 'lnCode',
                'fathers_name': 'fathersName',
                'alternate_phone': 'alternatePhone',
                'alternate_phone_country_code': 'alternatePhoneCountryCode',
                'joining_date': 'joiningDate',
                'tags': 'tags',
                'deduplication_keys': 'deduplicationKeys',
                'uans': 'uans'
            }
            
            for python_key, api_key in optional_field_mapping.items():
                if python_key in candidate_data and candidate_data[python_key] is not None:
                    payload[api_key] = candidate_data[python_key]
            
            # Make API request
            logger.info(f"Onboarding individual: {name} (email: {email or 'N/A'})")
            endpoint = f"/app/v1/community/{self.community_id}/individuals"
            response = self._make_request('POST', endpoint, data=payload)
            
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
        verifications: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Onboard an individual and simultaneously initiate background verifications.
        
        This API serves the dual purpose of creating candidate records in OnGrid and 
        simultaneously initiating verifications. It returns a unique Individual ID specific 
        to the individual created within OnGrid, along with verification request IDs.
        
        The employeeId can be passed to maintain a mapping between your system and OnGrid.
        OnGrid uses deduplicationKeys to de-duplicate incoming requests. If an API call comes 
        with the individual ID field populated, that call will update the individual's information.
        
        Args:
            candidate_data (dict): Dictionary containing candidate information with the following keys:
                
                Required fields:
                    - name (str): Individual's full name
                    - profession_id (str): ID of the individual's profession
                    - gender (str): Gender - M, F, T, O, or U
                    - city (str): City where the individual is working
                    - phone (str): Mobile number of the individual
                    - has_consent (bool): Consent status (must be True)
                
                Optional fields:
                    - phone_country_code (str): Country code (default: "91" for India)
                    - individual_id (int): Individual's ID for updates
                    - uid (str): Individual's UID
                    - email (str): Email of the individual
                    - dob (str): Date of birth (yyyy-MM-dd or yyyy format)
                    - other_profession (str): Designation if profession is 'Other'
                    - permanent_address (dict): Permanent address object (see below)
                    - current_address (str): Current address string
                    - current_address_country (str): Current address country
                    - current_address_id (int): Current address ID
                    - employee_id (str): Employee ID at client's end
                    - l_current_address (str): Current address in local language
                    - ln_code (str): ISO language code (only 'hi-IN' supported)
                    - fathers_name (str): Father's name
                    - alternate_phone (str): Alternate mobile number
                    - alternate_phone_country_code (str): Country code for alternate phone
                    - tags (list): List of tag objects to apply
                    - deduplication_keys (list): Unique identifiers for deduplication
                    - uans (list): UAN numbers
            
            verifications (list, optional): List of verification objects. Each verification object should contain:
                - code (str): Verification code (LAV, PANV, EDUV, EMPV, PCC, etc.)
                - key (str): Unique identifier for this verification (for deduplication)
                - data (dict, optional): Additional data specific to the verification type
                
                For document-based verifications (EDUV, EMPV, PCC), include documents in data:
                    - documents (list): List of document objects with:
                        - documentType (str): ProfileImage, EducationalCertificates, SalarySlip, etc.
                        - fileDataType (str): Url, Binary, or Base64
                        - fileContent (str): File content as per fileDataType
                        - fileName (str): Name of the file
                
                For address verifications (LAV, LADV, LAPV, PAV, PADV, PAPV, CCRV), include:
                    - currentAddress (str): Address to verify (if not in candidate_data)
        
        Permanent Address Object Structure:
            - co (str): Care of
            - line1 (str): House number / line 1
            - line2 (str): Street / line 2
            - locality (str): Locality
            - landmark (str): Landmark
            - vtc (str): Village/Town/City
            - district (str): District
            - state (str): State
            - pincode (str): Pincode
            - fullAddress (str): Complete address (takes precedence)
            - lFullAddress (str): Full address in local language
            - lnCode (str): Language code (hi-IN)
            - country (str): Country code
        
        Example:
            ```python
            result = client.onboard_and_initiate_verifications(
                candidate_data={
                    "name": "John Doe",
                    "profession_id": "123",
                    "gender": "M",
                    "city": "Mumbai",
                    "phone": "9876543210",
                    "has_consent": True,
                    "email": "john@example.com",
                    "employee_id": "EMP001",
                    "current_address": "123 Main St, Mumbai, 400001",
                    "deduplication_keys": ["EMP001"]
                },
                verifications=[
                    {
                        "code": "PANV",
                        "key": "pan_verification_1",
                        "data": {
                            "panNumber": "ABCDE1234F"
                        }
                    },
                    {
                        "code": "LAV",
                        "key": "address_verification_1",
                        "data": {
                            "currentAddress": "123 Main St, Mumbai, 400001"
                        }
                    },
                    {
                        "code": "EDUV",
                        "key": "education_verification_1",
                        "data": {
                            "documents": [
                                {
                                    "documentType": "EducationalCertificates",
                                    "fileDataType": "Url",
                                    "fileContent": "https://example.com/degree.pdf",
                                    "fileName": "degree.pdf"
                                }
                            ]
                        }
                    }
                ]
            )
            ```
        
        Returns:
            dict: Response containing:
                - individual (dict): Individual's information including:
                    - id (int): Individual's unique ID at OnGrid
                    - name (str): Individual's name
                    - professionsId (str): Profession ID
                    - employeeId (str): Employee ID
                    - deduplicationKeys (list): Deduplication keys
                    - ... other fields
                - verifications (list): List of initiated verifications with:
                    - code (str): Verification code
                    - key (str): Your unique key
                    - requestId (int): OnGrid request ID for this verification
        
        Raises:
            ValidationException: If required fields are missing or invalid
            OnGridException: If the API request fails
        """
        try:
            # Validate all candidate data at once
            validation_errors = self._validate_candidate_data(candidate_data)
            
            # If there are any validation errors, raise them all together
            if validation_errors:
                error_message = "Validation failed with the following errors:\n" + "\n".join(
                    f"  - {error}" for error in validation_errors
                )
                raise ValidationException(error_message)
            
            # Extract fields for payload building
            name = candidate_data.get('name')
            profession_id = candidate_data.get('profession_id')
            gender = candidate_data.get('gender')
            city = candidate_data.get('city')
            phone = candidate_data.get('phone')
            has_consent = candidate_data.get('has_consent')
            consent_text = self.consent_text
            
            # Build the request payload
            payload = {
                "name": name,
                "professionId": profession_id,
                "gender": gender,
                "city": city,
                "phone": phone,
                "phoneCountryCode": candidate_data.get('phone_country_code', "91"),
                "hasConsent": has_consent,
                "consentText": consent_text
            }
            
            # Add optional fields if present
            optional_field_mapping = {
                'individual_id': 'individualId',
                'uid': 'uid',
                'email': 'email',
                'dob': 'dob',
                'other_profession': 'otherProfession',
                'permanent_address': 'permanentAddress',
                'current_address': 'currentAddress',
                'current_address_country': 'currentAddressCountry',
                'current_address_id': 'currentAddressId',
                'employee_id': 'employeeId',
                'l_current_address': 'lCurrentAddress',
                'ln_code': 'lnCode',
                'fathers_name': 'fathersName',
                'alternate_phone': 'alternatePhone',
                'alternate_phone_country_code': 'alternatePhoneCountryCode',
                'tags': 'tags',
                'deduplication_keys': 'deduplicationKeys',
                'uans': 'uans'
            }
            
            for key, api_key in optional_field_mapping.items():
                if key in candidate_data and candidate_data[key] is not None:
                    payload[api_key] = candidate_data[key]

            # Add verifications if provided
            if verifications:
                payload['verifications'] = verifications

            # Make API request to the /initiate endpoint
            logger.info(f"Onboarding and initiating verifications for: {name}")
            if verifications:
                verification_codes = [str(v.get('code', 'UNKNOWN')) for v in verifications]
                logger.info(f"Initiating verifications: {', '.join(verification_codes)}")

            endpoint = f"/app/v1/community/{self.community_id}/individuals/initiate"
            response = self._make_request('POST', endpoint, data=payload)

            individual_id = response.get('individual', {}).get('id')
            logger.info(f"Individual onboarded successfully: ID {individual_id}")

            if 'verifications' in response and response['verifications']:
                logger.info(f"Initiated {len(response['verifications'])} verification(s)")
                for verification in response['verifications']:
                    logger.info(
                        f"  - {verification.get('code')}: Request ID {verification.get('requestId')}"
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

    # ========================================================================
    # DOCUMENT API METHODS
    # ========================================================================
    
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
            doc_type: Document type (pan, voterid, drivinglicense, passport, etc.)
            file_path: Path to document file
            document_uid: Document unique identifier
            name_as_per_document: Name as per document
            additional_fields: Optional additional fields
            
        Returns:
            API response dictionary
            
        Raises:
            OnGridException: If request fails
        """
        with self._handle_api_exceptions("add document"):
            endpoint = f"/app/v1/individual/{individual_id}/doc/{doc_type}"
            
            with open(file_path, 'rb') as f:
                files = {
                    'file': (os.path.basename(file_path), f, 'application/octet-stream')
                }

                form_data = {}
                for key, value in body.items():
                    if value is not None:
                        form_data[key] = value

                response = self._make_request(
                    method='POST',
                    endpoint=endpoint,
                    files=files,
                    data=form_data
                )
            
            logger.info(f"Document of type '{doc_type}' added for individual ID {individual_id}")
            return response
    
    def add_pan_document(
        self,
        individual_id: int,
        file_path: str,
        document_uid: str,
        name_as_per_document: str,
        legal_guardian_name: Optional[str] = None,
        dob: Optional[str] = None
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
        """
        body = self._build_form_data(
            required_fields={
                'documentUID': document_uid,
                'nameAsPerDocument': name_as_per_document,
            },
            optional_fields={
                'legalGuardianName': legal_guardian_name,
                'dob': dob,
            }
        )

        return self.add_document(
            individual_id=individual_id,
            doc_type=VerificationDocType.PANV,
            file_path=file_path,
            body=body
        )

    def update_pan_document(
        self,
        individual_id: int,
        document_id: int,
        file_path: str,
        document_uid: str,
        name_as_per_document: str,
        legal_guardian_name: Optional[str] = None,
        dob: Optional[str] = None
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
            API response dictionary containing:
                - id: ID of the document
                - documentUID: Document unique identifier
                - nameAsPerDocument: Name as per document
                - files: List of files on the document with:
                    - fileType: File type (image, pdf)
                    - side: Side of document (Front, Back, Other)
                    - servingUrl: Serving URL for the file
                - legalGuardianName: Name of legal guardian
                - dob: Date of birth (yyyy-MM-dd)
                
        Raises:
            OnGridException: If request fails
            ValidationException: If validation fails
        """
        with self._handle_api_exceptions("update PAN document"):
            endpoint = f"/app/v1/individual/{individual_id}/doc/pan/{document_id}"
            
            body = self._build_form_data(
                required_fields={
                    'documentUID': document_uid,
                    'nameAsPerDocument': name_as_per_document,
                },
                optional_fields={
                    'legalGuardianName': legal_guardian_name,
                    'dob': dob,
                }
            )
            
            with open(file_path, 'rb') as f:
                files = {
                    'file': (os.path.basename(file_path), f, 'application/octet-stream')
                }
                
                response = self._make_request(
                    method='POST',
                    endpoint=endpoint,
                    files=files,
                    data=body
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
        document_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add an education document to individual record.
        
        Args:
            individual_id: Individual's unique ID at OnGrid
            file_path: Path to education document file
            level: Education level (NO_EDUCATION, LESS_THEN_FIFTH_STD, FIFTH_STD, 
                  EIGHT_STD, TENTH_STD, TWELFTH_STD, DIPLOMA, GRADUATE, 
                  PROFESSIONAL_COURSE, MASTERS, PHD, POST_DOC, 
                  POT_GRADUATE_DIPLOMA, OTHER, NA)
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
        valid_levels = [
            "NO_EDUCATION", "LESS_THEN_FIFTH_STD", "FIFTH_STD", "EIGHT_STD",
            "TENTH_STD", "TWELFTH_STD", "DIPLOMA", "GRADUATE",
            "PROFESSIONAL_COURSE", "MASTERS", "PHD", "POST_DOC",
            "POT_GRADUATE_DIPLOMA", "OTHER", "NA"
        ]
        
        if level not in valid_levels:
            raise ValidationException(
                f"level must be one of: {', '.join(valid_levels)}"
            )
        
        body = self._build_form_data(
            required_fields={
                'level': level,
                'nameOfInstitute': name_of_institute,
                'degree': degree,
                'nameAsPerDocument': name_as_per_document,
                'registrationNumber': registration_number,
            },
            optional_fields={
                'yearOfPassing': str(year_of_passing) if year_of_passing is not None else None,
                'fieldOfStudy': field_of_study,
                'durationInMonths': str(duration_in_months) if duration_in_months is not None else None,
                'grade': grade,
                'nameOfBoardUniversity': name_of_board_university,
                'issueDate': issue_date,
                'documentId': document_id,
            }
        )
        
        return self.add_document(
            individual_id=individual_id,
            doc_type=VerificationDocType.EDUV,
            file_path=file_path,
            body=body
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
        hr_phone_country_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add an employment record to individual record.
        
        Args:
            individual_id: Individual's unique ID at OnGrid
            name_as_per_employer_records: Name as per employer records
            employer_name: Employer name
            employment_record_id: ID of employment record to update (None for new record)
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
        with self._handle_api_exceptions("add employment record"):
            endpoint = f"/app/v1/individual/{individual_id}/doc/emprecord"
            
            form_data = self._build_form_data(
                required_fields={
                    'nameAsPerEmployerRecords': name_as_per_employer_records,
                    'employerName': employer_name,
                },
                optional_fields={
                    'employmentRecordId': str(employment_record_id) if employment_record_id is not None else None,
                    'employeeId': employee_id,
                    'lastDesignation': last_designation,
                    'jobDescription': job_description,
                    'lastWorkingCity': last_working_city,
                    'joiningDate': joining_date,
                    'lastWorkingDate': last_working_date,
                    'annualCompensation': str(annual_compensation) if annual_compensation is not None else None,
                    'managerName': manager_name,
                    'managerEmail': manager_email,
                    'managerPhone': manager_phone,
                    'managerPhoneCountryCode': manager_phone_country_code,
                    'hrName': hr_name,
                    'hrEmail': hr_email,
                    'hrPhone': hr_phone,
                    'hrPhoneCountryCode': hr_phone_country_code,
                }
            )
            
            files = self._prepare_multiple_files({
                'salaryslip': salaryslip_path,
                'appointmentletter': appointmentletter_path,
                'experienceletter': experienceletter_path,
            })
            
            try:
                response = self._make_request(
                    method='POST',
                    endpoint=endpoint,
                    files=files if files else None,
                    data=form_data
                )
                logger.info(f"Employment record added for individual ID {individual_id}")
                return response
            finally:
                self._close_files(files)

    # ========================================================================
    # REQUEST VERIFICATION API METHODS
    # ========================================================================
    
    def request_pan_verification(
        self,
        individual_id: int,
        document_id: int
    ) -> Dict[str, Any]:
        """
        Request PAN verification for an individual.
        
        This API submits a request for PAN verification using a previously
        uploaded PAN document.
        
        Args:
            individual_id: Individual's unique ID at OnGrid
            document_id: ID of the PAN document to verify
            
        Returns:
            API response dictionary containing:
                - requestId: Verification request ID
                - document: PAN document details
                - state: Verification state (Requested, DataInsufficient, Deleted, 
                        Completed, Closed)
                - report: Verification report (if available)
                - closedReason: Reason for closure (if closed)
                - closedRemarks: Closure remarks (if closed)
                - created: Timestamp of request creation
                - dataSufficiencyDate: Timestamp of data sufficiency
                - completedDate: Timestamp of completion
                - closedDate: Timestamp of closure
            
        Raises:
            OnGridException: If request fails
            ValidationException: If validation fails
        """
        with self._handle_api_exceptions("request PAN verification"):
            endpoint = f"/app/v1/individual/{individual_id}/panv"
            
            payload = {"documentId": document_id}
            
            response = self._make_request(
                method="POST",
                endpoint=endpoint,
                data=payload
            )
            
            logger.info(
                f"PAN verification requested for individual ID {individual_id}, "
                f"document ID {document_id}, request ID: {response.get('requestId')}"
            )
            return response

    def request_education_verification(
        self,
        individual_id: int,
        education_document_id: int
    ) -> Dict[str, Any]:
        """
        Request education verification for an individual.
        
        This API submits a request for education verification using a previously
        uploaded education document.
        
        Args:
            individual_id: Individual's unique ID at OnGrid
            education_document_id: ID of the education document to verify
            
        Returns:
            API response dictionary containing:
                - requestId: Verification request ID
                - state: Verification state (Requested, DataInsufficient, Deleted,
                        Completed, Closed)
                - educationDetailDocument: Education document details including:
                    - id: Document ID
                    - nameAsPerDocument: Name as per document
                    - level: Education level (NO_EDUCATION, LESS_THEN_FIFTH_STD,
                            FIFTH_STD, EIGHT_STD, TENTH_STD, TWELFTH_STD, DIPLOMA,
                            GRADUATE, MASTERS, PHD, POST_DOC, POST_GRADUATE_DIPLOMA)
                    - registrationNumber: Registration number
                    - issueDate: Issue date
                    - nameOfInstitute: Institute name
                    - nameOfBoardUniversity: Board/University name
                    - yearOfPassing: Year of passing
                    - degree: Degree name
                    - fieldOfStudy: Field of study
                    - durationInMonths: Course duration
                    - grade: Grade obtained
                    - files: List of document files
                - eduvReport: Verification report (if available)
                - closedReason: Reason for closure (if closed)
            
        Raises:
            OnGridException: If request fails
            ValidationException: If validation fails
        """
        with self._handle_api_exceptions("request education verification"):
            endpoint = f"/app/v1/individual/{individual_id}/eduv"
            
            payload = {"educationDocumentId": education_document_id}
            
            response = self._make_request(
                method="POST",
                endpoint=endpoint,
                data=payload
            )
            
            logger.info(
                f"Education verification requested for individual ID {individual_id}, "
                f"education document ID {education_document_id}, "
                f"request ID: {response.get('requestId')}"
            )
            return response

    def request_employment_verification(
        self,
        individual_id: int,
        employment_record_id: int
    ) -> Dict[str, Any]:
        """
        Request employment verification for an individual.
        
        This API submits a request for employment verification and returns the
        details of the individual and employment record on which verification
        will be done.
        
        Args:
            individual_id: Individual's unique ID at OnGrid
            employment_record_id: ID of the employment record to verify
            
        Returns:
            API response dictionary containing:
                - requestId: Verification request ID
                - state: Verification state (Requested, DataInsufficient, Deleted,
                        Completed, Closed)
                - employmentRecord: Employment record details including:
                    - id: Employment record ID
                    - individualId: Individual ID
                    - nameAsPerEmployerRecords: Name as per employer records
                    - employeeId: Employee ID
                    - employerName: Employer name
                    - lastDesignation: Last designation
                    - jobDescription: Job description
                    - lastWorkingCity: Last working city
                    - joiningDate: Joining date (yyyy-MM-dd)
                    - lastWorkingDate: Last working date (yyyy-MM-dd)
                    - annualCompensation: Annual compensation
                    - managerName: Manager name
                    - managerEmail: Manager email
                    - managerPhone: Manager phone
                    - managerPhoneCountryCode: Manager phone country code
                    - hrName: HR name
                    - hrEmail: HR email
                    - hrPhone: HR phone
                    - hrPhoneCountryCode: HR phone country code
                    - currentEmployment: Whether currently employed
                    - documents: Employment documents
                - empvReport: Verification report (if available) including:
                    - employmentStatus: Working, Left, Probation, Absconding,
                                      Terminated, ServingNoticePeriod, Unknown, NA
                    - fnfStatus: Complete, Pending, NA
                    - result: Success, SuccessWithException, Failed, UnableToVerify
                - closedReason: Reason for closure (if closed)
                - closedRemarks: Closure remarks (if closed)
                - created: Timestamp of request creation
                - dataSufficiencyDate: Timestamp of data sufficiency
                - completedDate: Timestamp of completion
                - closedDate: Timestamp of closure
            
        Raises:
            OnGridException: If request fails
            ValidationException: If validation fails
        """
        with self._handle_api_exceptions("request employment verification"):
            endpoint = f"/app/v1/individual/{individual_id}/empv"
            
            payload = {"employmentRecordId": employment_record_id}
            
            response = self._make_request(
                method="POST",
                endpoint=endpoint,
                data=payload
            )
            
            logger.info(
                f"Employment verification requested for individual ID {individual_id}, "
                f"employment record ID {employment_record_id}, "
                f"request ID: {response.get('requestId')}"
            )
            return response

    def request_employment_history_check(
        self,
        individual_id: int,
        uans: List[str]
    ) -> Dict[str, Any]:
        """
        Request employment history check for an individual.
        
        This API submits a request for employment history check using UAN
        (Universal Account Number) from EPFO records.
        
        Args:
            individual_id: Individual's unique ID at OnGrid
            uans: List of UAN numbers of the individual
            
        Returns:
            API response dictionary containing:
                - requestId: EHC request ID
                - state: Verification state (Requested, DataInsufficient, Deleted,
                        Completed, Closed)
                - addressId: Address ID
                - ehcReport: Employment history check report (if available) including:
                    - uan: UAN(s) of individual
                    - candidateName: Name of candidate
                    - guardianName: Guardian name
                    - epfoRecordCount: Count of EPFO records
                    - source: Data source
                    - result: Success, Failed, UnableToVerify
                    - reason: Reason for result
                    - remarks: Additional remarks
                    - pdfServingUrl: URL to PDF report
                    - files: List of supporting documents
                - closedReason: Reason for closure (if closed)
                - closedRemarks: Closure remarks (if closed)
                - created: Timestamp of request creation
                - dataSufficiencyDate: Timestamp of data sufficiency
                - completedDate: Timestamp of completion
                - closedDate: Timestamp of closure
            
        Raises:
            OnGridException: If request fails
            ValidationException: If validation fails
        """
        with self._handle_api_exceptions("request employment history check"):
            endpoint = f"/app/v1/individual/{individual_id}/ehc"
            
            if not uans or not isinstance(uans, list):
                raise ValidationException("uans must be a non-empty list of UAN numbers")
            
            payload = {"uans": uans}
            
            response = self._make_request(
                method="POST",
                endpoint=endpoint,
                data=payload
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
        individual_designation: Optional[str] = None
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
            API response dictionary containing PRC request details
            
        Raises:
            OnGridException: If request fails
            ValidationException: If validation fails
        """
        with self._handle_api_exceptions("request PRC"):
            endpoint = f"/app/v1/individual/{individual_id}/prc"
            
            if reference_type not in ["Academic", "Professional"]:
                raise ValidationException(
                    "reference_type must be either 'Academic' or 'Professional'"
                )
            
            payload = self._build_form_data(
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
                }
            )
            
            response = self._make_request(
                method="POST",
                endpoint=endpoint,
                data=payload
            )
            
            logger.info(
                f"PRC requested for individual ID {individual_id}, "
                f"request ID: {response.get('requestId')}"
            )
            return response

    # ========================================================================
    # VERIFICATION STATUS API METHODS
    # ========================================================================
    
    def get_pan_verification_status(
        self,
        individual_id: int,
        request_id: int
    ) -> Dict[str, Any]:
        """
        Get PAN verification status for an individual.
        
        This API returns the status of PAN verification for the given request ID.
        
        Args:
            individual_id: Individual's unique ID at OnGrid
            request_id: ID of PANV request
            
        Returns:
            API response dictionary containing:
                - requestId: PANV request ID
                - document: PAN Document Model including:
                    - id: ID of the document
                    - documentUID: Document unique identifier
                    - nameAsPerDocument: Name as per document
                    - files: List of files on the document
                    - legalGuardianName: Name of legal Guardian
                    - dob: Date of birth (yyyy-MM-dd)
                    - state: Requested, DataInsufficient, Deleted, Completed, Closed
                    - report: PANV Report Response with:
                        - nameAsPerDocument: Name as per document
                        - dob: Date of birth
                        - legalGuardianName: Legal guardian name
                        - remarks: Remarks
                        - result: Verified, Invalid, InformationNotAvailable, 
                                UnableToVerify, SuccessWithException
                        - reason: Reason for result
                        - givenDocumentForVerification: Given document
                        - pdfServingUrl: PDF report URL
                        - gender: Gender
                        - phone: Phone number
                        - address: Address
                        - files: Supporting documents
                - closedReason: Reason for closure (if closed)
                - closedRemarks: Closure remarks (if closed)
                - created: Timestamp of created date
                - dataSufficiencyDate: Timestamp of data sufficiency date
                - completedDate: Timestamp of completion date
                - closedDate: Timestamp of closed date
            
        Raises:
            OnGridException: If request fails
            ValidationException: If validation fails
        """
        with self._handle_api_exceptions("get PAN verification status"):
            endpoint = f"/app/v1/individual/{individual_id}/panv"
            
            params = {"requestId": request_id}
            
            response = self._make_request(
                method="GET",
                endpoint=endpoint,
                params=params
            )
            
            logger.info(
                f"PAN verification status retrieved for individual ID {individual_id}, "
                f"request ID: {request_id}, state: {response.get('document', {}).get('state')}"
            )
            return response

    def get_education_verification_status(
        self,
        individual_id: int,
        request_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get education verification status for an individual.
        
        This API returns status of EDUV verification for the given request ID,
        or returns all the EDUV verification requests active for the individual
        for the community if request_id is not provided.
        
        Args:
            individual_id: Individual's unique ID at OnGrid
            request_id: ID of EDUV request (optional)
            
        Returns:
            API response dictionary containing:
                - requestId: EDUV request ID
                - state: Verification state (Requested, DataInsufficient, Deleted,
                        Completed, Closed)
                - educationDetailDocument: Education Detail Document including:
                    - id: Document ID
                    - nameAsPerDocument: Name as per document
                    - level: Education level (NO_EDUCATION, LESS_THEN_FIFTH_STD,
                            FIFTH_STD, EIGHT_STD, TENTH_STD, TWELFTH_STD, DIPLOMA,
                            GRADUATE, MASTERS, PHD, POST_DOC, POST_GRADUATE_DIPLOMA)
                    - registrationNumber: Registration number
                    - issueDate: Issue date
                    - nameOfInstitute: Name of institute
                    - nameOfBoardUniversity: Name of board/university
                    - yearOfPassing: Year of passing
                    - degree: Degree name
                    - fieldOfStudy: Field of study
                    - durationInMonths: Duration in months
                    - grade: Grade
                    - files: List of document files
                - eduvReport: EDUV Report Response with:
                    - registrationNumber: Registration number
                    - courseName: Course name
                    - fieldOfStudy: Field of study
                    - educationLevel: Education level
                    - durationInMonths: Duration in months
                    - yearOfPassing: Year of passing
                    - grade: Grade
                    - nameOfInstitute: Name of institute
                    - nameOfBoardUniversity: Name of board/university
                    - courseResult: Course result (Passed, Failed, DroppedOut)
                    - remarks: Remarks
                    - respondentName: Respondent name
                    - respondentDesignation: Respondent designation
                    - respondentEmail: Respondent email
                    - respondentPhone: Respondent phone
                    - receipt: Receipt document file
                    - result: Success, SuccessWithException, Failed
                    - givenDocumentForVerification: Given document
                    - files: Supporting documents
                    - pdfServingUrl: PDF report URL
                - closedReason: Reason for closure (if closed)
            
        Raises:
            OnGridException: If request fails
            ValidationException: If validation fails
        """
        with self._handle_api_exceptions("get education verification status"):
            endpoint = f"/app/v1/individual/{individual_id}/eduv"
            
            params = {}
            if request_id is not None:
                params["requestId"] = request_id
            
            response = self._make_request(
                method="GET",
                endpoint=endpoint,
                params=params if params else None
            )
            
            logger.info(
                f"Education verification status retrieved for individual ID {individual_id}"
                + (f", request ID: {request_id}" if request_id else " (all requests)")
                + (f", state: {response.get('state')}" if request_id else "")
            )
            return response

    def get_employment_verification_status(
        self,
        individual_id: int,
        request_id: int
    ) -> Dict[str, Any]:
        """
        Get employment verification status for an individual.
        
        This API returns status of Employment verification for the given request ID.
        
        Args:
            individual_id: Individual's unique ID at OnGrid
            request_id: ID of EMPV request
            
        Returns:
            API response dictionary containing:
                - requestId: EMPV request ID
                - state: Verification state (Requested, DataInsufficient, Deleted,
                        Completed, Closed)
                - employmentRecord: Employment Record DTO including:
                    - id: Unique ID for the employment record
                    - individualId: Individual ID
                    - nameAsPerEmployerRecords: Name as per employer records
                    - employeeId: Employee ID
                    - employerName: Employer name
                    - lastDesignation: Last designation
                    - jobDescription: Job description
                    - lastWorkingCity: Last working city
                    - joiningDate: Joining date (yyyy-MM-dd)
                    - lastWorkingDate: Last working date (yyyy-MM-dd)
                    - annualCompensation: Annual compensation
                    - managerName: Manager name
                    - managerEmail: Manager email
                    - managerPhone: Manager phone
                    - managerPhoneCountryCode: Manager phone country code
                    - hrName: HR name
                    - hrEmail: HR email
                    - hrPhone: HR phone
                    - hrPhoneCountryCode: HR phone country code
                    - currentEmployment: Current employment flag
                    - documents: EMP Document DTO
                - empvReport: EMPV Report Response with:
                    - nameAsPerEmployerRecords: Name as per employer records
                    - employeeId: Employee ID
                    - employerName: Employer name
                    - lastDesignation: Last designation
                    - lastWorkingCity: Last working city
                    - joiningDate: Joining date
                    - employmentStatus: Employment status (Working, Left, Probation,
                                      Absconding, Terminated, ServingNoticePeriod,
                                      Unknown, NA)
                    - lastWorkingDate: Last working date
                    - annualCompensation: Annual compensation
                    - fnfStatus: FnF status (Complete, Pending, NA)
                    - fnfPendingWithEmployee: FnF pending with employee flag
                    - performanceIssues: Performance issues
                    - integrityIssues: Integrity issues
                    - additionalRemarks: Additional remarks
                    - respondentName: Respondent name
                    - respondentDesignation: Respondent designation
                    - respondentEmail: Respondent email
                    - respondentPhone: Respondent phone
                    - givenEmploymentRecord: Given employment record
                    - result: Success, SuccessWithException, Failed, UnableToVerify
                    - reason: Reason for result
                    - receipt: Receipt document file
                    - files: Supporting documents
                    - pdfServingUrl: PDF report URL
                - closedReason: Reason for closure (if closed)
                - closedRemarks: Closure remarks (if closed)
                - created: Timestamp of created date
                - dataSufficiencyDate: Timestamp of data sufficiency date
                - completedDate: Timestamp of completed date
                - closedDate: Timestamp of closed date
            
        Raises:
            OnGridException: If request fails
            ValidationException: If validation fails
        """
        with self._handle_api_exceptions("get employment verification status"):
            endpoint = f"/app/v1/individual/{individual_id}/empv"
            
            params = {"requestId": request_id}
            
            response = self._make_request(
                method="GET",
                endpoint=endpoint,
                params=params
            )
            
            logger.info(
                f"Employment verification status retrieved for individual ID {individual_id}, "
                f"request ID: {request_id}, state: {response.get('state')}"
            )
            return response

    def get_professional_reference_check_status(
        self,
        individual_id: int,
        request_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get professional reference check status for an individual.
        
        This API returns status of PRC verification for the given request ID,
        or returns all the PRC verification requests for the individual for
        the community if request_id is not provided.
        
        Args:
            individual_id: Individual's unique ID at OnGrid
            request_id: ID of PRC request (optional)
            
        Returns:
            API response dictionary containing:
                - requestId: PRC request ID
                - state: Verification state (Requested, DataInsufficient, Deleted,
                        Completed, Closed)
                - referenceProvider: Reference Provider Details including:
                    - id: Reference provider ID
                    - name: Reference provider name
                    - phone: Phone number
                    - phoneCountryCode: Phone country code
                    - email: Email address
                    - organization: Organization name
                    - designation: Designation
                - dataCollectionSchemaId: Data collection schema ID
                - prcReport: PRC Report Response with:
                    - reportDetails: Report details
                    - referenceDenied: Reference denied flag
                    - referenceDeniedReason: Reference denied reason
                    - otherDeniedReason: Other denied reason
                    - result: ReferenceProvided, ReferenceDenied, UnableToVerify,
                             SuccessWithException
                    - remarks: Remarks
                    - pdfServingUrl: PDF report URL
                    - files: Supporting documents
                - closedReason: Reason for closure (if closed)
                - closedRemarks: Closure remarks (if closed)
                - created: Timestamp of created date
                - dataSufficiencyDate: Timestamp of data sufficiency date
                - completedDate: Timestamp of completion date
                - closedDate: Timestamp of closed date
            
        Raises:
            OnGridException: If request fails
            ValidationException: If validation fails
        """
        with self._handle_api_exceptions("get professional reference check status"):
            endpoint = f"/app/v1/individual/{individual_id}/prc"
            
            params = {}
            if request_id is not None:
                params["requestId"] = request_id
            
            response = self._make_request(
                method="GET",
                endpoint=endpoint,
                params=params if params else None
            )
            
            logger.info(
                f"Professional reference check status retrieved for individual ID {individual_id}"
                + (f", request ID: {request_id}" if request_id else " (all requests)")
                + (f", state: {response.get('state')}" if request_id else "")
            )
            return response

    # ========================================================================
  
