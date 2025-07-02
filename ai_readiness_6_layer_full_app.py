
import streamlit as st
import openai
import os
from io import BytesIO
from fpdf import FPDF

# Load OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", ""))

if not openai.api_key:
    st.error("🔐 OpenAI API key not found. Please add it in secrets.toml or environment variable.")
    st.stop()

# Create the Assistant if not already created
if "assistant_id" not in st.session_state:
    with st.spinner("🧠 Creating AI Readiness Assistant..."):
        assistant = openai.beta.assistants.create(
            name="AI Readiness Advisor",
            instructions=(
                "You are an AI strategy advisor. The user will upload a CSV or XLSX containing scores for AI maturity "
                "across six pillars (Infrastructure, Orchestration, Knowledge, Model, Agent, Governance). "
                "Your job is to:"
                "1. Analyze per-pillar scores"
                "2. Identify weaknesses"
                "3. Recommend specific, actionable next steps per pillar"
                "4. Summarize overall maturity"
                "Be precise, avoid generalities, and tailor suggestions to the score context (0–4)."
            ),
            model="gpt-4o",
            tools=[{"type": "code_interpreter"}]
        )
        st.session_state.assistant_id = assistant.id
        st.success("✅ Assistant created with ID: " + assistant.id)

st.title("AI Readiness Assessment with Assistant")

st.markdown("Upload your AI maturity score file (CSV/XLSX) and receive assistant-driven insights.")

uploaded_file = st.file_uploader("Upload File", type=["csv", "xlsx"])

if uploaded_file:
    st.success("File uploaded. Ready to process with assistant.")
    st.write("📎 Assistant ID:", st.session_state.get("assistant_id"))
    # You can add logic here to send the file to assistant for processing
