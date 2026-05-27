import requests, json, io, os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/massupload', methods=['POST'])
def handle_massupload():
    try:
        # Get data
        api_key = request.form.get('api_key')
        target_id = request.form.get('target_id')
        is_group = request.form.get('is_group') == 'true'
        asset_title = request.form.get('asset_title') # Format: "name_j"
        file = request.files.get('audio_file')

        if not file or not api_key:
            return jsonify({"status": "error", "message": "Missing fields"}), 400

        # Extract index from title (e.g., "mytrack_1", "mytrack_2")
        # We assume the index is the last part after the underscore
        try:
            index = int(asset_title.split('_')[-1])
        except:
            index = 1

        raw_data = file.read()
        
        # LOGIC: 1st (index 1) = 0 repeats, 2nd (index 2) = 1 repeat, 3rd (index 3) = 2 repeats
        # Calculation: repeats = index - 1
        num_repeats = max(0, index - 1)
        
        # Apply stutter if repeats > 0
        if num_repeats > 0:
            header_stutter = raw_data[:2500] * num_repeats
            processed_data = header_stutter + raw_data
        else:
            processed_data = raw_data

        # Prepare Roblox Asset Config
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
                'fileContent': ('v.mp3', io.BytesIO(processed_data), 'audio/mpeg')
            }
        )
        
        return jsonify({"status": "success", "code": response.status_code}), response.status_code

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
