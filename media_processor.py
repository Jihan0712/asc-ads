import os
import tempfile
import time
from google import genai

def upload_to_gemini(api_key, file_bytes, file_name):
    """
    Saves the Streamlit uploaded file to a temporary file,
    uploads it to Gemini's File API, and waits for it to be processed.
    """
    client = genai.Client(api_key=api_key)
    
    # Save the uploaded bytes to a local temp file
    file_extension = os.path.splitext(file_name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        temp_file.write(file_bytes)
        temp_file_path = temp_file.name

    try:
        # Upload to Gemini
        gemini_file = client.files.upload(file=temp_file_path)
        
        # Poll until the file is processed (Crucial for video files)
        while not gemini_file.state or gemini_file.state.name != "ACTIVE":
            if gemini_file.state and gemini_file.state.name == "FAILED":
                raise ValueError("Gemini failed to process the media file.")
            time.sleep(2)
            gemini_file = client.files.get(name=gemini_file.name)
            
        return gemini_file
    finally:
        # Clean up local storage
        os.remove(temp_file_path)