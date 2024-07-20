import functions_framework
from flask import Request

@functions_framework.http
def entry(request: Request):
    print("hello")
    try:
        print(request.json['id'])
    except:
        print("did not find 'id' in body")
    return "success with v6\n"
