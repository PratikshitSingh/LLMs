# 🧠 Natural Language Terminal Assistant (Offline, Local LLM)

Interact with your terminal using natural language, powered by **local LLMs** running via [Ollama](https://ollama.com). No API keys, no internet, full privacy.

---

## ✅ Features

- Converts natural language into shell commands
- Runs fully offline using `ollama`
- Uses open-source models like `mistral` or `codellama`
- Lets you approve before executing generated commands

---

## 🚀 Setup Instructions

### 1. Install Ollama

#### macOS
```bash
brew install ollama
```

Linux
```
curl -fsSL https://ollama.com/install.sh | sh
```

After installation, restart your terminal or run source ~/.bashrc or source ~/.zshrc.

### 2. Pull a Local LLM

We recommend mistral for general reasoning or codellama for shell/code tasks:
```
ollama pull mistral
```
or
```
ollama pull codellama
```

### 3. Create the Natural Language to Shell Script

Create a file named nltosh.sh:
```
touch ~/nltosh.sh
chmod +x ~/nltosh.sh
nano ~/nltosh.sh
```

Paste the following code:
```
#!/bin/bash

prompt="Convert this natural language instruction into a Unix shell command:\n\n$@\n\nOnly output the command. No explanation."

response=$(echo -e "$prompt" | ollama run mistral)

echo -e "\n🤖 Suggested Command:\n$response"
echo -e "\nDo you want to run it? [y/N]"
read -r confirm

if [[ "$confirm" =~ ^[Yy]$ ]]; then
  eval "$response"
else
  echo "Cancelled."
fi
```

#### Make it globally accessible (optional):
```
sudo mv ~/nltosh.sh /usr/local/bin/nltosh
```

### 🧪 Usage
```
nltosh "list all files modified in the last 2 days"
nltosh "find and delete all .DS_Store files"
nltosh "show me top 10 processes using most CPU"
```
The assistant will respond with a command and ask you to confirm before executing it.

  

### 🔐 Why Use This?
✅ Runs Locally – No cloud or OpenAI API key needed

✅ Privacy First – Your queries never leave your machine

✅ Lightweight – Uses efficient models like Mistral or CodeLlama

✅ Customizable – Fully scriptable and open


### 📌 Tips
You can swap out mistral with codellama or any Ollama-supported model

Add logging or fuzzy search (fzf) to build a more advanced shell helper

Extend to support aliases or safety warnings for destructive commands
