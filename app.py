import os, requests, json, io
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydub import AudioSegment

app = Flask(__name__)
CORS(app)

@app.route('/api/massupload', methods=['POST'])
def handle_massupload():
    try:
        # Get data
        api_key = request.form.get('api_key')
        target_id = request.form.get('target_id')
        is_group = request.form.get('is_group') == 'true'
        asset_title = request.form.get('asset_title')
        file = request.files.get('audio_file')

        if not file: return jsonify({"error": "No file"}), 400

        # --- STUTTER LOGIC ---
        # Loads the file into memory and adds the stutter effect
        audio = AudioSegment.from_file(file)
        stutter_block = audio[:100] # 100ms stutter
        processed_audio = (stutter_block * 3) + audio
        
        buffer = io.BytesIO()
        processed_audio.export(buffer, format="mp3")
        buffer.seek(0)

        # Prepare Roblox Request
        creator = {"groupId": target_id} if is_group else {"userId": target_id}
        asset_config = {
            "assetType": "Audio",
            "displayName": asset_title,
            "description": "zepti_W",
            "creationContext": {"creator": creator}
        }
        
        response = requests.post(
            "https://apis.roblox.com/assets/v1/assets",
            headers={"x-api-key": api_key},
            files={
                'request': (None, json.dumps(asset_config), 'application/json'),
                'fileContent': ('audio.mp3', buffer, 'audio/mpeg')
            }
        )
        return jsonify({"status": "success", "code": response.status_code}), response.status_code

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
