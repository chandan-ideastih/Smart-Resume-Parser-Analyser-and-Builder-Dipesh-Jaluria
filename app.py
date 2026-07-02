import streamlit as st
import PyPDF2
import google.generativeai as genai
import json
import pandas as pd
import re

# ==========================================
# CONFIGURATION & PAGE SETUP
# ==========================================
st.set_page_config(page_title="Smart Resume AI", page_icon="📄", layout="wide")
st.title("📄 Smart Resume Parser & Analyzer")

# Sidebar for API Key configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Google Gemini API Key:", type="password")
    st.markdown("""
    **How to get a key:**
    1. Go to [Google AI Studio](https://aistudio.google.com/)
    2. Click 'Get API Key'
    3. Create a new key and paste it here.
    """)
    st.divider()
    st.write("Built with Streamlit & Gemini AI")

# ==========================================
# CORE FUNCTIONS
# ==========================================
def extract_text_from_pdf(uploaded_file):
    """Extracts raw text from an uploaded PDF file."""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

def clean_json_response(raw_text):
    """Cleans markdown formatting from Gemini's JSON response."""
    # Remove markdown code blocks if the model wrapped the JSON
    cleaned = re.sub(r'```json\n?', '', raw_text)
    cleaned = re.sub(r'```\n?', '', cleaned)
    return cleaned.strip()

def parse_resume(text):
    """Uses Gemini to parse unstructured resume text into a structured JSON object."""
    prompt = f"""
    You are an expert HR Parser. Extract the following information from the resume text provided below. 
    Return the output STRICTLY as a valid JSON object without any additional markdown or text.
    
    Expected JSON Structure:
    {{
      "personal_info": {{"name": "", "email": "", "phone": ""}},
      "education": [{{"degree": "", "institution": "", "year": ""}}],
      "experience": [{{"role": "", "company": "", "duration": "", "description": ""}}],
      "skills": ["skill1", "skill2"]
    }}
    
    Resume Text:
    {text}
    """
    
    # Updated to the newer supported Gemini model
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    
    try:
        cleaned_json_string = clean_json_response(response.text)
        return json.loads(cleaned_json_string)
    except json.JSONDecodeError:
        st.error("Failed to parse the AI's response into JSON. Please try again.")
        st.write("Raw Output:", response.text)
        return None

def analyze_resume(resume_json, job_desc):
    """Uses Gemini to compare parsed resume data against a Job Description."""
    prompt = f"""
    You are an expert Applicant Tracking System (ATS). 
    Compare the following Parsed Resume JSON against the provided Job Description.
    
    Parsed Resume Data: {json.dumps(resume_json)}
    Job Description: {job_desc}
    
    Return the output STRICTLY as a valid JSON object without any additional markdown or text.
    
    Expected JSON Structure:
    {{
      "match_score_percentage": 85,
      "matching_skills": ["skill1", "skill2"],
      "missing_skills": ["skill3", "skill4"],
      "recommendations": "Add more keywords related to X. Rephrase Y to highlight Z."
    }}
    """
    
    # Updated to the newer supported Gemini model
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    
    try:
        cleaned_json_string = clean_json_response(response.text)
        return json.loads(cleaned_json_string)
    except json.JSONDecodeError:
        st.error("Failed to generate analysis.")
        return None

# ==========================================
# MAIN APP UI
# ==========================================
if not api_key:
    st.warning("⚠️ Please enter your Gemini API Key in the sidebar to proceed.")
    st.stop()

# Configure GenAI with the provided key
genai.configure(api_key=api_key)

# Create Tabs for the Workflow
tab1, tab2 = st.tabs(["1. Parse Resume", "2. Analyze vs Job Description"])

with tab1:
    st.header("Step 1: Upload & Extract")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("Extract & Parse Data", type="primary"):
            with st.spinner("Extracting text and calling AI model..."):
                raw_text = extract_text_from_pdf(uploaded_file)
                
                if raw_text:
                    parsed_data = parse_resume(raw_text)
                    
                    if parsed_data:
                        st.success("Successfully Parsed Resume!")
                        
                        # Store in session state for the next tab
                        st.session_state['parsed_resume'] = parsed_data
                        
                        # Display Extracted Data
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("Extracted JSON Data")
                            st.json(parsed_data)
                        with col2:
                            st.subheader("Skills Found")
                            skills_df = pd.DataFrame(parsed_data.get('skills', []), columns=["Skills"])
                            st.dataframe(skills_df, use_container_width=True)

with tab2:
    st.header("Step 2: ATS Match Scoring")
    
    if 'parsed_resume' not in st.session_state:
        st.info("Please upload and parse a resume in Step 1 first.")
    else:
        job_description = st.text_area("Paste the Target Job Description here:", height=200)
        
        if st.button("Analyze Match", type="primary"):
            if not job_description.strip():
                st.error("Please provide a Job Description.")
            else:
                with st.spinner("Analyzing resume against Job Description..."):
                    analysis = analyze_resume(st.session_state['parsed_resume'], job_description)
                    
                    if analysis:
                        st.subheader("Analysis Results")
                        
                        score = analysis.get('match_score_percentage', 0)
                        
                        # Display Score beautifully
                        metric_col, _ = st.columns([1, 3])
                        with metric_col:
                            st.metric(label="ATS Match Score", value=f"{score}%")
                        
                        st.progress(score / 100.0)
                        
                        # Display Skills Analysis
                        col_match, col_miss = st.columns(2)
                        with col_match:
                            st.success("✅ Matching Skills")
                            for skill in analysis.get('matching_skills', []):
                                st.write(f"- {skill}")
                                
                        with col_miss:
                            st.error("❌ Missing Skills")
                            for skill in analysis.get('missing_skills', []):
                                st.write(f"- {skill}")
                                
                        st.divider()
                        st.subheader("💡 Suggestions for the Builder Phase")
                        st.info(analysis.get('recommendations', 'No recommendations provided.'))