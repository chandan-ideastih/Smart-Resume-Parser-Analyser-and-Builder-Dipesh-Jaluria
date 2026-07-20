import streamlit as st
import PyPDF2
import google.generativeai as genai
import json
import pandas as pd
import re
from fpdf import FPDF
import sqlite3

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

def generate_pdf(resume_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Helper to sanitize strings to Latin-1 for standard FPDF fonts
    def clean(text):
        if not text:
            return ""
        text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
        text = text.replace("–", "-").replace("—", "-").replace("•", "*")
        return text.encode("latin-1", "ignore").decode("latin-1")
    
    # 1. Header (Name & Contact)
    personal = resume_data.get("personal_info", {})
    name = clean(personal.get("name", "Name"))
    email = clean(personal.get("email", ""))
    phone = clean(personal.get("phone", ""))
    
    pdf.set_font("helvetica", "B", 24)
    pdf.cell(0, 10, name, new_x="LMARGIN", new_y="NEXT", align="C")
    
    pdf.set_font("helvetica", "", 10)
    contact_info = f"Email: {email}  |  Phone: {phone}"
    pdf.cell(0, 10, contact_info, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    
    # Draw a line
    pdf.set_draw_color(100, 100, 100)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # Helper to add section headers
    def add_section_header(title):
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        # Underline
        pdf.set_draw_color(150, 150, 150)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)
        
    # 2. Education
    education = resume_data.get("education", [])
    if education:
        add_section_header("EDUCATION")
        for edu in education:
            degree = clean(edu.get("degree", ""))
            inst = clean(edu.get("institution", ""))
            year = clean(edu.get("year", ""))
            
            pdf.set_font("helvetica", "B", 11)
            pdf.cell(0, 6, f"{degree}", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("helvetica", "I", 10)
            pdf.cell(0, 5, f"{inst} ({year})", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
        pdf.ln(3)
        
    # 3. Experience
    experience = resume_data.get("experience", [])
    if experience:
        add_section_header("EXPERIENCE")
        for exp in experience:
            role = clean(exp.get("role", ""))
            company = clean(exp.get("company", ""))
            duration = clean(exp.get("duration", ""))
            desc = clean(exp.get("description", ""))
            
            pdf.set_font("helvetica", "B", 11)
            pdf.cell(0, 6, f"{role}", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("helvetica", "I", 10)
            pdf.cell(0, 5, f"{company}  |  {duration}", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("helvetica", "", 10)
            pdf.multi_cell(0, 5, desc)
            pdf.ln(3)
        pdf.ln(3)
        
    # 4. Skills
    skills = resume_data.get("skills", [])
    if skills:
        add_section_header("SKILLS")
        pdf.set_font("helvetica", "", 10)
        skills_str = ", ".join(skills) if isinstance(skills, list) else skills
        pdf.multi_cell(0, 5, clean(skills_str))
        
    return pdf.output()

def display_profile_card(parsed_data):
    # Personal Info
    personal = parsed_data.get("personal_info", {}) or {}
    name = personal.get("name", "Name Not Found")
    email = personal.get("email", "Email Not Found")
    phone = personal.get("phone", "Phone Not Found")
    
    # Styled Profile Header Card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e3a8a, #3b82f6); padding: 25px; border-radius: 15px; color: white; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1)">
        <h1 style="margin: 0; color: white; font-family: 'Inter', sans-serif; font-size: 2.2rem; font-weight: 700;">{name}</h1>
        <p style="margin: 8px 0 0 0; font-size: 1.1rem; opacity: 0.9;">
            📧 {email} &nbsp;&nbsp;|&nbsp;&nbsp; 📞 {phone}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Grid Layout for Education and Experience
    col_edu, col_exp = st.columns([1, 2])
    
    with col_edu:
        st.subheader("🎓 Education")
        education = parsed_data.get("education", []) or []
        for edu in education:
            degree = edu.get("degree", "Degree")
            inst = edu.get("institution", "Institution")
            year = edu.get("year", "Year")
            st.markdown(f"""
            <div style="background-color: #f3f4f6; border-left: 4px solid #3b82f6; padding: 12px; border-radius: 0 8px 8px 0; margin-bottom: 12px;">
                <h5 style="margin: 0; font-weight: 600; color: #1f2937;">{degree}</h5>
                <p style="margin: 4px 0 0 0; font-size: 0.9rem; color: #4b5563;">{inst}</p>
                <p style="margin: 2px 0 0 0; font-size: 0.85rem; font-weight: 500; color: #9ca3af;">🗓️ {year}</p>
            </div>
            """, unsafe_allow_html=True)
            
    with col_exp:
        st.subheader("💼 Work Experience")
        experience = parsed_data.get("experience", []) or []
        for exp in experience:
            role = exp.get("role", "Role")
            company = exp.get("company", "Company")
            duration = exp.get("duration", "Duration")
            desc = exp.get("description", "")
            
            # Format description bullets if they exist
            desc_html = ""
            if desc:
                bullets = [b.strip() for b in re.split(r'[\n•\-\*]', desc) if b.strip()]
                if bullets:
                    desc_html = "<ul style='margin: 6px 0 0 0; padding-left: 20px; font-size: 0.9rem; color: #4b5563; line-height: 1.4;'>"
                    for b in bullets:
                        desc_html += f"<li style='margin-bottom: 4px;'>{b}</li>"
                    desc_html += "</ul>"
                else:
                    desc_html = f"<p style='margin: 6px 0 0 0; font-size: 0.9rem; color: #4b5563; line-height: 1.4;'>{desc}</p>"
                    
            st.markdown(f"""
            <div style="background-color: #f9fafb; border-left: 4px solid #10b981; padding: 15px; border-radius: 0 8px 8px 0; margin-bottom: 15px; border: 1px solid #e5e7eb; border-top-right-radius: 8px; border-bottom-right-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                    <h5 style="margin: 0; font-weight: 700; color: #111827;">{role}</h5>
                    <span style="font-size: 0.8rem; font-weight: 600; color: #10b981; background-color: #ecfdf5; padding: 2px 8px; border-radius: 12px;">{duration}</span>
                </div>
                <p style="margin: 4px 0 0 0; font-size: 0.95rem; font-weight: 500; color: #4b5563;">🏢 {company}</p>
                {desc_html}
            </div>
            """, unsafe_allow_html=True)
            
    # Skills section at the bottom as badges
    st.write("---")
    st.subheader("🛠️ Technical Skills")
    skills = parsed_data.get("skills", []) or []
    skills_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px;">'
    for skill in skills:
        skills_html += f'<span style="background: linear-gradient(135deg, #eff6ff, #dbeafe); color: #1e40af; border: 1px solid #bfdbfe; font-weight: 600; font-size: 0.85rem; padding: 6px 12px; border-radius: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">{skill}</span>'
    skills_html += '</div>'
    st.markdown(skills_html, unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect("resume_data.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            skills TEXT,
            education TEXT,
            experience TEXT,
            raw_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER,
            job_description TEXT,
            match_score INTEGER,
            matching_skills TEXT,
            missing_skills TEXT,
            recommendations TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        )
    """)
    conn.commit()
    conn.close()

def save_candidate(parsed_data):
    try:
        conn = sqlite3.connect("resume_data.db")
        c = conn.cursor()
        
        personal = parsed_data.get("personal_info", {}) or {}
        name = personal.get("name", "Name Not Found")
        email = personal.get("email", "Email Not Found")
        phone = personal.get("phone", "Phone Not Found")
        
        skills = parsed_data.get("skills", []) or []
        skills_str = ", ".join(skills) if isinstance(skills, list) else str(skills)
        
        edu_str = json.dumps(parsed_data.get("education", []))
        exp_str = json.dumps(parsed_data.get("experience", []))
        raw_json_str = json.dumps(parsed_data)
        
        c.execute("""
            INSERT INTO candidates (name, email, phone, skills, education, experience, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, email, phone, skills_str, edu_str, exp_str, raw_json_str))
        
        candidate_id = c.lastrowid
        conn.commit()
        conn.close()
        return candidate_id
    except Exception as e:
        st.error(f"Error saving to database: {e}")
        return None

def save_evaluation(candidate_id, job_description, analysis):
    try:
        conn = sqlite3.connect("resume_data.db")
        c = conn.cursor()
        
        score = analysis.get("match_score_percentage", 0)
        
        matching = analysis.get("matching_skills", []) or []
        matching_str = ", ".join(matching) if isinstance(matching, list) else str(matching)
        
        missing = analysis.get("missing_skills", []) or []
        missing_str = ", ".join(missing) if isinstance(missing, list) else str(missing)
        
        recs = analysis.get("recommendations", "")
        
        c.execute("""
            INSERT INTO evaluations (candidate_id, job_description, match_score, matching_skills, missing_skills, recommendations)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (candidate_id, job_description, score, matching_str, missing_str, recs))
        
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error saving evaluation: {e}")

# Initialize Database at startup
init_db()

# ==========================================
# MAIN APP UI
# ==========================================
if not api_key:
    st.warning("⚠️ Please enter your Gemini API Key in the sidebar to proceed.")
    st.stop()

# Configure GenAI with the provided key
genai.configure(api_key=api_key)

# Create Tabs for the Workflow
tab1, tab2, tab3, tab4 = st.tabs(["1. Parse Resume", "2. Analyze vs Job Description", "3. Resume Builder", "4. Recruiter Dashboard"])

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
                        
                        # Save candidate to SQLite database
                        candidate_id = save_candidate(parsed_data)
                        st.session_state['candidate_id'] = candidate_id
                        
                        # Store in session state for the next tab
                        st.session_state['parsed_resume'] = parsed_data
                        
                        # Display Extracted Data
                        display_profile_card(parsed_data)
                        
                        st.write("")
                        with st.expander("🔍 View Raw JSON Data"):
                            st.json(parsed_data)

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
                        
                        # Save evaluation to SQLite database if candidate_id is known
                        if 'candidate_id' in st.session_state:
                            save_evaluation(st.session_state['candidate_id'], job_description, analysis)
                        
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

with tab3:
    st.header("Step 3: Resume Builder")
    
    if 'parsed_resume' not in st.session_state:
        st.info("Please upload and parse a resume in Step 1 first.")
    else:
        # Load data from session state
        resume_data = st.session_state['parsed_resume']
        
        st.subheader("Edit Resume Details")
        
        # 1. Personal Info
        personal = resume_data.get("personal_info", {})
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Full Name", value=personal.get("name", ""))
        with col2:
            email = st.text_input("Email Address", value=personal.get("email", ""))
        with col3:
            phone = st.text_input("Phone Number", value=personal.get("phone", ""))
            
        # Update personal info in our local builder copy
        builder_data = {
            "personal_info": {"name": name, "email": email, "phone": phone}
        }
        
        # 2. Education
        st.write("---")
        st.subheader("Education")
        education = resume_data.get("education", [])
        builder_edu = []
        for i, edu in enumerate(education):
            st.markdown(f"**Degree #{i+1}**")
            col_deg, col_inst, col_yr = st.columns([2, 2, 1])
            with col_deg:
                deg = st.text_input(f"Degree", value=edu.get("degree", ""), key=f"edu_deg_{i}")
            with col_inst:
                inst = st.text_input(f"Institution", value=edu.get("institution", ""), key=f"edu_inst_{i}")
            with col_yr:
                yr = st.text_input(f"Year", value=edu.get("year", ""), key=f"edu_yr_{i}")
            builder_edu.append({"degree": deg, "institution": inst, "year": yr})
        builder_data["education"] = builder_edu
        
        # 3. Experience
        st.write("---")
        st.subheader("Experience")
        experience = resume_data.get("experience", [])
        builder_exp = []
        for i, exp in enumerate(experience):
            st.markdown(f"**Job #{i+1}**")
            col_role, col_comp, col_dur = st.columns([2, 2, 1])
            with col_role:
                role = st.text_input(f"Role", value=exp.get("role", ""), key=f"exp_role_{i}")
            with col_comp:
                comp = st.text_input(f"Company", value=exp.get("company", ""), key=f"exp_comp_{i}")
            with col_dur:
                dur = st.text_input(f"Duration", value=exp.get("duration", ""), key=f"exp_dur_{i}")
            desc = st.text_area(f"Description / Bullet Points", value=exp.get("description", ""), key=f"exp_desc_{i}", height=100)
            builder_exp.append({"role": role, "company": comp, "duration": dur, "description": desc})
        builder_data["experience"] = builder_exp
        
        # 4. Skills
        st.write("---")
        st.subheader("Skills")
        skills_list = resume_data.get("skills", [])
        if isinstance(skills_list, list):
            skills_str = ", ".join(skills_list)
        else:
            skills_str = str(skills_list)
        
        skills_input = st.text_area("Skills (comma-separated)", value=skills_str, height=80)
        builder_data["skills"] = [s.strip() for s in skills_input.split(",") if s.strip()]
        
        # Generate & Download Button
        st.write("---")
        st.subheader("Export Resume")
        
        if st.button("Preview / Update PDF", type="secondary"):
            st.success("Resume preview updated! Click download button below to export.")
            
        try:
            pdf_bytes = generate_pdf(builder_data)
            st.download_button(
                label="📥 Download Resume PDF",
                data=pdf_bytes,
                file_name=f"{name.replace(' ', '_')}_Resume.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error generating PDF: {e}")

with tab4:
    st.header("Step 4: Recruiter Dashboard")
    
    # Read all candidates from the database
    try:
        conn = sqlite3.connect("resume_data.db")
        candidates_df = pd.read_sql_query("SELECT id, name, email, phone, skills, created_at FROM candidates ORDER BY id DESC", conn)
        conn.close()
    except Exception as e:
        st.error(f"Error loading database: {e}")
        candidates_df = pd.DataFrame()
        
    if candidates_df.empty:
        st.info("No candidates saved in the database yet. Go to Step 1 to parse a resume.")
    else:
        st.subheader("Saved Candidates")
        # Search box
        search_query = st.text_input("🔍 Search Candidates by Name, Email, or Skills:")
        if search_query:
            filtered_df = candidates_df[
                candidates_df['name'].str.contains(search_query, case=False, na=False) |
                candidates_df['email'].str.contains(search_query, case=False, na=False) |
                candidates_df['skills'].str.contains(search_query, case=False, na=False)
            ]
        else:
            filtered_df = candidates_df
            
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        # Select Candidate to View
        candidate_ids = filtered_df['id'].tolist()
        candidate_names = filtered_df['name'].tolist()
        options = {candidate_ids[i]: f"{candidate_names[i]} (ID: {candidate_ids[i]})" for i in range(len(candidate_ids))}
        
        selected_id = st.selectbox(
            "Select a candidate to view full profile and past evaluations:",
            options=list(options.keys()),
            format_func=lambda x: options[x]
        )
        
        if selected_id:
            # Load candidate details
            conn = sqlite3.connect("resume_data.db")
            c = conn.cursor()
            c.execute("SELECT raw_json FROM candidates WHERE id = ?", (selected_id,))
            raw_json = c.fetchone()[0]
            candidate_data = json.loads(raw_json)
            
            # Load past evaluations
            eval_df = pd.read_sql_query("""
                SELECT created_at as 'Date', match_score as 'Match Score (%)', matching_skills as 'Matching Skills', 
                       missing_skills as 'Missing Skills', recommendations as 'Recommendations'
                FROM evaluations WHERE candidate_id = ? ORDER BY id DESC
            """, conn, params=(selected_id,))
            conn.close()
            
            # Display Candidate Details
            st.write("---")
            st.subheader(f"Candidate Profile: {candidate_data.get('personal_info', {}).get('name', '')}")
            display_profile_card(candidate_data)
            
            # Display Evaluations History
            st.write("---")
            st.subheader("📈 Past ATS Match Evaluations")
            if eval_df.empty:
                st.info("No evaluations run for this candidate yet. Go to Step 2 to analyze against a Job Description.")
            else:
                for idx, row in eval_df.iterrows():
                    with st.expander(f"Match Score: {row['Match Score (%)']}% | Date: {row['Date']}"):
                        st.metric(label="Match Score", value=f"{row['Match Score (%)']}%")
                        col_m, col_mi = st.columns(2)
                        with col_m:
                            st.success("✅ Matching Skills")
                            st.write(row['Matching Skills'])
                        with col_mi:
                            st.error("❌ Missing Skills")
                            st.write(row['Missing Skills'])
                        st.info(f"💡 Recommendations:\n{row['Recommendations']}")