# Smart Resume AI Parser & Analyzer 📄🤖

An AI-powered web application that extracts key information from resume PDFs and compares them against target job descriptions using Google Gemini LLMs. It features semantic parsing, structured data extraction, and deep ATS (Applicant Tracking System) matching metrics.

---

## 🚀 Features

### 1. Resume Parser & Extractor
* **PDF Text Extraction**: Uses `PyPDF2` to read raw text from multi-page PDFs.
* **Semantic parsing**: Leverages `gemini-2.5-flash` to extract unstructured details into clean, structured JSON containing:
  * **Personal Information**: Name, Email, Phone
  * **Education**: Degree, Institution, Graduation Year
  * **Experience**: Job role, Company, Duration, Description
  * **Skills**: Key professional tags
* **Skills Visualization**: Automatically displays skills in a clean, searchable table using Pandas.

### 2. ATS Match Scoring & Analytics
* **ATS Score Calculation**: Compares the parsed resume data directly against a Job Description to generate a percentage match score.
* **Skill Gap Analysis**: Shows matching and missing skills to help candidates identify gaps.
* **Tailored Suggestions**: Provides structured advice on how to improve the resume relative to the role.

---

## 🛠️ Tech Stack
* **Frontend UI**: [Streamlit](https://streamlit.io/) (Python-based dashboard framework)
* **LLM Engine**: [Google Generative AI SDK](https://aistudio.google.com/) (Gemini 2.5 Flash)
* **PDF Reader**: `PyPDF2`
* **Data Processing**: `Pandas`

---

## 💻 How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/chandan-ideastih/Smart-Resume-Parser-Analyser-and-Builder-Dipesh-Jaluria.git
cd Smart-Resume-Parser-Analyser-and-Builder-Dipesh-Jaluria
```

### 2. Set Up Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
venv\Scripts\activate  # On Windows PowerShell
# source venv/bin/activate  # On macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit App
```bash
streamlit run app.py
```

### 5. Setup your API Key
* Open the app in your browser (usually `http://localhost:8501`).
* Go to the sidebar and input your **Google Gemini API Key**.
* Get a key for free at [Google AI Studio](https://aistudio.google.com/).

---

## 📂 Project Structure
```
├── app.py              # Main application source code
├── requirements.txt    # Project dependencies
├── .gitignore          # Git exclusion rules (ignores venv, .env, pycache)
└── Readme.md           # Project documentation
```
