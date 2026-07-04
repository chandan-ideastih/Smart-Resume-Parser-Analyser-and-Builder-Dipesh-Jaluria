# 📄 Smart Resume Parser & Analyzer

An AI-powered web application built with Streamlit that extracts text from resumes (PDFs) and uses Google's Gemini AI to parse the unstructured data into structured JSON. It also features an Applicant Tracking System (ATS) module to compare the parsed resume against a target job description, providing a match score and actionable feedback.

## 🚀 Features

* **PDF Text Extraction:** Reads and extracts raw text from uploaded resume PDFs using `PyPDF2`.
* **Intelligent AI Parsing:** Uses `gemini-2.5-flash` to convert raw resume text into structured JSON format (Personal Info, Education, Experience, Skills).
* **ATS Match Scoring:** Analyzes the structured resume against a user-provided job description to calculate a compatibility percentage.
* **Skill Gap Analysis:** Highlights exact matching skills and identifies critical missing keywords.
* **Actionable Insights:** Provides AI-driven recommendations to improve the resume for the specific role.

## 🛠️ Tech Stack

* **Language:** Python
* **Frontend Framework:** Streamlit
* **AI Model:** Google Generative AI (Gemini 2.5 Flash)
* **Data Processing:** Pandas, JSON, Regular Expressions (Regex)
* **PDF Processing:** PyPDF2

## ⚙️ Installation & Setup

To run this project locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
   cd YOUR_REPOSITORY_NAME
