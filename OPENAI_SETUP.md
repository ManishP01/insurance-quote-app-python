# 🌍 OpenAI Multilingual Setup Guide

## 🚀 Quick Setup (2 minutes)

### 1. Get OpenAI API Key
1. Go to: https://platform.openai.com/api-keys
2. Sign up/login to OpenAI
3. Click "Create new secret key"
4. Copy your key (starts with `sk-proj-...`)

### 2. Add API Key
1. Create `.env` file in project root:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file:
   ```
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```

### 3. Restart Server
```bash
python3 app.py
```

## ✅ Test Multilingual Features

Try these in the chat:

**Spanish:**
- "¿Qué incluye mi cobertura de responsabilidad civil?"
- "¿Estaré cubierto si un árbol cae en mi casa?"

**French:**
- "Qu'est-ce que ma couverture de responsabilité inclut?"
- "Quand est due ma prochaine facture?"

**Hindi:**
- "मेरा बिल कब देय है?"
- "मेरे देयता कवरेज में क्या शामिल है?"

## 🎯 What You Get

### With OpenAI API Key:
✅ **Multilingual responses** in 10+ languages  
✅ **Enhanced personalization** with AI  
✅ **Better conversation flow**  
✅ **Accurate translations** of insurance terms  

### Without OpenAI API Key:
✅ **English-only AI responses** (still works!)  
✅ **All insurance knowledge** intact  
✅ **Fallback multilingual** for basic queries  

## 💰 Cost

- **GPT-3.5-turbo**: ~$0.002 per chat message
- **Typical usage**: $1-5/month for testing
- **Production**: Scale based on usage

## 🔧 Advanced Configuration

Edit `ai_insurance_bot_openai.py` to:
- Change AI model (GPT-4, etc.)
- Adjust response style
- Add more languages
- Customize translations

**The AI bot works perfectly without OpenAI - multilingual support is just a bonus!** 🚀
