import streamlit as st
from ai_engine import check_ad_compliance

# --- Page Config ---
st.set_page_config(page_title="ASC Ad Checker", layout="centered")

# --- Sidebar ---
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
st.sidebar.markdown("---")
st.sidebar.info("This tool uses Gemini 2.0 Flash to instantly check ads against Philippine ASC guidelines.")

# --- Main App ---
st.title("🎥 ASC Ad Compliance Checker")
st.write("Upload an Image or Video advertisement to check for compliance.")

# Upload Widget
media_file = st.file_uploader("Upload Advertisement", type=["mp4", "mov", "jpg", "png", "jpeg"])

if media_file:
    if st.button("Run Compliance Check", type="primary", use_container_width=True):
        if not api_key:
            st.error("⚠️ Please enter your Gemini API Key in the sidebar.")
        else:
            with st.spinner("Analyzing media with Google Gemini..."):
                try:
                    # Run the engine
                    results = check_ad_compliance(
                        api_key=api_key,
                        file_bytes=media_file.getvalue(),
                        file_name=media_file.name,
                        mime_type=media_file.type
                    )
                    
                    # Display Results
                    st.subheader("Analysis Results")
                    for item in results:
                        if item.get("status") == "PASS":
                            st.success(f"✅ **{item.get('rule_id')}** - PASS")
                            st.caption(item.get('reason'))
                        else:
                            st.error(f"❌ **{item.get('rule_id')}** - FAIL")
                            st.write(f"**Details:** {item.get('reason')}")
                            
                except Exception as e:
                    st.error(f"🚨 An error occurred: {e}")