import json
import tempfile
import os
import time
from google import genai
from google.genai import types

# --- HARDCODED ASC GUIDELINES ---
ASC_RULES = """
I. GENERAL STANDARDS & ETHICS
* Advertisements must conform to Philippine laws and respect the national flag, government, and cultural or religious sensitivities.
* Profanity, obscenity, vulgarity, indecent exposure, and the glorification of crime or violence are strictly prohibited.
* Ads must not directly or indirectly disparage, ridicule, or unfairly attack competitors, minority groups, or people with disabilities.

II. CONSUMER PROTECTION & SAFETY
* Advertisements must be honest, truthful, and not deceptive or misleading.
* Product claims must be substantiated by third-party research, laboratory tests, or published medical journals.

III. PROTECTION OF CHILDREN
* Children must not be portrayed in dangerous situations or engaged in activities requiring adult supervision.
* Ads for alcohol, tobacco, e-cigarettes, or gambling must not inappropriately depict or exploit children.

IV. ADVERTISING CLAIMS
* No. 1 / Leadership: Requires at least 12-month cumulative data on both retail volume and value from an independent source.
* Absolute Claims (e.g., "100% germ-free"): Requires at least three separate identical tests by an independent 3rd-party testing agency.

V. REGULATED PRODUCTS
* OTC Drugs / Home Remedies: Must clearly display the Generic Name prominently over the Brand Name and include the mandatory statement "If symptoms persist, consult your doctor."
* Food/Dietary Supplements: Must strictly carry the standard message "MAHALAGANG PAALALA: ANG (NAME OF PRODUCT) AY HINDI GAMOT AT HINDI DAPAT GAMITING PANGGAMOT SA ANUMANG URI NG SAKIT" prominently.
* Alcohol Beverages: Must carry the mandatory statement "DRINK RESPONSIBLY", target persons of legal age (21+), and avoid appealing to minors.
"""

def check_ad_compliance(api_key, file_bytes, file_name, mime_type):
    """Uploads media to Gemini, runs the prompt, and returns JSON."""
    client = genai.Client(api_key=api_key)

    # 1. Save the Streamlit upload to a temporary file
    ext = os.path.splitext(file_name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name

    try:
        # 2. Upload the file to Google's secure servers
        uploaded_file = client.files.upload(file=temp_path)

        # 3. If it's a video, we must wait for Google to process the frames
        if "video" in mime_type:
            # Refresh the file status until it is ACTIVE
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(3)
                uploaded_file = client.files.get(name=uploaded_file.name)
            
            if uploaded_file.state.name == "FAILED":
                raise Exception("Google Gemini failed to process this video file.")

        # 4. Build the prompt
        prompt = f"""
        You are an expert Philippine Ad Compliance Checker. 
        Review the attached media against these core Ad Standards Council (ASC) rules:
        {ASC_RULES}
        
        Return your analysis STRICTLY as a JSON array matching this exact format:
        [
          {{
            "rule_id": "Name of the rule",
            "status": "PASS or FAIL",
            "reason": "Why it passed or failed based on what you see/hear."
          }}
        ]
        """

        # 5. Call the AI
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[uploaded_file, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )

        # 6. Delete the file from Google's servers to save space
        client.files.delete(name=uploaded_file.name)

        # Return the parsed JSON
        return json.loads(response.text)

    finally:
        # Clean up the local temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)