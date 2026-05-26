import requests, json, io, os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/massupload', methods=['POST'])
def handle_massupload():
    try:
        # Get data from request
        api_key = request.form.get('api_key')
        target_id = request.form.get('target_id')
        is_group = request.form.get('is_group') == 'true'
        asset_title = request.form.get('asset_title')
        file = request.files.get('audio_file')

        if not file or not api_key:
            return jsonify({"status": "error", "message": "Missing fields"}), 400

        # Read file as raw binary
        raw_data = file.read()
        
        # STUTTER LOGIC: 
        # 300 BPM = 200ms duration per beat.
        # Slicing the first 2500 bytes approximates 200ms.
        # Prepending this block 3 times creates the stutter effect.
        header_stutter = raw_data[:2500] * 3
        processed_data = header_stutter + raw_data

        # Prepare Roblox Asset Config
        creator = {"groupId": target_id} if is_group else {"userId": target_id}
        asset_config = {
            "assetType": "Audio",
            "displayName": asset_title,
            "description": "zepti_W",
            "creationContext": {"creator": creator}
        }
        
        # Send to Roblox API
        response = requests.post(
            "https://apis.roblox.com/assets/v1/assets",
            headers={"x-api-key": api_key},
            files={
                'request': (None, json.dumps(asset_config), 'application/json'),
                'fileContent': ('v.mp3', io.BytesIO(processed_data), 'audio/mpeg')
            }
        )
        
        return jsonify({"status": "success", "code": response.status_code}), response.status_code

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
