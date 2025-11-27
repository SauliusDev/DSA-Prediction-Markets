import base64
import subprocess
import json
import os

def encode_frame(payload_json, schema="BackMsg"):
    """
    Encode payload dict to protobuf binary entirely in memory.
    Returns bytes directly (no intermediate files).
    """
    try:
        payload_str = json.dumps(payload_json)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        encoder_path = os.path.join(script_dir, "protobuf_encoder.js")
        
        result = subprocess.run(
            ["node", encoder_path, schema],
            input=payload_str.encode("utf-8"),
            capture_output=True,
            check=True
        )
        return result.stdout  # <- this is your binary data
    except subprocess.CalledProcessError as e:
        print("Encoder error:", e.stderr.decode())
        return None