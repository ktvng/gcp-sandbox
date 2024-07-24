from flask import Request
import json

def entry(request: Request):
    print(f"API VERSION 2")

    try:
        print(f'content-type: {str(request.headers.get("Content-Type", "None"))}')
        body = request.get_json(force=True)
        print(json.dumps(body, indent=2))
    except:
        print('WARN: could not decode json body')
    return "OK"
