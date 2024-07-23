import functions_framework
from flask import Request
import requests
from google.auth import compute_engine
import google.auth.transport.requests
import uuid
from google.cloud import tasks_v2beta3 as tasks_v2
import traceback

project = "moonlit-web-429604-s7"
location = "us-west1"
queue = "test-task-queue2"

_request = google.auth.transport.requests.Request()
_credentials = compute_engine.IDTokenCredentials(
    request=_request, target_audience="www.google.com", use_metadata_identity_endpoint=True)
service_account_email = _credentials.service_account_email

@functions_framework.http
def entry(request: Request):
    url = "https://secondary-function-tidc3mgixq-uw.a.run.app/"
    print("hello")
    try:
        print(request.json['id'])
    except:
        print(f"did not find 'id' in body {request.json}")

    try:
        queue_task(url)
    except Exception as e:
        print(f"could not push to queue with error {e} {traceback.format_exc()}")

    token = get_access_token(url)
    r = requests.post(url, json={"id": str(uuid.uuid4())}, headers={"Authorization": f"Bearer {token}"})
    print(r)
    # time.sleep(10)
    return "success with v8\n"

def get_access_token(url):
    request = google.auth.transport.requests.Request()
    credentials = compute_engine.IDTokenCredentials(
        request=request, target_audience=url, use_metadata_identity_endpoint=True)

    credentials.refresh(request)
    print("USING SERVICE ACCOUNT", credentials.service_account_email)
    return credentials.token

def queue_task(url):
    client = tasks_v2.CloudTasksClient()
    print(client._transport._credentials.service_account_email)
    print(client._transport._credentials.account)
    task = tasks_v2.Task(
        http_request=tasks_v2.HttpRequest(
            http_method=tasks_v2.HttpMethod.POST,
            url=url,
            oidc_token=tasks_v2.OidcToken(
                service_account_email=service_account_email,
                audience=url,
            ),
            body="hellos",
        ),
    )
    return client.create_task(
        tasks_v2.CreateTaskRequest(
            parent=client.queue_path(project, location, queue),
            task=task,
        )
    )
