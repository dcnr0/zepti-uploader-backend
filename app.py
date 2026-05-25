from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import aiohttp
import json
import random
import string

app = Flask(__name__)
# Enable CORS completely so your local Google Chrome extension window can reach the cloud
CORS(app)

def get_uid(l=4): 
    return ''.join(random.choices(string.ascii_letters + string.digits, k=l))

async def upload_task(session, raw_audio_data, idx, title, api_key, target_id, creator_key):
    display_name = f"{title}{idx}" 
    headers = {"x-api-key": api_key}
    url = "https://apis.roblox.com/assets/v1/assets"
    
    # 15 retry loops to safely absorb 429 rate limit errors
    for attempt in range(15):  
        form = aiohttp.FormData()
        payload = {
            "assetType": "Audio", 
            "displayName": display_name, 
            "description": "Dispatched via Zepti's MassUploader Cloud Cluster Engine", 
            "creationContext": {"creator": {creator_key: str(target_id)}}
        }
        form.add_field('request', json.dumps(payload), content_type='application/json')
        form.add_field('fileContent', raw_audio_data, filename=f'{get_uid(6)}.mp3', content_type='audio/mpeg')
        
        try:
            async with session.post(url, data=form, headers=headers, timeout=25) as r:
                if r.status in [200, 201, 202]:
                    return {"status": "success", "name": display_name, "msg": "Uploaded successfully."}
                if r.status == 429:
                    await asyncio.sleep(6)  
                else:
                    return {"status": "error", "name": display_name, "msg": f"HTTP {r.status}"}
        except Exception:
            await asyncio.sleep(1)
            
    return {"status": "error", "name": display_name, "msg": "Retries exhausted"}

@app.route('/api/massupload', methods=['POST'])
def handle_massupload():
    api_key = request.form.get('apikey')
    target_id = request.form.get('targetId')
    is_group = request.form.get('isGroup') == 'true'
    title = request.form.get('title', 'name')
    
    # Get the list of pre-scrambled audio files sent from the extension
    audio_files = request.files.getlist('audio_files')
    
    if not audio_files:
        return jsonify({"error": "No mutated media stream chunks detected"}), 400
        
    creator_key = "groupId" if is_group else "userId"

    async def run_pipeline():
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=0)) as session:
            # Dynamically build tasks for each unique variant chunk sent by the extension
            tasks = [
                upload_task(session, file.read(), i, title, api_key, target_id, creator_key)
                for i, file in enumerate(audio_files, start=1)
            ]
            return await asyncio.gather(*tasks)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(run_pipeline())
    loop.close()
    
    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
