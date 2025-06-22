from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv
from transformers import pipeline
from googleapiclient.discovery import build

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# --- Gemini (Google Generative AI) Setup ---
# Get Gemini API key from environment variable for security
GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-pro')

# Store chat sessions for each user
chat_sessions = {}

# --- Hugging Face Emotion Analysis Setup ---
# Load a pre-trained emotion classification model
emotion_classifier = pipeline(
    'text-classification', 
    model='j-hartmann/emotion-english-distilroberta-base', 
    return_all_scores=True
)

# --- YouTube API Setup ---
YOUTUBE_API_KEY = os.getenv('youtibe_api')
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# List of emotions we care about
EMOTIONS = ['joy', 'sadness', 'anger', 'fear', 'surprise']


def analyze_emotion(text):
    """
    Analyze the emotional content of the text using a Hugging Face model.
    Returns a dictionary with emotion scores (0-10 scale).
    """
    scores = {emotion: 0 for emotion in EMOTIONS}
    try:
        results = emotion_classifier(text)[0]
        for result in results:
            label = result['label'].lower()
            if label in scores:
                # Convert probability to 0-10 scale
                scores[label] = int(result['score'] * 10)
    except Exception as e:
        print(f"Emotion analysis error: {e}")
    return scores


def get_music_recommendations(emotions):
    """
    Recommend music from YouTube based on the user's dominant emotion.
    Returns a list of song titles with YouTube links.
    """
    # Choose the emotion with the highest score
    dominant_emotion, _ = max(emotions.items(), key=lambda x: x[1])
    # Map each emotion to a search query
    emotion_queries = {
        "joy": "happy upbeat music",
        "sadness": "comforting emotional songs",
        "anger": "powerful intense songs",
        "fear": "calming soothing music",
        "surprise": "unique interesting songs"
    }
    query = emotion_queries.get(dominant_emotion, "popular music")
    try:
        search_response = youtube.search().list(
            q=query,
            part="snippet",
            maxResults=3,
            type="video"
        ).execute()
        recommendations = []
        for item in search_response.get('items', []):
            title = item['snippet']['title']
            video_id = item['id']['videoId']
            url = f"https://www.youtube.com/watch?v={video_id}"
            recommendations.append(f"{title} - {url}")
        return recommendations
    except Exception as e:
        print(f"YouTube API error: {e}")
        # Fallback recommendations if YouTube API fails
        return [
            "Ed Sheeran - Perfect",
            "The Weeknd - Blinding Lights",
            "Coldplay - Fix You"
        ]


@app.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint. Handles user messages, analyzes emotion, gets music recommendations,
    and generates a short chatbot reply using Gemini.
    """
    data = request.json
    user_message = data.get('message')
    user_id = data.get('user_id')

    # Start a new chat session for new users
    is_new_user = False
    if user_id not in chat_sessions:
        chat_sessions[user_id] = gemini_model.start_chat(history=[])
        is_new_user = True
    user_chat = chat_sessions[user_id]

    try:
        if is_new_user:
            bot_reply = (
                "Hello and welcome to Emotion Harmony! 😊\n"
                "I'm here to listen, understand your feelings, and recommend music to match your mood. "
                "How are you feeling today?"
            )
        else:
            # Ask Gemini for a short, friendly reply
            short_prompt = "Please answer in 1-2 short sentences. " + user_message
            gemini_response = user_chat.send_message(short_prompt)
            bot_reply = gemini_response.text

        # Analyze the user's emotions
        emotions = analyze_emotion(user_message)

        # Recommend music based on the dominant emotion
        recommendations = get_music_recommendations(emotions)

        # Debug output (optional)
        print("Emotions:", emotions)
        print("Recommendations:", recommendations)

        return jsonify({
            'bot_reply': bot_reply,
            'emotions': emotions,
            'recommendations': recommendations
        })
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'bot_reply': 'I apologize, but I encountered an error. Please try again.',
            'emotions': {emotion: 0 for emotion in EMOTIONS},
            'recommendations': [
                "Ed Sheeran - Perfect",
                "The Weeknd - Blinding Lights",
                "Coldplay - Fix You"
            ]
        })


if __name__ == '__main__':
    # Start the Flask development server
    app.run(debug=True)