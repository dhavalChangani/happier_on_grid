# OnGrid Flask Test App

Simple Flask app to test the OnGrid client.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your OnGrid API key:
```bash
export ONGRID_API_KEY="your-api-key-here"
```

3. Run the app:
```bash
python app.py
```

The app will run on `http://localhost:5000`

## API Endpoints

### 1. Home
```bash
curl http://localhost:5000/
```

### 2. Onboard a Candidate
```bash
curl -X POST http://localhost:5000/onboard \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "mobile": "+919876543210",
    "date_of_birth": "1990-01-15",
    "address": {
      "line1": "123 Main St",
      "city": "Mumbai",
      "state": "Maharashtra",
      "pincode": "400001"
    },
    "verification_types": ["identity", "address"],
    "reference_id": "EMP-001"
  }'
```

### 3. Get Verification Status
```bash
curl http://localhost:5000/status/VER-123456
```

### 4. Get Verification Report
```bash
curl http://localhost:5000/report/VER-123456
```

### 5. Cancel Verification
```bash
curl -X POST http://localhost:5000/cancel/VER-123456
```
