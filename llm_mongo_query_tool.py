import os
import pandas as pd
from pymongo import MongoClient
from together import Together

# === CONFIGURATION ===
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "mydb"
COLLECTION_NAME = "user"
TOGETHER_API_KEY = "085078471a75adad45e2d56224fce3001bc1e820857735acfe01eccafc9d4b45"  # ✅ Your actual Together.ai API key
TOGETHER_MODEL = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"  # ✅ Correct model name

os.environ["TOGETHER_API_KEY"] = TOGETHER_API_KEY

# === SETUP ===
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    exit(1)

try:
    together_client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
except Exception as e:
    print(f"❌ Together client init failed: {e}")
    exit(1)

# === FUNCTION: Generate MongoDB Query ===
def generate_mongo_query(user_question: str) -> str:
    prompt = f"""
You are a MongoDB expert. Convert the following user request into a valid PyMongo-style MongoDB query for the 'user' collection.
Return only the dictionary part of the query (omit collection.find()).

Request: {user_question}
MongoDB Query:
"""
    try:
        response = together_client.chat.completions.create(
            model=TOGETHER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )
        query_str = response.choices[0].message.content.strip()
        print("\n📋 Raw query from LLM:\n", query_str)
        return query_str
    except Exception as e:
        raise RuntimeError(f"LLM query generation failed: {str(e)}")

# === FUNCTION: Run MongoDB Query ===
def run_query(query_code: str):
    try:
        print("\n🔍 Evaluating Query:")
        print(query_code)
        query_dict = eval(query_code)  # Trusted output only
        if not isinstance(query_dict, dict):
            raise ValueError("Generated query is not a valid dictionary.")
        results = list(collection.find(query_dict))
        return results
    except Exception as e:
        raise RuntimeError(f"MongoDB query execution failed: {str(e)}")

# === FUNCTION: Log Query ===
def log_query(user_question: str, query_code: str):
    with open("Queries_generated.txt", "a", encoding="utf-8") as f:
        f.write(f"Q: {user_question}\nQuery: {query_code}\n\n")

# === MAIN FUNCTION ===
def main():
    print("🔎 Welcome to the LLM MongoDB Query Tool")
    print("You can ask natural language questions about your product data.\n")

    try:
        user_question = input("🧠 Enter your query (e.g., 'Find all products with rating < 4.5'): ").strip()
        query_code = generate_mongo_query(user_question)
        log_query(user_question, query_code)

        results = run_query(query_code)
        if not results:
            print("\n⚠️ No matching documents found.")
            return

        df = pd.DataFrame(results).drop(columns=["_id"], errors="ignore")

        print("\n🎯 Choose output format:")
        print("1. Display in terminal")
        print("2. Save to CSV")

        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            print("\n📊 Query Results:\n")
            print(df.to_markdown(index=False))
        elif choice == "2":
            filename = input("Enter filename to save (e.g., test_case1.csv): ").strip()
            df.to_csv(filename, index=False)
            print(f"✅ Results saved to {filename}")
        else:
            print("❌ Invalid choice.")

    except Exception as e:
        print(f"\n🚨 Error: {str(e)}")
        print("💡 Please check your question, query syntax, or MongoDB setup.")

if __name__ == "__main__":
    main()
