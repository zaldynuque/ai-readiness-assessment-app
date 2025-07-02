
import streamlit as st
import openai
import time
import tempfile
import os
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="AI Readiness Assessment with Assistant", layout="wide")

st.title("🧠 AI Readiness Assessment with Assistant")
st.markdown("Upload your AI maturity score file (CSV/XLSX) and receive assistant-driven insights.")

# Secure your OpenAI API Key
openai.api_key = st.secrets["OPENAI_API_KEY"]
assistant_id = st.secrets["OPENAI_ASSISTANT_ID"]

# File Upload
uploaded_file = st.file_uploader("Upload File", type=["csv", "xlsx"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        file_path = tmp_file.name

    st.success("File uploaded. Ready to process with assistant.")

    # Step 1: Create a thread
    thread = openai.beta.threads.create()

    # Step 2: Upload file to OpenAI
    with open(file_path, "rb") as f:
        file_upload = openai.files.create(file=f, purpose="assistants")

    # ✅ Ensure file upload is valid
    if not file_upload or not getattr(file_upload, "id", None):
        st.error("❌ File upload failed. Cannot proceed.")
        st.stop()
        
    st.write(f"Uploaded file ID: {file_upload.id}")
    
    # Step 3: Attach file to a message
    try:
        file_id = str(file_upload.id)
        if not file_id:
            raise ValueError("Empty file ID returned from upload.")

        st.write("📎 Attaching file to assistant thread...")
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content="Please analyze this AI readiness report.",
            attachments=[
                {
                    "file_id": file_upload.id,
                    "tools": [{"type": "code_interpreter"}]
                }
            ]
        )

    except Exception as e:
        st.error(f"❌ Failed to attach file to message: {e}")
        st.stop()

    # Step 4: Run the assistant
    run = openai.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant_id
    )

    # Step 5: Poll until completion
    with st.spinner("🔍 Assistant is analyzing your report..."):
        while True:
            run_status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                st.error("❌ Assistant failed to process the report.")
                st.stop()
            time.sleep(2)

    # Step 6: Retrieve assistant response
    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            st.subheader("✅ Assistant Insights")
            st.markdown(msg.content[0].text.value)

            # PDF export
            # Use a UTF-8 compatible font like DejaVuSans (install via apt/pip if needed)
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            if not os.path.exists(font_path):
                st.error("❌ Unicode font not found. Please install 'DejaVuSans.ttf' or provide a valid path.")
            else:
                pdf = FPDF()
                pdf.add_page()
                pdf.add_font("DejaVu", fname=font_path, uni=True)
                pdf.set_font("DejaVu", size=12)

                for line in msg.content[0].text.value.split("\n"):
                    pdf.multi_cell(0, 10, txt=line)

                pdf_buffer = BytesIO()
                pdf_output = pdf.output(dest='S').encode('latin-1', errors='replace')
                pdf_buffer.write(pdf_output)
                # pdf.output(pdf_buffer)
                pdf_buffer.seek(0)

                st.download_button(
                    label="📄 Download Insights (PDF)",
                    data=pdf_buffer,
                    file_name="ai_readiness_insights.pdf",
                    mime="application/pdf"
                )
            break
