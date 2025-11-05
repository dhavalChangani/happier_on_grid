"""
Test script for the updated onboard_candidate function
"""

from ongrid_client import OnGridClient, ValidationException, OnGridException
import os

# Initialize client
client = OnGridClient(
    client_id=os.getenv("ONGRID_CLIENT_ID", "your-client-id"),
    client_secret=os.getenv("ONGRID_CLIENT_SECRET", "your-client-secret"),
    community_id=os.getenv("ONGRID_COMMUNITY_ID", "your-community-id"),
    base_url=os.getenv("ONGRID_BASE_URL", "https://api-staging.ongrid.in"),
)


def test_basic_onboarding():
    """Test basic onboarding with minimum required fields"""
    print("\n=== Test 1: Basic Onboarding ===")
    
    candidate_data = {
        "name": "John Doe",
        "profession_id": "123",
        "gender": "M",
        "city": "Mumbai",
        "phone": "9876543210",
        "has_consent": True,
        "consent_text": "I agree to background verification"
    }
    
    try:
        result = client.onboard_candidate(candidate_data)
        print(f"✅ Success! Individual ID: {result.get('id')}")
        print(f"Response: {result}")
    except ValidationException as e:
        print(f"❌ Validation Error:\n{e}")
    except OnGridException as e:
        print(f"❌ API Error: {e}")


def test_complete_onboarding():
    """Test onboarding with all optional fields"""
    print("\n=== Test 2: Complete Onboarding ===")
    
    candidate_data = {
        "name": "Jane Smith",
        "profession_id": "456",
        "gender": "F",
        "city": "Delhi",
        "phone": "9876543211",
        "has_consent": True,
        "consent_text": "I agree to background verification",
        "phone_country_code": "91",
        "email": "jane.smith@example.com",
        "dob": "1992-05-20",
        "employee_id": "EMP002",
        "fathers_name": "Robert Smith",
        "alternate_phone": "9876543212",
        "alternate_phone_country_code": "91",
        "joining_date": "2024-01-15",
        "current_address": "123 Main St, Delhi",
        "permanent_address": {
            "line1": "456 Elm St",
            "city": "Delhi",
            "state": "Delhi",
            "pincode": "110001",
            "country": "India"
        },
        "deduplication_keys": ["EMP002", "jane.smith@example.com"],
        "tags": [
            {"communityTagId": 1, "value": "Engineering"},
            {"communityTagId": 2, "value": "Full-time"}
        ]
    }
    
    try:
        result = client.onboard_candidate(candidate_data)
        print(f"✅ Success! Individual ID: {result.get('id')}")
        print(f"Response: {result}")
    except ValidationException as e:
        print(f"❌ Validation Error:\n{e}")
    except OnGridException as e:
        print(f"❌ API Error: {e}")


def test_validation_errors():
    """Test that all validation errors are shown at once"""
    print("\n=== Test 3: Multiple Validation Errors ===")
    
    # Intentionally invalid data with multiple errors
    candidate_data = {
        "name": "",  # Empty name
        "profession_id": "",  # Empty profession
        "gender": "X",  # Invalid gender
        "city": "",  # Empty city
        "phone": "abc123",  # Invalid phone
        "has_consent": "yes",  # Should be boolean
        "consent_text": "",  # Empty consent text
        "email": "invalid-email",  # Invalid email format
        "dob": "20-05-1992",  # Wrong date format
        "ln_code": "en-US"  # Unsupported language code
    }
    
    try:
        result = client.onboard_candidate(candidate_data)
        print(f"Unexpected success: {result}")
    except ValidationException as e:
        print(f"✅ Validation caught all errors:\n{e}")
    except OnGridException as e:
        print(f"❌ API Error: {e}")


def test_missing_required_fields():
    """Test with missing required fields"""
    print("\n=== Test 4: Missing Required Fields ===")
    
    candidate_data = {
        "name": "Test User",
        "email": "test@example.com"
        # Missing: profession_id, gender, city, phone, has_consent, consent_text
    }
    
    try:
        result = client.onboard_candidate(candidate_data)
        print(f"Unexpected success: {result}")
    except ValidationException as e:
        print(f"✅ Validation caught missing fields:\n{e}")
    except OnGridException as e:
        print(f"❌ API Error: {e}")


def test_partial_data():
    """Test with some optional fields"""
    print("\n=== Test 5: Partial Data ===")
    
    candidate_data = {
        "name": "Alice Johnson",
        "profession_id": "789",
        "gender": "F",
        "city": "Bangalore",
        "phone": "9876543213",
        "has_consent": True,
        "consent_text": "I consent to verification",
        "email": "alice@example.com",
        "employee_id": "EMP003"
    }
    
    try:
        result = client.onboard_candidate(candidate_data)
        print(f"✅ Success! Individual ID: {result.get('id')}")
        print(f"Email: {result.get('email')}")
        print(f"Employee ID: {result.get('employeeId')}")
    except ValidationException as e:
        print(f"❌ Validation Error:\n{e}")
    except OnGridException as e:
        print(f"❌ API Error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("OnGrid Client - Onboarding Tests")
    print("=" * 60)
    
    # Run validation tests (these don't require actual API calls)
    # test_validation_errors()
    # test_missing_required_fields()
    
    # Uncomment below to test actual API calls
    # Make sure you have valid credentials in environment variables
    test_basic_onboarding()
    # test_complete_onboarding()
    # test_partial_data()
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)
