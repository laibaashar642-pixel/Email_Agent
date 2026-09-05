from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware, PIIMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
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

@tool
def get_deadline_info(project_name: str) -> str:
    """
    Get the deadline and current status information for a given project.
    Args:
        project_name (str): The name of the project to look up.
    Returns:
        str: Deadline date, time, and current status of the project.
    """
    deadlines = {
        "signbridge": "Deadline: 15th October 2026, 6:00 PM. Current status: Backend 70% complete.",
    }
    return deadlines.get(project_name.lower(), "No deadline information found for this project.")

system_prompt = """You are a professional email assistant working on behalf of Laiba, 
a Project Coordinator. When asked to send an email, always write in a formal, 
professional tone, even if the user's instruction is casual or brief. 
Always sign emails as 'Laiba, Project Coordinator' instead of using a placeholder. 
Never include passwords, API keys, or credentials in any email content."""

model = ChatGroq(model="openai/gpt-oss-20b", api_key=os.getenv("GROQ_API_KEY"))

agent = create_agent(
    model,
    tools=[send_email_tool, get_deadline_info],
    system_prompt=system_prompt,
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={"send_email_tool": True}
        ),
        PIIMiddleware(
            "api_key",
            detector=r"(gsk_[a-zA-Z0-9]{20,}|sk-[a-zA-Z0-9]{20,})",
            strategy="block",
            apply_to_output=True,
            apply_to_tool_results=True,
        ),
    ],
    checkpointer=InMemorySaver(),
)

config = {"configurable": {"thread_id": "email-session-1"}}

# Step 1: Agent ko instruction dein
response = agent.invoke(
    {"messages": [
        {"role": "user", "content": "Send an email to muhammad.qasim.dev07@gmail.com about the SignBridge project deadline so the next developer can be informed."}
    ]},
    config=config
)

# Step 2: Check karein kya agent ruka hua hai (interrupt) approval ke liye
if "__interrupt__" in response:
    interrupt_data = response["__interrupt__"][0].value
    print("\n⏸  APPROVAL NEEDED")
    print(interrupt_data)

    decision = input("\nApprove this email? (yes/no): ").strip().lower()

    if decision == "yes":
        final_response = agent.invoke(
            Command(resume={"decisions": [{"type": "approve"}]}),
            config=config
        )
    else:
        final_response = agent.invoke(
            Command(resume={"decisions": [{"type": "reject"}]}),
            config=config
        )

    print(final_response["messages"][-1].content)
else:
    print(response["messages"][-1].content)