import json
import io
from pypdf import PdfReader
from openai import OpenAI

def evaluate_ad(api_key, media_data, is_video, pdf_bytes):
    """Sends the extracted data to GPT-4o and forces a JSON response."""
    client = OpenAI(api_key=api_key)
    
    # 1. Read PDF text locally
    pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
    rules_text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    
    # 2. Build System Prompt (Forcing JSON Output)
    messages = [
        {
            "role": "system",
            "content": "You are an expert Ad Compliance Checker. Review the media against the provided PDF guidelines. You must return your analysis STRICTLY in JSON format matching this schema: {\"results\": [ {\"rule_id\": \"Name of Rule\", \"status\": \"PASS or FAIL\", \"reason\": \"Detailed explanation\"} ] }"
        }
    ]
    
    # 3. Build User Prompt
    user_text = f"Here are the rules and regulations:\n\n{rules_text}\n\n"
    user_content = []
    
    if is_video:
        frames, transcript = media_data
        user_text += f"Audio Transcript: {transcript}\n\nPlease review the following video frames and the transcript against the rules."
        user_content.append({"type": "text", "text": user_text})
        
        # Send up to 10 frames to GPT-4o (keeps API costs low while providing enough context)
        for frame in frames[:10]:
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{frame}"}
            })
    else:
        user_text += "Please review the attached image against the rules."
        user_content.append({"type": "text", "text": user_text})
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{media_data}"}
        })
        
    messages.append({"role": "user", "content": user_content})
    
    # 4. Call GPT-4o
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={"type": "json_object"}
    )
    
    # 5. Parse and return the JSON
    response_json = json.loads(response.choices[0].message.content)
    return response_json.get("results", [])