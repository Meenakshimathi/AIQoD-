import pandas as pd
from pymongo import MongoClient
from query_with_llm import generate_mongo_query

# === MongoDB Query Executor ===
def run_query_on_mongo(query_str):
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["mydb"]             # ✅ Updated to match your database
        collection = db["user"]         # ✅ Updated to match your collection

        print("\n📋 Evaluating Query String:\n", query_str)
        query = eval(query_str)         # Assumes it's a dict from LLM
        if not isinstance(query, dict):
            raise ValueError("Query is not a valid dictionary.")

        results = list(collection.find(query))
        return results
    except Exception as e:
        raise RuntimeError(f"Error executing MongoDB query: {e}")

# === Main Function ===
def main():
    print("🔍 LLM-Powered MongoDB Query Runner\n")
    user_input = input("🧠 Enter your natural language query: ").strip()

    try:
        query = generate_mongo_query(user_input)
        print("\n✅ LLM Generated Query:\n", query)

        results = run_query_on_mongo(query)
        if not results:
            print("⚠️ No matching results found.")
            return

        df = pd.DataFrame(results).drop(columns=["_id"], errors="ignore")

        choice = input("\n💾 Do you want to save the results to a CSV file? (yes/no): ").strip().lower()
        if choice == "yes":
            filename = input("Enter filename (e.g., test_case1.csv): ").strip()
            df.to_csv(filename, index=False)
            print(f"✅ Results saved to {filename}")
        else:
            print("\n📊 Results:\n")
            print(df.to_markdown(index=False))

    except Exception as e:
        print("\n🚨 Error:", str(e))
        print("💡 Check if your query, LLM, or MongoDB connection is valid.")

if __name__ == "__main__":
    main()
