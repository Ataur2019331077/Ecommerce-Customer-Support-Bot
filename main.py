from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
import requests
from dotenv import load_dotenv
load_dotenv()
import os
from langchain.chat_models import init_chat_model

user_message = []
last_message_type = None

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

llm = init_chat_model("google_genai:gemini-2.0-flash")

class MessageClassifier(BaseModel):
    message_type: Literal["order", "shipping", "complaint", "faq"] = Field(
        ...,
        description="Classify the user message as either 'order', 'shipping', 'complaint', or 'faq'."
    )


class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str 


def classify_message(state: State):
    global last_message_type
    #print(last_message_type)
    last_message = state["messages"][-1]
    
    classifier_llm = llm.with_structured_output(MessageClassifier)

    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": f"""
            Classify the user message as either:
            - 'order' if the message is about placing an order or checking order status,
            - 'shipping' if the message is about shipping or delivery,
            - 'complaint' if the message is a complaint,
            - 'faq' if the message is a frequently asked question(if the message does not fit into any of the above categories, classify it as 'faq').

            if you think user provide something that is related to previous message here is last message type: {last_message_type}
            and select this as message type if you think it is related to previous message.
            """
        },
        {"role": "user", "content": last_message.content}
    ])
    
    last_message_type = result.message_type

    return {"message_type": result.message_type}


def router(state: State):
    message_type = state.get("message_type", None)
    if not message_type:
        return {"next": None}

    # Define the routing logic based on the message type
    routing_map = {
        "order":"order_agent",
        "shipping": "shipping_agent",
        "complaint": "complaint_agent",
        "faq": "faq_agent"
    }

    next_node = routing_map.get(message_type, None)
    return {"next": next_node}
    




def order_agent(state: State):
    last_message = state["messages"][-1]
    response = llm.invoke([
        {"role": "system", 
         "content": """You are an order agent. Respond to the user's order query.
            provide necessary information to create a perfect endpoint of order -> /order/orderId.
            You should only return the endpoint like this:
            /order/12345686745656ghy768

            if user does not provide report id ask for it and do not say about enpoint as you are an assistant.
            Id can be at least 4 characters long and can't contain alphanumeric characters.
         """
         },
        {"role": "user", "content": last_message.content}
    ])

    reply_text = response.content.strip()
    if reply_text.startswith("/order/"):
        order_id = reply_text.split("/order/")[1]
        # Simulate fetching order details from a database or API
        print(f"Fetching order details for order ID: {order_id}")
        response = requests.get(f"http://localhost:8000/order/{order_id}")
        if response.status_code == 200:
            order_info = response.json()
            message_ = order_info[0].get("status", "No message returned.") if order_info else "No order found."
            state["messages"].append({"role": "assistant", "content": message_})
            return state
         
    state["messages"].append({"role": "assistant", "content": response.content})
    return state




def shipping_agent(state: State):
    global user_message
    last_user_message = user_message[-1] if user_message else ""


    last_message = state["messages"][-1]
    response = llm.invoke([
        {"role": "system", "content": f"""You are a shipping agent. Respond to the user's shipping query.
            provide necessary information to create a perfect endpoint of shipping -> /shipping/orderId.
            You should only return the endpoint like this:
            /shipping/12345686745656ghy768/<delivery_date>/<delivery_address>
            
         
         if user does not provide order id and delivery_date, delivery_address ask for it and do not say about enpoint as you are an assistant.
         here is last user message: {last_user_message} if you need it.
         Id can be at least 4 characters long and can't contain alphanumeric characters.
         """},
        {"role": "user", "content": last_message.content}
    ])

    reply_text = response.content.strip()
    if reply_text.startswith("/shipping/"):
        parts = reply_text.strip().split("/")
        if len(parts) >= 5:
            _, _, order_id, delivery_date, delivery_address = parts[:5]
        # Simulate fetching shipping details from a database or API
        respone = requests.put(
            f"http://localhost:8000/shipping/{order_id}",
            json={
                "orderId": order_id,
                "delivery_date": delivery_date if delivery_date else "2023-10-01",
                "delivery_address": delivery_address if delivery_address else "123 Main St, City, Country"
                })
        if respone.status_code == 200:
            shipping_info = respone.json()
            message_ = shipping_info.get("message", "No message returned.")
            state["messages"].append({"role": "assistant", "content": message_})
            return state
    
    state["messages"].append({"role": "assistant", "content": response.content})
    return state

def complaint_agent(state: State):
    global user_message
    last_user_message = user_message[-1] if user_message else ""
    last_message = state["messages"][-1]
    
    response = llm.invoke([
        {"role": "system", "content": 
         f"""You are a complaint agent. Respond to the user's complaint.
            provide necessary information to create a perfect endpoint of complaint -> /complaint/orderId.
            You should only return the endpoint like this:
            /complaint/12345686745656ghy768/<complaint_text>
        
            if user does not provide order id, complaint ask for it and do not say about enpoint as you are an assistant.
            here is last user message: {last_user_message} if you need it.
            Id can be at least 4 characters long and can't contain alphanumeric characters.
            """},
        {"role": "user", "content": last_message.content}
    ])

    reply_text = response.content.strip()
    if reply_text.startswith("/complaint/"):
        parts = reply_text.strip().split("/")
        if len(parts) >= 4:
            _, _, order_id, complaint_text = parts[:4]
        last_message = state["messages"][-1]
        response = requests.post(
            "http://localhost:8000/complaint",
            json={
                "orderId": order_id,
                "complaint": complaint_text
            }
        )
        if response.status_code == 200:
            complaint_info = response.json()
            message_ = complaint_info.get("message", "No message returned.")
            state["messages"].append({"role": "assistant", "content": message_})
            return state
    
    state["messages"].append({"role": "assistant", "content": response.content})
    return state

def faq_agent(state: State):
    with open("faq.txt", "r") as file:
        faq_text = file.read()
    

    last_message = state["messages"][-1]
    response = llm.invoke([
        {"role": "system", "content": f"You are a FAQ agent. Respond to the user's frequently asked question. Here is the FAQ text:\n{faq_text}"},
        {"role": "user", "content": last_message.content}
    ])
    
    state["messages"].append({"role": "assistant", "content": response.content})
    return state




graph_builder = StateGraph(State)
graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("order_agent", order_agent)
graph_builder.add_node("shipping_agent", shipping_agent)
graph_builder.add_node("complaint_agent", complaint_agent)
graph_builder.add_node("faq_agent", faq_agent)
graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")
graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next"),
    {
        "order_agent": "order_agent",
        "shipping_agent": "shipping_agent",
        "complaint_agent": "complaint_agent",
        "faq_agent": "faq_agent"
    }
)

graph_builder.add_edge("order_agent", END)
graph_builder.add_edge("shipping_agent", END) 
graph_builder.add_edge("complaint_agent", END)
graph_builder.add_edge("faq_agent", END)
graph = graph_builder.compile()


def run_chatbot():
    state = {"messages": [], "message_type": None}

    while True:
        user_input = input("Message: ")
        if user_input == "exit":
            print("Bye")
            break

        state["messages"] = state.get("messages", []) + [
            {"role": "user", "content": user_input}
        ]
        user_message.append(user_input)

        state = graph.invoke(state)

        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state["messages"][-1]
            print(f"Assistant: {last_message.content}")


if __name__ == "__main__":
    run_chatbot()