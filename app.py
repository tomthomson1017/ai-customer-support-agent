import streamlit as st
import json
from agent import get_response

st.set_page_config(page_title="AI Support Agent", page_icon="🤖")

def load_company():
    try:
        with open("company.json", "r") as f:
            return json.load(f)
    except:
        return None

def save_company(name, description, faqs):
    data = {
        "name": name,
        "description": description,
        "faqs": faqs
    }
    with open("company.json", "w") as f:
        json.dump(data, f, indent=2)

def format_chat_for_export(chat_history, company_name):
    lines = [f"Support Chat — {company_name}", "=" * 40, ""]
    for message in chat_history:
        role = "Customer" if message["role"] == "user" else "Agent"
        lines.append(f"{role}: {message['content']}")
        lines.append("")
    return "\n".join(lines)

page = st.sidebar.radio("Navigation", ["⚙️ Setup", "💬 Chat", "📋 Escalations"])

if page == "⚙️ Setup":
    st.title("⚙️ Company Setup")
    st.caption("Configure your AI support agent")

    company = load_company()

    name = st.text_input(
        "Company Name",
        value=company["name"] if company else ""
    )

    description = st.text_area(
        "Company Description",
        value=company["description"] if company else "",
        height=100
    )

    st.subheader("FAQs")
    st.caption("Enter each FAQ on a new line in this format: Q: question A: answer")

    faqs_text = st.text_area(
        "FAQs",
        value="\n".join(company["faqs"]) if company else "",
        height=200
    )

    if st.button("💾 Save Configuration"):
        if name and description and faqs_text:
            faqs_list = [f.strip() for f in faqs_text.strip().split("\n") if f.strip()]
            save_company(name, description, faqs_list)
            st.success("✅ Configuration saved! Go to the Chat page to test your agent.")
            st.session_state.chat_history = []
        else:
            st.error("Please fill in all fields before saving.")

elif page == "💬 Chat":
    company = load_company()

    if not company:
        st.warning("⚠️ Please set up your company first. Go to the Setup page.")
    else:
        st.title(f"🤖 {company['name']} Support Agent")
        st.caption("Powered by AI — Ask me anything")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        user_input = st.chat_input("Type your question here...")

        if user_input:
            with st.chat_message("user"):
                st.write(user_input)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    reply = get_response(user_input, st.session_state.chat_history)
                st.write(reply)

            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

        if st.session_state.get("chat_history"):
            export_text = format_chat_for_export(
                st.session_state.chat_history,
                company["name"]
            )
            st.download_button(
                label="⬇️ Export Chat",
                data=export_text,
                file_name="chat_export.txt",
                mime="text/plain"
            )

elif page == "📋 Escalations":
    st.title("📋 Escalation Log")
    st.caption("Questions the AI could not answer")

    try:
        with open("escalations.log", "r") as f:
            logs = f.read()
        if logs:
            st.code(logs)
        else:
            st.info("No escalations yet.")
    except FileNotFoundError:
        st.info("No escalations yet.")
