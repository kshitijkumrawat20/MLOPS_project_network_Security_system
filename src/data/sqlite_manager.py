import sqlite3
import pandas as pd
import os
from datetime import datetime
from src.exception.exception import NetworkSecurityException
from src.logging.logger import logging
import sys

class PhishingDataManager:
    def __init__(self, db_path="data/phishing_data.db"):
        """Initialize SQLite database for phishing data"""
        try:
            self.db_path = db_path
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self._create_tables()
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def _create_tables(self):
        """Create phishing data table and metadata table"""
        try:
            cursor = self.conn.cursor()
            
            # Main data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS phishing_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    having_IP_Address INTEGER,
                    URL_Length INTEGER,
                    Shortining_Service INTEGER,
                    having_At_Symbol INTEGER,
                    double_slash_redirecting INTEGER,
                    Prefix_Suffix INTEGER,
                    having_Sub_Domain INTEGER,
                    SSLfinal_State INTEGER,
                    Domain_registeration_length INTEGER,
                    Favicon INTEGER,
                    port INTEGER,
                    HTTPS_token INTEGER,
                    Request_URL INTEGER,
                    URL_of_Anchor INTEGER,
                    Links_in_tags INTEGER,
                    SFH INTEGER,
                    Submitting_to_email INTEGER,
                    Abnormal_URL INTEGER,
                    Redirect INTEGER,
                    on_mouseover INTEGER,
                    RightClick INTEGER,
                    popUpWidnow INTEGER,
                    Iframe INTEGER,
                    age_of_domain INTEGER,
                    DNSRecord INTEGER,
                    web_traffic INTEGER,
                    Page_Rank INTEGER,
                    Google_Index INTEGER,
                    Links_pointing_to_page INTEGER,
                    Statistical_report INTEGER,
                    Result INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    used_in_training BOOLEAN DEFAULT 0
                )
            """)
            
            # Training metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    training_timestamp TIMESTAMP,
                    data_count INTEGER,
                    model_accuracy REAL,
                    model_version TEXT,
                    artifact_path TEXT
                )
            """)
            
            self.conn.commit()
            logging.info("Database tables created successfully")
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def insert_data_from_csv(self, csv_path):
        """Bulk insert from CSV (initial load)"""
        try:
            df = pd.read_csv(csv_path)
            df.replace({"na": None}, inplace=True)
            
            # Insert only new records (avoid duplicates)
            df.to_sql('phishing_data', self.conn, if_exists='append', index=False)
            logging.info(f"Inserted {len(df)} records from CSV")
            return len(df)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def add_new_samples(self, data_dict_list):
        """Add new phishing samples incrementally"""
        try:
            df = pd.DataFrame(data_dict_list)
            df.to_sql('phishing_data', self.conn, if_exists='append', index=False)
            logging.info(f"Added {len(df)} new samples")
            return len(df)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def get_training_data(self, include_new_only=False):
        """Fetch data for training"""
        try:
            if include_new_only:
                # Only get data not used in training yet
                query = "SELECT * FROM phishing_data WHERE used_in_training = 0"
            else:
                # Get all data
                query = "SELECT * FROM phishing_data"
            
            df = pd.read_sql_query(query, self.conn)
            
            # Drop metadata columns
            df = df.drop(['id', 'created_at', 'used_in_training'], axis=1, errors='ignore')
            
            logging.info(f"Fetched {len(df)} records for training")
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def mark_data_as_trained(self):
        """Mark all data as used in training"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE phishing_data SET used_in_training = 1 WHERE used_in_training = 0")
            self.conn.commit()
            logging.info("Marked data as trained")
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def get_new_data_count(self):
        """Count untrained samples"""
        try:
            cursor = self.conn.cursor()
            result = cursor.execute("SELECT COUNT(*) FROM phishing_data WHERE used_in_training = 0").fetchone()
            return result[0]
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def log_training_run(self, data_count, accuracy, version, artifact_path):
        """Log training metadata"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO training_metadata (training_timestamp, data_count, model_accuracy, model_version, artifact_path)
                VALUES (?, ?, ?, ?, ?)
            """, (datetime.now(), data_count, accuracy, version, artifact_path))
            self.conn.commit()
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def should_retrain(self, threshold=100):
        """Check if retraining is needed based on new data"""
        new_count = self.get_new_data_count()
        return new_count >= threshold
    
    def close(self):
        self.conn.close()