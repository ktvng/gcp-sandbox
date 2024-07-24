import json
import uuid
import google.auth.transport.requests
import google.auth.compute_engine
from google.cloud import tasks_v2

class RemoteCall():
    def __init__(self, service_config_path: str) -> None:
        with open(service_config_path, 'r') as f:
            self._service_config = json.load(f)["service-config"]["value"]
        self._client = tasks_v2.CloudTasksClient()

        _request = google.auth.transport.requests.Request()
        _credentials = google.auth.compute_engine.IDTokenCredentials(
            request=_request,
            target_audience="https://www.googleapis.com/auth/cloud-platform",
            use_metadata_identity_endpoint=True)
        self.service_account_email = _credentials.service_account_email


    def _get_service_url(self, service: str) -> str:
        return self._service_config["functions"][service]

    def _get_service_queue(self, service: str) -> str:
        return self._service_config["queues"][service]

    def _get_location(self) -> str:
        return self._service_config["location"]

    def _get_project_id(self) -> str:
        return self._service_config["project-id"]


    def queue_task(self, service: str, body: dict):
        if body.get('id') is None:
            body['id'] = str(uuid.uuid4())

        url = self._get_service_url(service)
        task = tasks_v2.Task(
            http_request=tasks_v2.HttpRequest(
                http_method=tasks_v2.HttpMethod.POST,
                url=url,
                oidc_token=tasks_v2.OidcToken(
                    service_account_email=self.service_account_email,
                    audience=url,
                ),
                body=json.dumps(body).encode(),
                headers={"Content-Type": "application/json"}
            ),
        )

        return self._client.create_task(
            tasks_v2.CreateTaskRequest(
                parent=self._client.queue_path(
                    project=self._get_project_id(),
                    location=self._get_location(),
                    queue=self._get_service_queue(service)),
                task=task,
            )
        )
