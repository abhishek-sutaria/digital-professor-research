# 🎭 Interactive AI Avatar

An interactive AI avatar application that combines your custom headshot with Gemini AI and HeyGen to create personalized video responses to user questions.

## 🌟 Features

- **Custom Avatar**: Uses your personal headshot to create a realistic talking avatar
- **AI-Powered Responses**: Leverages Gemini AI for intelligent, context-aware answers
- **Video Generation**: HeyGen creates professional avatar videos speaking the responses
- **Voice Input**: 🎤 Press-and-hold microphone button to speak your questions (Web Speech API)
- **Text Input**: Traditional typing interface as fallback
- **Beautiful UI**: Modern, responsive web interface
- **Real-time Interaction**: Ask questions and get personalized video responses
- **Mobile Support**: Works on both desktop and mobile devices

## 🏗️ Architecture

```
User Question → Gemini AI (generates response) → HeyGen (creates avatar video) → Video Display
```

### Tech Stack
- **Backend**: Python + Flask
- **AI**: Google Gemini API
- **Avatar**: HeyGen API
- **Frontend**: HTML, CSS, JavaScript

## 📁 Project Structure

```
.
├── backend/
│   ├── app.py              # Flask server (main API)
│   ├── gemini_service.py   # Gemini AI integration
│   ├── heygen_service.py   # HeyGen video generation
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Main UI
│   ├── style.css           # Styling
│   └── script.js           # Frontend logic
├── .env                    # API credentials (DO NOT COMMIT!)
├── .gitignore             # Git ignore file
└── README.md              # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- A modern web browser
- Internet connection (for API calls)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd "/Users/abhisheksutaria/Cursor Projects/Digital Professor/Digital Professor - Free APIs"
   ```

2. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### Running the Application

#### Step 1: Start the Backend Server

```bash
cd backend
python app.py
```

You should see:
```
🎭 AI AVATAR SERVER
Server running at: http://localhost:5000
```

Keep this terminal running!

#### Step 2: Open the Frontend

1. Open a new terminal window
2. Navigate to the frontend folder:
   ```bash
   cd frontend
   ```
3. Start a simple HTTP server:
   
   **Option A - Python:**
   ```bash
   python -m http.server 8000
   ```
   
   **Option B - Node.js (if you have it):**
   ```bash
   npx http-server -p 8000
   ```

4. Open your browser and go to: **http://localhost:8000**

### Using the Application

#### Option 1: Voice Input (Recommended) 🎤
1. **Press and hold** the green microphone button
2. **Speak** your question clearly (e.g., "What is marketing strategy?")
3. **Release** the button when done speaking
4. The speech is automatically converted to text and sent
5. Wait 30-60 seconds for your video response

#### Option 2: Text Input ⌨️
1. Type a question in the input field
2. Click "Ask" or press Enter
3. Wait 30-60 seconds while:
   - Gemini generates an intelligent response
   - HeyGen creates a video of your avatar speaking
4. Watch your avatar respond with a personalized video!

**Note**: Voice input works best in Chrome/Edge browsers. See [VOICE_INPUT_GUIDE.md](VOICE_INPUT_GUIDE.md) for details.

## 🔑 API Keys Configuration

Your API keys are stored in `.env` file:

```env
GEMINI_API_KEY=AIzaSyDOa7PR3DaSQdI2nLiEgBVibiOYzV-6vzk
HEYGEN_API_KEY=sk_V2_hgu_kpCRYiLF6YB_RYtu193Qy2pMSfBHcDq5RiBKNmzxn1Mx
HEYGEN_AVATAR_ID=848c5c2a2edb488589e5d31c693bfed4
```

⚠️ **Security Note**: Never commit `.env` to git! It's already in `.gitignore`.

## 🎭 Avatar Personality Configuration

### Customizable System Prompt

Your avatar's personality, expertise, and behavior are controlled by the `AVATAR_SYSTEM_PROMPT` variable in `.env`.

**Current Persona: Professor Neil A. Morgan's Digital Surrogate "Jenniel"**

Jenniel is configured as:
- **Expert in**: Marketing strategy, brand management, organizational alignment
- **Voice**: Professional, structured, evidence-driven
- **Style**: Frameworks, numbered steps, consultative questioning
- **Behavior**: Strategy-first approach, value creation focus, avoids hype

### How to Change Avatar Personality

Simply edit the `AVATAR_SYSTEM_PROMPT` in your `.env` file:

```env
AVATAR_SYSTEM_PROMPT="Your custom persona description here..."
```

**Example Personas You Could Create:**
- Tech startup advisor
- Career coach
- Financial consultant
- Customer support specialist
- Educational tutor in any subject

The avatar will adopt whatever personality and expertise you define!

📖 **See detailed guide:** [AVATAR_CUSTOMIZATION_GUIDE.md](AVATAR_CUSTOMIZATION_GUIDE.md)

### Quick Test Your Persona

Want to test if Jenniel is responding correctly without generating videos?

```bash
cd backend
python test_persona.py
```

This will ask Professor Morgan-style questions and show the responses instantly.

## 🎨 Customization

### Change Avatar Voice

Edit `backend/heygen_service.py`, line 80:
```python
"voice_id": "2d5b0e6cf36f460aa7fc47e3eee4ba54",  # Change this
```

Find other voice IDs at: https://docs.heygen.com/reference/list-voices-v2

### Adjust AI Personality

**Easy Way (Recommended):** Edit the `AVATAR_SYSTEM_PROMPT` in `.env` file:
```env
AVATAR_SYSTEM_PROMPT="Your custom personality and behavior instructions..."
```

**Advanced Way:** The system prompt is loaded in `backend/gemini_service.py` from the environment variable. If not set, it uses a default friendly assistant persona.

### Change Video Background

Edit `backend/heygen_service.py`, line 99:
```python
"value": "#FFFFFF"  # Change color (hex code)
```

## 📊 API Endpoints

### Backend API

- `GET /api/health` - Check if server is running
- `POST /api/chat` - Send a message and get avatar response
  ```json
  Request: { "message": "Your question here" }
  Response: {
    "success": true,
    "ai_response": "Text response",
    "video_url": "https://...",
    "video_id": "abc123"
  }
  ```
- `POST /api/clear-history` - Clear conversation history

## ⏱️ Performance Notes

- **Gemini Response**: ~1-3 seconds
- **HeyGen Video Generation**: ~30-60 seconds
- **Total Time per Question**: ~30-60 seconds

### Free Tier Limitations

- **Gemini**: 60 requests/minute, 1500 requests/day
- **HeyGen**: Limited monthly credits (check your dashboard)

## 🐛 Troubleshooting

### Backend won't start
- Check if Python is installed: `python --version`
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify `.env` file exists with all API keys

### Frontend can't connect to backend
- Make sure backend is running on port 5000
- Check browser console for CORS errors
- Verify `API_BASE_URL` in `script.js` is correct

### Video generation fails
- Check HeyGen API key is valid
- Verify avatar ID is correct
- Check HeyGen credit balance in dashboard
- Look at backend terminal for error messages

### "API error" messages
- Gemini: Check API key is valid and has quota
- HeyGen: Verify API key and avatar ID
- Check internet connection

## 🔧 Development

### Testing Individual Components

**Test Gemini Service:**
```bash
cd backend
python gemini_service.py
```

**Test HeyGen Service:**
```bash
cd backend
python heygen_service.py
```

### Adding Features

Some ideas for enhancements:
- Add conversation history display
- Implement voice input (speech-to-text)
- Add multiple avatar support
- Save favorite responses
- Add video download button

## 📝 License

This is a prototype project for educational purposes.

## 🙏 Credits

- **AI**: Google Gemini
- **Avatar Technology**: HeyGen
- **Created by**: Your Name

## 📧 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review backend terminal logs
3. Check browser console for errors
4. Verify API keys are valid

---

**Enjoy your AI Avatar! 🎭✨**

