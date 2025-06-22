# Emotion Harmony Companion

A web app that analyzes your emotions using a Hugging Face model, chats with you using Gemini, and recommends music from YouTube based on your mood.

## Features
- Emotion analysis using Hugging Face Transformers
- Chatbot powered by Gemini (Google Generative AI)
- Music recommendations using YouTube API
- Modern web UI

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 2. Create and activate a virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root directory with the following content:

```
GOOGLE_API_KEY=your_gemini_api_key
youtibe_api=your_youtube_api_key
```

- Replace `your_gemini_api_key` with your Gemini API key.
- Replace `your_youtube_api_key` with your YouTube Data API v3 key.

### 5. Run the Flask app
```bash
python app.py
```

The backend will start at `http://localhost:5000`.

### 6. Open the Frontend
Open `ai_friend.html` in your browser. (You may want to serve it with a simple HTTP server for CORS.)

## Notes
- **Never commit your `.env` file or API keys to GitHub.**
- If you want to deploy, consider using environment variables on your server.

## License
MIT 