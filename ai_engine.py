import json
from google import genai
from google.genai import types

def evaluate_ad(api_key, gemini_media_file, gemini_pdf_file):
    """
    Prompts Gemini 2.0 Flash to evaluate the media based on the uploaded PDF guidelines.
    """
    client = genai.Client(api_key=api_key)
        
    prompt = """
    You are an expert Ad Compliance Checker. 
    Review the attached media (video/image) against the rules and regulations 
    found in the attached PDF document.
    
    Evaluate the media against the core guidelines in the PDF and determine 
    if the ad PASSES or FAILS.
    
    Return your analysis strictly in JSON format matching this schema:
    [
      {
        "rule_id": "Name of the specific rule from the PDF",
        "status": "PASS or FAIL",
        "reason": "Detailed explanation of why it passed or failed based on what you saw/heard."
      }
    ]
    """
    
    # Call Gemini 2.0 Flash with both files and force a JSON output
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[gemini_media_file, gemini_pdf_file, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        )
    )
    
    return json.loads(response.text)