from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_agent
from dotenv import load_dotenv
import os
from sendmail import send_email

load_dotenv()

@tool
def send_email_tool(to_email: str, subject: str, body: str) -> str:
    """
    Send an email to the specified recipient with the given subject and body.

    Args:
        to_email (str): The recipient's email address.
        subject (str): The subject line of the email.
        body (str): The main content/message of the email.

    Returns:
        str: A message indicating the success or failure of the email sending operation.
    """
    return send_email(to_email, subject, body)

# model = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
model = ChatGroq(model="openai/gpt-oss-20b", api_key=os.getenv("GROQ_API_KEY"))
agent = create_agent(model, tools=[send_email_tool])

response = agent.invoke({
    "messages": [
        {"role": "user", "content": "Send an email to muhammad.qasim.dev07@gmail.com with subject 'Test from LangChain Agent' and a short friendly message saying this is a test."}
    ]
})

print(response["messages"][-1].content)