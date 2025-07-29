# 📄 Resume Analysis Platform

A comprehensive AI-powered platform for analyzing resumes, matching candidates to job requirements, and providing detailed insights for hiring decisions.

## 🌟 Features

### Core Functionality
- **PDF Resume Parsing**: Extract structured data from PDF resumes
- **Smart Skills Detection**: Identify technical skills, programming languages, frameworks
- **Domain Classification**: Automatically categorize candidates (ML/AI, Frontend, Backend, Data Engineering, DevOps)
- **Experience Analysis**: Calculate years of experience and seniority levels
- **Job Matching**: Match candidates to job requirements with detailed scoring
- **Interactive Visualizations**: Comprehensive charts and analytics

### User Interface
- **Multi-page Dashboard**: Upload & Analyze, Candidate Dashboard, Job Matching, Analytics
- **Real-time Analysis**: Process multiple resumes simultaneously
- **Filter & Search**: Advanced filtering by skills, experience, domain
- **Export Capabilities**: Generate reports and candidate summaries

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or Download the Project**
   ```bash
   cd "C:\Users\2402635\vibecoding\resume analyzer"
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```

5. **Open in Browser**
   The application will automatically open in your default browser at `http://localhost:8501`

## 📋 Usage Guide

### 1. Upload & Analyze Resumes

1. Navigate to the "Upload & Analyze" page
2. Upload multiple PDF resume files
3. Click "Analyze Resumes" to process
4. View summary statistics and candidate preview

### 2. Browse Candidates

1. Go to "Candidate Dashboard"
2. Use filters to narrow down candidates:
   - Domain (ML/AI, Frontend, Backend, etc.)
   - Experience range
   - Skill search
3. View detailed candidate profiles

### 3. Job Matching

1. Navigate to "Job Matching"
2. Enter job requirements:
   - Job title and domain
   - Required experience
   - Required skills (comma-separated)
   - Job description
3. Click "Find Matching Candidates"
4. Review ranked matches with scores

### 4. Analytics Dashboard

1. Visit "Analytics" page
2. Explore visualizations:
   - Skills distribution
   - Experience patterns
   - Domain breakdown
   - Candidate analytics

## 🏗️ Project Structure

```
resume analyzer/
├── app.py                     # Main Streamlit application
├── src/                       # Source code modules
│   ├── pdf_parser.py         # PDF text extraction and parsing
│   ├── nlp_analyzer.py       # NLP analysis and classification
│   ├── candidate_matcher.py  # Job matching algorithms
│   └── visualization.py      # Chart and graph generation
├── data/                      # Data storage
├── models/                    # ML models (future use)
├── uploads/                   # Uploaded resume files
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🔧 Technical Details

### Supported File Formats
- **Input**: PDF resumes
- **Output**: Structured data, visualizations, reports

### Key Technologies
- **Framework**: Streamlit (Python web framework)
- **PDF Processing**: pdfplumber
- **Data Analysis**: pandas, numpy
- **Visualizations**: Plotly
- **Machine Learning**: scikit-learn
- **NLP**: spaCy, NLTK

### Skills Detection
The system recognizes skills in these categories:
- Programming Languages (Python, Java, JavaScript, etc.)
- Frameworks (React, Django, TensorFlow, etc.)
- Databases (MySQL, MongoDB, PostgreSQL, etc.)
- Cloud & DevOps (AWS, Docker, Kubernetes, etc.)
- ML/AI Technologies (TensorFlow, PyTorch, etc.)

### Domain Classification
Automatic classification into:
- **ML/AI**: Machine Learning, Data Science
- **Frontend**: React, Angular, Vue.js development
- **Backend**: Server-side development
- **Data Engineering**: ETL, Big Data, Data Pipelines
- **DevOps**: Infrastructure, CI/CD, Cloud
- **Full Stack**: Full-stack development
- **Mobile**: iOS, Android development

## 🎯 Job Matching Algorithm

The matching system uses a weighted scoring approach:

- **Domain Match (30%)**: Alignment between candidate and job domain
- **Skills Match (40%)**: Percentage of required skills possessed
- **Experience Match (20%)**: Years of experience vs. requirements
- **Text Similarity (10%)**: Keyword matching with job description

### Match Score Interpretation
- **90-100%**: Excellent match - highly recommended
- **70-89%**: Good match - consider for interview
- **50-69%**: Fair match - may need additional screening
- **30-49%**: Poor match - significant gaps
- **0-29%**: Very poor match - not recommended

## 📊 Analytics Features

### Candidate Analytics
- Skills distribution and frequency
- Experience level breakdown
- Domain distribution
- Education level analysis
- Seniority assessment

### Job-Specific Analytics
- Skills gap analysis
- Candidate ranking
- Match score distribution
- Hiring recommendations

## 🔄 Workflow Example

1. **HR uploads 50 resumes** for a "Senior ML Engineer" position
2. **System processes** and extracts structured data
3. **Candidates are classified** by domain and experience
4. **HR defines job requirements**: Python, TensorFlow, 5+ years experience
5. **System ranks candidates** by match score
6. **Top 10 candidates** are identified for interviews
7. **Analytics show** skills gaps and hiring recommendations

## 🛠️ Troubleshooting

### Common Issues

**PDF parsing errors:**
- Ensure PDFs contain readable text (not scanned images)
- Try re-saving PDFs from the original document

**Missing skills:**
- Skills database can be extended in `pdf_parser.py`
- Add domain-specific skills as needed

**Performance issues:**
- Process resumes in smaller batches
- Ensure sufficient system memory

### Error Messages

**"No text found in PDF":**
- PDF may be image-based or corrupted
- Try converting to text-based PDF

**"Module not found":**
- Run `pip install -r requirements.txt`
- Ensure virtual environment is activated

## 🚀 Future Enhancements

### Planned Features
- **Advanced ML Models**: Custom NER for better skill extraction
- **Resume Templates**: Support for different resume formats
- **API Integration**: Connect with job boards and ATS systems
- **Database Storage**: Persistent candidate database
- **Email Integration**: Automated candidate communication
- **Advanced Analytics**: Predictive hiring analytics

### Customization Options
- **Custom Skills Database**: Add industry-specific skills
- **Scoring Weights**: Adjust matching algorithm weights
- **UI Themes**: Custom branding and themes
- **Export Formats**: Additional report formats

## 📝 License

This project is for educational and internal use. Ensure compliance with data privacy regulations when processing personal information.

## 🤝 Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📧 Support

For questions or issues:
- Check the troubleshooting section
- Review the code documentation
- Create an issue in the project repository

---

**Happy Hiring! 🎉**

*Built with ❤️ using Python and Streamlit* 
