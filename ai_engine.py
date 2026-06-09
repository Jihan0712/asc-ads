import json
from google import genai
from google.genai import types
from google.genai.errors import APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

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
* Comparative Claims: Allowed if providing clear, substantiated bases from an independent source.

V. REGULATED PRODUCTS
* OTC Drugs / Home Remedies: Must clearly display the Generic Name prominently over the Brand Name and include the mandatory statement "If symptoms persist, consult your doctor."
* Food/Dietary Supplements: Must strictly carry the standard message "MAHALAGANG PAALALA: ANG (NAME OF PRODUCT) AY HINDI GAMOT AT HINDI DAPAT GAMITING PANGGAMOT SA ANUMANG URI NG SAKIT" prominently.
* Alcohol Beverages: Must carry the mandatory statement "DRINK RESPONSIBLY", target persons of legal age (21+), and avoid appealing to minors.
"""

@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(APIError),
    reraise=True
)
def call_gemini_with_retry(client, gemini_media_file, prompt):
    """Executes the API call with automatic backoff for rate limits."""
    return client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[gemini_media_file, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        )
    )

def evaluate_ad(api_key, gemini_media_file):
    """
    Prompts Gemini 2.0 Flash to evaluate the media based on the hardcoded ASC guidelines.
    """
    client = genai.Client(api_key=api_key)
        
    prompt = f"""
    You are an expert Philippine Ad Compliance Checker. 
    Review the attached media (video/image) against the following core Ad Standards Council (ASC) rules:
    
    {ASC_RULES}
    
    Evaluate the media against these guidelines and determine if the ad PASSES or FAILS.
    Pay special attention to mandatory phrases for regulated products.
    
    Return your analysis strictly in JSON format matching this schema:
    [
      {{
        "rule_id": "Name of the specific rule (e.g., Regulated Products: Alcohol)",
        "status": "PASS or FAIL",
        "reason": "Detailed explanation of why it passed or failed based on what you saw/heard."
      }}
    ]
    """
    
    # Call the retry-protected function (No PDF passed this time)
    response = call_gemini_with_retry(client, gemini_media_file, prompt)
    
    return json.loads(response.text)