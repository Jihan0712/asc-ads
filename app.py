import streamlit as st
from media_processor import upload_to_gemini
from ai_engine import evaluate_ad

# --- Configuration ---
st.set_page_config(page_title="AI Ad Checker", layout="wide")

# --- Sidebar ---
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
st.sidebar.markdown("---")

st.title("🎥 Automated Ad Compliance Checker")
st.write("Upload your Rules PDF and the Ad Media to run the compliance check.")

# File Uploaders
col1, col2 = st.columns(2)
with col1:
    pdf_file = st.file_uploader("1. Upload Rules & Regulations (PDF)", type=["pdf"])
with col2:
    media_file = st.file_uploader("2. Upload Ad (Video or Image)", type=["mp4", "mov", "jpg", "png", "jpeg"])

if pdf_file and media_file:
    if st.button("Run AI Check", type="primary"):
        if not api_key:
            st.error("Please enter your Gemini API Key in the sidebar.")
        else:
            with st.spinner("Uploading files and analyzing with Gemini 1.5 Pro..."):
                try:
                    # 1. Upload the PDF to Gemini
                    gemini_pdf = upload_to_gemini(
                        api_key=api_key, 
                        file_bytes=pdf_file.getvalue(), 
                        file_name=pdf_file.name
                    )
                    
                    # 2. Upload the Ad Media to Gemini
                    gemini_media = upload_to_gemini(
                        api_key=api_key, 
                        file_bytes=media_file.getvalue(), 
                        file_name=media_file.name
                    )
                    
                    # 3. Run the AI evaluation using both files
                    results = evaluate_ad(api_key, gemini_media, gemini_pdf)
                    
                    # 4. Display Results
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