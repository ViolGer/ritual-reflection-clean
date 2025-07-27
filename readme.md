# 🌿 Ritual Reflection Bot

A gentle Telegram bot for mindful evening self-reflection, with AI support via OpenAI.  
It helps users reconnect with themselves, track patterns, and stay emotionally aware.

---

## ✨ Features

  Step-by-step evening reflection ritual:
- Body check-in, inner voices, focus, intention
- Conversation with a compassionate AI consultant
- History of your responses with GPT-based insights
- Daily reminders at 20:00 if no session was completed
- Custom responses supported at every stage

---

## 🚀 Installation

1. Clone the repository:

`bash
git clone https://github.com/ViolGer/ritual-reflection-clean.git
cd ritual-reflection-clean

2. Install dependencies:

pip install -r requirements.txt

3. Create a .env file in the root directory with your keys:

TELEGRAM_TOKEN=your_telegram_token
OPENAI_KEY=your_openai_api_key

> ❗️ Make sure .env is included in .gitignore to avoid committing sensitive data.

---

▶️ Running the Bot

python main.py

Once started, the bot will respond to messages in Telegram.
Reminders are automatically scheduled for 20:00 each day.

---

📁 Project Structure

main.py — core bot logic

reflections.json — stores user reflection history

consultant_prompt.txt — system prompt for AI consultant

.env — tokens and keys (not committed)

---

🔐 Security

Tokens and secrets are stored in .env, excluded via .gitignore

Commit history is cleaned from sensitive content

Never push API keys to the repository

---

💡 Planned Features

Voice and photo support

Customizable reminders

Sync with cloud or Google Sheets

Multilingual interface

☁️
