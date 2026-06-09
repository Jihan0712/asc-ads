import streamlit as st
import os
from media_processor import process_video, process_image
from ai_engine import evaluate_ad

st.set_page_config(page_title="AI Ad Checker", layout="wide")

st.sidebar.title("Settings")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
st.sidebar.markdown("---")

st.title("🎥 Automated Ad Compliance Checker (GPT-4o)")
st.write("Upload your Rules PDF and the Ad Media to run the compliance check.")

col1, col2 = st.columns(2)
with col1:
    pdf_file = st.file_uploader("1. Upload Rules (PDF)", type=["pdf"])
with col2:
    media_file = st.file_uploader("2. Upload Ad (Video or Image)", type=["mp4", "mov", "jpg", "png", "jpeg"])

if pdf_file and media_file:
    if st.button("Run AI Check", type="primary"):
        if not api_key:
            st.error("Please enter your OpenAI API Key in the sidebar.")
        else:
            with st.spinner("Extracting frames/audio and analyzing with GPT-4o..."):
                try:
                    ext = os.path.splitext(media_file.name)[1].lower()
                    is_video = ext in ['.mp4', '.mov']
                    
                    # 1. Process Media
                    if is_video:
                        media_data = process_video(api_key, media_file.getvalue(), ext)
                    else:
                        media_data = process_image(media_file.getvalue())
                        
                    # 2. Run Evaluation
                    results = evaluate_ad(api_key, media_data, is_video, pdf_file.getvalue())
                    
                    # 3. Display Results
                    st.subheader("Evaluation Results")
                    for item in results:
                        if item.get("status") == "PASS":
                            st.success(f"✅ {item.get('rule_id')} - PASS")
                            st.caption(item.get('reason'))
                        else:
                            st.error(f"❌ {item.get('rule_id')} - FAIL")
                            st.write(f"**Violation Details:** {item.get('reason')}")
                            
                except Exception as e:
                    st.error(f"An error occurred: {e}")