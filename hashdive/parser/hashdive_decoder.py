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

input = "WooFCgAS6QMKQAoqJCRJRC0wMTQ5MjhiMDlhYjQ0N2U0NGM4MzYyM2IxOTZiMjI2Ny1Ob25lOhIKEAAAAAAAADVAAAAAAADAWEAKLgoqJCRJRC1jMDRjZDhiNjAyMDE5ZmQzNDg1YTFjMzcwZDZjMGUyZC1Ob25lKAIKMAoqJCRJRC02Y2MyM2Q5YTA0NTYxOTFhMzZjMTU5MzRmZDcxYzJlMy1Ob25lKKafBgpACiokJElELTY3Y2I1ZWE5MjU1ZDQ2ZWY3MTBhNzBiOTlhNjI5OWI3LU5vbmU6EgoQAAAAAAAAAAAAAAAAAABZQAo1CiokJElELTg4Y2EyMDAyOTg0NjdjMjBhMDgzMTU1MzlmNzEyZTEyLU5vbmUhfEwGdyYdY8EKNQoqJCRJRC1mMDI2ZTE4YTI4MTE4YzhlMTc2MDA1YWQyOTNiMGQ5MC1Ob25lIYmCCdxCCHVBCjMKKiQkSUQtYjkxYzZhZDRjNDU4NjM5MjJjM2RjZWE4MzBkYzY5MjktTm9uZTIFU2NvcmUKLgoqJCRJRC00MzNiZDJjZDdmYjkzYmJlMGE0NDEwMzY0MDc5NDgyOC1Ob25lKAAKLgoqJCRJRC0wODk1OTNiY2UzNmRmYTFhMDcyYmFiY2FlNDAxMjdlMy1Ob25lKAIaIDk1Y2JlNjE4YmZhZmI3NDM3MjYzMzQ2ZDZjODUwM2QyIgAqADogMmM2YzM3MmJiYmFmODA4YjlkZTNkNzQ0MjFlNzU2NjFCUgoPRXVyb3BlL0lzdGFuYnVsEMz+/////////wEaBWVuLVVTIiRodHRwczovL2hhc2hkaXZlLmNvbS9UcmFkZXJfZXhwbG9yZXIoADIFbGlnaHQ=/v////////8BGgVlbi1VUyIhaHR0cHM6Ly9oYXNoZGl2ZS5jb20vQW5hbHl6ZV9Vc2VyKAAyBWxpZ2h0"
result = decode_frame(input, schema="BackMsg")
print(str(result)+"\n")

input = "WqwFCgAS6QMKQAoqJCRJRC0wMTQ5MjhiMDlhYjQ0N2U0NGM4MzYyM2IxOTZiMjI2Ny1Ob25lOhIKEAAAAAAAADVAAAAAAADAWEAKLgoqJCRJRC1jMDRjZDhiNjAyMDE5ZmQzNDg1YTFjMzcwZDZjMGUyZC1Ob25lKAIKMAoqJCRJRC02Y2MyM2Q5YTA0NTYxOTFhMzZjMTU5MzRmZDcxYzJlMy1Ob25lKKafBgpACiokJElELTY3Y2I1ZWE5MjU1ZDQ2ZWY3MTBhNzBiOTlhNjI5OWI3LU5vbmU6EgoQAAAAAAAAAAAAAAAAAABZQAo1CiokJElELTg4Y2EyMDAyOTg0NjdjMjBhMDgzMTU1MzlmNzEyZTEyLU5vbmUhfEwGdyYdY8EKNQoqJCRJRC1mMDI2ZTE4YTI4MTE4YzhlMTc2MDA1YWQyOTNiMGQ5MC1Ob25lIYmCCdxCCHVBCjMKKiQkSUQtYjkxYzZhZDRjNDU4NjM5MjJjM2RjZWE4MzBkYzY5MjktTm9uZTIFU2NvcmUKLgoqJCRJRC00MzNiZDJjZDdmYjkzYmJlMGE0NDEwMzY0MDc5NDgyOC1Ob25lKAAKLgoqJCRJRC0zMmVkYTMyNWE5MDJiMThjYmYyM2UwZjM2YjM0MjIyOS1Ob25lKAQaIDk1Y2JlNjE4YmZhZmI3NDM3MjYzMzQ2ZDZjODUwM2QyIgAqADogMmM2YzM3MmJiYmFmODA4YjlkZTNkNzQ0MjFlNzU2NjE6IDU4NWMzNTVhNGM1ZTc0YzgzNWU3YTNjMjAxZmI3ZmUyQlIKD0V1cm9wZS9Jc3RhbmJ1bBDM/v////////8BGgVlbi1VUyIkaHR0cHM6Ly9oYXNoZGl2ZS5jb20vVHJhZGVyX2V4cGxvcmVyKAAyBWxpZ2h0"
result = decode_frame(input, schema="BackMsg")
print(str(result)+"\n")
