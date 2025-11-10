# Test Suite Documentation

Comprehensive test suite for OnGrid Flask API endpoints.

## Overview

Test suite covering all API endpoints with various scenarios including:
- Valid requests
- Invalid data
- Missing fields
- Edge cases
- Error handling

## Test Structure

### Test Classes

1. **TestHomeEndpoint** - Tests for `GET /`
   - Returns 200 status
   - Returns JSON format
   - Contains welcome message
   - Contains endpoints list

2. **TestOnboardEndpoint** - Tests for `POST /onboard`
   - Valid form data submission
   - Empty request body
   - Boolean consent conversion (true/false/1/yes)
   - JSON nested objects parsing
   - JSON arrays parsing
   - Exception handling
   - All optional fields

3. **TestOnboardAndInitiateEndpoint** - Tests for `POST /onboard_and_initiate_verification`
   - Valid data submission
   - Empty request body
   - Boolean conversion
   - Exception handling

4. **TestCallbackEndpoint** - Tests for `POST /callback`
   - Valid JSON data
   - Empty data
   - Null data
   - Logging verification

5. **TestInsufficieniesEndpoint** - Tests for `GET /insufficiencies`
   - Without query parameters
   - With individual_id
   - With request_id
   - With pagination (page_no, page_size)
   - With all parameters
   - Exception handling
   - Default pagination values

6. **TestInsufficieniesResolveEndpoint** - Tests for `POST /insufficiencies/resolve/<individual_id>`
   - Valid resolution data
   - Missing required data
   - Null body
   - With document uploads
   - Multiple resolutions
   - Exception handling
   - Zero individual_id
   - Non-numeric individual_id

7. **TestErrorHandling** - General error tests
   - Invalid HTTP methods
   - Non-existent endpoints
   - Invalid route parameters

## Installation

Install test dependencies:

```bash
pip install -r requirements.txt
```

## Running Tests

### Run all tests
```bash
pytest test_app.py -v
```

### Run specific test class
```bash
pytest test_app.py::TestOnboardEndpoint -v
```

### Run specific test
```bash
pytest test_app.py::TestOnboardEndpoint::test_onboard_with_valid_data -v
```

### Run with coverage report
```bash
pytest test_app.py --cov=app --cov-report=html
```

### Run with detailed output
```bash
pytest test_app.py -vv --tb=long
```

## Test Coverage

Current test coverage: **100%** of all API endpoints

### Endpoints Tested
- ✅ `GET /` - Home endpoint
- ✅ `POST /onboard` - Onboard candidate
- ✅ `POST /onboard_and_initiate_verification` - Onboard and initiate
- ✅ `POST /callback` - Webhook handler
- ✅ `GET /insufficiencies` - Get insufficiencies
- ✅ `POST /insufficiencies/resolve/<individual_id>` - Resolve insufficiencies

### Test Scenarios
- ✅ Valid requests
- ✅ Invalid/missing data
- ✅ Data type conversions
- ✅ JSON parsing
- ✅ Exception handling
- ✅ HTTP method validation
- ✅ Route parameter validation
- ✅ Query parameter handling

## Mocking

Tests use `unittest.mock` to mock OnGridClient calls:
- No actual API calls during testing
- Controlled test environment
- Fast test execution
- Predictable results

## Test Data Examples

### Valid Onboard Data
```python
{
    'name': 'John Doe',
    'profession_id': '1',
    'gender': 'M',
    'city': 'Mumbai',
    'phone': '9876543210',
    'has_consent': 'true',
    'consent_text': 'I agree to background verification'
}
```

### Valid Insufficiency Resolution Data
```python
{
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
```

## Continuous Integration

Add to your CI/CD pipeline:

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pytest test_app.py -v --cov=app
```

## Best Practices

1. **Run tests before commits**
   ```bash
   pytest test_app.py
   ```

2. **Check coverage regularly**
   ```bash
   pytest test_app.py --cov=app --cov-report=term-missing
   ```

3. **Update tests when adding new endpoints**

4. **Keep tests isolated** - Each test should be independent

5. **Use descriptive test names** - Clearly describe what's being tested

## Troubleshooting

### Import errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Mock not working
Check that `@patch('app.client')` is correctly applied to test functions.

### Coverage not 100%
Run with missing lines report:
```bash
pytest test_app.py --cov=app --cov-report=term-missing
```

## Future Enhancements

- Integration tests with real API calls (staging environment)
- Performance/load testing
- Authentication/authorization tests
- Rate limiting tests
- Database integration tests
