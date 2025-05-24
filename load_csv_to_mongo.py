import pandas as pd
from pymongo import MongoClient

def load_csv_to_mongo(csv_file, db_name="mydb", collection_name="user"):
    client = MongoClient("mongodb://localhost:27017/")
    db = client[db_name]
    collection = db[collection_name]
    
    df = pd.read_csv(csv_file)
    data = df.to_dict(orient='records')
    collection.insert_many(data)
    print(f"✅ Inserted {len(data)} records into {db_name}.{collection_name}")

if __name__ == "__main__":
    load_csv_to_mongo("C:/Users/DELL/Desktop/mangop1.csv")
