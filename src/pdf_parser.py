import pdfplumber
import re
import os
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_resume_data(pdf_path: str) -> Dict:
    """
    Extract structured data from a resume PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        Dict: Structured resume data
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Extract all text from PDF
            full_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
            
            if not full_text.strip():
                logger.warning(f"No text extracted from {pdf_path}")
                return {"raw_text": "", "error": "No text found in PDF"}
            
            # Extract structured information
            resume_data = {
                "raw_text": full_text,
                "name": extract_name(full_text),
                "email": extract_email(full_text),
                "phone": extract_phone(full_text),
                "skills": extract_skills(full_text),
                "experience": extract_experience(full_text),
                "education": extract_education(full_text),
                "linkedin": extract_linkedin(full_text)
            }
            
            logger.info(f"Successfully extracted data from {pdf_path}")
            return resume_data
            
    except Exception as e:
        logger.error(f"Error extracting data from {pdf_path}: {str(e)}")
        return {"raw_text": "", "error": str(e)}

def extract_name(text: str) -> str:
    """Extract candidate name from resume text."""
    lines = text.split('\n')
    
    # Look for name in first few lines
    for line in lines[:5]:
        line = line.strip()
        if line and len(line.split()) <= 4:  # Name usually 1-4 words
            # Skip lines that look like headers or contact info
            if not any(keyword in line.lower() for keyword in 
                      ['resume', 'cv', 'curriculum', 'email', 'phone', 'address', '@']):
                # Check if it looks like a name (contains letters, possibly with dots/apostrophes)
                if re.match(r'^[A-Za-z\s\.\'-]+$', line) and len(line) > 2:
                    return line.title()
    
    return "Unknown"

def extract_email(text: str) -> str:
    """Extract email address from resume text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else "Not provided"

def extract_phone(text: str) -> str:
    """Extract phone number from resume text."""
    # Various phone number patterns
    phone_patterns = [
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890 or 123.456.7890
        r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',    # (123) 456-7890
        r'\+\d{1,3}\s?\d{3,4}\s?\d{3,4}\s?\d{3,4}',  # International format
        r'\b\d{10}\b'  # 1234567890
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            return phones[0]
    
    return "Not provided"

def extract_linkedin(text: str) -> str:
    """Extract LinkedIn profile URL from resume text."""
    linkedin_pattern = r'https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+/?'
    linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
    return linkedin_matches[0] if linkedin_matches else "Not provided"

def extract_skills(text: str) -> List[str]:
    """Extract technical skills from resume text."""
    # Common technical skills database
    skills_database = {
        'programming_languages': [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'go', 'rust',
            'kotlin', 'swift', 'php', 'ruby', 'scala', 'r', 'matlab', 'perl', 'shell',
            'bash', 'powershell', 'sql', 'html', 'css', 'sass', 'less'
        ],
        'ml_ai': [
            'machine learning', 'deep learning', 'neural networks', 'tensorflow', 'pytorch',
            'keras', 'scikit-learn', 'pandas', 'numpy', 'opencv', 'nlp', 'computer vision',
            'reinforcement learning', 'transformers', 'bert', 'gpt', 'llm', 'ai', 'ml'
        ],
        'web_frameworks': [
            'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'fastapi',
            'spring', 'spring boot', 'laravel', 'rails', 'asp.net', 'next.js', 'nuxt.js'
        ],
        'databases': [
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
            'oracle', 'sql server', 'sqlite', 'firebase', 'dynamodb', 'neo4j'
        ],
        'cloud_devops': [
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab ci',
            'github actions', 'terraform', 'ansible', 'chef', 'puppet', 'vagrant'
        ],
        'tools': [
            'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'slack',
            'postman', 'swagger', 'figma', 'adobe', 'photoshop', 'illustrator'
        ],
        'data_engineering': [
            'hadoop', 'spark', 'kafka', 'airflow', 'snowflake', 'databricks',
            'etl', 'data pipeline', 'big data', 'data warehouse', 'data lake'
        ]
    }
    
    found_skills = []
    text_lower = text.lower()
    
    # Extract skills from all categories
    for category, skills_list in skills_database.items():
        for skill in skills_list:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                # Add the properly formatted skill name
                found_skills.append(skill.title())
    
    # Look for skills in common sections
    skills_sections = extract_skills_section(text)
    if skills_sections:
        found_skills.extend(skills_sections)
    
    # Remove duplicates and return
    return list(set(found_skills))

def extract_skills_section(text: str) -> List[str]:
    """Extract skills from dedicated skills sections."""
    skills = []
    lines = text.split('\n')
    
    skills_started = False
    for line in lines:
        line = line.strip()
        
        # Check if we're in a skills section
        if any(keyword in line.lower() for keyword in 
               ['skills', 'technical skills', 'technologies', 'programming languages']):
            skills_started = True
            continue
        
        # Stop if we hit another section
        if skills_started and any(keyword in line.lower() for keyword in 
                                 ['experience', 'education', 'projects', 'certifications']):
            break
        
        # Extract skills from the current line
        if skills_started and line:
            # Split by common delimiters
            line_skills = re.split(r'[,|•·\-\n]', line)
            for skill in line_skills:
                skill = skill.strip()
                if skill and len(skill) > 1:
                    skills.append(skill.title())
    
    return skills

def extract_experience(text: str) -> List[Dict]:
    """Extract work experience from resume text."""
    experience = []
    lines = text.split('\n')
    
    # Look for experience section
    experience_started = False
    current_job = {}
    
    for line in lines:
        line = line.strip()
        
        # Check if we're starting experience section
        if any(keyword in line.lower() for keyword in 
               ['experience', 'work experience', 'employment', 'professional experience']):
            experience_started = True
            continue
        
        # Stop if we hit another major section
        if experience_started and any(keyword in line.lower() for keyword in 
                                     ['education', 'skills', 'projects', 'certifications']):
            if current_job:
                experience.append(current_job)
            break
        
        if experience_started and line:
            # Try to identify job titles and companies
            if re.search(r'\b(engineer|developer|analyst|manager|director|lead|senior|junior|intern)\b', 
                        line.lower()):
                if current_job:
                    experience.append(current_job)
                current_job = {'title': line, 'description': []}
            elif current_job:
                current_job['description'].append(line)
    
    # Add the last job if exists
    if current_job:
        experience.append(current_job)
    
    return experience

def extract_education(text: str) -> List[Dict]:
    """Extract education information from resume text."""
    education = []
    lines = text.split('\n')
    
    education_started = False
    current_edu = {}
    
    for line in lines:
        line = line.strip()
        
        # Check if we're starting education section
        if any(keyword in line.lower() for keyword in 
               ['education', 'academic', 'qualifications', 'degrees']):
            education_started = True
            continue
        
        # Stop if we hit another major section
        if education_started and any(keyword in line.lower() for keyword in 
                                    ['experience', 'skills', 'projects', 'certifications']):
            if current_edu:
                education.append(current_edu)
            break
        
        if education_started and line:
            # Look for degree patterns
            degree_patterns = [
                r'\b(bachelor|master|phd|doctorate|associate|diploma|certificate)\b',
                r'\b(b\.?s\.?|m\.?s\.?|m\.?a\.?|ph\.?d\.?|b\.?a\.?|b\.?tech|m\.?tech)\b'
            ]
            
            for pattern in degree_patterns:
                if re.search(pattern, line.lower()):
                    if current_edu:
                        education.append(current_edu)
                    current_edu = {'degree': line, 'details': []}
                    break
            else:
                if current_edu:
                    current_edu['details'].append(line)
    
    # Add the last education entry if exists
    if current_edu:
        education.append(current_edu)
    
    return education

def calculate_experience_years(experience_list: List[Dict]) -> int:
    """Calculate total years of experience from experience list."""
    if not experience_list:
        return 0
    
    # Simple heuristic: count number of jobs and estimate
    # In a real implementation, you'd parse dates more carefully
    return min(len(experience_list) * 2, 15)  # Cap at 15 years for estimation

# Test function for development
def test_extraction():
    """Test function to verify PDF extraction works."""
    test_text = """
    John Doe
    Software Engineer
    john.doe@email.com
    (555) 123-4567
    
    SKILLS
    Python, JavaScript, React, Django, MySQL, AWS, Docker
    
    EXPERIENCE
    Senior Software Engineer at Tech Corp
    - Developed web applications using React and Django
    - Managed AWS infrastructure
    
    EDUCATION
    Master of Science in Computer Science
    University of Technology
    """
    
    print("Testing extraction functions...")
    print(f"Name: {extract_name(test_text)}")
    print(f"Email: {extract_email(test_text)}")
    print(f"Phone: {extract_phone(test_text)}")
    print(f"Skills: {extract_skills(test_text)}")
    print(f"Experience: {extract_experience(test_text)}")
    print(f"Education: {extract_education(test_text)}")

if __name__ == "__main__":
    test_extraction() 