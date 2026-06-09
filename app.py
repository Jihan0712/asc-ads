import streamlit as st
from ai_engine import check_ad_compliance

# --- Page Config ---
st.set_page_config(page_title="ASC Ad Checker", layout="centered")

# --- Sidebar ---
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Gemini API Key", type="password")

# Dynamic Model Selection from your personal active list
model_options = [
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-3.5-flash"
]
selected_model = st.sidebar.selectbox("Select AI Model Type", model_options)

st.sidebar.markdown("---")
st.sidebar.info("💡 Tip: If you get a 429 error on one model, switch to a 'lite' version to utilize a separate free quota allocation.")

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
            with st.spinner(f"Analyzing media with {selected_model}..."):
                try:
                    # Run the engine with the chosen model
                    results = check_ad_compliance(
                        api_key=api_key,
                        file_bytes=media_file.getvalue(),
                        file_name=media_file.name,
                        mime_type=media_file.type,
                        model_name=selected_model
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