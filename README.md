# AI Resume Analyzer & Interview Preparation System

A Django web application that helps job seekers analyze resumes, improve ATS compatibility, match job descriptions, and practice interviews with AI-generated feedback.

## Features 

- User registration and authentication
- Resume upload (PDF/DOCX) with text extraction
- AI/heuristic resume scoring (quality + ATS)
- Skill extraction and improvement suggestions
- Job description matching with compatibility score
- Mock interview sessions (technical, behavioral, HR)
- AI feedback on interview answers
- Career guidance dashboard with progress tracking

## Tech Stack

- **Backend:** Python, Django
- **Database:** SQLite
- **AI/NLP:** OpenAI API, NLTK-style keyword utilities
- **Resume parsing:** python-docx, pypdf
- **Frontend:** HTML, CSS
- **Deployment target:** Render

## Quick Start

```bash
cd resume-analyzer
python -m venv venv
venv\Scripts\activate        
pip install -r requirements.txt
copy .env.example .env         

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Workflow

1. Register and log in
2. Upload a resume (PDF/DOCX)
3. Review AI analysis and ATS score
4. Match resume against a job description
5. Create a mock interview session
6. Answer questions and review AI feedback
7. Track progress on the dashboard


