from flask import Request
import json
import time
import common.networking

def entry(request: Request):
    print(f"API VERSION 3")
    common.networking.log_details(request)
    time.sleep(20)
    return "OK"
