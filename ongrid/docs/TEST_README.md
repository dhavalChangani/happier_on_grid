# OnGrid Verification Testing

## Overview
This test suite demonstrates how to test OnGrid document verification using the test patterns defined in `VERIFICATION_TESTING.md`.

## Files
- `test_verification.py` - Test script with example scenarios
- `VERIFICATION_TESTING.md` - Quick reference guide for test patterns
- `Testing.md` - Complete testing documentation from OnGrid

## Prerequisites
1. Valid OnGrid credentials in `.env` file:
   ```
   ONGRID_CLIENT_ID=your-client-id
   ONGRID_CLIENT_SECRET=your-client-secret
   ONGRID_COMMUNITY_ID=your-community-id
   ONGRID_BASE_URL=https://api-staging.ongrid.in
   ```

2. **Important:** Testing only works in **STAGING environment**

3. Document files for upload (PAN cards, etc.)

## Running Tests

### Basic Execution
```bash
./venv/bin/python test_verification.py
```

### Test Scenarios Included

#### 1. PAN Verification - Success
- Pattern: `CMP::VER::Name`
- Expected: Verification completes with "Verified" result

#### 2. PAN Verification - Invalid
- Pattern: `CMP::INV::Name`
- Expected: Verification completes with "Invalid" result

#### 3. PAN Verification - Insufficiency
- Pattern: `INSUF::132::15::Name`
- Expected: Verification raises insufficiency with IDs 132 and 15

#### 4. Address Verification
- Pattern: `CMP::VER::Address`
- Note: Currently requires manual API testing (not fully automated)

## How Test Patterns Work

### Format
```
ACTION::RESULT::ActualValue
```

### Common Patterns

**For Success:**
```python
nameAsPerDocument = "CMP::VER::John Doe"
```

**For Failure:**
```python
nameAsPerDocument = "CMP::INV::John Doe"
```

**For Insufficiency:**
```python
nameAsPerDocument = "INSUF::132::15::John Doe"
```

### Delimiters
Use any of these delimiters:
- `::` (colons) - Recommended
- `..` (periods)
- `//` (slashes)
- `--` (dashes)
- `YY` (letter Y)

## Document Upload Requirements

The OnGrid API requires actual file uploads for document verification. You have options:

### Option 1: Use Real Files
```python
response = client.add_pan_document(
    individual_id=individual_id,
    file_path="/path/to/actual/pan_card.pdf",
    document_uid="ABCDE1234F",
    name_as_per_document="CMP::VER::John Doe",
)
```

### Option 2: Use URL Upload
```python
response = client.add_pan_document(
    individual_id=individual_id,
    file_path="https://your-server.com/documents/pan.pdf",
    document_uid="ABCDE1234F",
    name_as_per_document="CMP::VER::John Doe",
)
```

### Option 3: Manual Testing via OnGrid Dashboard
1. Onboard candidate via script
2. Upload documents manually in OnGrid dashboard
3. Customize field values using test patterns
4. Request verification

## Verification Types Reference

| Verification | Field to Customize | Example Pattern |
|--------------|-------------------|-----------------|
| PANV | nameAsPerDocument | `CMP::VER::Name` |
| VIDV | nameAsPerDocument | `CMP::VER::Name` |
| DLV | nameAsPerDocument | `CMP::VER::Name` |
| LAV/LADV | currentAddress | `CMP::VER::Address` |
| PAV/PADV | fullAddress | `CMP::VER::Address` |
| EMPV | employerName | `CMP::SCS::Company` |
| EDUV | nameOfInstitute | `CMP::SCS::College` |
| BAV | ifscCode | `AKID0001234` |

## Result Codes

- `VER` - Verified
- `SCS` - Success
- `INV` - Invalid
- `FLD` - Failed
- `UTV` - UnableToVerify
- `SWE` - SuccessWithException
- `DNR` - DoesNotReside
- `NT` - NonTraceable

## Notes

1. **Staging Only:** Test patterns only work in staging environment
2. **Case Insensitive:** All patterns are case-insensitive
3. **Async Processing:** Verifications are processed asynchronously - check status after a delay
4. **Real Data:** While using test patterns, still provide realistic candidate information

## Example Workflow

```python
from ongrid import OnGridClient

# 1. Initialize client
client = OnGridClient(community_id="your-community-id")

# 2. Onboard candidate
candidate_data = {
    "name": "Test User",
    "email": "test@example.com",
    "phone": "9876543210",
    "gender": "M",
    "profession_id": 1,
    "city": "Mumbai",
    "has_consent": True,
}
response = client.onboard_candidate(candidate_data)
individual_id = response["data"]["id"]

# 3. Add document with test pattern
response = client.add_pan_document(
    individual_id=individual_id,
    file_path="/path/to/pan.pdf",
    document_uid="ABCDE1234F",
    name_as_per_document="CMP::VER::Test User",  # Test pattern
)
document_id = response["data"]["id"]

# 4. Request verification
response = client.request_pan_verification(
    individual_id=individual_id,
    document_id=document_id,
)
request_id = response["data"]["id"]

# 5. Check status (after some delay)
import time
time.sleep(5)
response = client.get_pan_verification_status(
    individual_id=individual_id,
    request_id=request_id,
)
print(f"Status: {response['data']['status']}")
print(f"Result: {response['data']['result']}")
```

## Troubleshooting

### Issue: File validation error
**Solution:** Ensure file path points to valid, accessible file

### Issue: Request stays in "created" state
**Solution:** Check that test pattern is correct and uses proper delimiter

### Issue: Test patterns not working
**Solution:** Verify you're using staging environment, not production

### Issue: Insufficiency IDs ignored
**Solution:** Use valid insufficiency IDs from OnGrid documentation

## Support
Refer to `Testing.md` for complete OnGrid testing documentation.
