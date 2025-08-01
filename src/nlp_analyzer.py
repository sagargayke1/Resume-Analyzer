import re
from typing import Dict, List, Optional, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)

def analyze_candidate_profile(resume_data: Dict) -> Dict:
    """
    Analyze candidate profile and extract key information.
    
    Args:
        resume_data (Dict): Raw resume data from PDF parser
        
    Returns:
        Dict: Analyzed candidate profile
    """
    if 'error' in resume_data:
        return {'error': resume_data['error']}
    
    # Calculate experience years
    experience_years = calculate_experience_years_from_text(resume_data.get('raw_text', ''))
    
    # Process education
    education_level = analyze_education_level(resume_data.get('education', []))
    
    # Enhance skills extraction
    enhanced_skills = enhance_skills_extraction(resume_data.get('skills', []), resume_data.get('raw_text', ''))
    
    # Calculate seniority level
    seniority = calculate_seniority_level(experience_years, enhanced_skills, education_level)
    
    profile = {
        'name': resume_data.get('name', 'Unknown'),
        'email': resume_data.get('email', 'Not provided'),
        'phone': resume_data.get('phone', 'Not provided'),
        'linkedin': resume_data.get('linkedin', 'Not provided'),
        'skills': enhanced_skills,
        'experience_years': experience_years,
        'education': education_level,
        'seniority': seniority,
        'raw_experience': resume_data.get('experience', []),
        'raw_education': resume_data.get('education', [])
    }
    
    return profile

def classify_domain(skills: List[str]) -> str:
    """
    Classify candidate's primary domain based on skills.
    
    Args:
        skills (List[str]): List of candidate skills
        
    Returns:
        str: Primary domain classification
    """
    if not skills:
        return "General"
    
    # Domain classification rules based on skills
    domain_keywords = {
        'ML/AI': [
            'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras',
            'scikit-learn', 'neural networks', 'nlp', 'computer vision', 'ai',
            'transformers', 'bert', 'gpt', 'opencv', 'pandas', 'numpy', 'ml'
        ],
        'Data Engineering': [
            'hadoop', 'spark', 'kafka', 'airflow', 'etl', 'data pipeline',
            'snowflake', 'databricks', 'big data', 'data warehouse', 'data lake',
            'apache spark', 'hive', 'pig', 'scala', 'sql'
        ],
        'Frontend': [
            'react', 'angular', 'vue', 'javascript', 'typescript', 'html', 'css',
            'sass', 'less', 'webpack', 'babel', 'npm', 'yarn', 'jquery', 'bootstrap',
            'tailwind', 'next.js', 'nuxt.js', 'svelte'
        ],
        'Backend': [
            'node.js', 'express', 'django', 'flask', 'fastapi', 'spring', 'spring boot',
            'laravel', 'rails', 'asp.net', 'php', 'java', 'python', 'c#', 'go', 'rust'
        ],
        'DevOps': [
            'docker', 'kubernetes', 'jenkins', 'gitlab ci', 'github actions',
            'terraform', 'ansible', 'chef', 'puppet', 'aws', 'azure', 'gcp',
            'linux', 'bash', 'shell scripting', 'monitoring'
        ],
        'Mobile': [
            'ios', 'android', 'swift', 'kotlin', 'react native', 'flutter',
            'xamarin', 'ionic', 'cordova', 'mobile development'
        ],
        'Full Stack': [
            'full stack', 'fullstack', 'mean', 'mern', 'lamp', 'django + react',
            'node + react'
        ]
    }
    
    # Convert skills to lowercase for matching
    skills_lower = [skill.lower() for skill in skills]
    
    # Calculate scores for each domain
    domain_scores = {}
    for domain, keywords in domain_keywords.items():
        score = 0
        for keyword in keywords:
            for skill in skills_lower:
                if keyword in skill:
                    score += 1
        domain_scores[domain] = score
    
    # Find the domain with highest score
    if domain_scores:
        max_score = max(domain_scores.values())
        if max_score == 0:
            return "General"
        
        # Return the domain with highest score
        for domain, score in domain_scores.items():
            if score == max_score:
                return domain
    
    return "General"

def calculate_experience_years_from_text(text: str) -> int:
    """
    Calculate years of experience from resume text using pattern matching.
    
    Args:
        text (str): Resume text
        
    Returns:
        int: Estimated years of experience
    """
    if not text:
        return 0
    
    # Pattern to find years of experience mentions
    experience_patterns = [
        r'(\d+)\s*(?:\+)?\s*years?\s+(?:of\s+)?experience',
        r'(\d+)\s*(?:\+)?\s*yrs?\s+(?:of\s+)?experience',
        r'experience\s+(?:of\s+)?(\d+)\s*(?:\+)?\s*years?',
        r'(\d+)\s*(?:\+)?\s*years?\s+in\s+',
    ]
    
    years_found = []
    text_lower = text.lower()
    
    for pattern in experience_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            try:
                years = int(match)
                if 0 <= years <= 50:  # Reasonable range
                    years_found.append(years)
            except ValueError:
                continue
    
    if years_found:
        return max(years_found)  # Take the highest mentioned experience
    
    # Fallback: estimate from job positions (rough heuristic)
    job_keywords = ['engineer', 'developer', 'analyst', 'manager', 'lead', 'senior', 'principal']
    job_count = 0
    for keyword in job_keywords:
        job_count += len(re.findall(r'\b' + keyword + r'\b', text_lower))
    
    # Estimate 2 years per job position, capped at 15
    estimated_years = min(job_count * 2, 15)
    return max(estimated_years, 0)

def analyze_education_level(education_data: List[Dict]) -> str:
    """
    Analyze education level from education data.
    
    Args:
        education_data (List[Dict]): Education information
        
    Returns:
        str: Education level (PhD, Masters, Bachelors, etc.)
    """
    if not education_data:
        return "Not specified"
    
    education_levels = {
        'phd': ['phd', 'ph.d', 'doctorate', 'doctoral'],
        'masters': ['master', 'm.s', 'ms', 'm.a', 'ma', 'mba', 'm.tech', 'mtech'],
        'bachelors': ['bachelor', 'b.s', 'bs', 'b.a', 'ba', 'b.tech', 'btech', 'be'],
        'associate': ['associate', 'diploma'],
        'certificate': ['certificate', 'certification']
    }
    
    # Check each education entry
    for edu in education_data:
        degree_text = edu.get('degree', '').lower()
        
        for level, keywords in education_levels.items():
            for keyword in keywords:
                if keyword in degree_text:
                    return level.title()
    
    return "Not specified"

def enhance_skills_extraction(base_skills: List[str], text: str) -> List[str]:
    """
    Enhance skills extraction with additional patterns and context.
    
    Args:
        base_skills (List[str]): Skills found by basic extraction
        text (str): Full resume text
        
    Returns:
        List[str]: Enhanced skills list
    """
    enhanced_skills = list(set(base_skills))  # Remove duplicates
    
    # Additional skill patterns to look for
    additional_patterns = {
        'Version Control': r'\b(git|github|gitlab|bitbucket|svn|mercurial)\b',
        'Databases': r'\b(mysql|postgresql|mongodb|redis|oracle|sql server|sqlite)\b',
        'Cloud Platforms': r'\b(aws|azure|gcp|google cloud|amazon web services)\b',
        'Testing': r'\b(unit test|integration test|pytest|jest|selenium|cypress)\b',
        'Methodologies': r'\b(agile|scrum|kanban|devops|ci/cd|tdd|bdd)\b'
    }
    
    text_lower = text.lower()
    for category, pattern in additional_patterns.items():
        matches = re.findall(pattern, text_lower)
        for match in matches:
            skill_name = match.title()
            if skill_name not in enhanced_skills:
                enhanced_skills.append(skill_name)
    
    return sorted(enhanced_skills)

def calculate_seniority_level(experience_years: int, skills: List[str], education: str) -> str:
    """
    Calculate seniority level based on experience, skills, and education.
    
    Args:
        experience_years (int): Years of experience
        skills (List[str]): List of skills
        education (str): Education level
        
    Returns:
        str: Seniority level (Junior, Mid-level, Senior, Principal, etc.)
    """
    # Base score from experience
    exp_score = min(experience_years, 15)  # Cap at 15 years
    
    # Skill diversity bonus
    skill_score = min(len(skills) / 10, 2)  # Max 2 points for skills
    
    # Education bonus
    edu_score = 0
    if education.lower() in ['phd', 'masters']:
        edu_score = 1
    elif education.lower() == 'bachelors':
        edu_score = 0.5
    
    # Calculate total score
    total_score = exp_score + skill_score + edu_score
    
    # Determine seniority level
    if total_score >= 12:
        return "Principal/Staff"
    elif total_score >= 8:
        return "Senior"
    elif total_score >= 4:
        return "Mid-level"
    elif total_score >= 1:
        return "Junior"
    else:
        return "Entry-level"

def extract_key_projects(text: str) -> List[str]:
    """
    Extract key projects from resume text.
    
    Args:
        text (str): Resume text
        
    Returns:
        List[str]: List of project descriptions
    """
    projects = []
    lines = text.split('\n')
    
    project_started = False
    current_project = []
    
    for line in lines:
        line = line.strip()
        
        # Check if we're starting projects section
        if any(keyword in line.lower() for keyword in ['projects', 'personal projects', 'key projects']):
            project_started = True
            continue
        
        # Stop if we hit another section
        if project_started and any(keyword in line.lower() for keyword in 
                                  ['experience', 'education', 'skills', 'certifications']):
            if current_project:
                projects.append(' '.join(current_project))
            break
        
        if project_started and line:
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                if current_project:
                    projects.append(' '.join(current_project))
                current_project = [line]
            else:
                current_project.append(line)
    
    # Add the last project
    if current_project:
        projects.append(' '.join(current_project))
    
    return projects

def analyze_skill_proficiency(skills: List[str], text: str) -> Dict[str, str]:
    """
    Analyze skill proficiency levels from context.
    
    Args:
        skills (List[str]): List of skills
        text (str): Resume text
        
    Returns:
        Dict[str, str]: Skill to proficiency level mapping
    """
    proficiency_levels = {}
    text_lower = text.lower()
    
    # Proficiency keywords
    proficiency_keywords = {
        'expert': ['expert', 'advanced', 'proficient', 'extensive'],
        'intermediate': ['intermediate', 'experienced', 'solid', 'good'],
        'basic': ['basic', 'familiar', 'exposure', 'beginner']
    }
    
    for skill in skills:
        skill_lower = skill.lower()
        found_level = 'intermediate'  # Default level
        
        # Look for proficiency mentions near the skill
        for level, keywords in proficiency_keywords.items():
            for keyword in keywords:
                # Look for patterns like "expert in Python" or "Python (advanced)"
                pattern = f'({keyword}.*{re.escape(skill_lower)}|{re.escape(skill_lower)}.*{keyword})'
                if re.search(pattern, text_lower):
                    found_level = level
                    break
            if found_level != 'intermediate':
                break
        
        proficiency_levels[skill] = found_level
    
    return proficiency_levels

def get_skill_categories(skills: List[str]) -> Dict[str, List[str]]:
    """
    Categorize skills into different technology categories.
    
    Args:
        skills (List[str]): List of skills
        
    Returns:
        Dict[str, List[str]]: Categorized skills
    """
    categories = {
        'Programming Languages': [],
        'Frameworks': [],
        'Databases': [],
        'Cloud & DevOps': [],
        'Tools & Technologies': [],
        'ML/AI': [],
        'Other': []
    }
    
    # Category mappings
    category_keywords = {
        'Programming Languages': [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
            'kotlin', 'swift', 'php', 'ruby', 'scala', 'r', 'matlab'
        ],
        'Frameworks': [
            'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express',
            'laravel', 'rails', 'next.js', 'nuxt.js'
        ],
        'Databases': [
            'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sql server',
            'elasticsearch', 'cassandra', 'sqlite'
        ],
        'Cloud & DevOps': [
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform',
            'ansible', 'gitlab ci', 'github actions'
        ],
        'ML/AI': [
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'opencv', 'pandas',
            'numpy', 'machine learning', 'deep learning', 'nlp'
        ]
    }
    
    skills_lower = [skill.lower() for skill in skills]
    
    for skill in skills:
        skill_lower = skill.lower()
        categorized = False
        
        for category, keywords in category_keywords.items():
            if any(keyword in skill_lower for keyword in keywords):
                categories[category].append(skill)
                categorized = True
                break
        
        if not categorized:
            categories['Tools & Technologies'].append(skill)
    
    # Remove empty categories
    return {k: v for k, v in categories.items() if v}

# Test function
def test_analysis():
    """Test the analysis functions."""
    test_resume_data = {
        'name': 'John Doe',
        'email': 'john.doe@email.com',
        'skills': ['Python', 'TensorFlow', 'React', 'AWS', 'Docker'],
        'experience': [{'title': 'Senior ML Engineer', 'description': ['Built ML models']}],
        'education': [{'degree': 'Master of Science in Computer Science'}],
        'raw_text': 'Senior ML Engineer with 5 years of experience in Python and TensorFlow'
    }
    
    profile = analyze_candidate_profile(test_resume_data)
    domain = classify_domain(profile['skills'])
    
    print(f"Profile: {profile}")
    print(f"Domain: {domain}")

if __name__ == "__main__":
    test_analysis() 