import functions_framework
from flask import Request
from google.auth import compute_engine
import google.auth.transport.requests
import common.networking

remote = common.networking.RemoteProcedure("./service-config.json")

@functions_framework.http
def entry(request: Request):
    common.networking.log_details(request)

    for i in range(10):
        remote.queue_task("secondary-function", body={
            "part": f"{i}"
        })

    return "API v19\n"

def get_access_token(url):
    request = google.auth.transport.requests.Request()
    credentials = compute_engine.IDTokenCredentials(
        request=request, target_audience=url, use_metadata_identity_endpoint=True)

    credentials.refresh(request)
    return credentials.token
