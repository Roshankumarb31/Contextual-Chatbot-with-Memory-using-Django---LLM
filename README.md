# QueryBot 🧠💬

**QueryBot** is a smart, memory-aware chatbot powered by **LangChain**, **Google Gemini**, and **Django**. It understands natural language queries, maintains context across conversations, generates and executes SQL queries, and can optionally perform image-based similarity searches using **FAISS** and **ResNet50**.

---

## 🚀 Features

- 💬 Natural language to SQL conversion via LLM  
- 🧠 Entity Memory for multi-turn contextual conversations  
- 🗃️ PostgreSQL database integration with live query results  
- 📊 Structured JSON outputs with tabular display flags  
- 🖼️ *(Optional)* Visual similarity search using FAISS + ResNet50  
- 🔐 Environment-based API key and path configuration  

---

## 📂 Project Structure

```

querybot/
├── chatapp/
│   ├── chat\_logic.py          # LLM + LangChain chat logic
│   ├── response\_tools.py      # SQL execution + formatting
│   ├── feature\_extractor.py   # TensorFlow ResNet50 embedding extractor (optional)
│   ├── find\_similars.py       # FAISS-based visual similarity search (optional)
│   ├── views.py               # Django API endpoints
│   └── urls.py                # Routes
├── querybot/                  # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── static/
│   ├── assets/
│   │   └── main\_logo.png
│   ├── css/
│   │   └── chat.css
│   ├── js/
│   │   └── chat.js
│   └── json/
│       ├── data.json
│       └── output\_data.json
├── templates/
│   └── chat.html              # Chat frontend template
├── .env                      # Environment variables (API keys etc.)
├── db.sqlite3
├── manage.py
├── requirements.txt
└── README.md
```



---

## 📦 Requirements

```bash
django
langchain
langchain-google-genai
google-generativeai
numpy
tensorflow
pickle5
psycopg2-binary
````

> ⚠️ Optional for image similarity:
> `faiss-cpu`
> Install with: `pip install faiss-cpu`

---

## 🧠 Chatbot with Entity Memory

* Uses LangChain’s `ConversationEntityMemory` for persistent, context-aware conversations
* Generates SQL queries from natural language and executes on connected DB
* Returns JSON responses including the SQL query and display flags, e.g.:

```json
{
  "reply": "Showing sales data for the last month.",
  "sql_query": "SELECT * FROM sales WHERE sale_date >= CURRENT_DATE - INTERVAL '30 days';",
  "is_query_generated": 1,
  "table_display": 1
}
```

---

## 🖼️ Optional: Visual Similarity Search

* Extracts image embeddings using TensorFlow ResNet50 (`feature_extractor.py`)
* Searches for visually similar items with FAISS index (`find_similars.py`)
* Returns top matches from metadata JSON (`data.json` or similar)

Example usage:

```python
from feature_extractor import extract_features
from find_similars import find_similar_items

features = extract_features("sample.jpg")
results = find_similar_items(features, top_k=10)
```

---

## ⚙️ Setup Instructions

1. **Clone the repo**

```bash
git clone https://github.com/your-username/querybot.git
cd querybot
```

2. **Create & activate virtual environment**

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure `.env`**

Add your API keys, e.g.:

```
MODEL_API_KEY=your_gemini_api_key
```

5. **Run the Django server**

```bash
python manage.py migrate
python manage.py runserver
```

Open `http://localhost:8000/chat` to test the chatbot UI.

---

## 🔧 Optional: Image Search Setup

* Place your FAISS index file (`your_index_file.index`) and metadata pickle (`your_metadata.pkl`) in the project root or configured path
* Keep your image metadata JSON (`data.json`) updated
* Image search feature activates only if those files are present

---

## 🤝 Integration & Extensibility

* Connect with any frontend (React, Vue, mobile apps) via Django REST API
* Extend with voice-to-text or other AI modules easily
* Adapt database backend with minimal changes

---

## 🧑‍💻 Maintainer

**Roshan Kumar B**  
AI & Machine Learning Engineer | Django Backend Developer  
Specializing in building scalable backend systems integrated with machine learning, natural language processing, and computer vision.

---

## 📄 License

MIT License — free for personal and commercial use.

---

> ⚙️ Developer Ready. LLM-Powered. Visual-Aware. QueryBot is your smart assistant for advanced contextual queries.

---
