import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
from pathlib import Path

# Import existing modules
from src.pdf_parser import extract_resume_data
from src.nlp_analyzer import analyze_candidate_profile, classify_domain
from src.visualization import create_skills_chart, create_experience_chart, create_domain_distribution
from src.candidate_matcher import calculate_match_score, rank_candidates, find_best_matches, analyze_match_details
from src.database import CandidateDatabase

# Initialize database
@st.cache_resource
def init_database():
    """Initialize database connection (cached for performance)."""
    return CandidateDatabase()

db = init_database()

# Page configuration
st.set_page_config(
    page_title="Resume Analyzer Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS styling
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
.role-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    margin: 0.25rem;
    border-radius: 0.375rem;
    font-weight: 500;
    font-size: 0.875rem;
}
.admin-badge {
    background-color: #dc3545;
    color: white;
}
.recruiter-badge {
    background-color: #0d6efd;
    color: white;
}
.viewer-badge {
    background-color: #6c757d;
    color: white;
}
.metric-card {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
}
</style>
""", unsafe_allow_html=True)

# Role definitions
ROLES = {
    "admin": {
        "name": "Admin",
        "permissions": ["upload", "job_description", "analytics", "feedback", "database", "candidate_dashboard"],
        "pages": ["🏠 Dashboard", "📤 Upload Resumes", "👥 Candidate Dashboard", "🎯 Job Matching", "📊 Analytics", "⭐ Feedback", "🗄️ Database"]
    },
    "recruiter": {
        "name": "Recruiter", 
        "permissions": ["upload", "job_description", "analytics", "feedback", "candidate_dashboard"],
        "pages": ["🏠 Dashboard", "📤 Upload Resumes", "👥 Candidate Dashboard", "🎯 Job Matching", "📊 Analytics", "⭐ Feedback"]
    },
    "viewer": {
        "name": "Viewer",
        "permissions": ["upload", "candidate_dashboard"],
        "pages": ["🏠 Dashboard", "📤 Upload Resumes", "👥 Candidate Dashboard"]
    }
}

def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'feedback_data' not in st.session_state:
        st.session_state.feedback_data = []
    if 'job_requirements' not in st.session_state:
        st.session_state.job_requirements = None
    if 'top_candidates' not in st.session_state:
        st.session_state.top_candidates = []

def show_login_page():
    """Display the login page"""
    st.markdown('<h1 class="main-header">📄 Resume Analyzer Pro</h1>', unsafe_allow_html=True)
    
    st.markdown("### 🔐 Role-Based Access")
    st.info("Choose your role to access different features of the Resume Analyzer.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 👨‍💼 Admin")
        st.write("• Full access to all features")
        st.write("• Analytics and database management")
        st.write("• User feedback and system insights")
        if st.button("Login as Admin", key="admin_login", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_role = "admin"
            st.rerun()
    
    with col2:
        st.markdown("#### 👩‍💼 Recruiter")
        st.write("• Upload and analyze resumes")
        st.write("• Job matching and comparisons")
        st.write("• Provide candidate feedback")
        if st.button("Login as Recruiter", key="recruiter_login", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_role = "recruiter"
            st.rerun()
    
    with col3:
        st.markdown("#### 👤 Viewer")
        st.write("• Upload resumes only")
        st.write("• View basic analytics")
        st.write("• Limited access")
        if st.button("Login as Viewer", key="viewer_login", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_role = "viewer"
            st.rerun()

def show_sidebar():
    """Display sidebar with navigation and user info"""
    user_role = st.session_state.user_role
    role_info = ROLES[user_role]
    
    # User info
    st.sidebar.markdown(f"""
    <div class="role-badge {user_role}-badge">
        {role_info['name']} User
    </div>
    """, unsafe_allow_html=True)
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Navigation
    st.sidebar.markdown("### 📋 Navigation")
    available_pages = role_info["pages"]
    
    selected_page = st.sidebar.selectbox(
        "Choose a page",
        available_pages,
        key="page_selector"
    )
    
    return selected_page

def dashboard_page():
    """Main dashboard page"""
    st.markdown('<h1 class="main-header">📊 Dashboard</h1>', unsafe_allow_html=True)
    
    # Quick stats
    try:
        candidates = db.get_all_candidates()
        stats = db.get_database_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 Total Candidates", stats.get('total_candidates', 0))
        
        with col2:
            avg_exp = stats.get('average_experience', 0)
            st.metric("📈 Avg Experience", f"{avg_exp:.1f} years")
        
        with col3:
            domains = stats.get('domain_distribution', {})
            top_domain = max(domains.items(), key=lambda x: x[1])[0] if domains else "N/A"
            st.metric("🏢 Top Domain", top_domain)
        
        with col4:
            feedback_count = len(st.session_state.feedback_data)
            st.metric("⭐ Feedback Items", feedback_count)
        
        # Recent activity
        st.markdown("### 📈 Recent Activity")
        
        if candidates:
            recent_candidates = sorted(candidates, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
            
            st.markdown("**Recent Candidates:**")
            for candidate in recent_candidates:
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.write(f"👤 {candidate.get('name', 'Unknown')}")
                with col2:
                    st.write(f"🏢 {candidate.get('domain', 'Unknown')}")
                with col3:
                    st.write(f"⏱️ {candidate.get('experience_years', 0)} years")
        else:
            st.info("No candidates uploaded yet. Start by uploading some resumes!")
            
    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")

def upload_resumes_page():
    """Resume upload and analysis page"""
    st.markdown('<h1 class="main-header">📤 Upload & Analyze Resumes</h1>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose PDF files", 
        type="pdf", 
        accept_multiple_files=True,
        help="Upload one or more PDF resume files for analysis"
    )
    
    if uploaded_files:
        if st.button("🔍 Analyze Resumes", type="primary"):
            progress_bar = st.progress(0)
            candidates_processed = 0
            total_files = len(uploaded_files)
            
            for i, uploaded_file in enumerate(uploaded_files):
                try:
                    progress_bar.progress((i + 1) / total_files)
                    
                    with st.spinner(f"Processing {uploaded_file.name}..."):
                        # Extract resume data
                        resume_data = extract_resume_data(uploaded_file)
                        
                        # Analyze candidate profile
                        profile = analyze_candidate_profile(resume_data)
                        
                        # Classify domain
                        domain = classify_domain(resume_data.get('raw_text', ''))
                        profile['domain'] = domain
                        
                        # Prepare candidate info
                        candidate_info = {
                            'name': profile.get('name', 'Unknown'),
                            'email': profile.get('email', 'Not provided'),
                            'phone': profile.get('phone', 'Not provided'),
                            'linkedin': profile.get('linkedin', 'Not provided'),
                            'domain': domain,
                            'skills': profile.get('skills', []),
                            'experience_years': profile.get('experience_years', 0),
                            'education': profile.get('education', 'Not specified'),
                            'seniority': profile.get('seniority', 'Entry'),
                            'filename': uploaded_file.name
                        }
                        
                        # Save to database
                        candidate_id = db.save_candidate(candidate_info, profile, resume_data)
                        candidate_info['id'] = candidate_id
                        
                        candidates_processed += 1
                        
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            
            progress_bar.progress(1.0)
            st.success(f"✅ Successfully processed {candidates_processed} out of {total_files} resumes!")
            
            # Show quick summary
            if candidates_processed > 0:
                st.markdown("### 📊 Quick Summary")
                candidates = db.get_all_candidates()
                
                if candidates:
                    df = pd.DataFrame(candidates)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Domain distribution
                        domain_counts = df['domain'].value_counts()
                        fig_domain = px.pie(
                            values=domain_counts.values,
                            names=domain_counts.index,
                            title="Domain Distribution"
                        )
                        st.plotly_chart(fig_domain, use_container_width=True)
                    
                    with col2:
                        # Experience distribution
                        fig_exp = px.histogram(
                            df,
                            x='experience_years',
                            title="Experience Distribution",
                            labels={'experience_years': 'Years of Experience', 'count': 'Number of Candidates'}
                        )
                        st.plotly_chart(fig_exp, use_container_width=True)

def job_matching_page():
    """Job description input and candidate matching"""
    st.markdown('<h1 class="main-header">🎯 Job Matching & Filtering</h1>', unsafe_allow_html=True)
    
    # Simplified filters for recruiters
    st.markdown("### 🔍 Candidate Filters")
    st.info("Use these filters to find the best matching candidates for your role.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Domain selection
        domain = st.selectbox(
            "🏢 Select Domain *", 
            ["ML/AI", "Frontend", "Backend", "Data Engineering", "Analyst", "DevOps", "Mobile", "Testing", "Full Stack"],
            help="Choose the primary technical domain for this role"
        )
        
        # Experience filter
        experience_range = st.slider(
            "📈 Experience Range (years) *",
            min_value=0,
            max_value=15,
            value=(2, 8),
            help="Select minimum and maximum years of experience required"
        )
        min_experience, max_experience = experience_range
    
    with col2:
        # Skills filter
        skills_input = st.text_area(
            "🎯 Required Skills * (one per line)", 
            value="Python\nReact\nSQL\nGit",
            height=100,
            help="Enter the most important skills for this role"
        )
        
        required_skills = [skill.strip() for skill in skills_input.split('\n') if skill.strip()]
        
        # Optional skills filter
        optional_skills = st.text_input(
            "➕ Nice-to-Have Skills (comma separated)",
            placeholder="Docker, AWS, Kubernetes",
            help="Optional skills that would be a bonus"
        )
        
        nice_to_have_skills = [skill.strip() for skill in optional_skills.split(',') if skill.strip()] if optional_skills else []
    
    # Job description
    job_description = st.text_area(
        "📝 Job Description *", 
        value="We are looking for a skilled developer to join our team...",
        height=120,
        help="Provide a brief description of the role and responsibilities"
    )
    
    if st.button("🔍 Find Top 10 Candidates", type="primary"):
        # Validation
        if not required_skills:
            st.error("❌ Please enter at least one required skill.")
            return
        
        if not job_description.strip():
            st.error("❌ Please provide a job description.")
            return
        
        # Store job requirements with simplified structure
        job_requirements = {
            'domain': domain,
            'min_experience': min_experience,
            'max_experience': max_experience,
            'required_experience': min_experience,  # For compatibility with existing matcher
            'required_skills': required_skills,
            'nice_to_have_skills': nice_to_have_skills,
            'job_description': job_description
        }
        
        st.session_state.job_requirements = job_requirements
        
        # Get candidates from database
        candidates = db.get_all_candidates()
        
        if not candidates:
            st.warning("No candidates available. Please upload some resumes first.")
            return
        
        # Filter candidates by domain and experience first
        filtered_candidates = []
        
        for candidate in candidates:
            # Domain filtering with flexible matching
            candidate_domain = candidate.get('domain', '').lower()
            selected_domain = domain.lower()
            
            domain_match = False
            if selected_domain in candidate_domain or candidate_domain in selected_domain:
                domain_match = True
            elif selected_domain == 'ml/ai' and any(term in candidate_domain for term in ['ml', 'ai', 'machine learning', 'data science']):
                domain_match = True
            elif selected_domain == 'frontend' and any(term in candidate_domain for term in ['frontend', 'front-end', 'ui', 'react', 'angular', 'vue']):
                domain_match = True
            elif selected_domain == 'backend' and any(term in candidate_domain for term in ['backend', 'back-end', 'api', 'server']):
                domain_match = True
            elif selected_domain == 'full stack' and any(term in candidate_domain for term in ['full stack', 'fullstack', 'full-stack']):
                domain_match = True
            elif selected_domain == 'data engineering' and any(term in candidate_domain for term in ['data engineer', 'data engineering', 'etl', 'pipeline']):
                domain_match = True
            elif selected_domain == 'devops' and any(term in candidate_domain for term in ['devops', 'dev ops', 'infrastructure', 'cloud']):
                domain_match = True
            elif selected_domain == 'mobile' and any(term in candidate_domain for term in ['mobile', 'android', 'ios', 'react native', 'flutter']):
                domain_match = True
            elif selected_domain == 'testing' and any(term in candidate_domain for term in ['test', 'qa', 'quality assurance']):
                domain_match = True
            elif selected_domain == 'analyst' and any(term in candidate_domain for term in ['analyst', 'analysis', 'business intelligence', 'bi']):
                domain_match = True
            
            # Experience filtering
            candidate_exp = candidate.get('experience_years', 0)
            experience_match = min_experience <= candidate_exp <= max_experience
            
            # Include candidate if either domain or experience matches (flexible filtering)
            if domain_match or experience_match:
                filtered_candidates.append(candidate)
        
        if not filtered_candidates:
            st.warning(f"No candidates found matching {domain} domain or {min_experience}-{max_experience} years experience. Showing all candidates.")
            filtered_candidates = candidates
        
        # Get top 10 matching candidates using the matcher
        top_10_candidates = find_best_matches(filtered_candidates, job_requirements, top_n=10)
        
        if not top_10_candidates:
            st.warning("No matching candidates found.")
            return
        
        # Store results
        st.session_state.top_candidates = top_10_candidates[:5]  # Store top 5 for feedback
        
        # Show applied filters
        st.markdown("### 🔍 Applied Filters")
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            st.info(f"**Domain:** {domain}")
            
        with filter_col2:
            st.info(f"**Experience:** {min_experience}-{max_experience} years")
            
        with filter_col3:
            st.info(f"**Skills:** {len(required_skills)} required")
        
        st.markdown(f"**📋 Required Skills:** {', '.join(required_skills)}")
        if nice_to_have_skills:
            st.markdown(f"**⭐ Nice-to-Have:** {', '.join(nice_to_have_skills)}")
        
        st.divider()
        
        # Display filtering results
        st.markdown(f"### 🏆 Top 10 Candidates from {len(filtered_candidates)} Filtered Profiles")
        
        if len(filtered_candidates) < len(candidates):
            st.success(f"✅ Filtered down from {len(candidates)} total candidates to {len(filtered_candidates)} matching your criteria")
        
        # Create summary table for all 10
        summary_data = []
        for i, candidate in enumerate(top_10_candidates):
            match_percentage = round(candidate.get('match_score', 0) * 100, 1)
            
            # Calculate skills match for quick overview
            candidate_skills = set(skill.lower() for skill in candidate.get('skills', []))
            required_skills_set = set(skill.lower() for skill in required_skills)
            matched_skills_count = len(candidate_skills & required_skills_set)
            
            summary_data.append({
                'Rank': f"#{i+1}",
                'Name': candidate.get('name', 'Unknown'),
                'Match Score': f"{match_percentage}%",
                'Experience': f"{candidate.get('experience_years', 0)} years",
                'Domain': candidate.get('domain', 'Unknown'),
                'Skills Match': f"{matched_skills_count}/{len(required_skills)}",
                'Email': candidate.get('email', 'N/A') if st.session_state.user_role in ['recruiter', 'admin'] else 'Hidden'
            })
        
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, use_container_width=True)
        
        # Top 5 Detailed Comparison
        st.markdown("### 📊 Top 5 Candidates - Detailed Skills Analysis")
        
        top_5_candidates = top_10_candidates[:5]
        
        # Create comparison chart for top 5
        comparison_data = []
        detailed_analysis = []
        
        for i, candidate in enumerate(top_5_candidates):
            # Get detailed analysis using candidate_matcher
            analysis = analyze_match_details(candidate, job_requirements)
            detailed_analysis.append(analysis)
            
            match_percentage = round(candidate.get('match_score', 0) * 100, 1)
            matched_skills = analysis['skills_analysis']['matched_skills']
            missing_skills = analysis['skills_analysis']['missing_skills']
            
            comparison_data.append({
                'Rank': i + 1,
                'Name': candidate.get('name', 'Unknown'),
                'Match %': match_percentage,
                'Matched Skills': len(matched_skills),
                'Missing Skills': len(missing_skills),
                'Experience Gap': candidate.get('experience_years', 0) - required_experience
            })
        
        # Display comparison chart
        df_comparison = pd.DataFrame(comparison_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Match score comparison
            fig_scores = px.bar(
                df_comparison, 
                x='Name', 
                y='Match %',
                title="Match Score Comparison - Top 5",
                color='Match %',
                color_continuous_scale='RdYlGn'
            )
            fig_scores.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig_scores, use_container_width=True, key="match_scores_chart")
        
        with col2:
            # Skills gap analysis
            fig_skills = px.bar(
                df_comparison,
                x='Name',
                y=['Matched Skills', 'Missing Skills'],
                title="Skills Analysis - Top 5",
                barmode='stack'
            )
            fig_skills.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_skills, use_container_width=True, key="skills_analysis_chart")
        
        # Detailed individual analysis
        st.markdown("### 🔍 Individual Candidate Analysis")
        
        tabs = st.tabs([f"#{i+1} {candidate.get('name', 'Unknown')}" for i, candidate in enumerate(top_5_candidates)])
        
        for i, (tab, candidate, analysis) in enumerate(zip(tabs, top_5_candidates, detailed_analysis)):
            with tab:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📋 Candidate Profile")
                    st.write(f"**Name:** {candidate.get('name', 'Unknown')}")
                    st.write(f"**Match Score:** {round(analysis['overall_score'] * 100, 1)}%")
                    st.write(f"**Experience:** {candidate.get('experience_years', 0)} years")
                    st.write(f"**Domain:** {candidate.get('domain', 'Unknown')}")
                    st.write(f"**Education:** {candidate.get('education', 'Unknown')}")
                    
                    # Contact info (only for recruiter/admin)
                    if st.session_state.user_role in ['recruiter', 'admin']:
                        st.markdown("#### 📞 Contact Information")
                        st.write(f"**Email:** {candidate.get('email', 'N/A')}")
                        st.write(f"**Phone:** {candidate.get('phone', 'N/A')}")
                        st.write(f"**LinkedIn:** {candidate.get('linkedin', 'N/A')}")
                    
                    # Strengths and gaps
                    if analysis['strengths']:
                        st.markdown("#### ✅ Strengths")
                        for strength in analysis['strengths']:
                            st.write(f"• {strength}")
                    
                    if analysis['gaps']:
                        st.markdown("#### ⚠️ Areas for Improvement")
                        for gap in analysis['gaps']:
                            st.write(f"• {gap}")
                
                with col2:
                    st.markdown("#### 🎯 Skills Breakdown")
                    
                    skills_analysis = analysis['skills_analysis']
                    
                    # Matched skills
                    if skills_analysis['matched_skills']:
                        st.markdown("**✅ Matched Skills:**")
                        for skill in skills_analysis['matched_skills']:
                            st.success(f"✓ {skill}")
                    
                    # Missing skills
                    if skills_analysis['missing_skills']:
                        st.markdown("**❌ Missing Skills:**")
                        for skill in skills_analysis['missing_skills']:
                            st.error(f"✗ {skill}")
                    
                    # Nice-to-have skills
                    if nice_to_have_skills:
                        candidate_skills_lower = set(skill.lower() for skill in candidate.get('skills', []))
                        nice_skills_set = set(skill.lower() for skill in nice_to_have_skills)
                        matched_nice_skills = candidate_skills_lower & nice_skills_set
                        
                        if matched_nice_skills:
                            st.markdown("**⭐ Bonus Skills (Nice-to-Have):**")
                            for skill in matched_nice_skills:
                                st.success(f"⭐ {skill.title()}")
                    
                    # Additional skills
                    additional_skills = skills_analysis.get('additional_skills', [])
                    if additional_skills:
                        st.markdown("**➕ Other Skills:**")
                        for skill in additional_skills[:5]:  # Show top 5
                            st.info(f"+ {skill}")
                        if len(additional_skills) > 5:
                            st.write(f"... and {len(additional_skills) - 5} more skills")
                    
                    # Skills coverage gauge
                    total_required = len(job_requirements.get('required_skills', []))
                    matched_count = len(skills_analysis['matched_skills'])
                    coverage_percentage = (matched_count / total_required * 100) if total_required > 0 else 0
                    
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=coverage_percentage,
                        title={'text': f"Skills Coverage<br>{matched_count}/{total_required} skills"},
                        gauge={
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 50], 'color': "lightgray"},
                                {'range': [50, 80], 'color': "yellow"},
                                {'range': [80, 100], 'color': "green"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 90
                            }
                        }
                    ))
                    fig_gauge.update_layout(height=300)
                    st.plotly_chart(fig_gauge, use_container_width=True, key=f"gauge_chart_{i}")
                
                # Recommendations
                if analysis['recommendations']:
                    st.markdown("#### 💡 Recommendations")
                    for rec in analysis['recommendations']:
                        st.write(f"• {rec}")
        
        # Summary insights
        st.markdown("### 📋 Hiring Summary & Insights")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_score = sum(c.get('match_score', 0) for c in top_5_candidates) / len(top_5_candidates)
            st.metric("Average Match Score", f"{avg_score*100:.1f}%")
        
        with col2:
            perfect_matches = sum(1 for c in top_5_candidates if c.get('match_score', 0) >= 0.9)
            st.metric("Excellent Matches", f"{perfect_matches}/5")
        
        with col3:
            total_missing_skills = sum(len(analysis['skills_analysis']['missing_skills']) for analysis in detailed_analysis)
            avg_missing = total_missing_skills / len(detailed_analysis)
            st.metric("Avg Missing Skills", f"{avg_missing:.1f}")
        
        with col4:
            # Calculate nice-to-have skills coverage
            if nice_to_have_skills:
                nice_to_have_matches = 0
                for candidate in top_5_candidates:
                    candidate_skills = set(skill.lower() for skill in candidate.get('skills', []))
                    nice_skills_set = set(skill.lower() for skill in nice_to_have_skills)
                    nice_to_have_matches += len(candidate_skills & nice_skills_set)
                avg_bonus = nice_to_have_matches / len(top_5_candidates) if nice_to_have_skills else 0
                st.metric("Avg Bonus Skills", f"{avg_bonus:.1f}")
            else:
                st.metric("Bonus Skills", "N/A")
        
        # Filter effectiveness
        st.markdown("#### 🎯 Filter Effectiveness")
        filter_effectiveness = (len(filtered_candidates) / len(candidates)) * 100
        
        if filter_effectiveness < 30:
            st.success(f"🎯 **Highly Selective**: Filters reduced candidate pool by {100-filter_effectiveness:.0f}% ({len(candidates)} → {len(filtered_candidates)})")
        elif filter_effectiveness < 60:
            st.info(f"🔍 **Moderately Selective**: Filters reduced candidate pool by {100-filter_effectiveness:.0f}% ({len(candidates)} → {len(filtered_candidates)})")
        else:
            st.warning(f"📢 **Broad Search**: Filters included {filter_effectiveness:.0f}% of candidates ({len(filtered_candidates)}/{len(candidates)})")
        
        # Domain analysis
        domain_candidates = [c for c in filtered_candidates if domain.lower() in c.get('domain', '').lower()]
        if domain_candidates:
            domain_percentage = (len(domain_candidates) / len(filtered_candidates)) * 100
            st.write(f"**Domain Match**: {len(domain_candidates)} candidates ({domain_percentage:.0f}%) match the {domain} domain")
        
        # Recommendations based on analysis
        st.markdown("#### 🎯 Hiring Recommendations")
        
        if avg_score >= 0.8:
            st.success("🟢 **Strong candidate pool** - Recommend proceeding with interviews for top 3 candidates")
        elif avg_score >= 0.6:
            st.warning("🟡 **Good candidate pool** - Consider interviews with skills assessment for top candidates")
        else:
            st.error("🔴 **Weak candidate pool** - Consider revising requirements or expanding search")
        
        # Next steps
        next_steps = []
        if perfect_matches > 0:
            next_steps.append("Schedule technical interviews with excellent matches")
        if avg_missing < 2:
            next_steps.append("Focus on behavioral and cultural fit interviews")
        else:
            next_steps.append("Assess willingness to learn missing skills")
        
        if next_steps:
            st.markdown("**Recommended Next Steps:**")
            for step in next_steps:
                st.write(f"• {step}")

def feedback_page():
    """Feedback collection page for recruiters"""
    st.markdown('<h1 class="main-header">⭐ Candidate Feedback</h1>', unsafe_allow_html=True)
    
    if not st.session_state.top_candidates:
        st.warning("No candidates selected for feedback. Please run job matching first.")
        return
    
    st.markdown("### 📝 Provide Feedback on Top 5 Candidates")
    st.info("Your feedback helps improve our matching algorithm over time.")
    
    for i, candidate in enumerate(st.session_state.top_candidates):
        st.markdown(f"#### 🥇 Candidate {i+1}: {candidate.get('name', 'Unknown')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Overall rating
            overall_rating = st.slider(
                f"Overall Rating", 
                1, 5, 3,
                key=f"overall_{i}",
                help="How well does this candidate match the job requirements?"
            )
            
            # Skills rating
            skills_rating = st.slider(
                f"Skills Match", 
                1, 5, 3,
                key=f"skills_{i}",
                help="How well do the candidate's skills match the requirements?"
            )
            
            # Experience rating
            experience_rating = st.slider(
                f"Experience Level", 
                1, 5, 3,
                key=f"experience_{i}",
                help="Is the candidate's experience appropriate for this role?"
            )
        
        with col2:
            # Interview interest
            interview_interest = st.selectbox(
                f"Interview Interest",
                ["Definitely Yes", "Yes", "Maybe", "No", "Definitely No"],
                index=2,
                key=f"interview_{i}"
            )
            
            # Feedback comments
            comments = st.text_area(
                f"Additional Comments",
                key=f"comments_{i}",
                placeholder="Any specific feedback about this candidate..."
            )
        
        # Save feedback button
        if st.button(f"💾 Save Feedback for {candidate.get('name', 'Candidate')}", key=f"save_{i}"):
            feedback_entry = {
                'candidate_id': candidate.get('id'),
                'candidate_name': candidate.get('name', 'Unknown'),
                'job_title': st.session_state.job_requirements.get('job_title', 'Unknown'),
                'overall_rating': overall_rating,
                'skills_rating': skills_rating,
                'experience_rating': experience_rating,
                'interview_interest': interview_interest,
                'comments': comments,
                'feedback_date': datetime.now().isoformat(),
                'recruiter': st.session_state.user_role
            }
            
            st.session_state.feedback_data.append(feedback_entry)
            st.success(f"✅ Feedback saved for {candidate.get('name', 'candidate')}!")
    
    # Show feedback summary
    if st.session_state.feedback_data:
        st.markdown("### 📊 Feedback Summary")
        
        feedback_df = pd.DataFrame(st.session_state.feedback_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            avg_overall = feedback_df['overall_rating'].mean()
            st.metric("Average Overall Rating", f"{avg_overall:.1f}/5")
            
            avg_skills = feedback_df['skills_rating'].mean()
            st.metric("Average Skills Rating", f"{avg_skills:.1f}/5")
        
        with col2:
            interview_counts = feedback_df['interview_interest'].value_counts()
            
            fig = px.pie(
                values=interview_counts.values,
                names=interview_counts.index,
                title="Interview Interest Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

def analytics_page():
    """Analytics dashboard"""
    st.markdown('<h1 class="main-header">📊 Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    try:
        candidates = db.get_all_candidates()
        
        if not candidates:
            st.warning("No candidate data available. Please upload some resumes first.")
            return
        
        df = pd.DataFrame(candidates)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Candidates", len(candidates))
        
        with col2:
            avg_experience = df['experience_years'].mean()
            st.metric("Avg Experience", f"{avg_experience:.1f} years")
        
        with col3:
            total_feedback = len(st.session_state.feedback_data)
            st.metric("Feedback Items", total_feedback)
        
        with col4:
            if st.session_state.feedback_data:
                avg_rating = pd.DataFrame(st.session_state.feedback_data)['overall_rating'].mean()
                st.metric("Avg Rating", f"{avg_rating:.1f}/5")
            else:
                st.metric("Avg Rating", "N/A")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Domain distribution
            domain_counts = df['domain'].value_counts()
            fig_domain = px.bar(
                x=domain_counts.values,
                y=domain_counts.index,
                orientation='h',
                title="Candidates by Domain",
                labels={'x': 'Number of Candidates', 'y': 'Domain'}
            )
            st.plotly_chart(fig_domain, use_container_width=True)
        
        with col2:
            # Experience distribution
            fig_exp = px.histogram(
                df,
                x='experience_years',
                title="Experience Distribution",
                labels={'experience_years': 'Years of Experience', 'count': 'Count'}
            )
            st.plotly_chart(fig_exp, use_container_width=True)
        
        # Feedback analytics
        if st.session_state.feedback_data:
            st.markdown("### 📈 Feedback Analytics")
            
            feedback_df = pd.DataFrame(st.session_state.feedback_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Rating trends
                rating_cols = ['overall_rating', 'skills_rating', 'experience_rating']
                rating_means = feedback_df[rating_cols].mean()
                
                fig_ratings = px.bar(
                    x=rating_means.index,
                    y=rating_means.values,
                    title="Average Ratings by Category",
                    labels={'x': 'Rating Category', 'y': 'Average Rating'}
                )
                st.plotly_chart(fig_ratings, use_container_width=True)
            
            with col2:
                # Interview interest
                interview_counts = feedback_df['interview_interest'].value_counts()
                
                fig_interview = px.pie(
                    values=interview_counts.values,
                    names=interview_counts.index,
                    title="Interview Interest Distribution"
                )
                st.plotly_chart(fig_interview, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading analytics data: {str(e)}")

def database_page():
    """Database management page (admin only)"""
    st.markdown('<h1 class="main-header">🗄️ Database Management</h1>', unsafe_allow_html=True)
    
    try:
        candidates = db.get_all_candidates()
        stats = db.get_database_stats()
        
        # Database statistics
        st.markdown("### 📊 Database Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Candidates", stats.get('total_candidates', 0))
        
        with col2:
            st.metric("Average Experience", f"{stats.get('average_experience', 0):.1f} years")
        
        with col3:
            domains = stats.get('domain_distribution', {})
            domain_count = len(domains)
            st.metric("Unique Domains", domain_count)
        
        with col4:
            total_skills = stats.get('top_skills', {})
            skills_count = len(total_skills)
            st.metric("Unique Skills", skills_count)
        
        # Candidates table
        st.markdown("### 👥 All Candidates")
        
        if candidates:
            df = pd.DataFrame(candidates)
            
            # Select columns to display
            display_columns = ['name', 'domain', 'experience_years', 'education', 'created_at']
            available_columns = [col for col in display_columns if col in df.columns]
            
            if available_columns:
                st.dataframe(df[available_columns], use_container_width=True)
            else:
                st.dataframe(df, use_container_width=True)
            
            # Export functionality
            if st.button("📥 Export to CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No candidates in database.")
        
        # Database actions
        st.markdown("### ⚙️ Database Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh Database", type="secondary"):
                st.cache_resource.clear()
                st.success("Database cache refreshed!")
                st.rerun()
        
        with col2:
            if st.button("⚠️ Clear All Data", type="secondary"):
                if st.checkbox("I understand this will delete all data"):
                    # Implementation would go here
                    st.warning("Feature not implemented for safety.")
        
    except Exception as e:
        st.error(f"Error accessing database: {str(e)}")

def candidate_dashboard_page():
    """Advanced candidate dashboard with filtering capabilities"""
    st.markdown('<h1 class="main-header">👥 Candidate Dashboard</h1>', unsafe_allow_html=True)
    
    # Fetch all candidates from database
    try:
        candidates = db.get_all_candidates()
        if not candidates:
            st.warning("📂 No candidates available. Please upload some resumes first.")
            return
        
        # Get database statistics
        stats = db.get_database_stats()
        
        # Overview Statistics
        st.markdown("### 📊 Overview Statistics")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("👥 Total Candidates", stats.get('total_candidates', 0))
        
        with col2:
            avg_exp = stats.get('average_experience', 0)
            st.metric("📈 Avg Experience", f"{avg_exp:.1f} years")
        
        with col3:
            domains = stats.get('domain_distribution', {})
            unique_domains = len(domains)
            st.metric("🏢 Domains", unique_domains)
        
        with col4:
            skills = stats.get('top_skills', {})
            total_skills = len(skills)
            st.metric("🎯 Total Skills", total_skills)
        
        with col5:
            # Calculate candidates with complete profiles
            complete_profiles = len([c for c in candidates if c.get('email') and c.get('phone') and c.get('skills')])
            st.metric("✅ Complete Profiles", complete_profiles)
        
        st.divider()
        
        # Advanced Filters Section
        st.markdown("### 🔍 Advanced Filters")
        st.info("Use these filters to find candidates matching your specific criteria.")
        
        # Filter row 1
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            # Domain filter
            domain_options = ["All Domains", "ML/AI", "Data Engineering", "DevOps", "Frontend", "Backend", "Mobile", "Full Stack", "Testing", "Analyst", "General"]
            selected_domain = st.selectbox(
                "🏢 Filter by Domain",
                domain_options,
                help="Select a specific technical domain"
            )
        
        with filter_col2:
            # Experience filter
            experience_range = st.slider(
                "📈 Experience Range (years)",
                min_value=0,
                max_value=20,
                value=(0, 20),
                help="Filter candidates by years of experience"
            )
            min_exp, max_exp = experience_range
        
        with filter_col3:
            # Education filter
            education_options = ["All Education", "High School", "Associate", "Bachelor's", "Master's", "PhD"]
            selected_education = st.selectbox(
                "🎓 Education Level",
                education_options,
                help="Filter by minimum education level"
            )
        
        # Filter row 2
        filter_col4, filter_col5, filter_col6 = st.columns(3)
        
        with filter_col4:
            # Skills filter
            all_skills = set()
            for candidate in candidates:
                if candidate.get('skills'):
                    all_skills.update([skill.strip().lower() for skill in candidate['skills']])
            
            skills_list = sorted(list(all_skills))
            selected_skills = st.multiselect(
                "🎯 Filter by Skills",
                skills_list,
                help="Select one or more skills to filter candidates"
            )
        
        with filter_col5:
            # Seniority filter
            seniority_options = ["All Levels", "Junior", "Mid-Level", "Senior", "Lead", "Principal"]
            selected_seniority = st.selectbox(
                "🏆 Seniority Level",
                seniority_options,
                help="Filter by seniority level"
            )
        
        with filter_col6:
            # Search by name
            search_name = st.text_input(
                "👤 Search by Name",
                placeholder="Enter candidate name...",
                help="Search for specific candidates by name"
            )
        
        # Filter row 3 - Additional filters
        filter_col7, filter_col8, filter_col9 = st.columns(3)
        
        with filter_col7:
            # Sort options
            sort_options = ["Name (A-Z)", "Name (Z-A)", "Experience (High-Low)", "Experience (Low-High)", "Recently Added"]
            sort_by = st.selectbox(
                "📋 Sort By",
                sort_options,
                help="Choose how to sort the candidates"
            )
        
        with filter_col8:
            # Results per page
            results_per_page = st.selectbox(
                "📄 Results per Page",
                [10, 25, 50, 100],
                index=1,
                help="Number of candidates to display per page"
            )
        
        with filter_col9:
            # Quick actions
            col_action1, col_action2 = st.columns(2)
            with col_action1:
                if st.button("🔄 Reset Filters", help="Clear all filters"):
                    st.rerun()
            with col_action2:
                if st.button("📊 Export Results", help="Export filtered results"):
                    st.info("Export functionality coming soon!")
        
        # Apply filters
        filtered_candidates = candidates.copy()
        
        # Domain filtering
        if selected_domain != "All Domains":
            filtered_candidates = [
                c for c in filtered_candidates 
                if selected_domain.lower() in c.get('domain', '').lower() or
                   (selected_domain == "ML/AI" and any(term in c.get('domain', '').lower() for term in ['ml', 'ai', 'machine learning', 'data science'])) or
                   (selected_domain == "Data Engineering" and any(term in c.get('domain', '').lower() for term in ['data engineer', 'etl', 'pipeline'])) or
                   (selected_domain == "DevOps" and any(term in c.get('domain', '').lower() for term in ['devops', 'infrastructure', 'cloud'])) or
                   (selected_domain == "Frontend" and any(term in c.get('domain', '').lower() for term in ['frontend', 'front-end', 'ui', 'react', 'angular'])) or
                   (selected_domain == "Backend" and any(term in c.get('domain', '').lower() for term in ['backend', 'back-end', 'api', 'server'])) or
                   (selected_domain == "Mobile" and any(term in c.get('domain', '').lower() for term in ['mobile', 'android', 'ios', 'react native'])) or
                   (selected_domain == "Full Stack" and any(term in c.get('domain', '').lower() for term in ['full stack', 'fullstack'])) or
                   (selected_domain == "Testing" and any(term in c.get('domain', '').lower() for term in ['test', 'qa', 'quality assurance'])) or
                   (selected_domain == "Analyst" and any(term in c.get('domain', '').lower() for term in ['analyst', 'analysis', 'business intelligence']))
            ]
        
        # Experience filtering
        filtered_candidates = [
            c for c in filtered_candidates 
            if min_exp <= c.get('experience_years', 0) <= max_exp
        ]
        
        # Education filtering
        if selected_education != "All Education":
            education_hierarchy = {"High School": 1, "Associate": 2, "Bachelor's": 3, "Master's": 4, "PhD": 5}
            min_education_level = education_hierarchy.get(selected_education, 0)
            filtered_candidates = [
                c for c in filtered_candidates
                if education_hierarchy.get(c.get('education', ''), 0) >= min_education_level
            ]
        
        # Skills filtering
        if selected_skills:
            filtered_candidates = [
                c for c in filtered_candidates
                if any(skill.lower() in [s.lower() for s in c.get('skills', [])] for skill in selected_skills)
            ]
        
        # Seniority filtering
        if selected_seniority != "All Levels":
            filtered_candidates = [
                c for c in filtered_candidates
                if selected_seniority.lower() in c.get('seniority', '').lower()
            ]
        
        # Name search
        if search_name:
            filtered_candidates = [
                c for c in filtered_candidates
                if search_name.lower() in c.get('name', '').lower()
            ]
        
        # Sorting
        if sort_by == "Name (A-Z)":
            filtered_candidates.sort(key=lambda x: x.get('name', '').lower())
        elif sort_by == "Name (Z-A)":
            filtered_candidates.sort(key=lambda x: x.get('name', '').lower(), reverse=True)
        elif sort_by == "Experience (High-Low)":
            filtered_candidates.sort(key=lambda x: x.get('experience_years', 0), reverse=True)
        elif sort_by == "Experience (Low-High)":
            filtered_candidates.sort(key=lambda x: x.get('experience_years', 0))
        elif sort_by == "Recently Added":
            filtered_candidates.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Results section
        st.divider()
        st.markdown(f"### 📋 Filtered Results ({len(filtered_candidates)} candidates)")
        
        if len(filtered_candidates) == 0:
            st.warning("🔍 No candidates match your current filter criteria. Try adjusting your filters.")
            return
        
        # Filter effectiveness
        filter_effectiveness = (len(filtered_candidates) / len(candidates)) * 100
        if filter_effectiveness < 100:
            st.success(f"🎯 Filters reduced candidate pool by {100-filter_effectiveness:.0f}% ({len(candidates)} → {len(filtered_candidates)})")
        
        # Pagination
        total_pages = (len(filtered_candidates) - 1) // results_per_page + 1
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1
        
        if total_pages > 1:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            with col1:
                if st.button("⬅️ Previous", disabled=st.session_state.current_page <= 1):
                    st.session_state.current_page -= 1
                    st.rerun()
            with col2:
                if st.button("➡️ Next", disabled=st.session_state.current_page >= total_pages):
                    st.session_state.current_page += 1
                    st.rerun()
            with col3:
                st.write(f"Page {st.session_state.current_page} of {total_pages}")
            with col4:
                page_jump = st.number_input("Go to page:", min_value=1, max_value=total_pages, value=st.session_state.current_page, key="page_jump")
            with col5:
                if st.button("Go"):
                    st.session_state.current_page = page_jump
                    st.rerun()
        
        # Calculate pagination slice
        start_idx = (st.session_state.current_page - 1) * results_per_page
        end_idx = start_idx + results_per_page
        page_candidates = filtered_candidates[start_idx:end_idx]
        
        # Display candidates in cards
        for i, candidate in enumerate(page_candidates):
            with st.container():
                # Create expandable candidate card
                with st.expander(f"👤 {candidate.get('name', 'Unknown')} - {candidate.get('domain', 'Unknown')} ({candidate.get('experience_years', 0)} years)", expanded=False):
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Basic info
                        st.markdown("#### 📋 Basic Information")
                        st.write(f"**Name:** {candidate.get('name', 'Unknown')}")
                        st.write(f"**Domain:** {candidate.get('domain', 'Unknown')}")
                        st.write(f"**Experience:** {candidate.get('experience_years', 0)} years")
                        st.write(f"**Education:** {candidate.get('education', 'Not specified')}")
                        st.write(f"**Seniority:** {candidate.get('seniority', 'Not specified')}")
                        
                        # Contact info (role-based access)
                        if st.session_state.user_role in ['admin', 'recruiter']:
                            st.markdown("#### 📞 Contact Information")
                            st.write(f"**Email:** {candidate.get('email', 'Not provided')}")
                            st.write(f"**Phone:** {candidate.get('phone', 'Not provided')}")
                            st.write(f"**LinkedIn:** {candidate.get('linkedin', 'Not provided')}")
                        
                        # Skills section
                        st.markdown("#### 🎯 Skills")
                        skills = candidate.get('skills', [])
                        if skills:
                            # Group skills in columns for better display
                            skills_cols = st.columns(3)
                            for idx, skill in enumerate(skills[:15]):  # Show top 15 skills
                                with skills_cols[idx % 3]:
                                    # Highlight selected skills
                                    if skill.lower() in [s.lower() for s in selected_skills]:
                                        st.success(f"🎯 {skill}")
                                    else:
                                        st.info(f"• {skill}")
                            
                            if len(skills) > 15:
                                st.write(f"... and {len(skills) - 15} more skills")
                        else:
                            st.write("No skills listed")
                    
                    with col2:
                        # Quick actions and metrics
                        st.markdown("#### ⚡ Quick Actions")
                        
                        # Skills match percentage if skills filter is active
                        if selected_skills:
                            candidate_skills = set(skill.lower() for skill in candidate.get('skills', []))
                            selected_skills_set = set(skill.lower() for skill in selected_skills)
                            match_count = len(candidate_skills & selected_skills_set)
                            match_percentage = (match_count / len(selected_skills)) * 100 if selected_skills else 0
                            
                            st.metric("🎯 Skills Match", f"{match_percentage:.0f}%", f"{match_count}/{len(selected_skills)}")
                        
                        # Experience level indicator
                        exp_years = candidate.get('experience_years', 0)
                        if exp_years < 2:
                            exp_level = "👶 Junior"
                            exp_color = "blue"
                        elif exp_years < 5:
                            exp_level = "👨‍💼 Mid-Level"
                            exp_color = "green"
                        elif exp_years < 8:
                            exp_level = "🧑‍💼 Senior"
                            exp_color = "orange"
                        else:
                            exp_level = "👨‍🏫 Expert"
                            exp_color = "red"
                        
                        st.markdown(f'<p style="color: {exp_color}; font-weight: bold;">{exp_level}</p>', unsafe_allow_html=True)
                        
                        # Action buttons
                        if st.button(f"📧 Contact", key=f"contact_{i}", disabled=st.session_state.user_role == 'viewer'):
                            st.success(f"Contact info for {candidate.get('name', 'Unknown')} copied!")
                        
                        if st.button(f"⭐ Add to Shortlist", key=f"shortlist_{i}"):
                            if 'shortlisted_candidates' not in st.session_state:
                                st.session_state.shortlisted_candidates = []
                            if candidate not in st.session_state.shortlisted_candidates:
                                st.session_state.shortlisted_candidates.append(candidate)
                                st.success("Added to shortlist!")
                            else:
                                st.info("Already in shortlist")
                        
                        # Profile completeness
                        completeness_score = 0
                        if candidate.get('name'): completeness_score += 20
                        if candidate.get('email'): completeness_score += 20
                        if candidate.get('phone'): completeness_score += 15
                        if candidate.get('skills'): completeness_score += 25
                        if candidate.get('experience_years', 0) > 0: completeness_score += 20
                        
                        st.metric("📊 Profile Complete", f"{completeness_score}%")
        
        # Summary statistics for filtered results
        if len(filtered_candidates) > 0:
            st.divider()
            st.markdown("### 📈 Filtered Results Summary")
            
            summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
            
            with summary_col1:
                avg_filtered_exp = sum(c.get('experience_years', 0) for c in filtered_candidates) / len(filtered_candidates)
                st.metric("📈 Avg Experience", f"{avg_filtered_exp:.1f} years")
            
            with summary_col2:
                filtered_domains = [c.get('domain', '') for c in filtered_candidates]
                most_common_domain = max(set(filtered_domains), key=filtered_domains.count) if filtered_domains else "N/A"
                st.metric("🏢 Top Domain", most_common_domain)
            
            with summary_col3:
                # Calculate skills distribution
                all_filtered_skills = []
                for c in filtered_candidates:
                    all_filtered_skills.extend(c.get('skills', []))
                if all_filtered_skills:
                    most_common_skill = max(set(all_filtered_skills), key=all_filtered_skills.count)
                    st.metric("🎯 Top Skill", most_common_skill)
                else:
                    st.metric("🎯 Top Skill", "N/A")
            
            with summary_col4:
                # Shortlisted candidates count
                shortlisted_count = len(st.session_state.get('shortlisted_candidates', []))
                st.metric("⭐ Shortlisted", shortlisted_count)
    
    except Exception as e:
        st.error(f"❌ Error loading candidate dashboard: {str(e)}")
        st.info("Please check your database connection and try again.")

def main():
    """Main application function"""
    init_session_state()
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        show_login_page()
        return
    
    # Show sidebar navigation
    selected_page = show_sidebar()
    
    # Route to appropriate page based on selection and permissions
    user_role = st.session_state.user_role
    user_permissions = ROLES[user_role]["permissions"]
    
    if selected_page == "🏠 Dashboard":
        dashboard_page()
    
    elif selected_page == "📤 Upload Resumes":
        if "upload" in user_permissions:
            upload_resumes_page()
        else:
            st.error("❌ You don't have permission to access this page.")
    
    elif selected_page == "🎯 Job Matching":
        if "job_description" in user_permissions:
            job_matching_page()
        else:
            st.error("❌ You don't have permission to access this page.")
    
    elif selected_page == "📊 Analytics":
        if "analytics" in user_permissions:
            analytics_page()
        else:
            st.error("❌ You don't have permission to access this page.")
    
    elif selected_page == "⭐ Feedback":
        if "feedback" in user_permissions:
            feedback_page()
        else:
            st.error("❌ You don't have permission to access this page.")
    
    elif selected_page == "👥 Candidate Dashboard":
        if "candidate_dashboard" in user_permissions:
            candidate_dashboard_page()
        else:
            st.error("❌ You don't have permission to access this page.")
    
    elif selected_page == "🗄️ Database":
        if "database" in user_permissions:
            database_page()
        else:
            st.error("❌ You don't have permission to access this page.")

if __name__ == "__main__":
    main() 