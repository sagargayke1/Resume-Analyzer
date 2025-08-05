import re
from typing import Dict, List, Optional, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)

def calculate_match_score(candidate: Dict, job_requirements: Dict) -> float:
    """
    Calculate match score between candidate and job requirements.
    
    Args:
        candidate (Dict): Candidate profile
        job_requirements (Dict): Job requirements
        
    Returns:
        float: Match score between 0 and 1
    """
    scores = []
    weights = {
        'domain_match': 0.3,
        'skills_match': 0.4,
        'experience_match': 0.2,
        'text_similarity': 0.1
    }
    
    # Domain match score
    domain_score = calculate_domain_match(
        candidate.get('domain', 'General'),
        job_requirements.get('domain', 'General')
    )
    scores.append(('domain_match', domain_score))
    
    # Skills match score
    skills_score = calculate_skills_match(
        candidate.get('skills', []),
        job_requirements.get('required_skills', [])
    )
    scores.append(('skills_match', skills_score))
    
    # Experience match score
    experience_score = calculate_experience_match(
        candidate.get('experience_years', 0),
        job_requirements.get('required_experience', 0)
    )
    scores.append(('experience_match', experience_score))
    
    # Text similarity score (basic keyword matching)
    text_score = calculate_text_similarity(
        candidate.get('skills', []) + [candidate.get('domain', '')],
        job_requirements.get('job_description', '')
    )
    scores.append(('text_similarity', text_score))
    
    # Calculate weighted average
    total_score = sum(score * weights.get(category, 0.25) for category, score in scores)
    
    return min(max(total_score, 0.0), 1.0)  # Ensure score is between 0 and 1

def calculate_domain_match(candidate_domain: str, required_domain: str) -> float:
    """
    Calculate domain match score.
    
    Args:
        candidate_domain (str): Candidate's primary domain
        required_domain (str): Required domain for the job
        
    Returns:
        float: Domain match score (0-1)
    """
    if not candidate_domain or not required_domain:
        return 0.5  # Neutral score if domain info is missing
    
    candidate_domain = candidate_domain.lower()
    required_domain = required_domain.lower()
    
    # Exact match
    if candidate_domain == required_domain:
        return 1.0
    
    # Related domains scoring
    domain_relationships = {
        'ml/ai': ['data engineering', 'backend'],
        'data engineering': ['ml/ai', 'backend'],
        'frontend': ['full stack'],
        'backend': ['full stack', 'devops', 'ml/ai'],
        'devops': ['backend', 'cloud'],
        'full stack': ['frontend', 'backend'],
        'mobile': ['frontend']
    }
    
    # Check if domains are related
    related_domains = domain_relationships.get(required_domain, [])
    if candidate_domain in related_domains:
        return 0.7
    
    # Check reverse relationship
    related_domains = domain_relationships.get(candidate_domain, [])
    if required_domain in related_domains:
        return 0.7
    
    # Partial matches
    if 'full stack' in candidate_domain and required_domain in ['frontend', 'backend']:
        return 0.8
    if 'full stack' in required_domain and candidate_domain in ['frontend', 'backend']:
        return 0.8
    
    return 0.2  # Low score for unrelated domains

def calculate_skills_match(candidate_skills: List[str], required_skills: List[str]) -> float:
    """
    Calculate skills match score.
    
    Args:
        candidate_skills (List[str]): Candidate's skills
        required_skills (List[str]): Required skills for the job
        
    Returns:
        float: Skills match score (0-1)
    """
    if not required_skills:
        return 0.5  # Neutral score if no requirements specified
    
    if not candidate_skills:
        return 0.0
    
    # Normalize skills for comparison
    candidate_skills_lower = [skill.lower().strip() for skill in candidate_skills]
    required_skills_lower = [skill.lower().strip() for skill in required_skills]
    
    # Exact matches
    exact_matches = 0
    partial_matches = 0
    
    for required_skill in required_skills_lower:
        found_exact = False
        
        # Check for exact matches
        for candidate_skill in candidate_skills_lower:
            if required_skill == candidate_skill:
                exact_matches += 1
                found_exact = True
                break
        
        # Check for partial matches if no exact match found
        if not found_exact:
            for candidate_skill in candidate_skills_lower:
                if (required_skill in candidate_skill or candidate_skill in required_skill) and len(required_skill) > 2:
                    partial_matches += 1
                    break
    
    # Calculate score
    total_matches = exact_matches + (partial_matches * 0.5)
    match_score = total_matches / len(required_skills_lower)
    
    return min(match_score, 1.0)

def calculate_experience_match(candidate_experience: int, required_experience: int) -> float:
    """
    Calculate experience match score.
    
    Args:
        candidate_experience (int): Candidate's years of experience
        required_experience (int): Required years of experience
        
    Returns:
        float: Experience match score (0-1)
    """
    if required_experience <= 0:
        return 1.0  # No experience requirement
    
    if candidate_experience <= 0:
        return 0.1  # Some points for potential
    
    # Calculate ratio
    ratio = candidate_experience / required_experience
    
    # Scoring based on ratio
    if ratio >= 1.0:
        return 1.0  # Meets or exceeds requirement
    elif ratio >= 0.8:
        return 0.9  # Close to requirement
    elif ratio >= 0.6:
        return 0.7  # Somewhat below requirement
    elif ratio >= 0.4:
        return 0.5  # Significantly below requirement
    elif ratio >= 0.2:
        return 0.3  # Far below requirement
    else:
        return 0.1  # Very far below requirement

def calculate_text_similarity(candidate_keywords: List[str], job_description: str) -> float:
    """
    Calculate text similarity score using keyword matching.
    
    Args:
        candidate_keywords (List[str]): Keywords from candidate profile
        job_description (str): Job description text
        
    Returns:
        float: Text similarity score (0-1)
    """
    if not job_description or not candidate_keywords:
        return 0.0
    
    job_description_lower = job_description.lower()
    matches = 0
    
    for keyword in candidate_keywords:
        if keyword and keyword.lower() in job_description_lower:
            matches += 1
    
    if len(candidate_keywords) == 0:
        return 0.0
    
    return matches / len(candidate_keywords)

def rank_candidates(candidates_with_scores: List[Dict]) -> List[Dict]:
    """
    Rank candidates by their match scores.
    
    Args:
        candidates_with_scores (List[Dict]): List of candidates with match scores
        
    Returns:
        List[Dict]: Ranked list of candidates (highest score first)
    """
    return sorted(
        candidates_with_scores,
        key=lambda x: x.get('match_score', 0),
        reverse=True
    )

def find_best_matches(candidates: List[Dict], job_requirements: Dict, top_n: int = 10) -> List[Dict]:
    """
    Find the best matching candidates for a job.
    
    Args:
        candidates (List[Dict]): List of candidate profiles
        job_requirements (Dict): Job requirements
        top_n (int): Number of top candidates to return
        
    Returns:
        List[Dict]: Top matching candidates with scores
    """
    candidates_with_scores = []
    
    for candidate in candidates:
        match_score = calculate_match_score(candidate, job_requirements)
        candidate_with_score = candidate.copy()
        candidate_with_score['match_score'] = match_score
        candidates_with_scores.append(candidate_with_score)
    
    # Rank and return top N
    ranked_candidates = rank_candidates(candidates_with_scores)
    return ranked_candidates[:top_n]

def analyze_match_details(candidate: Dict, job_requirements: Dict) -> Dict:
    """
    Provide detailed analysis of why a candidate matches or doesn't match.
    
    Args:
        candidate (Dict): Candidate profile
        job_requirements (Dict): Job requirements
        
    Returns:
        Dict: Detailed match analysis
    """
    analysis = {
        'overall_score': calculate_match_score(candidate, job_requirements),
        'domain_analysis': {},
        'skills_analysis': {},
        'experience_analysis': {},
        'strengths': [],
        'gaps': [],
        'recommendations': []
    }
    
    # Domain analysis
    domain_score = calculate_domain_match(
        candidate.get('domain', 'General'),
        job_requirements.get('domain', 'General')
    )
    analysis['domain_analysis'] = {
        'score': domain_score,
        'candidate_domain': candidate.get('domain', 'General'),
        'required_domain': job_requirements.get('domain', 'General'),
        'match_level': get_match_level(domain_score)
    }
    
    # Skills analysis
    candidate_skills = candidate.get('skills', [])
    required_skills = job_requirements.get('required_skills', [])
    
    matched_skills = []
    missing_skills = []
    
    for req_skill in required_skills:
        found = False
        for cand_skill in candidate_skills:
            if req_skill.lower() in cand_skill.lower() or cand_skill.lower() in req_skill.lower():
                matched_skills.append(req_skill)
                found = True
                break
        if not found:
            missing_skills.append(req_skill)
    
    skills_score = calculate_skills_match(candidate_skills, required_skills)
    analysis['skills_analysis'] = {
        'score': skills_score,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'additional_skills': [skill for skill in candidate_skills if skill not in matched_skills],
        'match_level': get_match_level(skills_score)
    }
    
    # Experience analysis
    exp_score = calculate_experience_match(
        candidate.get('experience_years', 0),
        job_requirements.get('required_experience', 0)
    )
    analysis['experience_analysis'] = {
        'score': exp_score,
        'candidate_experience': candidate.get('experience_years', 0),
        'required_experience': job_requirements.get('required_experience', 0),
        'match_level': get_match_level(exp_score)
    }
    
    # Identify strengths and gaps
    if domain_score >= 0.7:
        analysis['strengths'].append(f"Strong domain match ({candidate.get('domain', 'General')})")
    else:
        analysis['gaps'].append(f"Domain mismatch (has {candidate.get('domain', 'General')}, needs {job_requirements.get('domain', 'General')})")
    
    if skills_score >= 0.7:
        analysis['strengths'].append(f"Good skills match ({len(matched_skills)}/{len(required_skills)} required skills)")
    else:
        analysis['gaps'].append(f"Missing key skills: {', '.join(missing_skills[:3])}")
    
    if exp_score >= 0.8:
        analysis['strengths'].append(f"Sufficient experience ({candidate.get('experience_years', 0)} years)")
    else:
        analysis['gaps'].append(f"Experience gap (has {candidate.get('experience_years', 0)}, needs {job_requirements.get('required_experience', 0)} years)")
    
    # Generate recommendations
    if missing_skills:
        analysis['recommendations'].append(f"Consider training in: {', '.join(missing_skills[:3])}")
    
    if exp_score < 0.6:
        analysis['recommendations'].append("Consider for junior/training role or mentorship program")
    
    if domain_score < 0.5 and skills_score > 0.6:
        analysis['recommendations'].append("Skills transferable, domain transition possible with training")
    
    return analysis

def get_match_level(score: float) -> str:
    """
    Convert numeric score to descriptive match level.
    
    Args:
        score (float): Match score (0-1)
        
    Returns:
        str: Match level description
    """
    if score >= 0.9:
        return "Excellent"
    elif score >= 0.7:
        return "Good"
    elif score >= 0.5:
        return "Fair"
    elif score >= 0.3:
        return "Poor"
    else:
        return "Very Poor"

def filter_candidates_by_criteria(candidates: List[Dict], filters: Dict) -> List[Dict]:
    """
    Filter candidates based on specific criteria.
    
    Args:
        candidates (List[Dict]): List of candidates
        filters (Dict): Filter criteria
        
    Returns:
        List[Dict]: Filtered candidates
    """
    filtered_candidates = candidates.copy()
    
    # Filter by minimum experience
    if 'min_experience' in filters:
        min_exp = filters['min_experience']
        filtered_candidates = [c for c in filtered_candidates if c.get('experience_years', 0) >= min_exp]
    
    # Filter by domain
    if 'domains' in filters and filters['domains']:
        domains = [d.lower() for d in filters['domains']]
        filtered_candidates = [c for c in filtered_candidates if c.get('domain', '').lower() in domains]
    
    # Filter by required skills
    if 'must_have_skills' in filters and filters['must_have_skills']:
        must_have = [s.lower() for s in filters['must_have_skills']]
        filtered_candidates = []
        for candidate in candidates:
            candidate_skills = [s.lower() for s in candidate.get('skills', [])]
            if any(skill in ' '.join(candidate_skills) for skill in must_have):
                filtered_candidates.append(candidate)
    
    # Filter by education level
    if 'min_education' in filters:
        education_hierarchy = {'certificate': 1, 'associate': 2, 'bachelors': 3, 'masters': 4, 'phd': 5}
        min_edu_level = education_hierarchy.get(filters['min_education'].lower(), 0)
        
        filtered_candidates = [
            c for c in filtered_candidates 
            if education_hierarchy.get(c.get('education', '').lower(), 0) >= min_edu_level
        ]
    
    return filtered_candidates

def generate_hiring_recommendation(candidates: List[Dict], job_requirements: Dict) -> Dict:
    """
    Generate hiring recommendations based on candidate analysis.
    
    Args:
        candidates (List[Dict]): List of analyzed candidates
        job_requirements (Dict): Job requirements
        
    Returns:
        Dict: Hiring recommendations
    """
    if not candidates:
        return {
            'recommendation': 'No suitable candidates found',
            'top_candidates': [],
            'summary': 'Consider expanding search criteria or job posting reach'
        }
    
    # Find top candidates
    top_candidates = find_best_matches(candidates, job_requirements, 5)
    
    # Analyze the pool
    avg_score = sum(c.get('match_score', 0) for c in top_candidates) / len(top_candidates)
    best_score = max(c.get('match_score', 0) for c in top_candidates)
    
    # Generate recommendation
    if best_score >= 0.8:
        recommendation = "Strong candidates available - recommend proceeding with interviews"
    elif best_score >= 0.6:
        recommendation = "Good candidates available - consider interviews with top performers"
    elif best_score >= 0.4:
        recommendation = "Moderate candidates available - may need additional screening or training"
    else:
        recommendation = "Weak candidate pool - consider revising requirements or expanding search"
    
    # Summary statistics
    domains = [c.get('domain', 'Unknown') for c in candidates]
    domain_counts = Counter(domains)
    
    avg_experience = sum(c.get('experience_years', 0) for c in candidates) / len(candidates)
    
    summary = {
        'total_candidates': len(candidates),
        'average_match_score': f"{avg_score:.2f}",
        'best_match_score': f"{best_score:.2f}",
        'domain_distribution': dict(domain_counts.most_common(3)),
        'average_experience': f"{avg_experience:.1f} years"
    }
    
    return {
        'recommendation': recommendation,
        'top_candidates': top_candidates[:3],  # Top 3 for detailed review
        'summary': summary,
        'next_steps': generate_next_steps(best_score, avg_score)
    }

def generate_next_steps(best_score: float, avg_score: float) -> List[str]:
    """
    Generate recommended next steps based on candidate quality.
    
    Args:
        best_score (float): Best candidate match score
        avg_score (float): Average match score
        
    Returns:
        List[str]: Recommended next steps
    """
    next_steps = []
    
    if best_score >= 0.8:
        next_steps.extend([
            "Schedule technical interviews with top 3 candidates",
            "Prepare role-specific assessment questions",
            "Check references for leading candidates"
        ])
    elif best_score >= 0.6:
        next_steps.extend([
            "Conduct phone screenings with top 5 candidates",
            "Assess skill gaps and training needs",
            "Consider flexible requirements for promising candidates"
        ])
    else:
        next_steps.extend([
            "Review and potentially expand job requirements",
            "Consider posting on additional platforms",
            "Evaluate internal training/development options",
            "Review compensation competitiveness"
        ])
    
    if avg_score < 0.4:
        next_steps.append("Consider adjusting role expectations or requirements")
    
    return next_steps

# Test function
def test_matching():
    """Test the matching functions."""
    test_candidate = {
        'name': 'John Doe',
        'domain': 'ML/AI',
        'skills': ['Python', 'TensorFlow', 'Machine Learning', 'AWS'],
        'experience_years': 5
    }
    
    test_job = {
        'domain': 'ML/AI',
        'required_skills': ['Python', 'Machine Learning', 'TensorFlow', 'Docker'],
        'required_experience': 3,
        'job_description': 'Looking for ML engineer with Python and TensorFlow experience'
    }
    
    score = calculate_match_score(test_candidate, test_job)
    analysis = analyze_match_details(test_candidate, test_job)
    
    print(f"Match Score: {score}")
    print(f"Analysis: {analysis}")

if __name__ == "__main__":
    test_matching() 