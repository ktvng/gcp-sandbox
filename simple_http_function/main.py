import functions_framework
from flask import Request
import requests
from google.auth import compute_engine
import google.auth.transport.requests

@functions_framework.http
def entry(request: Request):
    url = "https://secondary-function-tidc3mgixq-uw.a.run.app/"
    print("hello")
    try:
        print(request.json['id'])
    except:
        print(f"did not find 'id' in body {request.json}")


    token = get_access_token(url)
    r = requests.post(url, json={"id": "123"}, headers={"Authorization": f"Bearer {token}"})
    print(r)
    return "success with v6\n"

def get_access_token(url):
    request = google.auth.transport.requests.Request()
    credentials = compute_engine.IDTokenCredentials(
        request=request, target_audience=url, use_metadata_identity_endpoint=True)

    credentials.refresh(request)
    return credentials.token
