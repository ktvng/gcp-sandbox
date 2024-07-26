from flask import Request
import google.auth.compute_engine
import google.auth.credentials
import common.networking
import google.cloud.functions_v2 as cloud_functions
import math
import google.auth

def entry(request: Request):
    print("AUTOSCALER V1")
    common.networking.log_details(request)

    service = "secondary-function"
    remote = common.networking.RemoteProcedure("./service-config.json")
    queue = remote.get_queue_details(service)
    scale_factor = .8
    if queue.stats.tasks_count > 100:
        scale_factor = 2

    credentials, proj_id = google.auth.default()
    credentials: google.auth.compute_engine.Credentials = credentials
    print(f"using credentials '{credentials.service_account_email}' scope {credentials.scopes}")
    client = cloud_functions.FunctionServiceClient(credentials=credentials)
    r = cloud_functions.GetFunctionRequest(name=client.function_path(
        proj_id, "us-west1", service
    ))

    orig = client.get_function(r)
    max_instances = orig.service_config.max_instance_count

    new_max_instances = math.floor(max_instances * scale_factor)
    new_max_instances = min(30, new_max_instances)
    new_max_instances = max(2, new_max_instances)

    orig.service_config.max_instance_count = new_max_instances
    print(f"Updating max instances from {max_instances} to {new_max_instances}")
    try:
        r = cloud_functions.UpdateFunctionRequest(function=orig)
        result = client.update_function(r)
        print(f"Update success! {result}")
    except Exception as e:
        print(f"WARN failed to update function due to {e}")


    return "OK"
