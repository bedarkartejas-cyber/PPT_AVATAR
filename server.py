import os
import logging
import json
import subprocess
import threading
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from livekit import api
from werkzeug.utils import secure_filename
from pptx import Presentation
from pdf2image import convert_from_path

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ppt-server')

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Folders for storage
UPLOAD_FOLDER = 'uploads'
SLIDES_FOLDER = 'slides'  
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SLIDES_FOLDER, exist_ok=True)

def process_ppt(ppt_path):
    slides_data = []
    
    try:
        abs_ppt_path = os.path.abspath(ppt_path)
        abs_slides_folder = os.path.abspath(SLIDES_FOLDER)
        
        # 1. Clear old slides
        for f in os.listdir(abs_slides_folder):
            file_path = os.path.join(abs_slides_folder, f)
            if os.path.isfile(file_path):
                os.remove(file_path)

        print(f"⏳ Converting PPT to PDF (Linux Mode)...")
        
        # Use LibreOffice to convert PPTX -> PDF
        # This works on AWS/Linux without a GUI
        cmd = [
            "libreoffice", "--headless", "--invisible", "--nodefault", "--nofirststartwizard",
            "--convert-to", "pdf",
            "--outdir", abs_slides_folder,
            abs_ppt_path
        ]
        
        subprocess.run(cmd, check=True)
        
        # Get the generated PDF path
        base_name = os.path.splitext(os.path.basename(ppt_path))[0]
        pdf_path = os.path.join(abs_slides_folder, f"{base_name}.pdf")

        # 2. Convert PDF -> Images (JPG)
        print(f"📸 Extracting images from PDF...")
        if os.path.exists(pdf_path):
            images = convert_from_path(pdf_path)
            for i, image in enumerate(images, start=1):
                image_filename = f"Slide{i}.jpg"
                save_path = os.path.join(abs_slides_folder, image_filename)
                image.save(save_path, "JPEG")
                print(f"   -> Saved {image_filename}")
        else:
            print("❌ PDF conversion failed. Please check LibreOffice installation.")
            return []

        # 3. Extract Text (Platform Independent)
        prs = Presentation(ppt_path)
        for i, slide in enumerate(prs.slides, start=1):
            slide_text = []
            if slide.shapes.title and slide.shapes.title.text:
                slide_text.append(f"Title: {slide.shapes.title.text}")
            for shape in slide.shapes:
                if shape.has_text_frame and shape != slide.shapes.title:
                    text = shape.text.strip()
                    if text:
                        slide_text.append(text)
            
            # Verify image exists
            img_url = f"/slides/Slide{i}.jpg"
            if not os.path.exists(os.path.join(SLIDES_FOLDER, f"Slide{i}.jpg")):
                 logger.warning(f"Image for slide {i} missing")

            slides_data.append({
                "slide_number": i,
                "image_url": img_url, 
                "content": " ".join(slide_text)
            })

        # Save data for Agent
        with open("presentation.json", "w", encoding="utf-8") as f:
            json.dump(slides_data, f, indent=4, ensure_ascii=False)

        return slides_data

    except Exception as e:
        logger.error(f"❌ Error processing PPT: {e}")
        return []

# --- ROUTES ---

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/slides/<path:filename>')
def serve_slide(filename):
    return send_from_directory(SLIDES_FOLDER, filename)

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
        
        # Process in a thread to avoid blocking response
        def run_processing():
            process_ppt(filepath)

        thread = threading.Thread(target=run_processing)
        thread.start()
        thread.join() # Wait for simple implementation

        if os.path.exists("presentation.json"):
            with open("presentation.json", "r") as f:
                data = json.load(f)
            return jsonify({"status": "success", "slide_count": len(data)})
        else:
             return jsonify({"error": "Processing failed"}), 500
    
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/api/connection-details')
def connection_details():
    try:
        LIVEKIT_URL = os.getenv('LIVEKIT_URL')
        API_KEY = os.getenv('LIVEKIT_API_KEY')
        API_SECRET = os.getenv('LIVEKIT_API_SECRET')

        if not all([LIVEKIT_URL, API_KEY, API_SECRET]):
            return jsonify({"error": "Missing Keys"}), 500

        room_name = f"ppt_session_{os.urandom(4).hex()}"
        participant_identity = f"user_{os.urandom(4).hex()}"
        
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
    # AWS/Docker will provide the PORT env var
    port = int(os.environ.get("PORT", 8000))
    print(f"🟢 Web Server running on 0.0.0.0:{port}")
    serve(app, host='0.0.0.0', port=port, threads=4)

if __name__ == '__main__':
    start_server()
