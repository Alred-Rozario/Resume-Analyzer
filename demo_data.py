"""
Demo data and sample assets for Resume Analyzer Pro.
Provides pre-populated resumes, job descriptions, live jobs catalog, and history.
"""

import sqlite3
import db_auth as auth

SAMPLE_RESUME_TEXT = """# Alex Morgan
**Senior Full-Stack & AI Engineer**  
San Francisco, CA | alex.morgan@email.com | +1 (555) 382-9011 | linkedin.com/in/alexmorgan-demo | github.com/alexmorgan-ai

---

### Executive Summary
High-impact Senior Full-Stack and AI Engineer with 6+ years of experience building distributed systems, LLM-powered applications, and real-time cloud APIs. Proven track record scaling microservices from MVP to 2M+ monthly active users. Specialized in Python (FastAPI/Django), React/TypeScript, AWS cloud infrastructure, and generative AI integrations with vector embeddings (RAG).

---

### Core Competencies
- **Languages & Frameworks:** Python, TypeScript, JavaScript, SQL, FastAPI, Django, React, Next.js, Node.js
- **AI & Machine Learning:** LLM Orchestration (LangChain, LlamaIndex), OpenAI & Gemini APIs, PyTorch, RAG Pipelines, Vector DBs (Pinecone, ChromaDB)
- **Cloud & DevOps:** AWS (ECS, Lambda, S3, RDS), Docker, Kubernetes, Terraform, CI/CD (GitHub Actions), PostgreSQL, Redis
- **System Architecture:** Distributed Systems, Microservices, Event-Driven Architecture (Kafka), RESTful & gRPC APIs

---

### Professional Experience

#### Senior Full-Stack & AI Engineer | CloudScale Systems
*March 2022 – Present | San Francisco, CA*
- Architected an enterprise GenAI copilot using FastAPI, LangChain, and Gemini API that decreased internal document triage time by 64% across 800+ employees.
- Designed scalable asynchronous background processing pipelines using Celery and Redis to handle 4.5M monthly automated analytics queries.
- Containerized 12 core microservices with Docker and orchestrated deployment via AWS EKS, improving system availability to 99.98%.
- Mentored 6 junior engineers and spearheaded automated unit and integration testing protocols, increasing code test coverage from 68% to 94%.

#### Full-Stack Software Engineer | FinTech Wave Inc.
*July 2019 – February 2022 | Austin, TX*
- Built real-time transaction reconciliation dashboard using React, TypeScript, and WebSockets, rendering 50,000+ data rows with sub-100ms latency.
- Refactored legacy PostgreSQL queries, introducing indexing strategies and connection pooling to reduce p99 query latency by 42%.
- Integrated Stripe billing and automated tax calculation microservices processing over $18M in quarterly gross transactions.
- Collaborated closely with product designers and compliance officers to deliver SOC2-compliant data storage pipelines.

---

### Education
**Bachelor of Science in Computer Science**  
University of California, Berkeley | 2015 – 2019  
*Honors: Magna Cum Laude (GPA 3.82) | Coursework: Distributed Systems, Deep Learning, Algorithms*

---

### Key Projects
- **SmartResume AI (Open Source):** Multi-agent ATS scanner analyzing semantic keyword vectors with cosine similarity scoring. 1.8k GitHub stars.
- **RAG-Docs Assistant:** High-performance retrieval-augmented search over PDF technical manuals using ChromaDB and hybrid vector search.
"""

SAMPLE_COMMERCE_RESUME_TEXT = """# Priya Sharma
**Bachelor of Commerce (B.Com Honours) — Finance & Accounting**  
Mumbai, India | priya.sharma@email.com | +91 98201 44521 | linkedin.com/in/priyasharma-commerce

---

### Profile Summary
Detail-oriented and analytical Commerce graduate with strong foundations in Financial Accounting, Auditing, Corporate Taxation, Financial Modeling, and Cost Analysis. Demonstrated internship experience in statutory audit support, ledger reconciliation, GST return filings, and advanced financial modeling in Microsoft Excel and Tally ERP.

---

### Core Competencies & Skills
- **Accounting & Finance:** Financial Statement Analysis, General Ledger, Accounts Payable/Receivable, Variance Analysis, Budgeting
- **Taxation & Compliance:** Goods & Services Tax (GST), TDS, Income Tax filing, Statutory Audit Documentation
- **Software & Tools:** Advanced MS Excel (VLOOKUP, XLOOKUP, Pivot Tables, What-If Analysis), Tally Prime / ERP 9, QuickBooks, Power BI basics
- **Soft Skills:** Analytical thinking, audit precision, cross-functional reporting, client communication

---

### Practical Experience & Internships

#### Finance & Accounts Trainee | Apex Capital Advisory Services
*January 2024 – June 2024 | Mumbai, India*
- Assisted senior auditors in conducting quarterly financial audits for 14 mid-cap corporate clients, verifying $2.4M in balance sheet entries.
- Performed weekly bank reconciliations, vendor ledger audits, and discrepancy resolutions across 350+ monthly invoice accounts.
- Automated quarterly GST and TDS summary worksheets in MS Excel, reducing reporting preparation turnaround time by 30%.
- Drafted comparative cash flow statements and ratio analysis decks used in executive board presentations.

#### Accounting & Tax Intern | R.K. Mehta & Associates (Chartered Accountants)
*June 2023 – November 2023 | Mumbai, India*
- Processed 500+ journal vouchers and ledger entries in Tally Prime for retail and wholesale business clients.
- Prepared tax computation working papers and supported documentation for annual corporate income tax returns.
- Researched regulatory changes in tax deduction norms and drafted compliance briefing memos for client advisors.

---

### Education
**Bachelor of Commerce (Honours) — Accounting & Finance**  
St. Xavier's College, University of Mumbai | Graduated: 2024  
*Academic Score: CGPA 8.7/10.0 (First Class with Distinction)*  
*Key Coursework: Corporate Accounting, Management Accounting, Financial Management, Direct & Indirect Tax, Auditing*

---

### Certifications & Honors
- **Advanced Financial Modeling & Valuation** — Corporate Finance Institute (CFI)
- **Certified Tally Prime Professional** — National Institute of Financial Markets
- **First Prize:** National Inter-Collegiate Commerce & Business Analytics Case Competition (2023)
"""

SAMPLE_BBA_RESUME_TEXT = """# Rahul Verma
**Bachelor of Business Administration (BBA) — Marketing & Operations**  
Bangalore, India | rahul.verma@email.com | +91 98450 77123 | linkedin.com/in/rahulverma-bba

---

### Profile Summary
Enthusiastic and results-driven Business Administration graduate specializing in Marketing Strategy, Digital Campaign Management, Business Development, and Operations. Hands-on experience driving customer acquisition funnels, analyzing market trends, and coordinating B2B outreach across startup and corporate environments.

---

### Core Competencies
- **Business & Strategy:** Market Research, Go-To-Market Strategy, Competitor Benchmarking, Operations Management
- **Marketing & Growth:** Digital Marketing (SEO/SEM), Social Media Marketing, Meta Ads, Email Marketing, Content Strategy
- **Tools & Platforms:** Google Analytics (GA4), HubSpot CRM, Salesforce basics, Canva, Advanced MS Excel, Notion
- **Interpersonal:** Negotiation, B2B Client Presentation, Cross-functional Leadership, Agile Teamwork

---

### Work & Internship Experience

#### Business Development & Marketing Associate | QuickScale Tech Solutions
*September 2023 – April 2024 | Bangalore, India*
- Managed outbound lead generation campaigns across LinkedIn and email, generating 140+ qualified enterprise B2B sales meetings.
- Coordinated multi-channel digital campaigns on Meta and Google Ads, improving overall click-through rate (CTR) by 28%.
- Built comprehensive market sizing and competitor intelligence reports for executive leadership ahead of Series A expansion.
- Tracked pipeline conversion metrics in HubSpot CRM, establishing automated lead scoring workflows for the sales team.

#### Operations & Brand Coordinator Intern | MetroRetail Brands
*January 2023 – July 2023 | Bangalore, India*
- Monitored regional distribution supply chain fulfillment rates across 28 retail partner stores, boosting on-time stock delivery to 96%.
- Designed social media campaign assets and promotional materials that drove a 35% growth in Instagram follower engagement.
- Spearheaded student campus ambassador initiative across 12 universities, onboarding 400+ new verified app subscribers.

---

### Education
**Bachelor of Business Administration (BBA) — Marketing & Operations**  
Christ University, Bangalore | Graduated: 2024  
*Academic Score: CGPA 8.4/10.0*  
*Key Coursework: Marketing Management, Consumer Behaviour, Operations & Supply Chain, Business Statistics, Human Resource Management*

---

### Certifications & Achievements
- **Google Certified Digital Marketing & E-Commerce Specialist**
- **HubSpot Inbound Marketing & Sales Certification**
- **Vice President:** University Management & Entrepreneurship Association (2023-2024)
"""

SAMPLE_JOB_DESCRIPTION = """Role: Senior Full-Stack & AI Engineer
Company: NextGen Intelligence Technologies
Location: Remote (US / Global)
Compensation: $165,000 - $210,000 USD + Equity + Benefits

About the Role:
We are looking for a Senior Full-Stack & AI Engineer to lead the architectural evolution of our career intelligence and workforce optimization platform. You will build cutting-edge applications blending modern web interfaces with generative AI models and distributed cloud infrastructure.

Key Responsibilities:
- Build and maintain robust full-stack web applications and APIs utilizing Python (FastAPI/Flask) and modern React/TypeScript.
- Design, optimize, and deploy retrieval-augmented generation (RAG) pipelines and LLM integrations using Gemini API and vector databases.
- Architect scalable cloud infrastructure on AWS leveraging Docker containers, Kubernetes, and automated CI/CD pipelines.
- Ensure high performance, observability, and sub-second latency for customer-facing AI workflow tools.
- Collaborate with product managers, UX designers, and ML researchers to launch intuitive, polished features.

Requirements:
- 5+ years of software engineering experience in full-stack web development.
- Strong proficiency in Python, FastAPI/Django, React, TypeScript, and modern frontend styling.
- Hands-on experience integrating LLMs, prompt engineering, vector search (ChromaDB, Pinecone), or RAG systems.
- Production experience with Docker, cloud infrastructure (AWS/GCP), and relational databases (PostgreSQL).
- Strong understanding of RESTful API design, authentication, and microservice architectures.
- Bachelor's degree in Computer Science, Software Engineering, or equivalent practical experience.
"""

SAMPLE_BUILDER_INPUTS = {
    "name": "Alex Morgan",
    "target_role": "Senior Full-Stack & AI Engineer",
    "contact": "alex.morgan@email.com | +1 (555) 382-9011 | San Francisco, CA | linkedin.com/in/alexmorgan-demo",
    "skills": "Python, FastAPI, React, TypeScript, PyTorch, Docker, Kubernetes, AWS, Gemini API, LangChain, PostgreSQL, Redis, CI/CD",
    "education": "B.S. Computer Science, UC Berkeley (Magna Cum Laude, GPA 3.82, 2019)",
    "experience": """Senior Software Engineer at CloudScale Systems (2022-Present):
- Built enterprise GenAI copilot using FastAPI and Gemini API that decreased internal triage time by 64%.
- Containerized 12 microservices with Docker and orchestrated deployment via AWS EKS (99.98% uptime).
- Led team of 6 engineers and instituted testing frameworks bringing coverage to 94%.

Full-Stack Engineer at FinTech Wave Inc. (2019-2022):
- Developed real-time transaction dashboard in React & TypeScript with sub-100ms response times.
- Optimized PostgreSQL database queries, reducing p99 response time by 42%.
- Integrated automated Stripe payment and reconciliation pipelines processing $18M+ quarterly."""
}

SAMPLE_COVER_LETTER_TEXT = """**Alex Morgan**  
San Francisco, CA | alex.morgan@email.com | +1 (555) 382-9011 | linkedin.com/in/alexmorgan-demo  

---

**Hiring Team**  
NextGen Intelligence Technologies  

**Subject:** Application for Senior Full-Stack & AI Engineer Role  

Dear Hiring Team,

I am writing to express my strong enthusiasm for the Senior Full-Stack & AI Engineer position at NextGen Intelligence Technologies. Having spent over six years architecting high-throughput distributed systems and building customer-facing generative AI tools, I was energized to see NextGen's mission to pioneer intelligence-driven workforce optimization.

In my current role as Senior Full-Stack & AI Engineer at CloudScale Systems, I spearheaded the design of an enterprise LLM copilot leveraging FastAPI, React/TypeScript, and Gemini API embeddings. This system directly improved workflow triage speed by 64% while maintaining sub-second latency across 4.5M monthly API calls. My deep familiarity with Docker, AWS cloud architecture, and PostgreSQL enables me to build AI applications that are not only innovative, but reliable, secure, and production-ready.

NextGen's vision of blending modern, intuitive interfaces with state-of-the-art AI pipelines aligns perfectly with my background. I would love the opportunity to contribute to your core platform, scale your microservices, and deliver impactful features for your users.

Thank you for your time and consideration. I look forward to the possibility of discussing how my technical background and passion for AI can support NextGen's continued growth.

Warm regards,  

**Alex Morgan**  
alex.morgan@email.com | +1 (555) 382-9011  
"""

SAMPLE_JOBS_CATALOG = [
    # --- Finance & Accounting (Commerce / B.Com / M.Com) ---
    {
        "id": "job_fin_1",
        "title": "Financial Analyst — Valuation & Planning",
        "company": "Deloitte Advisory",
        "location": "Mumbai, India / Hybrid",
        "type": "Full-Time",
        "salary": "₹8.5L - ₹14.0L / $85k - $115k",
        "match": 93,
        "category": "Finance & Accounting",
        "tags": ["Financial Modeling", "MS Excel", "Variance Analysis", "B.Com", "Valuation"],
        "description": "Analyze corporate financial statements, build DCF and LBO forecast models, track monthly P&L variances, and draft executive investor presentations."
    },
    {
        "id": "job_fin_2",
        "title": "Senior Tax & Statutory Audit Associate",
        "company": "KPMG Global Services",
        "location": "Bangalore, India",
        "type": "Full-Time",
        "salary": "₹7.5L - ₹12.5L",
        "match": 90,
        "category": "Finance & Accounting",
        "tags": ["GST", "Statutory Audit", "Tally Prime", "Taxation", "Ledger Audit"],
        "description": "Lead statutory audit verification for multi-national accounts. Oversee GST compliance, TDS reconciliations, and quarterly tax filings."
    },
    {
        "id": "job_fin_3",
        "title": "Corporate Treasury & Accounts Executive",
        "company": "HDFC Bank Corporate Banking",
        "location": "Delhi NCR, India",
        "type": "Full-Time",
        "salary": "₹6.5L - ₹10.5L",
        "match": 88,
        "category": "Finance & Accounting",
        "tags": ["Banking", "Cash Flow", "Accounts Payable", "ERP", "MIS Reporting"],
        "description": "Manage day-to-day liquidity positioning, debt covenant reporting, vendor disbursement approvals, and corporate treasury transactions."
    },

    # --- Business, Operations & Strategy (BBA / MBA) ---
    {
        "id": "job_biz_1",
        "title": "Business Development & Partnerships Lead",
        "company": "Razorpay Enterprise",
        "location": "Bangalore, India / Remote",
        "type": "Full-Time",
        "salary": "₹10.0L - ₹16.0L + Incentives",
        "match": 92,
        "category": "Business & Strategy",
        "tags": ["B2B Sales", "Client Acquisition", "HubSpot", "Negotiation", "BBA"],
        "description": "Drive high-velocity B2B merchant partnerships. Build pipeline outreach, deliver consultative product demos, and negotiate contract renewals."
    },
    {
        "id": "job_biz_2",
        "title": "Operations & Supply Chain Associate",
        "company": "Flipkart Supply Chain",
        "location": "Hyderabad, India",
        "type": "Full-Time",
        "salary": "₹7.0L - ₹11.0L",
        "match": 89,
        "category": "Business & Strategy",
        "tags": ["Supply Chain", "Inventory Management", "Process Optimization", "Excel"],
        "description": "Optimize regional fulfillment logistics and distribution bottlenecks. Analyze warehouse SLA metrics and implement automated vendor tracking."
    },

    # --- Marketing, Growth & Digital Media (BBA / Arts / Mass Comm) ---
    {
        "id": "job_mkt_1",
        "title": "Digital Marketing & Performance Growth Manager",
        "company": "Zomato Growth Labs",
        "location": "Gurgaon, India / Hybrid",
        "type": "Full-Time",
        "salary": "₹9.0L - ₹15.0L",
        "match": 91,
        "category": "Marketing & Media",
        "tags": ["Meta Ads", "Google Ads", "GA4", "SEO/SEM", "Content Strategy"],
        "description": "Spearhead high-ROI user acquisition campaigns across search and paid social. Manage monthly ad budgets and conduct deep-dive attribution modeling."
    },
    {
        "id": "job_mkt_2",
        "title": "Brand Strategist & Communications Specialist",
        "company": "Ogilvy & Mather",
        "location": "Mumbai, India",
        "type": "Full-Time",
        "salary": "₹8.0L - ₹13.0L",
        "match": 87,
        "category": "Marketing & Media",
        "tags": ["Brand Positioning", "Copywriting", "Public Relations", "Social Media"],
        "description": "Craft brand storytelling narratives and omni-channel PR campaigns. Collaborate with creative directors to launch national consumer campaigns."
    },

    # --- Human Resources & People Operations (BBA HR / Psychology / Arts) ---
    {
        "id": "job_hr_1",
        "title": "Human Resources Generalist & Talent Acquisition",
        "company": "McKinsey & Company",
        "location": "Gurgaon, India",
        "type": "Full-Time",
        "salary": "₹8.5L - ₹14.0L",
        "match": 91,
        "category": "HR & People",
        "tags": ["Recruitment", "Employee Engagement", "HR Policies", "HRIS", "Onboarding"],
        "description": "Drive end-to-end talent acquisition pipelines across business and advisory practices. Facilitate performance appraisal cycles and employee retention initiatives."
    },

    # --- Healthcare, Life Sciences & Pharmacy (B.Sc / Pharma) ---
    {
        "id": "job_sci_1",
        "title": "Clinical Research & Regulatory Affairs Associate",
        "company": "Sun Pharma Global",
        "location": "Ahmedabad, India",
        "type": "Full-Time",
        "salary": "₹7.5L - ₹12.0L",
        "match": 89,
        "category": "Healthcare & Science",
        "tags": ["Clinical Trials", "GCP Compliance", "Pharmacovigilance", "B.Sc / B.Pharm"],
        "description": "Coordinate phase-II and III clinical trial data verification, review investigator dossiers, and ensure FDA/CDSCO statutory compliance."
    },

    # --- Technology, AI & Engineering (B.Tech / BCA / CS) ---
    {
        "id": "job_tech_1",
        "title": "Senior Full-Stack & AI Engineer",
        "company": "NextGen Intelligence",
        "location": "Remote (Global)",
        "type": "Full-Time",
        "salary": "$165k - $210k / ₹35L - ₹55L",
        "match": 94,
        "category": "AI & Tech",
        "tags": ["Python", "FastAPI", "React", "AWS", "LLMs", "B.Tech"],
        "description": "Lead the architectural evolution of our workforce AI copilot. Build reactive frontends with React and high-throughput Python microservices on AWS."
    },
    {
        "id": "job_tech_2",
        "title": "Lead Cloud Infrastructure Architect",
        "company": "Datadog",
        "location": "Remote",
        "type": "Full-Time",
        "salary": "$175k - $225k",
        "match": 88,
        "category": "AI & Tech",
        "tags": ["Kubernetes", "Terraform", "AWS", "Docker"],
        "description": "Architect multi-region Kubernetes clusters and automated CI/CD deployment pipelines. Ensure 99.99% availability for enterprise monitoring."
    },
    {
        "id": "job_tech_3",
        "title": "Senior Data Scientist (GenAI)",
        "company": "Spotify",
        "location": "New York, NY / Remote",
        "type": "Full-Time",
        "salary": "$150k - $190k",
        "match": 85,
        "category": "AI & Tech",
        "tags": ["SQL", "Python", "MLflow", "BigQuery"],
        "description": "Leverage semantic discovery and audio embedding models to deliver personalized recommendations to over 500 million active listeners."
    },

    # --- Product, Design & Creative ---
    {
        "id": "job_prod_1",
        "title": "Principal Product Manager",
        "company": "Figma",
        "location": "San Francisco, CA / Remote",
        "type": "Full-Time",
        "salary": "$190k - $250k",
        "match": 89,
        "category": "Product & Design",
        "tags": ["Product Strategy", "UX", "Roadmap", "Analytics"],
        "description": "Define the vision for generative design workflows. Partner with engineering to shape human-in-the-loop AI interfaces."
    }
]

SAMPLE_HISTORY_ENTRIES = [
    (
        "Career Discovery",
        """### 🎓 Candidate Profile Intelligence
- **Identified Domain / Industry:** Commerce & Corporate Finance / Auditing
- **Detected Education & Background:** Bachelor of Commerce (B.Com Honours) in Accounting & Finance
- **Experience Tier:** Early Career (1-2 yrs Practical Training & Trainee Experience)
- **Top Transferable Strengths:** Financial Statement Analysis, Tally Prime, GST Compliance, Advanced Excel, Statutory Audit Verification

---

### 💼 Recommended Job Roles & Career Matches

#### 1. Financial Analyst — Planning & Reporting
- **Capability & Readiness Score:** 94% Match
- **Why You Are Qualified:** Robust foundation in ratio analysis, financial modeling, and cash flow statement preparation from both coursework and practical audit experience.
- **Core Daily Responsibilities:** Evaluate revenue drivers, perform budget variance reconciliations, and prepare executive management decks.
- **High-Impact Skills to Level Up:** Power BI, Tableau, Advanced DCF valuation models.
- **Estimated Market Compensation:** ₹7,50,000 - ₹12,00,000 / $75,000 - $95,000

#### 2. Corporate Tax & Statutory Audit Associate
- **Capability & Readiness Score:** 91% Match
- **Why You Are Qualified:** Direct hands-on experience handling GST summaries, TDS computations, and 500+ ledger audit vouchers.
- **Core Daily Responsibilities:** Review trial balances, verify statutory tax compliance, and liaise with independent auditors.
- **High-Impact Skills to Level Up:** SAP FICO module certification.
- **Estimated Market Compensation:** ₹6,80,000 - ₹10,50,000
""",
        "2026-10-14 09:20:15"
    ),
    (
        "Resume",
        SAMPLE_RESUME_TEXT,
        "2026-10-12 10:45:12"
    ),
    (
        "Cover Letter",
        SAMPLE_COVER_LETTER_TEXT,
        "2026-10-12 10:30:04"
    ),
    (
        "Resume",
        """# Alex Morgan - Cloud Systems Architect Resume
**Target Role:** Lead Cloud Infrastructure Architect  
**Core Competencies:** AWS, Terraform, Docker, Kubernetes, Distributed Systems  
**Experience Highlight:** Led migration of 120+ microservices to Kubernetes with zero downtime and 35% cost reduction.
""",
        "2026-10-11 16:15:20"
    ),
    (
        "Cover Letter",
        """**Alex Morgan** | Application for Lead Cloud Infrastructure Architect at Datadog.  
Highlighting 5+ years managing multi-region Kubernetes deployments and resilient automated CI/CD pipelines.
""",
        "2026-10-11 15:50:11"
    )
]

def seed_demo_user():
    """Seeds the DemoUser into users.db with pre-populated history entries."""
    auth.create_usertable()
    auth.create_history_table()
    
    username = "DemoUser"
    password_hash = auth.make_hashes("demo123")
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT username FROM userstable WHERE username = ?', (username,))
    if not c.fetchone():
        c.execute('INSERT INTO userstable (username, password) VALUES (?, ?)', (username, password_hash))
    
    # Check if history already seeded
    c.execute('SELECT COUNT(*) FROM history WHERE username = ?', (username,))
    count = c.fetchone()[0]
    if count == 0:
        for doc_type, content, timestamp in SAMPLE_HISTORY_ENTRIES:
            c.execute('INSERT INTO history (username, doc_type, content, timestamp) VALUES (?, ?, ?, ?)',
                      (username, doc_type, content, timestamp))
    conn.commit()
    conn.close()
