# 🌿 Ritual Reflection Bot

A warm and mindful Telegram bot that guides users through a weekly self-reflection ritual — and offers gentle AI-based support during emotional moments.

> "Everything you feel — matters. Everything you say — stays between us."

---

## ✨ Features

- **/start** — welcome message and cozy main menu
- **/ritual** — step-by-step self-reflection ritual:
  - Body and emotion check-in
  - Identifying active inner voices
  - Choosing a weekly focus
  - Making a promise to oneself
- **/talk** — warm, supportive AI consultation (powered by GPT-4)
- **/cancel** — stop any conversation at any time
- **Auto-save** — reflections stored in `reflections.json`

---

## 🧠 AI Support

The `/talk` feature uses OpenAI GPT-4 with a soft prompt stored in `consultant_prompt.txt`. You can edit this file to tune the tone and personality of the assistant.

Example prompt:
```
You are a caring and warm assistant. Your job is to listen, not judge. Speak with empathy and gentleness. Be a warm blanket in words.
```

---

## 🔧 Installation

1. Clone the repo:
```bash
git clone https://github.com/yourusername/ritual-reflection-bot.git
cd ritual-reflection-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Add your API keys:
- Replace `YOUR_BOT_TOKEN_HERE` in the code with your Telegram bot token
- Replace `YOUR_OPENAI_API_KEY_HERE` with your OpenAI API key

---

## 🧪 Run the bot
```bash
python main.py
```

---

## 📦 Folder structure
```
ritual-reflection-bot/
├── main.py                  # Main bot logic
├── consultant_prompt.txt    # AI behavior template
├── reflections.json         # Stored reflections (auto-generated)
├── .gitignore
└── README.md
```

---

## 💬 Future ideas
- Weekly reminders (via apscheduler)
- Web dashboard to visualize reflections
- Support for anonymous journaling and mood tracking

---

## 🌷 License
MIT — but please use kindly 🌱
