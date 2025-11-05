#!/bin/bash

# Sample API Test Scripts for OnGrid Flask API using Form Data

echo "=== OnGrid API Test Scripts (Form Data) ==="
echo ""

# Test 1: Basic onboarding with form data
echo "1. Testing basic onboarding with form data..."
curl -X POST http://localhost:5001/onboard \
  -F "name=John Doe" \
  -F "profession_id=123" \
  -F "gender=M" \
  -F "city=Mumbai" \
  -F "phone=9876543210" \
  -F "has_consent=true" \
  -F "consent_text=I agree to background verification"
echo -e "\n"

# Test 2: Onboarding with additional fields
echo "2. Testing onboarding with additional fields..."
curl -X POST http://localhost:5001/onboard \
  -F "name=Jane Smith" \
  -F "profession_id=456" \
  -F "gender=F" \
  -F "city=Delhi" \
  -F "phone=9876543211" \
  -F "has_consent=true" \
  -F "consent_text=I agree to background verification" \
  -F "phone_country_code=91" \
  -F "email=jane.smith@example.com" \
  -F "dob=1992-05-20" \
  -F "employee_id=EMP002" \
  -F "fathers_name=Robert Smith" \
  -F "alternate_phone=9876543212" \
  -F "joining_date=2024-01-15" \
  -F "current_address=123 Main St, Delhi"
echo -e "\n"

# Test 3: Onboarding with nested JSON in form data
echo "3. Testing onboarding with nested objects..."
curl -X POST http://localhost:5001/onboard \
  -F "name=Alice Johnson" \
  -F "profession_id=789" \
  -F "gender=F" \
  -F "city=Bangalore" \
  -F "phone=9876543213" \
  -F "has_consent=true" \
  -F "consent_text=I agree to background verification" \
  -F "email=alice@example.com" \
  -F "employee_id=EMP003" \
  -F 'permanent_address={"line1":"456 Elm St","city":"Bangalore","state":"Karnataka","pincode":"560001","country":"India"}' \
  -F 'deduplication_keys=["EMP003","alice@example.com"]'
echo -e "\n"

# Test 4: Validation errors with form data
echo "4. Testing validation errors with form data..."
curl -X POST http://localhost:5001/onboard \
  -F "name=" \
  -F "profession_id=" \
  -F "gender=X" \
  -F "city=" \
  -F "phone=abc123" \
  -F "has_consent=maybe" \
  -F "consent_text=" \
  -F "email=invalid-email"
echo -e "\n"

# Test 5: Missing required fields
echo "5. Testing missing required fields..."
curl -X POST http://localhost:5001/onboard \
  -F "name=Test User" \
  -F "email=test@example.com"
echo -e "\n"

echo "=== Tests completed ==="
