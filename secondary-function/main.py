from flask import Request
def entry(request: Request):
    print(f"API VERSION 2")

    try:
        print("#######################################")
        print(str(request.data))
        print(str(request.headers))
        print("=======================================")
        body = request.get_json(force=True)
        id = body['id']
        print(f"id: {id}")
    except:
        print('WARN: no id found')
    return "OK"
