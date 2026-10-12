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
    """Helper to generate content using the new google-genai SDK."""
    api_key = get_api_key()
    if not api_key:
        return "⚠️ Error: Please configure your GEMINI_API_KEY inside the .env file in the project folder."
        
    import httpx
    try:
        # Disable SSL verification to bypass potential corporate proxy/VPN teardowns
        custom_httpx_client = httpx.Client(verify=False)
        
        # If the key provided is an OAuth token (e.g. from an enterprise Google Workspace)
        if not api_key.startswith("AIza"):
            custom_httpx_client.headers["Authorization"] = f"Bearer {api_key}"
            # Pass a dummy key to bypass the SDK's internal missing-key validation
            client = genai.Client(api_key="dummy_key", http_options={'httpx_client': custom_httpx_client})
        else:
            client = genai.Client(api_key=api_key, http_options={'httpx_client': custom_httpx_client})
        
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        return response.text
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

