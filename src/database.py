import sqlite3
import json
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class CandidateDatabase:
    def __init__(self, db_path: str = "data/candidates.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create candidates table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS candidates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    linkedin TEXT,
                    domain TEXT,
                    experience_years INTEGER DEFAULT 0,
                    education TEXT,
                    seniority TEXT,
                    filename TEXT,
                    raw_text TEXT,
                    match_history TEXT,
                    rating_average REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,
                    last_accessed TIMESTAMP
                )
            ''')
            
            # Create skills table (many-to-many relationship)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS candidate_skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id INTEGER,
                    skill_name TEXT NOT NULL,
                    FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE
                )
            ''')
            
            # Create experience table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS candidate_experience (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id INTEGER,
                    experience_data TEXT,  -- JSON string of experience data
                    FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE
                )
            ''')
            
            # Create education table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS candidate_education (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id INTEGER,
                    education_data TEXT,  -- JSON string of education data
                    FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_candidates_domain ON candidates(domain)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_candidates_experience ON candidates(experience_years)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_skills_name ON candidate_skills(skill_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_candidates_filename ON candidates(filename)')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def save_candidate(self, candidate_data: Dict, profile_data: Dict, raw_resume_data: Dict) -> int:
        """
        Save candidate information to database.
        
        Args:
            candidate_data: Processed candidate info from app.py
            profile_data: Profile data from nlp_analyzer
            raw_resume_data: Raw data from pdf_parser
            
        Returns:
            int: Candidate ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if candidate already exists (by filename or email)
            existing_id = self.get_candidate_id_by_filename(candidate_data.get('filename', ''))
            if existing_id:
                # Update existing candidate
                return self.update_candidate(existing_id, candidate_data, profile_data, raw_resume_data)
            
            # Insert main candidate record
            cursor.execute('''
                INSERT INTO candidates (
                    name, email, phone, linkedin, domain, experience_years, 
                    education, seniority, filename, raw_text, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                candidate_data.get('name', 'Unknown'),
                candidate_data.get('email', ''),
                candidate_data.get('phone', ''),
                profile_data.get('linkedin', ''),
                candidate_data.get('domain', ''),
                candidate_data.get('experience_years', 0),
                candidate_data.get('education', ''),
                profile_data.get('seniority', ''),
                candidate_data.get('filename', ''),
                raw_resume_data.get('raw_text', ''),
                datetime.now(),
                datetime.now()
            ))
            
            candidate_id = cursor.lastrowid
            
            # Insert skills
            skills = candidate_data.get('skills', [])
            for skill in skills:
                cursor.execute('''
                    INSERT INTO candidate_skills (candidate_id, skill_name)
                    VALUES (?, ?)
                ''', (candidate_id, skill))
            
            # Insert experience data
            raw_experience = profile_data.get('raw_experience', [])
            if raw_experience:
                cursor.execute('''
                    INSERT INTO candidate_experience (candidate_id, experience_data)
                    VALUES (?, ?)
                ''', (candidate_id, json.dumps(raw_experience)))
            
            # Insert education data
            raw_education = profile_data.get('raw_education', [])
            if raw_education:
                cursor.execute('''
                    INSERT INTO candidate_education (candidate_id, education_data)
                    VALUES (?, ?)
                ''', (candidate_id, json.dumps(raw_education)))
            
            conn.commit()
            logger.info(f"Saved candidate {candidate_data.get('name')} with ID {candidate_id}")
            return candidate_id
    
    def get_candidate_id_by_filename(self, filename: str) -> Optional[int]:
        """Get candidate ID by filename."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM candidates WHERE filename = ?', (filename,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def update_candidate(self, candidate_id: int, candidate_data: Dict, profile_data: Dict, raw_resume_data: Dict) -> int:
        """Update existing candidate record."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Update main candidate record
            cursor.execute('''
                UPDATE candidates SET
                    name = ?, email = ?, phone = ?, linkedin = ?, domain = ?,
                    experience_years = ?, education = ?, seniority = ?, raw_text = ?,
                    updated_at = ?
                WHERE id = ?
            ''', (
                candidate_data.get('name', 'Unknown'),
                candidate_data.get('email', ''),
                candidate_data.get('phone', ''),
                profile_data.get('linkedin', ''),
                candidate_data.get('domain', ''),
                candidate_data.get('experience_years', 0),
                candidate_data.get('education', ''),
                profile_data.get('seniority', ''),
                raw_resume_data.get('raw_text', ''),
                datetime.now(),
                candidate_id
            ))
            
            # Delete existing skills and insert new ones
            cursor.execute('DELETE FROM candidate_skills WHERE candidate_id = ?', (candidate_id,))
            skills = candidate_data.get('skills', [])
            for skill in skills:
                cursor.execute('''
                    INSERT INTO candidate_skills (candidate_id, skill_name)
                    VALUES (?, ?)
                ''', (candidate_id, skill))
            
            # Update experience data
            cursor.execute('DELETE FROM candidate_experience WHERE candidate_id = ?', (candidate_id,))
            raw_experience = profile_data.get('raw_experience', [])
            if raw_experience:
                cursor.execute('''
                    INSERT INTO candidate_experience (candidate_id, experience_data)
                    VALUES (?, ?)
                ''', (candidate_id, json.dumps(raw_experience)))
            
            # Update education data
            cursor.execute('DELETE FROM candidate_education WHERE candidate_id = ?', (candidate_id,))
            raw_education = profile_data.get('raw_education', [])
            if raw_education:
                cursor.execute('''
                    INSERT INTO candidate_education (candidate_id, education_data)
                    VALUES (?, ?)
                ''', (candidate_id, json.dumps(raw_education)))
            
            conn.commit()
            logger.info(f"Updated candidate ID {candidate_id}")
            return candidate_id
    
    def get_all_candidates(self) -> List[Dict]:
        """Retrieve all candidates from database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM candidates ORDER BY created_at DESC
            ''')
            candidates = cursor.fetchall()
            
            result = []
            for candidate in candidates:
                candidate_dict = dict(candidate)
                
                # Get skills for this candidate
                cursor.execute('''
                    SELECT skill_name FROM candidate_skills WHERE candidate_id = ?
                ''', (candidate['id'],))
                skills = [row[0] for row in cursor.fetchall()]
                candidate_dict['skills'] = skills
                
                # Get experience data
                cursor.execute('''
                    SELECT experience_data FROM candidate_experience WHERE candidate_id = ?
                ''', (candidate['id'],))
                exp_result = cursor.fetchone()
                candidate_dict['raw_experience'] = json.loads(exp_result[0]) if exp_result and exp_result[0] else []
                
                # Get education data
                cursor.execute('''
                    SELECT education_data FROM candidate_education WHERE candidate_id = ?
                ''', (candidate['id'],))
                edu_result = cursor.fetchone()
                candidate_dict['raw_education'] = json.loads(edu_result[0]) if edu_result and edu_result[0] else []
                
                result.append(candidate_dict)
            
            logger.info(f"Retrieved {len(result)} candidates from database")
            return result
    
    def get_candidate_by_id(self, candidate_id: int) -> Optional[Dict]:
        """Get a specific candidate by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM candidates WHERE id = ?', (candidate_id,))
            candidate = cursor.fetchone()
            
            if not candidate:
                return None
            
            candidate_dict = dict(candidate)
            
            # Get skills
            cursor.execute('SELECT skill_name FROM candidate_skills WHERE candidate_id = ?', (candidate_id,))
            skills = [row[0] for row in cursor.fetchall()]
            candidate_dict['skills'] = skills
            
            # Get experience data
            cursor.execute('SELECT experience_data FROM candidate_experience WHERE candidate_id = ?', (candidate_id,))
            exp_result = cursor.fetchone()
            candidate_dict['raw_experience'] = json.loads(exp_result[0]) if exp_result and exp_result[0] else []
            
            # Get education data
            cursor.execute('SELECT education_data FROM candidate_education WHERE candidate_id = ?', (candidate_id,))
            edu_result = cursor.fetchone()
            candidate_dict['raw_education'] = json.loads(edu_result[0]) if edu_result and edu_result[0] else []
            
            return candidate_dict
    
    def filter_candidates(self, filters: Dict) -> List[Dict]:
        """Filter candidates based on criteria."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build dynamic query
            where_clauses = []
            params = []
            
            if filters.get('domains'):
                domain_placeholders = ','.join(['?' for _ in filters['domains']])
                where_clauses.append(f'domain IN ({domain_placeholders})')
                params.extend(filters['domains'])
            
            if filters.get('min_experience') is not None:
                where_clauses.append('experience_years >= ?')
                params.append(filters['min_experience'])
            
            if filters.get('max_experience') is not None:
                where_clauses.append('experience_years <= ?')
                params.append(filters['max_experience'])
            
            if filters.get('search_skill'):
                where_clauses.append('''
                    id IN (
                        SELECT candidate_id FROM candidate_skills 
                        WHERE skill_name LIKE ?
                    )
                ''')
                params.append(f"%{filters['search_skill']}%")
            
            # Construct final query
            base_query = 'SELECT * FROM candidates'
            if where_clauses:
                base_query += ' WHERE ' + ' AND '.join(where_clauses)
            base_query += ' ORDER BY created_at DESC'
            
            cursor.execute(base_query, params)
            candidates = cursor.fetchall()
            
            # Get full candidate data including skills
            result = []
            for candidate in candidates:
                candidate_dict = dict(candidate)
                
                # Get skills
                cursor.execute('SELECT skill_name FROM candidate_skills WHERE candidate_id = ?', (candidate['id'],))
                skills = [row[0] for row in cursor.fetchall()]
                candidate_dict['skills'] = skills
                
                result.append(candidate_dict)
            
            return result
    
    def delete_candidate(self, candidate_id: int) -> bool:
        """Delete a candidate and all related data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Delete from main table (cascades to related tables due to foreign key constraints)
            cursor.execute('DELETE FROM candidates WHERE id = ?', (candidate_id,))
            
            deleted = cursor.rowcount > 0
            conn.commit()
            
            if deleted:
                logger.info(f"Deleted candidate ID {candidate_id}")
            
            return deleted
    
    def get_database_stats(self) -> Dict:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total candidates
            cursor.execute('SELECT COUNT(*) FROM candidates')
            total_candidates = cursor.fetchone()[0]
            
            # Candidates by domain
            cursor.execute('''
                SELECT domain, COUNT(*) FROM candidates 
                WHERE domain IS NOT NULL AND domain != ''
                GROUP BY domain
            ''')
            domain_stats = dict(cursor.fetchall())
            
            # Average experience
            cursor.execute('SELECT AVG(experience_years) FROM candidates WHERE experience_years > 0')
            avg_experience = cursor.fetchone()[0] or 0
            
            # Most common skills
            cursor.execute('''
                SELECT skill_name, COUNT(*) as count FROM candidate_skills 
                GROUP BY skill_name 
                ORDER BY count DESC 
                LIMIT 10
            ''')
            top_skills = dict(cursor.fetchall())
            
            return {
                'total_candidates': total_candidates,
                'domain_distribution': domain_stats,
                'average_experience': round(avg_experience, 1),
                'top_skills': top_skills
            }
    
    def close(self):
        """Close database connection (if needed for cleanup)."""
        # SQLite connections are automatically closed when using context managers
        pass 