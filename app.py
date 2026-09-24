import streamlit as st
import asyncio
import os
from core.office_agents import execute_team_task

# ---------------------------------------------------------
# 1. Page Configuration & Custom CSS (Theme Responsive)
# ---------------------------------------------------------
st.set_page_config(page_title="AutoGen IT Workspace", page_icon="🏢", layout="wide")

st.markdown("""
<style>
    /* Hide Streamlit Branding for a clean, professional look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Theme-responsive Agent Name Highlighting */
    .agent-name { 
        font-weight: 700; 
        font-size: 1.15em; 
        margin-bottom: 5px;
        color: var(--text-color);
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. UI Layout: Header & Sidebar
# ---------------------------------------------------------
col1, col2 = st.columns([1, 6])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/906/906324.png", width=70) # Placeholder building icon
with col2:
    st.title("AutoGen IT Workspace")
    st.caption("🚀 Interactive AI Office: HR, Developer, Tester, and IT Admin")

with st.sidebar:
    st.header("⚙️ Workspace Controls")
    st.markdown("Manage your agent environment and memory states below.")
    
    # Sleek button to wipe short-term memory
    if st.button("🧹 Clear Conversation State", use_container_width=True, type="primary"):
        if os.path.exists("workspace/team_state.json"):
            os.remove("workspace/team_state.json")
        st.session_state.messages = []
        st.success("Agent memory cleared! Ready for a fresh task.")
        st.rerun()
        
    st.divider()
    
    st.subheader("👥 Active Team Members")
    st.info("**👩‍💼 HR_Specialist**\n\nHandles client communications, memory logging, and sends emails.")
    st.success("**👨‍💻 Software_Developer**\n\nWrites and refactors Python code.")
    st.warning("**🕵️‍♂️ Testing_Engineer**\n\nReviews code and performs QA testing.")
    st.error("**🛠️ IT_Admin**\n\nManages infrastructure and deployment servers.")

# ---------------------------------------------------------
# 3. Session State Initialization
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Map agents to specific visual avatars
def get_avatar(sender):
    avatars = {
        "User": "👤",
        "HR_Specialist": "👩‍💼",
        "Software_Developer": "👨‍💻",
        "Testing_Engineer": "🕵️‍♂️",
        "IT_Admin": "🛠️",
        "System": "⚙️"
    }
    return avatars.get(sender, "🤖")

# ---------------------------------------------------------
# 4. Render Chat History
# ---------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["sender"], avatar=get_avatar(msg["sender"])):
        st.markdown(f"<div class='agent-name'>{msg['sender']}</div>", unsafe_allow_html=True)
        st.write(msg["content"])

# ---------------------------------------------------------
# 5. Chat Input & Async Execution
# ---------------------------------------------------------
if prompt := st.chat_input("Assign a task (e.g., 'HR, send a test email stating our sprint is complete...')"):
    
    # Render user prompt immediately
    st.session_state.messages.append({"sender": "User", "content": prompt})
    with st.chat_message("User", avatar=get_avatar("User")):
        st.markdown("<div class='agent-name'>User</div>", unsafe_allow_html=True)
        st.write(prompt)
        
    # Execute workflow with a visual spinner
    with st.spinner("🔄 The team is coordinating..."):
        try:
            # Run the AutoGen workflow
            new_messages = asyncio.run(execute_team_task(prompt))
            
            # Parse and render the responses
            for msg in new_messages:
                sender = getattr(msg, 'source', 'System')
                msg_type = str(type(msg))
                raw_msg_str = str(msg)
                
                # 1. Hide duplicated user prompts
                if sender.lower() == "user":
                    continue
                
                # 2. Capture Tool Result directly from the full raw string
                if "ToolCallExecutionEvent" in msg_type:
                    if "SUCCESS" in raw_msg_str:
                        clean_content = "✅ **Task Complete:** The email has been sent successfully!"
                        st.session_state.messages.append({"sender": sender, "content": clean_content})
                        with st.chat_message(sender, avatar=get_avatar(sender)):
                            st.markdown(f"<div class='agent-name'>{sender}</div>", unsafe_allow_html=True)
                            st.write(clean_content)
                    elif "ERROR" in raw_msg_str:
                        clean_content = "❌ **Error:** The tool encountered an issue."
                        st.session_state.messages.append({"sender": sender, "content": clean_content})
                        with st.chat_message(sender, avatar=get_avatar(sender)):
                            st.markdown(f"<div class='agent-name'>{sender}</div>", unsafe_allow_html=True)
                            st.write(clean_content)
                    continue
                    
                # 3. Hide memory queries and system logs (only keep TextMessages)
                if "TextMessage" not in msg_type:
                    continue
                
                # 4. Clean up standard text messages and filter out 'TERMINATE'
                content = getattr(msg, 'content', "")
                clean_text = str(content).replace("TERMINATE", "").strip()
                
                # Only print if there is actual conversation left
                if clean_text: 
                    st.session_state.messages.append({"sender": sender, "content": clean_text})
                    with st.chat_message(sender, avatar=get_avatar(sender)):
                        st.markdown(f"<div class='agent-name'>{sender}</div>", unsafe_allow_html=True)
                        st.write(clean_text)
                        
        except Exception as e:
            st.error(f"Workflow encountered an error: {e}")