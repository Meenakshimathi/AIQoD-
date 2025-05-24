import os
import pandas as pd
from pymongo import MongoClient
from together import Together

# === MongoDB Setup ===
client = MongoClient("mongodb://localhost:27017/")
db_name = "mydb"                  # ✅ Matches MongoDB Compass
collection_name = "user"         # ✅ Matches MongoDB Compass
db = client[db_name]
collection = db[collection_name]

# === Together.ai Setup ===
os.environ["TOGETHER_API_KEY"] = "your_real_api_key_here"  # ✅ Replace with your actual API key
together_client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

# === Generate MongoDB Query using Together.ai ===
def generate_mongo_query_llama4(column_input):
    prompt = f"""
You are a MongoDB expert. Convert the following natural language request into a valid PyMongo-style MongoDB query for the collection called 'user'.
Return ONLY the query dictionary inside collection.find() — no Python code, no comments.

Request: {column_input}
MongoDB Query:
"""

    response = together_client.chat.completions.create(
        model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",  # ✅ Your model of choice
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=300,
    )

    query_str = response.choices[0].message.content.strip()
    return query_str

# === Execute the MongoDB Query ===
def run_query_on_mongo(query_str):
    try:
        print("\n📋 Evaluating Query String:\n", query_str)
        # Assumes query_str is a raw dictionary string
        query = eval(query_str)
        if not isinstance(query, dict):
            raise ValueError("Generated query is not a valid Python dictionary.")
        results = list(collection.find(query))
        return results
    except Exception as e:
        print("❌ Query execution failed:", str(e))
        return []

# === Main User Interface ===
def main():
    print("🔎 Welcome to the LLM MongoDB Query Tool")
    user_input = input("💬 Enter your query (e.g., 'products with rating > 4.5'): ").strip()

    try:
        query_str = generate_mongo_query_llama4(user_input)
        print("\n✅ Generated MongoDB Query Dictionary:\n", query_str)

        results = run_query_on_mongo(query_str)
        if not results:
            print("\n⚠️ No matching records found or invalid query.")
            return

        df = pd.DataFrame(results).drop(columns=["_id"], errors="ignore")

        choice = input("\n💾 Do you want to save the results to a CSV file? (yes/no): ").strip().lower()
        if choice == "yes":
            file_name = input("Enter filename (e.g., test_case1.csv): ").strip()
            df.to_csv(file_name, index=False)
            print(f"✅ Saved to {file_name}")
        else:
            print("\n📊 Query Results:\n")
            print(df)

    except Exception as e:
        print(f"\n🚨 Error: {e}")
        print("💡 Check the API key, model name, query format, or MongoDB setup.")

if __name__ == "__main__":
    main()
