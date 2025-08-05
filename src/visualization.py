import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

def create_skills_chart(candidates_data: List[Dict], chart_type: str = 'bar') -> go.Figure:
    """
    Create a chart showing the most common skills across candidates.
    
    Args:
        candidates_data (List[Dict]): List of candidate profiles
        chart_type (str): Type of chart ('bar', 'pie', 'treemap')
        
    Returns:
        go.Figure: Plotly figure object
    """
    if not candidates_data:
        return create_empty_chart("No data available")
    
    # Collect all skills
    all_skills = []
    for candidate in candidates_data:
        skills = candidate.get('skills', [])
        all_skills.extend(skills)
    
    if not all_skills:
        return create_empty_chart("No skills data found")
    
    # Count skill frequency
    skill_counts = pd.Series(all_skills).value_counts().head(15)
    
    if chart_type == 'bar':
        fig = px.bar(
            x=skill_counts.values,
            y=skill_counts.index,
            orientation='h',
            title="Top 15 Skills in Candidate Pool",
            labels={'x': 'Number of Candidates', 'y': 'Skills'},
            color=skill_counts.values,
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=500, showlegend=False)
        
    elif chart_type == 'pie':
        fig = px.pie(
            values=skill_counts.values,
            names=skill_counts.index,
            title="Top Skills Distribution"
        )
        
    elif chart_type == 'treemap':
        fig = px.treemap(
            names=skill_counts.index,
            values=skill_counts.values,
            title="Skills Treemap"
        )
    
    else:
        # Default to bar chart
        fig = create_skills_chart(candidates_data, 'bar')
    
    return fig

def create_experience_chart(candidates_data: List[Dict]) -> go.Figure:
    """
    Create a chart showing experience distribution.
    
    Args:
        candidates_data (List[Dict]): List of candidate profiles
        
    Returns:
        go.Figure: Plotly figure object
    """
    if not candidates_data:
        return create_empty_chart("No data available")
    
    experience_years = [candidate.get('experience_years', 0) for candidate in candidates_data]
    
    if not any(experience_years):
        return create_empty_chart("No experience data found")
    
    fig = px.histogram(
        x=experience_years,
        nbins=10,
        title="Experience Distribution",
        labels={'x': 'Years of Experience', 'y': 'Number of Candidates'},
        color_discrete_sequence=['#2E86AB']
    )
    
    # Add mean line
    mean_exp = sum(experience_years) / len(experience_years)
    fig.add_vline(
        x=mean_exp,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Average: {mean_exp:.1f} years"
    )
    
    return fig

def create_domain_distribution(candidates_data: List[Dict]) -> go.Figure:
    """
    Create a chart showing domain distribution.
    
    Args:
        candidates_data (List[Dict]): List of candidate profiles
        
    Returns:
        go.Figure: Plotly figure object
    """
    if not candidates_data:
        return create_empty_chart("No data available")
    
    domains = [candidate.get('domain', 'Unknown') for candidate in candidates_data]
    domain_counts = pd.Series(domains).value_counts()
    
    fig = px.pie(
        values=domain_counts.values,
        names=domain_counts.index,
        title="Candidate Distribution by Domain",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

def create_experience_vs_domain_scatter(candidates_data: List[Dict]) -> go.Figure:
    """
    Create a scatter plot of experience vs domain.
    
    Args:
        candidates_data (List[Dict]): List of candidate profiles
        
    Returns:
        go.Figure: Plotly figure object
    """
    if not candidates_data:
        return create_empty_chart("No data available")
    
    df = pd.DataFrame(candidates_data)
    
    if 'experience_years' not in df.columns or 'domain' not in df.columns:
        return create_empty_chart("Missing required data fields")
    
    fig = px.scatter(
        df,
        x='experience_years',
        y='domain',
        title="Experience by Domain",
        labels={'experience_years': 'Years of Experience', 'domain': 'Domain'},
        color='domain',
        size_max=15
    )
    
    fig.update_layout(height=400)
    
    return fig

def create_seniority_distribution(candidates_data: List[Dict]) -> go.Figure:
    """
    Create a chart showing seniority level distribution.
    
    Args:
        candidates_data (List[Dict]): List of candidate profiles
        
    Returns:
        go.Figure: Plotly figure object
    """
    if not candidates_data:
        return create_empty_chart("No data available")
    
    seniority_levels = [candidate.get('seniority', 'Unknown') for candidate in candidates_data]
    seniority_counts = pd.Series(seniority_levels).value_counts()
    
    # Define custom order for seniority levels
    seniority_order = ['Entry-level', 'Junior', 'Mid-level', 'Senior', 'Principal/Staff']
    ordered_counts = seniority_counts.reindex(seniority_order, fill_value=0)
    
    fig = px.bar(
        x=ordered_counts.index,
        y=ordered_counts.values,
        title="Seniority Level Distribution",
        labels={'x': 'Seniority Level', 'y': 'Number of Candidates'},
        color=ordered_counts.values,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(showlegend=False)
    
    return fig

def create_skills_by_domain_heatmap(candidates_data: List[Dict]) -> go.Figure:
    """
    Create a heatmap showing skills distribution by domain.
    
    Args:
        candidates_data (List[Dict]): List of candidate profiles
        
    Returns:
        go.Figure: Plotly figure object
    """
    if not candidates_data:
        return create_empty_chart("No data available")
    
    # Create domain-skill matrix
    domain_skills = {}
    for candidate in candidates_data:
        domain = candidate.get('domain', 'Unknown')
        skills = candidate.get('skills', [])
        
        if domain not in domain_skills:
            domain_skills[domain] = {}
        
        for skill in skills:
            if skill not in domain_skills[domain]:
                domain_skills[domain][skill] = 0
            domain_skills[domain][skill] += 1
    
    if not domain_skills:
        return create_empty_chart("No domain-skill data found")
    
    # Get top skills overall
    all_skills = []
    for domain, skills in domain_skills.items():
        all_skills.extend(skills.keys())
    top_skills = pd.Series(all_skills).value_counts().head(10).index.tolist()
    
    # Create matrix
    domains = list(domain_skills.keys())
    matrix = []
    
    for domain in domains:
        row = []
        for skill in top_skills:
            count = domain_skills[domain].get(skill, 0)
            row.append(count)
        matrix.append(row)
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=top_skills,
        y=domains,
        colorscale='Blues',
        text=matrix,
        texttemplate="%{text}",
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title="Skills Distribution by Domain",
        xaxis_title="Skills",
        yaxis_title="Domains",
        height=400
    )
    
    return fig

def create_match_score_distribution(candidates_with_scores: List[Dict]) -> go.Figure:
    """
    Create a chart showing match score distribution.
    
    Args:
        candidates_with_scores (List[Dict]): Candidates with match scores
        
    Returns:
        go.Figure: Plotly figure object
    """
    if not candidates_with_scores:
        return create_empty_chart("No match score data available")
    
    match_scores = [candidate.get('match_score', 0) * 100 for candidate in candidates_with_scores]
    
    fig = px.histogram(
        x=match_scores,
        nbins=20,
        title="Match Score Distribution",
        labels={'x': 'Match Score (%)', 'y': 'Number of Candidates'},
        color_discrete_sequence=['#A8DADC']
    )
    
    # Add percentile lines
    percentiles = [25, 50, 75]
    colors = ['orange', 'red', 'purple']
    
    for p, color in zip(percentiles, colors):
        percentile_val = pd.Series(match_scores).quantile(p/100)
        fig.add_vline(
            x=percentile_val,
            line_dash="dash",
            line_color=color,
            annotation_text=f"{p}th percentile: {percentile_val:.1f}%"
        )
    
    return fig

def create_top_candidates_radar(top_candidates: List[Dict], job_requirements: Dict) -> go.Figure:
    """
    Create a radar chart comparing top candidates.
    
    Args:
        top_candidates (List[Dict]): Top candidate profiles
        job_requirements (Dict): Job requirements for context
        
    Returns:
        go.Figure: Plotly figure object
    """
    if not top_candidates:
        return create_empty_chart("No candidate data available")
    
    # Define categories for radar chart
    categories = ['Domain Match', 'Skills Match', 'Experience Match', 'Overall Score']
    
    fig = go.Figure()
    
    for i, candidate in enumerate(top_candidates[:5]):  # Max 5 candidates
        # Calculate individual scores (simplified)
        domain_score = 1.0 if candidate.get('domain') == job_requirements.get('domain') else 0.5
        
        # Skills match ratio
        candidate_skills = set(skill.lower() for skill in candidate.get('skills', []))
        required_skills = set(skill.lower() for skill in job_requirements.get('required_skills', []))
        skills_score = len(candidate_skills & required_skills) / max(len(required_skills), 1)
        
        # Experience score
        exp_ratio = candidate.get('experience_years', 0) / max(job_requirements.get('required_experience', 1), 1)
        exp_score = min(exp_ratio, 1.0)
        
        # Overall score
        overall_score = candidate.get('match_score', 0)
        
        values = [domain_score, skills_score, exp_score, overall_score]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=candidate.get('name', f'Candidate {i+1}'),
            line=dict(width=2)
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="Top Candidates Comparison"
    )
    
    return fig

def create_education_breakdown(candidates_data: List[Dict]) -> go.Figure:
    """
    Create a chart showing education level breakdown.
    
    Args:
        candidates_data (List[Dict]): List of candidate profiles
        
    Returns:
        go.Figure: Plotly figure object
    """
    if not candidates_data:
        return create_empty_chart("No data available")
    
    education_levels = [candidate.get('education', 'Not specified') for candidate in candidates_data]
    education_counts = pd.Series(education_levels).value_counts()
    
    fig = px.pie(
        values=education_counts.values,
        names=education_counts.index,
        title="Education Level Distribution",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    return fig

def create_skills_gap_analysis(candidates_data: List[Dict], required_skills: List[str]) -> go.Figure:
    """
    Create a chart showing skills gap analysis.
    
    Args:
        candidates_data (List[Dict]): List of candidate profiles
        required_skills (List[str]): Required skills for comparison
        
    Returns:
        go.Figure: Plotly figure object
    """
    if not candidates_data or not required_skills:
        return create_empty_chart("Insufficient data for gap analysis")
    
    # Count how many candidates have each required skill
    skill_coverage = {}
    total_candidates = len(candidates_data)
    
    for skill in required_skills:
        count = 0
        for candidate in candidates_data:
            candidate_skills = [s.lower() for s in candidate.get('skills', [])]
            if any(skill.lower() in cs for cs in candidate_skills):
                count += 1
        skill_coverage[skill] = (count / total_candidates) * 100
    
    # Create bar chart
    skills = list(skill_coverage.keys())
    coverage_pcts = list(skill_coverage.values())
    
    # Color bars based on coverage
    colors = ['green' if pct >= 70 else 'orange' if pct >= 40 else 'red' for pct in coverage_pcts]
    
    fig = go.Figure(data=[
        go.Bar(
            x=skills,
            y=coverage_pcts,
            marker_color=colors,
            text=[f'{pct:.1f}%' for pct in coverage_pcts],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Skills Gap Analysis - Required Skills Coverage",
        xaxis_title="Required Skills",
        yaxis_title="Percentage of Candidates with Skill",
        height=400
    )
    
    # Add reference lines
    fig.add_hline(y=70, line_dash="dash", line_color="green", annotation_text="Good Coverage (70%)")
    fig.add_hline(y=40, line_dash="dash", line_color="orange", annotation_text="Moderate Coverage (40%)")
    
    return fig

def create_comprehensive_dashboard(candidates_data: List[Dict], job_requirements: Optional[Dict] = None) -> Dict[str, go.Figure]:
    """
    Create a comprehensive set of charts for the dashboard.
    
    Args:
        candidates_data (List[Dict]): List of candidate profiles
        job_requirements (Optional[Dict]): Job requirements for context
        
    Returns:
        Dict[str, go.Figure]: Dictionary of chart names to figures
    """
    charts = {}
    
    try:
        charts['skills_distribution'] = create_skills_chart(candidates_data, 'bar')
        charts['experience_distribution'] = create_experience_chart(candidates_data)
        charts['domain_distribution'] = create_domain_distribution(candidates_data)
        charts['seniority_distribution'] = create_seniority_distribution(candidates_data)
        charts['experience_vs_domain'] = create_experience_vs_domain_scatter(candidates_data)
        charts['skills_by_domain_heatmap'] = create_skills_by_domain_heatmap(candidates_data)
        charts['education_breakdown'] = create_education_breakdown(candidates_data)
        
        # Add job-specific charts if requirements provided
        if job_requirements and job_requirements.get('required_skills'):
            charts['skills_gap_analysis'] = create_skills_gap_analysis(
                candidates_data, 
                job_requirements['required_skills']
            )
    
    except Exception as e:
        logger.error(f"Error creating charts: {str(e)}")
        charts['error'] = create_empty_chart(f"Error creating visualizations: {str(e)}")
    
    return charts

def create_empty_chart(message: str) -> go.Figure:
    """
    Create an empty chart with a message.
    
    Args:
        message (str): Message to display
        
    Returns:
        go.Figure: Empty chart with message
    """
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        xanchor='center',
        yanchor='middle',
        showarrow=False,
        font=dict(size=16)
    )
    fig.update_layout(
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        plot_bgcolor='white'
    )
    return fig

def customize_chart_theme(fig: go.Figure, theme: str = 'default') -> go.Figure:
    """
    Apply a custom theme to a chart.
    
    Args:
        fig (go.Figure): Plotly figure
        theme (str): Theme name ('default', 'dark', 'minimal')
        
    Returns:
        go.Figure: Themed figure
    """
    if theme == 'dark':
        fig.update_layout(
            plot_bgcolor='#2E2E2E',
            paper_bgcolor='#2E2E2E',
            font_color='white'
        )
    elif theme == 'minimal':
        fig.update_layout(
            plot_bgcolor='white',
            showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
    
    return fig

# Test function
def test_visualizations():
    """Test the visualization functions."""
    test_data = [
        {
            'name': 'John Doe',
            'domain': 'ML/AI',
            'skills': ['Python', 'TensorFlow', 'Machine Learning'],
            'experience_years': 5,
            'education': 'Masters',
            'seniority': 'Senior'
        },
        {
            'name': 'Jane Smith',
            'domain': 'Frontend',
            'skills': ['JavaScript', 'React', 'CSS'],
            'experience_years': 3,
            'education': 'Bachelors',
            'seniority': 'Mid-level'
        }
    ]
    
    charts = create_comprehensive_dashboard(test_data)
    print(f"Created {len(charts)} charts successfully")

if __name__ == "__main__":
    test_visualizations() 