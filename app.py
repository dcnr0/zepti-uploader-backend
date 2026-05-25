# app.py (Optimized Tunnel)
@app.route('/api/massupload', methods=['POST'])
def handle_massupload():
    # Bypass heavy processing; use direct read for speed
    data = request.form
    file = request.files.get('audio_file')
    
    # Send directly to Roblox
    resp = requests.post(
        "https://apis.roblox.com/assets/v1/assets", 
        headers={"x-api-key": data.get('api_key')}, 
        files={
            'request': (None, json.dumps({
                "assetType": "Audio",
                "displayName": data.get('asset_title'),
                "creationContext": {"creator": {"groupId" if data.get('is_group') == 'true' else "userId": str(data.get('target_id'))}}
            }), 'application/json'),
            'fileContent': ('v.mp3', file.read(), 'audio/mpeg')
        }
    )
    return jsonify({"status": "ok" if resp.status_code < 300 else "fail"}), resp.status_code
