from flask import Request
def entry(request: Request):
    print(f"called")
    return "OK"
