import os, requests, json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/massupload', methods=['POST'])
def handle_massupload():
    # Tunneling mode: The browser did the heavy lifting.
    data = request.form
    file = request.files.get('audio_file')
    
    if not file: return jsonify({"status": "error", "msg": "No file"}), 400

    headers = {"x-api-key": data.get('api_key')}
    asset_config = {
        "assetType": "Audio",
        "displayName": data.get('asset_title'),
        "description": "zepti_W",
        "creationContext": {"creator": {"groupId" if data.get('is_group') == 'true' else "userId": str(data.get('target_id'))}}
    }
    
    resp = requests.post(
        "https://apis.roblox.com/assets/v1/assets", 
        headers=headers, 
        files={
            'request': (None, json.dumps(asset_config), 'application/json'),
            'fileContent': ('v.mp3', file.read(), 'audio/mpeg')
        }
    )
    return jsonify({"status": "success" if resp.status_code < 300 else "failed", "code": resp.status_code}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
