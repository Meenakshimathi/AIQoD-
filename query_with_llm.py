import os
from together import Together

# ✅ Set your actual API key here (replace the string below with your real key)
os.environ["TOGETHER_API_KEY"] = "together_xxx123abc456"  # ✅ Use your real Together API key

# ✅ Initialize Together client using the actual API key
client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

# ✅ Query generation using your desired model
def generate_mongo_query(user_input):
    prompt = f"""
You are an expert in MongoDB. Convert the following natural language query into a MongoDB query.
Return ONLY the MongoDB query dictionary (omit 'collection.find' or 'db.collection.find').

Natural language: {user_input}
MongoDB query:
"""
    response = client.chat.completions.create(
        model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",  # ✅ Your chosen model
        messages=[{"role": "user", "content": prompt}],
        max_tokens=256,
        temperature=0.5,
    )

    mongo_query = response.choices[0].message.content.strip()
    log_query(user_input, mongo_query)
    return mongo_query

# ✅ Logging function
def log_query(question, query):
    with open("Queries_generated.txt", "a", encoding="utf-8") as f:
        f.write(f"Q: {question}\nQuery: {query}\n\n")
