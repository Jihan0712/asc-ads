import os
import cv2
import base64
import tempfile
from moviepy import VideoFileClip
from openai import OpenAI

def process_image(image_bytes):
    """Converts a standard image into a base64 string for GPT-4o."""
    return base64.b64encode(image_bytes).decode("utf-8")

def process_video(api_key, video_bytes, file_extension):
    """Extracts 1 frame per second and transcribes audio via Whisper."""
    client = OpenAI(api_key=api_key)
    base64_frames = []
    transcript = "No audio detected."
    
    # Save video bytes to a temporary file for processing
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_vid:
        temp_vid.write(video_bytes)
        video_path = temp_vid.name
        
    try:
        # 1. Extract Frames (1 per second)
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_count = 0
        
        while video.isOpened():
            success, frame = video.read()
            if not success:
                break
            # Capture strictly one frame per second to save token costs
            if int(frame_count % fps) == 0:
                _, buffer = cv2.imencode(".jpg", frame)
                base64_frames.append(base64.b64encode(buffer).decode("utf-8"))
            frame_count += 1
        video.release()

        # 2. Extract Audio and Transcribe via Whisper
        try:
            clip = VideoFileClip(video_path)
            if clip.audio is not None:
                audio_path = video_path.replace(file_extension, ".mp3")
                clip.audio.write_audiofile(audio_path, logger=None)
                with open(audio_path, "rb") as audio_file:
                    res = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
                    transcript = res.text
                os.remove(audio_path)
            clip.close()
        except Exception:
            transcript = "Audio extraction failed or missing."
            
    finally:
        os.remove(video_path)
        
    return base64_frames, transcript