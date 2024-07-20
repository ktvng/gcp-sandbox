import functions_framework
from flask import Request
import requests

@functions_framework.http
def entry(request: Request):
    url = "https://secondary-function-tidc3mgixq-uw.a.run.app/"
    print("hello")
    try:
        print(request.json['id'])
    except:
        print(f"did not find 'id' in body {request.json}")


    r = requests.post(url, json={"id": "123"})
    print(r)
    return "success with v6\n"
