import pymongo
import sys

# CONFIGURATION
# Use 27018 if running from Windows (VS Code), use 27017 if running inside Docker


def detect () :
    MONGO_URI = "mongodb://localhost:27018/" 
    DB_NAME = "universiteDB"
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        
        # 1. Does the collection exist?
        colls = db.list_collection_names()
        if "etudiants" not in colls:
            print("❌ CRITICAL: Collection 'etudiants' does not exist!")
            sys.exit()

        # 2. What indexes exist?
        # (Sharding requires an index on the Shard Key)
        indexes = db.etudiants.index_information()
        string = ''
        
        if "faculte_1" in indexes:
            string ='FACULTE'
        elif "annee_universitaire_1" in indexes:
            string = 'ANNEE'
        else:
            print("\n⚠️ RESULT: No Sharding Index found!")
            print("💡 HINT: You likely forgot to run 'setup_sharding.js' after the last restart.")

    except Exception as e:
        print(f"\n💥 Connection Error: {e}")
    finally:
        return string

