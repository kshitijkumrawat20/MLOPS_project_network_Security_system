from src.data.sqlite_manager import PhishingDataManager

if __name__ == "__main__":
    FILE_PATH = "data/phisingData.csv"
    
    print("Initializing SQLite database...")
    db_manager = PhishingDataManager()
    
    print("Loading data from CSV...")
    count = db_manager.insert_data_from_csv(FILE_PATH)
    
    print(f"✅ Successfully loaded {count} records into SQLite database!")
    print(f"Database location: data/phishing_data.db")
    
    db_manager.close()