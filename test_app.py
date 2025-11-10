"""
Comprehensive test suite for OnGrid Flask API endpoints.

Tests cover all endpoints with various scenarios including:
- Valid requests
- Invalid data
- Missing fields
- Edge cases
- Error handling
"""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

from app import app


@pytest.fixture
def client():
    """
    Create test client for Flask app.
    
    Returns:
        Flask test client
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_ongrid_client():
    """
    Mock OnGridClient for testing without actual API calls.
    
    Returns:
        Mock OnGridClient instance
    """
    with patch('app.client') as mock:
        yield mock


class TestHomeEndpoint:
    """Tests for GET / endpoint."""
    
    def test_home_returns_success(self, client):
        """Test home endpoint returns 200 status."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_home_returns_json(self, client):
        """Test home endpoint returns JSON response."""
        response = client.get('/')
        assert response.content_type == 'application/json'
    
    def test_home_contains_message(self, client):
        """Test home endpoint contains welcome message."""
        response = client.get('/')
        data = json.loads(response.data)
        assert 'message' in data
        assert data['message'] == 'OnGrid Test API'
    
    def test_home_contains_endpoints_list(self, client):
        """Test home endpoint contains list of available endpoints."""
        response = client.get('/')
        data = json.loads(response.data)
        assert 'endpoints' in data
        assert isinstance(data['endpoints'], list)
        assert len(data['endpoints']) == 4


class TestOnboardEndpoint:
    """Tests for POST /onboard endpoint."""
    
    def test_onboard_with_valid_data(self, client, mock_ongrid_client):
        """Test onboarding with valid form data."""
        mock_ongrid_client.onboard_candidate.return_value = {
            "success": True,
            "data": {"individual_id": 12345}
        }
        
        response = client.post('/onboard', data={
            'name': 'John Doe',
            'profession_id': '1',
            'gender': 'M',
            'city': 'Mumbai',
            'phone': '9876543210',
            'has_consent': 'true',
            'consent_text': 'I agree to background verification'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
    
    def test_onboard_with_empty_body(self, client):
        """Test onboarding with empty request body."""
        response = client.post('/onboard', data={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_onboard_converts_boolean_consent_true(self, client, mock_ongrid_client):
        """Test has_consent conversion from string 'true' to boolean."""
        mock_ongrid_client.onboard_candidate.return_value = {"success": True}
        
        client.post('/onboard', data={
            'name': 'Test User',
            'has_consent': 'true',
            'profession_id': '1',
            'gender': 'M',
            'city': 'Delhi',
            'phone': '9876543210',
            'consent_text': 'I agree'
        })
        
        call_args = mock_ongrid_client.onboard_candidate.call_args[0][0]
        assert call_args['has_consent'] is True
    
    def test_onboard_converts_boolean_consent_false(self, client, mock_ongrid_client):
        """Test has_consent conversion from string 'false' to boolean."""
        mock_ongrid_client.onboard_candidate.return_value = {"success": True}
        
        client.post('/onboard', data={
            'name': 'Test User',
            'has_consent': 'false',
            'profession_id': '1',
            'gender': 'M',
            'city': 'Delhi',
            'phone': '9876543210',
            'consent_text': 'I agree'
        })
        
        call_args = mock_ongrid_client.onboard_candidate.call_args[0][0]
        assert call_args['has_consent'] is False
    
    def test_onboard_converts_boolean_consent_one(self, client, mock_ongrid_client):
        """Test has_consent conversion from '1' to boolean."""
        mock_ongrid_client.onboard_candidate.return_value = {"success": True}
        
        client.post('/onboard', data={
            'name': 'Test User',
            'has_consent': '1',
            'profession_id': '1',
            'gender': 'M',
            'city': 'Delhi',
            'phone': '9876543210',
            'consent_text': 'I agree'
        })
        
        call_args = mock_ongrid_client.onboard_candidate.call_args[0][0]
        assert call_args['has_consent'] is True
    
    def test_onboard_converts_boolean_consent_yes(self, client, mock_ongrid_client):
        """Test has_consent conversion from 'yes' to boolean."""
        mock_ongrid_client.onboard_candidate.return_value = {"success": True}
        
        client.post('/onboard', data={
            'name': 'Test User',
            'has_consent': 'yes',
            'profession_id': '1',
            'gender': 'M',
            'city': 'Delhi',
            'phone': '9876543210',
            'consent_text': 'I agree'
        })
        
        call_args = mock_ongrid_client.onboard_candidate.call_args[0][0]
        assert call_args['has_consent'] is True
    
    def test_onboard_parses_json_nested_objects(self, client, mock_ongrid_client):
        """Test parsing of JSON string for nested objects."""
        mock_ongrid_client.onboard_candidate.return_value = {"success": True}
        
        address = json.dumps({"street": "123 Main St", "city": "Mumbai"})
        
        client.post('/onboard', data={
            'name': 'Test User',
            'permanent_address': address,
            'profession_id': '1',
            'gender': 'M',
            'city': 'Mumbai',
            'phone': '9876543210',
            'has_consent': 'true',
            'consent_text': 'I agree'
        })
        
        call_args = mock_ongrid_client.onboard_candidate.call_args[0][0]
        assert isinstance(call_args['permanent_address'], dict)
        assert call_args['permanent_address']['city'] == 'Mumbai'
    
    def test_onboard_parses_json_arrays(self, client, mock_ongrid_client):
        """Test parsing of JSON string for array fields."""
        mock_ongrid_client.onboard_candidate.return_value = {"success": True}
        
        dedup_keys = json.dumps(["email", "phone"])
        
        client.post('/onboard', data={
            'name': 'Test User',
            'deduplication_keys': dedup_keys,
            'profession_id': '1',
            'gender': 'M',
            'city': 'Mumbai',
            'phone': '9876543210',
            'has_consent': 'true',
            'consent_text': 'I agree'
        })
        
        call_args = mock_ongrid_client.onboard_candidate.call_args[0][0]
        assert isinstance(call_args['deduplication_keys'], list)
        assert 'email' in call_args['deduplication_keys']
    
    def test_onboard_handles_exception(self, client, mock_ongrid_client):
        """Test error handling when client raises exception."""
        mock_ongrid_client.onboard_candidate.side_effect = Exception("API Error")
        
        response = client.post('/onboard', data={
            'name': 'Test User',
            'profession_id': '1',
            'gender': 'M',
            'city': 'Mumbai',
            'phone': '9876543210',
            'has_consent': 'true',
            'consent_text': 'I agree'
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'API Error'
    
    def test_onboard_with_all_optional_fields(self, client, mock_ongrid_client):
        """Test onboarding with all optional fields included."""
        mock_ongrid_client.onboard_candidate.return_value = {"success": True}
        
        response = client.post('/onboard', data={
            'name': 'John Doe',
            'email': 'john@example.com',
            'dob': '1990-01-01',
            'employee_id': 'EMP123',
            'phone_country_code': '+91',
            'profession_id': '1',
            'gender': 'M',
            'city': 'Mumbai',
            'phone': '9876543210',
            'has_consent': 'true',
            'consent_text': 'I agree to background verification'
        })
        
        assert response.status_code == 200


class TestOnboardAndInitiateEndpoint:
    """Tests for POST /onboard_and_initiate_verification endpoint."""
    
    def test_onboard_and_initiate_with_valid_data(self, client, mock_ongrid_client):
        """Test onboarding and initiating verification with valid data."""
        mock_ongrid_client.onboard_and_initiate_verifications.return_value = {
            "success": True,
            "data": {"individual_id": 12345, "verification_id": 67890}
        }
        
        response = client.post('/onboard_and_initiate_verification', data={
            'name': 'Jane Doe',
            'profession_id': '1',
            'gender': 'F',
            'city': 'Delhi',
            'phone': '9876543210',
            'has_consent': 'true',
            'consent_text': 'I agree to background verification'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_onboard_and_initiate_with_empty_body(self, client):
        """Test onboard and initiate with empty request body."""
        response = client.post('/onboard_and_initiate_verification', data={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_onboard_and_initiate_converts_boolean(self, client, mock_ongrid_client):
        """Test has_consent conversion to boolean."""
        mock_ongrid_client.onboard_and_initiate_verifications.return_value = {"success": True}
        
        client.post('/onboard_and_initiate_verification', data={
            'name': 'Test User',
            'has_consent': 'true',
            'profession_id': '1',
            'gender': 'M',
            'city': 'Delhi',
            'phone': '9876543210',
            'consent_text': 'I agree'
        })
        
        call_args = mock_ongrid_client.onboard_and_initiate_verifications.call_args[0][0]
        assert call_args['has_consent'] is True
    
    def test_onboard_and_initiate_handles_exception(self, client, mock_ongrid_client):
        """Test error handling when client raises exception."""
        mock_ongrid_client.onboard_and_initiate_verifications.side_effect = Exception("Verification Error")
        
        response = client.post('/onboard_and_initiate_verification', data={
            'name': 'Test User',
            'profession_id': '1',
            'gender': 'M',
            'city': 'Mumbai',
            'phone': '9876543210',
            'has_consent': 'true',
            'consent_text': 'I agree'
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Verification Error'


class TestCallbackEndpoint:
    """Tests for POST /callback endpoint."""
    
    def test_callback_with_valid_data(self, client):
        """Test callback endpoint with valid JSON data."""
        callback_data = {
            "event": "verification_completed",
            "individual_id": 12345,
            "status": "completed"
        }
        
        response = client.post(
            '/callback',
            data=json.dumps(callback_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'Callback received'
    
    def test_callback_with_empty_data(self, client):
        """Test callback endpoint with empty data."""
        response = client.post(
            '/callback',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
    
    def test_callback_with_null_data(self, client):
        """Test callback endpoint with null data."""
        response = client.post(
            '/callback',
            data=json.dumps(None),
            content_type='application/json'
        )
        
        assert response.status_code == 200
    
    def test_callback_logs_data(self, client, capsys):
        """Test callback endpoint logs received data."""
        callback_data = {"test": "data"}
        
        client.post(
            '/callback',
            data=json.dumps(callback_data),
            content_type='application/json'
        )
        
        # Note: In actual implementation, you'd want to use proper logging
        # and test with logging fixtures


class TestInsufficieniesEndpoint:
    """Tests for GET /insufficiencies endpoint."""
    
    def test_get_insufficiencies_without_params(self, client, mock_ongrid_client):
        """Test getting insufficiencies without query parameters."""
        mock_ongrid_client.get_insufficiencies.return_value = {
            "success": True,
            "data": {"insufficiencies": []}
        }
        
        response = client.get('/insufficiencies')
        
        assert response.status_code == 200
        mock_ongrid_client.get_insufficiencies.assert_called_once_with(
            individual_id=None,
            request_id=None,
            page_no=0,
            page_size=100
        )
    
    def test_get_insufficiencies_with_individual_id(self, client, mock_ongrid_client):
        """Test getting insufficiencies with individual_id parameter."""
        mock_ongrid_client.get_insufficiencies.return_value = {
            "success": True,
            "data": {"insufficiencies": [{"id": 1}]}
        }
        
        response = client.get('/insufficiencies?individual_id=12345')
        
        assert response.status_code == 200
        mock_ongrid_client.get_insufficiencies.assert_called_once_with(
            individual_id=12345,
            request_id=None,
            page_no=0,
            page_size=100
        )
    
    def test_get_insufficiencies_with_request_id(self, client, mock_ongrid_client):
        """Test getting insufficiencies with request_id parameter."""
        mock_ongrid_client.get_insufficiencies.return_value = {
            "success": True,
            "data": {}
        }
        
        response = client.get('/insufficiencies?request_id=67890')
        
        assert response.status_code == 200
        mock_ongrid_client.get_insufficiencies.assert_called_once_with(
            individual_id=None,
            request_id=67890,
            page_no=0,
            page_size=100
        )
    
    def test_get_insufficiencies_with_pagination(self, client, mock_ongrid_client):
        """Test getting insufficiencies with pagination parameters."""
        mock_ongrid_client.get_insufficiencies.return_value = {
            "success": True,
            "data": {}
        }
        
        response = client.get('/insufficiencies?page_no=2&page_size=50')
        
        assert response.status_code == 200
        mock_ongrid_client.get_insufficiencies.assert_called_once_with(
            individual_id=None,
            request_id=None,
            page_no=2,
            page_size=50
        )
    
    def test_get_insufficiencies_with_all_params(self, client, mock_ongrid_client):
        """Test getting insufficiencies with all query parameters."""
        mock_ongrid_client.get_insufficiencies.return_value = {
            "success": True,
            "data": {}
        }
        
        response = client.get(
            '/insufficiencies?individual_id=123&request_id=456&page_no=1&page_size=25'
        )
        
        assert response.status_code == 200
        mock_ongrid_client.get_insufficiencies.assert_called_once_with(
            individual_id=123,
            request_id=456,
            page_no=1,
            page_size=25
        )
    
    def test_get_insufficiencies_handles_exception(self, client, mock_ongrid_client):
        """Test error handling when client raises exception."""
        mock_ongrid_client.get_insufficiencies.side_effect = Exception("Database Error")
        
        response = client.get('/insufficiencies')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Database Error'
    
    def test_get_insufficiencies_default_pagination(self, client, mock_ongrid_client):
        """Test default pagination values are used."""
        mock_ongrid_client.get_insufficiencies.return_value = {"success": True}
        
        client.get('/insufficiencies')
        
        call_kwargs = mock_ongrid_client.get_insufficiencies.call_args[1]
        assert call_kwargs['page_no'] == 0
        assert call_kwargs['page_size'] == 100


class TestInsufficieniesResolveEndpoint:
    """Tests for POST /insufficiencies/resolve/<individual_id> endpoint."""
    
    def test_resolve_with_valid_data(self, client, mock_ongrid_client):
        """Test insufficiency resolution with valid data."""
        mock_ongrid_client.provide_insufficiency_resolution_data.return_value = {
            "success": True,
            "data": {"status": "submitted"}
        }
        
        resolution_data = {
            "insuffResolutionData": [
                {
                    "requestId": 123,
                    "data": {
                        "comments": "Updated details",
                        "textDataMap": {"field": "value"}
                    }
                }
            ]
        }
        
        response = client.post(
            '/insufficiencies/resolve/12345',
            data=json.dumps(resolution_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_resolve_without_insufficiency_data(self, client):
        """Test insufficiency resolution without required data."""
        response = client.post(
            '/insufficiencies/resolve/12345',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'insuffResolutionData is required' in data['error']
    
    def test_resolve_with_null_body(self, client):
        """Test insufficiency resolution with null body."""
        response = client.post(
            '/insufficiencies/resolve/12345',
            data=json.dumps(None),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_resolve_with_documents(self, client, mock_ongrid_client):
        """Test insufficiency resolution with document upload."""
        mock_ongrid_client.provide_insufficiency_resolution_data.return_value = {
            "success": True
        }
        
        resolution_data = {
            "insuffResolutionData": [
                {
                    "requestId": 123,
                    "data": {
                        "comments": "Updated PAN details",
                        "textDataMap": {
                            "pan number": "ABCDE1234F",
                            "pan name": "John Doe"
                        }
                    },
                    "documents": {
                        "documenType": "ProfileImage",
                        "fileDataType": "Url",
                        "fileContent": {},
                        "fileName": "pan_card.jpg"
                    }
                }
            ]
        }
        
        response = client.post(
            '/insufficiencies/resolve/12345',
            data=json.dumps(resolution_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        mock_ongrid_client.provide_insufficiency_resolution_data.assert_called_once_with(
            individual_id=12345,
            insufficiency_resolution_data=resolution_data['insuffResolutionData']
        )
    
    def test_resolve_with_multiple_resolutions(self, client, mock_ongrid_client):
        """Test insufficiency resolution with multiple items."""
        mock_ongrid_client.provide_insufficiency_resolution_data.return_value = {
            "success": True
        }
        
        resolution_data = {
            "insuffResolutionData": [
                {"requestId": 123, "data": {"comments": "First update"}},
                {"requestId": 456, "data": {"comments": "Second update"}},
                {"requestId": 789, "data": {"comments": "Third update"}}
            ]
        }
        
        response = client.post(
            '/insufficiencies/resolve/12345',
            data=json.dumps(resolution_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        call_args = mock_ongrid_client.provide_insufficiency_resolution_data.call_args
        assert len(call_args[1]['insufficiency_resolution_data']) == 3
    
    def test_resolve_handles_exception(self, client, mock_ongrid_client):
        """Test error handling when client raises exception."""
        mock_ongrid_client.provide_insufficiency_resolution_data.side_effect = Exception(
            "Upload Failed"
        )
        
        resolution_data = {
            "insuffResolutionData": [
                {"requestId": 123, "data": {"comments": "Test"}}
            ]
        }
        
        response = client.post(
            '/insufficiencies/resolve/12345',
            data=json.dumps(resolution_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Upload Failed'
    
    def test_resolve_with_zero_individual_id(self, client, mock_ongrid_client):
        """Test insufficiency resolution with individual_id of 0."""
        mock_ongrid_client.provide_insufficiency_resolution_data.return_value = {
            "success": True
        }
        
        resolution_data = {
            "insuffResolutionData": [
                {"requestId": 123, "data": {"comments": "Test"}}
            ]
        }
        
        response = client.post(
            '/insufficiencies/resolve/0',
            data=json.dumps(resolution_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        mock_ongrid_client.provide_insufficiency_resolution_data.assert_called_once_with(
            individual_id=0,
            insufficiency_resolution_data=resolution_data['insuffResolutionData']
        )


class TestErrorHandling:
    """Tests for general error handling and edge cases."""
    
    def test_invalid_method_on_get_endpoint(self, client):
        """Test POST request on GET-only endpoint returns 405."""
        response = client.post('/')
        assert response.status_code == 405
    
    def test_invalid_method_on_post_endpoint(self, client):
        """Test GET request on POST-only endpoint returns 405."""
        response = client.get('/onboard')
        assert response.status_code == 405
    
    def test_nonexistent_endpoint(self, client):
        """Test request to non-existent endpoint returns 404."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
    
    def test_insufficiency_resolve_with_non_numeric_id(self, client):
        """Test insufficiency resolution with non-numeric individual_id."""
        resolution_data = {
            "insuffResolutionData": [
                {"requestId": 123, "data": {"comments": "Test"}}
            ]
        }
        
        response = client.post(
            '/insufficiencies/resolve/abc',
            data=json.dumps(resolution_data),
            content_type='application/json'
        )
        
        # Flask route with <int:individual_id> will return 404 for non-numeric
        assert response.status_code == 404


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
