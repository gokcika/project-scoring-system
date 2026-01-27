import sqlite3
import pandas as pd
from datetime import datetime
import os

class Database:
    def __init__(self, db_name="project_scoring.db"):
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        """Initialize database with tables"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # Projects table
        c.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_title TEXT NOT NULL,
                requestor_name TEXT NOT NULL,
                requestor_email TEXT NOT NULL,
                department TEXT NOT NULL,
                submission_date TEXT NOT NULL,
                status TEXT DEFAULT 'Submitted',
                
                -- Section 1: Regulatory
                reg_required TEXT,
                reg_citation TEXT,
                reg_deadline TEXT,
                reg_enforcement TEXT,
                reg_score REAL,
                
                -- Section 2: Reputational
                rep_headline TEXT,
                rep_risk_level TEXT,
                rep_harm_categories TEXT,
                rep_liability TEXT,
                rep_score REAL,
                
                -- Section 3: Strategic
                strat_document TEXT,
                strat_sponsor TEXT,
                strat_budget TEXT,
                strat_score REAL,
                
                -- Section 4: Operational
                op_process_name TEXT,
                op_current_time REAL,
                op_projected_time REAL,
                op_efficiency_gain REAL,
                op_scope TEXT,
                op_score REAL,
                
                -- Section 5: Resources
                res_approach TEXT,
                res_total_hours REAL,
                res_external_deps TEXT,
                res_score REAL,
                
                -- Section 6: Data Sensitivity
                data_type TEXT,
                data_third_party TEXT,
                data_volume TEXT,
                data_score REAL,
                
                -- Section 7: Stakeholder
                stake_requestor_level TEXT,
                stake_urgency TEXT,
                stake_score REAL,
                
                -- Scoring
                total_score REAL,
                priority TEXT,
                
                -- Compliance Review
                co_reviewed_by TEXT,
                co_reviewed_date TEXT,
                co_override_reg REAL,
                co_override_rep REAL,
                co_override_strat REAL,
                co_override_op REAL,
                co_override_res REAL,
                co_override_data REAL,
                co_override_stake REAL,
                co_final_score REAL,
                co_decision TEXT,
                co_notes TEXT,
                
                -- Red Flags
                red_flags TEXT,
                auto_reject INTEGER DEFAULT 0
            )
        ''')
        
        # Users table (simple auth)
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                email TEXT
            )
        ''')
        
        # Insert default admin if not exists
        c.execute('''
            INSERT OR IGNORE INTO users (username, password, role, email)
            VALUES ('admin', 'admin123', 'compliance_officer', 'admin@company.com')
        ''')
        
        # Insert default requestor for testing
        c.execute('''
            INSERT OR IGNORE INTO users (username, password, role, email)
            VALUES ('requestor', 'req123', 'requestor', 'requestor@company.com')
        ''')
        
        conn.commit()
        conn.close()
    
    def submit_project(self, data):
        """Submit new project"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        
        c.execute(f'''
            INSERT INTO projects ({columns})
            VALUES ({placeholders})
        ''', list(data.values()))
        
        project_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return project_id
    
    def get_projects(self, status=None):
        """Get projects, optionally filtered by status"""
        conn = sqlite3.connect(self.db_name)
        
        if status:
            query = "SELECT * FROM projects WHERE status = ? ORDER BY submission_date DESC"
            df = pd.read_sql_query(query, conn, params=(status,))
        else:
            query = "SELECT * FROM projects ORDER BY submission_date DESC"
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        return df
    
    def get_project(self, project_id):
        """Get single project by ID"""
        conn = sqlite3.connect(self.db_name)
        query = "SELECT * FROM projects WHERE id = ?"
        df = pd.read_sql_query(query, conn, params=(project_id,))
        conn.close()
        
        if len(df) > 0:
            return df.iloc[0].to_dict()
        return None
    
    def update_project(self, project_id, data):
        """Update project"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        values = list(data.values()) + [project_id]
        
        c.execute(f'''
            UPDATE projects
            SET {set_clause}
            WHERE id = ?
        ''', values)
        
        conn.commit()
        conn.close()
    
    def authenticate(self, username, password):
        """Simple authentication"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute('''
            SELECT username, role, email FROM users
            WHERE username = ? AND password = ?
        ''', (username, password))
        
        result = c.fetchone()
        conn.close()
        
        if result:
            return {
                'username': result[0],
                'role': result[1],
                'email': result[2]
            }
        return None
    
    def get_statistics(self):
        """Get dashboard statistics"""
        conn = sqlite3.connect(self.db_name)
        
        stats = {}
        
        # Total projects
        stats['total'] = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM projects", conn
        ).iloc[0]['count']
        
        # By status
        stats['by_status'] = pd.read_sql_query(
            "SELECT status, COUNT(*) as count FROM projects GROUP BY status", conn
        )
        
        # By priority
        stats['by_priority'] = pd.read_sql_query(
            "SELECT priority, COUNT(*) as count FROM projects GROUP BY priority", conn
        )
        
        # Average scores by department
        stats['avg_by_dept'] = pd.read_sql_query(
            """SELECT department, AVG(total_score) as avg_score, COUNT(*) as count 
               FROM projects GROUP BY department""", conn
        )
        
        # Recent high-priority
        stats['high_priority'] = pd.read_sql_query(
            """SELECT project_title, requestor_name, department, total_score, submission_date
               FROM projects 
               WHERE priority = 'IMMEDIATE' AND status = 'Submitted'
               ORDER BY total_score DESC LIMIT 5""", conn
        )
        
        conn.close()
        return stats
