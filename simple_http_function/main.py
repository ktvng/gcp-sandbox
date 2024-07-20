import functions_framework
from flask import Request

@functions_framework.http
def entry(request: Request):
    print("hello")
    try:
        print(request.args['id'])
    except:
        print("did not find 'id' in args")
    return "success with v6\n"
