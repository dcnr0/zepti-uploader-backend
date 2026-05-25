import os, requests, json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/massupload', methods=['POST'])
def handle_massupload():
    # Tunneling: Receive pre-processed binary and forward
    data = request.form
    file = request.files.get('audio_file')
    
    if not file: return jsonify({"error": "No file"}), 400

    headers = {"x-api-key": data.get('api_key')}
    asset_config = {
        "assetType": "Audio",
        "displayName": data.get('asset_title'),
        "description": "zepti_W",
        "creationContext": {"creator": {"groupId" if data.get('is_group') == 'true' else "userId": str(data.get('target_id'))}}
    }
    
    # Send directly to Roblox API
    resp = requests.post(
        "https://apis.roblox.com/assets/v1/assets", 
        headers=headers, 
        files={
            'request': (None, json.dumps(asset_config), 'application/json'),
            'fileContent': ('v.mp3', file.read(), 'audio/mpeg')
        }
    )
    return jsonify({"status": "ok" if resp.status_code < 300 else "fail"}), resp.status_code

if __name__ == '__main__':
    app.run(port=int(os.environ.get('PORT', 5000)))
