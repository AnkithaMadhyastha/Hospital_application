from flask import Flask, render_template, request, jsonify
from database import init_db, create_patient, get_all_patients, get_patient, update_patient, delete_patient
from ai_service import analyze_health_risk
import re
from datetime import datetime

app = Flask(__name__)

# Initialize database on startup
init_db()


def validate_patient_data(data):
    """Validate patient input data."""
    errors = []

    # Full name validation
    if not data.get('full_name') or len(data['full_name'].strip()) < 2:
        errors.append("Full name is required (minimum 2 characters)")

    # Email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not data.get('email') or not re.match(email_pattern, data['email']):
        errors.append("Valid email address is required")

    # Date of birth validation
    try:
        dob = datetime.strptime(data.get('date_of_birth', ''), '%Y-%m-%d')
        if dob > datetime.now():
            errors.append("Date of birth cannot be in the future")
    except ValueError:
        errors.append("Valid date of birth is required (YYYY-MM-DD)")

    # Numeric validations for blood test values
    try:
        glucose = float(data.get('glucose', 0))
        if glucose <= 0 or glucose > 1000:
            errors.append("Glucose must be a positive number (0-1000 mg/dL)")
    except (ValueError, TypeError):
        errors.append("Glucose must be a valid number")

    try:
        haemoglobin = float(data.get('haemoglobin', 0))
        if haemoglobin <= 0 or haemoglobin > 30:
            errors.append("Haemoglobin must be a positive number (0-30 g/dL)")
    except (ValueError, TypeError):
        errors.append("Haemoglobin must be a valid number")

    try:
        cholesterol = float(data.get('cholesterol', 0))
        if cholesterol <= 0 or cholesterol > 1000:
            errors.append("Cholesterol must be a positive number (0-1000 mg/dL)")
    except (ValueError, TypeError):
        errors.append("Cholesterol must be a valid number")

    return errors


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/patients', methods=['GET'])
def api_get_patients():
    patients = get_all_patients()
    return jsonify(patients)


@app.route('/api/patients/<int:patient_id>', methods=['GET'])
def api_get_patient(patient_id):
    patient = get_patient(patient_id)
    if patient:
        return jsonify(patient)
    return jsonify({'error': 'Patient not found'}), 404


@app.route('/api/patients', methods=['POST'])
def api_create_patient():
    data = request.json

    # Validate input
    errors = validate_patient_data(data)
    if errors:
        return jsonify({'errors': errors}), 400

    # Generate AI remarks
    try:
        remarks = analyze_health_risk(
            float(data['glucose']),
            float(data['haemoglobin']),
            float(data['cholesterol'])
        )
        data['remarks'] = remarks
    except Exception as e:
        data['remarks'] = f"AI analysis unavailable: {str(e)}"

    patient_id = create_patient(data)
    patient = get_patient(patient_id)
    return jsonify(patient), 201


@app.route('/api/patients/<int:patient_id>', methods=['PUT'])
def api_update_patient(patient_id):
    data = request.json

    # Validate input
    errors = validate_patient_data(data)
    if errors:
        return jsonify({'errors': errors}), 400

    # Regenerate AI remarks if blood values changed
    existing = get_patient(patient_id)
    if existing:
        values_changed = (
                float(data['glucose']) != existing['glucose'] or
                float(data['haemoglobin']) != existing['haemoglobin'] or
                float(data['cholesterol']) != existing['cholesterol']
        )

        if values_changed:
            try:
                remarks = analyze_health_risk(
                    float(data['glucose']),
                    float(data['haemoglobin']),
                    float(data['cholesterol'])
                )
                data['remarks'] = remarks
            except Exception as e:
                data['remarks'] = existing['remarks']
        else:
            data['remarks'] = existing['remarks']

    update_patient(patient_id, data)
    patient = get_patient(patient_id)
    return jsonify(patient)


@app.route('/api/patients/<int:patient_id>', methods=['DELETE'])
def api_delete_patient(patient_id):
    delete_patient(patient_id)
    return jsonify({'message': 'Patient deleted successfully'})


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Endpoint to get AI analysis without saving."""
    data = request.json
    try:
        remarks = analyze_health_risk(
            float(data['glucose']),
            float(data['haemoglobin']),
            float(data['cholesterol'])
        )
        return jsonify({'remarks': remarks})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
