import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Allow incoming cross-origin extension requests safely

ROBLOX_ASSETS_API = "https://apis.roblox.com/assets/v1/assets"

@app.route('/', methods=['GET'])
def health_check():
    """Returns a status check route to keep UptimeRobot monitors happy and green."""
    return "Pipeline backend link is fully active and loaded in system memory.", 200

@app.route('/api/massupload', methods=['POST'])
def handle_massupload():
    # Double-mapped input parameters to avoid KeyErrors
    api_key = request.form.get('api_key') or request.form.get('apikey')
    target_id = request.form.get('target_id') or request.form.get('targetId')
    is_group_raw = request.form.get('is_group') or request.form.get('isGroup') or 'false'
    base_title = request.form.get('title') or request.form.get('asset_title') or 'audio_variant'

    is_group = is_group_raw.lower() == 'true'

    if not api_key or not target_id:
        return jsonify({"error": "Bad Request: Missing api_key or target_id form elements."}), 400

    if 'audio_files' not in request.files:
        return jsonify({"error": "Bad Request: No binary file objects packed in form request."}), 400

    uploaded_files = request.files.getlist('audio_files')
    results = []

    # Map target context structure required by Roblox
    creator_key = "groupId" if is_group else "userId"

    headers = {
        "x-api-key": api_key
    }

    for idx, file in enumerate(uploaded_files, start=1):
        filename = file.filename or f"variant_{idx}.mp3"
        display_name = f"{base_title}_{idx}"
        
        # Build multipart asset structural configuration parameters
        asset_config = {
            "assetType": "Audio",
            "displayName": display_name,
            "description": "Dispatched via Zepti's MassUploader Cloud Cluster Engine",
            "creationContext": {
                "creator": {
                    creator_key: str(target_id)
                }
            }
        }

        try:
            # Reset file pointer to read raw stream data cleanly
            file.seek(0)
            file_bytes = file.read()

            files_payload = {
                'request': (None, jsonify(asset_config).get_data(), 'application/json'),
                'fileContent': (filename, file_bytes, 'audio/mpeg')
            }

            # Forward request package directly onto Roblox Open Cloud asset allocation matrix
            response = requests.post(ROBLOX_ASSETS_API, headers=headers, files=files_payload)

            if response.status_code in [200, 201]:
                results.append({"name": display_name, "status": "success"})
            else:
                error_msg = response.json().get('message', f'HTTP Status {response.status_code}')
                results.append({"name": display_name, "status": "failed", "msg": error_msg})

        except Exception as e:
            results.append({"name": display_name, "status": "failed", "msg": str(e)})

    return jsonify({"results": results}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
