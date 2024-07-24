from flask import Request
def entry(request: Request):
    print(f"API VERSION 2")

    try:
        print(str(request.data))
        print(str(request.headers))
        id = request.json['id']
        print(f"id: {id}")
    except:
        print('WARN: no id found')
    return "OK"
