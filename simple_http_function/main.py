import functions_framework
from flask import Request

@functions_framework.http
def entry(request: Request):
    print("hello")
    return "success with v4"
