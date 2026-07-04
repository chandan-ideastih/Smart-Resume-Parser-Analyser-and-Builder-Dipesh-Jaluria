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
