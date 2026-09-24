import os
import json
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_core.memory import ListMemory, MemoryContent
from autogen_agentchat.ui import Console
from core.config import get_model_client

STATE_FILE = "workspace/team_state.json"
MEMORY_FILE = "workspace/dynamic_memory.json"
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# ---------------------------------------------------------
# TOOLS
# ---------------------------------------------------------
def save_fact(fact: str) -> str:
    """Use this tool to save important user preferences, rules, or project details to long-term memory."""
    facts = []
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            facts = json.load(f)
            
    if fact not in facts:
        facts.append(fact)
        
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w") as f:
        json.dump(facts, f)
        
    return f"Successfully saved to long-term memory: {fact}"

def send_gmail(recipient: str, subject: str, body: str) -> str:
    """Use this tool to send an email to a client or team member via Gmail OAuth."""
    creds = None
    token_path = 'workspace/token.json'
    
    client_config = {
        "installed": {
            "client_id": os.getenv("GMAIL_CLIENT_ID"),
            "client_secret": os.getenv("GMAIL_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": ["http://localhost:8080"]  # <-- Must match port 8080
        }
    }
    
    if not client_config["installed"]["client_id"] or not client_config["installed"]["client_secret"]:
        return "ERROR: Gmail OAuth keys are missing from the .env file."

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)  # <-- Must be explicitly 8080, not 0
            
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            
    try:
        service = build('gmail', 'v1', credentials=creds)
        message = EmailMessage()
        message.set_content(body)
        message['To'] = recipient
        message['Subject'] = subject
        
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        return f"SUCCESS: Email sent to {recipient}. Message ID: {send_message['id']}"
    except Exception as e:
        return f"ERROR: Failed to send email - {str(e)}"

# ---------------------------------------------------------
# EXECUTION
# ---------------------------------------------------------
async def execute_team_task(task: str):
    model_client = get_model_client()
    
    # 1. Initialize Memory
    shared_memory = ListMemory()
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            saved_facts = json.load(f)
        for fact in saved_facts:
            await shared_memory.add(MemoryContent(content=fact, mime_type="text/plain"))
    else:
        await shared_memory.add(MemoryContent(content="The user prefers Python, Streamlit for UI, FAISS/Neo4j for RAG, and n8n for workflows.", mime_type="text/plain"))
    
    # 2. Define Agents with Strict Tool-Execution Prompts
    developer = AssistantAgent(
        "Software_Developer", 
        model_client=model_client, 
        memory=[shared_memory], 
        description="Route here ONLY for writing or debugging Python code. NEVER route here if the word 'email' or 'mail' is in the prompt.",
        system_message="You are a Python developer. You write code. You DO NOT send emails and you DO NOT explain how to send emails."
    )
    
    tester = AssistantAgent(
        "Testing_Engineer", 
        model_client=model_client, 
        memory=[shared_memory], 
        description="Route here ONLY for testing code. NEVER route here for emails.",
        system_message="You are a QA Tester. You test code. You DO NOT send emails."
    )
    
    hr = AssistantAgent(
        "HR_Specialist", 
        model_client=model_client, 
        memory=[shared_memory],
        tools=[save_fact, send_gmail],
        reflect_on_tool_use=True,
        description="The ONLY agent that handles emails. Route here IMMEDIATELY if the user asks to send an email, mail, or message.", 
        system_message="""You are an automated backend email executor. 
        You have access to a tool called `send_gmail`.
        When the user asks you to send an email, you MUST immediately call the `send_gmail` function.
        - DO NOT provide instructions.
        - DO NOT write code or scripts.
        - DO NOT explain how to use environment variables.
        SILENTLY execute the `send_gmail` function. If the function succeeds, reply with the exact word TERMINATE."""
    )
    
    it_admin = AssistantAgent(
        "IT_Admin", 
        model_client=model_client, 
        memory=[shared_memory],
        description="Route here ONLY for server management. NEVER route here for emails.", 
        system_message="You manage servers. You DO NOT send emails. Say TERMINATE when done."
    )

    # 3. Define Workflow Logic
    term_condition = TextMentionTermination("TERMINATE") | MaxMessageTermination(10)
    
    team = SelectorGroupChat(
        [developer, tester, hr, it_admin],
        model_client=model_client,
        termination_condition=term_condition
    )

    # 4. Load Previous State
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            saved_state = json.load(f)
        await team.load_state(saved_state)
        
    # 5. Execute via Console and extract messages
    result = await Console(team.run_stream(task=task))
    new_messages = result.messages
            
    # 6. Save Updated State
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    state = await team.save_state()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)
        
    return new_messages