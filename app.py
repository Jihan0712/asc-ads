import streamlit as st
from media_processor import upload_to_gemini
from ai_engine import evaluate_ad

# --- Configuration ---
st.set_page_config(page_title="AI Ad Checker", layout="centered") # Changed to centered for a cleaner look

# --- Sidebar ---
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
st.sidebar.markdown("---")

st.title("🎥 ASC Ad Compliance Checker")
st.write("Upload your Ad Media (Image or Video) to run an instant compliance check against Philippine ASC Guidelines.")

# File Uploader (Only Media now!)
media_file = st.file_uploader("Upload Ad (Video or Image)", type=["mp4", "mov", "jpg", "png", "jpeg"])

if media_file:
    if st.button("Run AI Check", type="primary", use_container_width=True):
        if not api_key:
            st.error("Please enter your Google Gemini API Key in the sidebar.")
        else:
            with st.spinner("Analyzing media with Gemini 2.0 Flash..."):
                try:
                    # 1. Upload the Ad Media to Gemini
                    gemini_media = upload_to_gemini(
                        api_key=api_key, 
                        file_bytes=media_file.getvalue(), 
                        file_name=media_file.name
                    )
                    
                    # 2. Run the AI evaluation (No PDF needed)
                    results = evaluate_ad(api_key, gemini_media)
                    
                    # 3. Display Results
                    st.subheader("Evaluation Results")
                    for item in results:
                        if item.get("status") == "PASS":
                            st.success(f"✅ **{item.get('rule_id')}** - PASS")
                            st.caption(item.get('reason'))
                        else:
                            st.error(f"❌ **{item.get('rule_id')}** - FAIL")
                            st.write(f"**Violation Details:** {item.get('reason')}")
                            
                except Exception as e:
                    st.error(f"An error occurred: {e}")