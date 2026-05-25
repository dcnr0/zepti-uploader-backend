import os, requests, json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/massupload', methods=['POST'])
def handle_massupload():
    try:
        # Get data from multipart/form-data
        api_key = request.form.get('api_key')
        asset_title = request.form.get('asset_title')
        is_group = request.form.get('is_group') == 'true'
        target_id = request.form.get('target_id')
        file = request.files.get('audio_file')

        if not file or not api_key:
            return jsonify({"status": "error", "message": "Missing fields"}), 400

        # Prepare Roblox API request
        creator = {"groupId": target_id} if is_group else {"userId": target_id}
        asset_config = {
            "assetType": "Audio",
            "displayName": asset_title,
            "creationContext": {"creator": creator}
        }
        
        # Stream file to Roblox
        response = requests.post(
            "https://apis.roblox.com/assets/v1/assets",
            headers={"x-api-key": api_key},
            files={
                'request': (None, json.dumps(asset_config), 'application/json'),
                'fileContent': ('audio.mp3', file.stream, 'audio/mpeg')
            }
        )
        return jsonify({"status": "success", "code": response.status_code}), response.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
