import re
import requests
import base64
import logging
import time

from typing import Dict, Any, List, Optional
from enum import Enum



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VerificationType(str, Enum):
    """Available verification types"""
    IDENTITY = "identity"
    ADDRESS = "address"
    EDUCATION = "education"
    EMPLOYMENT = "employment"
    CRIMINAL_RECORD = "criminal_record"
    CREDIT_CHECK = "credit_check"
    DRUG_TEST = "drug_test"
    REFERENCE_CHECK = "reference_check"


class VerificationStatus(str, Enum):
    """Verification status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Gender(str, Enum):
    """Gender options"""
    MALE = "M"
    FEMALE = "F"
    TRANSGENDER = "T"
    OTHER = "O"
    UNSPECIFIED = "U"


class DocumentType(str, Enum):
    """Document types"""
    PROFILE_IMAGE = "ProfileImage"
    POLICE_VERIFICATION = "PoliceVerification"
    ADDRESS_PROOF = "AddressProof"
    EDUCATIONAL_CERTIFICATES = "EducationalCertificates"
    RECOMMENDATION_LETTERS = "RecommendationLetters"
    SKILL_DOCUMENTS = "SkillDocuments"
    FINANCIAL_DOCUMENT = "FinancialDocument"
    VOTER_CARD = "VoterCard"
    PASSPORT = "Passport"
    DRIVING_LICENCE = "DrivingLicence"
    PAN_CARD = "PANCard"
    RATION_CARD = "RationCard"
    VEHICLE_REGISTRATION = "VehicleRegistration"
    CHARACTER_CERTIFICATE = "CharacterCertificate"
    BIRTH_CERTIFICATE = "BirthCertificate"
    OTHER = "Other"
    UTILITY_BILL = "UtilityBill"
    GAS_CONNECTION_DOCUMENT = "GasConnectionDocument"
    RENT_AGREEMENT = "RentAgreement"
    SALARY_SLIP = "SalarySlip"
    APPOINTMENT_LETTER = "AppointmentLetter"
    EXPERIENCE_LETTER = "ExperienceLetter"
    CUSTOM_DOCUMENT = "CustomDocument"


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
        api_key (str): OnGrid API key
        base_url (str): OnGrid API base URL
        timeout (int): Request timeout in seconds
    """
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        community_id: str,
        base_url: str,
        consent_text: str,
        timeout: int = 30,
        enable_logging: bool = True
    ):
        if not client_id or not client_secret or not community_id:
            raise OnGridException("Client ID, Client Secret, and Community ID are required")

        self.client_id = client_id
        self.client_secret = client_secret
        self.community_id = community_id
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.consent_text = consent_text

        if not enable_logging:
            logger.setLevel(logging.WARNING)
        
        logger.info("OnGrid client initialized")  
    
    def _get_headers(self) -> Dict[str, str]:
        print(f"Generating headers for request", self.client_id, self.client_secret)
        auth_str = f"{self.client_id}:{self.client_secret}"
        print(f"Auth string: {auth_str}")
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()
        print(f"Base64 Auth string: {b64_auth_str}")
        return {
            'Authorization': f'Basic {b64_auth_str}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
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
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            # Handle errors
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
            
        except requests.exceptions.Timeout:
            raise OnGridException("Request timeout - OnGrid API is not responding")
        except requests.exceptions.ConnectionError:
            raise OnGridException("Connection error - Cannot reach OnGrid API")
        except requests.exceptions.RequestException as e:
            raise OnGridException(f"Request failed: {str(e)}")
    
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
    
    # ========================================================================
    # INDIVIDUAL API METHODS - For advanced usage
    # ========================================================================
    
    def create_candidate(
        self,
        first_name: str,
        last_name: str,
        email: str,
        mobile: str,
        date_of_birth: str,
        address: Dict[str, str],
        reference_id: Optional[str] = None,
        gender: Optional[str] = None
    ) -> Dict[str, Any]:
        payload = {
            "candidate": {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "mobile": mobile,
                "date_of_birth": date_of_birth,
                "address": address,
                "reference_id": reference_id,
                "gender": gender
            }
        }
        
        response = self._make_request('POST', '/api/v1/candidates', data=payload)
        return response.get('data', response)
    
    def initiate_verification(
        self,
        candidate_id: str,
        verification_types: List[str],
        documents: Optional[List[Dict]] = None,
        package_id: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        payload = {
            "candidate_id": candidate_id,
            "verification_types": verification_types,
            "documents": documents or [],
            "package_id": package_id,
            "callback_url": callback_url
        }
        
        response = self._make_request('POST', '/api/v1/verifications', data=payload)
        return response.get('data', response)
    
    def get_verification_status(self, verification_id: str) -> Dict[str, Any]:
        response = self._make_request('GET', f'/api/v1/verifications/{verification_id}')
        return response.get('data', response)
    
    def get_verification_report(self, verification_id: str) -> Dict[str, Any]:
        response = self._make_request('GET', f'/api/v1/verifications/{verification_id}/report')
        return response.get('data', response)
    
    def cancel_verification(self, verification_id: str) -> Dict[str, Any]:
        response = self._make_request('POST', f'/api/v1/verifications/{verification_id}/cancel')
        return response.get('data', response)
    
    def get_candidate(self, candidate_id: str) -> Dict[str, Any]:
        response = self._make_request('GET', f'/api/v1/candidates/{candidate_id}')
        return response.get('data', response)
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def is_verification_complete(self, verification_id: str) -> bool:
        try:
            status = self.get_verification_status(verification_id)
            return status.get('overall_status') == 'completed'
        except OnGridException:
            return False
    
    def wait_for_completion(
        self,
        verification_id: str,
        poll_interval: int = 30,
        max_wait: int = 3600
    ) -> Dict[str, Any]:
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status = self.get_verification_status(verification_id)
            
            if status.get('overall_status') in ['completed', 'failed', 'cancelled']:
                return status
            
            logger.info(f"Verification in progress... {status.get('progress', 0)}%")
            time.sleep(poll_interval)
        
        raise OnGridException("Verification timeout - exceeded maximum wait time")