import functions_framework
from flask import Request
from google.auth import compute_engine
import google.auth.transport.requests
import traceback
import common.networking

@functions_framework.http
def entry(request: Request):
    url = "https://secondary-function-tidc3mgixq-uw.a.run.app/"
    try:
        print(request.json['id'])
    except:
        print(f"did not find 'id' in body {request.json}")

    caller = common.networking.RemoteCall("./service-config.json")
    caller.queue_task("secondary-function", body={
        "name": "hello there"
    })

    return "success with v17\n"

def get_access_token(url):
    request = google.auth.transport.requests.Request()
    credentials = compute_engine.IDTokenCredentials(
        request=request, target_audience=url, use_metadata_identity_endpoint=True)

    credentials.refresh(request)
    return credentials.token
