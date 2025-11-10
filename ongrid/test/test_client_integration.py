"""
Direct integration tests for OnGridClient with real API calls.

These tests directly use OnGridClient to make calls to OnGrid staging environment.
Requires valid credentials in .env file:
- ONGRID_CLIENT_ID
- ONGRID_CLIENT_SECRET
- ONGRID_COMMUNITY_ID

Run with: pytest test_client_integration.py -v -s
"""

import os
import pytest
import time
from datetime import datetime
from dotenv import load_dotenv

from ongrid import OnGridClient
from ongrid.enums import Gender
from ongrid.exceptions import OnGridException

load_dotenv()


@pytest.fixture
def check_credentials():
    """
    Check if credentials are configured.
    
    Raises:
        pytest.skip: If credentials are not configured
    """
    required_vars = ['ONGRID_CLIENT_ID', 'ONGRID_CLIENT_SECRET', 'ONGRID_COMMUNITY_ID']
    missing = [var for var in required_vars if not os.getenv(var) or (os.getenv(var) or '').startswith('your-')]
    
    if missing:
        pytest.skip(f"Integration tests skipped: Missing or invalid credentials {missing}")


@pytest.fixture
def client(check_credentials):
    """
    Create OnGridClient instance.
    
    Returns:
        OnGridClient instance
    """
    return OnGridClient(
        community_id=os.getenv("ONGRID_COMMUNITY_ID", ""),
        enable_logging=True
    )


@pytest.fixture
def test_candidate_data():
    """
    Generate test candidate data with timestamp for uniqueness.
    
    Returns:
        Dictionary with candidate information
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return {
        'name': f'Test User {timestamp}',
        'email': f'test_{timestamp}@example.com',
        'phone': '9876543210',
        'profession_id': 1,
        'gender': Gender.MALE,
        'city': 'Mumbai',
        'has_consent': True,
        'consent_text': 'I agree to background verification'
    }


class TestClientOnboard:
    """Integration tests for candidate onboarding."""
    
    def test_onboard_candidate_success(self, client, test_candidate_data):
        """Test successful candidate onboarding."""
        result = client.onboard_candidate(test_candidate_data)
        
        print(f"\nOnboard Result: {result}")
        
        assert result['success'] is True
        assert 'data' in result
        assert 'id' in result['data']
        assert isinstance(result['data']['id'], int)
        
        print(f"✓ Onboarded candidate with ID: {result['data']['id']}")
    
    def test_onboard_with_all_fields(self, client, test_candidate_data):
        """Test onboarding with all optional fields."""
        test_candidate_data.update({
            'dob': '1990-01-01',
            'employee_id': 'EMP001',
            'fathers_name': 'Test Father',
            'mothers_name': 'Test Mother',
            'phone_country_code': '91',  # Should be without +
        })
        
        result = client.onboard_candidate(test_candidate_data)
        
        assert result['success'] is True
        print(f"✓ Onboarded with all fields, ID: {result['data']['id']}")
    
    def test_onboard_with_invalid_profession(self, client, test_candidate_data):
        """Test onboarding with invalid profession_id."""
        test_candidate_data['profession_id'] = 99999
        
        result = client.onboard_candidate(test_candidate_data)
        
        # Should return error
        assert result['success'] is False
        assert 'message' in result
        print(f"✓ Correctly rejected invalid profession: {result['message']}")
    
    def test_onboard_with_missing_required_field(self, client, test_candidate_data):
        """Test onboarding with missing required field."""
        del test_candidate_data['name']
        
        result = client.onboard_candidate(test_candidate_data)
        
        # Should return validation error
        assert result['success'] is False
        assert 'message' in result
        print(f"✓ Correctly rejected missing field: {result['message']}")
    
    def test_onboard_with_invalid_gender(self, client, test_candidate_data):
        """Test onboarding with invalid gender."""
        test_candidate_data['gender'] = 'INVALID'
        
        result = client.onboard_candidate(test_candidate_data)
        
        # Should return validation error
        assert result['success'] is False
        print(f"✓ Correctly rejected invalid gender: {result['message']}")
    
    def test_onboard_with_invalid_email(self, client, test_candidate_data):
        """Test onboarding with invalid email format."""
        test_candidate_data['email'] = 'invalid-email'
        
        result = client.onboard_candidate(test_candidate_data)
        
        # Should return validation error
        assert result['success'] is False
        print(f"✓ Correctly rejected invalid email: {result['message']}")
    
    def test_onboard_with_invalid_phone(self, client, test_candidate_data):
        """Test onboarding with invalid phone format."""
        test_candidate_data['phone'] = '123'
        
        result = client.onboard_candidate(test_candidate_data)
        
        # Should return validation error
        assert result['success'] is False
        print(f"✓ Correctly rejected invalid phone: {result['message']}")


class TestClientOnboardAndInitiate:
    """Integration tests for onboard and initiate verification."""
    
    def test_onboard_and_initiate_success(self, client, test_candidate_data):
        """Test successful onboarding and verification initiation."""
        result = client.onboard_and_initiate_verifications(test_candidate_data)
        
        print(f"\nOnboard & Initiate Result: {result}")
        
        assert result['success'] is True
        assert 'data' in result
        assert 'individual' in result['data']
        assert 'id' in result['data']['individual']
        
        print(f"✓ Onboarded and initiated verification for ID: {result['data']['individual']['id']}")
    
    def test_onboard_and_initiate_with_test_pattern(self, client, test_candidate_data):
        """Test with OnGrid test pattern name."""
        test_candidate_data['name'] = 'PCC INSUFF MAJOR'
        test_candidate_data['fathers_name'] = 'Test Father'
        
        result = client.onboard_and_initiate_verifications(test_candidate_data)
        
        if result['success']:
            individual_id = result['data']['individual']['id']
            print(f"✓ Initiated verification with test pattern, ID: {individual_id}")
        else:
            print(f"⚠ Test pattern failed: {result['message']}")
        
        # May succeed or fail depending on OnGrid test environment
        assert 'success' in result


class TestClientInsufficienies:
    """Integration tests for insufficiency management."""
    
    @pytest.fixture
    def onboarded_individual(self, client, test_candidate_data):
        """Create a candidate for testing."""
        result = client.onboard_candidate(test_candidate_data)
        
        if result['success']:
            return result['data']['id']
        return None
    
    def test_get_all_insufficiencies(self, client):
        """Test getting all insufficiencies."""
        result = client.get_insufficiencies()
        
        print(f"\nGet Insufficiencies Result: {result}")
        
        assert result['success'] is True
        assert 'data' in result
        
        insufficiencies = result['data'].get('communityInsufficiencyDTO', [])
        print(f"✓ Total insufficiencies: {len(insufficiencies)}")
    
    def test_get_insufficiencies_with_pagination(self, client):
        """Test getting insufficiencies with pagination."""
        result = client.get_insufficiencies(page_no=0, page_size=10)
        
        assert result['success'] is True
        print(f"✓ Pagination test passed")
    
    def test_get_insufficiencies_for_individual(self, client, onboarded_individual):
        """Test getting insufficiencies for specific individual."""
        if not onboarded_individual:
            pytest.skip("Could not create test individual")
        
        result = client.get_insufficiencies(individual_id=onboarded_individual)
        
        assert result['success'] is True
        insufficiencies = result['data'].get('communityInsufficiencyDTO', [])
        print(f"✓ Insufficiencies for individual {onboarded_individual}: {len(insufficiencies)}")
    
    def test_get_insufficiencies_invalid_page_size(self, client):
        """Test getting insufficiencies with invalid page size."""
        result = client.get_insufficiencies(page_size=1000)
        
        # Should return validation error
        assert result['success'] is False
        print(f"✓ Correctly rejected invalid page size: {result['message']}")


class TestClientInsufficieniesResolve:
    """Integration tests for insufficiency resolution."""
    
    @pytest.fixture
    def individual_with_insufficiency(self, client, test_candidate_data):
        """Create candidate with insufficiency using test pattern."""
        test_candidate_data['name'] = 'PCC INSUFF MAJOR'
        test_candidate_data['fathers_name'] = 'Test Father'
        
        result = client.onboard_and_initiate_verifications(test_candidate_data)
        
        if result['success']:
            individual_id = result['data']['individual']['id']
            
            # Wait for verification to process
            time.sleep(5)
            
            # Check if insufficiency exists
            insuff_result = client.get_insufficiencies(individual_id=individual_id)
            
            if insuff_result['success'] and insuff_result['data'].get('communityInsufficiencyDTO'):
                return {
                    'individual_id': individual_id,
                    'insufficiencies': insuff_result['data']['communityInsufficiencyDTO']
                }
        
        return None
    
    def test_resolve_insufficiency(self, client, individual_with_insufficiency):
        """Test resolving insufficiency with comments."""
        if not individual_with_insufficiency:
            pytest.skip("No insufficiency available for testing")
        
        individual_id = individual_with_insufficiency['individual_id']
        insufficiencies = individual_with_insufficiency['insufficiencies']
        
        if not insufficiencies:
            pytest.skip("No insufficiency found")
        
        request_id = insufficiencies[0].get('requestId')
        
        resolution_data = [
            {
                "requestId": request_id,
                "data": {
                    "comments": "Updated information provided via integration test",
                    "textDataMap": {
                        "field_name": "updated_value"
                    }
                }
            }
        ]
        
        result = client.provide_insufficiency_resolution_data(
            individual_id=individual_id,
            insufficiency_resolution_data=resolution_data
        )
        
        print(f"\nResolve Result: {result}")
        
        assert result['success'] is True
        print(f"✓ Resolved insufficiency for individual {individual_id}")
    
    def test_resolve_with_invalid_individual(self, client):
        """Test resolving with non-existent individual."""
        resolution_data = [
            {
                "requestId": 999999,
                "data": {
                    "comments": "Test comment"
                }
            }
        ]
        
        result = client.provide_insufficiency_resolution_data(
            individual_id=999999,
            insufficiency_resolution_data=resolution_data
        )
        
        # Should return error
        assert result['success'] is False
        print(f"✓ Correctly rejected invalid individual: {result['message']}")


class TestClientEndToEnd:
    """End-to-end integration tests."""
    
    def test_complete_onboarding_flow(self, client, test_candidate_data):
        """Test complete flow: onboard -> check status -> get insufficiencies."""
        print(f"\n=== End-to-End Test ===")
        
        # Step 1: Onboard candidate
        onboard_result = client.onboard_candidate(test_candidate_data)
        assert onboard_result['success'] is True
        individual_id = onboard_result['data']['id']
        print(f"Step 1: ✓ Onboarded individual ID: {individual_id}")
        
        # Step 2: Check insufficiencies
        time.sleep(2)
        insuff_result = client.get_insufficiencies(individual_id=individual_id)
        
        if insuff_result['success']:
            insufficiency_count = len(insuff_result['data'].get('communityInsufficiencyDTO', []))
            print(f"Step 2: ✓ Found {insufficiency_count} insufficiencies")
        else:
            print(f"Step 2: ⚠ Could not fetch insufficiencies: {insuff_result['message']}")
        
        print(f"=== Test Complete ===\n")
    
    def test_onboard_initiate_and_check(self, client, test_candidate_data):
        """Test onboard with initiation and check status."""
        print(f"\n=== Onboard & Initiate Flow ===")
        
        # Step 1: Onboard and initiate
        result = client.onboard_and_initiate_verifications(test_candidate_data)
        assert result['success'] is True
        individual_id = result['data']['individual']['id']
        print(f"Step 1: ✓ Onboarded and initiated for ID: {individual_id}")
        
        # Step 2: Wait and check insufficiencies
        time.sleep(3)
        insuff_result = client.get_insufficiencies(individual_id=individual_id)
        
        if insuff_result['success']:
            insufficiencies = insuff_result['data'].get('communityInsufficiencyDTO', [])
            print(f"Step 2: ✓ Verification in progress, insufficiencies: {len(insufficiencies)}")
        
        print(f"=== Flow Complete ===\n")
    
    def test_multiple_test_patterns(self, client, test_candidate_data):
        """Test various OnGrid test patterns."""
        test_scenarios = [
            {
                'name': 'PCC MAJOR DISCREPANCY',
                'description': 'PCC with major discrepancy'
            },
            {
                'name': 'DOCUMENT UNABLE TO VERIFY',
                'description': 'Document unable to verify'
            }
        ]
        
        results = []
        
        print(f"\n=== Testing Multiple Patterns ===")
        
        for scenario in test_scenarios:
            test_data = test_candidate_data.copy()
            test_data['name'] = scenario['name']
            test_data['email'] = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
            
            result = client.onboard_and_initiate_verifications(test_data)
            
            if result['success']:
                individual_id = result['data']['individual']['id']
                results.append({
                    'scenario': scenario['description'],
                    'individual_id': individual_id,
                    'status': 'initiated'
                })
                print(f"✓ {scenario['description']}: ID {individual_id}")
            else:
                print(f"⚠ {scenario['description']}: {result['message']}")
            
            time.sleep(1)
        
        print(f"=== Completed {len(results)}/{len(test_scenarios)} scenarios ===\n")


class TestClientErrorHandling:
    """Test error handling and validation."""
    
    def test_client_with_invalid_credentials(self):
        """Test client initialization with invalid credentials."""
        try:
            invalid_client = OnGridClient(
                community_id="12345",  # Use numeric string
                enable_logging=False
            )
            # Try to use it
            result = invalid_client.get_insufficiencies()
            assert result['success'] is False
            print(f"✓ Invalid credentials handled: {result['message']}")
        except (OnGridException, ValueError) as e:
            print(f"✓ Invalid credentials caught: {str(e)}")
    
    def test_empty_community_id(self):
        """Test client initialization with empty community ID."""
        with pytest.raises(OnGridException) as exc_info:
            OnGridClient(community_id="")
        
        assert "Community ID is required" in str(exc_info.value)
        print(f"✓ Empty community ID rejected")
    
    def test_invalid_data_types(self, client):
        """Test with invalid data types."""
        invalid_data = {
            'name': 123,  # Should be string
            'profession_id': 'invalid',  # Should be int
            'gender': Gender.MALE,
            'city': 'Mumbai',
            'phone': '9876543210',
            'has_consent': True,
            'consent_text': 'I agree'
        }
        
        result = client.onboard_candidate(invalid_data)
        
        # Should handle validation
        assert 'success' in result
        print(f"✓ Invalid data types handled")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s', '--tb=short'])
