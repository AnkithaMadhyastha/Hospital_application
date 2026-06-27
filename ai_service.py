import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def analyze_health_risk(glucose, haemoglobin, cholesterol):

    prompt = f"""
You are an experienced medical AI assistant.

Analyze these blood test values.

Glucose: {glucose} mg/dL
Haemoglobin: {haemoglobin} g/dL
Cholesterol: {cholesterol} mg/dL

Return your answer with these headings only:

🩺 AI Health Assessment

📊 Blood Test Analysis

⚠️ Possible Health Risks

💡 Recommendations

Keep the response professional, around 150 words.

Mention that this is not a final medical diagnosis.
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text

    except Exception as e:

        print("Gemini Error:", e)

        return generate_fallback_remarks(glucose, haemoglobin, cholesterol)


def generate_fallback_remarks(glucose, haemoglobin, cholesterol):

    remarks = []

    remarks.append("⚠️ AI service is temporarily unavailable.\n")

    if glucose > 125:
        remarks.append("• High glucose detected.")
    elif glucose > 100:
        remarks.append("• Prediabetes range.")
    else:
        remarks.append("• Glucose normal.")

    if haemoglobin < 12:
        remarks.append("• Low haemoglobin detected.")
    else:
        remarks.append("• Haemoglobin normal.")

    if cholesterol > 239:
        remarks.append("• High cholesterol detected.")
    elif cholesterol > 200:
        remarks.append("• Borderline cholesterol.")
    else:
        remarks.append("• Cholesterol normal.")

    remarks.append("\nConsult a doctor for proper diagnosis.")

    return "\n".join(remarks)
