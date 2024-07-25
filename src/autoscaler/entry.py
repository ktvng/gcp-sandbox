from flask import Request
import common.networking

def entry(request: Request):
    print("AUTOSCALER V1")
    common.networking.log_details(request)

    remote = common.networking.RemoteProcedure("./service-config.json")
    # queue = remote.get_queue_details()

    return "OK"
