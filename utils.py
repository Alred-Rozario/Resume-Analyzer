import os
import re
import PyPDF2
import docx2txt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from google import genai
from dotenv import load_dotenv
try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

# Load environment variables from .env file
load_dotenv()

def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return ""

def extract_text_from_docx(file):
    try:
        text = docx2txt.process(file)
        return text
    except Exception as e:
        return ""

def clean_text(text):
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = text.lower()
    return text

def match_skills(resume_text, job_description):
    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(job_description)
    
    if not resume_clean or not jd_clean:
        return {
            "similarity_score": 0.0,
            "matched_skills": [],
            "missing_skills": []
        }

    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        vectors = vectorizer.fit_transform([resume_clean, jd_clean])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    except ValueError:
        similarity = 0.0
    
    vectorizer_jd = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    try:
        vectorizer_jd.fit([jd_clean])
        jd_keywords = set(vectorizer_jd.get_feature_names_out())
    except ValueError:
        jd_keywords = set()
    
    vectorizer_resume = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    try:
        vectorizer_resume.fit([resume_clean])
        resume_keywords = set(vectorizer_resume.get_feature_names_out())
    except ValueError:
        resume_keywords = set()
    
    matched_skills = list(jd_keywords.intersection(resume_keywords))
    missing_skills = list(jd_keywords.difference(resume_keywords))
    
    matched_skills.sort(key=len, reverse=True)
    missing_skills.sort(key=len, reverse=True)
    
    return {
        "similarity_score": round(similarity * 100, 2),
        "matched_skills": matched_skills[:20],
        "missing_skills": missing_skills[:20]
    }

def get_api_key():
    key = os.getenv("GEMINI_API_KEY")
    if not key or key.strip() == "your_api_key_here":
        return None
    return key.strip()

def safe_generate(prompt):
    """Helper to generate content using the new google-genai SDK with automatic resilient model fallback."""
    api_key = get_api_key()
    if not api_key:
        return "⚠️ Error: Please configure your GEMINI_API_KEY inside the .env file in the project folder."
        
    import httpx
    try:
        custom_httpx_client = httpx.Client(timeout=30.0, verify=False)
        client = genai.Client(api_key=api_key, http_options={'httpx_client': custom_httpx_client})
        
        # Test reliable available models in order of latency and availability
        models_to_try = ['gemini-3.1-flash-lite', 'gemini-3.5-flash-lite', 'gemini-3.8-flash']
        last_error = None
        for m in models_to_try:
            try:
                response = client.models.generate_content(
                    model=m,
                    contents=prompt,
                )
                if response and response.text:
                    return response.text
            except Exception as model_err:
                last_error = model_err
                continue
                
        return f"Error communicating with AI: {str(last_error)}"
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"

def get_resume_suggestions(resume_text, job_desc):
    """Uses Gemini API to provide actionable feedback on a resume."""
    prompt = f"""
    You are an expert technical recruiter and resume writer.
    Review the following resume against the provided job description.
    Give exactly 3 specific, actionable suggestions on how the candidate can improve their resume for this specific role.
    Format your response cleanly using markdown bullets. Do not include fluff.
    
    Job Description:
    {job_desc}
    
    Resume:
    {resume_text}
    """
    return safe_generate(prompt)

def generate_resume(details):
    """Uses Gemini API to generate a resume from scratch based on user inputs."""
    prompt = f"""
    You are an expert resume writer. The user has provided rough details about their career.
    Generate a highly professional, ATS-friendly resume in Markdown format.
    Make sure to elaborate on their experience to create strong, impact-driven bullet points (starting with action verbs).
    Ensure the resume is tailored toward their Target Role.
    
    User Details:
    Name: {details.get('name', 'N/A')}
    Contact Info: {details.get('contact', 'N/A')}
    Target Role: {details.get('target_role', 'N/A')}
    Core Skills: {details.get('skills', 'N/A')}
    Education: {details.get('education', 'N/A')}
    Experience Details: {details.get('experience', 'N/A')}
    """
    return safe_generate(prompt)

def generate_cover_letter(resume_text, job_desc):
    """Uses Gemini API to generate a cover letter based on a resume and job description."""
    prompt = f"""
    You are an expert career coach and professional writer.
    Generate a compelling, highly professional cover letter for the candidate based on their resume and the target job description.
    The cover letter should highlight the most relevant skills and experiences from the resume that align with the job description.
    Keep it concise, confident, and engaging. Return the cover letter in Markdown format.
    
    Job Description:
    {job_desc}
    
    Candidate Resume:
    {resume_text}
    """
    return safe_generate(prompt)

def discover_career_opportunities(resume_text):
    """
    Analyzes any resume across any discipline or stream (Commerce, Business Administration,
    Arts, Science, Engineering, Law, Healthcare, etc.) without requiring a job description.
    Identifies degree/background, core strengths, and suggests top suitable job roles.
    """
    prompt = f"""
    You are a world-class Executive Career Advisor, Senior Talent Recruiter, and Career Strategist.
    You evaluate candidates from ALL fields and academic backgrounds, including:
    - Commerce & Finance (B.Com, M.Com, CA, CFA, Banking, Accounts, Taxation)
    - Business & Management (BBA, MBA, Operations, Marketing, HR, Strategy, Sales)
    - Arts, Humanities & Social Sciences (BA, Economics, Psychology, Journalism, Literature, Media)
    - Science & Healthcare (B.Sc, M.Sc, Biotech, Nursing, Pharmacy, Medicine, Chemistry, Physics)
    - Technology & Engineering (B.Tech, BE, BCA, MCA, Data Science, CS, Civil, Mechanical, Electrical)
    - Law, Design, Hospitality, Media, and Vocational Certifications.

    Analyze the candidate's resume below carefully:
    ---
    RESUME:
    {resume_text}
    ---

    Provide a comprehensive, encouraging, and highly actionable Career Opportunity & Job Fit Report.
    Format your response in beautiful GitHub Markdown following this exact structure:

    ### 🎓 Candidate Profile Intelligence
    - **Identified Domain / Industry:** [e.g. Commerce & Corporate Finance / Digital Marketing & Sales / Healthcare Administration / Software Engineering]
    - **Detected Education & Background:** [e.g. Bachelor of Commerce (B.Com) / BBA in Marketing / B.Tech / Self-Taught Professional]
    - **Experience Tier:** [e.g. Fresh Graduate / Early Career (1-3 yrs) / Mid-Senior (5+ yrs)]
    - **Top Transferable Strengths:** [List 4-5 key skills, tools, or domain knowledge observed from the resume]

    ---

    ### 💼 Recommended Job Roles & Career Matches
    Identify the TOP 4 most suitable and realistic job roles the candidate is capable of performing right now or with minor preparation.
    For each role, format as:

    #### 1. [Job Title] (e.g. Financial Analyst / Operations Associate / Digital Marketer / Business Development Associate)
    - **Capability & Readiness Score:** [e.g. 92% Match]
    - **Why You Are Qualified:** [Explain specific skills, coursework, projects, or background from their resume that qualify them]
    - **Core Daily Responsibilities:** [Brief description of what they will do in this role]
    - **High-Impact Skills to Level Up:** [1-2 high-value tools/certifications to learn to get hired faster and earn a higher salary, e.g. Advanced Excel, PowerBI, Tally ERP, Google Analytics, Salesforce, Python, etc.]
    - **Estimated Market Compensation:** [Entry/standard market salary range for this role]

    [Repeat for Role 2, 3, and 4]

    ---

    ### 🚀 Immediate Action Plan & Interview Readiness
    - Provide 3 concrete, high-leverage steps the candidate can take this week to land interviews in their recommended roles (e.g., specific certifications, resume tweaks, portfolio items, or networking strategy).
    """
    return safe_generate(prompt)

def evaluate_universal_resume(resume_text):
    """
    Evaluates resume health, detected keywords, and overall ATS completeness
    when no job description is provided. Supports all fields (Commerce, Arts, Science, Tech, Business).
    """
    word_count = len(resume_text.split())
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+', resume_text))
    has_phone = bool(re.search(r'(\+?\d[\d\s\-\(\)\.]{7,15}\d)', resume_text))
    
    text_lower = resume_text.lower()
    sections = {
        "Experience / Internships": bool(re.search(r'(experience|employment|work history|internship|projects|practical)', text_lower)),
        "Education / Degree": bool(re.search(r'(education|degree|university|college|b\.?com|bba|b\.?tech|b\.?sc|ba|mba|diploma|school)', text_lower)),
        "Skills / Competencies": bool(re.search(r'(skills|competencies|proficiencies|expertise|tools|abilities)', text_lower)),
        "Contact Information": bool(has_email or has_phone)
    }
    
    score = 45
    if word_count >= 150: score += 10
    if word_count >= 300: score += 10
    if has_email: score += 10
    if has_phone: score += 10
    if sections["Education / Degree"]: score += 10
    if sections["Skills / Competencies"]: score += 5
    score = min(score, 95)
    
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=25)
    try:
        clean = clean_text(resume_text)
        vectorizer.fit([clean])
        keywords = list(vectorizer.get_feature_names_out())
    except Exception:
        keywords = []
        
    return {
        "readiness_score": score,
        "word_count": word_count,
        "has_email": has_email,
        "has_phone": has_phone,
        "sections": sections,
        "extracted_keywords": [k.title() for k in keywords if len(k) > 2][:16]
    }

def create_pdf(text):
    if not FPDF:
        return b""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    # Replace characters that latin-1 cannot handle easily
    text = text.encode('latin-1', 'replace').decode('latin-1')
    
    for line in text.split('\n'):
        pdf.multi_cell(0, 5, txt=line, align='L')
        
    return pdf.output(dest='S').encode('latin-1')


