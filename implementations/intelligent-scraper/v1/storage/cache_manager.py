import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """SQLite-based cache manager for storing and retrieving scraped data"""
    
    def __init__(self, cache_file: str = "scraping_cache.db"):
        self.cache_file = cache_file
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database with required tables"""
        conn = sqlite3.connect(self.cache_file)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS person_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                full_name TEXT,
                title TEXT,
                company TEXT,
                location TEXT,
                website TEXT,
                confidence_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraped_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER,
                source TEXT NOT NULL,
                data_type TEXT NOT NULL,
                content TEXT,
                metadata TEXT,
                url TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (person_id) REFERENCES person_profiles (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER,
                status TEXT NOT NULL,
                progress REAL DEFAULT 0.0,
                error_message TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (person_id) REFERENCES person_profiles (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_person_id(self, name: str) -> Optional[int]:
        """Get person ID by name"""
        conn = sqlite3.connect(self.cache_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM person_profiles WHERE name = ?', (name,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else None
    
    def create_person_profile(self, name: str, **kwargs) -> int:
        """Create a new person profile and return the ID"""
        conn = sqlite3.connect(self.cache_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO person_profiles (name, full_name, title, company, location, website, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            name,
            kwargs.get('full_name'),
            kwargs.get('title'),
            kwargs.get('company'),
            kwargs.get('location'),
            kwargs.get('website'),
            kwargs.get('confidence_score', 0.0)
        ))
        
        person_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return person_id
    
    def update_person_profile(self, person_id: int, **kwargs):
        """Update person profile information"""
        conn = sqlite3.connect(self.cache_file)
        cursor = conn.cursor()
        
        # Build dynamic update query
        fields = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['full_name', 'title', 'company', 'location', 'website', 'confidence_score']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if fields:
            values.append(person_id)
            query = f"UPDATE person_profiles SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            cursor.execute(query, values)
        
        conn.commit()
        conn.close()
    
    def store_scraped_data(self, person_id: int, source: str, data_type: str, 
                          content: str, metadata: Dict = None, url: str = None):
        """Store scraped data"""
        conn = sqlite3.connect(self.cache_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scraped_data (person_id, source, data_type, content, metadata, url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            person_id,
            source,
            data_type,
            content,
            json.dumps(metadata) if metadata else None,
            url
        ))
        
        conn.commit()
        conn.close()
    
    def get_scraped_data(self, person_id: int, source: str = None, data_type: str = None) -> List[Dict]:
        """Retrieve scraped data"""
        conn = sqlite3.connect(self.cache_file)
        cursor = conn.cursor()
        
        query = "SELECT * FROM scraped_data WHERE person_id = ?"
        params = [person_id]
        
        if source:
            query += " AND source = ?"
            params.append(source)
        
        if data_type:
            query += " AND data_type = ?"
            params.append(data_type)
        
        query += " ORDER BY scraped_at DESC"
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def update_processing_status(self, person_id: int, status: str, progress: float = 0.0, error_message: str = None):
        """Update processing status"""
        conn = sqlite3.connect(self.cache_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO processing_status (person_id, status, progress, error_message, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (person_id, status, progress, error_message))
        
        conn.commit()
        conn.close()
    
    def get_processing_status(self, person_id: int) -> Optional[Dict]:
        """Get current processing status"""
        conn = sqlite3.connect(self.cache_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM processing_status 
            WHERE person_id = ? 
            ORDER BY updated_at DESC 
            LIMIT 1
        ''', (person_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, result))
        return None
    
    def clear_person_data(self, person_id: int):
        """Clear all data for a person"""
        conn = sqlite3.connect(self.cache_file)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM scraped_data WHERE person_id = ?', (person_id,))
        cursor.execute('DELETE FROM processing_status WHERE person_id = ?', (person_id,))
        cursor.execute('DELETE FROM person_profiles WHERE id = ?', (person_id,))
        
        conn.commit()
        conn.close()
    
    def get_all_persons(self) -> List[Dict]:
        """Get all person profiles"""
        conn = sqlite3.connect(self.cache_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM person_profiles ORDER BY updated_at DESC')
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results



