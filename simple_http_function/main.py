import functions_framework
from flask import Request

@functions_framework.http
def entry(request: Request):
    print("hello")
    print(request.args)
    return "success with v5\n"
