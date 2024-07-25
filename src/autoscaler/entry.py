from flask import Request
import common.networking
import google.cloud.functions_v2 as cloud_functions
import math

def entry(request: Request):
    print("AUTOSCALER V1")
    common.networking.log_details(request)

    service = "secondary-function"
    remote = common.networking.RemoteProcedure("./service-config.json")
    queue = remote.get_queue_details(service)
    scale_factor = .8
    if queue.stats.tasks_count > 100:
        scale_factor = 2

    client = cloud_functions.FunctionServiceClient()
    request = cloud_functions.GetFunctionRequest(name=service)
    orig = client.get_function(request)
    max_instances = orig.service_config.max_instance_count

    new_max_instances = math.floor(max_instances * scale_factor)
    new_max_instances = min(30, new_max_instances)

    orig.service_config.max_instance_count = new_max_instances
    print(f"Updating max instances from {max_instances} to {new_max_instances}")
    request = cloud_functions.UpdateFunctionRequest(function=orig)
    client.update_function()

    return "OK"
