"""Integration tests for Flask app endpoints"""

import json
import os
import pytest

from io import BytesIO
from unittest.mock import patch, MagicMock

from app import app


@pytest.fixture
def client():
    """
    Create Flask test client.

    Returns:
        Flask test client
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_ongrid_client():
    """
    Mock OnGrid client.

    Returns:
        MagicMock instance
    """
    with patch('app.client') as mock:
        yield mock


class TestHomeEndpoint:
    """Tests for home endpoint"""

    def test_home_returns_api_info(self, client):
        """Test home endpoint returns API information"""
        response = client.get('/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'endpoints' in data
        assert isinstance(data['endpoints'], list)
        assert len(data['endpoints']) > 0


class TestOnboardEndpoint:
    """Tests for candidate onboarding endpoint"""

    def test_onboard_success(self, client, mock_ongrid_client):
        """Test successful candidate onboarding"""
        mock_ongrid_client.onboard_candidate.return_value = {
            "success": True,
            "data": {"individualId": 123}
        }

        form_data = {
            'name': 'John Doe',
            'profession_id': '1',
            'gender': 'M',
            'city': 'Mumbai',
            'phone': '9876543210',
            'has_consent': 'true',
            'consent_text': 'I agree'
        }

        response = client.post('/onboard', data=form_data)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data

    def test_onboard_empty_data(self, client):
        """Test onboarding with empty data"""
        response = client.post('/onboard', data={})
        assert response.status_code == 400

    def test_onboard_exception(self, client, mock_ongrid_client):
        """Test onboarding with exception"""
        mock_ongrid_client.onboard_candidate.side_effect = Exception("API Error")

        form_data = {
            'name': 'John Doe',
            'profession_id': '1',
            'gender': 'M',
            'city': 'Mumbai',
            'phone': '9876543210'
        }

        response = client.post('/onboard', data=form_data)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestOnboardAndInitiateEndpoint:
    """Tests for onboard and initiate verification endpoint"""

    def test_onboard_and_initiate_success(self, client, mock_ongrid_client):
        """Test successful onboard and initiate verification"""
        mock_ongrid_client.onboard_and_initiate_verifications.return_value = {
            "success": True,
            "data": {"individualId": 123, "verifications": []}
        }

        form_data = {
            'name': 'Jane Doe',
            'profession_id': '2',
            'gender': 'F',
            'city': 'Delhi',
            'phone': '9876543211',
            'has_consent': 'true',
            'consent_text': 'I agree'
        }

        response = client.post('/onboard_and_initiate_verification', data=form_data)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True


class TestDocumentPANEndpoints:
    """Tests for PAN document endpoints"""

    def test_add_pan_document_success(self, client, mock_ongrid_client):
        """Test adding PAN document successfully"""
        mock_ongrid_client.add_pan_document.return_value = {
            "success": True,
            "data": {"documentId": 456}
        }

        data = {
            'document_uid': 'ABCDE1234F',
            'name_as_per_document': 'John Doe',
            'file': (BytesIO(b'fake pan content'), 'pan.pdf')
        }

        response = client.post('/documents/pan/add/123', 
                              data=data,
                              content_type='multipart/form-data')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    def test_add_pan_document_missing_file(self, client):
        """Test adding PAN document without file"""
        data = {
            'document_uid': 'ABCDE1234F',
            'name_as_per_document': 'John Doe'
        }

        response = client.post('/documents/pan/add/123', data=data)
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result

    def test_add_pan_document_missing_required_fields(self, client):
        """Test adding PAN document with missing required fields"""
        data = {
            'file': (BytesIO(b'fake pan content'), 'pan.pdf')
        }

        response = client.post('/documents/pan/add/123',
                              data=data,
                              content_type='multipart/form-data')
        assert response.status_code == 400

    def test_update_pan_document_success(self, client, mock_ongrid_client):
        """Test updating PAN document successfully"""
        mock_ongrid_client.update_pan_document.return_value = {
            "success": True,
            "data": {"documentId": 456}
        }

        data = {
            'document_uid': 'ABCDE1234F',
            'name_as_per_document': 'John Doe',
            'file': (BytesIO(b'fake pan content'), 'pan.pdf')
        }

        response = client.put('/documents/pan/update/123/456',
                             data=data,
                             content_type='multipart/form-data')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True


class TestDocumentEducationEndpoints:
    """Tests for education document endpoints"""

    def test_add_education_document_success(self, client, mock_ongrid_client):
        """Test adding education document successfully"""
        mock_ongrid_client.add_education_document.return_value = {
            "success": True,
            "data": {"documentId": 789}
        }

        data = {
            'level': 'Bachelor',
            'name_of_institute': 'XYZ University',
            'degree': 'B.Tech',
            'name_as_per_document': 'John Doe',
            'registration_number': '12345',
            'file': (BytesIO(b'fake edu content'), 'degree.pdf')
        }

        response = client.post('/documents/education/add/123',
                              data=data,
                              content_type='multipart/form-data')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    def test_add_education_document_missing_required_fields(self, client):
        """Test adding education document with missing required fields"""
        data = {
            'level': 'Bachelor',
            'file': (BytesIO(b'fake edu content'), 'degree.pdf')
        }

        response = client.post('/documents/education/add/123',
                              data=data,
                              content_type='multipart/form-data')
        assert response.status_code == 400


class TestEmploymentEndpoints:
    """Tests for employment record endpoints"""

    def test_add_employment_record_success(self, client, mock_ongrid_client):
        """Test adding employment record successfully"""
        mock_ongrid_client.add_employment_record.return_value = {
            "success": True,
            "data": {"employmentRecordId": 999}
        }

        data = {
            'name_as_per_employer_records': 'John Doe',
            'employer_name': 'ABC Corp'
        }

        response = client.post('/employment/add/123', data=data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    def test_add_employment_record_missing_required_fields(self, client):
        """Test adding employment record with missing required fields"""
        data = {'name_as_per_employer_records': 'John Doe'}

        response = client.post('/employment/add/123', data=data)
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result

    def test_add_employment_record_with_files(self, client, mock_ongrid_client):
        """Test adding employment record with document files"""
        mock_ongrid_client.add_employment_record.return_value = {
            "success": True,
            "data": {"employmentRecordId": 999}
        }

        data = {
            'name_as_per_employer_records': 'John Doe',
            'employer_name': 'ABC Corp',
            'salaryslip': (BytesIO(b'salary content'), 'salary.pdf'),
            'appointmentletter': (BytesIO(b'appointment content'), 'appointment.pdf')
        }

        response = client.post('/employment/add/123',
                              data=data,
                              content_type='multipart/form-data')
        assert response.status_code == 200


class TestVerificationEndpoints:
    """Tests for verification request endpoints"""

    def test_request_pan_verification(self, client, mock_ongrid_client):
        """Test requesting PAN verification"""
        mock_ongrid_client.request_pan_verification.return_value = {
            "success": True,
            "data": {"requestId": 111}
        }

        response = client.post('/verifications/pan/123/456')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    def test_request_education_verification(self, client, mock_ongrid_client):
        """Test requesting education verification"""
        mock_ongrid_client.request_education_verification.return_value = {
            "success": True,
            "data": {"requestId": 222}
        }

        response = client.post('/verifications/education/123/789')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    def test_request_employment_verification(self, client, mock_ongrid_client):
        """Test requesting employment verification"""
        mock_ongrid_client.request_employment_verification.return_value = {
            "success": True,
            "data": {"requestId": 333}
        }

        response = client.post('/verifications/employment/123/999')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    def test_request_employment_history_check(self, client, mock_ongrid_client):
        """Test requesting employment history check"""
        mock_ongrid_client.request_employment_history_check.return_value = {
            "success": True,
            "data": {"requestId": 444}
        }

        payload = {"uans": ["123456789012", "987654321098"]}
        response = client.post('/verifications/employment_history/123',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    def test_request_employment_history_check_missing_uans(self, client):
        """Test requesting employment history check without UANs"""
        response = client.post('/verifications/employment_history/123',
                              data=json.dumps({}),
                              content_type='application/json')
        assert response.status_code == 400

    def test_request_prc(self, client, mock_ongrid_client):
        """Test requesting professional reference check"""
        mock_ongrid_client.request_prc.return_value = {
            "success": True,
            "data": {"requestId": 555}
        }

        payload = {
            "schema_id": 1,
            "reference_provider_name": "Manager Name",
            "reference_provider_email": "manager@example.com",
            "organisation": "ABC Corp",
            "designation": "Manager",
            "reference_type": "professional",
            "reporting_manager": True
        }

        response = client.post('/verifications/prc/123',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    def test_request_prc_missing_required_fields(self, client):
        """Test requesting PRC with missing required fields"""
        payload = {"schema_id": 1}

        response = client.post('/verifications/prc/123',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result


class TestStatusEndpoints:
    """Tests for verification status endpoints"""

    def test_get_pan_verification_status(self, client, mock_ongrid_client):
        """Test getting PAN verification status"""
        mock_ongrid_client.get_pan_verification_status.return_value = {
            "success": True,
            "data": {"status": "Completed"}
        }

        response = client.get('/status/pan/123/111')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    def test_get_education_verification_status(self, client, mock_ongrid_client):
        """Test getting education verification status"""
        mock_ongrid_client.get_education_verification_status.return_value = {
            "success": True,
            "data": {"status": "InProgress"}
        }

        response = client.get('/status/education/123')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    def test_get_education_verification_status_with_request_id(self, client, mock_ongrid_client):
        """Test getting education verification status with request_id"""
        mock_ongrid_client.get_education_verification_status.return_value = {
            "success": True,
            "data": {"status": "Completed"}
        }

        response = client.get('/status/education/123?request_id=222')
        assert response.status_code == 200

    def test_get_employment_verification_status(self, client, mock_ongrid_client):
        """Test getting employment verification status"""
        mock_ongrid_client.get_employment_verification_status.return_value = {
            "success": True,
            "data": {"status": "Verified"}
        }

        response = client.get('/status/employment/123/333')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    def test_get_prc_status(self, client, mock_ongrid_client):
        """Test getting professional reference check status"""
        mock_ongrid_client.get_professional_reference_check_status.return_value = {
            "success": True,
            "data": {"status": "Completed"}
        }

        response = client.get('/status/prc/123')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True


class TestInsufficientEndpoints:
    """Tests for insufficiency endpoints"""

    def test_get_insufficiencies(self, client, mock_ongrid_client):
        """Test getting insufficiencies"""
        mock_ongrid_client.get_insufficiencies.return_value = {
            "success": True,
            "data": {"insufficiencies": []}
        }

        response = client.get('/insufficiencies')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    def test_get_insufficiencies_with_params(self, client, mock_ongrid_client):
        """Test getting insufficiencies with query parameters"""
        mock_ongrid_client.get_insufficiencies.return_value = {
            "success": True,
            "data": {"insufficiencies": []}
        }

        response = client.get('/insufficiencies?individual_id=123&page_no=0&page_size=50')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    def test_provide_insufficiency_resolution_data(self, client, mock_ongrid_client):
        """Test providing insufficiency resolution data"""
        mock_ongrid_client.provide_insufficiency_resolution_data.return_value = {
            "success": True,
            "data": []
        }

        payload = {
            "insuffResolutionData": [
                {
                    "requestId": 123,
                    "data": {
                        "comments": "Updated details",
                        "textDataMap": {"key": "value"}
                    }
                }
            ]
        }

        response = client.post('/insufficiencies/resolve/123',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    def test_provide_insufficiency_resolution_data_missing_data(self, client):
        """Test providing insufficiency resolution data without data"""
        response = client.post('/insufficiencies/resolve/123',
                              data=json.dumps({}),
                              content_type='application/json')
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result


class TestCallbackEndpoint:
    """Tests for callback endpoint"""

    def test_callback_success(self, client):
        """Test callback endpoint"""
        payload = {
            "activityType": "PANVCompleted",
            "individualId": 123,
            "requestId": 456,
            "status": "Verified"
        }

        response = client.post('/callback',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'Callback received'
