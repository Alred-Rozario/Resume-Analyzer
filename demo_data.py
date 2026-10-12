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
    {
        "id": "job_1",
        "title": "Senior Full-Stack & AI Engineer",
        "company": "NextGen Intelligence",
        "location": "Remote (US)",
        "type": "Full-Time",
        "salary": "$165k - $210k",
        "match": 94,
        "category": "AI / Data",
        "tags": ["Python", "FastAPI", "React", "AWS", "LLMs"],
        "description": "Lead the architectural evolution of our workforce AI copilot. Build reactive frontends with React and high-throughput Python microservices on AWS."
    },
    {
        "id": "job_2",
        "title": "Staff Machine Learning Engineer",
        "company": "OpenAI Partner Labs",
        "location": "San Francisco, CA (Hybrid)",
        "type": "Full-Time",
        "salary": "$210k - $290k",
        "match": 91,
        "category": "AI / Data",
        "tags": ["PyTorch", "Distributed Systems", "Python", "RAG"],
        "description": "Design and train domain-adapted embeddings and fine-tuned models. Optimize inference pipelines for low latency and high scalability."
    },
    {
        "id": "job_3",
        "title": "Lead Cloud Infrastructure Architect",
        "company": "Datadog",
        "location": "Remote",
        "type": "Full-Time",
        "salary": "$175k - $225k",
        "match": 88,
        "category": "Engineering",
        "tags": ["Kubernetes", "Terraform", "AWS", "Docker"],
        "description": "Architect multi-region Kubernetes clusters and automated CI/CD deployment pipelines. Ensure 99.99% availability for enterprise monitoring."
    },
    {
        "id": "job_4",
        "title": "Senior Data Scientist (GenAI)",
        "company": "Spotify",
        "location": "New York, NY",
        "type": "Full-Time",
        "salary": "$150k - $190k",
        "match": 85,
        "category": "AI / Data",
        "tags": ["SQL", "Python", "MLflow", "BigQuery"],
        "description": "Leverage semantic discovery and audio embedding models to deliver personalized recommendations to over 500 million active listeners."
    },
    {
        "id": "job_5",
        "title": "Staff Frontend Engineer",
        "company": "Vercel",
        "location": "Remote",
        "type": "Full-Time",
        "salary": "$160k - $200k",
        "match": 82,
        "category": "Engineering",
        "tags": ["Next.js", "TypeScript", "Tailwind", "React"],
        "description": "Build high-performance, accessible developer tools and dashboard experiences with cutting-edge React Server Components."
    },
    {
        "id": "job_6",
        "title": "Principal Product Manager (AI Platform)",
        "company": "Figma",
        "location": "San Francisco, CA",
        "type": "Full-Time",
        "salary": "$190k - $250k",
        "match": 89,
        "category": "Product",
        "tags": ["Product Strategy", "LLM UX", "Roadmap", "Analytics"],
        "description": "Define the vision for generative design workflows. Partner with engineering to shape human-in-the-loop AI interfaces."
    }
]

SAMPLE_HISTORY_ENTRIES = [
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
