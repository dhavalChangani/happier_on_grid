import os

from flask import Flask, request, jsonify

from ongrid import OnGridClient, OnGridException

app = Flask(__name__)

client = OnGridClient(
    community_id=os.getenv("ONGRID_COMMUNITY_ID", "your-community-id-here"),
)

@app.route('/')
def home():
    return jsonify({
        "message": "OnGrid Test API",
        "endpoints": [
            "POST /onboard - Onboard a candidate",
            "POST /onboard_and_initiate_verification - Onboard and initiate verification for a candidate"]
    })


@app.route('/onboard', methods=['POST'])
def onboard():
    """
    Onboard a new candidate
    
    Accepts form data.
    
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

    # Accept form data
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
    
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    try:
        result = client.onboard_candidate(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/onboard_and_initiate_verification', methods=['POST'])
def onboard_and_initiate():
    """
    Onboard and initiate verification for a new candidate
    
    Accepts form data.
    
    Required fields:
    - name: Individual's full name
    - profession_id: ID of the profession
    - gender: M, F, T, O, or U
    - city: City where individual is working
    - phone: Mobile number
    - has_consent: true/false (boolean)
    - consent_text: Consent text
    """
    
    # Accept form data
    data = dict(request.form.to_dict())
      
        
    # Convert boolean fields from form data
    if 'has_consent' in data:
        consent_value = str(data['has_consent']).lower() in ['true', '1', 'yes']
        data['has_consent'] = consent_value
    
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    try:
        result = client.onboard_and_initiate_verifications(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/callback', methods=['POST'])
def callback():
    """
    Handle OnGrid verification callbacks
    """
    data = request.json
    # Log the callback data
    print("Received OnGrid Callback:", data)
    return jsonify({"status": "Callback received"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
