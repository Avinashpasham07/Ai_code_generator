import streamlit as st
import requests
import time  
import streamlit.components.v1 as components  

# ======== CONFIGURATION ======== #
USE_HUGGINGFACE_API = True  
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3" 
HUGGINGFACE_API_KEY = "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"  # Replace with a valid API key

API_URL = f"https://api-inference.huggingface.co/models/{MODEL_NAME}"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# ======== STREAMLIT UI SETTINGS ======== #
st.set_page_config(page_title="AI Code Generator", layout="wide")

# ======== CUSTOM DARK MODE STYLING ======== #
st.markdown("""
    <style>
    body { background-color: #1E1E1E !important; color: white !important; }
    .stTextInput>div>div>input { background: #444 !important; color: white !important; border: 2px solid red; text-align: center; }
    .stButton>button { background: linear-gradient(90deg, red, pink); color: white; border-radius: 8px; font-weight: bold; border: none; transition: 0.3s ease-in-out; width: 100%; }
    .stButton>button:hover { transform: scale(1.05); background: linear-gradient(90deg, darkred, pink); }
    .stCodeBlock { background: #222; border-radius: 8px; padding: 15px; border-left: 5px solid pink; }
    .title-container { text-align: center; font-size: 24px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ======== HISTORY STORAGE ======== #
if "history" not in st.session_state:
    st.session_state.history = []

# ======== LAYOUT ======== #
col1, col2 = st.columns([0.5, 3.5])  # Reduced left margin for better alignment

# ======== HISTORY SECTION (SIDEBAR) ======== #
st.sidebar.subheader("📜 History")
if st.session_state.history:
    selected_prompt = st.sidebar.radio("Select a prompt to view output:", [entry["prompt"] for entry in st.session_state.history])
    for entry in st.session_state.history:
        if entry["prompt"] == selected_prompt:
            st.sidebar.code(entry["response"], language="python")
else:
    st.sidebar.write("No history available yet.")

# ======== MAIN CONTENT (CENTER) ======== #
with col2:
    st.markdown("<div class='title-container'>AI Code Generator</div>", unsafe_allow_html=True)

    # User Input
    prompt = st.text_input("Enter your prompt:", placeholder="Describe what you want to generate...", max_chars=500)

    # Store generated code
    generated_code = None  

    # Generate Code Button
    if st.button("✨ Generate Code"):
        if prompt.strip():
            with st.spinner("Generating code... Please wait. ✨"):
                time.sleep(1)  

                # API Request
                payload = {"inputs": prompt, "parameters": {"max_new_tokens": 500}}
                response = requests.post(API_URL, headers=HEADERS, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and "generated_text" in data:
                        generated_code = data["generated_text"]
                    elif isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                        generated_code = data[0]["generated_text"]
                    else:
                        st.error("Unexpected API response format. Please try again.")
                else:
                    st.error(f"API Error: {response.text}")
        else:
            st.warning("Please enter a prompt before generating.")

    # Display Generated Code
    if generated_code:
        st.subheader(f"✨ Your Generated Code ✨")
        st.code(generated_code, language="python")

        # Store in history
        st.session_state.history.append({"prompt": prompt, "response": generated_code})

        # Copy Code Functionality
        safe_generated_code = generated_code.replace("`", r"\`")

        copy_code_html = f"""
        <script>
        function copyToClipboard() {{
            navigator.clipboard.writeText(`{safe_generated_code}`).then(() => {{
                alert("📋 Code copied to clipboard!");
            }}).catch(err => {{
                console.error("Copy failed:", err);
            }});
        }}
        </script>
        <button onclick="copyToClipboard()" style="padding: 12px; background: linear-gradient(90deg, red, pink); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">📋 Copy Code</button>
        """
        components.html(copy_code_html, height=50)

        # Download Code Functionality
        st.download_button(
            label="💾 Download Code",
            data=generated_code,
            file_name="generated_code.py",
            mime="text/plain"
        )
