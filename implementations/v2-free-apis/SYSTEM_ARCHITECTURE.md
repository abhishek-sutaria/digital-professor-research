# 🏗️ System Architecture - AI Avatar with Customizable Persona

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                     (Frontend - Browser)                         │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Input Field  │  │ Video Player │  │ Loading State│         │
│  │ "Ask Q"      │  │ (Avatar)     │  │ (Spinner)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP Request
                            │ POST /api/chat
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK API SERVER                            │
│                    (Backend - Python)                            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    app.py                                 │  │
│  │  • Receives user question                                │  │
│  │  • Orchestrates services                                 │  │
│  │  • Returns video URL                                     │  │
│  └───────┬──────────────────────────────┬───────────────────┘  │
│          │                               │                       │
│          ▼                               ▼                       │
│  ┌──────────────────┐          ┌──────────────────┐           │
│  │ gemini_service.py│          │ heygen_service.py│           │
│  │                  │          │                  │           │
│  │ • Loads persona  │          │ • Uses avatar ID │           │
│  │ • Calls Gemini   │          │ • Creates video  │           │
│  │ • Returns text   │          │ • Polls status   │           │
│  └────────┬─────────┘          └────────┬─────────┘           │
└───────────┼──────────────────────────────┼─────────────────────┘
            │                              │
            │ .env Configuration           │
            ▼                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CONFIGURATION (.env)                         │
│                                                                   │
│  GEMINI_API_KEY          = "AIza..."                            │
│  HEYGEN_API_KEY          = "sk_V2..."                           │
│  HEYGEN_AVATAR_ID        = "848c..."                            │
│  AVATAR_SYSTEM_PROMPT    = "You are Professor..."   ⭐ NEW!    │
└─────────────┬───────────────────────────────┬───────────────────┘
              │                               │
              ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│    GEMINI API            │    │    HEYGEN API            │
│  (Google AI Studio)      │    │  (Avatar Videos)         │
│                          │    │                          │
│  • Generates smart       │    │  • Creates talking       │
│    responses             │    │    avatar videos         │
│  • Uses persona prompt   │    │  • Uses your headshot    │
└──────────────────────────┘    └──────────────────────────┘
```

---

## Detailed Flow: User Question → Avatar Response

### Step-by-Step Process

```
1. USER ASKS QUESTION
   │
   └─→ "How should we approach our marketing strategy?"
       │
       ▼

2. FRONTEND (script.js)
   │
   ├─→ Captures user input
   ├─→ Shows loading state (spinner)
   └─→ Sends POST request to backend
       │
       │ HTTP POST /api/chat
       │ Body: { "message": "How should we..." }
       │
       ▼

3. BACKEND API (app.py)
   │
   ├─→ Receives request
   ├─→ Extracts user message
   └─→ Calls Gemini Service
       │
       ▼

4. GEMINI SERVICE (gemini_service.py)
   │
   ├─→ Loads AVATAR_SYSTEM_PROMPT from .env  ⭐ NEW!
   │   │
   │   └─→ "You are Professor Neil A. Morgan's digital surrogate Jenniel..."
   │
   ├─→ Combines prompt + user question
   │   │
   │   └─→ Full Prompt:
   │       "You are Professor Jenniel... [persona details]
   │        User: How should we approach our marketing strategy?
   │        Assistant:"
   │
   ├─→ Calls Gemini API
   │
   └─→ Receives AI response
       │
       └─→ "Let's start with strategy first. Do we really understand 
            why customers choose us? I recommend a three-step framework..."
       │
       ▼

5. BACKEND API (app.py)
   │
   ├─→ Receives Gemini's text response
   └─→ Calls HeyGen Service
       │
       ▼

6. HEYGEN SERVICE (heygen_service.py)
   │
   ├─→ Submits video generation request:
   │   • Avatar ID: 848c5c2a2edb488589e5d31c693bfed4
   │   • Text: [Gemini's response]
   │   • Voice ID: 2d5b0e6cf36f460aa7fc47e3eee4ba54
   │
   ├─→ Receives video ID
   │
   ├─→ Polls for completion (30-60 seconds)
   │   │
   │   └─→ Status check every 5 seconds
   │
   └─→ Video ready! Returns URL
       │
       └─→ "https://heygen.com/video/abc123.mp4"
       │
       ▼

7. BACKEND API (app.py)
   │
   └─→ Returns response to frontend:
       {
         "success": true,
         "ai_response": "Let's start with strategy...",
         "video_url": "https://heygen.com/video/abc123.mp4",
         "video_id": "abc123"
       }
       │
       ▼

8. FRONTEND (script.js)
   │
   ├─→ Receives response
   ├─→ Hides loading state
   ├─→ Sets video player source to video_url
   ├─→ Displays text response
   └─→ Auto-plays video
       │
       ▼

9. USER SEES AVATAR
   │
   └─→ Video of their headshot avatar speaking Jenniel's response!
```

---

## Persona Customization Architecture ⭐ NEW!

### How the Prompt System Works

```
┌─────────────────────────────────────────────────────────────┐
│                    .env FILE                                 │
│                                                               │
│  AVATAR_SYSTEM_PROMPT = "You are Professor Jenniel..."      │
│                                                               │
│  Contains:                                                   │
│  • Identity (Who is the avatar?)                            │
│  • Expertise (What do they know?)                           │
│  • Voice/Tone (How do they speak?)                          │
│  • Vocabulary (Signature words)                             │
│  • Behavior Rules (Always/Never)                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Loaded on startup
                         ▼
┌─────────────────────────────────────────────────────────────┐
│             GEMINI SERVICE (gemini_service.py)               │
│                                                               │
│  def __init__(self):                                        │
│      self.system_prompt = os.getenv('AVATAR_SYSTEM_PROMPT') │
│                                                               │
│  def get_response(self, user_message):                      │
│      full_prompt = f"{self.system_prompt}\n\n              │
│                      User: {user_message}\n                 │
│                      Assistant:"                            │
│      response = gemini.generate_content(full_prompt)        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Every request uses this
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    GEMINI API                                │
│                                                               │
│  Processes:                                                  │
│  1. System prompt (defines persona)                         │
│  2. User message (the question)                             │
│  3. Generates response IN CHARACTER                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
                 Response as Jenniel!
```

### Why This Design?

✅ **Separation of Concerns**
- Configuration (.env) ≠ Code (gemini_service.py)
- Change personality without touching Python files

✅ **Easy Customization**
- Edit one variable
- Restart server
- New persona active

✅ **Maintainable**
- Persona logic separate from API calls
- Clear fallback if not configured

✅ **Testable**
- `test_persona.py` verifies without videos
- Quick iteration on personality

---

## Component Responsibilities

### Frontend (`frontend/`)

**index.html**
- UI structure
- Input form
- Video player
- Loading states

**style.css**
- Modern, responsive design
- Animations and transitions
- Mobile-friendly layout

**script.js**
- Capture user input
- Call backend API
- Manage UI states (loading, video, error)
- Auto-play avatar video

### Backend (`backend/`)

**app.py** (Flask Server)
- Main API endpoint: `/api/chat`
- Orchestrates Gemini + HeyGen
- Error handling
- Health checks

**gemini_service.py** ⭐ MODIFIED
- Loads `AVATAR_SYSTEM_PROMPT` from .env
- Calls Gemini API
- Returns AI text response
- Maintains conversation history

**heygen_service.py**
- Creates video generation request
- Polls for video completion
- Returns video URL
- Uses avatar ID from .env

**test_persona.py** ⭐ NEW
- Quick persona testing
- No video generation
- Checks vocabulary alignment
- Development tool

### Configuration

**.env** ⭐ MODIFIED
- API keys (Gemini, HeyGen)
- Avatar ID
- **Avatar system prompt** (NEW!)

**.gitignore**
- Protects .env from git
- Python cache files
- IDE settings

---

## Data Flow Example

### Input → Output Journey

```
USER INPUT:
"Should we chase market share?"

↓ [Frontend captures]

HTTP REQUEST:
POST /api/chat
{ "message": "Should we chase market share?" }

↓ [Backend receives]

GEMINI PROMPT:
"You are Professor Jenniel... [full persona]

User: Should we chase market share?
Assistant:"

↓ [Gemini processes with persona]

GEMINI RESPONSE:
"Market share without profit logic rarely creates sustainable value. 
Instead, focus on building differentiated capabilities that drive 
customer choice and firm profitability."

↓ [HeyGen creates video]

HEYGEN REQUEST:
{
  "avatar_id": "848c5c2a2edb488589e5d31c693bfed4",
  "text": "Market share without profit logic...",
  "voice_id": "2d5b0e6cf36f460aa7fc47e3eee4ba54"
}

↓ [Video generated: 30-60 sec]

VIDEO URL:
"https://heygen.com/video/abc123.mp4"

↓ [Frontend receives]

USER SEES:
Video of their avatar speaking as Professor Morgan!
```

---

## Technology Stack

### Frontend
- **HTML5**: Structure
- **CSS3**: Styling, animations
- **Vanilla JavaScript**: Logic, API calls
- **Fetch API**: HTTP requests

### Backend
- **Python 3.8+**: Core language
- **Flask**: Web framework
- **python-dotenv**: Environment variables
- **google-generativeai**: Gemini SDK
- **requests**: HTTP client

### APIs
- **Google Gemini**: AI responses
- **HeyGen**: Avatar video generation

### Configuration
- **Environment Variables**: Secure config
- **dotenv**: .env file loading

---

## Security Architecture

```
┌──────────────────────────────────────┐
│         SECURITY LAYERS               │
└──────────────────────────────────────┘

1. API KEYS
   │
   ├─→ Stored in .env (not in code)
   ├─→ .gitignore prevents git commits
   └─→ Never exposed to frontend

2. CORS
   │
   └─→ Flask-CORS allows frontend calls
       (configured for localhost)

3. INPUT VALIDATION
   │
   ├─→ Backend checks for empty messages
   └─→ Error handling for malformed requests

4. RATE LIMITING
   │
   └─→ Gemini: 60 req/min
       HeyGen: Free tier limits
```

---

## Performance Characteristics

### Timing Breakdown

```
Total Response Time: ~35-65 seconds

┌─────────────────────────────────────┐
│ 1. User Input → Backend              │  < 1 second
├─────────────────────────────────────┤
│ 2. Gemini AI Response                │  1-3 seconds
├─────────────────────────────────────┤
│ 3. HeyGen Video Submission           │  < 1 second
├─────────────────────────────────────┤
│ 4. HeyGen Video Generation           │  30-60 seconds ⏳
│    (polling every 5 seconds)         │
├─────────────────────────────────────┤
│ 5. Video Playback Starts             │  < 1 second
└─────────────────────────────────────┘
```

### Bottleneck: Video Generation
- HeyGen processes video rendering
- Cannot be optimized (external API)
- Trade-off for realistic avatar quality

### Optimizations Possible:
- Cache common responses
- Pre-generate FAQs
- Add audio-only mode for instant feedback

---

## Scalability Considerations

### Current Setup (Prototype)
- ✅ Perfect for demos
- ✅ Low infrastructure cost
- ✅ Easy to deploy
- ⚠️ Sequential processing
- ⚠️ Limited by API rate limits

### Production Enhancements:
- Add request queue
- Implement caching layer
- Use async processing
- Add load balancing
- WebSocket for real-time updates

---

This architecture provides a solid foundation for an interactive AI avatar system with easy persona customization! 🎭




