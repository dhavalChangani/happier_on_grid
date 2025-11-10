import os

from flask import Flask, request, jsonify

from ongrid import OnGridClient

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
            "POST /onboard_and_initiate_verification - Onboard and initiate verification for a candidate",
            "POST /documents/pan/add/<individual_id> - Add PAN document",
            "PUT /documents/pan/update/<individual_id>/<document_id> - Update PAN document",
            "POST /documents/education/add/<individual_id> - Add education document",
            "POST /employment/add/<individual_id> - Add employment record",
            "POST /verifications/pan/<individual_id>/<document_id> - Request PAN verification",
            "POST /verifications/education/<individual_id>/<education_document_id> - Request education verification",
            "POST /verifications/employment/<individual_id>/<employment_record_id> - Request employment verification",
            "POST /verifications/employment_history/<individual_id> - Request employment history check",
            "POST /verifications/prc/<individual_id> - Request professional reference check",
            "GET /status/pan/<individual_id>/<request_id> - Get PAN verification status",
            "GET /status/education/<individual_id> - Get education verification status",
            "GET /status/employment/<individual_id>/<request_id> - Get employment verification status",
            "GET /status/prc/<individual_id> - Get professional reference check status",
            "GET /insufficiencies - Get list of insufficiencies",
            "POST /insufficiencies/resolve/<individual_id> - Provide insufficiency resolution data"]
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

@app.route('/insufficiencies', methods=['GET'])
def get_insufficiencies():
    """
    Get list of insufficiencies
    
    Query parameters:
    - individual_id: Individual ID (optional)
    - request_id: Request ID (optional)
    - page_no: Page number (default: 0)
    - page_size: Size of each page, range 1-500 (default: 100)
    """
    individual_id = request.args.get('individual_id', type=int)
    request_id = request.args.get('request_id', type=int)
    page_no = request.args.get('page_no', type=int, default=0)
    page_size = request.args.get('page_size', type=int, default=100)
    
    try:
        result = client.get_insufficiencies(
            individual_id=individual_id,
            request_id=request_id,
            page_no=page_no,
            page_size=page_size
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/insufficiencies/resolve/<int:individual_id>', methods=['POST'])
def provide_insufficiency_resolution_data(individual_id):
    """
    Provide data for insufficiency resolution for a particular individual
    
    Path parameters:
    - individual_id: Individual ID (required)
    
    Body (JSON):
    - insuffResolutionData: Array of insufficiency resolution objects
        - requestId: Request ID (required)
        - data: Data object with comments and textDataMap (optional)
        - documents: File upload object (optional)
    
    Example:
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
    """
    data = request.json
    
    if not data or 'insuffResolutionData' not in data:
        return jsonify({"error": "insuffResolutionData is required in request body"}), 400
    
    try:
        result = client.provide_insufficiency_resolution_data(
            individual_id=individual_id,
            insufficiency_resolution_data=data['insuffResolutionData']
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/documents/pan/add/<int:individual_id>', methods=['POST'])
def add_pan_document(individual_id):
    """
    Add PAN document
    
    Path parameters:
    - individual_id: Individual ID (required)
    
    Form data:
    - file: PAN document file (required)
    - document_uid: PAN number (required)
    - name_as_per_document: Name as per PAN (required)
    - legal_guardian_name: Legal guardian name (optional)
    - dob: Date of birth in YYYY-MM-DD format (optional)
    """
    if 'file' not in request.files:
        return jsonify({"error": "file is required"}), 400
    
    file = request.files['file']
    document_uid = request.form.get('document_uid')
    name_as_per_document = request.form.get('name_as_per_document')
    legal_guardian_name = request.form.get('legal_guardian_name')
    dob = request.form.get('dob')
    
    if not document_uid or not name_as_per_document:
        return jsonify({"error": "document_uid and name_as_per_document are required"}), 400
    
    file_path = f"/tmp/{file.filename}"
    file.save(file_path)
    
    try:
        result = client.add_pan_document(
            individual_id=individual_id,
            file_path=file_path,
            document_uid=document_uid,
            name_as_per_document=name_as_per_document,
            legal_guardian_name=legal_guardian_name,
            dob=dob
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.route('/documents/pan/update/<int:individual_id>/<int:document_id>', methods=['PUT'])
def update_pan_document(individual_id, document_id):
    """
    Update PAN document
    
    Path parameters:
    - individual_id: Individual ID (required)
    - document_id: Document ID (required)
    
    Form data:
    - file: PAN document file (required)
    - document_uid: PAN number (required)
    - name_as_per_document: Name as per PAN (required)
    - legal_guardian_name: Legal guardian name (optional)
    - dob: Date of birth in YYYY-MM-DD format (optional)
    """
    if 'file' not in request.files:
        return jsonify({"error": "file is required"}), 400
    
    file = request.files['file']
    document_uid = request.form.get('document_uid')
    name_as_per_document = request.form.get('name_as_per_document')
    legal_guardian_name = request.form.get('legal_guardian_name')
    dob = request.form.get('dob')
    
    if not document_uid or not name_as_per_document:
        return jsonify({"error": "document_uid and name_as_per_document are required"}), 400
    
    file_path = f"/tmp/{file.filename}"
    file.save(file_path)
    
    try:
        result = client.update_pan_document(
            individual_id=individual_id,
            document_id=document_id,
            file_path=file_path,
            document_uid=document_uid,
            name_as_per_document=name_as_per_document,
            legal_guardian_name=legal_guardian_name,
            dob=dob
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.route('/documents/education/add/<int:individual_id>', methods=['POST'])
def add_education_document(individual_id):
    """
    Add education document
    
    Path parameters:
    - individual_id: Individual ID (required)
    
    Form data:
    - file: Education document file (required)
    - level: Education level (required)
    - name_of_institute: Institute name (required)
    - degree: Degree name (required)
    - name_as_per_document: Name as per document (required)
    - registration_number: Registration number (required)
    - year_of_passing: Year of passing (optional)
    - field_of_study: Field of study (optional)
    - duration_in_months: Duration in months (optional)
    - grade: Grade (optional)
    - name_of_board_university: Board/University name (optional)
    - issue_date: Issue date in YYYY-MM-DD format (optional)
    - document_id: Document ID (optional)
    """
    if 'file' not in request.files:
        return jsonify({"error": "file is required"}), 400
    
    file = request.files['file']
    level = request.form.get('level')
    name_of_institute = request.form.get('name_of_institute')
    degree = request.form.get('degree')
    name_as_per_document = request.form.get('name_as_per_document')
    registration_number = request.form.get('registration_number')
    
    if not all([level, name_of_institute, degree, name_as_per_document, registration_number]):
        return jsonify({"error": "level, name_of_institute, degree, name_as_per_document, and registration_number are required"}), 400
    
    file_path = f"/tmp/{file.filename}"
    file.save(file_path)
    
    try:
        result = client.add_education_document(
            individual_id=individual_id,
            file_path=file_path,
            level=level,
            name_of_institute=name_of_institute,
            degree=degree,
            name_as_per_document=name_as_per_document,
            registration_number=registration_number,
            year_of_passing=int(request.form.get('year_of_passing')) if request.form.get('year_of_passing') else None,
            field_of_study=request.form.get('field_of_study'),
            duration_in_months=int(request.form.get('duration_in_months')) if request.form.get('duration_in_months') else None,
            grade=request.form.get('grade'),
            name_of_board_university=request.form.get('name_of_board_university'),
            issue_date=request.form.get('issue_date'),
            document_id=request.form.get('document_id')
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.route('/employment/add/<int:individual_id>', methods=['POST'])
def add_employment_record(individual_id):
    """
    Add employment record
    
    Path parameters:
    - individual_id: Individual ID (required)
    
    Form data:
    - name_as_per_employer_records: Name as per employer records (required)
    - employer_name: Employer name (required)
    - employment_record_id: Employment record ID (optional)
    - employee_id: Employee ID (optional)
    - last_designation: Last designation (optional)
    - job_description: Job description (optional)
    - last_working_city: Last working city (optional)
    - joining_date: Joining date in YYYY-MM-DD format (optional)
    - last_working_date: Last working date in YYYY-MM-DD format (optional)
    - annual_compensation: Annual compensation (optional)
    - salaryslip: Salary slip file (optional)
    - appointmentletter: Appointment letter file (optional)
    - experienceletter: Experience letter file (optional)
    - manager_name: Manager name (optional)
    - manager_email: Manager email (optional)
    - manager_phone: Manager phone (optional)
    - manager_phone_country_code: Manager phone country code (optional)
    - hr_name: HR name (optional)
    - hr_email: HR email (optional)
    - hr_phone: HR phone (optional)
    - hr_phone_country_code: HR phone country code (optional)
    """
    name_as_per_employer_records = request.form.get('name_as_per_employer_records')
    employer_name = request.form.get('employer_name')
    
    if not name_as_per_employer_records or not employer_name:
        return jsonify({"error": "name_as_per_employer_records and employer_name are required"}), 400
    
    salaryslip_path = None
    appointmentletter_path = None
    experienceletter_path = None
    
    try:
        if 'salaryslip' in request.files:
            file = request.files['salaryslip']
            salaryslip_path = f"/tmp/{file.filename}"
            file.save(salaryslip_path)
        
        if 'appointmentletter' in request.files:
            file = request.files['appointmentletter']
            appointmentletter_path = f"/tmp/{file.filename}"
            file.save(appointmentletter_path)
        
        if 'experienceletter' in request.files:
            file = request.files['experienceletter']
            experienceletter_path = f"/tmp/{file.filename}"
            file.save(experienceletter_path)
        
        result = client.add_employment_record(
            individual_id=individual_id,
            name_as_per_employer_records=name_as_per_employer_records,
            employer_name=employer_name,
            employment_record_id=int(request.form.get('employment_record_id')) if request.form.get('employment_record_id') else None,
            employee_id=request.form.get('employee_id'),
            last_designation=request.form.get('last_designation'),
            job_description=request.form.get('job_description'),
            last_working_city=request.form.get('last_working_city'),
            joining_date=request.form.get('joining_date'),
            last_working_date=request.form.get('last_working_date'),
            annual_compensation=int(request.form.get('annual_compensation')) if request.form.get('annual_compensation') else None,
            salaryslip_path=salaryslip_path,
            appointmentletter_path=appointmentletter_path,
            experienceletter_path=experienceletter_path,
            manager_name=request.form.get('manager_name'),
            manager_email=request.form.get('manager_email'),
            manager_phone=request.form.get('manager_phone'),
            manager_phone_country_code=request.form.get('manager_phone_country_code'),
            hr_name=request.form.get('hr_name'),
            hr_email=request.form.get('hr_email'),
            hr_phone=request.form.get('hr_phone'),
            hr_phone_country_code=request.form.get('hr_phone_country_code')
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        if salaryslip_path and os.path.exists(salaryslip_path):
            os.remove(salaryslip_path)
        if appointmentletter_path and os.path.exists(appointmentletter_path):
            os.remove(appointmentletter_path)
        if experienceletter_path and os.path.exists(experienceletter_path):
            os.remove(experienceletter_path)

@app.route('/verifications/pan/<int:individual_id>/<int:document_id>', methods=['POST'])
def request_pan_verification(individual_id, document_id):
    """
    Request PAN verification
    
    Path parameters:
    - individual_id: Individual ID (required)
    - document_id: Document ID (required)
    """
    try:
        result = client.request_pan_verification(individual_id, document_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/verifications/education/<int:individual_id>/<int:education_document_id>', methods=['POST'])
def request_education_verification(individual_id, education_document_id):
    """
    Request education verification
    
    Path parameters:
    - individual_id: Individual ID (required)
    - education_document_id: Education document ID (required)
    """
    try:
        result = client.request_education_verification(individual_id, education_document_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/verifications/employment/<int:individual_id>/<int:employment_record_id>', methods=['POST'])
def request_employment_verification(individual_id, employment_record_id):
    """
    Request employment verification
    
    Path parameters:
    - individual_id: Individual ID (required)
    - employment_record_id: Employment record ID (required)
    """
    try:
        result = client.request_employment_verification(individual_id, employment_record_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/verifications/employment_history/<int:individual_id>', methods=['POST'])
def request_employment_history_check(individual_id):
    """
    Request employment history check
    
    Path parameters:
    - individual_id: Individual ID (required)
    
    Body (JSON):
    - uans: List of UAN numbers (required)
    
    Example:
    {
        "uans": ["123456789012", "987654321098"]
    }
    """
    data = request.json
    
    if not data or 'uans' not in data:
        return jsonify({"error": "uans is required in request body"}), 400
    
    try:
        result = client.request_employment_history_check(individual_id, data['uans'])
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/verifications/prc/<int:individual_id>', methods=['POST'])
def request_prc(individual_id):
    """
    Request professional reference check
    
    Path parameters:
    - individual_id: Individual ID (required)
    
    Body (JSON):
    - schema_id: Schema ID (required)
    - reference_provider_name: Reference provider name (required)
    - reference_provider_email: Reference provider email (required)
    - organisation: Organisation (required)
    - designation: Designation (required)
    - reference_type: Reference type (required)
    - reporting_manager: Reporting manager boolean (required)
    - reference_provider_id: Reference provider ID (optional)
    - reference_provider_phone: Reference provider phone (optional)
    - reference_provider_phone_country_code: Reference provider phone country code (optional)
    - start_year_of_association: Start year of association (optional)
    - end_year_of_association: End year of association (optional)
    - individual_designation: Individual designation (optional)
    """
    data = request.json
    
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    required_fields = ['schema_id', 'reference_provider_name', 'reference_provider_email', 
                      'organisation', 'designation', 'reference_type', 'reporting_manager']
    
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    
    try:
        result = client.request_prc(
            individual_id=individual_id,
            schema_id=data['schema_id'],
            reference_provider_name=data['reference_provider_name'],
            reference_provider_email=data['reference_provider_email'],
            organisation=data['organisation'],
            designation=data['designation'],
            reference_type=data['reference_type'],
            reporting_manager=data['reporting_manager'],
            reference_provider_id=data.get('reference_provider_id'),
            reference_provider_phone=data.get('reference_provider_phone'),
            reference_provider_phone_country_code=data.get('reference_provider_phone_country_code'),
            start_year_of_association=data.get('start_year_of_association'),
            end_year_of_association=data.get('end_year_of_association'),
            individual_designation=data.get('individual_designation')
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/status/pan/<int:individual_id>/<int:request_id>', methods=['GET'])
def get_pan_verification_status(individual_id, request_id):
    """
    Get PAN verification status
    
    Path parameters:
    - individual_id: Individual ID (required)
    - request_id: Request ID (required)
    """
    try:
        result = client.get_pan_verification_status(individual_id, request_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/status/education/<int:individual_id>', methods=['GET'])
def get_education_verification_status(individual_id):
    """
    Get education verification status
    
    Path parameters:
    - individual_id: Individual ID (required)
    
    Query parameters:
    - request_id: Request ID (optional)
    """
    request_id = request.args.get('request_id', type=int)
    
    try:
        result = client.get_education_verification_status(individual_id, request_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/status/employment/<int:individual_id>/<int:request_id>', methods=['GET'])
def get_employment_verification_status(individual_id, request_id):
    """
    Get employment verification status
    
    Path parameters:
    - individual_id: Individual ID (required)
    - request_id: Request ID (required)
    """
    try:
        result = client.get_employment_verification_status(individual_id, request_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/status/prc/<int:individual_id>', methods=['GET'])
def get_professional_reference_check_status(individual_id):
    """
    Get professional reference check status
    
    Path parameters:
    - individual_id: Individual ID (required)
    
    Query parameters:
    - request_id: Request ID (optional)
    """
    request_id = request.args.get('request_id', type=int)
    
    try:
        result = client.get_professional_reference_check_status(individual_id, request_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
