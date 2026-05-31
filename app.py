import requests, json, io, os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/massupload', methods=['POST'])
def handle_massupload():
    try:
        api_key = request.form.get('api_key')
        target_id = request.form.get('target_id')
        is_group = request.form.get('is_group') == 'true'
        asset_title = request.form.get('asset_title')
        file = request.files.get('audio_file')

        if not file or not api_key:
            return jsonify({"status": "error", "message": "Missing fields"}), 400

        try:
            index = int(asset_title.split('_')[-1])
        except:
            index = 1

        raw_data = file.read()
        num_repeats = max(0, index - 1)
        
        if num_repeats > 0:
            header_stutter = raw_data[:2500] * num_repeats
            processed_data = header_stutter + raw_data
        else:
            processed_data = raw_data

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

@app.route('/api/decalupload', methods=['POST'])
def handle_decalupload():
    try:
        api_key = request.form.get('api_key')
        target_id = request.form.get('target_id')
        is_group = request.form.get('is_group') == 'true'
        asset_title = request.form.get('asset_title')
        file = request.files.get('decal_file')

        if not file or not api_key:
            return jsonify({"status": "error", "message": "Missing fields"}), 400

        # Pass-through image upload tracking structure
        raw_image_data = file.read()
        creator_key = "groupId" if is_group else "userId"
        
        asset_config = {
            "assetType": "Decal",
            "displayName": asset_title,
            "description": "zepti_W",
            "creationContext": {"creator": {creator_key: str(target_id)}}
        }

        response = requests.post(
            "https://apis.roblox.com/assets/v1/assets",
            headers={"x-api-key": api_key},
            files={
                'request': (None, json.dumps(asset_config), 'application/json'),
                'fileContent': ('f.png', io.BytesIO(raw_image_data), 'image/png')
            }
        )
        return jsonify({"status": "success", "code": response.status_code}), response.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
