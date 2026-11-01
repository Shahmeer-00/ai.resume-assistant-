import os
import json
import streamlit as st
from pypdf import PdfReader
from docx import Document
from google import genai

# Page Configuration
st.set_page_config(
    page_title="ATS Resume Checker & Optimizer",
    page_icon="📄",
    layout="wide"
)

# Text Extraction Functions
def extract_text_from_pdf(file):
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return ""

def extract_text_from_docx(file):
    try:
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs if para.text])
    except Exception as e:
        st.error(f"Error reading DOCX file: {e}")
        return ""

def extract_text(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    return ""

# AI Evaluation Function (Updated Model)
def analyze_resume(resume_text, job_description, api_key):
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an expert HR Specialist and Applicant Tracking System (ATS) Auditor.
    Evaluate the following resume against the job description (if provided) or against general industry standards.

    Resume Text:
    {resume_text}

    Job Description (Optional):
    {job_description if job_description else "Not provided (Evaluate against generic industry standards for the detected role)"}

    Return your analysis strictly in JSON format matching this exact schema:
    {{
        "ats_score": <number between 0 and 100>,
        "score_breakdown": {{
            "formatting": <number 0-100>,
            "keyword_match": <number 0-100>,
            "relevance": <number 0-100>
        }},
        "strengths": [<list of strings>],
        "critical_improvements": [<list of strings>],
        "missing_keywords": [<list of strings>]
    }}
    Do not include markdown code block formatting like ```json. Return valid JSON only.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",  # Updated to current supported model
        contents=prompt
    )
    return response.text

# Streamlit User Interface
st.title("📄 ATS Resume Checker & Optimizer")
st.write("Upload your resume, paste a target job description, and get instant feedback on your ATS compatibility.")

# Sidebar for API Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    env_api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    
    if env_api_key:
        api_key = env_api_key
        st.success("Gemini API Key detected.")
    else:
        api_key = st.text_input("Enter Gemini API Key:", type="password")
        st.caption("Get an API key from Google AI Studio.")

# Main Application Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
    
    st.subheader("2. Target Job Description (Optional)")
    job_description = st.text_area("Paste the job description to get tailored ATS keyword scoring:", height=200)

    analyze_button = st.button("🚀 Analyze Resume", use_container_width=True)

with col2:
    st.subheader("3. Analysis Results")
    
    if analyze_button:
        if not api_key:
            st.error("Please provide a valid Gemini API Key in the sidebar or app secrets.")
        elif not uploaded_file:
            st.warning("Please upload a PDF or DOCX resume.")
        else:
            with st.spinner("Extracting text and scanning with Gemini AI..."):
                resume_text = extract_text(uploaded_file)
                
                if not resume_text.strip():
                    st.error("Could not extract readable text from the file. Ensure the file is not a scanned image PDF.")
                else:
                    try:
                        raw_result = analyze_resume(resume_text, job_description, api_key)
                        
                        # Clean up formatting wrappers if returned by the model
                        clean_json = raw_result.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                        data = json.loads(clean_json)

                        # Render Overall Score
                        score = data.get("ats_score", 0)
                        st.metric(label="Overall ATS Score", value=f"{score} / 100")
                        st.progress(score / 100)

                        # Render Breakdown
                        st.markdown("### Score Breakdown")
                        bd = data.get("score_breakdown", {})
                        b_col1, b_col2, b_col3 = st.columns(3)
                        b_col1.metric("Formatting", f"{bd.get('formatting', 0)}%")
                        b_col2.metric("Keywords", f"{bd.get('keyword_match', 0)}%")
                        b_col3.metric("Relevance", f"{bd.get('relevance', 0)}%")

                        # Render Lists
                        st.markdown("### Key Strengths")
                        for s in data.get("strengths", []):
                            st.write(f"- ✅ {s}")

                        st.markdown("### Areas for Improvement")
                        for imp in data.get("critical_improvements", []):
                            st.write(f"- ⚠️ {imp}")

                        st.markdown("### Missing Keywords")
                        missing = data.get("missing_keywords", [])
                        if missing:
                            st.write(", ".join([f"`{kw}`" for kw in missing]))
                        else:
                            st.write("No major keywords missing.")

                    except json.JSONDecodeError:
                        st.error("Failed to parse AI model output into JSON. Raw output:")
                        st.write(raw_result)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                        def analyze_resume(resume_text, job_description, api_key):
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an expert HR Specialist and Applicant Tracking System (ATS) Auditor.
    Evaluate the following resume against the job description (if provided) or against general industry standards.

    Resume Text:
    {resume_text}

    Job Description (Optional):
    {job_description if job_description else "Not provided (Evaluate against generic industry standards for the detected role)"}

    Return your analysis strictly in JSON format matching this exact schema:
    {{
        "ats_score": <number between 0 and 100>,
        "score_breakdown": {{
            "formatting": <number 0-100>,
            "keyword_match": <number 0-100>,
            "relevance": <number 0-100>
        }},
        "strengths": [<list of strings>],
        "critical_improvements": [<list of strings>],
        "missing_keywords": [<list of strings>]
    }}
    Do not include markdown code block formatting like ```json. Return valid JSON only.
    """

    response = client.models.generate_content(
        model="gemini-3.8-flash",  # <--- Updated to the required current model
        contents=prompt
    )
    return response.text
