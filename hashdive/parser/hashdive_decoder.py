import subprocess
import json
import os

def decode_frame(data: str, schema="ForwardMsg"):
    """
    Decodes a base64-encoded frame and returns the parsed JSON.
    data: base64 string.
    output: decoded json.
    schema: protobuf schema to use (default "ForwardMsg" - server side response, "BackMsg" - client side response).
    """

    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        decoder_path = os.path.join(script_dir, "protobuf_decoder.js")
        
        result = subprocess.run(
            ["node", decoder_path, schema],
            input=data,
            capture_output=True,
            text=True,
            check=True
        )
        decoded_json = json.loads(result.stdout)
        return decoded_json
    except subprocess.CalledProcessError as e:
        print("Decoder error:", e.stderr)
        return None
    except json.JSONDecodeError:
        print("Failed to parse JSON output.")
        return None

input = "WpwBCjd1c2VyX2FkZHJlc3M9MHgyODVhZjE4NzJhYzk5N2RkNTQzNjdhNzk5Y2IyZmQ5Y2IwZDVmZDFiEgAaACIMQW5hbHl6ZV9Vc2VyQk8KD0V1cm9wZS9Jc3RhbmJ1bBDM/v////////8BGgVlbi1VUyIhaHR0cHM6Ly9oYXNoZGl2ZS5jb20vQW5hbHl6ZV9Vc2VyKAAyBWxpZ2h0"
result = decode_frame(input, schema="BackMsg")
print(str(result)+"\n")
