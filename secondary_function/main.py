from flask import Request
def entry(request: Request):
    print(f"API VERSION 2")

    try:
        id = request.json['id']
        print(f"id: {id}")
    except:
        print('WARN: no id found')
    return "OK"
