import requests
import os

HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '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')
API_URL = "[api-inference.huggingface.co](https://api-inference.huggingface.co/models/facebook/bart-large-mnli)"


def analyze_health_risk(glucose, haemoglobin, cholesterol):
    """
    Analyze health risk based on blood test values using AI classification.
    Uses zero-shot classification to predict health conditions.
    """

    # Build a clinical summary from the values
    clinical_text = f"""
    Patient blood test results:
    - Glucose level: {glucose} mg/dL
    - Haemoglobin level: {haemoglobin} g/dL  
    - Cholesterol level: {cholesterol} mg/dL
    """

    # Health condition labels for classification
    candidate_labels = [
        "healthy normal results",
        "diabetes risk high glucose",
        "anemia risk low haemoglobin",
        "cardiovascular risk high cholesterol",
        "multiple health concerns",
        "prediabetes borderline glucose"
    ]

    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {
        "inputs": clinical_text,
        "parameters": {"candidate_labels": candidate_labels}
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()

        # Get top prediction
        top_label = result.get('labels', ['Unable to analyze'])[0]
        confidence = result.get('scores', [0])[0]

        # Generate human-readable remarks
        remarks = generate_health_remarks(glucose, haemoglobin, cholesterol, top_label, confidence)
        return remarks

    except requests.exceptions.RequestException as e:
        # Fallback to rule-based analysis if API fails
        return generate_fallback_remarks(glucose, haemoglobin, cholesterol)


def generate_health_remarks(glucose, haemoglobin, cholesterol, ai_prediction, confidence):
    """Generate comprehensive health remarks combining AI prediction with medical ranges."""

    remarks = []

    # Add AI prediction
    confidence_pct = round(confidence * 100)
    remarks.append(f"🤖 AI Assessment: {ai_prediction.replace('_', ' ').title()} (Confidence: {confidence_pct}%)")
    remarks.append("")

    # Glucose analysis (normal: 70-100 mg/dL fasting)
    if glucose < 70:
        remarks.append("⚠️ Glucose: Low (Hypoglycemia risk)")
    elif glucose <= 100:
        remarks.append("✅ Glucose: Normal range")
    elif glucose <= 125:
        remarks.append("⚠️ Glucose: Elevated (Prediabetes range)")
    else:
        remarks.append("🔴 Glucose: High (Diabetes range)")

    # Haemoglobin analysis (normal: 12-17 g/dL)
    if haemoglobin < 12:
        remarks.append("⚠️ Haemoglobin: Low (Anemia risk)")
    elif haemoglobin <= 17:
        remarks.append("✅ Haemoglobin: Normal range")
    else:
        remarks.append("⚠️ Haemoglobin: Elevated")

    # Cholesterol analysis (normal: <200 mg/dL)
    if cholesterol < 200:
        remarks.append("✅ Cholesterol: Normal range")
    elif cholesterol <= 239:
        remarks.append("⚠️ Cholesterol: Borderline high")
    else:
        remarks.append("🔴 Cholesterol: High (Cardiovascular risk)")

    remarks.append("")
    remarks.append("📋 Recommendation: Please consult a healthcare professional for proper diagnosis.")

    return "\n".join(remarks)


def generate_fallback_remarks(glucose, haemoglobin, cholesterol):
    """Fallback rule-based analysis when API is unavailable."""

    remarks = ["📊 Health Analysis (Rule-based):", ""]
    risk_count = 0

    if glucose > 125:
        remarks.append("🔴 High glucose detected - Diabetes screening recommended")
        risk_count += 1
    elif glucose > 100:
        remarks.append("⚠️ Elevated glucose - Monitor blood sugar levels")
    else:
        remarks.append("✅ Glucose within normal limits")

    if haemoglobin < 12:
        remarks.append("🔴 Low haemoglobin - Anemia evaluation recommended")
        risk_count += 1
    else:
        remarks.append("✅ Haemoglobin within normal limits")

    if cholesterol > 239:
        remarks.append("🔴 High cholesterol - Cardiovascular risk assessment needed")
        risk_count += 1
    elif cholesterol > 200:
        remarks.append("⚠️ Borderline cholesterol - Lifestyle modifications suggested")
    else:
        remarks.append("✅ Cholesterol within normal limits")

    remarks.append("")
    if risk_count >= 2:
        remarks.append("⚠️ Multiple risk factors detected. Please consult a doctor.")
    elif risk_count == 1:
        remarks.append("📋 One risk factor identified. Follow-up recommended.")
    else:
        remarks.append("✅ All values within normal ranges. Continue healthy lifestyle.")

    return "\n".join(remarks)
