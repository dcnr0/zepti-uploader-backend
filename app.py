from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import asyncio
import aiohttp
import json
import random
import string
import io
import numpy as np

app = Flask(__name__)
CORS(app)

def get_uid(l=8): 
    return ''.join(random.choices(string.ascii_letters + string.digits, k=l))

def scramble_binary(raw_data: bytearray):
    if len(raw_data) > 2000:
        for _ in range(8):
            insert_pos = random.randint(500, len(raw_data) - 500)
            raw_data[insert_pos:insert_pos] = os.urandom(random.randint(4, 16))
    raw_data.extend(os.urandom(random.randint(128, 512)))
    return bytes(raw_data)

def apply_acoustic_stutter(audio_bytes, index):
    # If it's too short, don't chop it
    if len(audio_bytes) < 10000:
        return scramble_binary(bytearray(audio_bytes))
        
    # We slice the raw audio payload stream directly to create an acoustic stutter 
    # without needing legacy audioop extensions
    header_offset = 1024  # Keep the format headers safe
    stutter_chunk_size = random.randint(2000, 4000)
    
    stutter_chunk = audio_bytes[header_offset : header_offset + stutter_chunk_size]
    repeated_stutter = stutter_chunk * (index % 4 + 1) # Multiplies the audio sample start acoustic layer
    
    # Reconstruct the modified file layout
    mutated_audio = bytearray(audio_bytes[:header_offset])
    mutated_audio.extend(repeated_stutter)
    mutated_audio.extend(audio_bytes[header_offset + stutter_chunk_size:])
    
    return scramble_binary(mutated_audio)

async def upload_task(session, raw_audio, idx, title, api_key, target_id, creator_key):
    # Runs the calculation in a separate thread so it doesn't freeze your upload pipeline
    data = await asyncio.get_event_loop().run_in_executor(
        None, apply_acoustic_stutter, raw_audio, idx
    )
    
    display_name = f"{title}{idx}" 
    headers = {"x-api-key": api_key}
    url = "https://apis.roblox.com/assets/v1/assets"
    
    for attempt in range(15):  
        form = aiohttp.FormData()
        payload = {
            "assetType": "Audio", 
            "displayName": display_name, 
            "description": "zepti_W'", 
            "creationContext": {"creator": {creator_key: str(target_id)}}
        }
        form.add_field('request', json.dumps(payload), content_type='application/json')
        form.add_field('fileContent', data, filename=f'{get_uid(4)}.mp3', content_type='audio/mpeg')
        
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
    
@app.route('/', methods=['GET'])
def health_check():
    return "Pipeline active and listening.", 200
@app.route('/api/massupload', methods=['POST'])
def handle_massupload():
    api_key = request.form.get('apikey')
    target_id = request.form.get('targetId')
    is_group = request.form.get('isGroup') == 'true'
    title = request.form.get('title', 'name')
    upload_count = min(max(int(request.form.get('count', 10)), 1), 100)
    
    if 'audio_file' not in request.files:
        return jsonify({"error": "No audio file container detected"}), 400
        
    audio_file = request.files['audio_file']
    raw_audio = audio_file.read()
    
    creator_key = "groupId" if is_group else "userId"

    async def run_pipeline():
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=0)) as session:
            tasks = [
                upload_task(session, raw_audio, i, title, api_key, target_id, creator_key)
                for i in range(1, upload_count + 1)
            ]
            return await asyncio.gather(*tasks)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(run_pipeline())
    loop.close()
    
    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
