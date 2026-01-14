import os
import random
import logging
import json
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from livekit import api
from werkzeug.utils import secure_filename
from pptx import Presentation  # Ensure python-pptx is installed

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ppt-server')

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- 1. PPT PROCESSOR (Moved here to avoid import errors) ---
def ppt_to_json(ppt_path, json_path="presentation.json"):
    try:
        if not os.path.exists(ppt_path):
            return {}

        prs = Presentation(ppt_path)
        data = []

        for i, slide in enumerate(prs.slides, start=1):
            slide_content = f"Slide {i}: "
            
            # Extract text
            texts = []
            for shape in slide.shapes:
                if shape.has_text_frame:
                    text = shape.text.strip()
                    if text:
                        texts.append(text)
            
            if texts:
                slide_content += " ".join(texts)
                data.append(slide_content)

        # Save to root directory so Agent can find it
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return data

    except Exception as e:
        logger.error(f"Error converting PPT: {e}")
        return []

# --- 2. ROUTES ---
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/upload-ppt', methods=['POST'])
def upload_ppt():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.endswith('.pptx'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Call the local function
        data = ppt_to_json(filepath, "presentation.json")
        
        return jsonify({
            "status": "success", 
            "message": "Presentation processed",
            "slide_count": len(data)
        })
    
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/api/connection-details')
def connection_details():
    try:
        LIVEKIT_URL = os.getenv('LIVEKIT_URL')
        API_KEY = os.getenv('LIVEKIT_API_KEY')
        API_SECRET = os.getenv('LIVEKIT_API_SECRET')

        if not all([LIVEKIT_URL, API_KEY, API_SECRET]):
            return jsonify({"error": "Missing Keys"}), 500

        room_name = f"ppt_session_{random.randint(10000, 99999)}"
        participant_identity = f"user_{random.randint(1000, 9999)}"
        
        token = api.AccessToken(API_KEY, API_SECRET) \
            .with_identity(participant_identity) \
            .with_name("User") \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            )).to_jwt()

        return jsonify({
            "serverUrl": LIVEKIT_URL,
            "roomName": room_name,
            "participantToken": token
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def start_server():
    from waitress import serve
    print("🟢 Web Server running on http://localhost:8000")
    serve(app, host='0.0.0.0', port=8000, threads=4)

if __name__ == '__main__':
    start_server()