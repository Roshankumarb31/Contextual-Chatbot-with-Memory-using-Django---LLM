import os
import json
from dotenv import load_dotenv
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage
from django.conf import settings
from .response_tools import clean_response, fetch_from_db

load_dotenv()

INITIAL_INSTRUCTION = """
You are an intelligent AI assistant capable of understanding natural language queries and generating relevant SQL queries.

Your responsibilities:
- Engage with the user conversationally to collect necessary context.
- When confident, generate a valid SQL query based on the discussion.
- Use memory to remember context from previous interactions.
- Respond only in **valid JSON** format with the following fields:
    {
        "reply": [your message to the user],
        "sql_query": [SQL query if generated, else null],
        "is_query_generated": 1 if a query is generated, otherwise 0,
        "table_display": 1 if the query result is tabular (more than one column), else 0
    }
Rules:
- Do not reveal that you're generating or working with SQL.
- If the user goes off-topic, politely steer the conversation back.
- Be concise, context-aware, and user-friendly in your responses.
"""

def initialize_llm():
    API_KEY = os.getenv("MODEL_API_KEY")
    if not API_KEY:
        raise ValueError("API key is missing.")
    
    model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash")
    llm = ChatGoogleGenerativeAI(model = model_name, temperature = 0, google_api_key = API_KEY)
    return llm

def initialize_entity_memory(llm, memory_data):
    messages = []
    
    if not memory_data:
        messages.append(HumanMessage(content=INITIAL_INSTRUCTION))
    
    for msg in memory_data:
        if msg["type"] == "human":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["type"] == "ai":
            messages.append(AIMessage(content=msg["content"]))

    entity_memory = ConversationEntityMemory(llm=llm, k=5, input_key="input")
    entity_memory.chat_memory.messages = messages
    
    return entity_memory

def get_conversation_response(entity_memory, user_input, db_data = False):
    conversation = ConversationChain(
        llm=entity_memory.llm,
        prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
        memory=entity_memory
    )
    if db_data:
        user_input += f"This is the data fetched from the database: {db_data}"
    return conversation.run(input=user_input)


def verify_response(entity_memory, response):
    response = clean_response(response)
    print(response)

    if not response or not response.get("is_query_generated"):
        return "Sorry, something went wrong while processing your request.", False
    
    is_db_found = fetch_from_db(response["query"])
    print("Data Found" if is_db_found else "Data not Found")
    
    if not response["table_display"]:
        json_dir = os.path.join(settings.BASE_DIR, 'static', 'json')
        os.makedirs(json_dir, exist_ok=True)
        file_path = os.path.join(json_dir, 'data.json')

        with open(file_path, 'r') as json_file:
            table_data = json.load(json_file)
            # print(table_data)
    
        db_response = clean_response(get_conversation_response(entity_memory, table_data, db_data = True))
        db_response["table_display"] = False
        print("@@@@", db_response["reply"], db_response["table_display"], "@@@@")
        return db_response["reply"], db_response["table_display"]
    else:
        return response["reply"], response["table_display"]



def get_chat_response(user_input: str, session: dict) -> tuple:
    llm = initialize_llm()
    memory_data = session.get("entity_memory", [])
    print("session intialized")
    
    entity_memory = initialize_entity_memory(llm, memory_data)
    print("memory intialized")
    
    response = get_conversation_response(entity_memory, user_input)
    print("got response")
    
    response, is_tableview = verify_response(entity_memory, response)
    print("response verified")
    
    session["entity_memory"] = [
        {"type": "human", "content": msg.content} if isinstance(msg, HumanMessage) 
        else {"type": "ai", "content": msg.content} for msg in entity_memory.chat_memory.messages
    ]

    """
    --> Use an update function instead of doing it manually:
        update_session_memory(entity_memory, session)
    """

    return response, is_tableview
