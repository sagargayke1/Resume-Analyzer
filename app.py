import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

from pdf_parser import extract_resume_data
from nlp_analyzer import analyze_candidate_profile, classify_domain
from visualization import create_skills_chart, create_experience_chart, create_domain_distribution
from candidate_matcher import calculate_match_score, rank_candidates
from database import CandidateDatabase

# Initialize database
@st.cache_resource
def init_database():
    """Initialize database connection (cached for performance)."""
    return CandidateDatabase()

# Initialize systems
db = init_database()

# Page configuration
st.set_page_config(
    page_title="Resume Analysis Platform",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
        margin: 0.5rem 0;
    }
    .candidate-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">📄 Resume Analysis Platform</h1>', unsafe_allow_html=True)
    
    # Navigation
    st.sidebar.title("📋 Navigation")
    
    # Define all available pages (no authentication required)
    pages = [
        "📤 Upload & Analyze",
        "👥 Candidate Dashboard", 
        "🎯 Job Matching",
        "📈 Analytics",
        "🗄️ Database Management"
    ]
    
    # Page selection
    selected_page_display = st.sidebar.selectbox("Choose a page", pages)
    selected_page = selected_page_display.split(" ", 1)[1]  # Remove icon
    
    # Route to appropriate page
    if selected_page == "Upload & Analyze":
        upload_and_analyze_page()
    elif selected_page == "Candidate Dashboard":
        candidate_dashboard_page()
    elif selected_page == "Job Matching":
        job_matching_page()
    elif selected_page == "Analytics":
        analytics_page()
    elif selected_page == "Database Management":
        database_management_page()

def upload_and_analyze_page():
    st.header("📤 Upload and Analyze Resumes")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Upload Resume Files")
        uploaded_files = st.file_uploader(
            "Choose PDF files", 
            type=['pdf'], 
            accept_multiple_files=True,
            help="Upload multiple resume files in PDF format"
        )
        
        if uploaded_files:
            st.success(f"📁 {len(uploaded_files)} files uploaded successfully!")
            
            # Save uploaded files
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)
            
            if st.button("🔍 Analyze Resumes", type="primary"):
                with st.spinner("Analyzing resumes... This may take a few moments."):
                    candidates_data = []
                    
                    for uploaded_file in uploaded_files:
                        # Save file
                        file_path = upload_dir / uploaded_file.name
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Extract and analyze data
                        try:
                            resume_data = extract_resume_data(str(file_path))
                            profile = analyze_candidate_profile(resume_data)
                            domain = classify_domain(profile['skills'])
                            
                            candidate_info = {
                                'name': profile.get('name', 'Unknown'),
                                'email': profile.get('email', 'Not provided'),
                                'phone': profile.get('phone', 'Not provided'),
                                'domain': domain,
                                'experience_years': profile.get('experience_years', 0),
                                'skills': profile.get('skills', []),
                                'education': profile.get('education', 'Not specified'),
                                'filename': uploaded_file.name
                            }
                            
                            # Save to database
                            candidate_id = db.save_candidate(candidate_info, profile, resume_data)
                            candidate_info['id'] = candidate_id
                            candidates_data.append(candidate_info)
                            
                        except Exception as e:
                            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                    
                    # Update session state with database flag
                    st.session_state['candidates_loaded'] = True
                    
                    # Display results
                    if candidates_data:
                        st.success(f"✅ Successfully analyzed {len(candidates_data)} resumes!")
                        display_candidate_summary(candidates_data)
    
    with col2:
        st.subheader("💡 Tips")
        st.info("""
        **For best results:**
        - Use clear, well-formatted PDF resumes
        - Ensure resumes contain standard sections (Experience, Skills, Education)
        - File names should be descriptive
        - Supported domains: ML/AI, Frontend, Backend, Data Engineering, DevOps
        """)

def display_candidate_summary(candidates_data):
    st.subheader("📊 Analysis Summary")
    
    if not candidates_data:
        st.warning("No candidates data available.")
        return
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Candidates", len(candidates_data))
    
    with col2:
        domains = [c['domain'] for c in candidates_data]
        unique_domains = len(set(domains))
        st.metric("Unique Domains", unique_domains)
    
    with col3:
        avg_experience = sum(c['experience_years'] for c in candidates_data) / len(candidates_data)
        st.metric("Avg Experience", f"{avg_experience:.1f} years")
    
    with col4:
        total_skills = sum(len(c['skills']) for c in candidates_data)
        st.metric("Total Skills Found", total_skills)
    
    # Quick preview of candidates
    st.subheader("👥 Candidates Preview")
    for i, candidate in enumerate(candidates_data[:5]):  # Show first 5
        with st.expander(f"👤 {candidate['name']} - {candidate['domain']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Email:** {candidate['email']}")
                st.write(f"**Experience:** {candidate['experience_years']} years")
                st.write(f"**Domain:** {candidate['domain']}")
            with col2:
                st.write(f"**Skills:** {', '.join(candidate['skills'][:5])}")
                if len(candidate['skills']) > 5:
                    st.write(f"... and {len(candidate['skills']) - 5} more")

def candidate_dashboard_page():
    st.header("👥 Candidate Dashboard")
    
    # Fetch candidates from database
    try:
        candidates_data = db.get_all_candidates()
        if not candidates_data:
            st.warning("No candidate data available. Please upload and analyze resumes first.")
            return
        
        # Add database stats
        stats = db.get_database_stats()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Candidates", stats['total_candidates'])
        with col2:
            st.metric("Avg Experience", f"{stats['average_experience']} years")
        with col3:
            top_domain = max(stats['domain_distribution'].items(), key=lambda x: x[1])[0] if stats['domain_distribution'] else "N/A"
            st.metric("Top Domain", top_domain)
        with col4:
            top_skill = list(stats['top_skills'].keys())[0] if stats['top_skills'] else "N/A"
            st.metric("Top Skill", top_skill)
        
        st.divider()
        
    except Exception as e:
        st.error(f"Error fetching candidate data: {str(e)}")
        return
    
    df = pd.DataFrame(candidates_data)
    
    # Filters
    st.subheader("🔍 Filters")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        available_domains = list(set([c['domain'] for c in candidates_data if c.get('domain')]))
        domain_filter = st.multiselect("Domain", available_domains, default=available_domains)
    
    with col2:
        min_exp, max_exp = st.slider("Experience Range (years)", 0, 20, (0, 20))
    
    with col3:
        search_skill = st.text_input("Search by Skill")
    
    with col4:
        if st.button("🗑️ Clear Filters"):
            st.experimental_rerun()
    
    # Apply filters using database
    filter_criteria = {
        'domains': domain_filter,
        'min_experience': min_exp,
        'max_experience': max_exp
    }
    
    if search_skill:
        filter_criteria['search_skill'] = search_skill
    
    try:
        filtered_candidates = db.filter_candidates(filter_criteria)
        filtered_df = pd.DataFrame(filtered_candidates)
    except Exception as e:
        st.error(f"Error applying filters: {str(e)}")
        filtered_df = df
    
    # Display filtered candidates
    st.subheader(f"📋 Candidates ({len(filtered_df)} found)")
    
    for _, candidate in filtered_df.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="candidate-card">
                <h4>👤 {candidate['name']}</h4>
                <p><strong>Domain:</strong> {candidate['domain']} | <strong>Experience:</strong> {candidate['experience_years']} years</p>
                <p><strong>Email:</strong> {candidate['email']} | <strong>Phone:</strong> {candidate['phone']}</p>
                <p><strong>Skills:</strong> {', '.join(candidate['skills'][:8])}</p>
                <p><strong>Education:</strong> {candidate['education']}</p>
            </div>
            """, unsafe_allow_html=True)

def job_matching_page():
    st.header("🎯 Job Matching")
    
    # Fetch candidates from database
    try:
        candidates_data = db.get_all_candidates()
        if not candidates_data:
            st.warning("No candidate data available. Please upload and analyze resumes first.")
            return
    except Exception as e:
        st.error(f"Error fetching candidate data: {str(e)}")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Job Requirements")
        job_title = st.text_input("Job Title", placeholder="e.g., Senior ML Engineer")
        job_domain = st.selectbox("Domain", ["ML/AI", "Frontend", "Backend", "Data Engineering", "DevOps", "Full Stack"])
        required_experience = st.slider("Required Experience (years)", 0, 15, 3)
        
        required_skills = st.text_area(
            "Required Skills (comma-separated)", 
            placeholder="e.g., Python, TensorFlow, Machine Learning, Deep Learning"
        )
        
        job_description = st.text_area(
            "Job Description",
            placeholder="Enter detailed job description...",
            height=150
        )
        
        if st.button("🔍 Find Matching Candidates", type="primary"):
            if required_skills and job_description:
                skills_list = [skill.strip() for skill in required_skills.split(',')]
                
                # Calculate match scores
                matched_candidates = []
                for candidate in candidates_data:
                    match_score = calculate_match_score(candidate, {
                        'domain': job_domain,
                        'required_experience': required_experience,
                        'required_skills': skills_list,
                        'job_description': job_description
                    })
                    
                    candidate_with_score = candidate.copy()
                    candidate_with_score['match_score'] = match_score
                    matched_candidates.append(candidate_with_score)
                
                # Rank candidates
                ranked_candidates = rank_candidates(matched_candidates)
                st.session_state['ranked_candidates'] = ranked_candidates
            else:
                st.error("Please fill in required skills and job description.")
    
    with col2:
        st.subheader("🏆 Top Matches")
        
        if 'ranked_candidates' in st.session_state:
            ranked_candidates = st.session_state['ranked_candidates']
            
            for i, candidate in enumerate(ranked_candidates[:10]):  # Top 10
                match_percentage = candidate['match_score'] * 100
                
                # Color coding for match score
                if match_percentage >= 80:
                    color = "🟢"
                elif match_percentage >= 60:
                    color = "🟡"
                else:
                    color = "🔴"
                
                with st.expander(f"{color} #{i+1} {candidate['name']} - {match_percentage:.1f}% match"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**Domain:** {candidate['domain']}")
                        st.write(f"**Experience:** {candidate['experience_years']} years")
                        st.write(f"**Email:** {candidate['email']}")
                    with col_b:
                        st.write(f"**Match Score:** {match_percentage:.1f}%")
                        st.write(f"**Skills:** {', '.join(candidate['skills'][:5])}")
                        if len(candidate['skills']) > 5:
                            st.write(f"... +{len(candidate['skills']) - 5} more")

def analytics_page():
    st.header("📈 Analytics Dashboard")
    
    # Fetch candidates from database
    try:
        candidates_data = db.get_all_candidates()
        if not candidates_data:
            st.warning("No candidate data available. Please upload and analyze resumes first.")
            return
        
        df = pd.DataFrame(candidates_data)
    except Exception as e:
        st.error(f"Error fetching candidate data: {str(e)}")
        return
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Domain distribution
        domain_counts = df['domain'].value_counts()
        fig_domain = px.pie(
            values=domain_counts.values,
            names=domain_counts.index,
            title="Candidate Distribution by Domain"
        )
        st.plotly_chart(fig_domain, use_container_width=True)
        
        # Experience distribution
        fig_exp = px.histogram(
            df, 
            x='experience_years', 
            nbins=10,
            title="Experience Distribution",
            labels={'experience_years': 'Years of Experience', 'count': 'Number of Candidates'}
        )
        st.plotly_chart(fig_exp, use_container_width=True)
    
    with col2:
        # Skills analysis
        all_skills = []
        for skills_list in df['skills']:
            all_skills.extend(skills_list)
        
        skill_counts = pd.Series(all_skills).value_counts().head(15)
        
        fig_skills = px.bar(
            x=skill_counts.values,
            y=skill_counts.index,
            orientation='h',
            title="Top 15 Skills",
            labels={'x': 'Number of Candidates', 'y': 'Skills'}
        )
        fig_skills.update_layout(height=500)
        st.plotly_chart(fig_skills, use_container_width=True)
        
        # Experience vs Domain
        fig_scatter = px.scatter(
            df, 
            x='experience_years', 
            y='domain',
            title="Experience by Domain",
            labels={'experience_years': 'Years of Experience'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

def database_management_page():
    st.header("🗄️ Database Management")
    
    # Database statistics
    try:
        stats = db.get_database_stats()
        
        st.subheader("📊 Database Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Candidates", stats['total_candidates'])
            st.metric("Average Experience", f"{stats['average_experience']} years")
        
        with col2:
            if stats['domain_distribution']:
                st.write("**Domain Distribution:**")
                for domain, count in stats['domain_distribution'].items():
                    st.write(f"• {domain}: {count}")
            else:
                st.write("No domain data available")
        
        with col3:
            if stats['top_skills']:
                st.write("**Top Skills:**")
                for skill, count in list(stats['top_skills'].items())[:5]:
                    st.write(f"• {skill}: {count}")
            else:
                st.write("No skills data available")
        
        st.divider()
        
        # Candidate management
        st.subheader("👥 Candidate Management")
        
        # Get all candidates for management
        candidates = db.get_all_candidates()
        
        if candidates:
            # Search and filter options
            col1, col2 = st.columns([3, 1])
            
            with col1:
                search_name = st.text_input("Search by name or email:")
            
            with col2:
                st.write("")  # Spacing
                if st.button("🔄 Refresh Data"):
                    st.experimental_rerun()
            
            # Filter candidates based on search
            if search_name:
                filtered_candidates = [
                    c for c in candidates 
                    if search_name.lower() in c.get('name', '').lower() 
                    or search_name.lower() in c.get('email', '').lower()
                ]
            else:
                filtered_candidates = candidates
            
            # Display candidates with management options
            st.write(f"**Showing {len(filtered_candidates)} of {len(candidates)} candidates**")
            
            for candidate in filtered_candidates[:20]:  # Limit to 20 for performance
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**{candidate.get('name', 'Unknown')}**")
                        st.write(f"📧 {candidate.get('email', 'N/A')} | 📱 {candidate.get('phone', 'N/A')}")
                        st.write(f"💼 {candidate.get('domain', 'N/A')} | 📈 {candidate.get('experience_years', 0)} years")
                        st.write(f"📄 {candidate.get('filename', 'N/A')}")
                    
                    with col2:
                        if st.button(f"🔍 View Details", key=f"view_{candidate['id']}"):
                            st.session_state[f"show_details_{candidate['id']}"] = True
                    
                    with col3:
                        if st.button(f"🗑️ Delete", key=f"delete_{candidate['id']}", type="secondary"):
                            if st.session_state.get(f"confirm_delete_{candidate['id']}", False):
                                # Actually delete
                                if db.delete_candidate(candidate['id']):
                                    st.success(f"Deleted candidate {candidate.get('name', 'Unknown')}")
                                    st.experimental_rerun()
                                else:
                                    st.error("Failed to delete candidate")
                            else:
                                # Ask for confirmation
                                st.session_state[f"confirm_delete_{candidate['id']}"] = True
                                st.warning("Click delete again to confirm")
                    
                    # Show details if requested
                    if st.session_state.get(f"show_details_{candidate['id']}", False):
                        with st.expander(f"Details for {candidate.get('name', 'Unknown')}", expanded=True):
                            st.write(f"**Skills:** {', '.join(candidate.get('skills', []))}")
                            st.write(f"**Education:** {candidate.get('education', 'N/A')}")
                            st.write(f"**Seniority:** {candidate.get('seniority', 'N/A')}")
                            st.write(f"**LinkedIn:** {candidate.get('linkedin', 'N/A')}")
                            
                            if st.button(f"❌ Hide Details", key=f"hide_{candidate['id']}"):
                                st.session_state[f"show_details_{candidate['id']}"] = False
                                st.experimental_rerun()
                    
                    st.divider()
            
            if len(filtered_candidates) > 20:
                st.info(f"Showing first 20 candidates. {len(filtered_candidates) - 20} more available.")
        
        else:
            st.info("No candidates found in the database.")
        
        st.divider()
        
        # Database operations
        st.subheader("⚠️ Database Operations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear All Data", type="secondary"):
                if st.session_state.get('confirm_clear_all', False):
                    # Clear all data
                    candidates = db.get_all_candidates()
                    for candidate in candidates:
                        db.delete_candidate(candidate['id'])
                    st.success("All candidate data cleared!")
                    st.experimental_rerun()
                else:
                    st.session_state['confirm_clear_all'] = True
                    st.warning("Click again to confirm clearing ALL data")
        
        with col2:
            if st.button("📊 Export Data", type="primary"):
                candidates = db.get_all_candidates()
                if candidates:
                    df = pd.DataFrame(candidates)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="⬬ Download CSV",
                        data=csv,
                        file_name="candidates_export.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No data to export")
    
    except Exception as e:
        st.error(f"Error accessing database: {str(e)}")
        st.info("Make sure the database is properly initialized and accessible.")

if __name__ == "__main__":
    main() 