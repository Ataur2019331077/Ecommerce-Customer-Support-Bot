
# 🛒 Open E-Commerce AI Assistant

This project is an AI-powered customer support assistant for an e-commerce platform, built using **FastAPI, MongoDB**, and **LangGraph (LangChain)**. It classifies user messages and intelligently routes them to agents that handle orders, shipping, complaints, or FAQs using a **Large Language Model (Gemini)**.

---

## 📌 Features
- 🔍 Message Classification: Classifies incoming messages into order, shipping, complaint, or faq.

- 🛍️ Order Agent: Retrieves order details based on orderId.

- 📦 Shipping Agent: Updates shipping info like address and delivery date.

- 😡 Complaint Agent: Logs complaints against orders and returns a unique issue token.

- ❓ FAQ Agent: Answers common queries using a knowledge base from a faq.txt file.

- 🔁 LangGraph Routing: Uses LangGraph to orchestrate classification → routing → agent responses.

- 🧠 LLM-Powered Understanding: Utilizes Google Gemini 2.0 Flash for natural language understanding.

## 🛠️ Tech Stack
- Backend: FastAPI

- LLM: Google Gemini (via LangChain)

- Graph Workflow: LangGraph

- Database: MongoDB

- Environment: Python 3.10+

- Other Tools: pydantic, requests, dotenv, bson

📂 Project Structure
```
├── main.py                   
├── app.py               
├── faq.txt                    
├── .env                       
├── requirements.txt           
└── README.md                  
```
## 📥 Installation
1. Clone the repository
```
git clone https://github.com/Astaiss/ecommerce-customer-support.git
cd open-ecommerce-assistant
```
2. Create a virtual environment
```
python -m venv venv
source venv/bin/activate  # for windows
```
3. Install dependencies
```
pip install -r requirements.txt
```
4. Setup .env file
Create a .env file and fill in your credentials:
```
GOOGLE_API_KEY=your_google_api_key
MONGO_URI=your_mongodb_uri
```

## 🚀 Running the App
1. Start FastAPI Backend
```
uvicorn app:app --reload
```

2. Run LangGraph Logic
```
python main.py
```

## ✅ API Endpoints
| Method | Endpoint              | Description            |
|--------|------------------------|------------------------|
| GET    | `/order/{orderId}`     | Fetch order details    |
| POST   | `/complaint`           | Submit a complaint     |
| PUT    | `/shipping/{orderId}`  | Update shipping info   |


## 🤖 LangGraph Agents
| Agent           | Responsibility                          |
|------------------|------------------------------------------|
| `order_agent`    | Handle order queries                     |
| `shipping_agent` | Manage delivery address and date         |
| `complaint_agent`| Register customer complaints             |
| `faq_agent`      | Respond to general questions using faq.txt |


## 📘 How it Works

1. user message is classified by `classify_message(state: State)` 
2. then message goes to `router(state: State)`
3. then router routes to appropriate agent.
    - `order_agent(state: State)`
    - `complaint_agent(state: State)`
    - `shipping_agent(state: State)`
    - `faq_agent(state: State)`

Here is some input and AI Assistant respone

```
Message: where is my order?
Assistant: Can you please provide your order ID?
Message: 1234
Assistant: pending
```

```
Message: I have received bad product
Assistant: I am sorry to hear that you received a bad product.

To help me investigate this issue, could you please provide the order ID associated with your purchase? The ID can be at least 4 characters long and can't contain alphanumeric characters.
Message: 45667
Assistant: Complaint created successfully.
```
```
Message: I want to change my shipping address
Assistant: Okay, I can help you with that. To change your shipping address, I'll need your order ID and the new delivery address.
Message: order id 1235 and date:30june,2025 and new location Rangpur
Assistant: Shipping details updated successfully.
```
```
Message: what is your return policy?
Assistant: Returns and exchanges are accepted within 7-30 days of delivery, provided the item is unused, in its original condition, and returned with all tags and packaging. Return shipping is free for damaged or incorrect items. Refunds are initiated after the returned item is received and inspected.
Message: Are coupon codes allowed?
Assistant: Yes, coupon codes can be applied at checkout. Terms and conditions for each offer are displayed on the promotions page.
```

## Resource 
- [Langgraph](https://www.langchain.com/langgraph)
- [Fastapi](https://fastapi.tiangolo.com/)
- [Video Tutorial](https://www.youtube.com/watch?v=1w5cCXlh7JQ)


## 📄 License
[MIT License](LICENSE.md) – feel free to use, modify, and contribute.

