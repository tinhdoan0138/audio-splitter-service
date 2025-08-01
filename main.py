import os
import io
import base64
from flask import Flask, request, jsonify
from pydub import AudioSegment

app = Flask(__name__)

@app.route("/", methods=["POST"])
def split_audio():
    data = request.get_json()

    if not data or 'data_base64' not in data:
        return jsonify({"error": "Missing data_base64 in request"}), 400

    try:
        audio_data = base64.b64decode(data['data_base64'])
        audio_file = io.BytesIO(audio_data)
        sound = AudioSegment.from_file(audio_file)
    except Exception as e:
        return jsonify({"error": f"Could not process audio file: {str(e)}"}), 400

    # 600 giây * 1000 = 600000 ms
    chunk_length_ms = 600 * 1000 
    chunks = []

    for i in range(0, len(sound), chunk_length_ms):
        chunk = sound[i:i + chunk_length_ms]
        buffer = io.BytesIO()
        chunk.export(buffer, format="mp3")
        buffer.seek(0)
        encoded_chunk = base64.b64encode(buffer.read()).decode('utf-8')
        chunks.append(encoded_chunk)

    return jsonify({"chunks": chunks})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
