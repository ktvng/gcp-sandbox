import functions_framework
from flask import Request
import requests
from google.auth import impersonated_credentials
import google.auth.transport.requests

@functions_framework.http
def entry(request: Request):
    url = "https://secondary-function-tidc3mgixq-uw.a.run.app/"
    print("hello")
    try:
        print(request.json['id'])
    except:
        print(f"did not find 'id' in body {request.json}")


    token = get_access_token()
    r = requests.post(url, json={"id": "123"}, headers={"Authorization": f"Bearer {token}"})
    print(r)
    return "success with v6\n"

def get_access_token():
    credentials, project_id = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
    auth_req_session = google.auth.transport.requests.Request()
    credentials.refresh(auth_req_session)
    return credentials.token
