from flask import Request
def entry(request: Request):
    print(f"API VERSION 2")

    try:
        print(str(request.data))
        print(str(request.headers))
        body = request.get_json(force=True)
        id = body['id']
        print(f"id: {id}")
    except:
        print('WARN: no id found')
    return "OK"
