# Database Integration for Resume Analyzer

## Overview

The Resume Analyzer now includes **SQLite database integration** to persistently store and manage candidate information. This replaces the previous session-based storage and provides better data management capabilities.

## Features

### 🗄️ Database Storage
- **Persistent Storage**: All candidate data is now stored in a SQLite database (`data/candidates.db`)
- **Structured Schema**: Organized tables for candidates, skills, experience, and education
- **Automatic Backups**: Data persists across application restarts

### 📊 Database Schema

#### Main Tables:
1. **`candidates`** - Core candidate information
   - id, name, email, phone, linkedin, domain, experience_years, education, seniority, filename, raw_text, timestamps

2. **`candidate_skills`** - Skills for each candidate (many-to-many)
   - candidate_id, skill_name

3. **`candidate_experience`** - Raw experience data (JSON)
   - candidate_id, experience_data

4. **`candidate_education`** - Raw education data (JSON)
   - candidate_id, education_data

## New Features

### 🎯 Enhanced Navigation
- **Database Management Page**: New page for managing stored candidates
- **Real-time Statistics**: Database metrics and insights
- **Data Export**: Export candidate data to CSV

### 🔍 Advanced Filtering
- **Database-powered Filters**: More efficient filtering using SQL queries
- **Search Functionality**: Search candidates by name, email, or skills
- **Performance Optimized**: Faster queries with database indexes

### 👥 Candidate Management
- **Individual Management**: View, edit, or delete specific candidates
- **Bulk Operations**: Clear all data or export everything
- **Duplicate Prevention**: Automatic handling of duplicate uploads

## How to Use

### 1. Upload & Analyze (Enhanced)
- Upload resumes as before
- Data is now automatically saved to the database
- Shows confirmation of successful database storage

### 2. Candidate Dashboard (Database-Powered)
- **Real-time Stats**: See total candidates, average experience, top domains/skills
- **Advanced Filters**: Use database-powered filtering for better performance
- **Persistent Data**: All candidates remain available across sessions

### 3. Database Management (New)
- **Statistics Overview**: View database metrics and distributions
- **Search & Filter**: Find specific candidates quickly
- **Individual Actions**: View details or delete specific candidates
- **Bulk Operations**: Export data or clear all records
- **Confirmation Dialogs**: Safety measures for destructive operations

### 4. Job Matching (Database-Powered)
- Now uses database for candidate retrieval
- Better performance with large datasets
- Persistent matching history

### 5. Analytics (Database-Powered)
- Real-time analytics from database
- More accurate statistics
- Better performance for large datasets

## Database Operations

### Automatic Operations:
- **Database Creation**: Auto-created on first run
- **Schema Updates**: Automatic table creation and indexing
- **Data Insertion**: Automatic saving during upload
- **Duplicate Handling**: Smart detection and updates

### Manual Operations:
- **Individual Delete**: Remove specific candidates
- **Bulk Delete**: Clear all data (with confirmation)
- **Export**: Download all data as CSV
- **Search**: Find candidates by name/email
- **Statistics**: View database metrics

## Technical Details

### Database Location:
```
data/candidates.db
```

### Key Classes:
- **`CandidateDatabase`**: Main database interface
- **`@st.cache_resource`**: Cached database connection for performance

### Performance Features:
- **Indexes**: Optimized queries on domain, experience, skills, filename
- **Connection Pooling**: Efficient database connections
- **Batch Operations**: Efficient bulk operations

## Migration from Session Storage

### Automatic Migration:
- Existing session-based code has been updated
- No data loss - old uploads will create new database entries
- Seamless transition

### Benefits:
- **Persistence**: Data survives application restarts
- **Performance**: Better filtering and search capabilities
- **Management**: Individual candidate management
- **Export**: Easy data export capabilities
- **Scalability**: Better performance with large datasets

## File Structure Changes

```
project/
├── src/
│   ├── database.py          # New: Database operations
│   ├── pdf_parser.py        # Unchanged
│   ├── nlp_analyzer.py      # Unchanged
│   ├── candidate_matcher.py # Unchanged
│   └── visualization.py     # Unchanged
├── data/
│   └── candidates.db        # New: SQLite database
├── app.py                   # Updated: Database integration
└── DATABASE_README.md       # New: This documentation
```

## Error Handling

### Robust Error Management:
- **Database Errors**: Graceful handling with user-friendly messages
- **Connection Issues**: Automatic retry and fallback mechanisms
- **Data Validation**: Comprehensive input validation
- **Backup Safety**: Confirmation dialogs for destructive operations

## Future Enhancements

### Potential Improvements:
- **Backup/Restore**: Database backup and restore functionality
- **Advanced Search**: Full-text search capabilities
- **Audit Trail**: Track changes and operations
- **User Management**: Multi-user support
- **API Integration**: REST API for external access

## Troubleshooting

### Common Issues:

1. **Database File Permissions**
   ```bash
   # Ensure write permissions for data/ directory
   chmod 755 data/
   ```

2. **Database Corruption**
   ```bash
   # Delete and recreate database
   rm data/candidates.db
   # Restart application - database will be recreated
   ```

3. **Performance Issues**
   ```bash
   # Check database size
   ls -lh data/candidates.db
   # Consider clearing old data if too large
   ```

## Summary

The database integration provides:
- ✅ **Persistent storage** of candidate data
- ✅ **Better performance** with large datasets
- ✅ **Advanced management** capabilities
- ✅ **Data export** functionality
- ✅ **Robust error handling**
- ✅ **Seamless migration** from session storage

Your resume analyzer is now ready for production use with enterprise-grade data management! 