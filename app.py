from flask import Flask, request, jsonify
from ongrid_client import OnGridClient, OnGridException
import os

app = Flask(__name__)

client_id=os.getenv("ONGRID_CLIENT_ID", "your-client-id-here")
client_secret=os.getenv("ONGRID_CLIENT_SECRET", "your-client-secret-here")
community_id=os.getenv("ONGRID_COMMUNITY_ID", "your-community-id-here")
base_url=os.getenv("ONGRID_BASE_URL", "https://api-staging.ongrid.in/app")
consent_text=os.getenv("ONGRID_CONSENT_TEXT", "I agree to background verification")

# Initialize OnGrid client
client = OnGridClient(
    client_id=client_id,
    client_secret=client_secret,
    community_id=community_id,
    base_url=base_url,
    consent_text=consent_text
)


@app.route('/')
def home():
    return jsonify({
        "message": "OnGrid Test API",
        "endpoints": [
            "POST /onboard - Onboard a candidate",
            "GET /status/<verification_id> - Get verification status",
            "GET /report/<verification_id> - Get verification report",
            "POST /cancel/<verification_id> - Cancel verification"
        ]
    })


@app.route('/onboard', methods=['POST'])
def onboard():
    """
    Onboard a new candidate
    
    Accepts either JSON or form data.
    
    Required fields:
    - name: Individual's full name
    - profession_id: ID of the profession
    - gender: M, F, T, O, or U
    - city: City where individual is working
    - phone: Mobile number
    - has_consent: true/false (boolean)
    - consent_text: Consent text
    
    Optional fields:
    - email, dob, employee_id, phone_country_code, etc.
    """
    
    # Accept both JSON and form data
    if request.is_json:
        data = request.json
    else:
        data = dict(request.form.to_dict())
        
        # Convert boolean fields from form data
        if 'has_consent' in data:
            consent_value = str(data['has_consent']).lower() in ['true', '1', 'yes']
            data['has_consent'] = consent_value
        
        # Convert nested objects if sent as JSON strings
        import json
        for field in ['permanent_address', 'other_identifiers', 'tags']:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except json.JSONDecodeError:
                    pass
        
        # Convert array fields if sent as JSON strings
        for field in ['deduplication_keys', 'uans']:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except json.JSONDecodeError:
                    pass
    
    print(f"Received onboarding request: {data}")
    
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    try:
        result = client.onboard_candidate(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/status/<verification_id>', methods=['GET'])
def get_status(verification_id):
    """Get verification status"""
    try:
        result = client.get_verification_status(verification_id)
        return jsonify(result)
    except OnGridException as e:
        return jsonify({"error": str(e)}), 400


@app.route('/report/<verification_id>', methods=['GET'])
def get_report(verification_id):
    """Get verification report"""
    try:
        result = client.get_verification_report(verification_id)
        return jsonify(result)
    except OnGridException as e:
        return jsonify({"error": str(e)}), 400


@app.route('/cancel/<verification_id>', methods=['POST'])
def cancel(verification_id):
    """Cancel verification"""
    try:
        result = client.cancel_verification(verification_id)
        return jsonify(result)
    except OnGridException as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
