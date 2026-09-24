# 🏢 AutoGen IT Workspace

An interactive multi-agent IT workspace built with **Streamlit** and **Microsoft AutoGen**.

The application provides a user-friendly interface for interacting with a specialized team of AI agents that can handle software development, testing, infrastructure tasks, HR communication, and automated email operations through the Gmail API.

## ✨ Features

### 🤖 Multi-Agent Team

The workspace includes four specialized AI agents:

- 👩‍💼 **HR_Specialist** — Handles communications, client interactions, and automated email operations.
- 👨‍💻 **Software_Developer** — Writes, refactors, and designs Python code.
- 🕵️‍♂️ **Testing_Engineer** — Reviews code, performs QA checks, and validates implementation quality.
- 🛠️ **IT_Admin** — Handles infrastructure and deployment-related tasks.

The agents collaborate to complete tasks based on the user's request.

### 📧 Gmail API Integration

The application integrates with the **Gmail API** to send emails through Google OAuth 2.0 authentication.

The first time email functionality is used, Google authentication is performed and the authentication token is stored locally for future sessions.

### 🖥️ Streamlit UI

The application provides:

- Interactive chat interface
- Agent-specific avatars
- Dark/light mode compatibility
- Clean agent communication display
- Backend log filtering
- Conversation state management

### 🧠 Conversation Memory

The application maintains the team's conversation state using AutoGen.

A **Clear Conversation State** button allows users to reset the current agent conversation before starting a new task.

---

## 🛠️ Tech Stack

- **Language:** Python
- **Frontend:** Streamlit
- **Multi-Agent Framework:** Microsoft AutoGen
- **Async Processing:** Asyncio
- **Authentication:** Google OAuth 2.0
- **Email Integration:** Gmail API
- **Google Integration:** Google API Python Client
- **LLM:** OpenAI

---

## 📋 Prerequisites

Before running the application, configure a Google Cloud project with Gmail API access.

### 1. Enable Gmail API

Open the Google Cloud Console:

https://console.cloud.google.com/

Then:

1. Create or select a Google Cloud project.
2. Go to **APIs & Services → Library**.
3. Search for **Gmail API**.
4. Click **Enable**.

### 2. Configure OAuth Consent Screen

Go to:

**APIs & Services → OAuth consent screen**

Configure the application and add the Gmail account you want to use under **Test users**.

### 3. Create OAuth Credentials

Go to:

**APIs & Services → Credentials**

Create:

**OAuth Client ID → Desktop App**

Download or copy the Client ID and Client Secret.

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-repo-directory>
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here

GMAIL_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your_google_client_secret
```

Do not commit `.env` to GitHub.

### 4. Create the workspace directory

Create a folder named:

```text
workspace/
```

The application uses this directory to store local application state:

```text
workspace/
├── token.json
└── team_state.json
```

These files are generated automatically when the application runs.

---

## 💻 Running the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will normally be available at:

```text
http://localhost:8501
```

---

## 🔐 First-Time Gmail Authentication

When the HR agent sends an email for the first time:

1. A browser window opens for Google authentication.
2. Sign in with the Google account configured as a test user.
3. Grant the requested permissions.
4. Google authentication information is stored in:

```text
workspace/token.json
```

Future sessions can reuse the stored authentication token.

---

## 🧠 Managing Conversation Memory

The application stores the team's conversation state in:

```text
workspace/team_state.json
```

After a task is completed, use:

**🧹 Clear Conversation State**

from the Streamlit sidebar before starting a completely new task.

This resets the current AutoGen conversation state.

---

## 📁 Project Structure

```text
AutoGen-IT-Workspace/
│
├── app.py
│
├── core/
│   └── office_agents.py
│
├── workspace/
│   ├── token.json
│   └── team_state.json
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

### File Description

| File / Folder               | Purpose                                         |
| --------------------------- | ----------------------------------------------- |
| `app.py`                    | Streamlit application and UI                    |
| `core/office_agents.py`     | AutoGen agent definitions and Gmail integration |
| `workspace/token.json`      | Google OAuth authentication token               |
| `workspace/team_state.json` | AutoGen conversation state                      |
| `requirements.txt`          | Python dependencies                             |
| `.env`                      | API keys and Google credentials                 |
| `.gitignore`                | Files excluded from Git                         |
| `README.md`                 | Project documentation                           |

---

## 🔒 Security

Never commit sensitive credentials or authentication files.

Recommended `.gitignore`:

```gitignore
.env
workspace/token.json
workspace/team_state.json
__pycache__/
*.pyc
```

Keep your:

- OpenAI API key
- Google Client Secret
- OAuth token

private.

---

## 🔄 Application Flow

```text
                    User
                     ↓
              Streamlit UI
                     ↓
              AutoGen Team
                     ↓
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
     HR Agent    Developer     IT Admin
                     ↓
              Testing Engineer
                     ↓
              Task Completion
                     ↓
               Final Response
```

For email-related tasks:

```text
User Request
     ↓
HR Specialist
     ↓
Gmail API
     ↓
Google OAuth
     ↓
Email Sent
```

---

## 🎯 Project Goal

This project demonstrates how **multi-agent AI systems** can coordinate specialized agents to perform different IT and business tasks through a single conversational interface.

It also demonstrates integration between **AutoGen, Streamlit, OpenAI, and external APIs such as Gmail**.
