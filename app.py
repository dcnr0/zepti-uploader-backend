import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ROBLOX_ASSETS_API = "https://apis.roblox.com/assets/v1/assets"

@app.route('/', methods=['GET'])
def health_check():
    """Returns a status check route to keep UptimeRobot monitors happy and green."""
    return "Pipeline backend link is fully active and loaded in system memory.", 200

@app.route('/api/massupload', methods=['POST'])
def handle_massupload():
    # The browser has already done the heavy lifting (stutter/warp/scramble)
    # We just grab the data and forward it to Roblox.
    data = request.form
    file = request.files.get('audio_file')

    if not file:
        return jsonify({"status": "failed", "msg": "No file received"}), 400

    headers = {"x-api-key": data.get('api_key')}
    
    asset_config = {
        "assetType": "Audio",
        "displayName": data.get('asset_title'),
        "description": "zepti_W",
        "creationContext": {
            "creator": {
                "groupId" if data.get('is_group') == 'true' else "userId": str(data.get('target_id'))
            }
        }
    }

    # Stream the bytes directly to Roblox
    resp = requests.post(
        "https://apis.roblox.com/assets/v1/assets", 
        headers=headers, 
        files={
            'request': (None, json.dumps(asset_config), 'application/json'),
            'fileContent': ('processed.mp3', file.read(), 'audio/mpeg')
        }
    )
    
    return jsonify({
        "status": "success" if resp.status_code < 300 else "failed",
        "code": resp.status_code
    }), 200
    
    asset_config = {
        "assetType": "Audio",
        "displayName": display_name,
        "description": "zepti_W",
        "creationContext": {
            "creator": {
                creator_key: str(target_id)
            }
        }
    }

    try:
        file.seek(0)
        file_bytes = file.read()

        files_payload = {
            'request': (None, jsonify(asset_config).get_data(), 'application/json'),
            'fileContent': (filename, file_bytes, 'audio/mpeg')
        }

        response = requests.post(ROBLOX_ASSETS_API, headers=headers, files=files_payload)

        if response.status_code in [200, 201]:
            results.append({"name": display_name, "status": "success"})
        else:
            try:
                error_msg = response.json().get('message', f'HTTP Status {response.status_code}')
            except:
                error_msg = f'HTTP Error {response.status_code}'
            results.append({"name": display_name, "status": "failed", "msg": error_msg})

    except Exception as e:
        results.append({"name": display_name, "status": "failed", "msg": str(e)})

    return jsonify({"results": results}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
