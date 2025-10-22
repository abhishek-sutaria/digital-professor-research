# 🚀 Quick Start Guide - AI Avatar with Professor Jenniel

## TL;DR - Get Running in 5 Minutes

Your AI avatar is **ready to go**! Here's the fastest path to see it in action.

---

## ⚡ Super Quick Start

### 1. Install Dependencies (1 minute)

```bash
cd backend
pip install -r requirements.txt
```

### 2. Test the Persona (30 seconds)

```bash
python test_persona.py
```

You should see Professor Jenniel responding to marketing questions!

### 3. Start Backend Server (10 seconds)

```bash
python app.py
```

Keep this terminal running! ✅

### 4. Start Frontend (New Terminal)

```bash
cd frontend
python -m http.server 8000
```

Keep this terminal running too! ✅

### 5. Open in Browser

Go to: **http://localhost:8000**

### 6. Ask a Question!

Try: *"How should we approach our marketing strategy?"*

Wait 30-60 seconds → Watch your avatar respond as Professor Morgan! 🎭

---

## ✅ What's Already Configured

- ✅ **API Keys**: Gemini + HeyGen (in `.env`)
- ✅ **Avatar ID**: Your headshot avatar (848c5c...)
- ✅ **Persona**: Professor Neil A. Morgan's surrogate "Jenniel"
- ✅ **Frontend**: Beautiful UI ready
- ✅ **Backend**: Flask server configured

You don't need to set anything up - **just run it**!

---

## 🎯 Recommended First Questions

Ask Professor Jenniel these to see the persona in action:

1. **"How should we approach our marketing strategy?"**
   - Tests strategic thinking framework

2. **"What metrics should we track for customer satisfaction?"**
   - Tests measurement expertise

3. **"Should we chase market share aggressively?"**
   - Tests consultative questioning & avoiding hype

---

## 📊 What to Expect

### Timeline per Question:
```
┌──────────────────────────────────────┐
│ You ask question           │  < 1s   │
│ Gemini generates response  │  1-3s   │
│ HeyGen creates video       │  30-60s │ ⏳
│ Video plays                │  Auto   │
└──────────────────────────────────────┘

Total: ~35-65 seconds
```

The wait is for video generation - it's worth it! 🎬

---

## 🎓 Understanding Jenniel

**Who is Jenniel?**
- Digital surrogate of Professor Neil A. Morgan
- Marketing strategy expert & consultant
- Published in top journals (JM, SMJ, HBR)
- Fortune 500 consulting experience

**How will Jenniel respond?**
- 📊 Frameworks and numbered steps
- 🎯 Evidence-based recommendations
- 💡 Consultative questions
- 🚀 Focus on value creation
- ❌ Avoids hype and fads

---

## 🛠️ Troubleshooting

### "Backend won't start"
```bash
# Make sure you're in the backend folder
cd backend

# Install dependencies again
pip install -r requirements.txt

# Try running again
python app.py
```

### "Frontend shows errors"
- Make sure backend is running first (Terminal 1)
- Check browser console for errors (F12)
- Verify you're at http://localhost:8000

### "Video generation fails"
- Check HeyGen credit balance
- Verify API keys in `.env`
- Look at backend terminal for error messages

### "Responses don't sound like Professor Morgan"
```bash
# Test the persona
cd backend
python test_persona.py

# Should show marketing-focused responses
# If not, check .env has AVATAR_SYSTEM_PROMPT
```

---

## 📖 Want to Learn More?

- **Full Documentation**: [README.md](README.md)
- **Customization**: [AVATAR_CUSTOMIZATION_GUIDE.md](AVATAR_CUSTOMIZATION_GUIDE.md)
- **Architecture**: [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)
- **Implementation Details**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

---

## 🎨 Customize Your Avatar

### Change Personality

1. Open `.env` file
2. Edit `AVATAR_SYSTEM_PROMPT`
3. Restart backend: `python app.py`
4. Done!

See [AVATAR_CUSTOMIZATION_GUIDE.md](AVATAR_CUSTOMIZATION_GUIDE.md) for examples.

---

## 💡 Pro Tips

### Tip 1: Test Without Videos
```bash
cd backend
python test_persona.py
```
Instant responses - saves time & HeyGen credits!

### Tip 2: Keep Terminals Organized
- Terminal 1: Backend (must run continuously)
- Terminal 2: Frontend (must run continuously)
- Terminal 3: Testing/experiments

### Tip 3: Best Questions for Jenniel
- Ask about **strategy** (her strength)
- Request **frameworks** (she loves those)
- Challenge with **trendy ideas** (she'll push back)
- Ask **diagnostic questions** (watch her question your assumptions)

### Tip 4: Response Length
Current setting: 2-4 sentences (optimal for video)
- Longer = more video generation time
- Shorter = less natural conversation

---

## 🎬 Example Session

```
You: "Should we reorganize our marketing team?"

Jenniel: "Let's start with strategy and capabilities first—structure 
should follow, not lead. What are the critical marketing capabilities 
required to create customer and firm value in your context? Once we've 
identified those, we can design the optimal organizational alignment."

[Video shows your avatar speaking this response professionally]

You: "What metrics should we focus on?"

Jenniel: "Avoid vanity metrics. Focus on measures that link to both 
customer value and firm profitability—things like customer lifetime 
value, advocacy scores, and attribution to revenue growth. Do we have 
evidence these metrics actually predict performance?"

[Another personalized video response]
```

---

## 🎉 You're Ready!

Your AI avatar system is fully configured and ready to use!

Just run:
```bash
# Terminal 1
cd backend && python app.py

# Terminal 2  
cd frontend && python -m http.server 8000

# Browser
http://localhost:8000
```

**Ask your first question and watch Jenniel come to life! 🎭✨**

---

## 🆘 Need Help?

1. Check terminal output for errors
2. Review [README.md](README.md) troubleshooting section
3. Verify `.env` file has all required variables
4. Test with `python test_persona.py`

**Most Common Fix:** Restart both servers! 🔄




