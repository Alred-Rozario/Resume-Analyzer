# Resume-Analyzer

An enterprise-grade, AI-powered Career Intelligence Platform built with Streamlit, Python, and the Google Gemini API.

## 🚀 Key Features

- **📈 Resume Analyzer Pro**:
  - Semantic resume parsing (PDF and DOCX) against target job descriptions.
  - Interactive Plotly match compatibility gauge scoring.
  - Keyword extraction highlighting matched vs. missing competency terms.
  - Recruiter-level actionable AI suggestions.

- **✨ AI Resume Builder**:
  - Generate ATS-optimized resumes from scratch or import LinkedIn profile exports.
  - Integrated in-browser Markdown live editor.
  - One-click downloads for Markdown (`.md`) and formatted PDF (`.pdf`).

- **✉️ Cover Letter Generator**:
  - Automatically drafts tailored, high-converting cover letters aligning your experience with specific role requirements.
  - Includes real-time editing and PDF export.

- **💼 Live Job Market & Compatibility**:
  - Explore curated opportunities across AI, Engineering, and Product.
  - Real-time role filtering and compatibility match scoring.
  - One-click application simulation.

- **📊 Career Intelligence Dashboard**:
  - Personal document management tracking generation history and compatibility metrics.
  - Integrated SQLite user authentication system.
  - Interactive 1-click Demo Mode with pre-populated candidate data (Alex Morgan - Senior AI Engineer).

---

## 🛠️ Tech Stack

- **Framework**: Streamlit
- **AI Model**: Google Gemini API (`gemini-1.5-flash`)
- **Document Processing**: PyPDF2, docx2txt, fpdf2, markdown
- **NLP & Scoring**: Scikit-Learn (TF-IDF vectorizer, Cosine Similarity)
- **Data Visualization**: Plotly
- **Database & Auth**: SQLite3 with SHA-256 password hashing

---

## 📦 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Alred-Rozario/Resume-Analyzer.git
   cd Resume-Analyzer
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your API Key**:
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Run the Streamlit application**:
   ```bash
   streamlit run app.py
   ```

---

## 📄 License

This project is licensed under the MIT License.
