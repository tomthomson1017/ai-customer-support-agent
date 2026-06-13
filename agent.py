import json
import os
from datetime import datetime
from openai import OpenAI

client = OpenAI()

def load_company():
    with open("company.json", "r") as f:
        return json.load(f)

def build_system_prompt(company):
    faqs = "\n".join(company["faqs"])
    return f"""You are a helpful customer support agent for {company["name"]}.

About the company:
{company["description"]}

Frequently asked questions:
{faqs}

Important rules:
- Only answer based on the information above
- If you don't know the answer, say exactly: "I don't have that information. Let me escalate this to a human agent."
- Be friendly, concise, and professional
- Never make up information"""

def log_escalation(user_message):
    with open("escalations.log", "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {user_message}\n")

def get_response(user_message, chat_history):
    company = load_company()
    system_prompt = build_system_prompt(company)

    messages = [{"role": "system", "content": system_prompt}]
    messages += chat_history
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    reply = response.choices[0].message.content

    if "escalate" in reply.lower():
        log_escalation(user_message)

    return reply
