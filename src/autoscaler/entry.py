from flask import Request
import common.networking

def entry(request: Request):
    print("AUTOSCALER V1")
    common.networking.log_details(request)
    return "OK"
